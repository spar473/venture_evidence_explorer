import { expect, test } from "@playwright/test";

test("workbench opens with the five university projects and keeps research navigation", async ({ page }) => {
  await page.goto("/");
  const main = page.getByRole("navigation", { name: "Main navigation" });
  const watchlist = page.getByRole("navigation", { name: "University watchlist" });
  await expect(main.getByRole("button", { name: "Precedents" })).toHaveAttribute("aria-current", "page");
  await expect(watchlist.getByRole("button")).toHaveCount(5);
  await expect(page.getByRole("heading", { name: "Automated Breast MRI Reporting" })).toBeVisible();
  await expect(page.getByText("Subject today vs peers at their first institutional round", {exact: false})).toBeVisible();
  await watchlist.getByRole("button", { name: "Neurofanos" }).click();
  await expect(page.getByRole("heading", { name: "Neurofanos" })).toBeVisible();
  await page.getByRole("button", { name: /Outlook/ }).click();
  await expect(page.getByRole("heading", { name: "Outcome rates locked" })).toBeVisible();
  await main.getByRole("button", { name: "Outcome library" }).click();
  await expect(page.getByRole("heading", { name: "Outcome library" })).toBeVisible();
  await page.getByRole("link", { name: "Research mode" }).click();
  await expect(page).toHaveURL(/mode=research/);
  await expect(page.getByRole("heading", { name: "Venture directory" })).toBeVisible();
});

