from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.all_models import JobRecord
from backend.app.jobs.queue import JobManager

router = APIRouter(prefix="/jobs", tags=["Background Jobs"])

@router.get("/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "task_type": job.task_type,
        "status": job.status,
        "progress_pct": job.progress_pct,
        "message": job.message,
        "error": job.error,
        "result": job.result_json
    }

@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str):
    return StreamingResponse(
        JobManager.subscribe(job_id),
        media_type="text/event-stream"
    )
