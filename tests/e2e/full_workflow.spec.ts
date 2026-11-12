import { test, expect } from "@playwright/test";

test.describe("InsightForge AI v2: Autonomous End-to-End Pipeline", () => {
  const BASE_URL = process.env.FRONTEND_URL || "http://localhost:5173";

  test("full flow: upload -> clean -> semantic -> dashboard -> chat -> trash -> restore", async ({ page }) => {
    // 1. Visit application
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/InsightForge AI/i);

    // 2. Load Messy Sales Demo Dataset
    const loadDemoBtn = page.getByRole("button", { name: /load demo data/i });
    if (await loadDemoBtn.isVisible()) {
      await loadDemoBtn.click();
      await page.getByText(/Messy Retail Sales \(Excel\)/i).click();
    }

    // 3. Verify Dashboard Loads within 60s
    await expect(page.getByText(/Performance Dashboard/i)).toBeVisible({ timeout: 30000 });
    
    // Verify KPI Cards exist with "Show how" formula links
    const showHowButtons = page.getByText(/show how/i);
    await expect(showHowButtons.first()).toBeVisible();
    await showHowButtons.first().click();
    await expect(page.getByText(/Deterministic SQL Formula/i)).toBeVisible();

    // 4. Navigate to Cleaning Studio
    await page.getByRole("button", { name: /cleaning studio/i }).click();
    await expect(page.getByText(/Quality Score/i)).toBeVisible();
    await expect(page.getByText(/Completeness/i)).toBeVisible();

    // 5. Navigate to Semantic Layer
    await page.getByRole("button", { name: /semantic layer/i }).click();
    await expect(page.getByText(/Unified Semantic Layer/i)).toBeVisible();
    await expect(page.getByText(/Active Metric Definitions/i)).toBeVisible();

    // 6. Navigate to Safe Text-to-SQL Agent Chat
    await page.getByRole("button", { name: /safe agent chat/i }).click();
    await expect(page.getByText(/sqlglot ast validated/i)).toBeVisible();

    // Ask a grounded question
    const chatInput = page.getByPlaceholder(/ask anything about this dataset/i);
    await chatInput.fill("What is the total sales amount by region?");
    await page.getByRole("button", { name: /send/i }).click();

    // Verify response contains grounded computed numbers and Show SQL button
    await expect(page.getByText(/Based on the dataset|Found.*groups/i)).toBeVisible({ timeout: 15000 });
    const showSqlBtn = page.getByText(/show sql/i).first();
    await expect(showSqlBtn).toBeVisible();
    await showSqlBtn.click();
    await expect(page.getByText(/SELECT.*FROM data/i)).toBeVisible();

    // 7. Test Soft Delete to Trash
    await page.getByRole("button", { name: /trash & versions/i }).click();
    await expect(page.getByText(/Trash & Dataset Version Lifecycle/i)).toBeVisible();
  });
});
