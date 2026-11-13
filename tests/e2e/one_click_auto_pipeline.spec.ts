import { test, expect } from "@playwright/test";
import * as path from "path";

test.describe("One-Click Autonomous Pipeline for Beginners", () => {
  const BASE_URL = process.env.FRONTEND_URL || "http://127.0.0.1:5173";

  test("upload messy Excel -> auto-pipeline -> dashboard opens automatically in <60s with KPIs, charts, insights", async ({ page }) => {
    // 1. Visit app
    await page.goto(BASE_URL);

    // Fast sign in with seeded demo user
    const demoBtn = page.getByRole("button", { name: /Fast Sign In|Demo Lead Analyst/i });
    if (await demoBtn.isVisible({ timeout: 5000 })) {
      await demoBtn.click();
    }

    // 2. Navigate to Home / Ingestion screen
    await page.getByRole("button", { name: "Home" }).click();
    await expect(page.getByText("Ingest Any Data. Get Clean Insights in 60 Seconds.")).toBeVisible({ timeout: 15000 });

    // 3. Upload messy Excel file
    const excelPath = path.resolve("sample_data/messy_sales_data.xlsx");
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(excelPath);

    // 4. Verify progress screen appears during pipeline run
    await expect(page.getByText(/Auto-Pipeline running|converting to columnar|Opening|building/i).first()).toBeVisible({ timeout: 10000 });

    // 5. Dashboard opens automatically in under 60 seconds with NO manual clicks
    await expect(page.getByText(/Performance Dashboard/i)).toBeVisible({ timeout: 60000 });

    // 6. Verify Top Cleaning Banner
    await expect(page.getByText(/We cleaned.*issues and built this dashboard from your data/i)).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole("button", { name: "What changed" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Customize" })).toBeVisible();

    // 7. Verify Key Numbers (KPI cards) with "Show how" links
    await expect(page.getByText(/Key Numbers|Key Performance Indicators/i).first()).toBeVisible();
    await expect(page.getByText("Show how").first()).toBeVisible();

    // 8. Verify Recommended Charts & "Why this chart?" tooltips
    const charts = page.locator(".echarts-for-react");
    await expect(charts.first()).toBeVisible({ timeout: 15000 });
    await expect(page.locator('button[title="Why this chart?"]').first()).toBeVisible();

    // 9. Verify Ranked Insights on Dashboard
    await expect(page.getByText(/Top Ranked Insights/i)).toBeVisible({ timeout: 10000 });

    // 10. Open "What changed" modal and verify Undo button
    await page.getByRole("button", { name: "What changed" }).click();
    await expect(page.getByText("What Changed During Auto-Cleaning")).toBeVisible();
    await expect(page.getByRole("button", { name: /Undo Changes/i })).toBeVisible();
  });
});
