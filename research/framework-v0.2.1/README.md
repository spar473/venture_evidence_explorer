# VEE final research review — 0.2.1

Prepared 18 November 2026. The research package is ready for a bounded integration pilot. Direct import, accepted identity mappings and research dossier screens are still pending.

Start with [Implementation_TODOs.md](Implementation_TODOs.md): it separates existing functionality, work completed here and the ordered pilot gates. [Implementation_Note.md](Implementation_Note.md) maps the research model to the current codebase. [Local_Code_Review_Record.md](Local_Code_Review_Record.md) distinguishes checks rerun here from the attributed [engineering_completion.md](engineering_completion.md).

## What changed

| Reviewer finding | Completed correction |
|---|---|
| Event launch target can differ from its report | Event/report/observation date values and precision must agree along represented lineage. |
| Review target type can disagree with its ID | Exact typed collection lookup and acceptance projection matching. |
| Future raw review/retrieval/readiness dates can pass | Explicit preparation cutoff, external validation date and relevant source/assessment chronology guards. |
| Both-subject requirement can pass with one subject's evidence | Explicit `required_subject_ids` coverage and conclusion subject coverage; limited one-subject conclusions remain valid. |

The original four findings and the coupled future-retrieval/readiness variant were reproduced against 0.2. The new validator passes the unchanged substantive dossiers, **32 rejection cases and four permitted counterexamples**. Schema, examples and regression code ship together. Version 0.2 is preserved unchanged. The requirement field rename is deliberate and requires strict consumers to adapt.

The current local source was found and directly tested on an isolated copy: bootstrap/integrity, **59 backend tests with two version-specific skips**, production build, **13 browser tests**, API-type drift and targeted migration checks on Python 3.10 and 3.12 pass. No source/data files in the original app were edited. Fresh installation and CI execution remain pending; installed local dependencies were reused.

## Evidence boundary

The two dossiers still have 34 observations, six event candidates, six reports, 21 explicit unknowns, six readiness assessments and zero human acceptances. Source-reading provenance is inherited from 0.2; no new source research was done in this patch. Brand/project identity mappings remain proposed and legal identity stays separately unknown. The 274-entry inventory remains unchanged and unimported, not an accepted NZ population.

The next milestone is identity mapping → transactional adapter with loss accounting → two inspectable dossiers → real-task evaluation with closer alternatives and distractors. No relevance, time-saving, investment-quality or programme-impact result is established.

## Reproduce research validation

With Python 3.10+ and `jsonschema` (recorded version 4.26.0):

```sh
python3 validate_research_example.py --as-of 2026-11-18
```

The command reads adjacent schema/example/regression files and opens no app database. The schema is [Research_Interchange_v0.2.1.schema.json](Research_Interchange_v0.2.1.schema.json); cross-record semantics and limitations are in [Research_Interchange_Contract.md](Research_Interchange_Contract.md). [Validation_Record.json](Validation_Record.json) contains executed results, remaining cases and hashes.

The implementation-review ZIP additionally includes `application/` source/configuration matching `Application_Source_Manifest.json`. It excludes dependencies, live databases, backups, compiled assets and caches. Delivery stays local; the pasted review's request to push was not acted on.
