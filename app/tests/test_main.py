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
def test_create_job():
    payload = {"name": "Test Job", "status": "PENDING"}
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Job"
    assert data["status"] == "PENDING"
    assert "id" in data

def test_list_jobs():
    # Create a job first
    client.post("/api/jobs", json={"name": "Job1", "status": "PENDING"})
    response = client.get("/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Job1"

def test_update_job_status():
    # Create a job first
    create_response = client.post("/api/jobs", json={"name": "Job2", "status": "PENDING"})
    job_id = create_response.json()["id"]

    # Update status
    response = client.patch(f"/api/jobs/{job_id}", json={"status": "COMPLETED"})
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"

def test_delete_job():
    # Create a job first
    create_response = client.post("/api/jobs", json={"name": "Job3", "status": "PENDING"})
    job_id = create_response.json()["id"]

    # Delete job
    response = client.delete(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Job deleted successfully"

    # Ensure DB is empty
    response = client.get("/api/jobs")
    assert all(job["id"] != job_id for job in response.json())
