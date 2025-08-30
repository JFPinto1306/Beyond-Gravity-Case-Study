from datetime import datetime
from fastapi import FastAPI, Query, Request, HTTPException
from typing import List, Literal, Optional
from db import get_connection, create_table, save_records
from usgs import fetch_usgs
import asyncio
import logging

app = FastAPI(title="Earthquake API")
logging.basicConfig(level=logging.INFO)


FETCH_INTERVAL = 10 # seconds
ALLOWED_PARAMS = {"limit", "min_mag", "min_depth", "start_time", "end_time"}


# Database setup
@app.on_event("startup")
async def startup_event():
    logging.info("Creating Table")
    create_table()

    # Real Time Updates Simulation
    asyncio.create_task(periodic_fetch())

# Real Time Updates Simulation
async def periodic_fetch():
    while True:
        try:
            data = fetch_usgs()
            save_records(data)
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
        await asyncio.sleep(FETCH_INTERVAL)


# Helper Function
def fetch_earthquakes_from_db(limit: int = 100,min_mag: Optional[float] = None,start_time: Optional[datetime] = None,end_time: Optional[datetime] = None) -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()
    
    sql = "SELECT * FROM earthquake_records WHERE 1=1"
    params = []

    if min_mag is not None:
        sql += " AND mag >= %s"
        params.append(min_mag)
    if start_time is not None:
        sql += " AND time >= %s"
        params.append(start_time)
    if end_time is not None:
        sql += " AND time <= %s"
        params.append(end_time)
        
    sql += " ORDER BY time DESC LIMIT %s"
    params.append(limit)
    
    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return [
        {"id": r[0], "location": r[1], "mag": r[2], "depth": r[3], "time": r[4].isoformat()}
        for r in rows
    ]

# API endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to the Earthquake API. Please refer to /docs for API documentation."}

@app.get("/earthquakes", response_model=List[dict])
def get_earthquakes(
    request: Request,
    limit: int = 100,
    min_mag: Optional[float] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    received_params = set(request.query_params.keys())
    unknown_params = received_params - ALLOWED_PARAMS
    if unknown_params:
        raise HTTPException(
            status_code=400,
            detail=f"Unexpected query parameter(s): {', '.join(unknown_params)}. "
                   f"Please use only the allowed parameters: {', '.join(ALLOWED_PARAMS)}."
        )

    return fetch_earthquakes_from_db(
        limit=limit,
        min_mag=min_mag,
        start_time=start_time,
        end_time=end_time
    )

@app.get("/earthquakes/{eq_id}", response_model=dict)
def get_earthquake(eq_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, location, mag, depth, time FROM earthquake_records WHERE id = %s", (eq_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Earthquake not found")
    
    return {
        "id": row[0],
        "location": row[1],
        "mag": row[2],
        "depth": row[3],
        "time": row[4].isoformat()
    }