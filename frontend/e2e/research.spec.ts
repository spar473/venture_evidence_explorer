import { test, expect } from "@playwright/test";
import { createHash } from "node:crypto";

async function openResearch(page: import("@playwright/test").Page, subject: string) {
  await page.goto("/");
  await page.getByRole("button", {name: "Research dossiers", exact: true}).click();
  const opener = page.getByRole("button", {name: subject, exact: true});
  await opener.click();
  const dossier = page.getByRole("dialog", {name: `${subject} research dossier`});
  await expect(dossier.locator(".research-dossier")).toBeVisible();
  return {opener, dossier};
}

async function downloadedText(download: import("@playwright/test").Download) {
  const stream = await download.createReadStream();
  if (!stream) throw new Error("Download unavailable");
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  return Buffer.concat(chunks);
}

test("research directory filters preserve quarantine, unknown identity and source responsibility", async ({page}) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await page.getByRole("button", {name: "Research dossiers", exact: true}).click();
  await expect(page.locator(".research-directory-row")).toHaveCount(12);
  await page.getByLabel("Research review state", {exact: true}).selectOption("accepted");
  await expect(page.getByRole("status")).toContainText("No research dossiers match");
  await page.getByRole("button", {name: "Reset research filters"}).click();
  await page.getByLabel("Search research dossiers").fill("RosterLab");
  await expect(page.locator(".research-directory-row")).toHaveCount(1);
  const opener = page.getByRole("button", {name: "RosterLab", exact: true});
  await opener.click();
  const dossier = page.getByRole("dialog", {name: "RosterLab research dossier"});
  await expect(dossier.locator(".research-identity")).toContainText("Unknown / unverified");
  await expect(dossier).toContainText("proposed unresolved at brand/project level");
  await expect(dossier).toContainText("quarantined from accepted structured matching and B0 retrieval");
  await expect(dossier.getByRole("button", {name: "Close dossier"})).toBeFocused();
  await dossier.getByLabel("Evidence field").selectOption("advertised_price");
  await expect(dossier.locator(".research-observation")).toHaveCount(1);
  const price = dossier.locator("#research-obs_rl_price");
  await expect(price).toContainText("$20 per rostered person per month");
  await expect(price.locator(".research-money")).toContainText("CurrencyUnknown");
  await expect(price.locator(".research-money")).not.toContainText("NZD");
  await expect(price).toContainText("Claim responsibility: company");
  await expect(price).toContainText("Actor: assistant");
  await price.getByRole("link", {name: "src_rl_pricing", exact: true}).click();
  const source = dossier.locator("#research-src_rl_pricing");
  await expect(source).toBeFocused();
  await expect(source.getByRole("link").first()).toHaveAttribute("href", /^https:\/\/rosterlab.com\/pricing/);
  await expect(source).toContainText("Historical availabilityNot verified");
  await page.keyboard.press("Escape");
  await expect(opener).toBeFocused();
  expect(errors).toEqual([]);
});

