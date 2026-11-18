export type Evidence = {
  observation_id?: string;
  award_id?: string;
  venture_id: string;
  field?: string;
  value_text?: string;
  source_id: string;
  source_title: string;
  url: string;
  publisher: string;
  published_at: string;
  retrieved_at: string;
  locator: string;
  review_status: string;
  assertion_type?: string;
  effective_at?: string | null;
  date_basis?: string;
  limitations: string;
};
export type Award = Evidence & {
  programme: string;
  award_year: number;
  award_label: string;
  event_date: string | null;
  place: number | null;
};
export type Connection = {
  connection_id: string;
  connection_type: string;
  institution: string;
  observation_id: string;
  evidence: Evidence;
};
export type Venture = {
  venture_id: string;
  display_name: string;
  aliases: string[];
  entity_type: string;
  legal_name: string | null;
  registration_id: string | null;
  current_operating_status: string | null;
  current_funding_stage: string | null;
  selection_bucket: string;
  identity_review_status: string;
  observations: Evidence[];
  awards: Award[];
  connections: Connection[];
  proposed_annotations: {
    annotation_id: string;
    field: string;
    value_text: string;
    review_status: string;
    basis_observation_ids: string[];
  }[];
};
export type Facets = {
  programmes: { programme: string; awards: number; ventures: number }[];
  years: number[];
  connection_types: {
    connection_type: string;
    recorded_connections: number;
    distinct_ventures: number;
  }[];
  counts: Record<string, number>;
};
export type Comparison = {
  method: {
    name: string;
    version: string;
    scoring: string;
    normalization: string;
    abstention: string;
    limitations: string;
  };
  mode: string;
  query: string;
  effective_query?: string;
  subject: Venture | null;
  results: {
    venture: Venture;
    ranking_score: number;
    query_token_coverage: number;
    matched_terms: string[];
    evidence: { observation: Evidence; matched_terms: string[] }[];
    wording_differences: {
      query_only_terms: string[];
      candidate_only_terms: string[];
      meaning: string;
    };
    unavailable_evidence: string[];
    brief: string;
  }[];
  abstention_reason: string | null;
  questions: string[];
  brief_type: string;
  annotations_used: boolean;
};
