import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.db.session import get_db
from backend.app.models.all_models import User, Workspace, WorkspaceMember

logger = logging.getLogger("insightforge.auth")

# Use auto_error=False so get_current_user can explicitly log the failure reason
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token or not token.strip():
        logger.warning("Auth failure (401): Missing or empty Authorization header")
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            logger.warning("Auth failure (401): Missing 'sub' claim in JWT payload")
            raise credentials_exception
    except ExpiredSignatureError:
        logger.warning("Auth failure (401): Token has expired")
        raise credentials_exception
    except JWTClaimsError as ce:
        logger.warning("Auth failure (401): Invalid JWT claims (%s)", str(ce))
        raise credentials_exception
    except JWTError as je:
        logger.warning("Auth failure (401): Bad signature or malformed JWT (%s)", str(je))
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.warning("Auth failure (401): User not found in database for email: %s", email)
        raise credentials_exception
    if not user.is_active:
        logger.warning("Auth failure (400): Inactive user account for email: %s", email)
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user

def check_workspace_role(workspace_id: str, user: User, allowed_roles: list[str], db: Session) -> WorkspaceMember:
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user.id
    ).first()
    if not member:
        # Check if user is superuser
        if user.is_superuser:
            return WorkspaceMember(workspace_id=workspace_id, user_id=user.id, role="Owner")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this workspace")
    if member.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Requires one of roles: {', '.join(allowed_roles)}")
    return member