test("realigns dated events, opens a keyboard-accessible claim and shows gate counts", async ({page}) => {
  await page.setViewportSize({width: 390, height: 844});
  await page.goto("/");
  await expect(page.getByRole("heading", {name: "Where comparable NZ ventures went"})).toBeVisible();
  await page.getByLabel("Align at").selectOption("first_regulatory_decision");
  const mark = page.getByRole("button", {name: /Formus Labs,.*2023-03-31/}).first();
  await mark.focus();
  await expect(mark).toBeFocused();
  await mark.press("Enter");
  await expect(page.getByRole("dialog", {name: "Claim evidence"})).toContainText("2023-03-31");
  await page.getByRole("button", {name: "Close evidence"}).click();
  await page.getByRole("button", {name: "View as table"}).click();
  await expect(page.getByRole("row").filter({hasText: "Formus Labs"}).first()).toBeVisible();
  await page.getByRole("button", {name: "Similar cohort"}).click();
  await expect(page.getByText(/Fewer than 3 peers/)).toBeVisible();
  await expect(page.getByText("55 of 150")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("outcome library reconciles filtered counts and retains post-window source notes", async ({page}) => {
  await page.goto("/");
  await page.getByRole("button", {name: "Outcome library", exact: true}).click();
  await expect(page.getByText("55 of 55")).toBeVisible();
  await expect(page.getByText(/Post-window closure · primary unknown/).first()).toBeVisible();
  await page.getByRole("button", {name: "Next companies"}).click();
  await expect(page.getByText("9–16 of 55")).toBeVisible();
  await page.getByRole("combobox", {name: "Outcome", exact: true}).selectOption("secondary");
  await expect(page.getByRole("heading", {name: /36-month status · Next priced equity round/})).toBeVisible();
  await page.getByLabel("Entry vintage").selectOption("2022");
  await expect(page.getByText("11 of 55")).toBeVisible();
  await expect(page.getByText(/Rates locked/)).toBeVisible();
});

test("same-stage evidence uses witnesses and Outlook withholds estimates", async ({page}) => {
  await page.route("**/api/workbench/gates", async route => {
    const response = await route.fetch();
    await route.fulfill({response, json: {...await response.json(), synthetic_probability: 0.9876}});
  });
  await page.goto("/");
  const views = page.getByRole("navigation", {name: "Precedent views"});
  await views.getByRole("button", {name: "Evidence"}).click();
  const matrix = page.getByRole("table", {name: "Evidence matrix"});
  await expect(matrix.getByRole("row").nth(1)).toContainText("Automated Breast MRI Reporting");
  await page.getByRole("button", {name: "Comparison snapshots"}).click();
  await expect(matrix.getByRole("row").nth(1)).toContainText("As of 2026-11-21");
  await expect(matrix.getByText("Not in public record").first()).toBeVisible();
  await expect(matrix.getByText("No dated witness")).toHaveCount(0);
  await views.getByRole("button", {name: /Outlook/}).click();
  await expect(page.getByRole("heading", {name: "Outcome rates locked"})).toBeVisible();
  await expect(page.getByText(/Dated signed closing records or cap-table/)).toBeVisible();
  await expect(page.getByText(/0\.9876|98\.76%/)).toHaveCount(0);
});

test("screening note downloads the selected subject and anchor", async ({page}) => {
  await page.goto("/");
  const exportLink = page.getByRole("link", {name: "Export screening note"});
  await expect(exportLink).toBeVisible();
  const href = await exportLink.getAttribute("href");
  const response = await page.request.get(href!);
  expect(response.headers()["content-disposition"]).toContain("attachment");
  const draft = await response.json();
  expect(draft.alternatives[0].metadata).toMatchObject({
    company_id: "subj_ht_mri", anchor_kind: "first_institutional_round", as_of: "2026-11-21",
    similarity_version: "witnessed-gower-b0:3", snapshot_basis: "subject_as_of", witness_mode: "strict",
  });
  expect(draft.weight_profiles).toEqual([]);
});

test("Toku excludes zero-workflow comps and late witness badges identify delayed evidence", async ({page}) => {
  await page.goto("/");
  const mode = page.getByRole("combobox", {name: "Peer witness mode", exact: true});
  await expect(mode).toHaveValue("strict");
  await mode.selectOption("contemporaneous");
  await expect(page.getByText("Late workflow and buyer evidence", {exact: false})).toBeVisible();
  await page.getByRole("button", {name: "Evidence", exact: true}).click();
  await page.getByRole("button", {name: "Comparison snapshots", exact: true}).click();
  const candidate = page.getByRole("row").filter({hasText: "The Insides Company"});
  await expect(candidate.getByText("+20 days", {exact: true}).first()).toBeVisible();
  await page.getByRole("searchbox", {name: "Search ventures"}).fill("Toku");
  await page.getByRole("button", {name: "Toku Eyes", exact: true}).click();
  await expect(page.getByRole("heading", {name: "Toku Eyes", exact: true})).toBeVisible();
  await expect(page.getByText(/Fewer than 3 peers meet the clinical workflow/)).toBeVisible();
  await expect(page.locator(".wb-comp")).toHaveCount(0);
  await mode.selectOption("strict");
  await expect(page.getByText("All 0 similar peers")).toBeVisible();
});

test("captures workbench screenshots for the README and PR", async ({page}, info) => {
  await page.setViewportSize({width: 1440, height: 960});
  await page.goto("/");
  await expect(page.getByRole("heading", {name: "Where comparable NZ ventures went"})).toBeVisible();
  await expect(page.getByRole("link", {name: "Export screening note"})).toBeVisible();
  const views = page.getByRole("navigation", {name: "Precedent views"});
  await page.screenshot({path: info.outputPath("workbench-overview.png"), fullPage: true});
  await views.getByRole("button", {name: "Evidence"}).click();
  await expect(page.getByRole("table", {name: "Evidence matrix"})).toBeVisible();
  await page.screenshot({path: info.outputPath("workbench-evidence.png"), fullPage: true});
  await page.getByRole("button", {name: "Outcome library", exact: true}).click();
  await expect(page.getByRole("heading", {name: "36-month status · Series A or later"})).toBeVisible();
  await page.screenshot({path: info.outputPath("workbench-outcome-library.png"), fullPage: true});
});
