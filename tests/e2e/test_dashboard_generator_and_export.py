import os
import re
import io
import uuid
import shutil
import pytest
import pdfplumber
from playwright.sync_api import sync_playwright, expect

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")

def test_upload_cricket_to_dashboard_and_download_pdf():
    """
    Playwright End-to-End Test:
    1. Authenticate with seeded Lead Analyst demo account.
    2. Navigate to 'Data Upload'.
    3. Upload cricket dataset (index, runs, opponent, ground, date, match, Match_No, total).
    4. Progress indicator shows real-time pipeline status.
    5. Dashboard opens automatically with sports theme, 4 grounded KPIs, charts, and top opponent table.
    6. Click 'Download' -> 'PDF Document (A4)' to download server-side generated PDF.
    7. Verify downloaded PDF exists and contains exact on-screen numbers (516, 254, Australia).
    """
    unique_id = uuid.uuid4().hex[:6]
    test_csv = os.path.abspath(f"sample_data/cricket_{unique_id}.csv")
    shutil.copyfile(os.path.abspath("sample_data/cricket_dataset.csv"), test_csv)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Step 1: Visit app
            page.goto(FRONTEND_URL)

            # Fast sign in
            demo_btn = page.get_by_role("button", name=re.compile(r"Fast Sign In|Demo Lead Analyst", re.IGNORECASE))
            if demo_btn.is_visible(timeout=5000):
                demo_btn.click()

            # Step 2: Navigate to Data Upload screen
            page.get_by_role("button", name=re.compile(r"Data Upload", re.IGNORECASE)).click()
            expect(page.get_by_text("Ingest Any Data. Get Clean Insights in 60 Seconds.")).to_be_visible(timeout=15000)

            # Step 3: Upload cricket CSV
            file_input = page.locator('input[type="file"]')
            file_input.set_input_files(test_csv)

            # Step 4: Progress bar appears
            expect(page.get_by_text(re.compile(r"Auto-Pipeline running|converting to columnar|Opening|building", re.IGNORECASE)).first).to_be_visible(timeout=10000)

            # Step 5: Dashboard opens automatically with sports domain
            expect(page.get_by_text(re.compile(r"Welcome back, Lead Analyst", re.IGNORECASE))).to_be_visible(timeout=60000)
            expect(page.get_by_text(re.compile(r"SPORTS DOMAIN", re.IGNORECASE))).to_be_visible(timeout=15000)

            # Step 6: Verify 4 Grounded KPI cards
            expect(page.get_by_text("TOTAL MATCHES").first).to_be_visible()
            expect(page.get_by_text("516").first).to_be_visible()

            expect(page.get_by_text("TOTAL RUNS").first).to_be_visible()

            expect(page.get_by_text("HIGHEST MATCH RUNS").first).to_be_visible()
            expect(page.get_by_text("254").first).to_be_visible()

            expect(page.get_by_text("TOP OPPONENT").first).to_be_visible()
            expect(page.get_by_text("Australia").first).to_be_visible()

            # Verify no fake wins/losses widgets
            expect(page.get_by_text(re.compile(r"Matches Won|Matches Lost|Wins/Losses", re.IGNORECASE))).not_to_be_visible()

            # Step 7: Open Download menu and download PDF
            download_btn = page.get_by_role("button", name=re.compile(r"Download", re.IGNORECASE)).first
            download_btn.click()

            pdf_option = page.get_by_text(re.compile(r"PDF Document", re.IGNORECASE)).first
            expect(pdf_option).to_be_visible()

            # Trigger download and verify
            with page.expect_download() as download_info:
                pdf_option.click()

            download = download_info.value
            download_path = download.path()

            assert os.path.exists(download_path), "Downloaded PDF must exist on disk"
            file_size = os.path.getsize(download_path)
            assert file_size > 10000, f"Downloaded PDF size ({file_size} bytes) should be > 10KB"

            # Step 8: Verify numbers in downloaded PDF equal on-screen numbers
            with pdfplumber.open(download_path) as pdf:
                pdf_text = "\n".join([page.extract_text() for page in pdf.pages])

            assert "516" in pdf_text
            assert "254" in pdf_text
            assert "Australia" in pdf_text
            assert "Sports" in pdf_text

            context.close()
            browser.close()
    finally:
        if os.path.exists(test_csv):
            try:
                os.remove(test_csv)
            except Exception:
                pass
