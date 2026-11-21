const labels: Record<string, string> = {
  velocity_100k: "Velocity $100K Challenge",
  velocity_ideas: "Velocity Ideas Challenge",
  uoa_programme_participation: "Programme participation",
  uoa_student_venture: "Student venture",
  uoa_staff_research_team: "Staff research team",
  uoa_research_origin: "Research origin",
  uoa_spinout: "Spinout",
  uoa_staff_alumni_founders: "Staff / alumni founders",
  product_description: "Product description",
  uoa_connection: "University connection",
  product_customer: "Product / customer",
  commercialisation: "Commercialisation pathway",
  stage_milestone: "Stage / milestone",
  source_checked_owner_review_pending: "Source checked; owner review pending",
  needs_owner_review: "Owner review pending",
  historical_description_at_publication: "Historical description at publication",
  relationship_reported_at_publication: "Relationship reported at publication",
  "100k_award": "Recorded $100K recognition",
  ideas_award: "Recorded Ideas recognition",
  uoa_origin: "University origin",
  programme_recognition: "Programme recognition",
  connection_coverage: "University connections",
  source_coverage: "Evidence coverage",
  programme: "Programme",
  award_year: "Year",
  recorded_awards: "Awards",
  distinct_ventures: "Ventures",
  connection_type: "Connection type",
  recorded_connections: "Relationships",
  venture_id: "Record ID",
  display_name: "Venture",
  source_count: "Sources",
  observation_count: "Observations",
  earliest_source_date: "First published",
  latest_source_date: "Last published",
  latest_retrieval_date: "Last retrieved",
  as_of_date: "As of (UTC)",
  latest_source_age_days: "Source age (days)",
  evidence_note: "Coverage note",
};
export const label = (s: string) => labels[s] || s.replaceAll("_", " ");
export const unknown = (s: string | null | undefined) => s || "Unknown / unverified";

/** Retain date precision: display a year/month without implying a day. */
export function dateLabel(
  raw: string | null | undefined,
  interval?: { precision: string; lower_bound?: string | null } | null,
) {
  if (interval?.precision === "unknown") return "Unknown / not recorded";
  if (interval?.lower_bound) {
    if (interval.precision === "year")
      return interval.lower_bound.slice(0, 4) + " (year precision)";
    if (interval.precision === "month")
      return interval.lower_bound.slice(0, 7) + " (month precision)";
    return interval.lower_bound;
  }
  return raw || "Unknown / not recorded";
}
