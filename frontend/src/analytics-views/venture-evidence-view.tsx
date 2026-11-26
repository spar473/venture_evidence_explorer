import { useState } from "react";
import { categories, precedents, type Category } from "./rookie-model";
import { eventEvidence, evidenceKinds, trainingLabel, type EvidenceKind } from "./venture-evidence";
import {
  evidenceClasses,
  trainEvidenceClassifier,
  type EvidenceClass,
} from "./evidence-classifier";
import "./rookie.css";

const catalogue = [...precedents.values()];
const pageSize = 12;
const suggestEvidence = trainEvidenceClassifier(
  catalogue.flatMap(({ events }) =>
    events.map((event) => ({ text: event.description, label: trainingLabel(event) })),
  ),
);

function EvidenceSuggestion() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<EvidenceClass | null>();
  return (
    <details className="vee-panel vee-annotation">
      <summary>Suggest a type for new evidence</summary>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          setResult(suggestEvidence(input) ?? null);
        }}
      >
        <label>
          Paste a public source excerpt
          <textarea
            value={input}
            maxLength={2500}
            rows={4}
            onChange={(event) => {
              setInput(event.currentTarget.value);
              setResult(undefined);
            }}
          />
        </label>
        <p className="vee-note">
          Learns from the catalogue’s editorial tags. Review the proposed type against the source.
        </p>
        <button className="vee-table-toggle" type="submit" disabled={!input.trim()}>
          Suggest type
        </button>
        {result !== undefined && (
          <p role="status">
            {result === null
              ? "Too little overlap to suggest a type."
              : "Suggested type · " + evidenceClasses[result]}
          </p>
        )}
      </form>
    </details>
  );
}

export default function VentureEvidence({
  caseId,
  onCase,
}: {
  caseId: string | null;
  onCase: (id: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<Category | "all">("all");
  const [region, setRegion] = useState("all");
  const [kind, setKind] = useState<EvidenceKind | "all">("all");
  const [limit, setLimit] = useState(pageSize);
  const selected = caseId ? precedents.get(caseId) : undefined;
  const needle = query.trim().toLowerCase();
  const visible = catalogue.filter(
    (venture) =>
      (category === "all" || venture.category === category) &&
      (region === "all" || (region === "nz") === venture.country.startsWith("New Zealand")) &&
      [venture.name, venture.country, venture.focus].some((text) =>
        text.toLowerCase().includes(needle),
      ),
  );
  const records = (selected ? [selected] : visible)
    .flatMap((venture) =>
      venture.events.map((event) => ({ venture, event, evidence: eventEvidence(event) })),
    )
    .filter(({ evidence }) => kind === "all" || evidence.kind === kind)
    .sort(
      (left, right) =>
        right.event.end.localeCompare(left.event.end) ||
        left.venture.name.localeCompare(right.venture.name) ||
        left.event.id.localeCompare(right.event.id),
    );

  function choose(id: string) {
    setLimit(pageSize);
    if (id !== (caseId ?? "")) onCase(id);
  }

  return (
    <div className="vee-rookie vee-ledger">
      <div className="vee-page-heading">
        <div>
          <h1>Funding &amp; outcomes</h1>
          <p>Inspect the original sources behind the comparison catalogue.</p>
        </div>
        <a href="?view=rookie">Open Venture Outlook</a>
      </div>
      <div className="vee-ledger-layout">
        <aside className="vee-panel vee-ledger-controls" aria-label="Catalogue filters">
          <h2>Venture catalogue</h2>
          <label>
            Search ventures
            <input
              value={query}
              type="search"
              onChange={(event) => {
                setQuery(event.currentTarget.value);
                choose("");
              }}
            />
          </label>
          <label>
            Category
            <select
              value={category}
              onChange={(event) => {
                setCategory(event.currentTarget.value as Category | "all");
                choose("");
              }}
            >
              <option value="all">All categories</option>
              {Object.entries(categories).map(([id, name]) => (
                <option value={id} key={id}>
                  {name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Origin
            <select
              value={region}
              onChange={(event) => {
                setRegion(event.currentTarget.value);
                choose("");
              }}
            >
              <option value="all">All origins</option>
              <option value="nz">New Zealand</option>
              <option value="international">International</option>
            </select>
          </label>
          <label>
            Venture · {visible.length} found
            <select
              value={selected?.id ?? ""}
              onChange={(event) => choose(event.currentTarget.value)}
            >
              <option value="">All matching ventures</option>
              {visible.map((venture) => (
                <option value={venture.id} key={venture.id}>
                  {venture.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Evidence type
            <select
              value={kind}
              onChange={(event) => {
                setKind(event.currentTarget.value as EvidenceKind | "all");
                setLimit(pageSize);
              }}
            >
              <option value="all">All milestones</option>
              {Object.entries(evidenceKinds).map(([id, name]) => (
                <option value={id} key={id}>
                  {name}
                </option>
              ))}
            </select>
          </label>
        </aside>
        <section className="vee-panel vee-ledger-records" aria-labelledby="vee-ledger-heading">
          <div className="vee-ledger-summary">
            <div>
              <h2 id="vee-ledger-heading">{selected?.name ?? "Catalogue evidence"}</h2>
              <p>
                {selected
                  ? selected.country + " · " + selected.focus
                  : visible.length + (visible.length === 1 ? " venture" : " ventures")}
              </p>
            </div>
            <span aria-live="polite">
              {records.length} sourced {records.length === 1 ? "record" : "records"}
            </span>
          </div>
          <p className="vee-note">
            Selected public observations. Amounts retain their reported scope and currency.
          </p>
          {records.length === 0 && (
            <p>No records for these filters. Try a different evidence type or venture.</p>
          )}
          <ol className="vee-ledger-events">
            {records.slice(0, limit).map(({ venture, event, evidence }) => (
              <li key={event.id}>
                <div className="vee-ledger-date">
                  <strong>{event.date}</strong>
                  {!selected && (
                    <button
                      type="button"
                      className="vee-table-toggle"
                      onClick={() => choose(venture.id)}
                    >
                      {venture.name}
                    </button>
                  )}
                </div>
                <div>
                  <span className="vee-eyebrow">{evidenceKinds[evidence.kind]}</span>
                  <h3>{event.title}</h3>
                  <p>{event.description}</p>
                  {evidence.scope && <p>{evidence.scope}</p>}
                  <a href={event.url} target="_blank" rel="noreferrer">
                    {event.source}
                  </a>
                </div>
                <div className="vee-ledger-status">
                  <span>{evidence.status}</span>
                  {evidence.amount && <strong>{evidence.amount}</strong>}
                </div>
              </li>
            ))}
          </ol>
          {limit < records.length && (
            <button
              className="vee-table-toggle"
              type="button"
              onClick={() => setLimit(limit + pageSize)}
            >
              Show {Math.min(pageSize, records.length - limit)} more records
            </button>
          )}
        </section>
      </div>
      <EvidenceSuggestion />
    </div>
  );
}
