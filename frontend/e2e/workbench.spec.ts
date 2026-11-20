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
