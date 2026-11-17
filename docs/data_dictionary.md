# Data dictionary and modelling decisions

## Unit and identity
A venture is a stable identity representing a publicly named project or business. Legal incorporation is not assumed. All ten seed identities have entity_type=venture_or_project because legal-entity checks are outside this pass.

Keep legal_name, registration_id, current_operating_status and current_funding_stage null until separately verified. A brand, project name and registered company are not automatically interchangeable.

Normalize case and punctuation to generate duplicate candidates only. Never auto-merge on name alone. Review product, people and institutional evidence. Preserve old names as aliases. A renamed project becoming a company needs an explicit identity decision. Aliases listed here are descriptive/source spellings, not verified legal trade names.

selection_bucket is the reason for inclusion in this small sample, not an exclusive cohort membership. For example, RosterLab has documented Velocity participation although it was selected under uoa_origin. Missing award rows do not assert no award.

## Sources
source_id: stable record ID.
title, url, publisher: public source identity.
source_type: institutional_news in this seed.
published_at: date displayed on the source, using the page over URL paths.
retrieved_at: date the assistant read the source.
content_version: human-readable retrieval label, not a cryptographic page snapshot.
archive_path: null; full source pages were not archived in this pass.
limitations: publisher reports are not independent verification.

For automated collection, add a legally appropriate raw snapshot location and content digest. Do not claim the original page can be reconstructed from this seed.

## Observations
observation_id, venture_id: stable assertion and subject.
field: product_description or uoa_connection in this seed.
value_text: short original paraphrase.
source_id, locator: supporting document and passage/section.
assertion_type: publisher_report, distinct from independent validation.
effective_at: date the fact applied, null unless explicitly known.
date_basis: explains how to interpret the historical description.
review_status: source_checked_owner_review_pending. This means source checking by the assistant, not validation by the owner, founders or an expert.

A statement describing a planned benefit must retain that intent. Do not convert aims or entrant descriptions into measured efficacy.

New sources may add conflicting or newer observations. Preserve both; do not overwrite earlier evidence with a single latest value.

## Awards
award_id, venture_id: event identity and subject.
programme: velocity_100k or velocity_ideas.
award_year: programme year.
award_label: exact place where reported, otherwise Winner (category not recorded).
place: ordinal placement, null for an unranked winner listing.
event_date: ceremony/result date if supported; null when not verified. Award year is not event day.
source_id, locator, review_status: evidence linkage.

No prize money is captured. Awards are not investment rounds. Finalists, entrants and award recipients require different event types when added. RosterLab participation is not entered as an award.

## Connections
connection_id, venture_id, institution, connection_type, observation_id.
Types used: uoa_programme_participation, uoa_student_venture, uoa_staff_research_team, uoa_research_origin, uoa_spinout, uoa_staff_alumni_founders.
Prefer the most specific supported relationship. Multiple relationship rows per venture are allowed. Programme participation alone does not establish a research spinout.

## Proposed annotations
annotation_id, venture_id, field, value_text, basis_observation_ids.
origin=analyst_proposed; review_status=proposed.
Fields: sector, modality, user_context, comparison_angle, example_diligence_question.
These support interface design and research review, not factual assertions or trusted evaluation labels. The users named are possible users/contexts, not verified purchasers. Commercialisation challenges are hypotheses for investigation, not established deficiencies.

## Time rules
- An article read in 2026 about 2021 does not verify 2026 operating status.
- source published_at and retrieved_at are different from effective_at and event_date.
- This seed is usable for contemporary exploration of historical reports, not a point-in-time return backtest.
- Strict backtesting would require versioned source availability, capture dates and a specified assessment cutoff.
- Query publication cutoffs must use the selected observation's source date. Never join an old award to today's text and call it historical knowledge.
- Future-stage or outcome analysis needs additional dated observations and cannot be inferred from the seed.

## Analytical denominators
Counts describe this selected dataset only. Category counts may overlap. Count distinct venture_id for ventures, award_id for awards and connection_id for relationships. Never sum overlapping programme counts as unique founders or businesses. No entrant denominator, comparison population or commercial-success labels are available.

