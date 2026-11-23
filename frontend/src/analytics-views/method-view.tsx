import { MethodFigures } from "../charts/labs";
import { useAnalytics } from "./shell";
import { formatDate, type Cohort, type Method } from "./data";

export function MethodLab({ cohort }: { cohort: Cohort }) {
  const figures = useAnalytics<Method>("/views/method");
  const { gates } = cohort;
  const minEntries = gates.minimum_entries ?? 150;
  const minEvents = gates.minimum_events ?? 30;
  const maxUnknown = Math.max(0, Math.floor((gates.entries - 1) / 4));
  const metrics = [
    {
      label: "Confirmed companies",
      value: gates.entries,
      max: minEntries,
      goal: `${gates.entries} of ${minEntries}`,
      passed: gates.entries >= minEntries,
    },
    {
      label: "Verified Series A outcomes",
      value: gates.primary.events,
      max: minEvents,
      goal: `${gates.primary.events} of ${minEvents}`,
      passed: gates.primary.events >= minEvents,
    },
    {
      label: "Unknown or lost",
      value: gates.primary.unknown_or_lost,
      max: Math.max(1, gates.entries),
      goal: `${gates.primary.unknown_or_lost} of ${gates.entries} · maximum ${maxUnknown}`,
      passed: gates.entries > 0 && gates.primary.unknown_or_lost <= maxUnknown,
    },
  ];
  return (
    <>
      <div className="vee-method-hero">
        <section className="vee-panel vee-gates">
          <div className="vee-section-heading">
            <h2>Real evidence gate</h2>
            <span className="vee-tag">{gates.primary.gate_ready ? "Met" : "Locked"}</span>
          </div>
          <p className="vee-note">Cohort audit · {formatDate(cohort.audit_date)}</p>
          {metrics.map((metric, i) => (
            <div className="vee-gate" key={metric.label}>
              <label htmlFor={`vee-gate-${i}`}>{metric.label}</label>
              <strong>{metric.goal}</strong>
              <meter
                className={metric.passed ? "met" : ""}
                id={`vee-gate-${i}`}
                min={0}
                max={metric.max}
                value={Math.min(metric.value, metric.max)}
              />
            </div>
          ))}
        </section>
        <section className="vee-method-figures" aria-label="Synthetic charts">
          {figures?.error && <p role="alert">{figures.error}</p>}
          {!figures?.data && !figures?.error && <p role="status">Loading synthetic figures…</p>}
          {figures?.data && <MethodFigures method={figures.data} referenceCount={gates.entries} />}
        </section>
      </div>
    </>
  );
}
