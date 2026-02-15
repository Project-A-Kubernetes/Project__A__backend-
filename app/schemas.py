from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Optional

# -------------------------
# Status Enum
# -------------------------
class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# -------------------------
# Full Job Schema (GET/POST)
# -------------------------
class Job(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    name: str
    status: JobStatus = JobStatus.PENDING
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True  # Enables reading from SQLAlchemy models

# -------------------------
# Job Status Update Schema (PATCH)
# -------------------------
class JobUpdateStatus(BaseModel):
    status: JobStatus
