# Feasibility of a provider deployment forecast

## Target and entry

Proposed endpoint. A named provider begins routine use of a specific NZ-origin diagnostic product within 24 calendar months of the first verified human evaluation of that product in a provider setting. Record whether a source establishes payment in a separate field. Freeze the endpoint, scope and evidence rules before collecting outcomes.

The observational unit is a product family at its first eligible evaluation. Consolidate repeated studies, registry mirrors and renamed companies only after reviewing their version and entity links. Record the actual start date and its precision. Require a dated public record that proves which predictors were available at entry. Record planned evaluations, studies completed within research only, regulatory decisions, and deployments as distinct evidence.

For a positive outcome, retain the named provider, routine-workflow evidence, actual deployment interval, product, source and passage. Treat an interval straddling the 24-month threshold as unresolved. An explicit independently checkable record of no deployment by the horizon supports a negative label. Missing publicity, disappearance from an investor portfolio, and a trial’s registry status leave the outcome unknown. Document follow-up coverage and date for every entry, including discontinued or unfunded projects.

## Public source feasibility check

On 19 November 2026, a broad ClinicalTrials.gov search retrieved all **140 study records** with a New Zealand site, a device intervention and a listed 2016–2023 study start. It returned 77 completed, 29 active with recruitment closed, 15 recruiting, nine unknown, eight terminated, one withdrawn and one enrolling by invitation. These are registry records at retrieval. The dates, study status and location filter alone cannot establish eligible products or 24-month deployment outcomes. [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api) · [Registry data definitions](https://clinicaltrials.gov/policy/protocol-definitions)

```sh
curl --fail --silent --show-error --get 'https://clinicaltrials.gov/api/v2/studies' \
  --data-urlencode 'query.term=AREA[LocationCountry]"New Zealand" AND AREA[StartDate]RANGE[2016-01-01,2023-12-31] AND AREA[InterventionType]Device' \
  --data-urlencode 'fields=NCTId,BriefTitle,OverallStatus,LeadSponsorName,StartDate,StudyFirstPostDate,InterventionName,DesignPrimaryPurpose,StudyType' \
  --data-urlencode 'countTotal=true' --data-urlencode 'pageSize=200'
```

A narrower screening-or-diagnostic purpose query returned zero records and omitted the registry’s Alimetry comparison study. The broader query found that study, whose ANZCTR mirror links back to the same NCT identifier. This illustrates both the limits of purpose-code filtering and the need to collapse mirrored records. ANZCTR documents a search export that could complement this frame. Medsafe restricts WAND access and describes WAND as a notification system. MBIE’s award register can corroborate research support for some projects, with coverage limited to the grants it lists. [Gastric Alimetry registration](https://clinicaltrials.gov/study/NCT04992884) · [ANZCTR mirror](https://www.anzctr.org.au/Trial/Registration/TrialReview.aspx?id=21704&isClinicalTrial=True) · [ANZCTR export instructions](https://www.anzctr.org.au/docs/faqs.pdf) · [Medsafe access](https://www.medsafe.govt.nz/regulatory/devicesnew/3-4AccessingWANDDatabase.asp) · [MBIE award register](https://www.mbie.govt.nz/science-and-technology/science-and-innovation/funding-information-and-opportunities/investment-funds/who-got-funded)

## Decision

The public registry probe supplies discovery leads. It leaves the count of eligible NZ-origin product families, actual evaluation entries, and adequately ascertained outcomes unknown. The ten pilot cases were selected for comparison and remain outside the forecast cohort. No forecast was fit.

The next data work is to capture a fixed export from both registries, document exclusions and missing coverage, and obtain provider-side outcome follow-up from a source that can also substantiate negative cases. Review missingness by entry year, product class and sponsor, including quiet and discontinued projects. If outcome coverage supports evaluation, freeze an earlier training cohort and a later held-out cohort with disjoint product families and complete outcome windows. Compare any prespecified simple model with the training prevalence baseline on Brier score, calibration and uncertainty in the held-out cohort. Publish estimates only if those checks support the intended use.
