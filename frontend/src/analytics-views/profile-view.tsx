import { KPI, matchesFilter, type Filters } from "./shell";
import { Development, PeerChart, type EventSeries } from "../charts/peers";
import { FactDetails, badge, eventDetail, useDetail } from "./details";
import {
  type Cohort,
  type Company,
  type Peer,
  type Profile,
  type Robustness,
  formatDate,
  profileEvidence,
  scoreBand,
  scoreValue,
  textValue,
  uiOrder,
} from "./data";

const DAY = 86400000;
const asDay = (date: string) => Math.round(Date.parse(date + "T00:00:00Z") / DAY);
const dateAt = (day: number) => new Date(day * DAY).toISOString().slice(0, 10);

function moveMonth(date: string, delta: number) {
  const next = new Date(date + "T00:00:00Z");
  const day = next.getUTCDate();
  next.setUTCDate(1);
  next.setUTCMonth(next.getUTCMonth() + delta);
  const end = new Date(Date.UTC(next.getUTCFullYear(), next.getUTCMonth() + 1, 0)).getUTCDate();
  next.setUTCDate(Math.min(day, end));
  return next.toISOString().slice(0, 10);
}

const sameRank = (a: Peer, b: Peer) =>
  a.product_customer?.toFixed(12) === b.product_customer?.toFixed(12) &&
  a.similarity?.toFixed(12) === b.similarity?.toFixed(12);

