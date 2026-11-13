from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.app.db.session import get_db
from backend.app.models.all_models import User, Workspace, WorkspaceMember
from backend.app.services.auth_service import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/register", response_model=TokenResponse)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pw = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        full_name=user_in.full_name or user_in.email.split("@")[0]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create default workspace
    workspace = Workspace(name=f"{user.full_name}'s Workspace", owner_id=user.id)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    
    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="Owner")
    db.add(member)
    db.commit()
    
    token = create_access_token({"sub": user.email, "uid": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "workspace_id": workspace.id,
            "role": "Owner"
        }
    }

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
    # Get primary workspace
    member = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == user.id).first()
    workspace_id = member.workspace_id if member else None
    role = member.role if member else "Viewer"
    
    token = create_access_token({"sub": user.email, "uid": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "workspace_id": workspace_id,
            "role": role
        }
    }

@router.get("/demo-token", response_model=TokenResponse)
def get_demo_token(db: Session = Depends(get_db)):
    user, workspace = ensure_default_user_and_workspace(db)
    token = create_access_token({"sub": user.email, "uid": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "workspace_id": workspace.id,
            "role": "Owner"
        }
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).first()
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "workspace_id": member.workspace_id if member else None,
        "role": member.role if member else "Viewer"
    }

def ensure_default_user_and_workspace(db: Session) -> tuple[User, Workspace]:
    """Ensures a default demo user and workspace exists for instant out-of-the-box usage."""
    # Seed InsightX AI primary demo user
    user = db.query(User).filter(User.email.in_(["demo@insightx.ai", "demo@insightforge.ai"])).first()
    if not user:
        user = User(
            email="demo@insightx.ai",
            hashed_password=get_password_hash("insightx123"),
            full_name="Lead Analyst"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        workspace = Workspace(name="Default Analytics Workspace", owner_id=user.id)
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        
        member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="Owner")
        db.add(member)
        db.commit()
        return user, workspace
        
    workspace = db.query(Workspace).filter(Workspace.owner_id == user.id).first()
    return user, workspace
