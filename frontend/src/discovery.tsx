import { useEffect, useRef, useState } from "react";
import type {
  DiscoveryPage,
  DiscoveryDetail,
  DiscoveryFacets,
  PromotionPreview,
} from "./api-schema";
import { useResource } from "./hooks";
import { Status } from "./shared";
import { ResearchRaw } from "./research-shared";
import { label } from "./labels";
const names: Record<string, string> = {
  pending_review: "Awaiting review",
  reviewed_staging: "Reviewed · staging only",
  excluded_by_review: "Excluded by review",
  identity: "Identity review",
  nz_inclusion: "Dated NZ inclusion",
  source_observations: "Source-backed claims",
  source_capture: "Saved source capture",
  dated_activity: "Dated activity evidence",
  app_identity_id: "Proposed application identity",
  nz_eligibility_review: "NZ inclusion review",
  date_window_review: "Period review",
  targeted_outcome_events: "Reported outcomes",
  name_links: "Name links",
  unresolved_cases: "Unresolved cases",
};
const readable = (value: string) => names[value] || label(value);
function Gaps({ items }: { items: string[] }) {
  return items.length ? (
    <details className="discovery-gaps">
      <summary>
        {items.slice(0, 2).map(readable).join(" · ")}
        {items.length > 2 ? " · +" + (items.length - 2) + " more checks" : ""}
      </summary>
      <ul>
        {items.map((k) => (
          <li key={k}>{readable(k)}</li>
        ))}
      </ul>
    </details>
  ) : (
    <span>No recorded gaps; not acceptance</span>
  );
}

const text = (row: Record<string, unknown>, key: string) =>
  row[key] === null || row[key] === undefined ? "Unknown / not supplied" : String(row[key]);
