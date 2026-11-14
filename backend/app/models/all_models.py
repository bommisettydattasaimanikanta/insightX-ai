import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

def gen_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspaces = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="workspace", cascade="all, delete-orphan")

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="Editor")  # Owner, Editor, Viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspaces")

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_type = Column(String(50), nullable=False)  # csv, xlsx, json, parquet, sqlite
    source_type = Column(String(50), default="upload")  # upload, db_snapshot, live_query
    current_version = Column(Integer, default=1)
    status = Column(String(50), default="ready")  # processing, ready, error
    row_count = Column(Integer, default=0)
    col_count = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)  # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="datasets")
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")
    dashboards = relationship("DashboardSpec", back_populates="dataset", cascade="all, delete-orphan")
    semantic_models = relationship("SemanticModel", back_populates="dataset", cascade="all, delete-orphan")
    models = relationship("MLModelRecord", back_populates="dataset", cascade="all, delete-orphan")

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    version_num = Column(Integer, nullable=False)
    parquet_path = Column(String(500), nullable=False)
    raw_file_path = Column(String(500), nullable=True)
    row_count = Column(Integer, default=0)
    col_count = Column(Integer, default=0)
    schema_json = Column(JSON, default=dict)
    quality_score = Column(Float, default=100.0)
    change_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dataset = relationship("Dataset", back_populates="versions")

class CleaningStep(Base):
    __tablename__ = "cleaning_steps"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    version_num = Column(Integer, nullable=False)
    step_index = Column(Integer, nullable=False)
    step_type = Column(String(100), nullable=False)  # impute_missing, remove_duplicates, outlier_clip, type_cast, etc.
    column = Column(String(255), nullable=True)
    config_json = Column(JSON, default=dict)
    rows_affected = Column(Integer, default=0)
    status = Column(String(50), default="pending")  # approved, rejected, applied
    created_at = Column(DateTime, default=datetime.utcnow)

class SemanticModel(Base):
    __tablename__ = "semantic_models"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    version_num = Column(Integer, nullable=False)
    domain = Column(String(100), default="general")
    metrics_json = Column(JSON, default=list)  # [{name, label, expression, format, description}]
    dimensions_json = Column(JSON, default=list)  # [{name, label, column, type}]
    time_grains_json = Column(JSON, default=list)  # [{name, column, grains: ['day', 'week', 'month', 'year']}]
    target_column = Column(String(255), nullable=True)
    ml_task_type = Column(String(100), nullable=True)  # classification, regression, time_series
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    dataset = relationship("Dataset", back_populates="semantic_models")

class DashboardSpec(Base):
    __tablename__ = "dashboards"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    version_num = Column(Integer, default=1)
    spec_json = Column(JSON, nullable=False)  # Declarative JSON layout with KPI cards, charts, filters
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    dataset = relationship("Dataset", back_populates="dashboards")

class MLModelRecord(Base):
    __tablename__ = "ml_models"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    name = Column(String(255), nullable=False)
    task_type = Column(String(100), nullable=False)  # regression, classification, clustering, forecast
    target_col = Column(String(255), nullable=True)
    algorithm = Column(String(100), nullable=False)
    metrics_json = Column(JSON, default=dict)  # R2, RMSE, Accuracy, F1, etc.
    model_path = Column(String(500), nullable=False)
    feature_importance_json = Column(JSON, default=list)
    model_card_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dataset = relationship("Dataset", back_populates="models")

ModelMetadata = MLModelRecord

class JobRecord(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=True)
    dataset_id = Column(String(36), nullable=True)
    task_type = Column(String(100), nullable=False)
    status = Column(String(50), default="queued")  # queued, running, completed, failed
    progress_pct = Column(Integer, default=0)
    message = Column(String(500), default="Initializing")
    error = Column(Text, nullable=True)
    result_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    workspace_id = Column(String(36), nullable=True)
    user_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)  # create, update, delete, restore, edit_cell
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(36), nullable=False)
    details_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseConnection(Base):
    __tablename__ = "db_connections"
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    db_type = Column(String(50), nullable=False)  # postgresql, mysql, sqlite, sqlserver
    host = Column(String(255), nullable=True)
    port = Column(Integer, nullable=True)
    database_name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    encrypted_password = Column(String(500), nullable=True)
    is_readonly_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
