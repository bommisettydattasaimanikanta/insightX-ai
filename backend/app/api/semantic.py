from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.all_models import User, SemanticModel
from backend.app.services.auth_service import get_current_user
from backend.app.services.dataset_service import DatasetService
from backend.app.services.semantic_service import SemanticService

router = APIRouter(prefix="/semantic", tags=["Semantic Layer"])

class UpdateSemanticRequest(BaseModel):
    domain: Optional[str] = None
    metrics: List[Dict[str, Any]]
    dimensions: List[Dict[str, Any]]
    time_grains: List[Dict[str, Any]]
    suggested_target: Optional[str] = None
    suggested_ml_task: Optional[str] = None

@router.get("/{dataset_id}")
def get_or_create_semantic_layer(
    dataset_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    
    # Check if record exists in db
    sem_model = db.query(SemanticModel).filter(
        SemanticModel.dataset_id == dataset_id,
        SemanticModel.version_num == dataset.current_version
    ).first()
    
    if sem_model:
        return {
            "domain": sem_model.domain,
            "metrics": sem_model.metrics_json,
            "dimensions": sem_model.dimensions_json,
            "time_grains": sem_model.time_grains_json,
            "suggested_target": sem_model.target_column,
            "suggested_ml_task": sem_model.ml_task_type,
            "confidence": sem_model.confidence
        }
        
    # Auto-generate semantic layer
    generated = SemanticService.build_semantic_layer(df)
    new_sem = SemanticModel(
        dataset_id=dataset_id,
        version_num=dataset.current_version,
        domain=generated["domain"],
        metrics_json=generated["metrics"],
        dimensions_json=generated["dimensions"],
        time_grains_json=generated["time_grains"],
        target_column=generated["suggested_target"],
        ml_task_type=generated["suggested_ml_task"],
        confidence=generated["confidence"]
    )
    db.add(new_sem)
    db.commit()
    return generated

@router.put("/{dataset_id}")
def update_semantic_layer(
    dataset_id: str,
    req: UpdateSemanticRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, _ = DatasetService.get_dataset_df(db, dataset_id)
    sem_model = db.query(SemanticModel).filter(
        SemanticModel.dataset_id == dataset_id,
        SemanticModel.version_num == dataset.current_version
    ).first()
    
    if not sem_model:
        sem_model = SemanticModel(
            dataset_id=dataset_id,
            version_num=dataset.current_version,
            domain=req.domain or "general",
            metrics_json=req.metrics,
            dimensions_json=req.dimensions,
            time_grains_json=req.time_grains,
            target_column=req.suggested_target,
            ml_task_type=req.suggested_ml_task,
            confidence=1.0
        )
        db.add(sem_model)
    else:
        if req.domain:
            sem_model.domain = req.domain
        sem_model.metrics_json = req.metrics
        sem_model.dimensions_json = req.dimensions
        sem_model.time_grains_json = req.time_grains
        sem_model.target_column = req.suggested_target
        sem_model.ml_task_type = req.suggested_ml_task
        
    db.commit()
    return {"success": True, "message": "Semantic layer definitions successfully updated."}