test("dossiers retain prospective targets, possibly duplicate financing and scoped withheld conclusions", async ({page}, testInfo) => {
  const {dossier} = await openResearch(page, "QuickMas");
  await dossier.screenshot({path: testInfo.outputPath("quickmas-desktop.png")});
  const target = dossier.locator("#research-event_qm_launch_target");
  await expect(target).toContainText("Target / intention");
  await expect(target).toContainText("2025 (year precision)");
  await expect(target).toContainText("Unknown / not established");
  await expect(target).toContainText("does not establish occurrence, failure or cancellation");
  await expect(target).not.toContainText("2025-01-01");
  await target.screenshot({path: testInfo.outputPath("quickmas-launch-target.png")});
  const targetQuestion = dossier.locator("#research-ready_quickmas_target");
  await expect(targetQuestion).toContainText("Conclusions withheld");
  await expect(targetQuestion).toContainText("That launch occurred, failed or was cancelled");
  await expect(dossier.locator("#research-ready_elapsed")).toContainText("Elapsed times, zero-sale conclusions or time-to-revenue ranking");
  await expect(dossier.locator("#research-ready_regulatory")).toContainText("No supported business conclusion supplied");
  await page.keyboard.press("Escape");
  await page.getByRole("button", {name: "RosterLab", exact: true}).click();
  const roster = page.getByRole("dialog", {name: "RosterLab research dossier"});
  await expect(roster.locator(".research-dossier")).toBeVisible();
  await roster.screenshot({path: testInfo.outputPath("rosterlab-desktop.png")});
  await expect(roster.locator("#research-case_rl_financing_possible_duplicate")).toContainText("Aggregation prohibited while unresolved");
  await expect(roster.locator("#research-event_rl_financing_uoa")).toContainText("Reported occurrence");
  await expect(roster.locator("#research-event_rl_financing_movac")).toContainText("Reported occurrence");
  await expect(roster.locator("#research-ready_journeys")).toContainText("The identity of the payer, budget authority, a completed IT integration");
  await expect(roster.locator("#research-gap_healthnz")).toContainText("payment");
  await expect(roster.locator("#research-gap_healthnz")).toContainText("Cannot establish");
  await roster.locator("#research-ready_solutions").getByRole("link", {name: "obs_qm_solution", exact: true}).last().click();
  await expect(roster.getByLabel("Evidence subjects")).toHaveValue("all");
  await expect(roster.locator("#research-obs_qm_solution")).toBeFocused();
  await expect(roster.locator("#research-obs_qm_solution")).toContainText("QuickMas");
});

test("research exports download preserved IDs, review, money scope and exact packet bytes", async ({page}) => {
  const {dossier} = await openResearch(page, "RosterLab");
  const csvEvent = page.waitForEvent("download");
  await dossier.getByRole("link", {name: "observations CSV ↓", exact: true}).click();
  const csv = (await downloadedText(await csvEvent)).toString("utf8");
  for (const value of ["observation_id", "source_url", "publication_precision", "review_actor_role", "currency_unknown_reason", "money_scope", "obs_rl_price", "round_total", "investor_cheque", "not_stated_in_inspected_sources"]) expect(csv).toContain(value);
  expect(csv).not.toContain("NZD");
  const packetEvent = page.waitForEvent("download");
  await dossier.getByRole("link", {name: "Original research packet JSON ↓"}).click();
  const bytes = await downloadedText(await packetEvent);
  const packet = JSON.parse(bytes.toString("utf8"));
  expect(packet.metadata.format_version).toBe("0.2.1");
  expect(packet.metadata.accepted_records_count).toBe(0);
  expect(packet.review_events).toEqual([]);
  const digest = createHash("sha256").update(bytes).digest("hex");
  await expect(dossier).toContainText(digest);
  for (const name of ["events", "event_reports", "unknowns", "readiness", "sources", "reconciliation_cases", "access_gaps", "identity_mappings", "date_intervals"]) {
    const response = await page.request.get(`/api/research/exports/${name}.csv?subject_id=subj_rosterlab&packet_sha256=${digest}`);
    expect(response.status()).toBe(200);
    expect(response.headers()["content-type"]).toContain("text/csv");
    expect(await response.text()).toContain("packet_sha256");
  }
});

test("research drawers remain keyboard accessible with narrow screens", async ({page}, testInfo) => {
  await page.setViewportSize({width: 390, height: 844});
  const {dossier, opener} = await openResearch(page, "QuickMas");
  await expect(dossier.getByRole("button", {name: "Close dossier"})).toBeFocused();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(await dossier.evaluate(node => node.scrollWidth <= node.clientWidth)).toBe(true);
  await dossier.screenshot({path: testInfo.outputPath("quickmas-mobile.png")});
  await page.keyboard.press("Tab");
  expect(await dossier.evaluate(node => node.contains(document.activeElement))).toBe(true);
  await page.keyboard.press("Escape");
  await expect(opener).toBeFocused();
});
