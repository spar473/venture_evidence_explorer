import { useEffect, useState } from "react";
import { Details } from "./details";
import {
  STATIC,
  formatDate,
  resourceURL,
  today,
  type Cohort,
  type Company,
  type Profile,
  type Robustness,
} from "./data";
import { CompanyProfile } from "./profile-view";
import { CohortExplorer } from "./cohort-view";
import { ScenarioLab } from "./scenario-view";
import { MethodLab } from "./method-view";
import "./views.css";

const views = {
  profile: "Company profile",
  cohort: "Cohort explorer",
  scenario: "Scenario lab",
  method: "Method lab",
} as const;
type View = keyof typeof views;
const legacy = new URLSearchParams(location.search);
const updated = new URLSearchParams(legacy);
if (!updated.has("view") && updated.has("page")) {
  updated.set("view", updated.get("page") === "outcomes" ? "cohort" : "profile");
  updated.delete("page");
}
if (!updated.has("company") && updated.has("company_id")) {
  updated.set("company", updated.get("company_id")!);
  updated.delete("company_id");
}
if (!updated.has("asof") && updated.has("as_of")) {
  updated.set("asof", updated.get("as_of")!);
  updated.delete("as_of");
}

export function useAnalytics<T>(path: string | null) {
  const [result, setResult] = useState<{ path: string; data?: T; error?: string }>();
  useEffect(() => {
    if (!path) return;
    const abort = new AbortController();
    fetch(resourceURL(path), { signal: abort.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error("Could not load this view.");
        const data: T = await response.json();
        if (!abort.signal.aborted) setResult({ path, data });
      })
      .catch(() => {
        if (!abort.signal.aborted)
          setResult({ path, error: "Could not load this view. Reload to retry." });
      });
    return () => abort.abort();
  }, [path]);
  return result?.path === path ? result : undefined;
}

export type Filters = {
  sectors: string[];
  from: number;
  to: number;
  asof: string;
};

