import * as Plot from "@observablehq/plot";
import { eventStyles, patternMarker, reviewFill, statuses } from "./encoding";
import { Figure, titleFor, type Row } from "./figure";
import { badge, eventDetail, FactDetails, Source, useDetail } from "../analytics-views/details";
import {
  fieldNames,
  formatDate,
  reviewNames,
  type Company,
  type CompanyDetail,
} from "../analytics-views/data";

export type ObservedCompany = {
  company: Company;
  info: CompanyDetail;
  status: string;
  eventId: string | null;
};

export function CohortStack({
  companies,
  bySector = false,
}: {
  companies: ObservedCompany[];
  bySector?: boolean;
}) {
  const open = useDetail();
  const byGroup = (row: ObservedCompany) =>
    bySector ? row.company.sector_group : String(row.company.year);
  const groups = bySector
    ? ["Healthtech", "Other sectors"]
    : [...new Set(companies.map(byGroup))].sort();
  const data = groups.flatMap((group) => {
    let start = 0;
    return Object.entries(statuses).flatMap(([status, { label, style }]) => {
      const members = companies.filter(
        (company) => byGroup(company) === group && company.status === status,
      );
      if (!members.length) return [];
      const low = start;
      start += members.length;
      const row: Row = {
        key: group + status,
        values: [group, label, members.length],
        detail: {
          heading: `${group} · ${label}`,
          content: (
            <ul className="vee-link-list">
              {members.map(({ company, info, eventId }) => {
                const event =
                  info.events.find((item) => item.event_id === eventId) ?? company.entry;
                return (
                  <li key={company.company_id}>
                    <button type="button" onClick={() => open(eventDetail(company.name, event))}>
                      {company.name} · {formatDate(event.date.value ?? "")}
                    </button>
                  </li>
                );
              })}
            </ul>
          ),
        },
      };
      return [{ group, status, row, style, low, high: start, count: members.length }];
    });
  });
  return (
    <Figure
      title={bySector ? "Healthtech and other sectors" : "36-month outcomes by vintage"}
      summary={
        bySector
          ? "Company counts by sector and 36-month outcome."
          : "Company counts by entry year and 36-month primary outcome."
      }
      columns={[bySector ? "Sector" : "Vintage", "36-month status", "Companies"]}
      rows={data.map(({ row }) => row)}
      onDetail={open}
      marks={(width) => ({
        height: bySector ? 200 : 318,
        marginLeft: bySector ? 100 : 53,
        x: bySector
          ? { label: "Companies", grid: true, ticks: 6 }
          : {
              label: "Entry year",
              domain: groups,
              tickFormat: (year) => (width < 500 ? String(year).slice(2) : year),
            },
        y: bySector
          ? { label: null, domain: groups }
          : { label: "Companies", grid: true, ticks: 5 },
        marks: bySector
          ? [Plot.barX(data, { y: "group", x1: "low", x2: "high", ...stackStyle })]
          : [Plot.barY(data, { x: "group", y1: "low", y2: "high", ...stackStyle })],
      })}
    >
      {bySector ? (
        <p className="vee-note">Small groups. Use these counts to inspect evidence.</p>
      ) : (
        <div className="vee-legend">
          {Object.entries(statuses).map(([id, { label, style }]) => (
            <span key={id}>
              <i
                className={`vee-swatch ${style} ${id}`}
                style={
                  {
                    "--mark": eventStyles[style].fill,
                    "--stroke": eventStyles[style].stroke,
                  } as React.CSSProperties
                }
              />
              {label}
            </span>
          ))}
        </div>
      )}
    </Figure>
  );
}

const stackStyle = {
  fill: ({ style }: { style: keyof typeof eventStyles }) =>
    style === "unknown" ? patternMarker : eventStyles[style].fill,
  stroke: ({ style }: { style: keyof typeof eventStyles }) =>
    style === "active" ? "#64748b" : "#fff",
  strokeWidth: 1,
  opacity: ({ status }: { status: string }) => (status === "lost_to_follow_up" ? 0.66 : 1),
  title: ({ row }: { row: Row }) => titleFor(row),
  inset: 0.5,
};

const fieldShort: Record<string, string> = {
  description: "Off",
  product_type: "Prd",
  buyer: "Buy",
  business_model: "Biz",
  sector_normalised: "Sec",
  market_focus: "Mkt",
  prototype: "Pro",
  paid_pilot_or_revenue: "Rev",
  full_time_team: "FT",
  round_size_band: "Rnd",
  lead_investor_type: "Inv",
  months_since_founding: "Age",
};

export function Heatmap({
  companies,
  fields,
  asof,
}: {
  companies: ObservedCompany[];
  fields: string[];
  asof: string;
}) {
  const open = useDetail();
  const data = companies.flatMap(({ company, info }) =>
    fields.map((field) => {
      const recorded = info.fields[field];
      const fact =
        recorded?.source.available_on <= asof &&
        (!recorded.reviewed_on || recorded.reviewed_on <= asof)
          ? recorded
          : undefined;
      const state = fact?.review_state ?? "missing";
      const label = reviewNames[state];
      const heading = `${company.name} · ${fieldNames[field]}`;
      const row: Row = {
        key: company.company_id + ":" + field,
        values: [company.name, fieldNames[field], label],
        detail: {
          heading,
          hint: fact ? `${badge(fact)} · ${fact.source.publisher}` : "Missing",
          content:
            fact && ["rejected", "disputed"].includes(fact.review_state) ? (
              <Source source={fact.source} review={badge(fact)} />
            ) : fact ? (
              <FactDetails facts={[fact]} />
            ) : (
              <p>No dated field evidence in this snapshot.</p>
            ),
        },
      };
      return { company: company.name, field, state, row };
    }),
  );
  return (
    <Figure
      title="Evidence heatmap"
      summary="Each row is a company. Each of twelve columns shows the review status of one evidence field."
      columns={["Company", "Field", "Review"]}
      rows={data.map(({ row }) => row)}
      onDetail={open}
      marks={(width) => ({
        height: Math.max(152, companies.length * 24 + 55),
        marginLeft: width < 500 ? 98 : 165,
        x: {
          label: null,
          domain: fields,
          axis: "top",
          tickFormat: (field) => fieldShort[String(field)],
        },
        y: {
          label: null,
          domain: companies.map(({ company }) => company.name),
          tickFormat: (name) => (width < 500 ? String(name).slice(0, 14) : name),
        },
        marks: [
          Plot.cell(data, {
            x: "field",
            y: "company",
            fill: ({ state }) => reviewFill[state],
            title: ({ row }) => titleFor(row),
            inset: 1.2,
          }),
        ],
      })}
    >
      <div className="vee-legend">
        {["ai_adjudicated", "confirmed", "proposed", "rejected", "missing"].map((state) => (
          <span key={state}>
            <i
              className="vee-swatch"
              style={{ "--mark": reviewFill[state] } as React.CSSProperties}
            />
            {reviewNames[state]}
          </span>
        ))}
      </div>
    </Figure>
  );
}
