from uuid import UUID
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas import Job, JobUpdateStatus
from app.telemetry import metrics_middleware, setup_logging
from app.models.database import SessionLocal, engine, Base
from app.models.job import JobModel

# Setup logging
setup_logging()

#  we Create DB tables (for quick start, note: we use Alembic in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Management API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def track_metrics(request: Request, call_next):
    return await metrics_middleware(request, call_next)



# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# Routes
# -------------------------

@app.get("/api/jobs", response_model=list[Job])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobModel).all()
    return [Job.from_orm(job) for job in jobs]


@app.post("/api/jobs", response_model=Job)
def create_job(job: Job, db: Session = Depends(get_db)):
    db_job = JobModel(name=job.name, status=job.status)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return Job.from_orm(db_job)


@app.patch("/api/jobs/{job_id}", response_model=Job)
def update_job_status(job_id: UUID, job_update: JobUpdateStatus, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == str(job_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = job_update.status
    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return Job.from_orm(job)


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == str(job_id)).first()  # <- convert to str
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}


# -------------------------
# Health Checks
# -------------------------

@app.get("/health/live")
def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database not ready")
