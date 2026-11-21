import { test, expect } from "@playwright/test";

test("browse, filter, inspect and unknowns", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/?mode=research");
  await expect(page.getByRole("heading", { name: "Venture directory" })).toBeVisible();
  await expect(page.locator(".venture-card")).toHaveCount(10);
  await page.getByLabel("Recorded programme").selectOption("velocity_ideas");
  await page.getByLabel("Award year", { exact: true }).selectOption("2026");
  await expect(page.locator(".venture-card")).toHaveCount(2);
  await page.getByRole("button", { name: "Reset filters", exact: true }).click();
  await expect(page.locator(".venture-card")).toHaveCount(10);
  await page.getByLabel("Search ventures").fill("FormusLabs");
  await expect(page.locator(".venture-card")).toHaveCount(1);
  await page.locator(".venture-open").click();
  await expect(
    page.locator(".profile").getByRole("heading", { name: "Formus Labs", exact: true }),
  ).toBeVisible();
  await expect(page.locator(".profile")).toContainText("Unknown / unverified");
  await expect(page.locator(".profile")).toContainText("No award recorded");
  const source = page.locator(".profile .source a").first();
  await expect(source).toHaveAttribute("href", /formuslabs-raises/);
  await expect(page.locator(".profile")).toContainText("Published 2022-06-29");
  await expect(page.locator(".profile")).toContainText("Retrieved 2026-11-16");
  await page.getByText("Proposed analyst annotations · 5 proposals", { exact: true }).click();
  await expect(page.locator(".proposals")).toContainText("Excluded from comparison inputs");
  await page.getByRole("button", { name: "Close profile", exact: true }).click();
  await expect(page.locator(".venture-open")).toBeFocused();
  await page.getByRole("button", { name: "Reset filters", exact: true }).click();
  await page.getByLabel("Search ventures").fill("nothingmatches");
  await expect(page.getByRole("status")).toContainText("No ventures match");
  expect(errors).toEqual([]);
});

test("comparison, source evidence, fewer than three and stage abstention", async ({ page }) => {
  await page.goto("/?mode=research");
  await page.getByRole("button", { name: "Find comparisons", exact: true }).click();
  await page
    .getByLabel("Investigation description")
    .fill("clinical images software surgical planning");
  await page
    .locator(".compare-form")
    .getByRole("button", { name: "Find comparisons", exact: true })
    .click();
  await expect(page.getByRole("heading", { name: /comparison candidates/ })).toBeVisible();
  await expect(page.locator(".comparison-card")).toHaveCount(2);
  await expect(page.locator(".method")).toContainText("b0-token-overlap-1.0");
  await page
    .locator(".comparison-card")
    .first()
    .getByText("Matching fields & source passages", { exact: true })
    .click();
  await expect(
    page.locator(".comparison-card").first().locator(".source a").first(),
  ).toHaveAttribute("href", /^https:\/\/www.auckland.ac.nz/);
  await page.getByLabel("Subject venture").selectOption("v_formus");
  await page
    .locator(".compare-form")
    .getByRole("button", { name: "Find comparisons", exact: true })
    .click();
  await expect(page.locator(".subject-evidence")).toContainText("Formus Labs");
  await expect(page.locator(".comparison-card")).toHaveCount(1);
  expect((await page.locator(".comparison-card").allTextContents()).join(" ")).not.toContain(
    "Formus Labs",
  );
  await page.getByLabel("Investigation mode").selectOption("stage_milestone");
  await page
    .locator(".compare-form")
    .getByRole("button", { name: "Find comparisons", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText(
    "Insufficient eligible dated milestone evidence",
  );
  await expect(page.locator(".comparison-card")).toHaveCount(0);
});

test("analytics and real CSV download", async ({ page }) => {
  await page.goto("/?mode=research");
  await page.getByRole("button", { name: "Data & exports" }).click();
  await expect(
    page.getByRole("heading", { name: "Programme recognition", exact: true }),
  ).toBeVisible();
  const download = page.waitForEvent("download");
  await page.locator('a[href="/api/exports/programme_recognition.csv"]').click();
  const file = await download;
  expect(file.suggestedFilename()).toBe("programme_recognition.csv");
  expect(await file.failure()).toBeNull();
  await expect(page.locator("table")).toHaveCount(3);
  await expect(page.locator(".analytics")).toContainText("As of (UTC)");
});

test("loading and recoverable API error states", async ({ page }) => {
  let blocked = true;
  await page.route("**/api/ventures?*", async (route) => {
    if (blocked) await route.fulfill({ status: 503, body: "unavailable" });
    else await route.continue();
  });
  await page.goto("/?mode=research");
  await expect(page.getByRole("alert")).toContainText("Database unavailable");
  blocked = false;
  await page.getByRole("button", { name: "Retry", exact: true }).click();
  await expect(page.locator(".venture-card")).toHaveCount(10);
  await page.route("**/api/ventures?*", async (route) => {
    await new Promise((r) => setTimeout(r, 500));
    await route.continue();
  });
  await page.getByLabel("Search ventures").fill("RosterLab");
  await expect(page.getByRole("status")).toContainText("Loading venture records");
  await expect(page.locator(".venture-card")).toHaveCount(1);
});

test("narrow layout has no page overflow", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/?mode=research");
  await expect(page.locator(".venture-card")).toHaveCount(10);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
  await page.screenshot({ path: testInfo.outputPath("mobile.png"), fullPage: true });
});

test("desktop release capture", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 1440, height: 1050 });
  await page.goto("/?mode=research");
  await expect(page.locator(".venture-card")).toHaveCount(10);
  await page.screenshot({ path: testInfo.outputPath("desktop.png"), fullPage: true });
});

test("changing a comparison query invalidates stale results", async ({ page }) => {
  await page.goto("/?mode=research");
  await page.getByRole("button", { name: "Find comparisons", exact: true }).click();
  await page
    .getByLabel("Investigation description")
    .fill("clinical images software surgical planning");
  await page.route("**/api/compare", async (route) => {
    await new Promise((r) => setTimeout(r, 500));
    await route.continue();
  });
  await page
    .locator(".compare-form")
    .getByRole("button", { name: "Find comparisons", exact: true })
    .click();
  await page
    .getByLabel("Investigation description")
    .fill("unrelated query changed while searching");
  await page.waitForTimeout(800);
  await expect(page.locator(".comparison-results")).toHaveCount(0);
});

test("evidence drawer supports Escape and returns keyboard focus", async ({ page }) => {
  await page.goto("/?mode=research");
  const subject = page.getByRole("button", {
    name: "Formus Labs",
    exact: true,
  });
  await subject.click();
  await expect(page.getByRole("dialog", { name: "Formus Labs", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Close profile", exact: true })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(subject).toBeFocused();
});
