import time
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

# Disable problematic monkey-patching early
@pytest.fixture(autouse=True)
def disable_gevent_monkeypatch():
    import gevent.monkey
    gevent.monkey.patch_all(ssl=False, thread=False)

# Create test client with explicit async config
@pytest.fixture
def test_client():
    return TestClient(app, backend_options={"use_uvloop": False})

def test_get_users_latency(test_client):
    """Test /users endpoint response time with proper isolation"""
    # Mock data
    mock_users = [{
        "email": "test@example.com",
        "name": "Test User",
        "avatar_url": "https://s3.amazonaws.com/avatar.jpg"
    }]
    
    # Patch at the correct location with proper await handling
    with patch("app.main.get_all_users", return_value=mock_users):
        # Warm up (first call may be slower)
        test_client.get("/users")
        
        # Actual measurement
        start = time.monotonic()
        response = test_client.get("/users")
        elapsed = time.monotonic() - start
        
        # Verify
        assert response.status_code == 200
        assert elapsed < 1.0, f"Response took {elapsed:.3f}s (expected <1s)"
        assert response.json() == {"users": mock_users}