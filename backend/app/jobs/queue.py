import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator
from sqlalchemy.orm import Session
from backend.app.models.all_models import JobRecord
from backend.app.db.session import SessionLocal

class JobManager:
    """Manages asynchronous processing jobs with live status updates for SSE/polling."""
    
    _subscribers: Dict[str, list[asyncio.Queue]] = {}

    @classmethod
    def create_job(cls, db: Session, task_type: str, dataset_id: Optional[str] = None, workspace_id: Optional[str] = None) -> JobRecord:
        job = JobRecord(
            task_type=task_type,
            dataset_id=dataset_id,
            workspace_id=workspace_id,
            status="queued",
            progress_pct=0,
            message="Job queued",
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @classmethod
    def update_job_progress(cls, job_id: str, progress_pct: int, message: str, status: str = "running", result: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        db = SessionLocal()
        try:
            job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
            if job:
                job.progress_pct = progress_pct
                job.message = message
                job.status = status
                if result is not None:
                    job.result_json = result
                if error is not None:
                    job.error = error
                job.updated_at = datetime.utcnow()
                db.commit()
                
                # Notify any active SSE subscribers
                event_data = {
                    "job_id": job_id,
                    "status": status,
                    "progress_pct": progress_pct,
                    "message": message,
                    "error": error,
                    "result": result
                }
                cls.broadcast(job_id, event_data)
        finally:
            db.close()

    @classmethod
    def broadcast(cls, job_id: str, data: dict):
        if job_id in cls._subscribers:
            for q in cls._subscribers[job_id]:
                try:
                    q.put_nowait(data)
                except Exception:
                    pass

    @classmethod
    async def subscribe(cls, job_id: str) -> AsyncGenerator[str, None]:
        q = asyncio.Queue()
        if job_id not in cls._subscribers:
            cls._subscribers[job_id] = []
        cls._subscribers[job_id].append(q)
        try:
            # Yield initial status from db
            db = SessionLocal()
            job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
            if job:
                init_data = {
                    "job_id": job.id,
                    "status": job.status,
                    "progress_pct": job.progress_pct,
                    "message": job.message,
                    "error": job.error,
                    "result": job.result_json,
                }
                yield f"data: {json.dumps(init_data)}\n\n"
            db.close()
            
            while True:
                data = await q.get()
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") in ["completed", "failed"]:
                    break
        finally:
            if job_id in cls._subscribers and q in cls._subscribers[job_id]:
                cls._subscribers[job_id].remove(q)
