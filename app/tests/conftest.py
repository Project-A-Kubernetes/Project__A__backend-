# flake8: noqa: E402
import os
import pytest

# -----------------------------
# Set DATABASE_URL for tests
# Must be set BEFORE importing app modules
# -----------------------------
os.environ["DATABASE_URL"] = "sqlite:///:memory:"  

# Now it is safe to import app modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models.database import Base, JobModel

# -----------------------------
# Test Database Setup (SQLite in-memory)
# -----------------------------
engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},  # required for SQLite in-memory
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Create tables
Base.metadata.create_all(bind=engine)

# -----------------------------
# Override FastAPI DB dependency
# -----------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# -----------------------------
# Fixture: clear DB before each test
# -----------------------------
@pytest.fixture(autouse=True)
def clear_db():
    db = TestingSessionLocal()
    db.query(JobModel).delete()
    db.commit()
    db.close()
