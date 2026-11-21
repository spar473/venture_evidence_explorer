import { test, expect } from "@playwright/test";

test("directory paginates summaries and loads evidence only when opened", async ({ page }) => {
  const details: string[] = [];
  page.on("request", (request) => {
    if (/\/api\/ventures\/[^/?]+$/.test(request.url())) details.push(request.url());
  });
  await page.goto("/?mode=research");
  await expect(page.locator(".venture-card")).toHaveCount(10);
  expect(details).toHaveLength(0);
  const firstName = await page.locator(".venture-open").first().textContent();
  await page.getByLabel("Records per page").selectOption("5");
  await expect(page.locator(".venture-card")).toHaveCount(5);
  const pages = page.getByRole("navigation", { name: "Directory pages" });
  await expect(pages).toContainText("1–5 of 10");
  await pages.getByRole("button", { name: "Next", exact: true }).click();
  await expect(pages).toContainText("6–10 of 10");
  await expect(pages.getByRole("button", { name: "Next", exact: true })).toBeDisabled();
  await expect(page.locator(".venture-open").first()).not.toHaveText(firstName || "");
  expect(details).toHaveLength(0);
  const opener = page.locator(".venture-open").first();
  await opener.click();
  await expect(page.locator(".profile .source").first()).toBeVisible();
  expect(details).toHaveLength(1);
  await page.keyboard.press("Escape");
  await expect(opener).toBeFocused();
  await page.getByLabel("Search ventures").fill("FormusLabs");
  await expect(page.locator(".venture-card")).toHaveCount(1);
  await expect(pages).toContainText("1–1 of 1");
  await expect(pages.getByRole("button", { name: "Previous", exact: true })).toBeDisabled();
});

test("closing a loading profile prevents late evidence reopening the drawer", async ({ page }) => {
  await page.route("**/api/ventures/v_formus", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    await route.continue();
  });
  await page.goto("/?mode=research");
  const opener = page.getByRole("button", { name: "Formus Labs", exact: true });
  await opener.click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(opener).toBeFocused();
  await page.waitForTimeout(700);
  await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("historical profile preserves unknown and partial dates with review state", async ({
  page,
}) => {
  // Synthetic response fixture only: never imported into the research database.
  await page.route("**/api/ventures/v_formus", async (route) => {
    const response = await route.fetch();
    const profile = await response.json();
    profile.observations[0].published_at = null;
    profile.observations[0].publication_date = {
      precision: "unknown",
      lower_bound: null,
      upper_bound: null,
    };
    profile.observations[0].effective_at = null;
    profile.observations[0].effective_date = {
      precision: "year",
      lower_bound: "2022-01-01",
      upper_bound: "2022-12-31",
    };
    profile.observations[0].effective_review_status = "rejected";
    profile.observations[0].superseded = true;
    await route.fulfill({ response, json: profile });
  });
  await page.goto("/?mode=research");
  await page.getByRole("button", { name: "Formus Labs", exact: true }).click();
  const evidence = page.locator(".profile .source").first();
  await expect(evidence).toContainText("Published Unknown / not recorded");
  await expect(evidence).toContainText("2022 (year precision)");
  await expect(evidence).not.toContainText("2022-01-01");
  await expect(evidence).toContainText("Current review: rejected");
  await expect(evidence).toContainText("Retained for historical inspection");
});

test("exported comparison run replays against the recorded corpus", async ({ page }) => {
  await page.goto("/?mode=research");
  await page.getByRole("button", { name: "Find comparisons", exact: true }).click();
  await page
    .getByLabel("Investigation description")
    .fill("clinical images software surgical planning");
  await page
    .locator(".compare-form")
    .getByRole("button", { name: "Find comparisons", exact: true })
    .click();
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download comparison run JSON ↓" }).click();
  const download = await downloadEvent;
  expect(download.suggestedFilename()).toBe("comparison-run.json");
  const stream = await download.createReadStream();
  if (!stream) throw new Error("Comparison run download was unavailable");
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  const record = JSON.parse(Buffer.concat(chunks).toString("utf8"));
  expect(record.corpus_digest).toMatch(/^[a-f0-9]{64}$/);
  expect(record.selected_observations.length).toBeGreaterThan(0);
  expect(record.method_version).toBe("b0-token-overlap-1.0");
  const replay = await page.request.post("/api/comparison-runs/replay", { data: record });
  expect(replay.status()).toBe(200);
  expect((await replay.json()).run).toEqual(record);
});

test("tab navigation retains directory inputs, page and completed comparison", async ({ page }) => {
  let comparisons = 0;
  page.on("request", (request) => {
    if (request.url().endsWith("/api/compare")) comparisons++;
  });
  const browse = page.getByRole("button", { name: "Explore ventures", exact: true });
  const compare = page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("button", { name: "Find comparisons", exact: true });
  await page.goto("/?mode=research");
  await page.getByLabel("Search ventures").fill("FormusLabs");
  await expect(page.locator(".venture-card")).toHaveCount(1);
  await page.getByRole("button", { name: "Data & exports", exact: true }).click();
  await browse.click();
  await expect(page.getByLabel("Search ventures")).toHaveValue("FormusLabs");
  await expect(page.locator(".venture-card")).toHaveCount(1);
  await page.getByRole("button", { name: "Reset filters", exact: true }).click();
  await page.getByLabel("Records per page").selectOption("5");
  const pages = page.getByRole("navigation", { name: "Directory pages" });
  await pages.getByRole("button", { name: "Next", exact: true }).click();
  await expect(pages).toContainText("6–10 of 10");
  await expect(page.locator(".venture-open").first()).toHaveText("Formus Labs");
  const secondPageNames = await page.locator(".venture-open").allTextContents();
  await compare.click();
  await expect(page.locator(".venture-card")).toHaveCount(0);
  await page
    .getByLabel("Investigation description")
    .fill("clinical images software surgical planning");
  await page
    .locator(".compare-form")
    .getByRole("button", { name: "Find comparisons", exact: true })
    .click();
  await expect(page.locator(".comparison-card")).toHaveCount(2);
  await browse.click();
  await expect(page.getByLabel("Records per page")).toHaveValue("5");
  await expect(pages).toContainText("6–10 of 10");
  await expect(page.locator(".venture-card")).toHaveCount(5);
  expect(await page.locator(".venture-open").allTextContents()).toEqual(secondPageNames);
  await compare.click();
  await expect(page.getByLabel("Investigation description")).toHaveValue(
    "clinical images software surgical planning",
  );
  await expect(page.locator(".comparison-card")).toHaveCount(2);
  expect(comparisons).toBe(1);
  // A changed shared filter must invalidate the retained comparison.
  await browse.click();
  await page.getByLabel("Recorded programme").selectOption("velocity_100k");
  await compare.click();
  await expect(page.locator(".comparison-results")).toHaveCount(0);
});
