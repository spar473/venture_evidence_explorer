import { useState } from "react";
import type { WorkbenchClaim, WorkbenchPoint } from "./api-schema";
import { dateLabel, fieldLabel } from "./workbench-shared";

const month = 365.25 / 12;
type TimelineRow = {
  company_id: string;
  display_name: string;
  points: WorkbenchPoint[];
  notes?: Record<string, string>;
};

export function Trajectory({
  rows,
  onClaim,
  title,
}: {
  rows: TimelineRow[];
  onClaim: (claim: WorkbenchClaim) => void;
  title: string;
}) {
  const [table, setTable] = useState(false);
  const [hover, setHover] = useState<{ company: string; claim: WorkbenchClaim } | null>(null);
  const points = rows.flatMap((row) => row.points);
  if (!points.length) return <p>No dated events can be aligned for this selection.</p>;
  const lower = Math.min(0, ...points.map((point) => point.lower_days));
  const upper = Math.max(36 * month, ...points.map((point) => point.upper_days));
  const farTick = Math.floor(upper / (12 * month)) * 12;
  const ticks = farTick > 36 ? [0, 12, 24, 36, farTick] : [0, 12, 24, 36];
  const width = 900,
    left = 185,
    gap = 43,
    top = 45;
  const height = top + rows.length * gap + 45;
  const x = (days: number) => left + ((days - lower) / (upper - lower)) * (width - left - 48);
  return (
    <figure
      className="wb-timeline"
      aria-label={`${title}, ${rows.length} ${rows.length === 1 ? "company" : "companies"} and ${points.length} dated marks`}
    >
      <div className="wb-toolbar">
        <figcaption>
          {rows.length} {rows.length === 1 ? "company" : "companies"} · 36-month window shaded
        </figcaption>
        <button
          type="button"
          aria-pressed={table}
          onClick={() => {
            setTable(!table);
            setHover(null);
          }}
        >
          {table ? "View as chart" : "View as table"}
        </button>
      </div>
      {table ? (
        <div className="wb-table-scroll">
          <table className="wb-table">
            <thead>
              <tr>
                <th scope="col">Company</th>
                <th scope="col">Event</th>
                <th scope="col">Date</th>
                <th scope="col">Source</th>
              </tr>
            </thead>
            <tbody>
              {rows.flatMap((row) =>
                row.points.map((point) => (
                  <tr key={row.company_id + point.claim.claim_id}>
                    <th scope="row">{row.display_name}</th>
                    <td>
                      <button onClick={() => onClaim(point.claim)}>
                        {fieldLabel(point.claim.field)}
                      </button>
                      {row.notes?.[point.claim.claim_id] && (
                        <small>{row.notes[point.claim.claim_id]}</small>
                      )}
                    </td>
                    <td>{dateLabel(point.claim)}</td>
                    <td>{point.claim.publisher}</td>
                  </tr>
                )),
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="wb-chart-scroll">
          <svg viewBox={`0 0 ${width} ${height}`} aria-label={title}>
            <rect
              x={x(0)}
              y={18}
              width={x(36 * month) - x(0)}
              height={height - 58}
              fill="#edf3fd"
            />
            {ticks.map((value) => (
              <g key={value}>
                <line
                  x1={x(value * month)}
                  x2={x(value * month)}
                  y1={18}
                  y2={height - 38}
                  stroke="#b7c8e4"
                  strokeDasharray={value ? "4 4" : undefined}
                />
                <text x={x(value * month)} y={height - 15} textAnchor="middle" className="wb-axis">
                  {value} mo
                </text>
              </g>
            ))}
            {rows.map((row, index) => {
              const y = top + index * gap;
              const notes = [...new Set(Object.values(row.notes ?? {}))];
              return (
                <g key={row.company_id}>
                  <text x={left - 10} y={y + 4} textAnchor="end" className="wb-axis">
                    <title>{row.display_name}</title>
                    {row.display_name.length > 24
                      ? row.display_name.slice(0, 22) + "…"
                      : row.display_name}
                  </text>
                  <line x1={x(lower)} x2={x(upper)} y1={y} y2={y} stroke="#c2cbda" />
                  {notes.length > 0 && (
                    <text x={left + 5} y={y + 18} className="wb-axis">
                      {notes.join(" · ")}
                    </text>
                  )}
                  {row.points.map((point) => {
                    const claim = point.claim;
                    const caption = `${row.display_name}, ${fieldLabel(claim.field)}, ${dateLabel(claim)}, ${claim.publisher}${row.notes?.[claim.claim_id] ? `, ${row.notes[claim.claim_id]}` : ""}`;
                    const interval = point.upper_days !== point.lower_days;
                    const uncertainAnchor = point.is_anchor && claim.lower_on !== claim.upper_on;
                    const center = x((point.lower_days + point.upper_days) / 2);
                    const markColor = claim.field.startsWith("closed_")
                      ? "#bd4f00"
                      : point.is_anchor
                        ? "#28446d"
                        : "#0072b2";
                    const show = () => setHover({ company: row.display_name, claim });
                    return (
                      <g
                        key={claim.claim_id}
                        role="button"
                        tabIndex={0}
                        aria-label={caption}
                        onMouseEnter={show}
                        onMouseLeave={() => setHover(null)}
                        onFocus={show}
                        onBlur={() => setHover(null)}
                        onClick={() => onClaim(claim)}
                        onKeyDown={(event) => {
                          if (event.key === "Enter" || event.key === " ") {
                            event.preventDefault();
                            onClaim(claim);
                          }
                        }}
                      >
                        <title>{caption}</title>
                        <rect
                          x={center - 18}
                          y={y - 18}
                          width={36}
                          height={36}
                          fill="transparent"
                        />
                        {(interval || uncertainAnchor) && (
                          <rect
                            x={interval ? x(point.lower_days) : center - 9}
                            y={y - 8}
                            width={
                              interval ? Math.max(3, x(point.upper_days) - x(point.lower_days)) : 18
                            }
                            height={16}
                            fill={markColor}
                            fillOpacity={0.3}
                            rx={3}
                          />
                        )}
                        {claim.field.startsWith("closed_") ? (
                          <path
                            d={`M${center - 5} ${y - 5}l10 10m-10 0l10 -10`}
                            stroke={markColor}
                            strokeWidth={2.5}
                          />
                        ) : (
                          !interval && (
                            <circle
                              cx={center}
                              cy={y}
                              r={5}
                              fill={point.is_anchor ? "#fff" : markColor}
                              stroke={markColor}
                              strokeWidth={2}
                            />
                          )
                        )}
                      </g>
                    );
                  })}
                </g>
              );
            })}
          </svg>
        </div>
      )}
      <p className="wb-muted">
        Bands show date intervals. A band at month zero identifies a partial-date anchor.
      </p>
      {hover && !table && (
        <p role="status" className="wb-tooltip">
          {hover.company} · {fieldLabel(hover.claim.field)} · {dateLabel(hover.claim)} ·{" "}
          {hover.claim.publisher}
        </p>
      )}
    </figure>
  );
}
