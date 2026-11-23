import * as Plot from "@observablehq/plot";
import { eventStyles } from "./encoding";
import { Figure, titleFor, type Row } from "./figure";
import { useDetail, FactDetails, badge } from "../analytics-views/details";
import { scoreValue, type Fact, type Method, type Robustness } from "../analytics-views/data";

export function CountBars({
  rows,
  selected,
  onSelect,
}: {
  rows: { id: string; name: string; value: number; detail?: Row["detail"]; denominator?: number }[];
  selected?: string;
  onSelect?: (id: string) => void;
}) {
  const open = useDetail();
  const membership = !onSelect;
  const data = rows.map((item) => ({
    ...item,
    row: {
      key: item.id,
      values: [
        item.name,
        item.denominator
          ? `${item.value.toLocaleString("en-NZ")} of ${item.denominator.toLocaleString("en-NZ")}`
          : item.value,
      ],
      detail: item.detail ?? { heading: item.name, content: null },
    },
  }));
  return (
    <Figure
      title={membership ? "Top-three membership" : "Qualifying peers by scenario"}
      summary={
        membership
          ? "Number of weight draws in which each peer reached the top three, including boundary ties."
          : "Number of qualifying peers for each recorded or hypothetical setting. Select a bar to inspect its peer map."
      }
      columns={[membership ? "Peer" : "Scenario", membership ? "Draws" : "Qualifying peers"]}
      rows={data.map(({ row }) => row)}
      onDetail={(detail) => {
        if (!onSelect) return open(detail);
        const item = data.find(({ name }) => name === detail.heading);
        if (item) onSelect(item.id);
      }}
      marks={(width) => ({
        height: Math.max(178, data.length * 30 + 56),
        marginLeft: width < 460 ? 134 : 151,
        marginRight: membership ? 102 : 31,
        x: {
          label: membership ? "Draws" : "Qualifying peers",
          grid: true,
          ticks: 4,
          domain: [0, Math.max(1, ...data.map(({ value }) => value))],
        },
        y: {
          label: null,
          domain: data.map(({ name }) => name),
          tickFormat: (name) => (width < 460 ? String(name).slice(0, 22) : name),
        },
        marks: [
          Plot.barX(data, {
            x: (item) => Math.max(item.value, 0.08),
            y: "name",
            insetTop: 4,
            insetBottom: 4,
            fill: (item) => (item.id === selected ? "#1e3a8a" : "#a9bfee"),
            title: ({ row }) => titleFor(row),
          }),
          Plot.text(data, {
            x: "value",
            y: "name",
            text: ({ row }) => String(row.values[1]),
            textAnchor: "start",
            dx: 5,
            fontWeight: 650,
            fill: "#293e62",
          }),
        ],
      })}
    />
  );
}

export function Tornado({
  name,
  ranges,
  baseline,
  facts,
}: {
  name: string;
  ranges: Robustness["ranges"][string];
  baseline: number;
  facts: Fact[];
}) {
  const open = useDetail();
  const data = Object.entries(ranges)
    .map(([dimension, [low, high]]) => {
      const row: Row = {
        key: dimension,
        values: [dimension, scoreValue(low), scoreValue(high)],
        detail: {
          heading: `${name} · ${dimension}`,
          hint: facts[0] ? `${badge(facts[0])} · ${facts[0].source.publisher}` : undefined,
          content: (
            <>
              <p>
                {scoreValue(low)} to {scoreValue(high)} · recorded {scoreValue(baseline)}
              </p>
              <FactDetails facts={facts} />
            </>
          ),
        },
      };
      return { dimension, low, high, row };
    })
    .sort((a, b) => b.high - b.low - (a.high - a.low));
  const min = Math.min(...data.map(({ low }) => low)) - 0.025;
  const max = Math.max(...data.map(({ high }) => high)) + 0.025;
  return (
    <Figure
      title="Sensitivity by weight"
      summary={`Similarity range for ${name} after each individual weight adjustment.`}
      columns={["Weight", "Lower similarity", "Upper similarity"]}
      rows={data.map(({ row }) => row)}
      onDetail={open}
      marks={(width) => ({
        height: 224,
        marginLeft: width < 440 ? 125 : 153,
        x: { label: "Overall similarity", domain: [min, max], grid: true, ticks: 5 },
        y: { label: null, domain: data.map(({ dimension }) => dimension) },
        marks: [
          Plot.ruleX([baseline], { stroke: "#486599", strokeDasharray: "4 3" }),
          Plot.barX(data, {
            x1: "low",
            x2: "high",
            y: "dimension",
            fill: "#a9bfee",
            insetTop: 4,
            insetBottom: 4,
          }),
          Plot.dot(data, {
            x: (item) => (item.low + item.high) / 2,
            y: "dimension",
            r: 4.5,
            fill: "#1e3a8a",
            title: ({ row }) => titleFor(row),
          }),
        ],
      })}
    >
      <div className="vee-legend">
        <span>{name}</span>
        <span>Recorded score · {scoreValue(baseline)}</span>
      </div>
    </Figure>
  );
}

const causes: Record<
  string,
  { label: string; fill: string; symbol: "circle" | "diamond" | "triangle" }
> = {
  outcome: { ...eventStyles.series, label: "Series A" },
  closure: eventStyles.closure,
  exit: { ...eventStyles.exit, fill: eventStyles.exit.stroke },
};
const percent = (value: number) => `${Math.round(value * 100)}%`;

