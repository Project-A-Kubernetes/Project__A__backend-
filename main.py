import uuid
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from app.schemas import Job
from app.telemetry import metrics_middleware, setup_logging

# 1. Setup & App Initialization
setup_logging()
app = FastAPI(title="Job Management API")

# 2. CORS Middleware (Must be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Metrics Exposure
# This creates the /metrics page for Prometheus
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# 4. Custom Metrics Middleware
# This tracks response times and status codes for every request
@app.middleware("http")
async def track_metrics(request: Request, call_next):
    return await metrics_middleware(request, call_next)

# 5. In-Memory Database
db_jobs = []

# 6. Routes
@app.get("/api/jobs", response_model=list[Job])
async def list_jobs():
    return db_jobs

@app.post("/api/jobs", response_model=Job)
async def create_job(job_data: Job):
    job_data.id = uuid.uuid4()
    job_data.created_at = datetime.utcnow()
    job_data.updated_at = datetime.utcnow()
    db_jobs.append(job_data)
    return job_data

@app.patch("/api/jobs/{job_id}", response_model=Job)
async def update_job_status(job_id: uuid.UUID, status: str):
    for job in db_jobs:
        if job.id == job_id:
            job.status = status
            job.updated_at = datetime.utcnow()
            return job
    raise HTTPException(status_code=404, detail="Job not found")

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: uuid.UUID):
    global db_jobs
    initial_length = len(db_jobs)
    db_jobs = [job for job in db_jobs if job.id != job_id]
    
    if len(db_jobs) == initial_length:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

@app.get("/health/live")
async def liveness():
    return {"status": "alive"}
@app.get("/health/ready")

async def readiness():
    # This tells Docker the app is not just "on", but ready
    return {"status": "ready"}