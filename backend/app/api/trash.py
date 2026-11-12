from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.all_models import Dataset, User
from backend.app.services.auth_service import get_current_user
from backend.app.services.dataset_service import DatasetService

router = APIRouter(prefix="/trash", tags=["Trash"])

class PermanentDeleteRequest(BaseModel):
    confirmation_name: str

@router.get("/")
def list_trash(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    trashed = db.query(Dataset).filter(Dataset.is_deleted == True).all()
    return [{
        "id": d.id,
        "name": d.name,
        "file_type": d.file_type,
        "row_count": d.row_count,
        "col_count": d.col_count,
        "deleted_at": d.deleted_at.isoformat() if d.deleted_at else None,
    } for d in trashed]

@router.post("/{dataset_id}/restore")
def restore(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return DatasetService.restore_from_trash(db, dataset_id, user_id=current_user.id)

@router.post("/{dataset_id}/permanent")
def permanent_delete(
    dataset_id: str, 
    req: PermanentDeleteRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return DatasetService.permanent_delete(db, dataset_id, req.confirmation_name, user_id=current_user.id)
