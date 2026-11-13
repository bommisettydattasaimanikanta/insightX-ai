import math
from typing import Dict, Any, Optional
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.all_models import User, DashboardSpec, SemanticModel
from backend.app.services.auth_service import get_current_user
from backend.app.services.dataset_service import DatasetService
from backend.app.services.semantic_service import SemanticService
from backend.app.services.insight_engine import InsightEngine
from backend.app.services.dashboard_generator import DashboardGenerator
from backend.app.services.export_service import ExportService

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])

def sanitize_spec(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_spec(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_spec(v) for v in obj]
    elif isinstance(obj, tuple):
        return [sanitize_spec(v) for v in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        if np.isnan(obj) or np.isinf(obj):
            return 0.0
        return float(obj)
    return obj

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

    if dash:
        spec = dict(dash.spec_json)
        # Ensure insights and cleaning summary are populated
        if not spec.get("insights"):
            insights = InsightEngine.generate_and_rank_insights(df, sem_dict)
            spec["insights"] = insights[:5]
            dash.spec_json = spec
            db.commit()
            
        return {
            "id": dash.id,
            "name": dash.name,
            "version_num": dash.version_num,
            "spec": sanitize_spec(spec)
        }
        
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
        "spec": sanitize_spec(new_dash.spec_json)
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

@router.get("/{dataset_id}/export/pdf")
def export_dashboard_pdf(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    dash = db.query(DashboardSpec).filter(
        DashboardSpec.dataset_id == dataset_id,
        DashboardSpec.version_num == dataset.current_version
    ).first()
    
    if not dash or not dash.spec_json:
        sem_model = db.query(SemanticModel).filter(
            SemanticModel.dataset_id == dataset_id,
            SemanticModel.version_num == dataset.current_version
        ).first()
        sem_dict = {"metrics": sem_model.metrics_json, "dimensions": sem_model.dimensions_json, "time_grains": sem_model.time_grains_json, "domain": sem_model.domain} if sem_model else SemanticService.build_semantic_layer(df)
        spec = DashboardGenerator.generate_auto_dashboard(df, sem_dict, dataset_name=dataset.name)
    else:
        spec = dash.spec_json

    pdf_bytes = ExportService.export_pdf(spec, user_name=current_user.full_name or "Lead Analyst")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{dataset.name}_dashboard.pdf"'}
    )

@router.get("/{dataset_id}/export/png")
def export_dashboard_png(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    dash = db.query(DashboardSpec).filter(
        DashboardSpec.dataset_id == dataset_id,
        DashboardSpec.version_num == dataset.current_version
    ).first()
    
    spec = dash.spec_json if dash and dash.spec_json else DashboardGenerator.generate_auto_dashboard(df, SemanticService.build_semantic_layer(df), dataset_name=dataset.name)
    png_bytes = ExportService.export_png(spec, user_name=current_user.full_name or "Lead Analyst")
    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{dataset.name}_dashboard.png"'}
    )

@router.get("/{dataset_id}/export/pptx")
def export_dashboard_pptx(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    dash = db.query(DashboardSpec).filter(
        DashboardSpec.dataset_id == dataset_id,
        DashboardSpec.version_num == dataset.current_version
    ).first()
    
    spec = dash.spec_json if dash and dash.spec_json else DashboardGenerator.generate_auto_dashboard(df, SemanticService.build_semantic_layer(df), dataset_name=dataset.name)
    pptx_bytes = ExportService.export_pptx(spec, df, user_name=current_user.full_name or "Lead Analyst")
    return Response(
        content=pptx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{dataset.name}_presentation.pptx"'}
    )

@router.get("/{dataset_id}/export/excel")
def export_dashboard_excel(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    dash = db.query(DashboardSpec).filter(
        DashboardSpec.dataset_id == dataset_id,
        DashboardSpec.version_num == dataset.current_version
    ).first()
    
    spec = dash.spec_json if dash and dash.spec_json else DashboardGenerator.generate_auto_dashboard(df, SemanticService.build_semantic_layer(df), dataset_name=dataset.name)
    excel_bytes = ExportService.export_excel(df, spec)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{dataset.name}_data.xlsx"'}
    )

@router.get("/{dataset_id}/export/csv")
def export_dashboard_csv(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    csv_str = ExportService.export_csv(df)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{dataset.name}_data.csv"'}
    )
