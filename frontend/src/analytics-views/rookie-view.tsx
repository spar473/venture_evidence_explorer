import { useState } from "react";
import * as Plot from "@observablehq/plot";
import { Figure, titleFor, type Row } from "../charts/figure";
import { useDetail } from "./details";
import { evidenceUrl } from "./venture-evidence";
import { rankPrecedents } from "./venture-retrieval";
import {
  categories,
  elapsedMilestones,
  precedents,
  scenarioPath,
  subjects,
  type Category,
  type Milestone,
} from "./rookie-model";
import "./rookie.css";

const roleColors = {
  Upside: "#057365",
  Development: "#233f83",
  Downside: "#a44826",
  Selected: "#536481",
};
const years = [1, 3, 5, 7, 10, 15];
const presets = [
  { name: "Faster progress", advance: 28, stall: 4 },
  { name: "Reference inputs", advance: 18, stall: 8 },
  { name: "Slower progress", advance: 10, stall: 16 },
];

function milestoneDetail(name: string, item: Milestone, timing?: string) {
  return {
    heading: item.title,
    hint: name + " · " + item.date,
    content: (
      <>
        <p>
          {name} · {item.date}
          {timing && " · " + timing}
        </p>
        <p>{item.description}</p>
        <a href={item.url} target="_blank" rel="noreferrer">
          {item.source}
        </a>
      </>
    ),
  };
}

function Scenario({ goal }: { goal: string }) {
  const [advance, setAdvance] = useState(18);
  const [stall, setStall] = useState(8);
  const [steps, setSteps] = useState<1 | 2>(2);
  const open = useDetail();
  const path = scenarioPath(advance / 100, stall / 100, steps, 12);
  const last = path[path.length - 1];
  const percent = (fraction: number) => Math.round(100 * fraction) + "%";
  const rows: Row[] = path.map(({ quarter, reached, stalled, inProgress }) => ({
    key: String(quarter),
    values: [quarter * 3, percent(reached), percent(stalled), percent(inProgress)],
  }));
  return (
    <section className="vee-rookie-simulator" aria-label="Conditional simulator">
      <div className="vee-panel">
        <h2>Scenario inputs</h2>
        <p>{goal}.</p>
        <p>Illustrative rates that you can change. VEE has no fitted estimate for this venture.</p>
        <div className="vee-rookie-presets" role="group" aria-label="Illustrative presets">
          {presets.map((preset) => (
            <button
              key={preset.name}
              type="button"
              className="vee-table-toggle"
              aria-pressed={advance === preset.advance && stall === preset.stall}
              onClick={() => {
                setAdvance(preset.advance);
                setStall(preset.stall);
              }}
            >
              {preset.name}
            </button>
          ))}
        </div>
        <label>
          Steps to target
          <select value={steps} onChange={(event) => setSteps(event.target.value === "1" ? 1 : 2)}>
            <option value="1">One step</option>
            <option value="2">Two sequential steps</option>
          </select>
        </label>
        <label>
          Advance per quarter · {advance}%
          <input
            type="range"
            min={0}
            max={100 - stall}
            value={advance}
            onChange={(event) => setAdvance(event.currentTarget.valueAsNumber)}
          />
        </label>
        <label>
          Stall per quarter · {stall}%
          <input
            type="range"
            min={0}
            max={100 - advance}
            value={stall}
            onChange={(event) => setStall(event.currentTarget.valueAsNumber)}
          />
        </label>
        <p>
          At 36 months · {percent(last.reached)} reach the target, {percent(last.stalled)} stall and{" "}
          {percent(last.inProgress)} remain in progress under these assumptions.
        </p>
      </div>
      <Figure
        title="What-if trajectory"
        summary="Modelled target attainment, stall and ongoing paths under illustrative inputs"
        columns={["Month", "Reached", "Stalled", "In progress"]}
        rows={rows}
        onDetail={open}
        synthetic="Illustrative model · probabilities come from the inputs"
        marks={() => ({
          height: 290,
          x: { label: "Months from scenario start", ticks: [0, 6, 12, 18, 24, 30, 36] },
          y: {
            label: "Modelled share",
            domain: [0, 1],
            tickFormat: (d) => percent(Number(d)),
            grid: true,
          },
          color: {
            domain: ["Reached", "Stalled", "In progress"],
            range: ["#057365", "#a44826", "#233f83"],
            legend: true,
          },
          marks: [
            Plot.lineY(
              path.flatMap(({ quarter, reached, stalled, inProgress }) => [
                { month: quarter * 3, share: reached, result: "Reached" },
                { month: quarter * 3, share: stalled, result: "Stalled" },
                { month: quarter * 3, share: inProgress, result: "In progress" },
              ]),
              { x: "month", y: "share", stroke: "result", curve: "step-after", strokeWidth: 2.5 },
            ),
          ],
        })}
      />
    </section>
  );
}

