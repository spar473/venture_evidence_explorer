import * as Plot from "@observablehq/plot";
import { eventLastDate, eventTiming } from "./event-clock";
import { Figure, titleFor, type Row } from "./figure";
import {
  developmentColors,
  eventLabels,
  eventStyle,
  eventStyles,
  eventTimingLabels,
  patternMarker,
  type EventTiming,
} from "./encoding";
import {
  formatDate,
  scoreBand,
  scoreValue,
  rankablePeers,
  type Company,
  type Peer,
  type Scenario,
} from "../analytics-views/data";
import { eventDetail, peerDetail, useDetail } from "../analytics-views/details";
import type { Fact } from "../analytics-views/data";
import type { BacktestEvent } from "../api-schema";

const rounded = (n: number | null) => (n == null ? "" : n.toFixed(12));
const keyFor = (peer: Peer) => `${rounded(peer.product_customer)}|${rounded(peer.similarity)}`;

type PeerProps = {
  scenario: Scenario;
  companies: Map<string, Company>;
  facts: Record<string, Fact[]>;
  subjectFacts: Fact[];
  coveredPeers: ReadonlySet<string>;
};

export function PeerChart({
  scenario,
  companies,
  facts,
  subjectFacts,
  coveredPeers,
  productOnly = false,
  reserve = false,
}: PeerProps & { productOnly?: boolean; reserve?: boolean }) {
  const open = useDetail();
  const peers = rankablePeers(scenario.peers, coveredPeers);
  const groupMap = new Map<string, Peer[]>();
  for (const peer of peers) {
    const key = keyFor(peer);
    groupMap.set(key, [...(groupMap.get(key) ?? []), peer]);
  }
  const rows = peers.map((peer) => {
    const company = companies.get(peer.company_id)!;
    const group = groupMap.get(keyFor(peer))!;
    const tie =
      group.length > 1 ? `${group.length} tied at ${peer.similarity!.toFixed(2)}` : undefined;
    return {
      key: peer.company_id,
      values: [
        company.name,
        scoreValue(peer.product_customer),
        scoreValue(peer.similarity),
        peer.shared_fields,
        scoreBand(peer),
        tie ?? "—",
      ],
      detail: peerDetail(
        peer,
        company,
        facts[peer.company_id] ?? [],
        subjectFacts,
        tie,
        scenario.overrides,
      ),
    };
  });
  const byId = new Map(rows.map((row) => [row.key, row]));
  const points = [...groupMap.values()].map((group) => {
    const peer = group[0];
    if (group.length === 1) return { peer, row: byId.get(peer.company_id)!, label: "" };
    const heading = `${group.length} tied at ${peer.similarity!.toFixed(2)}`;
    return {
      peer,
      label: heading,
      row: {
        key: keyFor(peer),
        values: [heading, scoreBand(peer)],
        detail: {
          heading,
          content: (
            <ul className="vee-link-list">
              {group.map(({ company_id }) => (
                <li key={company_id}>
                  <button type="button" onClick={() => open(byId.get(company_id)!.detail)}>
                    {companies.get(company_id)!.name}
                  </button>
                </li>
              ))}
            </ul>
          ),
        },
      },
    };
  });
  const allMarks = [...rows, ...points.map(({ row }) => row).filter((row) => !byId.has(row.key))];
  const display = peers.map((peer) => ({
    peer,
    row: byId.get(peer.company_id)!,
    name: companies.get(peer.company_id)!.name,
    tie: groupMap.get(keyFor(peer))?.length ?? 1,
  }));
  const chartHeight = Math.max(195, 58 + display.length * 24);
  const bar = scenario.thresholds.product_customer;
  const min = scenario.thresholds.similarity;
  const maxX = Math.min(
    1,
    Math.max(0.55, ...peers.map((peer) => (peer.product_customer ?? 0) + 0.13)),
  );
  return (
    <Figure
      title={productOnly ? "Why no comps" : "Peer map"}
      summary={
        productOnly
          ? "Product and customer scores by company, with the minimum shown."
          : `Product and customer versus overall similarity. ${scenario.qualifying_count} peers clear all checks.`
      }
      columns={["Company", "Product and customer", "Similarity", "Shared facts", "Band", "Tie"]}
      rows={rows}
      markRows={allMarks}
      onDetail={open}
      reserve={reserve}
      defer={productOnly || reserve}
      placeholderHeight={productOnly ? chartHeight : undefined}
      marks={(width) =>
        productOnly
          ? {
              height: chartHeight,
              marginLeft: width < 420 ? 108 : 148,
              x: { label: "Product and customer", domain: [0, maxX], grid: true },
              y: {
                label: null,
                domain: display.map(({ name }) => name),
                tickFormat: (value) => (width < 420 ? String(value).slice(0, 17) : value),
              },
              marks: [
                Plot.ruleX([bar], { stroke: "#2858a5", strokeDasharray: "4 3" }),
                Plot.barX(display, {
                  x: ({ peer }) => Math.max(0.002, peer.product_customer ?? 0),
                  y: "name",
                  fill: ({ peer }) => ((peer.product_customer ?? 0) >= bar ? "#547dd9" : "#c7d3e4"),
                  title: ({ row }) => titleFor(row),
                  insetTop: 4,
                  insetBottom: 4,
                }),
                Plot.text(
                  display.filter(
                    (item, index) =>
                      item.tie > 1 && display[index - 1]?.row.values[5] !== item.row.values[5],
                  ),
                  {
                    x: ({ peer }) => peer.product_customer ?? 0,
                    y: "name",
                    text: ({ tie }) => `${tie} tied`,
                    textAnchor: "start",
                    dx: 7,
                    fill: "#364c70",
                  },
                ),
              ],
            }
          : {
              height: 258,
              marginLeft: 51,
              marginRight: width < 430 ? 21 : 29,
              x: { label: "Product and customer", domain: [-0.045, maxX], grid: true, ticks: 5 },
              y: { label: "Overall similarity", domain: [0, 1], grid: true, ticks: 5 },
              marks: [
                Plot.rect([{ x1: bar, x2: maxX, y1: min, y2: 1 }], {
                  x1: "x1",
                  x2: "x2",
                  y1: "y1",
                  y2: "y2",
                  fill: "#eaf0ff",
                }),
                Plot.ruleX([bar], { stroke: "#7288bd", strokeDasharray: "4 4" }),
                Plot.ruleY([min], { stroke: "#7288bd", strokeDasharray: "4 4" }),
                Plot.text([{ x: (maxX + bar) / 2, y: 0.91 }], {
                  x: "x",
                  y: "y",
                  text: () => "Score thresholds",
                  fill: "#304b7b",
                  fontWeight: 650,
                }),
                Plot.dot(points, {
                  x: ({ peer }) => peer.product_customer!,
                  y: ({ peer }) => peer.similarity!,
                  r: ({ peer }) => peer.shared_fields,
                  fill: ({ peer }) => (peer.qualifies ? "#254891" : "#fff"),
                  stroke: ({ peer }) => (peer.qualifies ? "#254891" : "#547293"),
                  strokeWidth: 1.5,
                  title: ({ row }) => titleFor(row),
                }),
                Plot.text(
                  points.filter(({ label }) => label),
                  {
                    x: ({ peer }) => peer.product_customer!,
                    y: ({ peer }) => peer.similarity!,
                    text: "label",
                    textAnchor: "start",
                    dx: 10,
                    dy: 0,
                    fill: "#364c70",
                    fontSize: 10,
                  },
                ),
              ],
            }
      }
    >
      <div className="vee-legend">
        {productOnly ? (
          <span>Product and customer bar · {bar.toFixed(2)}</span>
        ) : (
          <>
            <span>
              <i className="vee-dot filled" /> Clears all checks
            </span>
            <span>
              <i className="vee-dot" /> Not a comp
            </span>
            <span>Size · shared facts</span>
          </>
        )}
      </div>
    </Figure>
  );
}

