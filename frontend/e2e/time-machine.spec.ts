import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { join } from "node:path";

const route = "/?page=timemachine";
const provisional =
  "Provisional preview: AI-adjudicated evidence, not human-confirmed. Strict evidence gate not passed (9 of 15 peers).";
const forbidden = /%|probability|likely|predict|success rate|validated/i;
const jargon =
  /\b(?:witness(?:ed)?|anchor|alignable|gower|idf|n_eff|snapshot scope|as-of-anchor)\b|α/i;

async function assertLanguage(page: Page) {
  const visible = await page.locator("body").innerText();
  expect(visible).not.toMatch(forbidden);
  expect(visible).not.toMatch(jargon);
  const candidates = page.getByRole("region", { name: "Nearest available, not comps" });
  if (await candidates.count())
    expect(await candidates.innerText()).not.toMatch(/\b(?:ceiling|typical|floor)\b/i);
}

test("the first screen and 60-second demo show evidence, abstention and the source after reveal", async ({
  page,
  context,
}) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  const response = page.waitForResponse(/\/api\/backtest\/public_supie\?/);
  await page.goto(route);
  const initial = new URL((await response).url());
  expect(initial.searchParams.get("track")).toBe("preview");
  expect(initial.searchParams.get("witness_mode")).toBe("strict");
  expect(initial.searchParams.get("peer_history")).toBe("as_of_anchor");
  const banner = page.getByText(provisional);
  const story = page.getByText(/9 November 2021, Supie has just reported a seed round/);
  const snapshot = page.getByRole("region", { name: "Supie’s snapshot" });
  const reveal = page.getByRole("button", { name: "Reveal what happened to Supie" });
  await expect(banner).toBeVisible();
  await expect(story).toContainText(
    "none of the past companies has a close enough product and customer match",
  );
  for (const element of [banner, story, snapshot, reveal]) {
    const box = await element.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.y).toBeGreaterThanOrEqual(0);
    expect(box!.y + box!.height).toBeLessThanOrEqual(900);
  }
  expect(await page.evaluate(() => window.scrollY)).toBe(0);
  await expect(snapshot.locator("dt")).toHaveCount(6);
  for (const fact of await snapshot.locator("dl > div").all()) {
    const link = fact.getByRole("link");
    await expect(link).toHaveAttribute("href", /^https:\/\//);
    await expect(link).toHaveAttribute("title", /\S/);
    await expect(fact.locator("time")).toHaveAttribute("datetime", "2021-11-09");
    await expect(fact.getByText(/AI-adjudicated/)).toHaveAttribute(
      "title",
      /Checked by .+ on 23 November 2026/,
    );
  }
  await expect(page.getByText("Voluntary administration", { exact: true })).toHaveCount(0);
  await expect(page.getByText("Liquidation", { exact: true })).toHaveCount(0);
  await expect(
    page.getByText(/Partly.*No qualifying evidence public by 8 October 2020/),
  ).toBeVisible();
  await expect(
    page.getByText(/Halter.*No qualifying evidence public by 1 December 2016/),
  ).toBeVisible();
  await assertLanguage(page);

  const captureDir = process.env.VEE_CAPTURE_PREVIEW;
  if (captureDir) await page.screenshot({ path: join(captureDir, "time-machine-desktop.png") });

  const candidates = page.getByRole("region", { name: "Nearest available, not comps" });
  await expect(candidates.getByRole("article")).toHaveCount(3);
  await expect(candidates.getByRole("heading", { name: "Social Club" })).toBeVisible();
  for (const card of await candidates.getByRole("article").all()) {
    await expect(card.getByText("Product and customer match below 0.25")).toBeVisible();
    await expect(card.getByText(/0\.\d{3} · Loose/)).toBeVisible();
    for (const list of await card.locator(".tm-differences").all())
      expect(await list.getByRole("listitem").count()).toBeLessThanOrEqual(3);
  }
  await reveal.click();
  await expect(page.getByRole("button", { name: "Hide the outcome" })).toHaveAttribute(
    "aria-expanded",
    "true",
  );
  await expect(page.getByText("Voluntary administration", { exact: true })).toBeVisible();
  await expect(page.getByText("Liquidation", { exact: true })).toBeVisible();
  await expect(page.getByText("9 November 2023", { exact: true })).toBeVisible();
  const source = page.getByRole("link", { name: "NZ Companies Office source for Liquidation" });
  const expected = await source.getAttribute("href");
  expect(expected).toBe(
    "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/7775376",
  );
  // Exercise the real link and destination URL without making CI depend on a third-party site.
  await context.route(expected!, (request) => request.fulfill({ body: "Companies Register" }));
  const popup = page.waitForEvent("popup");
  await source.click();
  await expect(await popup).toHaveURL(expected!);
  await assertLanguage(page);
});

test("the historical toggle marks later evidence and every subject keeps the banner", async ({
  page,
}) => {
  await page.goto(route);
  await expect(page.getByText(provisional)).toBeVisible();
  await expect(page.getByText("Hindsight", { exact: true })).toHaveCount(0);
  const history = page.waitForResponse(/\/api\/backtest\/public_supie\?.*peer_history=today/);
  await page.getByRole("checkbox", { name: "Include what we know today" }).check();
  await history;
  await expect(page.getByText("Hindsight", { exact: true }).first()).toBeVisible();
  await expect(page.getByText(provisional)).toBeVisible();
  await assertLanguage(page);
  await page.getByRole("checkbox", { name: "Include what we know today" }).uncheck();
  await expect(page.getByText("Hindsight", { exact: true })).toHaveCount(0);

  for (const [name, cutoff] of [
    ["Partly", "8 October 2020"],
    ["Halter", "1 December 2016"],
  ]) {
    await page.getByRole("combobox", { name: "Company to explore" }).selectOption({ label: name });
    await expect(page.getByText(provisional)).toBeVisible();
    await expect(
      page.getByText(
        `No qualifying evidence about ${name} was public by ${cutoff}, so there is no comparison.`,
      ),
    ).toBeVisible();
    await expect(page.getByRole("heading", { name: "Why no comps yet" })).toBeVisible();
    await expect(page.getByText("Series A", { exact: true })).toHaveCount(0);
    await page.getByRole("button", { name: `Reveal what happened to ${name}` }).click();
    await expect(page.getByText("Series A", { exact: true })).toBeVisible();
    await assertLanguage(page);
  }
});

