from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.all_models import User, SemanticModel
from backend.app.services.auth_service import get_current_user
from backend.app.services.dataset_service import DatasetService
from backend.app.services.semantic_service import SemanticService
from backend.app.services.insight_engine import InsightEngine

router = APIRouter(prefix="/insights", tags=["Insights & Recommendations"])

# In-memory recommendation status cache for user status updates
_REC_STATUS_STORE: Dict[str, str] = {}

class StatusUpdateRequest(BaseModel):
    status: str  # To-do, Doing, Done

@router.get("/{dataset_id}")
def get_insights(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    sem_model = db.query(SemanticModel).filter(
        SemanticModel.dataset_id == dataset_id,
        SemanticModel.version_num == dataset.current_version
    ).first()
    
    if sem_model:
        sem_dict = {
            "domain": sem_model.domain,
            "metrics": sem_model.metrics_json,
            "dimensions": sem_model.dimensions_json,
            "time_grains": sem_model.time_grains_json,
        }
    else:
        sem_dict = SemanticService.build_semantic_layer(df)
        
    insights = InsightEngine.generate_and_rank_insights(df, sem_dict)
    return {
        "dataset_id": dataset_id,
        "count": len(insights),
        "insights": insights
    }

@router.get("/{dataset_id}/recommendations")
def get_recommendations(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    sem_model = db.query(SemanticModel).filter(
        SemanticModel.dataset_id == dataset_id,
        SemanticModel.version_num == dataset.current_version
    ).first()
    
    sem_dict = {
        "metrics": sem_model.metrics_json,
        "dimensions": sem_model.dimensions_json,
        "time_grains": sem_model.time_grains_json,
    } if sem_model else SemanticService.build_semantic_layer(df)
    
    insights = InsightEngine.generate_and_rank_insights(df, sem_dict)
    recs = InsightEngine.generate_recommendations(insights)
    
    # Apply cached status
    for r in recs:
        if r["id"] in _REC_STATUS_STORE:
            r["status"] = _REC_STATUS_STORE[r["id"]]
            
    return recs

@router.patch("/{dataset_id}/recommendations/{rec_id}")
def update_recommendation_status(
    dataset_id: str,
    rec_id: str,
    req: StatusUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    _REC_STATUS_STORE[rec_id] = req.status
    return {"success": True, "rec_id": rec_id, "status": req.status}
