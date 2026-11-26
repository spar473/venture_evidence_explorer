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
      await expect(page.getByText("Locked", { exact: true })).toBeVisible();
    }
    expect(await seriousViolations(page)).toEqual([]);
    const figures = page.locator(".vee-main figure");
    for (const figure of await figures.all()) {
      await figure.scrollIntoViewIfNeeded();
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
  const product = page.getByLabel("Product", { exact: true });
  const buyer = page.getByLabel("Buyer", { exact: true });
  await expect(product.locator("option:checked")).toHaveText("Food and beverage · recorded");
  await expect(product).toHaveAttribute("title", "food_beverage");
  await expect(buyer.locator("option:checked")).toHaveText("Households · recorded");
  await expect(buyer.locator("option:checked")).toHaveAttribute("title", "household");
  await counts.getByRole("button", { name: /Business buyer · 4/ }).click();
  await expect(page.getByText(/Hindsight · 4 qualifying peers/)).toBeVisible();
  await expect(buyer).toHaveValue("business");
  await expect(buyer).toHaveAttribute("title", "business");
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

test("profile ranks evidence-ready peers and defers the lower chart", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/?view=profile&asof=2021-11-09");
  const nearest = page
    .locator(".vee-kpis > div")
    .filter({ hasText: "Nearest on product and customer" });
  await expect(nearest).toContainText("Social Club");
  await expect(nearest).toContainText("Product 0.018 · overall 0.524");
  await expect(
    page.getByText(
      "Closest product match, not enough evidence yet: Formus Labs, Inhibit Coatings. Research these next.",
      { exact: true },
    ),
  ).toBeVisible();

  const why = page
    .locator("figure")
    .filter({ has: page.getByText("Why no comps", { exact: true }) });
  const map = page.locator("figure").filter({ has: page.getByText("Peer map", { exact: true }) });
  await expect(map.locator("svg")).toBeVisible();
  await expect(why.locator("svg")).toHaveCount(0);
  for (const chart of [map, why]) {
    await chart.getByRole("button", { name: "View as table" }).click();
    const names = await chart.locator("tbody th").allTextContents();
    expect(names).toHaveLength(9);
    expect(names.slice(0, 3)).toEqual(["Social Club", "Parcelport", "First AML"]);
    expect(names).not.toContain("Formus Labs");
    expect(names).not.toContain("Inhibit Coatings Limited");
    await expect(chart.getByText("4 tied at 0.47", { exact: true })).toHaveCount(4);
    await chart.getByRole("button", { name: "View as chart" }).click();
  }
  await expect(why.locator("svg")).toBeVisible();
});

test("development curves label the selected companies and distinguish all three clocks", async ({
  page,
}) => {
  await page.goto("/?view=profile&asof=2021-11-09");
  const curve = page
    .locator("figure")
    .filter({ has: page.getByText("Development curves", { exact: true }) });
  const chart = curve.locator("svg");
  const labels = chart.locator('g[aria-label="text"] text');
  await expect(labels).toHaveCount(4);
  const names = await labels.evaluateAll((elements) =>
    elements.map((el) =>
      [...el.childNodes]
        .filter((node) => node.nodeName !== "title")
        .map((node) => node.textContent)
        .join(""),
    ),
  );
  expect(names).toEqual(["Supie", "Parcelport", "First AML", "Social Club"]);
  const palette = await labels.evaluateAll((elements) =>
    elements.map((el) => el.getAttribute("fill") ?? el.parentElement?.getAttribute("fill")),
  );
  expect(new Set(palette)).toEqual(new Set(["#254891", "#0e766e", "#8e3a78", "#9a4d14"]));

  const known = curve.getByRole("button", { name: /^First AML · Series B.*Known by date/ });
  const late = curve.getByRole("button", {
    name: /^Social Club · Register removal.*Happened before; source found later/,
  });
  const future = curve.getByRole("button", { name: /^Parcelport · Last seen active.*Hindsight/ });
  await expect(known).toHaveAttribute("fill", "#1e3a8a");
  await expect(late).toHaveAttribute("fill", "#fff");
  await expect(future).toBeVisible();
  await expect(chart.locator('g[aria-label="line"][stroke-dasharray="5 4"] path')).toHaveCount(1);
  await expect(chart.locator('g[aria-label="line"]:not([stroke-dasharray]) path')).toHaveCount(3);
  if (process.env.VEE_SCREENSHOTS) {
    await page.setViewportSize({ width: 390, height: 844 });
    await curve.scrollIntoViewIfNeeded();
    await page.screenshot({ path: resolve(process.env.VEE_SCREENSHOTS, "profile-curves-390.png") });
  }
  await late.focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("dialog").getByText(/Happened before; source found later/),
  ).toBeVisible();
});

