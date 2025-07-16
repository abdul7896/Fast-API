from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user_invalid():
    response = client.post("/user", json={"email": "bad-email", "name": "Name"})
    assert response.status_code == 422
