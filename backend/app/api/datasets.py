import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.db.session import get_db
from backend.app.models.all_models import Dataset, DatasetVersion, Workspace, User, DashboardSpec, SemanticModel
from backend.app.services.auth_service import get_current_user
from backend.app.services.ingestion import load_dataset_file, save_to_parquet
from backend.app.services.profiling import profile_dataset
from backend.app.services.dataset_service import DatasetService
from backend.app.services.pipeline_service import PipelineService
from backend.app.services.semantic_service import SemanticService
from backend.app.services.dashboard_generator import DashboardGenerator
from backend.app.jobs.queue import JobManager

router = APIRouter(prefix="/datasets", tags=["Datasets"])

class CellEditRequest(BaseModel):
    row_index: int
    column_name: str
    new_value: Any

class PermanentDeleteRequest(BaseModel):
    confirmation_name: str

@router.get("/")
def list_datasets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    datasets = db.query(Dataset).filter(Dataset.is_deleted == False).order_by(Dataset.updated_at.desc()).all()
    return [{
        "id": d.id,
        "name": d.name,
        "description": d.description,
        "file_type": d.file_type,
        "source_type": d.source_type,
        "current_version": d.current_version,
        "row_count": d.row_count,
        "col_count": d.col_count,
        "status": d.status,
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
    } for d in datasets]

