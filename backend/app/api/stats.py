from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.all_models import User
from backend.app.services.auth_service import get_current_user
from backend.app.services.dataset_service import DatasetService
from backend.app.services.statistics import StatisticsService

router = APIRouter(prefix="/stats", tags=["Statistical Analysis"])

@router.get("/{dataset_id}/correlations")
def get_correlations(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, df = DatasetService.get_dataset_df(db, dataset_id)
    return StatisticsService.compute_correlations(df)

@router.get("/{dataset_id}/hypothesis")
def get_hypothesis_tests(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, df = DatasetService.get_dataset_df(db, dataset_id)
    return StatisticsService.run_hypothesis_tests(df)

@router.get("/{dataset_id}/trends")
def get_trends(
    dataset_id: str,
    time_col: str = Query(...),
    metric_col: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _, df = DatasetService.get_dataset_df(db, dataset_id)
    return StatisticsService.detect_trends_and_seasonality(df, time_col, metric_col)