export function DiscoveryWorkspace() {
  const [q, setQ] = useState("");
  const [family, setFamily] = useState("");
  const [status, setStatus] = useState("");
  const [period, setPeriod] = useState("");
  const [gap, setGap] = useState("");
  const [offset, setOffset] = useState(0);
  const [selected, setSelected] = useState<{ id: string; name: string } | null>(null);
  const params = new URLSearchParams({
    q,
    family,
    status,
    gap,
    offset: String(offset),
    limit: "25",
  });
  if (period === "unknown") params.set("unknown_period", "true");
  else if (period) params.set("year", period);
  const { data, error, loading } = useResource<DiscoveryPage>("/discovery?" + params, 0, 120);
  const { data: facets } = useResource<DiscoveryFacets>("/discovery/facets");
  function change(set: (s: string) => void, value: string) {
    set(value);
    setOffset(0);
  }
  return (
    <section className="discovery-workspace">
      <p className="notice">
        Discovery staging is separate from accepted ventures. A current portfolio does not establish
        historic population, investment date, legal identity, NZ inclusion or current operating
        status. No update does not mean failure.
      </p>
      <p>
        {data?.staged_total ?? "—"} staged leads · {data?.source_families_total ?? "—"} source
        families · {data?.promoted_total ?? 0} promoted · Accepted NZ population: unknown
      </p>
      <div className="research-toolbar">
        <label>
          Search discovery leads
          <input value={q} onChange={(e) => change(setQ, e.target.value)} />
        </label>
        <label>
          Source family
          <select value={family} onChange={(e) => change(setFamily, e.target.value)}>
            <option value="">All families</option>
            {facets?.families.map((f) => (
              <option key={f.organisation_id} value={f.organisation_id}>
                {f.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Candidate status
          <select value={status} onChange={(e) => change(setStatus, e.target.value)}>
            <option value="">All staging states</option>
            {["pending_review", "reviewed_staging", "excluded_by_review"].map((s) => (
              <option key={s} value={s}>
                {readable(s)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Reported outcome period
          <select value={period} onChange={(e) => change(setPeriod, e.target.value)}>
            <option value="">All / not a population period</option>
            <option value="unknown">Unknown dated activity</option>
            {facets?.outcome_years.map((y) => (
              <option key={y}>{y}</option>
            ))}
          </select>
        </label>
        <label>
          Evidence gap
          <select value={gap} onChange={(e) => change(setGap, e.target.value)}>
            <option value="">All gaps</option>
            {[
              "identity",
              "nz_inclusion",
              "source_observations",
              "source_capture",
              "dated_activity",
            ].map((s) => (
              <option key={s} value={s}>
                {readable(s)}
              </option>
            ))}
          </select>
        </label>
      </div>
      {loading ? (
        <Status>Loading discovery queue…</Status>
      ) : error ? (
        <Status error>{error}</Status>
      ) : (
        <>
          <p>
            {data?.total} matching leads. Period filters use reported outcome dates only, not
            founding or investment dates.
          </p>
          <div className="table-scroll" tabIndex={0}>
            <table className="discovery-table">
              <thead>
                <tr>
                  <th>Lead</th>
                  <th>Reported relationships</th>
                  <th>Review state / gaps</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((c) => (
                  <tr key={c.discovery_id}>
                    <td>
                      <button
                        type="button"
                        onClick={() => setSelected({ id: c.discovery_id, name: c.display_name })}
                      >
                        {c.display_name}
                      </button>
                      <details className="discovery-record-id">
                        <summary>Record ID</summary>
                        <code>{c.discovery_id}</code>
                      </details>
                    </td>
                    <td>{c.source_families.join(", ") || "No family supplied"}</td>
                    <td>
                      {readable(c.status)}
                      <Gaps items={c.evidence_gaps} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p>
            <button disabled={offset === 0} onClick={() => setOffset((n) => Math.max(0, n - 25))}>
              Previous leads
            </button>{" "}
            {data?.total ? offset + 1 : 0}–{Math.min(offset + 25, data?.total || 0)} of{" "}
            {data?.total}{" "}
            <button
              disabled={offset + 25 >= (data?.total || 0)}
              onClick={() => setOffset((n) => n + 25)}
            >
              Next leads
            </button>
          </p>
        </>
      )}
      <p>
        Staging exports:{" "}
        {[
          "candidates",
          "sources",
          "organisations",
          "listings",
          "targeted_outcome_events",
          "name_links",
          "unresolved_cases",
        ].map((c) => (
          <a
            key={c}
            href={"/api/discovery/exports/" + c + ".csv"}
            download
            style={{ marginRight: 16 }}
          >
            {readable(c)} CSV ↓
          </a>
        ))}
      </p>
      {selected && (
        <DiscoveryDrawer id={selected.id} name={selected.name} close={() => setSelected(null)} />
      )}
    </section>
  );
}
function DiscoveryDrawer({ id, name, close }: { id: string; name: string; close: () => void }) {
  const node = useRef<HTMLDialogElement>(null);
  const { data, error } = useResource<DiscoveryDetail>(
    "/discovery/candidates/" + encodeURIComponent(id),
  );
  const { data: promotion } = useResource<PromotionPreview>(
    "/discovery/candidates/" + encodeURIComponent(id) + "/promotion",
  );
  useEffect(() => {
    const opener = document.activeElement as HTMLElement;
    node.current?.showModal();
    return () => {
      node.current?.close();
      opener?.focus();
    };
  }, []);
  return (
    <dialog
      ref={node}
      className="profile-wrap research-drawer"
      aria-label={name + " discovery lead"}
      onCancel={(e) => {
        e.preventDefault();
        close();
      }}
    >
      <div className="research-drawer-head">
        <h2>{name}</h2>
        <button autoFocus onClick={close}>
          Close lead
        </button>
      </div>
      {error ? (
        <Status error>{error}</Status>
      ) : !data ? (
        <Status>Loading lead…</Status>
      ) : (
        <div className="research-dossier">
          <p className="notice">
            Staging only · no accepted identity, legal continuity or NZ population inclusion.
          </p>
          <h3>Missingness and scope</h3>
          <Gaps items={data.evidence_gaps} />
          <dl className="research-values">
            {[
              "current_operating_status",
              "current_funding_stage",
              "first_investment_date",
              "company_domain",
              "app_identity_id",
              "nz_eligibility_review",
              "date_window_review",
            ].map((k) => (
              <div key={k}>
                <dt>{readable(k)}</dt>
                <dd>{readable(text(data.candidate, k))}</dd>
              </div>
            ))}
          </dl>
          <h3>Duplicate / mapping preview</h3>
          {data.duplicate_candidates.length ? (
            data.duplicate_candidates.map((d, i) => (
              <article key={i}>
                {d.name === d.id ? "Linked candidate" : d.name} · {readable(d.kind)} · {d.basis}
                <details>
                  <summary>Linked record ID</summary>
                  <code>{d.id}</code>
                </details>
              </article>
            ))
          ) : (
            <p>No name candidate found; this does not resolve identity.</p>
          )}
          <h3>Explicit name links (not legal merges)</h3>
          {data.name_links.map((r, i) => (
            <article key={i}>
              <p>
                {text(r, "other_name")} · {text(r, "basis")}
              </p>
              <ResearchRaw record={r} />
            </article>
          ))}
          <h3>Investor / programme listings</h3>
          <p>
            Portfolio mention does not prove cheque, fund vehicle, first investment date or
            same-round co-investment.
          </p>
          {data.listings.map((r, i) => (
            <article className="research-record" key={i}>
              <p>
                {text(r, "source_id")} · {text(r, "claim_type")} · {text(r, "locator")}
              </p>
              <ResearchRaw record={r} />
            </article>
          ))}
          <h3>Dated outcome reports</h3>
          {!data.outcomes.length && (
            <p>No dated outcome record supplied. No failure or zero outcome inferred.</p>
          )}
          {data.outcomes.map((r, i) => (
            <article className="research-record" key={i}>
              <p>
                {text(r, "date_value")} ({text(r, "date_precision")}) · {text(r, "event_type")}
              </p>
              <p>{text(r, "summary")}</p>
              <p>
                {text(r, "date_basis")} · {text(r, "review_status")}
              </p>
              <ResearchRaw record={r} />
            </article>
          ))}
          <h3>Unresolved cases</h3>
          {data.unresolved_cases.map((r, i) => (
            <article className="research-record" key={i}>
              <p>
                {text(r, "issue_type")} · {text(r, "status")}
              </p>
              <p>{text(r, "action")}</p>
              <ResearchRaw record={r} />
            </article>
          ))}
          <h3>Source lineage and access</h3>
          {data.sources.map((r, i) => (
            <article className="research-record" key={i}>
              <a href={text(r, "url")} target="_blank" rel="noreferrer">
                {text(r, "title")}
              </a>
              <p>
                Retrieved {text(r, "retrieved_on")} · Publication {text(r, "published_at")} ·{" "}
                {readable(text(r, "access_status"))}
              </p>
              <p>{text(r, "limitations")}</p>
              <ResearchRaw record={r} />
            </article>
          ))}
          <h3>Promotion dry run · no writes</h3>
          {promotion && (
            <>
              <p>
                {promotion.ready_for_research_import
                  ? "Review prerequisites represented; explicit research import still required"
                  : "Promotion withheld"}
              </p>
              <ul>
                {promotion.blockers.map((b) => (
                  <li key={b}>
                    {b
                      .replaceAll("nz_inclusion", "NZ inclusion")
                      .replaceAll("period_scope", "period scope")}
                  </li>
                ))}
              </ul>
              <p>{promotion.scope}</p>
            </>
          )}
          <h3>Recorded review decisions</h3>
          {data.review_decisions.length ? (
            <ResearchRaw record={data.review_decisions} />
          ) : (
            <p>No actual review decisions supplied.</p>
          )}
          <ResearchRaw record={data.candidate} />
        </div>
      )}
    </dialog>
  );
}