export type EventSeries = {
  company: Company;
  events: BacktestEvent[];
  subject?: boolean;
  color?: string;
};
type EventPoint = {
  name: string;
  companyId: string;
  color: string;
  month: number;
  stage: string;
  track: string;
  kind: string;
  timing: EventTiming;
  review: Row;
};
const stages = ["Seed", "Extra round", "Series A", "Series B", "Closed"];
const roundKinds = new Set([
  "pre_series_a",
  "convertible_note",
  "seed_extension",
  "other_financing",
  "bridge",
  "crowdfunding",
]);

function calendarMonths(start: string, date: string) {
  const [year, month, day] = date.split("-").map(Number);
  const [entryYear, entryMonth, entryDay] = start.split("-").map(Number);
  return Math.max(0, (year - entryYear) * 12 + month - entryMonth + (day - entryDay) / 31);
}

export function eventPoints(
  series: EventSeries[],
  asof: string,
  showLaterPeers: boolean,
): EventPoint[] {
  return series.flatMap(({ company, events, subject, color }) => {
    let stage = 0;
    const visible = [company.entry, ...events].filter(
      (event) =>
        event.event_id === company.entry.event_id ||
        (showLaterPeers
          ? !subject || eventTiming(company, event, asof) !== "hindsight"
          : event.source.available_on <= asof),
    );
    return visible.map((event) => {
      if (event.kind.startsWith("closed_")) stage = 4;
      else if (["series_b", "series_c_plus"].includes(event.kind)) stage = Math.max(stage, 3);
      else if (["series_a", "series_a_equivalent"].includes(event.kind)) stage = Math.max(stage, 2);
      else if (roundKinds.has(event.kind)) stage = Math.max(stage, 1);
      const timing = eventTiming(company, event, asof);
      const eventName = eventLabels[event.kind] ?? event.kind.replaceAll("_", " ");
      const month =
        event.event_id === company.entry.event_id
          ? 0
          : calendarMonths(company.start, eventLastDate(company, event));
      return {
        name: company.name,
        companyId: company.company_id,
        color: color ?? developmentColors.other,
        month,
        stage: stages[stage],
        track: subject ? "Subject" : "Peer",
        kind: event.kind,
        timing,
        review: {
          key: event.event_id,
          values: [
            company.name,
            eventName,
            formatDate(event.date.value ?? ""),
            Math.round(month),
            eventTimingLabels[timing],
          ],
          detail: eventDetail(company.name, event, timing),
        },
      };
    });
  });
}

