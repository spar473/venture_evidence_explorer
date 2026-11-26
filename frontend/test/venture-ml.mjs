import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  evidenceClasses,
  trainEvidenceClassifier,
} from "../src/analytics-views/evidence-classifier.ts";
import { eventEvidence, trainingLabel } from "../src/analytics-views/venture-evidence.ts";

const ventures = JSON.parse(
  await readFile(new URL("../src/analytics-views/rookie-precedents.json", import.meta.url), "utf8"),
);
const examples = ventures.flatMap(({ id, events }) =>
  events.map((event) => ({
    venture: id,
    label: trainingLabel(event),
    text: event.description,
  })),
);
assert.equal(ventures.length, 40);
assert.equal(examples.length, 149);
assert.equal(trainEvidenceClassifier(examples)("zzzzz xxxxx"), undefined);
const linca = ventures.find(({ id }) => id === "mint-innovation").events.at(-1);
assert.equal(eventEvidence(linca).amount, undefined);
assert.match(eventEvidence(linca).scope, /Linca/);

const counts = Object.keys(evidenceClasses).map((label) => ({
  label,
  actual: 0,
  suggested: 0,
  correct: 0,
}));
let correct = 0;
let majorityCorrect = 0;
let abstained = 0;
for (const { id } of ventures) {
  const heldOut = examples.filter(({ venture }) => venture === id);
  const training = examples.filter(({ venture }) => venture !== id);
  const classify = trainEvidenceClassifier(training);
  const majority = [...counts].sort(
    (a, b) =>
      training.filter(({ label }) => label === b.label).length -
      training.filter(({ label }) => label === a.label).length,
  )[0].label;
  for (const { text, label } of heldOut) {
    const actual = counts.find((row) => row.label === label);
    const result = classify(text);
    const predicted = counts.find((row) => row.label === result);
    actual.actual++;
    if (predicted) predicted.suggested++;
    else abstained++;
    if (result === label) {
      correct++;
      actual.correct++;
    }
    if (label === majority) majorityCorrect++;
  }
}
const macroF1 =
  counts.reduce((sum, row) => sum + (2 * row.correct) / (row.actual + row.suggested), 0) /
  counts.length;
console.log(
  JSON.stringify(
    {
      examples: examples.length,
      ventures: ventures.length,
      correct,
      majorityCorrect,
      abstained,
      macroF1,
      counts,
    },
    null,
    2,
  ),
);
