# Method v2 comparison audit · 21 November 2026

The disposable demo and production precedent API were evaluated with `as_of=2026-11-21`. The method is `witnessed-gower-b0:2`. A ranked peer requires clinical workflow coverage above zero, overall similarity of at least 0.35 and weighted coverage of at least 0.15. Named roles require at least three qualifying peers. The 36-month audit and gate inputs use the same definitions and data as before.

## Automated Breast MRI Reporting

The subject contributes witnessed `modality`, `clinical_user`, `output_type` and `description` as of 21 November. Its three categorical workflow values are breast MRI, radiologist and draft clinical imaging report. The missing subject fields are `buyer`, `procurement_path`, `business_model`, `regulatory_class`, `jurisdiction`, `regulatory_decision`, `stage`, `prototype`, `provider_study`, `submission`, `paid_pilot`, `full_time_team`, `months_since_founding`, `round_size_band` and `lead_investor_type`. Those fields cannot contribute coverage even when a peer has them. The subject's own entry date is unnecessary for this method.

| Peer anchor | Alignable Cohort A peers | Ranked peers | Roles |
| --- | ---: | ---: | --- |
| First institutional round | 55 | 0 | None |
| First provider or clinical study | 1 | 0 | None |
| First regulatory decision | 1 | 0 | None |
| First paid customer | 0 | 0 | None |

### First institutional round

This table lists the exact **missing peer fields among the four MRI can use today**. Coverage is weighted across all five dimensions. The [witnessed snapshot audit](WITNESSED_SNAPSHOT_AUDIT.md#field-by-field-coverage) lists present and missing fields across all five dimensions for the audited healthtech companies and sources.

| Candidate | Clinical fields missing at entry | Similarity | Coverage | Blocker |
| --- | --- | ---: | ---: | --- |
| HeartLab, Firstcheck Ltd | None | 0.0000 | 0.2500 | No shared categorical value or description token |
| TamoRx, Avalia Immunotherapies Ltd | `clinical_user` | 0.0000 | 0.1875 | No match among the available fields |
| RespirAq | `clinical_user`, `output_type` | 0.0000 | 0.1250 | Similarity and coverage |
| Tiro Lifesciences Ltd | `clinical_user`, `output_type` | 0.0469 | 0.1250 | Similarity and coverage. This was the highest raw similarity |
| Carepatron, Cleanery, Excellent, Immersve, Quashed, Runn.io, Supie | `modality`, `clinical_user`, `output_type` | 0.0000 | 0.0625 | Similarity and coverage |
| Formus Labs, Opum Technology, The Insides Company, AuramerBio, Myovolt Limited and the 37 other Cohort A entries below | `modality`, `clinical_user`, `output_type`, `description` | 0.0000 | 0.0000 | Required clinical coverage |

The 37 other entries with no witnessed comparison features at this anchor are Aplenty (Hot Lime Labs), Aspiring Materials, Astrix, Cetogenix, Cropsy, Dawn Aerospace, EnergyBank, eVouch, Foundry Lab, Halter, Inhibit Coatings Limited, Liquium, Marama Labs, Mint Innovation, Miruku, Sharesies, StretchSense, TasmanIon, TDRI, Vertus Energy, Vortex Power Systems, Zincovery, 1Centre, CodeLingo Limited, First AML, Fluent Scientific Ltd, Hi-Aspect, Jasper, Koti Technologies, Narrative, Parcelport, Partly, Photonic Innovations Ltd, Rocos, SafeStack, Social Club and VidApp.

Volpara and Wellumio remain curated references with no eligible entry anchor in the ranked cohort. Alimetry and Toku Eyes are also outside the ranked cohort. Formus Labs is both curated and a Cohort A candidate.

### First provider or clinical study

Only Formus Labs has an eligible Cohort A study anchor. Its witnessed description provides 0.0625 weighted coverage against MRI and 0.0000 similarity. Its missing comparable fields are `modality`, `clinical_user` and `output_type`. Every other Cohort A company lacks an eligible dated study anchor in the loaded records. The HeartLab publisher witness establishes that a pilot had occurred by publication. The collected record does not establish the study's first event date. Under the regulatory decision anchor, Formus has the same three missing clinical fields. The paid-customer anchor has no dated candidate.

## Toku Eyes

The seed-entry benchmark returns three ranked peers under the new workflow requirement. Each has positive clinical workflow coverage and zero clinical workflow similarity. Shared stage evidence drives the overall score. The ranking preserves the supplied dated status evidence and assigns each role to a different company.

| Role | Peer | Similarity | Coverage | As-of comp status | Status date |
| --- | --- | ---: | ---: | --- | --- |
| Ceiling | HeartLab | 0.5000 | 0.3333 | Operating on seed | 2026-07-01 |
| Typical | RespirAq | 0.5000 | 0.1667 | Operating on seed | 2026-11-16 |
| Floor | Firstcheck Ltd | 0.5000 | 0.2917 | Verified closure | 2021-10-13 |

Firstcheck's closure occurred after the 36-month window. Its legacy primary status remains `unknown`. The displayed latest-status ladder includes the verified closure, so the no-closure flag is false for this peer set.