test("cohort event strip scrolls all dated companies and preserves outcome sorting", async ({
  page,
}) => {
  await page.goto("/?view=cohort&asof=2026-11-23");
  const region = page.getByRole("region", { name: "Scroll company event timeline" });
  const entries = region.getByRole("button", { name: / · First round · / });
  await expect(entries).toHaveCount(55);
  const firstVintage = await entries.first().getAttribute("aria-label");
  expect(await region.evaluate((element) => element.scrollHeight > element.clientHeight)).toBe(
    true,
  );
  await region.focus();
  await page.keyboard.press("PageDown");
  await expect.poll(() => region.evaluate((element) => element.scrollTop)).toBeGreaterThan(0);
  await page.getByLabel("Sort by").selectOption("outcome");
  await expect(entries).toHaveCount(55);
  await expect(entries.first()).not.toHaveAttribute("aria-label", firstVintage!);
});

test("profile reserves mobile plot space before evidence arrives", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  let deliver!: () => void;
  const delay = new Promise<void>((resolve) => {
    deliver = resolve;
  });
  await page.route(/\/views\/(profile|overview)\/public_supie(?:\.json)?$/, async (route) => {
    await delay;
    await route.continue();
  });
  await page.goto("/?view=profile&asof=2021-11-09", { waitUntil: "domcontentloaded" });
  const loadingFrames = page
    .getByRole("status", { name: "Loading company evidence" })
    .locator(".vee-plot-frame");
  await expect(loadingFrames).toHaveCount(2);
  const reserved = (await loadingFrames.first().boundingBox())!.height;
  deliver();
  const profileFrames = page.locator(".vee-profile-hero .vee-plot-frame");
  await expect(profileFrames).toHaveCount(2);
  expect((await profileFrames.first().boundingBox())!.height).toBe(reserved);
  await expect(page.locator(".vee-profile-hero figure").first().locator("svg")).toBeVisible();
});

test("venture outlook changes subjects, replays dated analogues and keeps scenario inputs explicit", async ({
  page,
}) => {
  await page.goto("/?view=rookie");
  await expect(page.getByRole("heading", { name: "Venture outlook" })).toBeVisible();
  const timeline = page.locator("figure").filter({ hasText: "What happened to the precedents?" });
  await timeline.getByRole("button", { name: "View as table" }).click();
  await expect(timeline.getByText("Pilot procurement constraint")).toBeVisible();
  await page.getByLabel("Peer follow-up").selectOption("1");
  await expect(timeline.getByText("Pilot procurement constraint")).toHaveCount(0);
  await page.getByLabel("Peer follow-up").selectOption("15");
  await expect(timeline.getByText("Share acquisition").first()).toBeVisible();
  for (const [category, venture] of [
    ["education", "writewise"],
    ["climate", "neocrete"],
    ["agriculture", "agriphage"],
    ["health", "pulsemap"],
  ]) {
    await page.getByRole("combobox", { name: "Category", exact: true }).selectOption(category);
    const subjects = page.getByRole("combobox", { name: "NZ venture" });
    await expect(subjects.locator("option")).toHaveCount(2);
    await subjects.selectOption(venture);
    await expect(page).toHaveURL(new RegExp("venture=" + venture));
    await expect(page.getByText(/^10 precedents in/)).toBeVisible();
  }
  await page.getByText(/^10 precedents in/).click();
  await page.getByRole("button", { name: "Alimetry · New Zealand", exact: true }).click();
  await expect(
    page.getByRole("dialog").getByRole("link", { name: "FDA decision letter" }),
  ).toHaveAttribute("href", /K240946/);
  await page.getByRole("button", { name: "Close details" }).click();
  const model = page.getByRole("region", { name: "Conditional simulator" });
  await expect(model.getByText(/no fitted estimate/)).toBeVisible();
  const initial = await model.getByText(/^At 36 months/).innerText();
  await model.getByRole("button", { name: "Slower progress" }).click();
  await expect(model.getByText(/^At 36 months/)).not.toHaveText(initial);
  await model.getByRole("combobox", { name: "Steps to target" }).selectOption("1");
  await expect(model.getByLabel(/Advance per quarter/)).toHaveValue("10");
  await expect(model.getByText(/^At 36 months/)).toContainText("37% reach the target");
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
  expect(await seriousViolations(page)).toEqual([]);
});

