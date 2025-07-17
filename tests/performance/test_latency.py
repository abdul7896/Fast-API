import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_latency():
    start = time.time()
    response = client.get("/health")
    elapsed = time.time() - start
    assert response.status_code == 200
    assert elapsed < 0.5, f"Latency too high: {elapsed}s"

def test_get_users_latency():
    start = time.time()
    response = client.get("/users")
    elapsed = time.time() - start
    assert response.status_code == 200
    assert elapsed < 1.0, f"Latency too high: {elapsed}s"