function validDate(value: string | null, fallback: string) {
  if (!value || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return fallback;
  const date = new Date(value + "T00:00:00Z");
  return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value
    ? value
    : fallback;
}

export function matchesFilter(company: Company, filters: Filters) {
  return (
    company.year >= filters.from &&
    company.year <= filters.to &&
    (!filters.sectors.length || filters.sectors.includes(company.sector_group))
  );
}

export function KPI({
  values,
}: {
  values: { name: string; value: string | number; hint?: string }[];
}) {
  return (
    <dl className="vee-kpis">
      {values.map(({ name, value, hint }) => (
        <div key={name}>
          <dt>{name}</dt>
          <dd>{value}</dd>
          {hint && <dd className="vee-kpi-hint">{hint}</dd>}
        </div>
      ))}
    </dl>
  );
}

export function AnalyticsViews() {
  const [params, setParams] = useState(updated);
  useEffect(() => {
    if (legacy.toString() !== updated.toString())
      history.replaceState(null, "", `?${updated}${location.hash}`);
    const pop = () => setParams(new URLSearchParams(location.search));
    window.addEventListener("popstate", pop);
    return () => window.removeEventListener("popstate", pop);
  }, []);
  const set = (values: Record<string, string>, replace = false) => {
    const next = new URLSearchParams(params);
    for (const [name, value] of Object.entries(values)) {
      next.delete(name);
      if (value) next.set(name, value);
    }
    history[replace ? "replaceState" : "pushState"](null, "", `?${next}`);
    setParams(next);
  };
  const requested = params.get("view") as View | null;
  const view = requested && Object.hasOwn(views, requested) ? requested : "profile";
  const withSubject = view === "profile" || view === "scenario";
  const cohortResource = useAnalytics<Cohort>("/views/cohort");
  const cohort = cohortResource?.data;
  const companyId = cohort?.subjects.includes(params.get("company") ?? "")
    ? params.get("company")!
    : "public_supie";
  const companies = new Map(cohort?.companies.map((company) => [company.company_id, company]));
  const subject = companies.get(companyId);
  const profileResource = useAnalytics<Profile>(withSubject ? `/views/profile/${companyId}` : null);
  const robustnessResource = useAnalytics<Robustness>(
    withSubject ? `/robustness/${companyId}` : null,
  );
  const profile = profileResource?.data;
  const last = today();
  const firstRound = view === "profile" ? subject?.start : undefined;
  const defaultAsOf = firstRound ?? last;
  const date = validDate(params.get("asof"), defaultAsOf);
  const asof = date > last ? last : firstRound && date < firstRound ? firstRound : date;
  useEffect(() => {
    if (firstRound && params.has("asof") && params.get("asof") !== asof) set({ asof }, true);
  }, [asof, firstRound, params]);
  const years = [...new Set(cohort?.companies.map(({ year }) => year))].sort();
  const min = years[0] ?? 2012;
  const max = years[years.length - 1] ?? 2022;
  const startYear = Number(params.get("from") ?? min);
  const endYear = Number(params.get("to") ?? max);
  const filters: Filters = {
    sectors: (params.get("sector") ?? "")
      .split(",")
      .filter((x) => x === "Healthtech" || x === "Other sectors"),
    from: years.includes(startYear) ? startYear : min,
    to: years.includes(endYear) ? endYear : max,
    asof,
  };

  function viewHref(next: View) {
    const target = new URLSearchParams(params);
    target.set("view", next);
    target.set("asof", asof);
    return `?${target}`;
  }
  function switchSector(sector: string) {
    set({
      sector: filters.sectors.includes(sector)
        ? filters.sectors.filter((value) => value !== sector).join(",")
        : [...filters.sectors, sector].join(","),
    });
  }

  return (
    <div className="vee-app">
      <a className="skip-link" href="#vee-main">
        Skip to analytics
      </a>
      <header className="vee-header">
        <div className="vee-header-inner">
          <a className="vee-brand" href="?view=profile" aria-label="Venture Evidence Explorer home">
            <span className="vee-brand-icon" aria-hidden="true">
              <i />
              <i />
              <i />
            </span>
            <span>
              Venture Evidence <strong>Explorer</strong>
            </span>
          </a>
          <nav aria-label="Analytics views">
            {(Object.keys(views) as View[]).map((next) => (
              <a
                key={next}
                href={viewHref(next)}
                aria-current={view === next ? "page" : undefined}
                onClick={(event) => {
                  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
                  event.preventDefault();
                  set({ view: next, asof });
                  window.scrollTo(0, 0);
                }}
              >
                {views[next]}
              </a>
            ))}
          </nav>
          <a className="vee-research-link" href="?mode=research">
            Research workspace
          </a>
        </div>
      </header>
      <main id="vee-main" className="vee-main" tabIndex={-1}>
        <div className="vee-banner">
          <span className="vee-banner-dot" aria-hidden="true" />
          <strong>Provisional preview</strong>
          <span>
            AI-checked evidence · human review pending ·{" "}
            {cohort?.strict_gate_passed
              ? "Strict evidence gate met"
              : `strict evidence gate unmet${cohort ? ` (${cohort.preview_peers} of 15 earlier Partly peers AI-checked)` : ""}`}
          </span>
        </div>
        <Details>
          <div className="vee-page-heading">
            <div>
              {view === "profile" && subject && (
                <div className="vee-eyebrow">
                  {subject.sector} <span>·</span> First round{" "}
                  {formatDate(subject.entry.date.value ?? subject.start)}
                </div>
              )}
              <h1>{view === "profile" ? (subject?.name ?? views.profile) : views[view]}</h1>
              {view === "profile" && (
                <p>
                  {profile?.fields.find(({ name }) => name === "description")?.value ??
                    (subject ? `Entry sector · ${subject.sector}` : "")}
                </p>
              )}
              {view === "cohort" && (
                <p>New Zealand seed entries · 36-month follow-up through the selected date.</p>
              )}
              {view === "scenario" && <p>Change an entry fact and inspect the same peer pool.</p>}
              {view === "method" && <p>Evidence requirements and a synthetic estimator demo.</p>}
            </div>
            {withSubject && (
              <label className="vee-select-label">
                Company
                <select
                  value={companyId}
                  disabled={!cohort}
                  onChange={(event) => set({ company: event.currentTarget.value })}
                >
                  {(cohort?.subjects ?? [companyId]).map((id) => (
                    <option key={id} value={id}>
                      {companies.get(id)?.name ?? "Supie"}
                    </option>
                  ))}
                </select>
              </label>
            )}
          </div>
          {view !== "method" && (
            <div className="vee-filters" aria-label="Shared filters">
              <div className="vee-filter-chips" role="group" aria-label="Sectors">
                {["Healthtech", "Other sectors"].map((sector) => (
                  <button
                    key={sector}
                    type="button"
                    aria-pressed={filters.sectors.includes(sector)}
                    onClick={() => switchSector(sector)}
                  >
                    {sector}
                  </button>
                ))}
              </div>
              <div className="vee-vintage-filter" role="group" aria-label="Vintage range">
                <span>Vintage</span>
                <select
                  aria-label="First vintage"
                  value={filters.from}
                  onChange={(event) => {
                    const from = Number(event.currentTarget.value);
                    set({ from: String(from), to: String(Math.max(from, filters.to)) });
                  }}
                >
                  {(years.length ? years : [filters.from]).map((year) => (
                    <option key={year}>{year}</option>
                  ))}
                </select>
                <span aria-hidden="true">–</span>
                <select
                  aria-label="Last vintage"
                  value={filters.to}
                  onChange={(event) => {
                    const to = Number(event.currentTarget.value);
                    set({ from: String(Math.min(to, filters.from)), to: String(to) });
                  }}
                >
                  {(years.length ? years : [filters.to]).map((year) => (
                    <option key={year}>{year}</option>
                  ))}
                </select>
              </div>
              <label className="vee-date-filter">
                As of{" "}
                <input
                  aria-label="As of date"
                  type="date"
                  min={firstRound}
                  max={last}
                  value={asof}
                  onChange={(event) => set({ asof: event.currentTarget.value })}
                />
              </label>
            </div>
          )}
          {cohortResource?.error || (withSubject && profileResource?.error) ? (
            <p role="alert">{cohortResource?.error ?? profileResource?.error}</p>
          ) : !cohort || (withSubject && (!profile || !subject)) ? (
            <p role="status">Loading evidence…</p>
          ) : (
            <>
              {view === "profile" && profile && subject && (
                <CompanyProfile
                  {...{
                    profile,
                    subject,
                    cohort,
                    companies,
                    filters,
                    playback: asof,
                    latest: last,
                    onDate: (asof: string) => set({ asof }, true),
                    robustness: robustnessResource?.data,
                  }}
                />
              )}
              {view === "cohort" && <CohortExplorer cohort={cohort} filters={filters} />}
              {view === "scenario" && profile && subject && (
                <ScenarioLab
                  key={companyId}
                  {...{
                    profile,
                    subject,
                    cohort,
                    companies,
                    filters,
                    robustness: robustnessResource?.data,
                  }}
                />
              )}
              {view === "method" && <MethodLab cohort={cohort} />}
            </>
          )}
        </Details>
      </main>
      <footer className="vee-footer">
        <span>Venture Evidence Explorer · New Zealand seed cohort</span>
        <div>
          <a
            href={
              STATIC
                ? `${import.meta.env.BASE_URL}analytics-data/method.txt`
                : "/time-machine/method"
            }
          >
            Method notes
          </a>
          {!STATIC && <a href="?mode=workbench">Previous workbench</a>}
        </div>
      </footer>
    </div>
  );
}
