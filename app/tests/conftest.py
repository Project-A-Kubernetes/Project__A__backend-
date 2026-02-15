# flake8: noqa: E402
import os

# -----------------------------
# Must set DATABASE_URL before importing app modules
# -----------------------------
os.environ["DATABASE_URL"] = "sqlite:///./test_db.db"

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
    connect_args={"check_same_thread": False},
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


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    def remove_test_db():
        if os.path.exists("./test_db.db"):
            os.remove("./test_db.db")
    request.addfinalizer(remove_test_db)