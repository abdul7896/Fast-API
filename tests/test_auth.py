# tests/test_auth.py
def test_missing_api_key(client):
    response = client.post("/user", json={"email": "test@example.com", "name": "Test User"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Missing or invalid API key"}

def test_invalid_api_key(client):
    response = client.post("/user", json={"email": "test@example.com", "name": "Test User"}, headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Missing or invalid API key"}