test("keyboard can operate every control and reach every source including revealed events", async ({
  page,
}) => {
  await page.goto(route);
  await expect(page.getByText(provisional)).toBeVisible();
  const main = page.getByRole("main");
  const picker = page.getByRole("combobox", { name: "Company to explore" });
  const reveal = page.getByRole("button", { name: "Reveal what happened to Supie" });
  const toggle = page.getByRole("checkbox", { name: "Include what we know today" });
  const reached = new Set<string>();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to workspace" })).toBeFocused();
  await page.keyboard.press("Enter");

  for (let step = 0; step < 85; step++) {
    await page.keyboard.press("Tab");
    if (
      !reached.has("picker") &&
      (await picker.evaluate((element) => element === document.activeElement))
    ) {
      reached.add("picker");
      await expect(picker).toHaveValue("public_supie");
    }
    if (
      (await reveal.count()) &&
      (await reveal.evaluate((element) => element === document.activeElement))
    ) {
      reached.add("reveal");
      await page.keyboard.press("Enter");
    }
    if (await toggle.evaluate((element) => element === document.activeElement)) {
      if (reached.has("toggle")) break;
      reached.add("toggle");
      await page.keyboard.press("Space");
      await expect(page.getByText("Hindsight", { exact: true }).first()).toBeVisible();
    }
    const active = await page.evaluate(() => {
      const element = document.activeElement;
      if (element instanceof HTMLAnchorElement && element.target === "_blank")
        return [element.href, element.getAttribute("aria-label")].join("|");
      if (element?.tagName === "SUMMARY") return "summary:" + element.textContent?.trim();
      if (element?.textContent?.trim() === "View as table") return "table";
      return null;
    });
    if (
      await main
        .getByRole("link", { name: "See the case results" })
        .evaluate((element) => element === document.activeElement)
    )
      break;
    if (!active) continue;
    reached.add(active);
    if (
      active === "summary:Events after 36 months" ||
      active === "summary:Show time chart" ||
      active === "table"
    ) {
      await page.keyboard.press("Enter");
    }
    if (active === "table") {
      await expect(main.getByRole("table")).toHaveCount(2);
    }
  }
  await expect(toggle).toBeChecked();
  for (const control of ["picker", "reveal", "toggle", "table"]) expect(reached).toContain(control);
  const sources = await main
    .locator('a[target="_blank"]:visible')
    .evaluateAll((links) =>
      links.map((link) =>
        [(link as HTMLAnchorElement).href, link.getAttribute("aria-label")].join("|"),
      ),
    );
  expect(sources.length).toBeGreaterThan(8);
  for (const source of sources) expect(reached, source).toContain(source);
  await assertLanguage(page);
});

test("the company picker changes cases with the keyboard", async ({ page }) => {
  await page.goto(route);
  await expect(page.getByText(provisional)).toBeVisible();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to workspace" })).toBeFocused();
  await page.keyboard.press("Enter");
  await page.keyboard.press("Tab");
  const picker = page.getByRole("combobox", { name: "Company to explore" });
  await expect(picker).toBeFocused();
  await page.keyboard.press("p");
  await expect(picker).toHaveValue("public_partly");
  await expect(page.getByRole("button", { name: "Reveal what happened to Partly" })).toBeVisible();
});

test("axe has no serious or critical violations in the entry, reveal and hindsight views", async ({
  page,
}) => {
  await page.goto(route);
  await expect(page.getByText(provisional)).toBeVisible();
  async function check() {
    const report = await new AxeBuilder({ page }).analyze();
    expect(
      report.violations.filter(({ impact }) => impact === "serious" || impact === "critical"),
    ).toEqual([]);
  }
  await check();
  await page.getByRole("button", { name: "Reveal what happened to Supie" }).click();
  await page.getByText("Show time chart", { exact: true }).click();
  await check();
  await page.getByRole("checkbox", { name: "Include what we know today" }).check();
  await expect(page.getByText("Hindsight", { exact: true }).first()).toBeVisible();
  await check();
});

test("390px layout keeps the banner and expanded reveal readable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 1100 });
  await page.goto(route);
  const banner = page.getByText(provisional);
  const reveal = page.getByRole("button", { name: "Reveal what happened to Supie" });
  await expect(banner).toBeVisible();
  await reveal.click();
  const event = page.getByText("Liquidation", { exact: true });
  await expect(event).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  const layout = await page.evaluate(() => ({
    view: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
  }));
  expect(layout).toEqual({ view: 390, scroll: 390 });
  for (const element of [banner, event, page.getByRole("button", { name: "Hide the outcome" })]) {
    const box = await element.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.x).toBeGreaterThanOrEqual(0);
    expect(box!.x + box!.width).toBeLessThanOrEqual(390);
    expect(box!.y + box!.height).toBeLessThanOrEqual(1100);
  }
  await assertLanguage(page);
  const captureDir = process.env.VEE_CAPTURE_PREVIEW;
  if (captureDir) await page.screenshot({ path: join(captureDir, "time-machine-mobile.png") });
});
