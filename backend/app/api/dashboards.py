from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.all_models import User, DashboardSpec, SemanticModel
from backend.app.services.auth_service import get_current_user
from backend.app.services.dataset_service import DatasetService
from backend.app.services.semantic_service import SemanticService
from backend.app.services.dashboard_generator import DashboardGenerator

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])

class UpdateDashboardRequest(BaseModel):
    name: Optional[str] = "Overview Dashboard"
    spec: Dict[str, Any]

@router.get("/{dataset_id}")
def get_or_generate_dashboard(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    
    # Check if a dashboard already exists
    dash = db.query(DashboardSpec).filter(
        DashboardSpec.dataset_id == dataset_id,
        DashboardSpec.version_num == dataset.current_version
    ).first()
    
    if dash:
        return {
            "id": dash.id,
            "name": dash.name,
            "version_num": dash.version_num,
            "spec": dash.spec_json
        }
        
    # Get or create semantic layer
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
        
    spec = DashboardGenerator.generate_auto_dashboard(df, sem_dict, title=f"{dataset.name} Performance Dashboard")
    
    new_dash = DashboardSpec(
        dataset_id=dataset_id,
        workspace_id=dataset.workspace_id,
        name=spec["title"],
        version_num=dataset.current_version,
        spec_json=spec,
        is_default=True
    )
    db.add(new_dash)
    db.commit()
    db.refresh(new_dash)
    
    return {
        "id": new_dash.id,
        "name": new_dash.name,
        "version_num": new_dash.version_num,
        "spec": new_dash.spec_json
    }

@router.put("/{dataset_id}")
def update_dashboard(
    dataset_id: str,
    req: UpdateDashboardRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, _ = DatasetService.get_dataset_df(db, dataset_id)
    dash = db.query(DashboardSpec).filter(
        DashboardSpec.dataset_id == dataset_id,
        DashboardSpec.version_num == dataset.current_version
    ).first()
    
    if not dash:
        dash = DashboardSpec(
            dataset_id=dataset_id,
            workspace_id=dataset.workspace_id,
            name=req.name or "Custom Dashboard",
            version_num=dataset.current_version,
            spec_json=req.spec,
            is_default=True
        )
        db.add(dash)
    else:
        dash.name = req.name or dash.name
        dash.spec_json = req.spec
        
    db.commit()
    return {"success": True, "message": "Dashboard spec saved successfully."}
