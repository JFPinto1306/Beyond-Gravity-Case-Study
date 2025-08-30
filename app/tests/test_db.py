import pytest
from db import create_table, save_records, get_connection

@pytest.fixture(scope="module")
def setup_db():
    # Ensure table exists before tests
    create_table()
    yield
    # optional: cleanup after tests
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM earthquake_records;")
    conn.commit()
    cur.close()
    conn.close()

def test_save_records_new(setup_db):
    records = [
        {"id": "test1", "location": "Testville", "mag": 5.0, "depth": 10, "time": "2025-08-30T00:00:00"}
    ]
    save_records(records)
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, location, mag, depth FROM earthquake_records WHERE id = 'test1'")
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    assert row is not None
    assert row[0] == "test1"
    assert row[1] == "Testville"
    assert row[2] == 5.0
    assert row[3] == 10

def test_save_records_duplicates(setup_db):
    records = [
        {"id": "test1", "location": "Testville", "mag": 5.0, "depth": 10, "time": "2025-08-30T00:00:00"}
    ]
    save_records(records)  # same record again
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM earthquake_records WHERE id = 'test1'")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    # Should still only be one record
    assert count == 1