test("outlook retrieves a starting-record match and opens the funding ledger", async ({ page }) => {
  await page.goto("/?view=rookie&venture=breast-mri");
  const retrieval = page.getByRole("region", { name: "Find more precedents" });
  const query = retrieval.getByRole("searchbox");
  await query.fill("zzzzz xxxxx");
  await expect(retrieval.getByRole("status")).toContainText("No shared terms");
  await query.fill("gastric diagnostic device");
  await expect(retrieval.getByRole("link", { name: "Alimetry", exact: true })).toBeVisible();
  await retrieval.getByRole("button", { name: "Plot Alimetry", exact: true }).click();
  const timeline = page.locator("figure").filter({ hasText: "What happened to the precedents?" });
  await expect(timeline.getByText(/Added for inspection.*Alimetry/)).toBeVisible();
  await timeline.getByRole("button", { name: "View as table" }).click();
  await expect(timeline.getByRole("rowheader", { name: "Alimetry" }).first()).toBeVisible();
  await timeline.getByRole("button", { name: "Remove added venture" }).click();
  await expect(timeline.getByRole("rowheader", { name: "Alimetry" })).toHaveCount(0);

  const formus = page.locator(".vee-rookie-peers section").filter({
    has: page.getByRole("heading", { name: "Formus Labs" }),
  });
  await formus.getByRole("link", { name: "Funding & outcomes" }).click();
  await expect(page).toHaveURL(/view=evidence&case=formus-labs/);
  await expect(page.getByRole("heading", { name: "Formus Labs" })).toBeVisible();
  await page.getByRole("combobox", { name: "Evidence type" }).selectOption("equity");
  await expect(page.getByText("1 sourced record")).toBeVisible();
  await expect(page.getByText("US$5 million", { exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "Company launch announcement" })).toHaveAttribute(
    "href",
    /formus.com/,
  );
});

test("funding and outcomes browses the full catalogue and suggests a review label", async ({
  page,
}) => {
  await page.goto("/?view=evidence");
  await expect(page.getByRole("heading", { name: "Funding & outcomes" })).toBeVisible();
  await expect(page.getByText("149 sourced records")).toBeVisible();
  await expect(page.getByText("40 ventures", { exact: true })).toBeVisible();
  await page.getByRole("combobox", { name: "Category" }).selectOption("agriculture");
  await expect(page.getByText("10 ventures", { exact: true })).toBeVisible();
  await page.getByRole("combobox", { name: "Origin" }).selectOption("nz");
  await expect(page.getByText("3 ventures", { exact: true })).toBeVisible();
  await page.getByRole("searchbox", { name: "Search ventures" }).fill("Halter");
  await expect(page.getByText("1 venture", { exact: true })).toBeVisible();
  await page.getByRole("combobox", { name: "Evidence type" }).selectOption("equity");
  await expect(page.getByText("NZ$377 million", { exact: true })).toBeVisible();
  await page.getByText("Suggest a type for new evidence", { exact: true }).click();
  const excerpt = page.getByRole("textbox", { name: "Paste a public source excerpt" });
  await excerpt.fill("zzzzz xxxxx");
  await page.getByRole("button", { name: "Suggest type" }).click();
  await expect(page.getByRole("status")).toContainText("Too little overlap");
  await excerpt.fill(
    "The venture announced a Series B funding round led by an institutional investor.",
  );
  await page.getByRole("button", { name: "Suggest type" }).click();
  await expect(page.getByRole("status")).toContainText("Suggested type");
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
  expect(await seriousViolations(page)).toEqual([]);
});
