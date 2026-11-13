import { test, expect } from "@playwright/test";
import * as path from "path";

test.describe("Auth Flow & CSV Upload End-to-End", () => {
  const BASE_URL = process.env.FRONTEND_URL || "http://127.0.0.1:5173";

  test("route guard -> register -> login -> upload CSV -> confirm dataset -> logout", async ({ page }) => {
    // 1. Visit app without session -> routed to login
    await page.goto(BASE_URL);
    await expect(page.getByRole("button", { name: "Sign In", exact: true })).toBeVisible({ timeout: 10000 });

    // 2. Register a new user
    const uniqueId = Math.random().toString(36).substring(2, 8);
    const testEmail = `playwright_${uniqueId}@insightforge.ai`;
    const testName = `Playwright Analyst ${uniqueId}`;

    await page.getByRole("button", { name: "Create Account", exact: true }).click();
    await page.getByPlaceholder("Dr. Alex Rivera").fill(testName);
    await page.getByPlaceholder("analyst@organization.com").fill(testEmail);
    await page.getByPlaceholder("••••••••••••").fill("SecurePass123!");
    await page.getByRole("button", { name: "Create Workspace Account" }).click();

    // 3. Confirm redirected to authenticated view
    await expect(page.getByText("Ingest Any Data. Get Clean Insights in 60 Seconds.")).toBeVisible({ timeout: 15000 });
    await expect(page.getByText(testName)).toBeVisible();

    // 4. Upload CSV file
    const filePath = path.resolve("sample_data/auth_test_sales.csv");
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(filePath);

    // 5. Confirm upload succeeds and transitions to cleaning/dashboard
    await expect(page.getByRole("heading", { name: "Cleaning Studio" })).toBeVisible({ timeout: 20000 });
    await expect(page.getByText("auth_test_sales").first()).toBeVisible({ timeout: 10000 });

    // 6. Test logout
    await page.locator('button[title="Sign Out"]').click();
    await expect(page.getByRole("button", { name: "Sign In", exact: true })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("You have logged out successfully.")).toBeVisible();
  });
});
