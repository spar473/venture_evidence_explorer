# Comparing research workflows

Generate the development tasks and frozen method outputs with `python scripts/healthtech_demo.py --evaluate`. Under the printed output directory’s `evaluation` folder, use `task-cards.json` for the common prompts and rubric. The worksheet `task-runs.csv` has one row per task and method. Keep participant and reviewer IDs pseudonymous and record actual times and judgments in a local copy.

| Method | Material to give the analyst |
|---|---|
| Manual | Task card and access to public sources |
| Lexical B0 | Task card and the corresponding result in `lexical-evidence.json`, with links to its supporting sources |
| Curated dossiers | Task card and the corresponding result in `research-results.json`, or the same frozen records in the demo |

Assign one method per analyst per task to avoid repeating a task after exposure to another method. Rotate method assignments across tasks where feasible. Start the timer when the analyst receives the task. Stop it when they submit the sourced answer, a justified abstention or their unfinished work. Record the candidate or evidence gap, source passages, and the search performed. The independent reviewer should assess the answer without seeing the method or elapsed time where practical, then record their rubric grade, count of material evidence errors, reasons and review date. A useful answer or supported abstention requires a grade of at least 2 and zero material errors. Place the reviewer declarations in a copy of `lexical-review/reviewers.json` using the workbench’s existing human reviewer format.

Run the report from the repository root with the actual review cutoff.

```sh
python scripts/healthtech_review.py /tmp/demo/evaluation \
  --runs /tmp/review/task-runs.csv --reviewers /tmp/review/reviewers.json \
  --as-of 2026-11-19
```

The report lists submitted observations and compares methods on tasks with all three reviewed runs. It reports time to a useful answer within the successful runs, alongside denominators and material errors. Use the results descriptively because the workflows expose different corpora and analyst allocations may differ. The six tasks were used in development. The held-out slot awaits independently authored tasks and a product-family-disjoint evidence set. The older candidate-level sheets remain available for separate relevance and claim audits.
