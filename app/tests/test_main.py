from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# -----------------------------
# Health Endpoints
# -----------------------------
def test_health_liveness():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_health_readiness():
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

# -----------------------------
# Job Endpoints
# -----------------------------
# -----------------------------
# Job Endpoints
# -----------------------------
def test_create_job():
    # Changed "PENDING" to "pending"
    payload = {"name": "Test Job", "status": "pending"}
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Job"
    assert data["status"] == "pending"
    assert "id" in data

def test_list_jobs():
    # Changed "PENDING" to "pending"
    client.post("/api/jobs", json={"name": "Job1", "status": "pending"})
    response = client.get("/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Job1"

def test_update_job_status():
    # Changed "PENDING" to "pending"
    create_response = client.post("/api/jobs", json={"name": "Job2", "status": "pending"})
    job_id = create_response.json()["id"]

    # Changed "COMPLETED" to "completed"
    response = client.patch(f"/api/jobs/{job_id}", json={"status": "completed"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

def test_delete_job():
    # Changed "PENDING" to "pending"
    create_response = client.post("/api/jobs", json={"name": "Job3", "status": "pending"})
    job_id = create_response.json()["id"]

    response = client.delete(f"/api/jobs/{job_id}")
    assert response.status_code == 200