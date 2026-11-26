import { precedents, type Category, type Venture } from "./rookie-model";

import { ventureTokens } from "./venture-text.ts";

function startingText(venture: Venture) {
  // The first row is a dossier starting record, not a verified as-of snapshot.
  return [venture.focus, venture.events[0]?.title, venture.events[0]?.description].join(" ");
}

const documents = [...precedents.values()].map((venture) => ({
  venture,
  words: ventureTokens(startingText(venture)),
}));

const documentFrequency = new Map<string, number>();
for (const { words } of documents) {
  for (const word of new Set(words)) {
    documentFrequency.set(word, (documentFrequency.get(word) ?? 0) + 1);
  }
}

function vector(words: string[]) {
  const weights = new Map<string, number>();
  for (const word of words) {
    if (documentFrequency.has(word)) weights.set(word, (weights.get(word) ?? 0) + 1);
  }
  let squaredNorm = 0;
  for (const [word, frequency] of weights) {
    const idf = 1 + Math.log((documents.length + 1) / (documentFrequency.get(word)! + 1));
    const weight = (1 + Math.log(frequency)) * idf;
    weights.set(word, weight);
    squaredNorm += weight ** 2;
  }
  const norm = Math.sqrt(squaredNorm);
  for (const [word, weight] of weights) weights.set(word, weight / norm);
  return weights;
}

const corpus = documents.map(({ venture, words }) => ({ venture, weights: vector(words) }));

export function rankPrecedents(query: string, category: Category) {
  const weights = vector(ventureTokens(query));
  return corpus
    .filter(({ venture }) => venture.category === category)
    .map(({ venture, weights: candidate }) => {
      const terms = [...weights.entries()]
        .map(([word, weight]) => ({ word, contribution: weight * (candidate.get(word) ?? 0) }))
        .filter(({ contribution }) => contribution > 0)
        .sort(
          (left, right) =>
            right.contribution - left.contribution || left.word.localeCompare(right.word),
        );
      return {
        venture,
        similarity: Math.min(
          1,
          terms.reduce((total, term) => total + term.contribution, 0),
        ),
        matches: terms.slice(0, 5).map(({ word }) => word),
      };
    })
    .filter(({ similarity }) => similarity > 0)
    .sort(
      (left, right) =>
        right.similarity - left.similarity || left.venture.id.localeCompare(right.venture.id),
    );
}
