# flake8: noqa: E402
import os

# -----------------------------
# Must set DATABASE_URL before importing app modules
# -----------------------------
os.environ["DATABASE_URL"] = "sqlite:///:memory:"  # in-memory SQLite for tests

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models.database import Base
from app.models.job import JobModel

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
    bind=engine
)

# Create all tables for tests
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
