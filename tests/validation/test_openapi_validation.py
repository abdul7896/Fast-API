import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_invalid_email():
    response = client.post("/user", json={"name": "John", "email": "not-an-email"})
    assert response.status_code == 422

def test_empty_name():
    response = client.post("/user", json={"name": "", "email": "john@example.com"})
    assert response.status_code == 422

def test_missing_fields():
    response = client.post("/user", json={})
    assert response.status_code == 422
