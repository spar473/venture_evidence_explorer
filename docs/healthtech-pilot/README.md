# NZ healthtech comparison pilot

This branch starts from `implementation/vee-workbench` at `bff2c0624907ef58e45a9cb617f0e3c56bf29e4d`. It begins with a [source-checked cohort inventory](cohort.json) and a [copy-ready implementation prompt](IMPLEMENTATION_PROMPT.md). The inventory is evidence preparation for the existing research adapter.

## First release

Use Automated Breast MRI Reporting to help an analyst answer what a university healthtech team should verify before seeking a provider evaluation. A comparison should show which historical products faced a similar workflow, what each looked like at its documented early stage, what happened later, and where the analogy breaks.

| Track | Cases | Use |
|---|---|---|
| Established reference companies | Formus Labs, Toku Eyes, Volpara, Alimetry | Clinical imaging workflow, commercialisation, adoption or regulatory pathway precedents scoped to the question |
| Adjacent reference | Wellumio | Portable stroke imaging and investor discovery. Use when hardware and acute care differences are visible |
| University projects | Automated Breast MRI Reporting, Neurofanos, PulseMap PAD Detector, IVF Decision Support Tool, VistaVision | Live diligence queries and scenario inputs after their starting evidence is reviewed |
| Existing contrast case | RosterLab | Useful for provider workflow and purchasing questions. Shared healthcare vocabulary alone should give it little relevance for diagnostic imaging validation |

The four established references have documented financing, regulatory and/or acquisition milestones. Some still need their earliest qualifying snapshot reconstructed. The five university projects are selected cases with incomplete follow-up. Their portfolio similarity cannot estimate their probability of fundraising, approval or adoption. Leave them out of model training.

## Sequence

1. **Evidence and identity.** Reconcile the inventory against existing dossier, seed and staged-discovery identities. Preserve project labels, product versions and unresolved mappings. Trace earlier contemporaneous evidence for Formus Labs and Toku before admitting them as same-stage peers. Volpara is a legacy pathway precedent. Each dossier must show its source, clinical context, key milestone, confidence boundary, and material unknowns.
2. **Test one comparison.** Produce a validated research packet for the MRI project and two source-supported historical references or scoped pathway precedents. Run a dry-run and exercise the import on a temporary database. Verify the existing dossier screen exposes the evidence. Verify that an early replay excludes future sources. If there is no supported same-stage comparison, the app should state that and display scoped pathway evidence independently.
3. **Expand and evaluate.** Prepare the other four university dossiers, build a common elapsed-time view, and evaluate against manual research and the existing lexical B0 baseline. Use held-out analyst tasks, include a deliberately sparse case, and measure time to a useful sourced result, relevance and material evidence errors.
4. **Add conditional scenarios.** After analyst feedback, use Venture Frame to test the cash and timing effects of a provider evaluation, delayed conversion or implementation costs. Expose assumptions and ranges. Keep execution deterministic so a reviewer can reproduce the figures.
5. **Research forecasting.** Define one endpoint such as publicly documented provider deployment within 24 months of a verified evaluation. Build a consistent historical entry cohort that includes quiet, unfunded and discontinued cases where possible. Check ascertainment and complete follow-up before modelling. Hold out later ventures and compare a simple model with the cohort baseline on calibration and error. Only publish probabilities if the data and validation support the decision use.

The ultimate product is decision support for the NZ healthtech pipeline. A founder or analyst can move from evidence to historical precedents, then to a concrete next milestone and a conditional scenario. Forecasting is an optional result of stronger longitudinal evidence.

## What counts as evidence

- Distinguish what an institution, investor, company or regulator actually establishes. Partnership, trial registration, research funding, equity financing, provider evaluation and paid deployment are separate events.
- Keep dates for events, publication and retrieval. The date a regulator made a decision is not automatically the date a particular version of its database became public.
- Preserve gaps, date precision, conflicts and product jurisdictions. In this inventory the 2023 Formus Hip FDA record and the company’s May 2026 clearance report need product and submission-level reconciliation.
- Avoid importing a duplicate company because a product, research project and legal entity have different labels. Leave patient-level data out of the workflow.

The next analyst review can start with the MRI comparison. Record which references helped answer the question and which material gaps remain.

## Implemented pilot · 19 November 2026

