import { test, expect } from "@playwright/test";
test("save/reload/reopen user draft and compare without accepting source facts", async ({
  page,
}) => {
  await page.goto("/?mode=research");
  await page.getByRole("button", { name: "Add venture", exact: true }).click();
  await page.getByLabel("Venture or project name").fill("Synthetic intake browser fixture");
  await page.getByLabel("Aliases (comma separated)").fill("FormusLabs");
  await page
    .getByLabel("Description", { exact: true })
    .fill("clinical images software surgical planning");
  await expect(page.getByText("Possible identity duplicates — unresolved")).toBeVisible();
  await page.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Saved: Synthetic intake browser fixture" }),
  ).toBeVisible();
  await page.reload();
  await page.getByRole("button", { name: "Add venture", exact: true }).click();
  await page
    .getByRole("button", { name: "Synthetic intake browser fixture · revision 1", exact: true })
    .click();
  await expect(page.getByLabel("Description", { exact: true })).toHaveValue(
    "clinical images software surgical planning",
  );
  await page.getByRole("button", { name: "Compare saved draft", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Saved-draft comparison" })).toBeVisible();
  await expect(page.locator(".intake-comparison table")).toContainText("Saved draft · query only");
  await expect(page.locator(".intake-comparison table tbody tr")).toHaveCount(3);
  await page.getByLabel("Candidate evidence policy").selectOption("accepted");
  await page.getByRole("button", { name: "Compare saved draft", exact: true }).click();
  await expect(page.locator(".intake-comparison")).toContainText("No eligible candidate");
  const corpus = await page.request.get("/api/ventures");
  expect((await corpus.json()).total).toBe(10);
});
test("source validation and persistence failure keep typed input", async ({ page }) => {
  await page.goto("/?mode=research");
  await page.getByRole("button", { name: "Add venture", exact: true }).click();
  await page.getByRole("button", { name: "Start another draft" }).click();
  await page.getByLabel("Venture or project name").fill("Synthetic retained input");
  await page.getByRole("button", { name: "Add optional source attribution" }).click();
  await page
    .getByLabel("Attributed claim", { exact: true })
    .fill("Synthetic claim, not real research");
  await page.getByLabel("Source URL", { exact: true }).fill("http://example.org");
  await page.getByLabel("Source title", { exact: true }).fill("Synthetic source");
  await page.getByLabel("Publisher", { exact: true }).fill("Synthetic publisher");
  await page.getByLabel("Passage locator", { exact: true }).fill("Synthetic paragraph");
  await page.getByLabel("Retrieval date", { exact: true }).fill("2026-11-18");
  await page.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("Check required fields");
  await expect(page.getByLabel("Venture or project name")).toHaveValue("Synthetic retained input");
  await page.getByLabel("Source URL", { exact: true }).fill("https://example.org");
  await page.route("**/api/intake/drafts", async (route) => {
    if (route.request().method() === "POST")
      await route.fulfill({ status: 503, contentType: "application/json", body: "{}" });
    else await route.continue();
  });
  await page.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("Your input is retained");
  await expect(page.getByLabel("Attributed claim", { exact: true })).toHaveValue(
    "Synthetic claim, not real research",
  );
  await page.unroute("**/api/intake/drafts");
  await page.getByRole("button", { name: "Retry uncertain save", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Saved: Synthetic retained input" }),
  ).toBeVisible();
});
