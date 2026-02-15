from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime
from uuid import uuid4

from app.models.database import Base
from app.schemas import JobStatus


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)

    status = Column(
        Enum(
            JobStatus,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=False,
        default=JobStatus.PENDING
    )

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
