import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.api.auth import ensure_default_user_and_workspace
from backend.app.services.auth_service import create_access_token
from backend.app.services.pipeline_service import PipelineService
from backend.app.services.dataset_service import DatasetService
from backend.app.services.cleaning import CleaningService
from backend.app.services.insight_engine import InsightEngine
from backend.app.models.all_models import Dataset, DashboardSpec

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    db = SessionLocal()
    user, workspace = ensure_default_user_and_workspace(db)
    db.close()
    return user, workspace

@pytest.fixture
def auth_headers(setup_db):
    user, _ = setup_db
    token = create_access_token({"sub": user.email, "uid": user.id})
    return {"Authorization": f"Bearer {token}"}

def test_auto_pipeline_success_end_to_end(auth_headers):
    """
    Test that the autonomous pipeline runs all 7 steps end-to-end:
    Ingest -> Profile -> Classify -> Auto-Clean -> Build Semantic Layer -> Generate Dashboard -> Rank Insights.
    """
    with open("sample_data/messy_sales_data.xlsx", "rb") as f:
        upload_resp = client.post(
            "/api/datasets/upload",
            headers=auth_headers,
            files={"file": ("messy_sales_e2e.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"name": "Pipeline Resilience Test Dataset"}
        )
    assert upload_resp.status_code == 200, f"Upload failed: {upload_resp.text}"
    data = upload_resp.json()
    dataset_id = data["id"]
    assert dataset_id is not None
    assert data["pipeline_status"] == "completed"

    # Verify Dashboard Spec was auto-built
    dash_resp = client.get(f"/api/dashboards/{dataset_id}", headers=auth_headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()["spec"]

    # Verify 4-6 KPI cards exist
    assert len(dash_data["kpi_cards"]) >= 4
    # Verify recommended charts exist with plain-English descriptions and tooltips
    assert len(dash_data["charts"]) >= 4
    for chart in dash_data["charts"]:
        assert "description" in chart
        assert "why_this_chart" in chart
    # Verify top ranked insights are present
    assert len(dash_data.get("insights", [])) > 0

def test_pipeline_step_failure_is_skipped_without_crashing_job(auth_headers):
    """
    CRITICAL REQUIREMENT: A failure in one step must not kill the job.
    Mark that step 'skipped' with a reason and continue with what is available.
    
    Here we simulate an unexpected crash in Step 4 (Auto-Clean).
    The pipeline must record Step 4 as 'skipped' and continue successfully
    through Semantic Layer, Dashboard, and Insights.
    """
    # 1. Create a dataset
    with open("sample_data/messy_sales_data.xlsx", "rb") as f:
        res = client.post(
            "/api/datasets/upload",
            headers=auth_headers,
            files={"file": ("fail_step4.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"name": "Step 4 Fail Test"}
        )
    dataset_id = res.json()["id"]

    # 2. Re-run pipeline with Step 4 raising an unexpected exception
    with patch.object(CleaningService, "auto_clean_safe_defaults", side_effect=RuntimeError("Simulated safe-cleaning engine exception")):
        pipeline_res = PipelineService.run_auto_pipeline(dataset_id)

    # 3. Verify job did NOT crash
    assert pipeline_res["status"] == "completed"
    
    # 4. Check step logs
    step_logs = {s["step"]: s for s in pipeline_res["step_logs"]}
    assert "Auto-Clean" in step_logs
    assert step_logs["Auto-Clean"]["status"] == "skipped"
    assert "Simulated safe-cleaning engine exception" in step_logs["Auto-Clean"]["reason"]

    # 5. Confirm downstream steps still completed
    assert step_logs["Semantic Layer"]["status"] == "completed"
    assert step_logs["Dashboard"]["status"] == "completed"
    assert step_logs["Insights"]["status"] == "completed"

def test_pipeline_insights_failure_is_skipped_without_crashing_job(auth_headers):
    """
    Simulate failure in Step 7 (Insights).
    The pipeline must mark Step 7 as 'skipped' and successfully return the dashboard.
    """
    with open("sample_data/messy_sales_data.xlsx", "rb") as f:
        res = client.post(
            "/api/datasets/upload",
            headers=auth_headers,
            files={"file": ("fail_step7.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"name": "Step 7 Fail Test"}
        )
    dataset_id = res.json()["id"]

    with patch.object(InsightEngine, "generate_and_rank_insights", side_effect=ValueError("Simulated statistical test error")):
        pipeline_res = PipelineService.run_auto_pipeline(dataset_id)

    assert pipeline_res["status"] == "completed"
    step_logs = {s["step"]: s for s in pipeline_res["step_logs"]}
    assert step_logs["Insights"]["status"] == "skipped"
    assert "Simulated statistical test error" in step_logs["Insights"]["reason"]
    assert step_logs["Dashboard"]["status"] == "completed"

def test_reanalyze_and_undo_clean_endpoints(auth_headers):
    """
    Test one-click 'Re-analyze' and 'Undo clean' endpoints.
    """
    with open("sample_data/messy_sales_data.xlsx", "rb") as f:
        res = client.post(
            "/api/datasets/upload",
            headers=auth_headers,
            files={"file": ("undo_test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"name": "Undo Test Dataset"}
        )
    dataset_id = res.json()["id"]

    # Test Re-analyze
    reanalyze_resp = client.post(f"/api/datasets/{dataset_id}/reanalyze", headers=auth_headers)
    assert reanalyze_resp.status_code == 200
    assert reanalyze_resp.json()["status"] == "completed"

    # Test Undo-clean
    undo_resp = client.post(f"/api/datasets/{dataset_id}/undo-clean", headers=auth_headers)
    assert undo_resp.status_code == 200
    assert undo_resp.json()["current_version"] == 1
    assert "Reverted to original immutable data" in undo_resp.json()["message"]
