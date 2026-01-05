from fastapi.testclient import TestClient
from app.backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# We can add more tests here, but without a running DB/LLM they might require extensive mocking.
# For now, health check confirms app structure is valid.
