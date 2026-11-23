import { useEffect, useMemo, useState } from "react";
import { EventStrip, PeerChart } from "../charts/peers";
import { CountBars, Tornado } from "../charts/labs";
import { matchesFilter, type Filters } from "./shell";
import { peerDetail } from "./details";
import {
  STATIC,
  fieldNames,
  formatDate,
  profileEvidence,
  textValue,
  uiOrder,
  type Cohort,
  type Company,
  type Peer,
  type Profile,
  type Robustness,
  type Scenario,
  type Snapshot,
} from "./data";
import { scoreScenario } from "./scorer";

const mainFields = ["product_type", "buyer", "business_model", "paid_pilot_or_revenue"];

export function ScenarioLab({
  profile,
  subject,
  cohort,
  companies,
  filters,
  robustness,
}: {
  profile: Profile;
  subject: Company;
  cohort: Cohort;
  companies: Map<string, Company>;
  filters: Filters;
  robustness?: Robustness;
}) {
  const [selected, setSelected] = useState("recorded");
  const [custom, setCustom] = useState<Snapshot>({});
  const [savedCustom, setSavedCustom] = useState<Scenario>();
  const localCustom = useMemo(() => scoreScenario(profile, custom), [profile, custom]);
  useEffect(() => {
    if (STATIC || selected !== "custom") return;
    const controller = new AbortController();
    fetch(`/api/scenario/${profile.company_id}`, {
      method: "POST",
      signal: controller.signal,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ overrides: custom }),
    })
      .then((response) => (response.ok ? (response.json() as Promise<Scenario>) : null))
      .then((result) => {
        if (result && !controller.signal.aborted) setSavedCustom(result);
      })
      .catch(() => {});
    return () => controller.abort();
  }, [custom, profile.company_id, selected]);
  const customResult =
    savedCustom && JSON.stringify(savedCustom.overrides) === JSON.stringify(custom)
      ? savedCustom
      : localCustom;
  const options = [...profile.presets, { id: "custom", name: "Custom", result: customResult }];
  const chosen = options.find(({ id }) => id === selected) ?? options[0];
  const visible = (peers: Peer[]) =>
    peers.filter((peer) => matchesFilter(companies.get(peer.company_id)!, filters));
  const chosenPeers = visible(chosen.result.peers);
  const qualifiers = uiOrder(chosenPeers.filter(({ qualifies }) => qualifies));
  const activeOverrides = chosen.result.overrides;
  const followThrough = filters.asof < cohort.audit_date ? filters.asof : cohort.audit_date;
  const { subjectFacts, peerFacts } = profileEvidence(profile);
  const topGroup = robustness?.baseline_ranks[0] ?? [];
  const top = topGroup.length === 1 ? topGroup[0] : null;
  const topScore = profile.recorded.peers.find(({ company_id }) => company_id === top)?.similarity;
  const boundary = robustness?.boundary_ties?.[0];
  const boundaryScore = profile.recorded.peers.find(
    ({ company_id }) => company_id === boundary?.companies[0],
  )?.similarity;
  const membership = robustness
    ? robustness.baseline_ranks.flatMap((group) =>
        group.flatMap((key) => {
          const count = robustness.membership[key];
          const peer = profile.recorded.peers.find(({ company_id }) => company_id === key);
          const company = companies.get(key)!;
          return count && peer
            ? [
                {
                  id: key,
                  name: company.name,
                  value: count,
                  denominator: robustness.draws,
                  detail: peerDetail(peer, company, peerFacts[key] ?? [], subjectFacts),
                },
              ]
            : [];
        }),
      )
    : [];
  function fieldSelect(field: string) {
    const recorded = profile.scorer.subject[field];
    const choices = profile.scorer.options[field] ?? [];
    return (
      <label key={field} className="vee-fact-toggle">
        <span>{fieldNames[field]}</span>
        <select
          aria-label={fieldNames[field]}
          disabled={!subjectFacts.length}
          value={String(activeOverrides[field] ?? "")}
          onChange={(event) => {
            const value = event.currentTarget.value;
            const next = { ...activeOverrides };
            if (value) next[field] = value;
            else delete next[field];
            setCustom(next);
            setSelected("custom");
          }}
        >
          <option value="">
            {recorded != null ? `${textValue(recorded)} · recorded` : "Unrecorded"}
          </option>
          {choices
            .filter((value) => value !== recorded)
            .map((value) => (
              <option key={value} value={value}>
                {textValue(value)}
              </option>
            ))}
        </select>
      </label>
    );
  }
  return (
    <>
      <div className="vee-columns vee-scenario-hero">
        <CountBars
          selected={selected}
          onSelect={setSelected}
          rows={options.map(({ id, name, result }) => ({
            id,
            name,
            value: visible(result.peers).filter(({ qualifies }) => qualifies).length,
          }))}
        />
        <section className="vee-panel vee-controls">
          <div className="vee-section-heading">
            <h2>{subject.name} · entry facts</h2>
            <span className="vee-tag">{selected === "recorded" ? "Recorded" : "Hypothetical"}</span>
          </div>
          {subjectFacts.length ? (
            <p className="vee-note">Scored at {formatDate(profile.cutoff)}.</p>
          ) : (
            <p className="vee-note">
              No qualifying evidence public by {formatDate(profile.cutoff)}. A dated offering and
              buyer source would help.
            </p>
          )}
          <div className="vee-toggle-grid">{mainFields.map(fieldSelect)}</div>
          <details>
            <summary>More fields</summary>
            <div className="vee-toggle-grid">
              {Object.keys(profile.scorer.options)
                .filter((field) => !mainFields.includes(field))
                .map(fieldSelect)}
            </div>
          </details>
        </section>
      </div>
      <PeerChart
        scenario={{ ...chosen.result, peers: chosenPeers, qualifying_count: qualifiers.length }}
        companies={companies}
        facts={peerFacts}
        subjectFacts={subjectFacts}
      />
      {qualifiers.length > 0 && (
        <>
          <p className="vee-note">
            Hindsight · {qualifiers.length} qualifying {qualifiers.length === 1 ? "peer" : "peers"}.
            Records through {formatDate(followThrough)}.
          </p>
          <EventStrip
            title="What qualifying peers went on to do"
            asof={profile.cutoff}
            hindsight
            series={qualifiers
              .filter(({ company_id }) => companies.get(company_id)!.end <= followThrough)
              .map(({ company_id }) => ({
                company: companies.get(company_id)!,
                events: cohort.reveal[company_id].events.filter(
                  ({ source }) => source.available_on <= followThrough,
                ),
              }))}
          />
        </>
      )}
      <section className="vee-section-heading vee-section-title">
        <h2>Recorded score robustness</h2>
        <span className="vee-note">Overall similarity · full entry-date peer pool</span>
      </section>
      {boundary && boundaryScore != null && (
        <aside className="vee-callout">
          <strong>Key tension</strong> · {boundary.companies.length} tied at{" "}
          {boundaryScore.toFixed(2)} in the recorded ranking. All boundary ties count.
        </aside>
      )}
      {topGroup.length > 1 && (
        <p className="vee-note">{topGroup.length} peers tie for the highest recorded similarity.</p>
      )}
      {membership.length > 0 && (
        <div className="vee-columns">
          {robustness && top && topScore != null && (
            <Tornado
              name={companies.get(top)!.name}
              ranges={robustness.ranges[top]}
              baseline={topScore}
              facts={peerFacts[top] ?? []}
            />
          )}
          <CountBars rows={membership} />
        </div>
      )}
      {!membership.length && (
        <p className="vee-note">Weight checks require shared entry evidence.</p>
      )}
    </>
  );
}