function PrecedentSearch({
  category,
  initialQuery,
  excluded,
  onPlot,
}: {
  category: Category;
  initialQuery: string;
  excluded: string[];
  onPlot: (id: string) => void;
}) {
  const [query, setQuery] = useState(initialQuery);
  const matches = rankPrecedents(query, category).slice(0, 5);
  return (
    <section className="vee-panel vee-retrieval" aria-label="Find more precedents">
      <h2>Find more precedents</h2>
      <label>
        What should the comparison focus on?
        <input
          value={query}
          maxLength={300}
          type="search"
          onChange={(event) => setQuery(event.currentTarget.value)}
        />
      </label>
      <p className="vee-note">
        Text matches from dossier starting records. Check the shared terms and read the source
        before using a match.
      </p>
      {matches.length ? (
        <ol className="vee-retrieval-results">
          {matches.map(({ venture, similarity, matches: terms }) => (
            <li key={venture.id}>
              <div>
                <a href={evidenceUrl(venture.id)}>
                  <strong>{venture.name}</strong>
                </a>
                <small>
                  Text match {similarity.toFixed(2)} · {terms.join(", ")}
                </small>
              </div>
              {excluded.includes(venture.id) ? (
                <small>Already on chart</small>
              ) : (
                <button
                  className="vee-table-toggle"
                  type="button"
                  onClick={() => onPlot(venture.id)}
                >
                  Plot {venture.name}
                </button>
              )}
            </li>
          ))}
        </ol>
      ) : (
        <p role="status">
          No shared terms in this category. Try a shorter query or browse the catalogue.
        </p>
      )}
    </section>
  );
}

