# tests/unit/test_routes.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    if "text/plain" in response.headers["Content-Type"]:
        assert "# HELP" in response.text  # Prometheus text format
    else:
        assert response.json()["message"] == "Prometheus metrics are not enabled"

        
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
