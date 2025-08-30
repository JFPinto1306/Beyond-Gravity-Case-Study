import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_get_earthquakes_basic():
    response = client.get("/earthquakes?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5
    if data:
        eq = data[0]
        assert "id" in eq
        assert "location" in eq
        assert "mag" in eq
        assert "depth" in eq
        assert "time" in eq

def test_get_earthquake_by_id():
    # First fetch a record to use its id
    list_resp = client.get("/earthquakes?limit=1")
    assert list_resp.status_code == 200
    items = list_resp.json()
    if not items:
        pytest.skip("No earthquakes in DB to test against")
    eq_id = items[0]["id"]

    resp = client.get(f"/earthquakes/{eq_id}")
    assert resp.status_code == 200
    eq = resp.json()
    assert eq["id"] == eq_id
    assert "location" in eq
    assert "mag" in eq
    assert "depth" in eq
    assert "time" in eq

def test_unknown_query_param():
    response = client.get("/earthquakes?foo=bar")
    assert response.status_code == 400
    assert "Unexpected query parameter" in response.json()["detail"]