export default function RookieOutlook({
  subjectId,
  onSubject,
}: {
  subjectId: string | null;
  onSubject: (id: string) => void;
}) {
  const subject = subjects.find(({ id }) => id === subjectId) ?? subjects[0];
  const [year, setYear] = useState(7);
  const [extra, setExtra] = useState<{ subject: string; id: string }>();
  const open = useDetail();
  const cohort = [...precedents.values()].filter(({ category }) => category === subject.category);
  const selected = subject.peers.map((peer) => {
    const venture = precedents.get(peer.venture);
    const entry = venture?.events[peer.event - 1];
    if (!venture || !entry) throw new Error("Invalid precedent selection: " + peer.venture);
    return { ...peer, venture, entry };
  });
  const extraVenture =
    extra?.subject === subject.id ? cohort.find(({ id }) => id === extra.id) : undefined;
  const plotted = extraVenture
    ? [
        ...selected,
        { role: "Selected" as const, venture: extraVenture, entry: extraVenture.events[0] },
      ]
    : selected;
  const marks = plotted.flatMap(({ role, venture, entry }) =>
    elapsedMilestones(venture, entry, year * 12).map((point) => {
      const { event, from, through } = point;
      const timing = point.entry
        ? "Comparison starting point"
        : from + "–" + through + " months after starting point";
      const row: Row = {
        key: event.id,
        values: [venture.name, event.title, event.date, timing, event.source],
        detail: milestoneDetail(venture.name, event, timing),
      };
      return { ...point, name: venture.name, role, row };
    }),
  );

  return (
    <div className="vee-rookie">
      <div className="vee-page-heading">
        <div>
          <h1>Venture outlook</h1>
          <p>
            Compare early New Zealand ventures with historical paths, then test your own
            assumptions.
          </p>
        </div>
      </div>
      <div className="vee-filters vee-rookie-controls">
        <label className="vee-select-label">
          Category
          <select
            value={subject.category}
            onChange={(event) => {
              const next = subjects.find(
                ({ category }) => category === (event.currentTarget.value as Category),
              );
              if (next) onSubject(next.id);
            }}
          >
            {Object.entries(categories).map(([key, name]) => (
              <option key={key} value={key}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <label className="vee-select-label">
          NZ venture
          <select value={subject.id} onChange={(event) => onSubject(event.currentTarget.value)}>
            {subjects
              .filter(({ category }) => category === subject.category)
              .map(({ id, name }) => (
                <option key={id} value={id}>
                  {name}
                </option>
              ))}
          </select>
        </label>
        <label className="vee-select-label">
          Peer follow-up
          <select value={year} onChange={(event) => setYear(Number(event.currentTarget.value))}>
            {years.map((value) => (
              <option key={value} value={value}>
                {value} {value === 1 ? "year" : "years"}
              </option>
            ))}
          </select>
        </label>
      </div>
      <section className="vee-rookie-subject vee-panel">
        <div>
          <div className="vee-eyebrow">New Zealand venture · {subject.date}</div>
          <h2>{subject.name}</h2>
          <p>
            {subject.summary}{" "}
            <a href={subject.source} target="_blank" rel="noreferrer">
              Source
            </a>
          </p>
        </div>
        <div className="vee-rookie-goal">
          <div className="vee-eyebrow">Next milestone</div>
          <strong>{subject.goal}</strong>
          <p>{subject.question}</p>
        </div>
      </section>
      <Figure
        title="What happened to the precedents?"
        summary="Historical milestone timelines from each precedent’s editorial starting point"
        columns={["Venture", "Milestone", "Event date", "Elapsed time", "Source"]}
        rows={marks.map(({ row }) => row)}
        onDetail={open}
        marks={(width) => ({
          height: extraVenture ? 270 : 230,
          marginLeft: width > 580 ? 160 : 90,
          x: {
            label: "Years from the selected peer milestone",
            domain: [0, year],
            grid: true,
            ticks: Math.min(year + 1, 6),
          },
          y: {
            domain: plotted.map(({ venture }) => venture.name),
            label: null,
            tickFormat: (value) =>
              width > 580 ? String(value) : String(value).split(" ").slice(0, 1).join(" "),
          },
          color: { domain: Object.keys(roleColors), range: Object.values(roleColors) },
          marks: [
            Plot.ruleY(marks, {
              y: "name",
              x1: (p) => p.from / 12,
              x2: (p) => p.through / 12,
              stroke: "role",
              strokeWidth: 2,
              strokeOpacity: 0.8,
            }),
            Plot.dot(marks, {
              x: (p) => p.through / 12,
              y: "name",
              fill: "role",
              r: 5,
              title: (p) => titleFor(p.row),
            }),
          ],
        })}
      >
        <p className="vee-note">
          Editorial pathway analogues. Bars show timing ranges where dates are imprecise.
        </p>
        {extraVenture && (
          <p className="vee-note">
            Added for inspection from its first dossier record · {extraVenture.name}{" "}
            <button type="button" className="vee-table-toggle" onClick={() => setExtra(undefined)}>
              Remove added venture
            </button>
          </p>
        )}
      </Figure>
      <div className="vee-rookie-peers">
        {selected.map(({ role, venture, entry, reason }) => (
          <section
            className="vee-panel"
            key={venture.id}
            style={{ borderTopColor: roleColors[role] }}
          >
            <div className="vee-eyebrow">{role} analogue</div>
            <h2>{venture.name}</h2>
            <p>{reason}</p>
            <div className="vee-rookie-peer-links">
              <button
                className="vee-table-toggle"
                type="button"
                onClick={() => open(milestoneDetail(venture.name, entry))}
              >
                Starting evidence
              </button>
              <a href={evidenceUrl(venture.id)}>Funding &amp; outcomes</a>
            </div>
          </section>
        ))}
      </div>
      <Scenario key={"scenario-" + subject.id} goal={subject.goal} />
      <PrecedentSearch
        key={"retrieval-" + subject.id}
        category={subject.category}
        initialQuery={subject.summary + " " + subject.goal}
        excluded={plotted.map(({ venture }) => venture.id)}
        onPlot={(id) => setExtra({ subject: subject.id, id })}
      />
      <details className="vee-panel vee-rookie-library">
        <summary>
          {cohort.length} precedents in {categories[subject.category]}
        </summary>
        <ul>
          {cohort.map((venture) => (
            <li key={venture.id}>
              <button
                className="vee-table-toggle"
                type="button"
                onClick={() =>
                  open({
                    heading: venture.name,
                    content: (
                      <>
                        <p>
                          {venture.country} · {venture.focus}
                        </p>
                        <ul className="vee-fact-details">
                          {venture.events.map((event) => (
                            <li key={event.id}>
                              <strong>
                                {event.date} · {event.title}
                              </strong>
                              <p>{event.description}</p>
                              <a href={event.url} target="_blank" rel="noreferrer">
                                {event.source}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </>
                    ),
                  })
                }
              >
                {venture.name} · {venture.country}
              </button>
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}
