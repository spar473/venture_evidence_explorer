import { expect, test } from "@playwright/test";

test("workbench opens with the five university projects and keeps research navigation", async ({ page }) => {
  await page.goto("/");
  const main = page.getByRole("navigation", { name: "Main navigation" });
  const watchlist = page.getByRole("navigation", { name: "University watchlist" });
  await expect(main.getByRole("button", { name: "Precedents" })).toHaveAttribute("aria-current", "page");
  await expect(watchlist.getByRole("button")).toHaveCount(5);
  await expect(page.getByRole("heading", { name: "Automated Breast MRI Reporting" })).toBeVisible();
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
  await page.getByLabel("Outcome", {exact: true}).selectOption("secondary");
  await expect(page.getByRole("heading", {name: /36-month status · Next priced equity round/})).toBeVisible();
  await page.getByLabel("Entry vintage").selectOption("2022");
  await expect(page.getByText("11 of 55")).toBeVisible();
  await expect(page.getByText(/Rates locked/)).toBeVisible();
});
