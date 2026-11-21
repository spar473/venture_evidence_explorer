import { expect, test } from "@playwright/test";

test("fixture directory shows all companies and distinguishes closure from follow-up", async ({
  page,
}) => {
  await page.goto("/?mode=research");
  await page.getByRole("button", { name: "Research dossiers", exact: true }).click();
  await page.getByText("NZ reference fixture", { exact: true }).click();
  const coverage = page.getByRole("region", { name: "Fixture coverage" });
  await expect(coverage).toContainText("30 companies");
  await expect(coverage).toContainText("20 without a witnessed entry snapshot");
  const company = page.getByLabel("Reference company");
  await expect(company.locator("option")).toHaveCount(31);
  await company.selectOption("supie");
  const trajectory = page.locator(".pool-trajectory");
  await expect(trajectory.locator(".pool-close")).toHaveText("×");
  await trajectory.getByText("Inspect source evidence", { exact: true }).click();
  await expect(
    trajectory.getByRole("link", { name: "Supie Group first liquidators’ report" }),
  ).toHaveAttribute("href", /liquidators-first-report-supie-limited/);
  await trajectory.getByText("What was public at the time", { exact: true }).click();
  await expect(trajectory).toContainText("As of 2021-11-09");
  await company.selectOption("cleanery");
  await expect(trajectory.locator(".pool-censor")).toHaveText("○");
});

test("university analogy shows sourced peers and preserves the sparse abstention", async ({
  page,
}) => {
  await page.goto("/?mode=research");
  await page.getByRole("button", { name: "Research dossiers", exact: true }).click();
  await page.getByRole("button", { name: "Neurofanos", exact: true }).click();
  const drawer = page.getByRole("dialog");
  await drawer.getByText("Peer trajectories", { exact: true }).click();
  const panel = drawer.locator(".pool-panel");
  const formus = panel.locator(".pool-trajectory").filter({ hasText: "Formus Labs" });
  await expect(formus.locator(".pool-range")).toBeVisible();
  await formus.getByText("Inspect source evidence", { exact: true }).click();
  await expect(formus).toContainText("Event date 2019 · year precision");
  await expect(formus).toContainText("first payment date remains unknown");
  await formus.getByText("What was public at the time", { exact: true }).click();
  await expect(formus).toContainText("As of 2022-02-11");
  await expect(panel).toContainText("This project is an analogy query");
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "PulseMap PAD Detector", exact: true }).click();
  await drawer.getByText("Peer trajectories", { exact: true }).click();
  await expect(panel).toContainText("There is insufficient comparison evidence");
  await expect(panel.locator(".pool-figure")).toHaveCount(0);
});
