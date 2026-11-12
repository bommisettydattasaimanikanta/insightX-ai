import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.api.auth import ensure_default_user_and_workspace
from backend.app.services.auth_service import create_access_token

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

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_auth_me(auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "demo@insightforge.ai"

def test_upload_messy_excel(auth_headers):
    with open("sample_data/messy_sales_data.xlsx", "rb") as f:
        response = client.post(
            "/api/datasets/upload",
            headers=auth_headers,
            files={"file": ("messy_sales.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"name": "Messy Sales Automated Test"}
        )
    assert response.status_code == 200
    res_data = response.json()
    dataset_id = res_data["id"]
    assert dataset_id is not None
    assert res_data["row_count"] > 0
    assert "quality_score" in res_data

    # Test profile
    prof_resp = client.get(f"/api/datasets/{dataset_id}/profile", headers=auth_headers)
    assert prof_resp.status_code == 200
    assert "quality_score" in prof_resp.json()

    # Test auto-dashboard generation
    dash_resp = client.get(f"/api/dashboards/{dataset_id}", headers=auth_headers)
    assert dash_resp.status_code == 200
    dash_json = dash_resp.json()
    assert len(dash_json["spec"]["kpi_cards"]) > 0
    assert len(dash_json["spec"]["charts"]) > 0

    # Test chat agent safe query
    chat_resp = client.post(
        f"/api/chat/{dataset_id}/query",
        headers=auth_headers,
        json={"question": "What is the total sales amount by region?"}
    )
    assert chat_resp.status_code == 200
    chat_json = chat_resp.json()
    assert chat_json["can_answer"] is True
    assert "SELECT" in chat_json["sql"].upper()
    assert len(chat_json["data"]) > 0

    # Test delete and restore
    del_resp = client.delete(f"/api/datasets/{dataset_id}/trash", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    restore_resp = client.post(f"/api/datasets/{dataset_id}/restore", headers=auth_headers)
    assert restore_resp.status_code == 200
    assert restore_resp.json()["success"] is True
