from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.all_models import User
from backend.app.services.auth_service import get_current_user
from backend.app.services.dataset_service import DatasetService
from backend.app.services.cleaning import CleaningService

router = APIRouter(prefix="/clean", tags=["Cleaning Studio"])

class ApplyCleaningRequest(BaseModel):
    approved_steps: List[Dict[str, Any]]

@router.get("/{dataset_id}/plan")
def get_cleaning_plan(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, df = DatasetService.get_dataset_df(db, dataset_id)
    plan = CleaningService.generate_cleaning_plan(df)
    return {
        "dataset_id": dataset_id,
        "proposed_steps": plan,
        "count": len(plan)
    }

@router.post("/{dataset_id}/apply")
def apply_cleaning(
    dataset_id: str,
    req: ApplyCleaningRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    if not req.approved_steps:
        raise HTTPException(status_code=400, detail="No steps provided to apply.")
        
    cleaned_df, report = CleaningService.execute_cleaning_plan(df, req.approved_steps)
    summary = f"Applied {len(report['applied_steps'])} cleaning steps. Quality improved from {report['score_before']['overall']} to {report['score_after']['overall']} (+{report['improvement']})."
    
    new_ver = DatasetService.create_new_version(db, dataset, cleaned_df, summary, user_id=current_user.id)
    
    return {
        "success": True,
        "new_version": new_ver.version_num,
        "report": report
    }
