import os
import re
import pytest
from playwright.sync_api import sync_playwright, expect

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")

def test_one_click_auto_pipeline_messy_excel_to_dashboard():
    """
    Playwright Test for One-Click Autonomous Pipeline:
    1. Log in.
    2. Upload messy sample Excel (messy_sales_data.xlsx).
    3. Progress screen updates automatically.
    4. Dashboard opens automatically in under 60s with NO manual clicks.
    5. Confirms KPI cards, recommended charts, and ranked insights appear.
    6. Verifies 'What changed' modal and 'Undo' capabilities.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Step 1: Visit app and authenticate with Demo Lead Analyst
        page.goto(FRONTEND_URL)
        
        # Fast sign in with seeded demo user
        demo_btn = page.get_by_role("button", name=re.compile(r"Fast Sign In|Demo Lead Analyst", re.IGNORECASE))
        if demo_btn.is_visible(timeout=5000):
            demo_btn.click()

        # Step 2: Navigate to Ingestion screen
        page.get_by_role("button", name=re.compile(r"Data Upload|Home", re.IGNORECASE)).click()
        expect(page.get_by_text("Ingest Any Data. Get Clean Insights in 60 Seconds.")).to_be_visible(timeout=15000)

        # Step 3: Upload messy Excel file
        excel_path = os.path.abspath("sample_data/messy_sales_data.xlsx")
        assert os.path.exists(excel_path), f"File {excel_path} must exist"

        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(excel_path)

        # Step 4: Verify Progress indicator appears during pipeline run
        expect(page.get_by_text(re.compile(r"Auto-Pipeline running|converting to columnar|Opening|building", re.IGNORECASE)).first).to_be_visible(timeout=10000)

        # Step 5: Dashboard opens automatically in under 60 seconds with NO clicks
        expect(page.get_by_text(re.compile(r"Performance Dashboard", re.IGNORECASE))).to_be_visible(timeout=60000)

        # Step 6: Verify Top Cleaning Banner
        expect(page.get_by_text(re.compile(r"We cleaned.*issues and built this dashboard from your data", re.IGNORECASE))).to_be_visible(timeout=10000)
        expect(page.get_by_role("button", name="What changed")).to_be_visible()
        expect(page.get_by_role("button", name="Customize")).to_be_visible()

        # Step 7: Verify Key Numbers (KPI cards) with "Show how" links
        expect(page.get_by_text(re.compile(r"Key Numbers|Key Performance Indicators", re.IGNORECASE)).first).to_be_visible()
        show_how_btns = page.get_by_text("Show how")
        expect(show_how_btns.first).to_be_visible()

        # Step 8: Verify Recommended Charts & "Why this chart?" buttons
        charts = page.locator(".echarts-for-react")
        expect(charts.first).to_be_visible(timeout=15000)
        expect(page.locator('button[title="Why this chart?"]').first).to_be_visible()

        # Step 9: Verify Ranked Insights on Dashboard
        expect(page.get_by_text(re.compile(r"Top Ranked Insights", re.IGNORECASE))).to_be_visible(timeout=10000)

        # Step 10: Open "What changed" modal and verify before/after score & Undo button
        page.get_by_role("button", name="What changed").click()
        expect(page.get_by_text("What Changed During Auto-Cleaning")).to_be_visible()
        expect(page.get_by_role("button", name=re.compile(r"Undo Changes", re.IGNORECASE))).to_be_visible()

        # Close modal
        page.get_by_role("button", name="Close").click()

        context.close()
        browser.close()
