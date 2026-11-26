import { ventureTokens } from "./venture-text.ts";

export const evidenceClasses = {
  funding: "Funding or programme support",
  transaction: "Ownership or public-market transaction",
  setback: "Setback or restructuring",
  milestone: "Product or operating milestone",
} as const;

export type EvidenceClass = keyof typeof evidenceClasses;
type Example = { text: string; label: EvidenceClass };

export function trainEvidenceClassifier(examples: Example[]) {
  const labels = new Map<
    EvidenceClass,
    { documents: number; words: Map<string, number>; total: number }
  >();
  const vocabulary = new Set<string>();
  for (const { label, text } of examples) {
    const stats = labels.get(label) ?? { documents: 0, words: new Map(), total: 0 };
    stats.documents += 1;
    for (const term of ventureTokens(text)) {
      vocabulary.add(term);
      stats.total += 1;
      stats.words.set(term, (stats.words.get(term) ?? 0) + 1);
    }
    labels.set(label, stats);
  }

  return (text: string) => {
    const words = ventureTokens(text).filter((word) => vocabulary.has(word));
    if (new Set(words).size < 2) return undefined;
    const scores = [...labels].map(([label, stats]) => {
      const normalizer = stats.total + vocabulary.size;
      const score = words.reduce(
        (total, word) => total + Math.log(((stats.words.get(word) ?? 0) + 1) / normalizer),
        Math.log(stats.documents / examples.length),
      );
      return { label, score };
    });
    scores.sort((left, right) => right.score - left.score || left.label.localeCompare(right.label));
    return scores[0]?.label;
  };
}
