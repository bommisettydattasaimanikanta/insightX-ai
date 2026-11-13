import pytest
import io
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

def test_upload_without_token_returns_401():
    """Upload endpoint without Authorization header must return 401 Unauthorized."""
    csv_content = b"region,sales\nNorth,100\n"
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("unauth_test.csv", io.BytesIO(csv_content), "text/csv")},
        data={"name": "Unauthenticated Dataset"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_upload_with_invalid_token_returns_401():
    """Upload endpoint with an invalid or corrupted JWT must return 401 Unauthorized."""
    csv_content = b"region,sales\nNorth,100\n"
    response = client.post(
        "/api/datasets/upload",
        headers={"Authorization": "Bearer invalid.jwt.token.here"},
        files={"file": ("bad_token_test.csv", io.BytesIO(csv_content), "text/csv")},
        data={"name": "Bad Token Dataset"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_auth_me_without_token_returns_401():
    """GET /api/auth/me without token must return 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_register_login_upload_e2e_flow():
    """
    Test end-to-end flow:
    1. Register a new user -> 200 + access_token
    2. Login with credentials -> 200 + access_token
    3. Validate session with /api/auth/me -> 200 + user profile
    4. Upload a CSV with valid token -> 200 + dataset created
    5. List datasets with valid token -> dataset is present
    """
    import uuid
    unique_suffix = uuid.uuid4().hex[:6]
    test_email = f"analyst_{unique_suffix}@insightforge.ai"
    test_password = "SecurePassword123!"
    full_name = f"Test Analyst {unique_suffix}"

    # 1. Register
    reg_response = client.post(
        "/api/auth/register",
        json={"email": test_email, "password": test_password, "full_name": full_name}
    )
    assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
    reg_data = reg_response.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == test_email

    # 2. Login
    login_response = client.post(
        "/api/auth/login",
        data={"username": test_email, "password": test_password}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    login_data = login_response.json()
    token = login_data["access_token"]
    assert token is not None
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 3. Validate session (/api/auth/me)
    me_response = client.get("/api/auth/me", headers=auth_headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == test_email
    assert me_data["full_name"] == full_name
    assert me_data["workspace_id"] is not None

    # 4. Upload CSV with valid token
    csv_bytes = b"product,revenue,orders,date\nAlpha,1500,12,2026-01-01\nBeta,3200,25,2026-01-02\nGamma,4800,40,2026-01-03\n"
    upload_response = client.post(
        "/api/datasets/upload",
        headers=auth_headers,
        files={"file": ("sales_pipeline.csv", io.BytesIO(csv_bytes), "text/csv")},
        data={"name": f"Pipeline Sales {unique_suffix}", "description": "End-to-end auth test dataset"}
    )
    assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
    upload_data = upload_response.json()
    dataset_id = upload_data["id"]
    assert dataset_id is not None
    assert upload_data["row_count"] == 3
    assert upload_data["col_count"] == 4
    assert "quality_score" in upload_data

    # 5. Confirm dataset appears in dataset list
    list_response = client.get("/api/datasets/", headers=auth_headers)
    assert list_response.status_code == 200
    datasets_list = list_response.json()
    created_dataset = next((d for d in datasets_list if d["id"] == dataset_id), None)
    assert created_dataset is not None
    assert created_dataset["name"] == f"Pipeline Sales {unique_suffix}"
    assert created_dataset["row_count"] == 3
