from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_valid_ticker():
    response = client.get("/metrics?ticker=AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert "pe_ratio" in data
    assert "eps" in data
    assert "volume" in data

def test_invalid_ticker():
    response = client.get("/metrics?ticker=INVALID123")
    assert response.status_code == 500  # Yahoo will raise internally
    assert "detail" in response.json()
