import type {
  AnalyticsCohort as Cohort,
  AnalyticsCompany as Company,
  AnalyticsHistory as CompanyDetail,
  AnalyticsMethod as Method,
  AnalyticsPeer as Peer,
  AnalyticsProfile as Profile,
  AnalyticsRobustness as Robustness,
  AnalyticsScenario as Scenario,
  BacktestSource,
  ScorerInput as Scorer,
} from "../api-schema";

export type { Cohort, Company, CompanyDetail, Method, Peer, Profile, Robustness, Scenario, Scorer };
export type ProfileOverview = Omit<Profile, "presets" | "scorer">;
export type Value = string | number;
export type Snapshot = Record<string, Value>;
export type RoleMap = Record<string, string[]>;
export type Fact = {
  name: string;
  value: Value;
  source: BacktestSource;
  review_state: string;
  second_reading_matched?: boolean;
  reviewed_by?: string | null;
  reviewed_on?: string | null;
};

export const STATIC = import.meta.env.MODE === "static";

export function resourceURL(path: string) {
  return STATIC ? `${import.meta.env.BASE_URL}analytics-data${path}.json` : `/api${path}`;
}
export function profileEvidence(profile: ProfileOverview) {
  const reviews = new Map(
    profile.reveal.evidence_reviews.map((review) => [
      review.company_id + ":" + review.field,
      review,
    ]),
  );
  const reviewed = (id: string, facts: Fact[]) =>
    facts.map((fact) => ({
      ...fact,
      ...reviews.get(id + ":" + fact.name),
    }));
  return {
    subjectFacts: reviewed(profile.company_id, profile.fields),
    peerFacts: Object.fromEntries(
      Object.entries(profile.peer_facts).map(([id, facts]) => [id, reviewed(id, facts)]),
    ),
  };
}
export function formatDate(value: string) {
  const date = new Date(value.length === 7 ? value + "-01" : value);
  if (!Number.isFinite(date.getTime())) return value;
  return date.toLocaleDateString("en-NZ", {
    day: value.length > 7 ? "numeric" : undefined,
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}
export function today() {
  const local = new Date();
  return [
    local.getFullYear(),
    String(local.getMonth() + 1).padStart(2, "0"),
    String(local.getDate()).padStart(2, "0"),
  ].join("-");
}
export function textValue(value: Value) {
  return typeof value === "string" ? value.replaceAll("_", " ") : String(value);
}
const vocabularyLabels: Record<string, string> = {
  food_beverage: "Food and beverage",
  household: "Households",
  individual: "Individuals",
  saas: "SaaS",
  new_zealand: "New Zealand",
  australia_new_zealand: "Australia and New Zealand",
  "lt0.5m": "Below NZ$0.5m",
  "0.5m_to_lt2m": "NZ$0.5m to under NZ$2m",
  "2m_to_lt5m": "NZ$2m to under NZ$5m",
  "5m_to_lt10m": "NZ$5m to under NZ$10m",
  gte10m: "NZ$10m or more",
};
export function vocabularyLabel(value: Value) {
  const label = textValue(value);
  return vocabularyLabels[String(value)] ?? label.charAt(0).toUpperCase() + label.slice(1);
}

export const fieldNames: Record<string, string> = {
  description: "Offering",
  product_type: "Product",
  buyer: "Buyer",
  business_model: "Business model",
  sector_normalised: "Sector",
  market_focus: "Market",
  prototype: "Prototype",
  paid_pilot_or_revenue: "Paid pilot or revenue",
  full_time_team: "Full-time team",
  round_size_band: "Round size",
  lead_investor_type: "Lead investor",
  months_since_founding: "Company age",
};
export const reviewNames: Record<string, string> = {
  ai_adjudicated: "AI-checked",
  confirmed: "Human-confirmed",
  proposed: "Unsure",
  rejected: "Rejected",
  disputed: "Rejected",
  missing: "Missing",
  dated_source: "Dated source",
  source_recorded: "Recorded source",
};
export const bars: Record<string, string> = {
  similarity: "Overall similarity",
  product_customer: "Product and customer",
  coverage: "Shared evidence",
  subject_fields: "Subject facts",
  peer_fields: "Peer facts",
  no_shared_evidence: "No shared evidence",
};
export function scoreValue(value: number | null) {
  return value == null ? "—" : value.toFixed(3);
}
export function scoreBand(peer: Peer) {
  return !peer.qualifies ? "not a comp" : (peer.similarity ?? 0) >= 0.6 ? "close" : "loose";
}
export function uiOrder(peers: Peer[]) {
  return [...peers].sort(
    (a, b) =>
      (b.product_customer ?? -1) - (a.product_customer ?? -1) ||
      (b.similarity ?? -1) - (a.similarity ?? -1),
  );
}
export function samePeerRank(a: Peer, b: Peer) {
  return (
    a.product_customer?.toFixed(12) === b.product_customer?.toFixed(12) &&
    a.similarity?.toFixed(12) === b.similarity?.toFixed(12)
  );
}
export function rankablePeers(peers: Peer[], covered: ReadonlySet<string>) {
  return uiOrder(
    peers.filter(
      (peer) =>
        covered.has(peer.company_id) && peer.similarity != null && peer.product_customer != null,
    ),
  );
}
export function statusAt(
  company: CompanyDetail,
  asof: string,
  auditDate: string,
): [string, string | null] {
  if (asof >= auditDate) return [company.status, company.outcome_event_id];
  const found = [...company.status_clock].reverse().find(([date]) => date <= asof);
  return found ? [found[1], found[2]] : ["unknown", null];
}
