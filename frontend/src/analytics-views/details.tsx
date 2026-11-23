import { createContext, useCallback, useContext, useState, useRef, type ReactNode } from "react";
import type { BacktestEvent, BacktestSource } from "../api-schema";
import { eventLabels } from "../charts/encoding";
import type { Detail } from "../charts/figure";
import {
  type Fact,
  type Peer,
  type Snapshot,
  type Company,
  bars,
  fieldNames,
  formatDate,
  reviewNames,
  scoreBand,
  scoreValue,
  textValue,
} from "./data";

const DetailContext = createContext<(detail: Detail) => void>(() => {});
export const useDetail = () => useContext(DetailContext);

export function Details({ children }: { children: ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const trigger = useRef<HTMLElement | SVGElement | null>(null);
  const [detail, setDetail] = useState<Detail>();
  const open = useCallback((next: Detail) => {
    if (!dialog.current?.open) trigger.current = document.activeElement as HTMLElement | SVGElement;
    setDetail(next);
    if (!dialog.current?.open) dialog.current?.showModal();
  }, []);
  return (
    <DetailContext.Provider value={open}>
      {children}
      <dialog
        ref={dialog}
        className="vee-drawer"
        aria-labelledby="vee-detail-heading"
        onClose={() => trigger.current?.focus()}
      >
        <form method="dialog">
          <button className="vee-drawer-close">Close details</button>
        </form>
        <h2 id="vee-detail-heading">{detail?.heading ?? "Details"}</h2>
        {detail?.content}
      </dialog>
    </DetailContext.Provider>
  );
}

export function Source({ source, review }: { source: BacktestSource; review: string }) {
  return (
    <div className="vee-source">
      <span className="vee-badge">{review}</span>
      <a href={source.url} target="_blank" rel="noreferrer">
        {source.publisher} ·{" "}
        {formatDate(source.witness_on ?? source.published_on ?? source.available_on)}
      </a>
      <small>{source.locator}</small>
      <small>Available by {formatDate(source.available_on)}</small>
    </div>
  );
}

export function badge(fact: Fact) {
  return (
    reviewNames[fact.review_state] +
    (fact.second_reading_matched ? " · second reading matched" : "")
  );
}

export function FactDetails({ facts }: { facts: Fact[] }) {
  return (
    <ul className="vee-fact-details">
      {facts.map((fact) => (
        <li key={fact.name}>
          <strong>
            {fieldNames[fact.name]} · {textValue(fact.value)}
          </strong>
          <Source source={fact.source} review={badge(fact)} />
          {fact.reviewed_by && fact.reviewed_on && (
            <small>
              {fact.reviewed_by} · {formatDate(fact.reviewed_on)}
            </small>
          )}
        </li>
      ))}
    </ul>
  );
}

export function eventDetail(name: string, event: BacktestEvent, hindsight: boolean): Detail {
  const review = reviewNames[event.review_state];
  return {
    heading: `${name} · ${eventLabels[event.kind] ?? textValue(event.kind)}`,
    hint: `${hindsight ? "Hindsight · " : ""}${review} · ${event.source.publisher}`,
    content: (
      <>
        <p>
          {formatDate(event.date.value ?? "")}
          {hindsight ? " · Hindsight" : ""}
        </p>
        <Source source={event.source} review={review} />
      </>
    ),
  };
}

export function peerDetail(
  peer: Peer,
  company: Company,
  facts: Fact[],
  subjectFacts: Fact[],
  tie?: string,
  overrides: Snapshot = {},
): Detail {
  const comparisonFacts = facts.filter((fact) => Object.hasOwn(peer.field_scores, fact.name));
  const matching = Object.keys(peer.field_scores)
    .filter((key) => peer.field_scores[key] > 0)
    .slice(0, 3);
  const differing = Object.keys(peer.field_scores)
    .filter((key) => peer.field_scores[key] < 1)
    .slice(0, 3);
  const hypothetical = Object.entries(overrides).filter(([key]) =>
    Object.hasOwn(peer.field_scores, key),
  );
  const first = comparisonFacts[0];
  return {
    heading: company.name,
    hint: first ? `${badge(first)} · ${first.source.publisher}` : undefined,
    content: (
      <>
        <p>
          {scoreValue(peer.similarity)} · {scoreBand(peer)}
          {tie ? ` · ${tie}` : ""}
        </p>
        <p>
          {peer.failed_bars.length
            ? `Checks missed. ${peer.failed_bars.map((key) => bars[key]).join(", ")}.`
            : "Meets each comparison check."}
        </p>
        <dl className="vee-breakdown">
          <div>
            <dt>Shared evidence</dt>
            <dd>{scoreValue(peer.coverage)}</dd>
          </div>
          {peer.dimensions.map((dim) => (
            <div key={dim.dimension}>
              <dt>{dim.dimension}</dt>
              <dd>{scoreValue(dim.similarity)}</dd>
            </div>
          ))}
        </dl>
        {matching.length > 0 && (
          <p>Shared features · {matching.map((key) => fieldNames[key]).join(", ")}</p>
        )}
        {differing.length > 0 && (
          <p>Differences · {differing.map((key) => fieldNames[key]).join(", ")}</p>
        )}
        {hypothetical.length > 0 && (
          <>
            <h3>Hypothetical subject inputs</h3>
            <dl className="vee-breakdown">
              {hypothetical.map(([field, value]) => (
                <div key={field}>
                  <dt>{fieldNames[field]}</dt>
                  <dd>{textValue(value)}</dd>
                </div>
              ))}
            </dl>
          </>
        )}
        <h3>Peer facts</h3>
        <FactDetails facts={comparisonFacts} />
        {subjectFacts.length > 0 && (
          <>
            <h3>Recorded subject facts</h3>
            <FactDetails
              facts={subjectFacts.filter((fact) => Object.hasOwn(peer.field_scores, fact.name))}
            />
          </>
        )}
      </>
    ),
  };
}
