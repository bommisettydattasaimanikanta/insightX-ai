import os
import json
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# Explicitly load .env from the project root
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PARQUET_DIR = DATA_DIR / "parquet"
MODELS_DIR = DATA_DIR / "saved_models"

for p in [DATA_DIR, UPLOAD_DIR, PARQUET_DIR, MODELS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "InsightX AI"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    # Load strictly from .env with fallback
    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY", "insightx-super-secret-jwt-key-change-in-production-min32chars")
    )
    ALGORITHM: str = Field(default=os.getenv("ALGORITHM", "HS256"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # Minimum 60 mins, default 1440 mins (24 hrs)
    )
    
    DATA_DIR: Path = DATA_DIR
    UPLOAD_DIR: Path = UPLOAD_DIR
    PARQUET_DIR: Path = PARQUET_DIR
    MODELS_DIR: Path = MODELS_DIR
    
    DB_URL: str = os.getenv("DB_URL", f"sqlite:///{DATA_DIR / 'insightforge_meta.db'}")
    UPLOAD_MAX_BYTES: int = 200 * 1024 * 1024  # 200 MB
    
    # CORS Origins
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    
    # Sandbox Limits
    SANDBOX_TIMEOUT_SECONDS: int = 10
    SANDBOX_MAX_MEMORY_MB: int = 512
    MAX_QUERY_ROWS: int = 10000
    
    PRIVACY_MODE_DEFAULT: bool = False

    class Config:
        env_file = str(ENV_PATH)
        extra = "allow"

settings = Settings()