function eventDots(points: EventPoint[], y: "stage" | "name") {
  return Plot.dot(points, {
    x: "month",
    y,
    r: (point) => (point.track === "Subject" ? 5.5 : 4.2),
    fill: (point) =>
      point.timing === "late_source"
        ? "#fff"
        : eventStyle(point.kind) === "unknown"
          ? patternMarker
          : eventStyles[eventStyle(point.kind)].fill,
    stroke: (point) => eventStyles[eventStyle(point.kind)].stroke,
    symbol: (point: EventPoint) => eventStyles[eventStyle(point.kind)].symbol,
    strokeWidth: 1.4,
    title: ({ review }) => titleFor(review),
  });
}

export function StatusLegend({ strip = false }: { strip?: boolean }) {
  return (
    <div className="vee-legend">
      {(strip
        ? Object.entries(eventStyles)
        : Object.entries(eventStyles).filter(([key]) => key !== "exit")
      ).map(([key, style]) => (
        <span key={key}>
          <i
            className={`vee-symbol ${style.symbol} ${key}`}
            style={{ "--mark": style.fill, "--stroke": style.stroke } as React.CSSProperties}
          />
          {style.label}
        </span>
      ))}
    </div>
  );
}

export function Development({ series, asof }: { series: EventSeries[]; asof: string }) {
  const open = useDetail();
  const data = eventPoints(series, asof, true);
  const endpoints: EventPoint[] = [];
  const lines = series.flatMap(({ company }) => {
    const points = data.filter((point) => point.companyId === company.company_id);
    if (!points.length) return [];
    endpoints.push(points[points.length - 1]);
    return points.slice(1).flatMap((point, i) => [
      { ...points[i], segment: point.review.key, dashed: point.timing === "hindsight" },
      { ...point, segment: point.review.key, dashed: point.timing === "hindsight" },
    ]);
  });
  const visibleMax = Math.max(36, ...data.map((point) => point.month + 3));
  const line = (dashed: boolean) =>
    Plot.line(
      lines.filter((point) => point.dashed === dashed),
      {
        x: "month",
        y: "stage",
        z: "segment",
        curve: "step-after",
        stroke: "color",
        strokeWidth: (point) => (point.track === "Subject" ? 2.6 : 1.8),
        ...(dashed ? { strokeDasharray: "5 4" } : {}),
      },
    );
  return (
    <Figure
      title="Development curves"
      summary="Funding and closure milestones from each company’s first round. Each line is labelled at its last point."
      columns={["Company", "Event", "Date", "Month", "Timing"]}
      rows={data.map((point) => point.review)}
      onDetail={open}
      reserve
      defer
      marks={(width) => {
        const marginRight = Math.min(
          width * 0.37,
          Math.max(80, ...endpoints.map(({ name }) => name.length * 5.6 + 12)),
        );
        const marginLeft = width < 420 ? 67 : 80;
        const monthWidth = (width - marginLeft - marginRight) / visibleMax;
        const labels = stages.flatMap((stage) => {
          const atStage = endpoints
            .filter((point) => point.stage === stage)
            .sort((a, b) => a.month - b.month);
          return atStage.map((point) => {
            const neighbours = atStage.filter(
              (other) => Math.abs(other.month - point.month) * monthWidth < marginRight,
            );
            const slot = neighbours.indexOf(point);
            const offset = neighbours.length > 1 ? (slot - (neighbours.length - 1) / 2) * 13 : 0;
            return Plot.text([point], {
              x: "month",
              y: "stage",
              text: "name",
              dx: 8,
              dy: offset,
              textAnchor: "start",
              fill: "color",
              fontSize: 10,
              fontWeight: 650,
              stroke: "#fff",
              strokeWidth: 3,
              lineWidth: (marginRight - 10) / 10,
              textOverflow: "ellipsis",
              title: (item) => item.name,
            });
          });
        });
        return {
          height: 258,
          marginLeft,
          marginRight,
          marginBottom: 43,
          x: {
            label: "Months from first round",
            domain: [0, visibleMax],
            grid: true,
            ticks: width < 420 ? 4 : 6,
          },
          y: { label: null, domain: [...stages].reverse(), grid: true },
          marks: [line(false), line(true), eventDots([...data].reverse(), "stage"), ...labels],
        };
      }}
    >
      <div className="vee-legend">
        <span>
          <i className="vee-line" />
          {eventTimingLabels.known}
        </span>
        <span>
          <i className="vee-dot" />
          Source found later
        </span>
        <span>
          <i className="vee-line dashed" />
          {eventTimingLabels.hindsight}
        </span>
      </div>
    </Figure>
  );
}

