/** API models are generated from backend OpenAPI by scripts/export_contract.py. */
export type { Venture, VentureSummary, VenturePage, Facets, Comparison, Award, Connection } from "./api-schema";
import type { Observation } from "./api-schema";
/** Shared source presentation accepts observation or award evidence. */
export type Evidence = Partial<Pick<Observation, "observation_id" | "field" | "value_text" | "assertion_type" | "effective_at" | "date_basis" | "effective_review_status" | "superseded" | "relations" | "financial_value" | "event_value" | "effective_date" | "announcement_date">> & Omit<Observation, "observation_id" | "field" | "value_text" | "assertion_type" | "effective_at" | "date_basis" | "effective_review_status" | "superseded" | "relations" | "financial_value" | "event_value" | "effective_date" | "announcement_date"> & {award_id?: string};
