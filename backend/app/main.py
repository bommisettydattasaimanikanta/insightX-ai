from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.db.session import engine, Base, SessionLocal
from backend.app.api.auth import router as auth_router, ensure_default_user_and_workspace
from backend.app.api.datasets import router as datasets_router
from backend.app.api.clean import router as clean_router
from backend.app.api.semantic import router as semantic_router
from backend.app.api.stats import router as stats_router
from backend.app.api.dashboards import router as dashboards_router
from backend.app.api.ml import router as ml_router
from backend.app.api.insights import router as insights_router
from backend.app.api.chat import router as chat_router
from backend.app.api.jobs import router as jobs_router
from backend.app.api.trash import router as trash_router
from backend.app.api.reports import router as reports_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous AI Data Analyst and Dashboard Platform with Grounded Semantic Layer"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        ensure_default_user_and_workspace(db)
    finally:
        db.close()

# Mount all API routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(datasets_router, prefix=settings.API_V1_STR)
app.include_router(clean_router, prefix=settings.API_V1_STR)
app.include_router(semantic_router, prefix=settings.API_V1_STR)
app.include_router(stats_router, prefix=settings.API_V1_STR)
app.include_router(dashboards_router, prefix=settings.API_V1_STR)
app.include_router(ml_router, prefix=settings.API_V1_STR)
app.include_router(insights_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(trash_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": "development"
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to InsightForge AI API (v2)",
        "docs_url": "/docs",
        "health": "/health"
    }
