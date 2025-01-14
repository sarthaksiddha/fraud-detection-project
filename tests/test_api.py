from fastapi.testclient import TestClient
from src.api.api_server import app
import pytest
from datetime import datetime

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    """Test API health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_endpoint(client):
    """Test transaction prediction endpoint."""
    transaction = {
        "transaction_id": "TX123",
        "user_id": 1,
        "amount": 1000.0,
        "currency": "USD",
        "merchant_category": "retail",
        "timestamp": datetime.now().isoformat(),
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    }
    
    response = client.post("/api/v1/predict", json=transaction)
    assert response.status_code == 200
    
    data = response.json()
    assert "transaction_id" in data
    assert "is_fraud" in data
    assert "fraud_probability" in data