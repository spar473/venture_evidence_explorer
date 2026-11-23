export const patterns = { unknown: "unknown" } as const;

export const eventStyles = {
  series: { fill: "#1e3a8a", stroke: "#1e3a8a", symbol: "circle", label: "Series A or B" },
  other: { fill: "#93c5fd", stroke: "#2858a5", symbol: "circle", label: "Other round" },
  closure: { fill: "#ea580c", stroke: "#9a3412", symbol: "diamond", label: "Closure" },
  removal: { fill: "#ffffff", stroke: "#c2410c", symbol: "diamond", label: "Register removal" },
  active: { fill: "#ffffff", stroke: "#64748b", symbol: "circle", label: "Last seen active" },
  unknown: { fill: "#e2e8f0", stroke: "#64748b", symbol: "square", label: "Unknown" },
  exit: { fill: "#d8b4fe", stroke: "#6b21a8", symbol: "triangle", label: "Exit" },
} as const;

export type EventStyle = keyof typeof eventStyles;
export const eventLabels: Record<string, string> = {
  seed: "First round",
  series_a: "Series A",
  series_a_equivalent: "Series A equivalent",
  series_b: "Series B",
  series_c_plus: "Series C or later",
  other_financing: "Other financing",
  grant: "Grant",
  pre_series_a: "Pre-Series A",
  convertible_note: "Convertible note",
  seed_extension: "Seed extension",
  closed_liquidation: "Liquidation",
  closed_register_removal: "Register removal",
  closed_founder_announcement: "Closure announcement",
  last_verified_activity: "Last seen active",
  voluntary_administration: "Voluntary administration",
  acquired: "Acquisition",
  ipo: "IPO",
};
export function eventStyle(kind: string): EventStyle {
  if (kind === "closed_register_removal") return "removal";
  if (kind.startsWith("closed_")) return "closure";
  if (kind.startsWith("series_")) return "series";
  if (kind === "last_verified_activity") return "active";
  if (kind === "acquired" || kind === "ipo") return "exit";
  if (kind === "unknown" || kind === "voluntary_administration") return "unknown";
  return "other";
}
export const statuses: Record<string, { label: string; style: EventStyle }> = {
  reached_outcome: { label: "Series A or later", style: "series" },
  closed_before_outcome: { label: "Closed", style: "closure" },
  acquired_or_ipo_before_outcome: { label: "Exit", style: "exit" },
  observed_no_outcome: { label: "Last seen active", style: "active" },
  lost_to_follow_up: { label: "Lost to follow-up", style: "unknown" },
  unknown: { label: "Unknown", style: "unknown" },
};

export const reviewFill: Record<string, string> = {
  ai_adjudicated: "#547dd9",
  confirmed: "#0e766e",
  proposed: "#f2c279",
  rejected: "#f0a095",
  disputed: "#f0a095",
  missing: "#e2e8f0",
};

export const patternMarker = "url(#vee-hatch)";
