import { useEffect, useId, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import * as Plot from "@observablehq/plot";
import { patternMarker } from "./encoding";

export type Detail = { heading: string; hint?: string; content: ReactNode };
export type Row = {
  key: string;
  values: (string | number)[];
  detail?: Detail;
};
type FigureProps = {
  title: string;
  summary: string;
  columns: string[];
  rows: Row[];
  markRows?: Row[];
  marks: (width: number) => Plot.PlotOptions;
  onDetail: (detail: Detail) => void;
  synthetic?: string;
  reserve?: boolean;
  defer?: boolean;
  placeholderHeight?: number;
  plotScrollLabel?: string;
  children?: ReactNode;
};

export function titleFor(row: Row) {
  return [row.values.join(" · "), row.detail?.hint, "Open details"].filter(Boolean).join(" · ");
}

function addPattern(svg: SVGSVGElement, id: string) {
  const ns = svg.namespaceURI;
  const defs = document.createElementNS(ns, "defs");
  const pattern = document.createElementNS(ns, "pattern");
  const base = document.createElementNS(ns, "rect");
  const stripe = document.createElementNS(ns, "path");
  for (const [key, value] of Object.entries({
    id,
    width: "6",
    height: "6",
    patternUnits: "userSpaceOnUse",
  }))
    pattern.setAttribute(key, value);
  base.setAttribute("width", "6");
  base.setAttribute("height", "6");
  base.setAttribute("fill", "#e2e8f0");
  stripe.setAttribute("d", "M-1,1L1,-1M0,6L6,0M5,7L7,5");
  stripe.setAttribute("stroke", "#64748b");
  stripe.setAttribute("stroke-width", "1");
  pattern.append(base, stripe);
  defs.append(pattern);
  svg.prepend(defs);
  for (const element of svg.querySelectorAll(`[fill="${patternMarker}"]`))
    element.setAttribute("fill", `url(#${id})`);
}

export function Figure({
  title,
  summary,
  columns,
  rows,
  markRows = rows,
  marks,
  onDetail,
  synthetic,
  reserve = false,
  defer = false,
  placeholderHeight,
  plotScrollLabel,
  children,
}: FigureProps) {
  const id = useId();
  const [table, setTable] = useState(false);
  const [near, setNear] = useState(false);
  const host = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!defer || near || table || !host.current) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setNear(true);
      },
      { rootMargin: "120px" },
    );
    observer.observe(host.current);
    return () => observer.disconnect();
  }, [defer, near, table]);

  useLayoutEffect(() => {
    const container = host.current;
    if (!container || table || !rows.length || (defer && !near)) return;
    const lookup = new Map(markRows.map((row) => [titleFor(row), row]));
    let previousWidth = 0;
    const render = () => {
      const width = Math.max(220, Math.floor(container.getBoundingClientRect().width));
      if (width === previousWidth) return;
      previousWidth = width;
      const svg = Plot.plot({
        width,
        marginRight: 19,
        marginBottom: 43,
        marginTop: 16,
        style: {
          fontFamily: "inherit",
          fontSize: "11px",
          color: "#465774",
          background: "transparent",
        },
        ...marks(width),
        ...(reserve ? { height: Math.round(container.getBoundingClientRect().height) } : {}),
      }) as SVGSVGElement;
      svg.setAttribute("role", "group");
      svg.setAttribute("aria-label", summary);
      svg.querySelector("style")?.remove();
      for (const group of svg.querySelectorAll("g[aria-label]:not([role])"))
        group.setAttribute("role", "group");
      addPattern(svg, "hatch-" + id.replace(/[^a-z0-9]/gi, ""));
      for (const label of svg.querySelectorAll("title")) {
        const row = lookup.get(label.textContent ?? "");
        const mark = label.parentElement;
        if (!row || !mark || !row.detail) continue;
        mark.setAttribute("tabindex", "0");
        mark.setAttribute("role", "button");
        mark.setAttribute("aria-label", titleFor(row));
        const open = () => {
          if (row.detail) onDetail(row.detail);
        };
        mark.addEventListener("click", open);
        mark.addEventListener("keydown", (event) => {
          const { key } = event as KeyboardEvent;
          if (key === "Enter" || key === " ") {
            event.preventDefault();
            open();
          }
        });
      }
      container.replaceChildren(svg);
    };
    render();
    const observer = new ResizeObserver(render);
    observer.observe(container);
    return () => observer.disconnect();
  }, [table, marks, rows, markRows, summary, onDetail, id, defer, near, reserve]);

  return (
    <figure className={`vee-figure${synthetic ? " vee-synthetic" : ""}`} aria-label={summary}>
      <div className="vee-figure-heading">
        <figcaption>{title}</figcaption>
        <button
          type="button"
          className="vee-table-toggle"
          aria-expanded={table}
          aria-controls={id}
          onClick={() => setTable(!table)}
        >
          {table ? "View as chart" : "View as table"}
        </button>
      </div>
      {synthetic && <div className="vee-synthetic-label">{synthetic}</div>}
      {children}
      {!rows.length && <p className="vee-empty">No matching records.</p>}
      <div
        id={id}
        className={
          table ? "vee-table-scroll" : plotScrollLabel ? "vee-plot vee-plot-scroll" : "vee-plot"
        }
        role={!table && plotScrollLabel ? "region" : undefined}
        aria-label={!table ? plotScrollLabel : undefined}
        tabIndex={table || plotScrollLabel ? 0 : undefined}
      >
        {table ? (
          <table>
            <caption className="sr-only">{title}</caption>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column} scope="col">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.key}>
                  {row.values.map((value, i) =>
                    i === 0 ? (
                      <th key={i} scope="row">
                        {row.detail ? (
                          <button type="button" onClick={() => onDetail(row.detail!)}>
                            {value}
                          </button>
                        ) : (
                          value
                        )}
                      </th>
                    ) : (
                      <td key={i}>{value}</td>
                    ),
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div
            ref={host}
            className={reserve ? "vee-plot-frame" : undefined}
            style={
              rows.length && placeholderHeight ? { minBlockSize: placeholderHeight } : undefined
            }
          />
        )}
      </div>
    </figure>
  );
}
