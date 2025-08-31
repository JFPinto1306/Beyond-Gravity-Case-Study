# Earthquake Monitoring API

This project is a **backend service** that ingests real-time earthquake data from the [USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/), stores it in PostgreSQL, and exposes it via a **RESTful API**.  

It was built as part of a **Junior Backend case study** for Beyond Gravity.

## Features

- Fetches earthquake data from **USGS** every 10 seconds (simulated real-time updates).  
- Stores records in a **PostgreSQL** database.  
- Provides REST API endpoints:
  - `GET /earthquakes`: List recent earthquakes with optional filters.
  - `GET /earthquakes/{id}`: Get details of a specific earthquake.
- Supports **filtering** by:
  - Minimum magnitude (`min_mag`)
  - Date range (`start_time`, `end_time`)
- Runs fully in **Docker** (via `docker-compose`).

## Tech Stack

- **Python** with [FastAPI]
- **PostgreSQL** for persistence  
- **Docker & Docker Compose** for containerized setup  
- **Async background tasks** for periodic ingestion  

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Beyond-Gravity-Case-Study.git
cd Beyond-Gravity-Case-Study
```

### 2. Build the containers and start the services:
```bash
docker-compose up --build
```

### 3. Access the API
- The API will be available at `http://localhost:8000`
- API documentation (Swagger UI) at `http://localhost:8000/docs`
- Two endpoints are available:
  - `GET /earthquakes`: List recent earthquakes with optional filters: 
    - `limit`: Number of records to return (default 100)
    - `min_mag`: Minimum magnitude to filter
    - `start_time`: Start of date range (ISO format)
    - `end_time`: End of date range (ISO format)
  - `GET /earthquakes/{id}`: Get details of a specific earthquake.
 
> **Note on `.env` file**:  
> .env was included to facilitate setup, but in a real production environment a proper secrets manager would be used.  



## Walkthrough
### Fetching Earthquake Data
  - The service retrieves daily earthquake data from the USGS API and stores it in the PostgreSQL database.
  - The fetching logic is implemented in `app/usgs.py` and runs every 10 seconds as a background task.

### Database Schema
- The `Earthquake` model is defined in `app/db.py` and includes fields such as:
  - `id`: Unique identifier
  - `location`: Approximate location of the earthquake
  - `mag`: Magnitude of the earthquake
  - `depth`: Depth of the earthquake
  - `time`: Timestamp of the event

### API Endpoints
- The API exposes two main endpoints:
  - `GET /earthquakes`: Fetch a list of recent earthquakes with optional query parameters for filtering.
  - `GET /earthquakes/{id}`: Fetch detailed information about a specific earthquake by its ID.

### Running in Docker
- The entire application is containerized using Docker. The `docker-compose.yml` file sets up both the FastAPI application and the PostgreSQL database.
- Environment variables for database connection are managed via a `.env` file.
- Uvicorn is used as the ASGI server to run the FastAPI application.

## Running Tests

Tests are located in the `app/tests` directory and cover both **database operations** and **API endpoints**.  

### Database Tests
- **`test_save_records_new`**: Inserts new earthquake records into the database successfully.
- **`test_save_records_duplicates`**: Ensures duplicate records are not inserted.

### API Tests
- **`test_get_earthquakes_basic`**: Fetches a list of recent earthquakes.
- **`test_get_earthquake_by_id`**: Fetches details of a specific earthquake by its ID.
- **`test_unknown_query_param`**: Validates that the API returns a **400 Bad Request** for unexpected query parameters.

### Running Tests
Run the tests inside the Docker container using:

```bash
docker compose run --rm -e PYTHONPATH=/app app pytest tests/ -v
```