@router.post("/demo/{sample_type}")
def load_sample_dataset_endpoint(
    sample_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from backend.app.models.all_models import WorkspaceMember
    member = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).first()
    workspace_id = member.workspace_id if member else db.query(Workspace).first().id

    if sample_type == "cricket":
        file_path = "sample_data/cricket_dataset.csv"
        ext = "csv"
        dataset_name = "Cricket Matches Performance"
        description = "516 match records with runs, opponent, ground, format, and milestone totals."
    elif sample_type == "sales":
        file_path = "sample_data/messy_sales_data.xlsx"
        ext = "xlsx"
        dataset_name = "Messy Retail Sales (Demo)"
        description = "Demonstration dataset with merged cells, subtotals, Indian numbers, currencies, and mixed dates."
    else:
        file_path = "sample_data/web_traffic_timeseries.csv"
        ext = "csv"
        dataset_name = "Web Traffic Time-Series (Demo)"
        description = "180 days of daily web traffic, bounce rate, conversions, and revenue."

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Sample file {file_path} not found on disk.")

    df, parse_meta = load_dataset_file(file_path, ext)
    
    dataset = Dataset(
        workspace_id=workspace_id,
        name=dataset_name,
        description=description,
        file_type=ext,
        source_type="demo",
        current_version=1,
        status="ready",
        row_count=len(df),
        col_count=len(df.columns),
        metadata_json=parse_meta
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    parquet_path = save_to_parquet(df, dataset.id, 1)
    profile = profile_dataset(df)

    version_rec = DatasetVersion(
        dataset_id=dataset.id,
        version_num=1,
        parquet_path=parquet_path,
        raw_file_path=file_path,
        row_count=len(df),
        col_count=len(df.columns),
        schema_json=profile["columns"],
        quality_score=profile["quality_score"]["overall"],
        change_summary="Initial demo ingestion"
    )
    db.add(version_rec)
    db.commit()

    # Trigger Auto-Pipeline (Ingest -> Profile -> Classify -> Auto-Clean -> Semantic -> Dashboard -> Insights)
    job = JobManager.create_job(db, "auto_pipeline", dataset_id=dataset.id, workspace_id=workspace_id)
    pipeline_res = PipelineService.run_auto_pipeline(dataset.id, job.id, workspace_id)

    return {
        "id": dataset.id,
        "name": dataset.name,
        "row_count": dataset.row_count,
        "col_count": dataset.col_count,
        "current_version": dataset.current_version,
        "quality_score": profile["quality_score"],
        "parse_meta": parse_meta,
        "job_id": job.id,
        "pipeline_status": pipeline_res.get("status", "completed"),
        "cleaning_summary": pipeline_res.get("cleaning_summary", {})
    }

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset_name = name or file.filename.rsplit(".", 1)[0]
    filename = file.filename
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "csv"
    
    # Save uploaded raw file
    saved_raw_path = settings.UPLOAD_DIR / f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
    with open(saved_raw_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Get user's primary workspace
    from backend.app.models.all_models import WorkspaceMember
    member = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).first()
    workspace_id = member.workspace_id if member else db.query(Workspace).first().id

    try:
        df, parse_meta = load_dataset_file(str(saved_raw_path), ext)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse data file: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file produced an empty dataset.")

    # Create dataset record
    dataset = Dataset(
        workspace_id=workspace_id,
        name=dataset_name,
        description=description or f"Ingested {ext.upper()} file with {len(df)} rows and {len(df.columns)} columns.",
        file_type=ext,
        source_type="upload",
        current_version=1,
        status="ready",
        row_count=len(df),
        col_count=len(df.columns),
        metadata_json=parse_meta
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    
    # Save parquet v1
    parquet_path = save_to_parquet(df, dataset.id, 1)
    profile = profile_dataset(df)
    
    version_rec = DatasetVersion(
        dataset_id=dataset.id,
        version_num=1,
        parquet_path=parquet_path,
        raw_file_path=str(saved_raw_path),
        row_count=len(df),
        col_count=len(df.columns),
        schema_json=profile["columns"],
        quality_score=profile["quality_score"]["overall"],
        change_summary="Initial ingestion"
    )
    db.add(version_rec)
    db.commit()
    
    # Trigger Auto-Pipeline (Ingest -> Profile -> Classify -> Auto-Clean -> Semantic -> Dashboard -> Insights)
    job = JobManager.create_job(db, "auto_pipeline", dataset_id=dataset.id, workspace_id=workspace_id)
    pipeline_res = PipelineService.run_auto_pipeline(dataset.id, job.id, workspace_id)

    return {
        "id": dataset.id,
        "name": dataset.name,
        "row_count": dataset.row_count,
        "col_count": dataset.col_count,
        "current_version": dataset.current_version,
        "quality_score": profile["quality_score"],
        "parse_meta": parse_meta,
        "job_id": job.id,
        "pipeline_status": pipeline_res.get("status", "completed"),
        "cleaning_summary": pipeline_res.get("cleaning_summary", {})
    }

@router.get("/{dataset_id}")
def get_dataset(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    preview_rows = df.head(100).replace({float("nan"): None}).to_dict(orient="records")
    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
        "file_type": dataset.file_type,
        "current_version": dataset.current_version,
        "row_count": len(df),
        "col_count": len(df.columns),
        "columns": [str(c) for c in df.columns],
        "preview": preview_rows,
        "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None
    }

@router.get("/{dataset_id}/profile")
def get_profile(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _, df = DatasetService.get_dataset_df(db, dataset_id)
    profile = profile_dataset(df)
    return profile

@router.get("/{dataset_id}/versions")
def list_versions(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    versions = db.query(DatasetVersion).filter(DatasetVersion.dataset_id == dataset_id).order_by(DatasetVersion.version_num.desc()).all()
    return [{
        "version_num": v.version_num,
        "row_count": v.row_count,
        "col_count": v.col_count,
        "quality_score": v.quality_score,
        "change_summary": v.change_summary,
        "created_at": v.created_at.isoformat() if v.created_at else None
    } for v in versions]

@router.post("/{dataset_id}/edit-cell")
def edit_cell(
    dataset_id: str, 
    edit_req: CellEditRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    dataset, df = DatasetService.get_dataset_df(db, dataset_id)
    if edit_req.column_name not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{edit_req.column_name}' not found")
    if edit_req.row_index < 0 or edit_req.row_index >= len(df):
        raise HTTPException(status_code=400, detail=f"Row index {edit_req.row_index} out of bounds")
        
    old_val = df.at[edit_req.row_index, edit_req.column_name]
    df.at[edit_req.row_index, edit_req.column_name] = edit_req.new_value
    
    summary = f"Cell edit: row {edit_req.row_index}, col '{edit_req.column_name}': '{old_val}' -> '{edit_req.new_value}'"
    new_ver = DatasetService.create_new_version(db, dataset, df, summary, user_id=current_user.id)
    return {
        "success": True,
        "new_version": new_ver.version_num,
        "message": summary
    }

@router.get("/{dataset_id}/impact")
def get_impact(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return DatasetService.get_deletion_impact(db, dataset_id)

@router.delete("/{dataset_id}/trash")
def move_to_trash(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return DatasetService.soft_delete(db, dataset_id, user_id=current_user.id)

@router.post("/{dataset_id}/restore")
def restore_dataset(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return DatasetService.restore_from_trash(db, dataset_id, user_id=current_user.id)

@router.post("/{dataset_id}/permanent")
def permanent_delete(
    dataset_id: str, 
    req: PermanentDeleteRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return DatasetService.permanent_delete(db, dataset_id, req.confirmation_name, user_id=current_user.id)

@router.post("/{dataset_id}/reanalyze")
@router.post("/{dataset_id}/auto-pipeline")
def trigger_auto_pipeline_endpoint(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """One-click Re-analyze: runs full pipeline on existing dataset."""
    dataset, _ = DatasetService.get_dataset_df(db, dataset_id)
    job = JobManager.create_job(db, "auto_pipeline", dataset_id=dataset.id, workspace_id=dataset.workspace_id)
    pipeline_res = PipelineService.run_auto_pipeline(dataset.id, job.id, dataset.workspace_id)
    return {
        "dataset_id": dataset.id,
        "job_id": job.id,
        "status": pipeline_res.get("status", "completed"),
        "result": pipeline_res
    }

@router.post("/{dataset_id}/undo-clean")
def undo_cleaning_endpoint(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reverts dataset to Version 1 (original immutable raw data) and refreshes dashboard."""
    dataset, _ = DatasetService.get_dataset_df(db, dataset_id)
    v1 = db.query(DatasetVersion).filter(
        DatasetVersion.dataset_id == dataset.id,
        DatasetVersion.version_num == 1
    ).first()
    if not v1:
        raise HTTPException(status_code=404, detail="Initial raw version not found.")
        
    dataset.current_version = 1
    dataset.row_count = v1.row_count
    dataset.col_count = v1.col_count
    db.commit()
    
    # Re-run dashboard on v1
    _, raw_df = DatasetService.get_dataset_df(db, dataset_id)
    sem_dict = SemanticService.build_semantic_layer(raw_df)
    dash_spec = DashboardGenerator.generate_auto_dashboard(
        raw_df,
        sem_dict,
        title=f"{dataset.name} Performance Dashboard (Original Data)",
        cleaning_summary={"issues_fixed_count": 0, "undone": True}
    )
    
    dash = db.query(DashboardSpec).filter(
        DashboardSpec.dataset_id == dataset.id,
        DashboardSpec.version_num == 1
    ).first()
    if dash:
        dash.spec_json = dash_spec
    else:
        dash = DashboardSpec(
            dataset_id=dataset.id,
            workspace_id=dataset.workspace_id,
            name=dash_spec["title"],
            version_num=1,
            spec_json=dash_spec,
            is_default=True
        )
        db.add(dash)
    db.commit()
    
    return {
        "success": True,
        "dataset_id": dataset.id,
        "current_version": 1,
        "message": "Reverted to original immutable data."
    }
