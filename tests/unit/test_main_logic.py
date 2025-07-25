import io
import os

from fastapi.testclient import TestClient

from app.main import app

# Use API_KEY from env or fallback to a default for tests
API_KEY = os.getenv("API_KEY", "secret-api-key")
client = TestClient(app)


def get_headers(key=API_KEY):
    # Helper function to build headers with the API key
    return {"X-API-Key": key}


def test_missing_api_key():
    # Test request without API key returns 403 forbidden
    response = client.post("/user")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_invalid_api_key():
    # Test request with wrong API key returns 403 forbidden
    response = client.post("/user", headers=get_headers("wrongkey"))
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API credentials"


def test_missing_name():
    # Test missing required 'name' field results in validation error (422)
    files = {"avatar": ("avatar.jpg", io.BytesIO(b"fake image"), "image/jpeg")}
    data = {"email": "user@example.com"}
    response = client.post("/user", headers=get_headers(), data=data, files=files)
    assert response.status_code == 422  # Missing required 'name'


def test_missing_email():
    # Test missing required 'email' field results in validation error (422)
    files = {"avatar": ("avatar.jpg", io.BytesIO(b"fake image"), "image/jpeg")}
    data = {"name": "Test User"}
    response = client.post("/user", headers=get_headers(), data=data, files=files)
    assert response.status_code == 422  # Missing required 'email'


def test_missing_avatar():
    # Test missing required 'avatar' file results in validation error (422)
    data = {"name": "Test User", "email": "user@example.com"}
    response = client.post("/user", headers=get_headers(), data=data)  # no files
    assert response.status_code == 422  # Missing avatar


def test_invalid_avatar_type():
    # Test uploading avatar with unsupported content type returns 400 error
    files = {"avatar": ("avatar.png", io.BytesIO(b"fake image"), "image/png")}
    data = {"name": "Test User", "email": "user@example.com"}
    response = client.post("/user", headers=get_headers(), data=data, files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Only JPEG images are accepted"
