import type { Milestone } from "./rookie-model";

export const evidenceKinds = {
  equity: "Equity and investment",
  debt: "Debt and credit",
  support: "Grant and programme support",
  public: "Listing and public-market transaction",
  transaction: "Acquisition and asset transaction",
  setback: "Setback and restructuring",
  milestone: "Other milestone",
} as const;

export type EvidenceKind = keyof typeof evidenceKinds;
type Entry = { kind: EvidenceKind; status: string; amount?: string; scope?: string };

const register: Record<string, Entry> = {};
function add(kind: EvidenceKind, status: string, ids: string[]) {
  for (const id of ids) register[id] = { kind, status };
}
add("equity", "Investment reported", [
  "kami-2",
  "halter-1",
  "biolumic-1",
  "olive-ai-2",
  "mint-innovation-1",
]);
add("equity", "Investment announced", [
  "kami-3",
  "education-perfect-3",
  "carboncure-technologies-2",
  "twelve-2",
  "robotics-plus-1",
]);
add("transaction", "Transaction completed", [
  "volpara-health-technologies-3",
  "kheiron-medical-technologies-3",
  "icad-3",
  "edmodo-2",
  "instructure-3",
  "instructure-4",
  "coursera-4",
  "2u-2",
  "li-cycle-3",
  "northvolt-5",
  "robotics-plus-3",
  "benson-hill-2",
]);
add("transaction", "Transaction reported", ["byjus-think-learn-2", "agbiome-3", "agbiome-4"]);
add("transaction", "Transaction announced", ["agworld-3", "qlarity-imaging-2"]);
add("public", "Public-market event recorded", [
  "butterfly-network-3",
  "duolingo-3",
  "coursera-3",
  "lanzatech-3",
]);
add("support", "Support recorded", ["banqer-4", "twelve-1"]);
add("setback", "Constraint or disruption reported", [
  "kheiron-medical-technologies-2",
  "olive-ai-4",
  "edmodo-3",
  "edmodo-4",
  "edmodo-5",
  "byjus-think-learn-4",
  "li-cycle-2",
  "northvolt-4",
  "climeworks-4",
  "running-tide-3",
  "agbiome-2",
  "benson-hill-3",
  "plenty-3",
]);
add("setback", "Emergence from restructuring reported", ["2u-3", "plenty-4"]);

Object.assign(register, {
  "formus-labs-1": { kind: "equity", status: "Raise announced", amount: "US$5 million" },
  "viz-ai-3": { kind: "equity", status: "Series D reported", amount: "US$100 million" },
  "labster-3": {
    kind: "equity",
    status: "Funding tranche announced",
    amount: "$47 million as reported",
    scope: "The dossier does not specify currency.",
  },
  "byjus-think-learn-1": {
    kind: "equity",
    status: "Financing disclosed",
    scope:
      "Combined primary and secondary investment. The company’s cash proceeds are not established.",
  },
  "redwood-materials-2": {
    kind: "debt",
    status: "Conditional commitment",
    amount: "Up to US$2 billion",
    scope: "The loan was conditional. This record establishes a commitment.",
  },
  "redwood-materials-4": {
    kind: "equity",
    status: "Series E final close announced",
    amount: "US$425 million",
  },
  "carboncure-technologies-3": {
    kind: "equity",
    status: "Equity reported",
    amount: "US$80 million",
  },
  "twelve-4": {
    kind: "debt",
    status: "Credit facility announced",
    amount: "Up to $45 million as reported",
    scope: "Facility maximum. Draws and currency are not specified in this dossier.",
  },
  "halter-3": { kind: "equity", status: "Series D announced", amount: "NZ$165 million" },
  "halter-4": {
    kind: "equity",
    status: "Series E announced",
    amount: "NZ$377 million",
    scope: "Regional announcements report the same round in different currencies.",
  },
  "biolumic-2": { kind: "equity", status: "Series A reported", amount: "US$5 million" },
  "pivot-bio-3": { kind: "equity", status: "Series D close reported", amount: "US$430 million" },
  "indigo-ag-1": { kind: "equity", status: "Series C announced", amount: "US$100 million" },
  "plenty-1": { kind: "equity", status: "Series B reported", amount: "US$200 million" },
  "innerplant-1": { kind: "equity", status: "Series A announced", amount: "US$16 million" },
  "innerplant-2": { kind: "equity", status: "Series B announced", amount: "US$30 million" },
  "kami-4": {
    kind: "transaction",
    status: "Investor realisation disclosed",
    scope: "Applies to the reporting investor. The dossier does not state a company-wide return.",
  },
  "mint-innovation-4": {
    kind: "transaction",
    status: "Spinout announced",
    scope: "Linca was the recipient of the NZ$5 million seed first close.",
  },
  "byjus-think-learn-3": { kind: "transaction", status: "Proposed combination notified" },
  "olive-ai-3": { kind: "transaction", status: "Asset sale reported" },
  "benson-hill-4": {
    kind: "transaction",
    status: "Asset sale approved",
    scope: "Court approval. Verify closing separately.",
  },
} satisfies Record<string, Entry>);

export function eventEvidence(event: Milestone): Entry {
  return register[event.id] ?? { kind: "milestone", status: "Dossier observation" };
}

export function evidenceUrl(company: string) {
  return "?view=evidence&" + new URLSearchParams({ case: company }).toString();
}

export function trainingLabel(event: Milestone) {
  const { kind } = eventEvidence(event);
  if (kind === "equity" || kind === "debt" || kind === "support") return "funding";
  if (kind === "public" || kind === "transaction") return "transaction";
  if (kind === "setback") return "setback";
  return "milestone";
}
