import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PARQUET_DIR = DATA_DIR / "parquet"
MODELS_DIR = DATA_DIR / "saved_models"

for p in [DATA_DIR, UPLOAD_DIR, PARQUET_DIR, MODELS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "InsightForge AI"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "insightforge-dev-secret-key-32-chars-long-at-least")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    DATA_DIR: Path = DATA_DIR
    UPLOAD_DIR: Path = UPLOAD_DIR
    PARQUET_DIR: Path = PARQUET_DIR
    MODELS_DIR: Path = MODELS_DIR
    
    DB_URL: str = os.getenv("DB_URL", f"sqlite:///{DATA_DIR / 'insightforge_meta.db'}")
    UPLOAD_MAX_BYTES: int = 200 * 1024 * 1024  # 200 MB
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")  # gemini, openai, anthropic, mock
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    
    # Sandbox Limits
    SANDBOX_TIMEOUT_SECONDS: int = 10
    SANDBOX_MAX_MEMORY_MB: int = 512
    MAX_QUERY_ROWS: int = 10000
    
    # Privacy Mode
    PRIVACY_MODE_DEFAULT: bool = False

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
