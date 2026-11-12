from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.all_models import User, SemanticModel, DatasetVersion
from backend.app.services.auth_service import get_current_user
from backend.app.services.dataset_service import DatasetService
from backend.app.services.semantic_service import SemanticService
from backend.app.agents.text_to_sql import SafeTextToSQLAgent

router = APIRouter(prefix="/chat", tags=["Agentic Chatbot"])

class ChatQueryRequest(BaseModel):
    question: str
    history: Optional[List[Dict[str, str]]] = None
    privacy_mode: Optional[bool] = False

@router.post("/{dataset_id}/query")
def chat_query(
    dataset_id: str,
    req: ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    version_rec = db.query(DatasetVersion).filter(
        DatasetVersion.dataset_id == dataset_id,
        DatasetVersion.version_num == dataset.current_version
    ).first()
    
    if not version_rec or not version_rec.parquet_path:
        raise HTTPException(status_code=404, detail="Parquet data file not found.")

    # Fetch semantic layer
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

    # Execute safe grounded query
    response = SafeTextToSQLAgent.query(
        question=req.question,
        parquet_path=version_rec.parquet_path,
        semantic_layer=sem_dict,
        conversation_history=req.history
    )
    return response
