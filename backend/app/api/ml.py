from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.all_models import User, MLModelRecord
from backend.app.services.auth_service import get_current_user
from backend.app.services.dataset_service import DatasetService
from backend.app.ml.automl import AutoMLTrainer
from backend.app.ml.forecasting import TimeSeriesForecaster
from backend.app.services.decision_support import DecisionSupportService

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

class TrainRequest(BaseModel):
    target_column: str

class ForecastRequest(BaseModel):
    time_column: str
    metric_column: str
    horizon: int = 30

class WhatIfRequest(BaseModel):
    model_name: str
    base_features: Dict[str, float]
    feature_tweaks: Dict[str, float]

class GoalSeekRequest(BaseModel):
    model_name: str
    base_features: Dict[str, float]
    target_feature: str
    desired_output: float

@router.post("/{dataset_id}/train")
def train_model(
    dataset_id: str,
    req: TrainRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    if req.target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column '{req.target_column}' not found.")
        
    model_save_name = f"{dataset_id}_{req.target_column}_{dataset.current_version}"
    try:
        results = AutoMLTrainer.train_and_evaluate(df, req.target_column, model_save_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save to database
    record = MLModelRecord(
        dataset_id=dataset_id,
        name=model_save_name,
        task_type=results["task_type"],
        target_col=req.target_column,
        algorithm=results["best_algorithm"],
        metrics_json=results["leaderboard"],
        model_path=results["model_path"],
        feature_importance_json=results["feature_importance"],
        model_card_json=results["model_card"]
    )
    db.add(record)
    db.commit()
    return results

@router.post("/{dataset_id}/forecast")
def run_forecast(
    dataset_id: str,
    req: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _, df = DatasetService.get_dataset_df(db, dataset_id)
    if req.time_column not in df.columns or req.metric_column not in df.columns:
        raise HTTPException(status_code=400, detail="Specified time or metric column does not exist in dataset.")
        
    try:
        return TimeSeriesForecaster.forecast(df, req.time_column, req.metric_column, req.horizon)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{dataset_id}/what-if")
def simulate_what_if(
    dataset_id: str,
    req: WhatIfRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    model_record = db.query(MLModelRecord).filter(
        MLModelRecord.dataset_id == dataset_id,
        MLModelRecord.name == req.model_name
    ).first()
    if not model_record:
        raise HTTPException(status_code=404, detail="Model record not found.")
        
    try:
        return DecisionSupportService.simulate_what_if(model_record.model_path, req.base_features, req.feature_tweaks)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{dataset_id}/tornado")
def get_tornado(
    dataset_id: str,
    model_name: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    model_record = db.query(MLModelRecord).filter(
        MLModelRecord.dataset_id == dataset_id,
        MLModelRecord.name == model_name
    ).first()
    if not model_record:
        raise HTTPException(status_code=404, detail="Model record not found.")
        
    # Get median baseline values from dataset
    _, df = DatasetService.get_dataset_df(db, dataset_id)
    base_features = {c: float(df[c].median()) for c in df.select_dtypes(include=['number']).columns}
    
    return DecisionSupportService.sensitivity_tornado(model_record.model_path, base_features)

@router.post("/{dataset_id}/goal-seek")
def run_goal_seek(
    dataset_id: str,
    req: GoalSeekRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    model_record = db.query(MLModelRecord).filter(
        MLModelRecord.dataset_id == dataset_id,
        MLModelRecord.name == req.model_name
    ).first()
    if not model_record:
        raise HTTPException(status_code=404, detail="Model record not found.")
        
    try:
        return DecisionSupportService.goal_seek(
            model_record.model_path, 
            req.base_features, 
            req.target_feature, 
            req.desired_output
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
