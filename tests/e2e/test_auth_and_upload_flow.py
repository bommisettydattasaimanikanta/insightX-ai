import os
import re
import uuid
import pytest
from playwright.sync_api import sync_playwright, expect

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")

def test_auth_route_guard_login_and_upload_e2e():
    """
    End-to-end browser test with Playwright:
    1. Unauthenticated user visits app -> Redirected to Login view.
    2. Register a new user -> Token saved, redirected to dashboard/upload view.
    3. User uploads CSV file -> 200 OK, dataset ingested, appears in datasets dropdown.
    4. User logs out -> Token cleared, redirected back to Login view.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Step 1: Visit app without credentials
        page.goto(FRONTEND_URL)
        
        # Verify Login view is shown (route guard)
        expect(page.get_by_role("button", name="Sign In", exact=True)).to_be_visible(timeout=10000)
        expect(page.get_by_text("InsightForge AI")).to_be_visible()

        # Step 2: Register a new test user
        unique_id = uuid.uuid4().hex[:6]
        test_email = f"e2e_analyst_{unique_id}@insightforge.ai"
        test_pass = "SecurePass123!"
        test_name = f"Analyst {unique_id}"

        # Switch to "Create Account" tab
        page.get_by_role("button", name="Create Account", exact=True).click()
        page.get_by_placeholder("Dr. Alex Rivera").fill(test_name)
        page.get_by_placeholder("analyst@organization.com").fill(test_email)
        page.get_by_placeholder("••••••••••••").fill(test_pass)

        # Click Create Account submit button
        page.get_by_role("button", name="Create Workspace Account").click()

        # Step 3: Verify authenticated view loads & navigate to Data Upload
        expect(page.get_by_text(test_name).first).to_be_visible(timeout=15000)
        page.get_by_role("button", name=re.compile(r"Data Upload|Home", re.IGNORECASE)).click()
        expect(page.get_by_text("Ingest Any Data. Get Clean Insights in 60 Seconds.")).to_be_visible(timeout=15000)

        # Step 4: Upload CSV file
        csv_file_path = os.path.abspath("sample_data/auth_test_sales.csv")
        assert os.path.exists(csv_file_path), f"File {csv_file_path} must exist"

        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(csv_file_path)

        # Step 5: Verify upload success and auto-transition to Dashboard view
        expect(page.get_by_text(re.compile(r"Performance Dashboard", re.IGNORECASE))).to_be_visible(timeout=20000)

        # Verify dataset name appears in dataset dropdown in the header
        expect(page.get_by_text("auth_test_sales").first).to_be_visible(timeout=10000)

        # Step 6: Verify Logout
        logout_btn = page.locator('button[title="Sign Out"]')
        expect(logout_btn).to_be_visible()
        logout_btn.click()

        # Confirm redirected back to Login view
        expect(page.get_by_role("button", name="Sign In", exact=True)).to_be_visible(timeout=10000)
        expect(page.get_by_text("You have logged out successfully.")).to_be_visible()

        context.close()
        browser.close()