export function EventStrip({
  series,
  asof,
  title = "Event strip",
  hindsight = false,
  scroll = false,
}: {
  series: EventSeries[];
  asof: string;
  title?: string;
  hindsight?: boolean;
  scroll?: boolean;
}) {
  const open = useDetail();
  const points = eventPoints(series, asof, hindsight).filter((point) => point.month <= 150);
  return (
    <Figure
      title={title}
      summary="Company events aligned at the first round, from month zero to 150. The first 36 months are shaded."
      columns={["Company", "Event", "Date", "Month", "Timing"]}
      rows={points.map((point) => point.review)}
      onDetail={open}
      plotScrollLabel={scroll ? "Scroll company event timeline" : undefined}
      marks={(width) => ({
        height: Math.max(156, series.length * 26 + 62),
        marginTop: scroll ? 42 : undefined,
        marginBottom: scroll ? 14 : undefined,
        marginLeft: width < 440 ? 106 : 175,
        x: {
          label: "Months from first round",
          axis: scroll ? "top" : "bottom",
          domain: [0, 150],
          grid: true,
          ticks: width < 440 ? 4 : 7,
        },
        y: {
          label: null,
          domain: series.map(({ company }) => company.name),
          grid: true,
          tickFormat: (name) => (width < 440 ? String(name).slice(0, 16) : name),
        },
        marks: [
          Plot.rectX([{ start: 0, end: 36 }], { x1: "start", x2: "end", fill: "#eef3ff" }),
          Plot.ruleX([36], { stroke: "#7288bd", strokeDasharray: "4 4" }),
          eventDots(points, "name"),
        ],
      })}
    >
      <StatusLegend strip />
    </Figure>
  );
}
