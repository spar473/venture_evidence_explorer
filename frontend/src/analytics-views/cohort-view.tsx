import { useState } from "react";
import { CohortStack, Heatmap, type ObservedCompany } from "../charts/cohort";
import { EventStrip } from "../charts/peers";
import { statuses } from "../charts/encoding";
import { formatDate, statusAt, type Cohort } from "./data";
import { KPI, matchesFilter, type Filters } from "./shell";

const PAGE_SIZE = 12;

function PageControl({
  page,
  setPage,
  total,
  label,
}: {
  page: number;
  setPage: (page: number) => void;
  total: number;
  label: string;
}) {
  return (
    <div className="vee-pager" role="group" aria-label={label}>
      <button type="button" disabled={page === 0} onClick={() => setPage(page - 1)}>
        Previous
      </button>
      <span>
        {total ? page * PAGE_SIZE + 1 : 0}–{Math.min(total, (page + 1) * PAGE_SIZE)} of {total}
      </span>
      <button
        type="button"
        disabled={(page + 1) * PAGE_SIZE >= total}
        onClick={() => setPage(page + 1)}
      >
        Next
      </button>
    </div>
  );
}

export function CohortExplorer({ cohort, filters }: { cohort: Cohort; filters: Filters }) {
  const [order, setOrder] = useState("vintage");
  const [heat, setHeat] = useState(0);
  const selected: ObservedCompany[] = cohort.companies
    .filter((company) => matchesFilter(company, filters) && company.end <= filters.asof)
    .map((company) => {
      const info = cohort.reveal[company.company_id];
      const [status, eventId] = statusAt(info, filters.asof, cohort.audit_date);
      return { company, info, status, eventId };
    });
  const vintageOrder = [...selected].sort(
    (a, b) =>
      a.company.start.localeCompare(b.company.start) ||
      a.company.name.localeCompare(b.company.name),
  );
  const ordered =
    order === "vintage"
      ? vintageOrder
      : [...vintageOrder].sort(
          (a, b) =>
            Object.keys(statuses).indexOf(a.status) - Object.keys(statuses).indexOf(b.status),
        );
  const lastPage = Math.max(0, Math.ceil(selected.length / PAGE_SIZE) - 1);
  const heatPage = Math.min(heat, lastPage);
  return (
    <>
      <KPI
        values={[
          {
            name: "Candidates reviewed",
            value: cohort.candidate_records,
            hint: "Full intake audit",
          },
          { name: "Confirmed entries", value: selected.length },
          {
            name: "Verified Series A within 36 months",
            value: selected.filter(({ status }) => status === "reached_outcome").length,
          },
          {
            name: "Status unknown",
            value: selected.filter(({ status }) => status === "unknown").length,
          },
        ]}
      />
      <div className="vee-columns vee-cohort-hero">
        <CohortStack companies={selected} />
        <CohortStack companies={selected} bySector />
      </div>
      <section aria-label="Company events">
        <div className="vee-section-toolbar">
          <label className="vee-sort">
            Sort by{" "}
            <select
              value={order}
              onChange={(event) => {
                setOrder(event.currentTarget.value);
              }}
            >
              <option value="vintage">Vintage</option>
              <option value="outcome">Outcome</option>
            </select>
          </label>
        </div>
        <EventStrip
          asof={filters.asof}
          scroll
          series={ordered.map(({ company, info }) => ({ company, events: info.events }))}
        />
      </section>
      <section aria-label="Review coverage">
        <div className="vee-section-toolbar">
          <p className="vee-note">Sources through {formatDate(cohort.audit_date)}.</p>
          <PageControl
            page={heatPage}
            setPage={setHeat}
            total={selected.length}
            label="Heatmap pages"
          />
        </div>
        <Heatmap
          companies={vintageOrder.slice(heatPage * PAGE_SIZE, (heatPage + 1) * PAGE_SIZE)}
          fields={cohort.fields}
          asof={filters.asof}
        />
      </section>
    </>
  );
}
