# Project specification
Working title: Venture Evidence Explorer. Version 0.1, 16 November 2026.

## Problem and user
Public information about university ventures is spread across award announcements, research stories and company pages. An analyst or student founder preparing for a conversation needs relevant precedents, their differences and the evidence behind them.

Primary first user: an early-stage analyst preparing a company meeting.
Secondary user: a student founder investigating comparable commercialisation challenges.
Hiring audience: VC investment teams and data/analytics engineering recruiters.

## First task
Given a venture description and an investigation mode, return up to three useful comparisons, explain the match and important differences, show dated sources and draft five questions. Return fewer or no matches when evidence is insufficient.

Modes: product/customer; commercialisation pathway; stage/milestone (only when dated stage evidence exists).

## Cohort
Past Velocity $100K Challenge award recipients; Velocity Ideas Challenge award recipients; ventures with a documented UoA connection. Include projects as well as incorporated businesses. Treat programme awards, research origin, alumni connection and incubation as separate relationships.

Begin with ten selected records, then enumerate complete award lists for specified years (initially 2024–2026), retaining one venture identity across years and programmes. Expand historical coverage only after matching and provenance rules work. Do not describe the sample as the complete UoA ecosystem.

## Five questions
1. Which selected ventures have documented programme or university relationships?
2. Which cases are relevant to a specified customer, technology or deployment challenge?
3. Where does each suggested comparison break down?
4. What is unknown, historical, disputed or only proposed?
5. What questions or support pathways should a founder investigate next?

## First deliverable
A reviewed dataset, repeatable import and three source-aware SQL analyses. Next: a profile/search interface and evaluated comparison baseline. Later: AI briefs, Power BI and optional reviewed exports to MCDA Studio.

## Requirements
R1 Every sourced assertion resolves to a URL, publisher, publication/retrieval dates and passage locator.
R2 Unknown stays null; no inferred operating stage, closure, return or success label.
R3 Awards and UoA connections are many-to-one records, not one exclusive company category.
R4 Annotations and sourced observations remain visibly separate.
R5 Imports are repeatable and reject changed content under an existing immutable ID.
R6 A comparison states its purpose, evidence coverage and important differences.
R7 AI-generated content remains reviewable and source-linked.
R8 Public use starts with public sources and original summaries; private material needs explicit permission and a separate access design.

## Acceptance and evidence
Data gate: ten identity-reviewed venture/project records; every observation and award source-linked; no duplicate IDs or orphan references; repeat import changes no row counts.
Search gate: compare filters/keywords, structured matching and semantic retrieval on reviewer-judged tasks; report results without invented labels.
Product gate: several voluntary users can inspect a comparison and locate its source; record actual task time and usefulness feedback.
No users, relevance scores or productivity improvements are claimed yet.

## Boundaries
The first release does not rank founder quality, recommend investments or predict returns. Competition recognition is provenance metadata, excluded from default relevance features. A sparse public footprint does not imply inactivity. Published objectives are not demonstrated performance.

Main risks: sparse evidence, entity renames, selection bias, historical leakage, unsupported AI statements and misleading cross-sector matches. The design addresses these through dated records, explicit unknowns, reviewed labels and abstention.

