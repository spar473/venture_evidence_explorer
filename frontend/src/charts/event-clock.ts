import type { BacktestEvent } from "../api-schema";
import type { Company } from "../analytics-views/data";
import type { EventTiming } from "./encoding";

export function eventLastDate(company: Company, event: BacktestEvent) {
  const entry = new Date(company.start + "T00:00:00Z");
  entry.setUTCDate(entry.getUTCDate() + event.upper_days);
  return entry.toISOString().slice(0, 10);
}

export function eventTiming(company: Company, event: BacktestEvent, asof: string): EventTiming {
  const occurredOn =
    event.event_id === company.entry.event_id ? company.start : eventLastDate(company, event);
  if (occurredOn > asof) return "hindsight";
  return event.source.available_on > asof ? "late_source" : "known";
}