export function CompanyProfile({
  profile,
  subject,
  cohort,
  companies,
  filters,
  playback,
  latest,
  onDate,
  robustness,
}: {
  profile: Profile;
  subject: Company;
  cohort: Cohort;
  companies: Map<string, Company>;
  filters: Filters;
  playback: string;
  latest: string;
  onDate: (date: string) => void;
  robustness?: Robustness;
}) {
  const open = useDetail();
  const peers = uiOrder(
    profile.recorded.peers.filter((peer) =>
      matchesFilter(companies.get(peer.company_id)!, filters),
    ),
  );
  const ranked = peers
    .filter((peer) => peer.similarity !== null)
    .filter((peer) => peer.product_customer !== null);
  const qualifying = ranked.filter((peer) => peer.qualifies);
  const pool = qualifying.length ? qualifying : ranked;
  const shown = pool.filter((peer, i) => i < 3 || sameRank(peer, pool[2]));
  const nearest = pool[0];
  const tied = nearest && pool.filter((peer) => sameRank(peer, nearest));
  const stability = robustness?.boundary_ties.reduce((count, tie) => count + tie.draws, 0);
  const covered = peers.filter((peer) => profile.covered_peer_ids.includes(peer.company_id)).length;
  const { subjectFacts: caseFacts, peerFacts } = profileEvidence(profile);
  const hasSharedSource =
    caseFacts.length > 0 &&
    caseFacts.every(
      (fact) =>
        fact.source.url === caseFacts[0].source.url &&
        fact.source.witness_on === caseFacts[0].source.witness_on &&
        fact.source.available_on === caseFacts[0].source.available_on,
    );
  const shownCompanies = [subject, ...shown.map((peer) => companies.get(peer.company_id)!)];
  const series: EventSeries[] = shownCompanies.map((company) => ({
    company,
    events: cohort.reveal[company.company_id].events,
    subject: company.company_id === subject.company_id,
  }));
  const chart = {
    scenario: { ...profile.recorded, peers, qualifying_count: qualifying.length },
    companies,
    facts: peerFacts,
    subjectFacts: caseFacts,
  };
  return (
    <>
      <section className="vee-playback" aria-label="Company playback">
        <div className="vee-playback-date">
          <label htmlFor="vee-playback">Playback date</label>
          <strong>{formatDate(playback)}</strong>
        </div>
        <div className="vee-playback-range">
          <input
            id="vee-playback"
            type="range"
            min={asDay(subject.start)}
            max={asDay(latest)}
            value={asDay(playback)}
            aria-valuetext={formatDate(playback)}
            onChange={(event) => onDate(dateAt(Number(event.currentTarget.value)))}
            onKeyDown={(event) => {
              const delta =
                event.key === "ArrowLeft" || event.key === "ArrowDown"
                  ? -1
                  : event.key === "ArrowRight" || event.key === "ArrowUp"
                    ? 1
                    : 0;
              if (!delta) return;
              event.preventDefault();
              const date = moveMonth(playback, delta);
              onDate(date < subject.start ? subject.start : date > latest ? latest : date);
            }}
          />
          <div>
            <span>{formatDate(subject.start)}</span>
            <span>Today</span>
          </div>
        </div>
        <button type="button" onClick={() => onDate(subject.start)}>
          First round
        </button>
        <button type="button" onClick={() => onDate(latest)}>
          Today
        </button>
      </section>
      <KPI
        values={[
          { name: "Comps found", value: `${qualifying.length} of 3 needed` },
          { name: "Peers with enough evidence", value: `${covered} of ${peers.length} eligible` },
          {
            name: "Nearest on product and customer",
            value: !nearest
              ? "—"
              : tied.length > 1
                ? `${tied.length} tied`
                : companies.get(nearest.company_id)!.name,
            hint: nearest
              ? `Product ${scoreValue(nearest.product_customer)} · overall ${scoreValue(nearest.similarity)} · ${scoreBand(nearest)}`
              : undefined,
          },
          {
            name: "Ranking stability · full pool",
            value: !robustness?.baseline_ranks.length
              ? "—"
              : stability
                ? "Top-three tie"
                : "No boundary tie",
            hint: stability
              ? `${stability.toLocaleString("en-NZ")} of ${robustness!.draws.toLocaleString("en-NZ")} draws`
              : undefined,
          },
        ]}
      />
      <p className="vee-view-summary">
        {!caseFacts.length
          ? `No qualifying evidence public by ${formatDate(profile.cutoff)}. A dated offering and buyer source would help.`
          : !qualifying.length
            ? "No comps clear all checks. Dated offering and buyer evidence would help."
            : `${qualifying.length} peers clear all checks. Scores use entry-date evidence.`}
      </p>
      <div className="vee-columns vee-profile-hero">
        <PeerChart {...chart} />
        <Development series={series} asof={playback} />
      </div>
      <section className="vee-evidence vee-panel">
        <div className="vee-section-heading">
          <h2>Entry evidence</h2>
          <button
            type="button"
            onClick={() =>
              open({
                heading: `${subject.name} · first round`,
                content: eventDetail(subject.name, subject.entry, false).content,
              })
            }
          >
            First-round source
          </button>
        </div>
        {!caseFacts.length ? (
          <p>No scoreable entry facts.</p>
        ) : (
          <>
            <div className="vee-fact-chips">
              {caseFacts.map((fact) => (
                <button
                  type="button"
                  key={fact.name}
                  title={badge(fact)}
                  onClick={() =>
                    open({ heading: subject.name, content: <FactDetails facts={[fact]} /> })
                  }
                >
                  {fact.name === "description" ? "Offering" : `${textValue(fact.value)}`}{" "}
                  <span aria-hidden="true">·</span> {badge(fact).split(" · ")[0]}
                </button>
              ))}
            </div>
            {hasSharedSource && (
              <a href={caseFacts[0].source.url} target="_blank" rel="noreferrer">
                {caseFacts[0].source.publisher} · {formatDate(caseFacts[0].source.available_on)}
              </a>
            )}
            <button
              type="button"
              className="vee-text-button"
              onClick={() =>
                open({
                  heading: `${subject.name} · entry facts`,
                  content: <FactDetails facts={caseFacts} />,
                })
              }
            >
              Review and source details
            </button>
          </>
        )}
      </section>
      {!qualifying.length && <PeerChart {...chart} productOnly />}
    </>
  );
}
