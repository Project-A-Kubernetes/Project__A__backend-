import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.models.database import Base
from app.models.job import JobModel

# -----------------------------
# Test Database (SQLite)
# -----------------------------

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base.metadata.create_all(bind=engine)


# -----------------------------
# Override DB dependency
# -----------------------------

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture(autouse=True)
def clear_db():
    """
    Ensures DB is clean before each test.
    """
    db = TestingSessionLocal()
    db.query(JobModel).delete()
    db.commit()
    db.close()


# -----------------------------
# Tests
# -----------------------------

def test_health_liveness():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_health_readiness():
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_create_job():
    payload = {
        "name": "Test Job",
        "status": "PENDING"
    }

    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Test Job"
    assert data["status"] == "PENDING"
    assert "id" in data


def test_list_jobs():
    # Create job first
    client.post("/api/jobs", json={
        "name": "Job1",
        "status": "PENDING"
    })

    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_job_status():
    # Create job
    create_response = client.post("/api/jobs", json={
        "name": "Job1",
        "status": "PENDING"
    })

    job_id = create_response.json()["id"]

    # Update status
    response = client.patch(
        f"/api/jobs/{job_id}",
        json={"status": "COMPLETED"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_delete_job():
    create_response = client.post("/api/jobs", json={
        "name": "Job1",
        "status": "PENDING"
    })

    job_id = create_response.json()["id"]

    response = client.delete(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Job deleted successfully"

    # Ensure it's gone
    response = client.get("/api/jobs")
    assert len(response.json()) == 0
