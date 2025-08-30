import os
import psycopg2
from psycopg2.extras import execute_values

# Read DB credentials from environment variables
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "db"),       # default = "db" (service name in docker-compose)
    "database": os.environ.get("DB_NAME", "earthquakes"),
    "user": os.environ.get("DB_USER", "earth_user"),
    "password": os.environ.get("DB_PASSWORD", "supersecret"),
    "port": os.environ.get("DB_PORT", 5432)
}

TABLE_NAME = "earthquake_records"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id TEXT PRIMARY KEY,
    location TEXT,
    mag REAL,
    depth REAL,
    time TIMESTAMP
);
"""

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(CREATE_TABLE_SQL)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Table '{TABLE_NAME}' is ready.")

def save_records(records):
    if not records:
        print("No records to save.")
        return

    
    values = [(r['id'], r['location'], r['mag'], r['depth'], r['time']) for r in records]

    sql = f"""
    INSERT INTO {TABLE_NAME} (id, location, mag, depth, time)
    VALUES %s
    ON CONFLICT (id) DO NOTHING;
    """

    conn = get_connection()
    cur = conn.cursor()

    # Fetching initial count for logging
    cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    before = cur.fetchone()[0]
    
    
    execute_values(cur, sql, values)
    conn.commit()
    
    # Fetching final count for logging
    cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    after = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    print(f"Inserted {after - before} new records.")