import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { resolve } from "node:path";

const views = [
  { id: "profile", hero: "Peer map", asof: "2021-11-09" },
  { id: "cohort", hero: "36-month outcomes by vintage", asof: "2026-11-23" },
  { id: "scenario", hero: "Qualifying peers by scenario", asof: "2026-11-23" },
  { id: "method", hero: "Competing outcomes", asof: "2026-11-23" },
];
const forbidden =
  /%|\b(probabilit\w*|likely|chance|predict\w*|success rates?|validated|witness\w*|anchor\w*|alignable|Gower|IDF|n_eff|snapshot scope)\b|α/i;

async function seriousViolations(page: Page) {
  const result = await new AxeBuilder({ page }).analyze();
  return result.violations.filter(({ impact }) => impact === "serious" || impact === "critical");
}

for (const { id, hero, asof } of views) {
  test(`${id} first screen, language, chart accessibility and mobile layout`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(`/?view=${id}&asof=${asof}`);
    const first = page.locator("figure").filter({ has: page.getByText(hero, { exact: true }) });
    await expect(first.locator("svg")).toBeVisible();
    const box = (await first.boundingBox())!;
    expect(box.y + box.height).toBeLessThanOrEqual(900);
    await expect(page.getByText("Provisional preview", { exact: true })).toBeVisible();

    const lint = await page.locator(".vee-app").evaluate((element) => {
      const clone = element.cloneNode(true) as HTMLElement;
      clone.querySelectorAll("dialog, .vee-synthetic").forEach((node) => node.remove());
      const prose = [
        ...element.querySelectorAll(".vee-main p, .vee-main aside, .vee-main .vee-banner"),
      ]
        .filter((node) => node.getClientRects().length && !node.closest("dialog, .vee-synthetic"))
        .map((node) => (node as HTMLElement).innerText.trim())
        .join(" ");
      return { text: clone.textContent ?? "", words: prose.match(/\b[\w’'-]+\b/g)?.length ?? 0 };
    });
    expect(lint.text).not.toMatch(forbidden);
    expect(lint.words).toBeLessThanOrEqual(120);
    test.info().annotations.push({ type: "body-copy words", description: String(lint.words) });
    if (id === "method") {
      await expect(
        page.getByText("Synthetic cohort, no real company", { exact: true }),
      ).toHaveCount(3);
      await expect(page.getByRole("meter")).toHaveCount(3);
    }
    expect(await seriousViolations(page)).toEqual([]);
    const figures = page.locator(".vee-main figure");
    for (const figure of await figures.all()) {
      const svg = figure.locator("svg");
      await expect(svg).toHaveAttribute("aria-label", /\S/);
      const mark = figure.locator('svg [role=button][tabindex="0"]').first();
      await mark.focus();
      await expect(mark).toBeFocused();
      await figure.getByRole("button", { name: "View as table" }).click();
      await expect(figure.getByRole("table")).toBeVisible();
      await figure.getByRole("button", { name: "View as chart" }).click();
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    if (process.env.VEE_SCREENSHOTS)
      await page.screenshot({ path: resolve(process.env.VEE_SCREENSHOTS, `${id}-1440.png`) });

    await page.setViewportSize({ width: 390, height: 844 });
    await page.evaluate(() => window.scrollTo(0, 0));
    await expect(first.locator("svg")).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
    expect(await seriousViolations(page)).toEqual([]);
    if (process.env.VEE_SCREENSHOTS)
      await page.screenshot({ path: resolve(process.env.VEE_SCREENSHOTS, `${id}-390.png`) });
    expect(errors).toEqual([]);
  });
}

test("profile playback reveals each dated event and its source by keyboard", async ({ page }) => {
  await page.goto("/?view=profile&company=public_supie&asof=2021-11-09");
  await expect(page.getByRole("heading", { name: "Supie" })).toBeVisible();
  await expect(page.getByText("No comps clear all checks.", { exact: false })).toBeVisible();
  const curve = page
    .locator("figure")
    .filter({ has: page.getByText("Development curves", { exact: true }) });
  const slider = page.getByRole("slider", { name: "Playback date" });
  const liquidation = curve.getByRole("button", { name: /^Supie · Liquidation/ });
  await expect(liquidation).toHaveCount(0);
  await slider.focus();
  await page.keyboard.press("ArrowRight");
  await expect(slider).toHaveAttribute("aria-valuetext", "9 Dec 2021");
  await expect(page).toHaveURL(/asof=2021-12-09/);
  await page.getByRole("button", { name: "Today", exact: true }).click();
  await expect(liquidation).toBeVisible();
  await liquidation.focus();
  await page.keyboard.press("Enter");
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByText("Recorded source")).toBeVisible();
  const source = dialog.getByRole("link");
  await expect(source).toHaveAttribute("href", /companiesoffice\.govt\.nz/);
  const url = (await source.getAttribute("href"))!;
  await page.context().route(url, (route) => route.fulfill({ body: "Source navigation fixture" }));
  const popup = page.waitForEvent("popup");
  await source.focus();
  await page.keyboard.press("Enter");
  const opened = await popup;
  await opened.waitForURL(url);
  await opened.close();
  await page.keyboard.press("Escape");

  await page.getByRole("combobox", { name: "Company", exact: true }).selectOption("public_partly");
  await expect(page.getByText(/No qualifying evidence public by 8 Oct 2020/)).toBeVisible();
  await page
    .getByRole("combobox", { name: "Company", exact: true })
    .selectOption("discovery_halter");
  await expect(page.getByText(/No qualifying evidence public by 1 Dec 2016/)).toBeVisible();
});

test("shared filters travel between views and a vintage segment lists companies", async ({
  page,
}) => {
  await page.goto("/?view=cohort&asof=2026-11-23");
  const chart = page
    .locator("figure")
    .filter({ has: page.getByText("36-month outcomes by vintage", { exact: true }) });
  const mark = chart.locator('svg [role="button"]').first();
  await mark.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("dialog").locator("li").first()).toBeVisible();
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Healthtech", exact: true }).click();
  await page.getByRole("combobox", { name: "First vintage" }).selectOption("2020");
  await page.getByRole("link", { name: "Scenario lab" }).click();
  await expect(page).toHaveURL(/sector=Healthtech/);
  await expect(page).toHaveURL(/from=2020/);
  await expect(page.getByRole("button", { name: "Healthtech", exact: true })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  await expect(page.getByRole("combobox", { name: "First vintage" })).toHaveValue("2020");
  await expect(page.getByLabel("As of date")).toHaveValue("2026-11-23");
});

test("scenario presets, custom rescoring without an API, and explicit ties", async ({ page }) => {
  await page.route("**/api/scenario/**", (route) => route.abort());
  await page.goto("/?view=scenario&company=public_supie");
  const counts = page
    .locator("figure")
    .filter({ has: page.getByText("Qualifying peers by scenario", { exact: true }) });
  for (const [label, value] of [
    ["Recorded", 0],
    ["Business buyer", 4],
    ["Business + subscription", 5],
    ["Software", 3],
    ["Software + business", 7],
    ["Revenue", 0],
  ] as const)
    await expect(
      counts.getByRole("button", { name: `${label} · ${value} · Open details`, exact: true }),
    ).toBeVisible();
  await counts.getByRole("button", { name: /Business buyer · 4/ }).click();
  await expect(page.getByText(/Hindsight · 4 qualifying peers/)).toBeVisible();
  await expect(page.getByLabel("Buyer", { exact: true })).toHaveValue("business");
  await page.getByLabel("Business model", { exact: true }).selectOption("subscription");
  await expect(counts.getByRole("button", { name: /Custom · 5/ })).toBeVisible();
  await expect(page.getByText(/4 tied at 0\.47 in the recorded ranking/)).toBeVisible();
  await expect(page.getByText("2,000 of 2,000", { exact: true }).first()).toBeVisible();
});

test("legacy links canonicalize in the production router", async ({ page }) => {
  test.skip(
    !process.env.VEE_STATIC && process.env.VEE_LEGACY_ROUTES !== "0",
    "Legacy regression server intentionally preserves old routes",
  );
  await page.goto("/?page=timemachine&company_id=public_supie&as_of=2021-11-09");
  await expect(page).toHaveURL(/view=profile/);
  await expect(page).toHaveURL(/company=public_supie/);
  await expect(page.getByRole("heading", { name: "Supie" })).toBeVisible();
  await page.goto("/?page=precedents");
  await expect(page).toHaveURL(/view=profile/);
  await page.goto("/?page=outcomes");
  await expect(page).toHaveURL(/view=cohort/);
});
