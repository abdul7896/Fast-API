# tests/unit/test_routes.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
 
def test_create_user_validation():
    # Missing email
    response = client.post("/user", json={"name": "No Email"})
    assert response.status_code == 422

    # Missing name
    response = client.post("/user", json={"email": "no-name@example.com"})
    assert response.status_code == 422

    # Invalid email
    response = client.post("/user", json={"email": "invalid", "name": "Test User"})
    assert response.status_code == 422
