import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import duckdb
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.app.config import settings
from backend.app.models.all_models import (
    Dataset, DatasetVersion, DashboardSpec, MLModelRecord, 
    SemanticModel, AuditLog
)
from backend.app.services.ingestion import load_dataset_file, save_to_parquet
from backend.app.services.profiling import profile_dataset

class DatasetService:
    
    @staticmethod
    def get_dataset_df(db: Session, dataset_id: str, version: Optional[int] = None) -> Tuple[Dataset, pd.DataFrame]:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        if dataset.is_deleted:
            raise HTTPException(status_code=400, detail="Dataset is in Trash")
            
        ver_num = version or dataset.current_version
        version_rec = db.query(DatasetVersion).filter(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.version_num == ver_num
        ).first()
        if not version_rec or not os.path.exists(version_rec.parquet_path):
            raise HTTPException(status_code=404, detail=f"Data version {ver_num} not found on disk")
            
        df = pd.read_parquet(version_rec.parquet_path)
        return dataset, df

    @staticmethod
    def query_duckdb(dataset_id: str, parquet_path: str, sql_query: str) -> List[Dict[str, Any]]:
        """Safely executes a query on the dataset's parquet file using DuckDB."""
        con = duckdb.connect(database=":memory:")
        # Register the parquet file as a virtual table named 'data' or 'dataset'
        con.execute(f"CREATE VIEW data AS SELECT * FROM read_parquet('{parquet_path}')")
        con.execute(f"CREATE VIEW dataset AS SELECT * FROM data")
        
        rel = con.execute(sql_query)
        columns = [desc[0] for desc in rel.description]
        rows = rel.fetchall()
        con.close()
        
        result = []
        for r in rows:
            row_dict = {}
            for col_name, val in zip(columns, r):
                if isinstance(val, (datetime, pd.Timestamp)):
                    row_dict[col_name] = str(val)
                elif pd.isna(val):
                    row_dict[col_name] = None
                else:
                    row_dict[col_name] = val
            result.append(row_dict)
        return result

    @staticmethod
    def detect_schema_drift(old_df: pd.DataFrame, new_df: pd.DataFrame) -> Dict[str, Any]:
        """Detects column additions, deletions, and data type shifts."""
        old_cols = {c: str(old_df[c].dtype) for c in old_df.columns}
        new_cols = {c: str(new_df[c].dtype) for c in new_df.columns}
        
        added = [c for c in new_cols if c not in old_cols]
        missing = [c for c in old_cols if c not in new_cols]
        type_changes = []
        
        for c in old_cols:
            if c in new_cols and old_cols[c] != new_cols[c]:
                type_changes.append({
                    "column": c,
                    "old_type": old_cols[c],
                    "new_type": new_cols[c],
                })
                
        has_drift = bool(added or missing or type_changes)
        return {
            "has_drift": has_drift,
            "added_columns": added,
            "missing_columns": missing,
            "type_changes": type_changes,
            "old_columns_count": len(old_cols),
            "new_columns_count": len(new_cols),
            "recommendation": "Map missing columns or accept schema evolution." if has_drift else "Schema perfectly matches."
        }

    @staticmethod
    def create_new_version(
        db: Session,
        dataset: Dataset,
        df: pd.DataFrame,
        change_summary: str,
        user_id: Optional[str] = None
    ) -> DatasetVersion:
        """Saves updated dataframe as the next immutable version."""
        new_version_num = dataset.current_version + 1
        parquet_path = save_to_parquet(df, dataset.id, new_version_num)
        
        profile = profile_dataset(df)
        quality_score = profile["quality_score"]["overall"]
        
        version_rec = DatasetVersion(
            dataset_id=dataset.id,
            version_num=new_version_num,
            parquet_path=parquet_path,
            row_count=len(df),
            col_count=len(df.columns),
            schema_json=profile["columns"],
            quality_score=quality_score,
            change_summary=change_summary,
        )
        db.add(version_rec)
        
        dataset.current_version = new_version_num
        dataset.row_count = len(df)
        dataset.col_count = len(df.columns)
        dataset.updated_at = datetime.utcnow()
        
        # Log to audit trail
        audit = AuditLog(
            workspace_id=dataset.workspace_id,
            user_id=user_id,
            action="create_version",
            entity_type="dataset",
            entity_id=dataset.id,
            details_json={"version": new_version_num, "change": change_summary}
        )
        db.add(audit)
        
        db.commit()
        db.refresh(version_rec)
        return version_rec

    @staticmethod
    def get_deletion_impact(db: Session, dataset_id: str) -> Dict[str, Any]:
        """Checks dependent dashboards, semantic models, and ML models."""
        dashboards_count = db.query(DashboardSpec).filter(DashboardSpec.dataset_id == dataset_id).count()
        models_count = db.query(MLModelRecord).filter(MLModelRecord.dataset_id == dataset_id).count()
        semantics_count = db.query(SemanticModel).filter(SemanticModel.dataset_id == dataset_id).count()
        
        has_dependencies = (dashboards_count > 0 or models_count > 0 or semantics_count > 0)
        return {
            "dataset_id": dataset_id,
            "has_dependencies": has_dependencies,
            "dashboards_count": dashboards_count,
            "models_count": models_count,
            "semantics_count": semantics_count,
            "message": f"{dashboards_count} dashboard(s), {models_count} model(s), and {semantics_count} semantic layer(s) depend on this dataset."
        }

    @staticmethod
    def soft_delete(db: Session, dataset_id: str, user_id: Optional[str] = None):
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        dataset.is_deleted = True
        dataset.deleted_at = datetime.utcnow()
        
        audit = AuditLog(
            workspace_id=dataset.workspace_id,
            user_id=user_id,
            action="soft_delete",
            entity_type="dataset",
            entity_id=dataset.id,
            details_json={"name": dataset.name}
        )
        db.add(audit)
        db.commit()
        return {"success": True, "message": "Dataset moved to Trash. Available for restore for 30 days."}

    @staticmethod
    def restore_from_trash(db: Session, dataset_id: str, user_id: Optional[str] = None):
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        dataset.is_deleted = False
        dataset.deleted_at = None
        
        audit = AuditLog(
            workspace_id=dataset.workspace_id,
            user_id=user_id,
            action="restore",
            entity_type="dataset",
            entity_id=dataset.id,
            details_json={"name": dataset.name}
        )
        db.add(audit)
        db.commit()
        return {"success": True, "message": "Dataset restored from Trash."}

    @staticmethod
    def permanent_delete(db: Session, dataset_id: str, confirmation_name: str, user_id: Optional[str] = None):
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        if dataset.name != confirmation_name.strip():
            raise HTTPException(status_code=400, detail=f"Confirmation name mismatch. Expected '{dataset.name}'")
            
        # Delete parquet files on disk
        versions = db.query(DatasetVersion).filter(DatasetVersion.dataset_id == dataset_id).all()
        for v in versions:
            if v.parquet_path and os.path.exists(v.parquet_path):
                try:
                    os.remove(v.parquet_path)
                except Exception:
                    pass
                    
        # Delete dataset and cascading records
        db.delete(dataset)
        db.commit()
        return {"success": True, "message": f"Dataset '{confirmation_name}' permanently deleted."}