The first comparison and four university extensions now use the existing **Research dossiers** entry point and research 0.2.1 importer. Nothing is imported at server startup. The legacy ten-venture corpus and lexical B0 policy remain unchanged.

From a checkout with the documented Python and Node dependencies installed:

```sh
npm --prefix frontend ci
npm --prefix frontend run build
python scripts/healthtech_demo.py --serve --evaluate
```

Open <http://127.0.0.1:8001>, choose **Research dossiers → Automated Breast MRI Reporting**, then **Provider evaluation comparison**. Volpara, Formus and Wellumio are curated **pathway precedents**. The directory also shows the number and names of eligible reference ventures for each university project. Each has cited match rationale, material differences, reference-document evidence, later reports and unresolved questions. Expand a reference claim to inspect its publisher, responsibility, locator, publication, retrieval, context, occurrence and target dates. Evidence links reveal the corresponding original dossier record.

The script creates a fresh system-temporary database, validates/dry-runs/imports all four packets, verifies unchanged dry-run bytes and repeat-import rows, and refuses a nonempty explicit output directory. `--output-dir /tmp/my-new-healthtech-demo` selects a new/empty directory; omit `--serve` to prepare without starting a service. `--evaluate` exports the existing frozen B0 task/review workflow alongside curated research results and a separate blank research-review sheet. No relevance, factual-error or time-saving judgment is supplied.

The MRI packet is [packet.json](../../research/healthtech-pilot/packet.json). The additional projects and Toku reference are in [extension.json](../../research/healthtech-pilot/extension.json). The [clinical studies packet](../../research/healthtech-pilot/clinical-studies.json) adds Wellumio and Alimetry, with the original project records needed to validate its comparisons independently. Shared Formus rows retain exactly the same IDs and semantic content; importing both does not duplicate them. [comparisons.json](../../research/healthtech-pilot/comparisons.json) is a strict, versioned editorial selection manifest referencing imported readiness records. It orders at most three peers; it supplies no score and changes no B0 method.

| Selectable case | Current comparison | Boundary |
|---|---|---|
| Automated Breast MRI Reporting | Volpara, Formus, Wellumio | Breast imaging, image-guided planning and hospital MR feasibility testing. The provider admission threshold remains unknown. |
| Neurofanos | Formus, Wellumio | Surgical image guidance and brain imaging feasibility. Real-time navigation requires a different comparator from hip planning or stroke detection. |
| IVF Decision Support Tool | Formus, Alimetry | Specialist decision support and a method for assessing changes to clinical decisions. IVF clinic testing remains a plan. |
| VistaVision | Toku | Eye-care commercialisation analogy only; telerobotics differ from retinal-analysis software |
| PulseMap PAD Detector | Abstain | Modality, performance comparator and evaluated provider workflow are insufficiently described |
| RosterLab (existing dossier) | Abstain | A healthcare buyer and software vocabulary do not establish diagnostic-imaging relevance |

With all four packets imported, four of five university projects have at least one comparison. The eight project–venture pairs use five distinct reference dossiers. Formus appears in three pairs and Wellumio in two. The directory counts each once in the distinct reference total. RosterLab and QuickMas are additional research dossiers outside the university-project denominator.

**Historical snapshots abstain.** The authoritative research 0.2.1 contract fixes historical availability to false and provides no dated archive-witness locator. A contemporaneously authored document retrieved today is useful research, but cannot prove availability at an earlier cutoff. The UI keeps reference-document dates separate from verified early-stage anchors, which remain unset. Future/overlapping partial dates and later assessments cannot qualify an earlier comparison. The cutoff controls the comparison panel; the full source dossier remains inspectable below it.

Regulatory decisions and acquisition reports remain atomic observations because the existing event-kind enum cannot represent them. They appear in the comparison’s later-evidence section rather than being recast as financing or adoption. Neurofanos’s university research grant remains a text claim with its month precision: the contract’s monetary scopes do not support a grant, so no round-total or currency value is invented. Planned licences, clinic testing and launch targets remain intentions.

See [SOURCE_LOG.md](SOURCE_LOG.md) for source checks and identity reconciliation, and [STATUS.md](STATUS.md) for the exact implementation checkpoint and executed checks. Scenario modelling, a historical availability-witness extension and any forecasting cohort remain follow-on work.
