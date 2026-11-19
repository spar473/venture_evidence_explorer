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

The next review is the MRI comparison with its first two reference dossiers. Review the question, time anchor, match rationale and unknowns before expanding the interface.