export function MethodFigures({
  method,
  referenceCount,
}: {
  method: Method;
  referenceCount: number;
}) {
  const open = useDetail();
  const curves = method.curves.map((point) => {
    const label = causes[point.cause].label;
    const row: Row = {
      key: point.cause + point.month,
      values: [label, point.month, percent(point.value)],
      detail: {
        heading: `Synthetic ${label} · month ${point.month}`,
        content: <p>Cumulative incidence · {point.value.toFixed(3)}</p>,
      },
    };
    return { ...point, row };
  });
  const sizes = method.sizes.map((point) => {
    const label = point.label === "Today" ? `Today · ${point.n}` : point.label;
    const row: Row = {
      key: point.label,
      values: [label, percent(point.lower), percent(point.value), percent(point.upper)],
      detail: {
        heading: `Synthetic sample · ${point.n}`,
        content: (
          <p>
            Central estimate {point.value.toFixed(3)} · interval {point.lower.toFixed(3)}–
            {point.upper.toFixed(3)}
          </p>
        ),
      },
    };
    return { ...point, label, row };
  });
  const calibration = method.calibration.map((point) => {
    const label = `Group ${point.group}`;
    const row: Row = {
      key: label,
      values: [label, percent(point.estimate), percent(point.observed), point.held_out_n],
      detail: {
        heading: `Synthetic ${label.toLowerCase()}`,
        content: (
          <p>
            Estimate {point.estimate.toFixed(3)} · held-out incidence {point.observed.toFixed(3)}
          </p>
        ),
      },
    };
    return { ...point, row };
  });
  return (
    <>
      <Figure
        title="Competing outcomes"
        summary="Synthetic weighted incidence curves up to month 36."
        synthetic={method.label}
        columns={["Event", "Month", "Cumulative incidence"]}
        rows={curves.map(({ row }) => row)}
        onDetail={open}
        marks={() => ({
          height: 285,
          marginLeft: 58,
          x: {
            label: "Months from first round",
            domain: [0, 36],
            ticks: [0, 6, 12, 18, 24, 30, 36],
          },
          y: {
            label: "Cumulative incidence",
            domain: [0, 0.6],
            tickFormat: percent,
            grid: true,
            ticks: 4,
          },
          marks: [
            Plot.line(curves, {
              x: "month",
              y: "value",
              z: "cause",
              stroke: (d) => causes[d.cause].fill,
              curve: "step-after",
              strokeWidth: 2.6,
            }),
            Plot.dot(
              curves.filter(({ month }) => month > 0 && month % 6 === 0),
              {
                x: "month",
                y: "value",
                fill: (d) => causes[d.cause].fill,
                symbol: (d: (typeof curves)[number]) => causes[d.cause].symbol,
                stroke: "#fff",
                r: 4.5,
                title: ({ row }) => titleFor(row),
              },
            ),
          ],
        })}
      >
        <div className="vee-legend">
          {Object.entries(causes).map(([key, item]) => (
            <span key={key}>
              <i
                className={`vee-symbol ${item.symbol}`}
                style={{ "--mark": item.fill } as React.CSSProperties}
              />
              {item.label}
            </span>
          ))}
        </div>
      </Figure>
      <div className="vee-columns">
        <Figure
          title="Interval by sample size"
          summary="Synthetic 90 percent bootstrap intervals for three sample sizes."
          synthetic={method.label}
          columns={["Sample", "Lower", "Estimate", "Upper"]}
          rows={sizes.map(({ row }) => row)}
          onDetail={open}
          marks={() => ({
            height: 255,
            marginLeft: 57,
            x: { label: "Companies", domain: sizes.map(({ label }) => label) },
            y: { label: "Series A incidence", tickFormat: percent, grid: true, domain: [0, 0.7] },
            marks: [
              Plot.ruleX(sizes, {
                x: "label",
                y1: "lower",
                y2: "upper",
                strokeWidth: 3,
                stroke: "#6b21a8",
                title: ({ row }) => titleFor(row),
              }),
              Plot.dot(sizes, {
                x: "label",
                y: "value",
                fill: "#6b21a8",
                stroke: "#fff",
                r: 5,
                title: ({ row }) => titleFor(row),
              }),
            ],
          })}
        >
          {referenceCount !== sizes[0].n && (
            <p className="vee-note">“Today” uses a fixed illustration of {sizes[0].n} companies.</p>
          )}
        </Figure>
        <Figure
          title="Held-out calibration"
          summary="Synthetic estimates compared with synthetic observed incidence in held-out groups."
          synthetic={method.label}
          columns={["Group", "Estimated", "Observed", "Held-out cases"]}
          rows={calibration.map(({ row }) => row)}
          onDetail={open}
          marks={() => ({
            height: 255,
            marginLeft: 56,
            x: {
              label: "Estimated incidence",
              domain: [0, 1],
              tickFormat: percent,
              grid: true,
              ticks: 4,
            },
            y: {
              label: "Held-out incidence",
              domain: [0, 1],
              tickFormat: percent,
              grid: true,
              ticks: 4,
            },
            marks: [
              Plot.line(
                [
                  { x: 0, y: 0 },
                  { x: 1, y: 1 },
                ],
                { x: "x", y: "y", strokeDasharray: "5 4", stroke: "#64748b" },
              ),
              Plot.dot(calibration, {
                x: "estimate",
                y: "observed",
                fill: "#6b21a8",
                stroke: "#fff",
                r: 6,
                title: ({ row }) => titleFor(row),
              }),
            ],
          })}
        />
      </div>
    </>
  );
}
