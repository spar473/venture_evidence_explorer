"""Apply the frozen NZ entry rule to public evidence, independently of outcomes."""
from collections import Counter, defaultdict
import hashlib
from pathlib import Path
import re
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, model_validator

from .database import ROOT
from .discovery import PACK, validate_packet
from .ingestion import StrictModel, Text, day
from .reference_pool import ENTRY_END, ENTRY_START, EventDate, https
from .research_validation import decode_packet
from .retrieval import name_key


ENTRIES = ROOT / 'research/healthtech-pilot/cohort-entry-evidence.json'


class EntrySource(StrictModel):
    publisher: Text
    url: Text
    retrieved_on: str
    publication: EventDate
    scope: Text


class EntryReport(StrictModel):
    company_id: Text
    name: Text
    source_id: Text
    locator: Text
    sector: Text
    date: EventDate
    date_basis: Literal['reported_occurrence', 'reported_month', 'announced_completed', 'unknown']
    label: Text | None = None
    institutional_investor: Text | None = None
    nz_basis: Literal['founded_or_headquartered', 'reported_location', 'outside_nz', 'unknown']
    first_basis: Literal['explicit_first', 'earliest_supported', 'publisher_round_one', 'unresolved']
    passage: Text
    corroborating_source_ids: list[Text] = Field(default_factory=list)


class DealBenchmark(StrictModel):
    year: int
    count: int = Field(gt=0)
    source_id: Text
    locator: Text
    definition: Text


class RegistryStatus(StrictModel):
    company_id: Text
    company_number: str = Field(pattern=r'^[0-9]+$')
    source_id: Text
    status: Literal['liquidation', 'removed']
    effective_on: str
    locator: Text


class PublicEntryEvidence(StrictModel):
    format_version: Literal['nz-cohort-entry-evidence:1']
    captured_on: str
    sources: dict[str, EntrySource]
    reports: list[EntryReport]
    benchmarks: list[DealBenchmark]
    registry_statuses: list[RegistryStatus] = Field(default_factory=list)

    @model_validator(mode='after')
    def chronology(self):
        day(self.captured_on)
        for source in self.sources.values():
            https(source.url)
            if day(source.retrieved_on) > self.captured_on:
                raise ValueError('Source was retrieved after evidence capture')
            _, end = source.publication.bounds()
            if end and end > source.retrieved_on:
                raise ValueError('Publication date exceeds retrieval')
        for report in self.reports:
            source = self.sources.get(report.source_id)
            if source is None:
                raise ValueError('Entry report must reference a known source')
            start, end = report.date.bounds()
            if (start is None) != (report.date_basis == 'unknown'):
                raise ValueError('Entry date and its basis disagree')
            _, publication_end = source.publication.bounds()
            if end and end > (publication_end or source.retrieved_on):
                raise ValueError('Reported event follows the publication or retrieval cutoff')
            if report.date_basis == 'announced_completed' and (
                report.date.precision != 'day' or source.publication.precision != 'day' or end != publication_end
            ):
                raise ValueError('Announcement-based date must match the dated publication')
            if report.date_basis == 'reported_month' and report.date.precision != 'month':
                raise ValueError('A reported month must retain month precision')
            if set(report.corroborating_source_ids) - self.sources.keys():
                raise ValueError('Unknown corroborating entry source')
        keys = {(row.company_id, row.source_id, row.locator) for row in self.reports}
        if len(keys) != len(self.reports):
            raise ValueError('Duplicate company/source passage')
        if any(row.source_id not in self.sources for row in self.benchmarks):
            raise ValueError('Benchmark must reference a known source')
        for record in self.registry_statuses:
            source = self.sources.get(record.source_id)
            url = urlsplit(source.url) if source else urlsplit('')
            if url.hostname != 'app.companiesoffice.govt.nz' or not url.path.endswith('/'+record.company_number):
                raise ValueError('Registry status requires its official company-number record')
            if day(record.effective_on) > source.retrieved_on:
                raise ValueError('Registry status takes effect after retrieval')
        return self


def seed_label(label):
    return bool(label and re.fullmatch(
        r'(?:pre[- ]?)?seed(?:\s+(?:equity|funding|financing|investment|capital|round|raise|money))*', label.strip(), re.I
    ))


def gaps(report):
    result = []
    if report.nz_basis != 'founded_or_headquartered':
        result.append('nz_founding_or_headquarters')
    if not seed_label(report.label):
        result.append('qualifying_round_label')
    if not report.institutional_investor:
        result.append('named_institutional_investor')
    if report.first_basis not in ('explicit_first', 'earliest_supported'):
        result.append('first_institutional_round')
    if report.date.precision == 'unknown':
        result.append('dated_round')
    return result


def decide(reports, identity_pending):
    if identity_pending:
        return 'unresolved', None, ['company_identity']
    dated = [(r.date.bounds(), r) for r in reports if not gaps(r)]
    if not dated:
        return 'unresolved', None, sorted({gap for r in reports for gap in gaps(r)}) or ['dated_entry_evidence']
    # Multiple reports of a round may overlap. Avoid selecting a precise day when
    # the reports support different labels or the earlier lead is still open.
    (_, upper), chosen = min(dated, key=lambda item:(item[0][1], item[0][0], item[1].source_id))
    lower, _ = chosen.date.bounds()
    for candidate in reports:
        if candidate is chosen or not seed_label(candidate.label):
            continue
        start, end = candidate.date.bounds()
        if start is None or end < lower or (
            start <= upper and candidate.label.lower().startswith('pre') != chosen.label.lower().startswith('pre')
        ):
            return 'unresolved', None, ['earlier_or_conflicting_round']
    if upper < ENTRY_START or lower > ENTRY_END:
        return 'outside_entry_window', chosen, []
    if lower < ENTRY_START or upper > ENTRY_END:
        return 'unresolved', None, ['entry_window_boundary']
    return 'included', chosen, []


def run_audit(discovery_path=PACK, evidence_path=ENTRIES):
    evidence_raw = Path(evidence_path).read_bytes()
    discovery_raw = Path(discovery_path).read_bytes()
    evidence = PublicEntryEvidence.model_validate(decode_packet(evidence_raw))
    discovery = decode_packet(discovery_raw)
    validate_packet(discovery, evidence.captured_on)
    discovery_rows = {row['discovery_id']:row for row in discovery['candidates']}
    cases = {company_id:row['display_name'] for company_id,row in discovery_rows.items()}
    open_identity = {company_id for case in discovery['unresolved_cases']
                     if case['status'] == 'open' and case['issue_type'] == 'possible_identity_link'
                     for company_id in case.get('subjects', [])}
    reports = defaultdict(list)
    for report in evidence.reports:
        if report.company_id.startswith('discovery_') and report.company_id not in cases:
            raise ValueError('Entry report references an unknown discovery ID')
        cases.setdefault(report.company_id, report.name)
        reports[report.company_id].append(report)
    normalized = Counter(name_key(name) for name in cases.values())
    results = []
    for company_id, company_name in sorted(cases.items()):
        claims = reports[company_id]
        staged = discovery_rows.get(company_id)
        status, entry, reasons = decide(claims, company_id in open_identity or normalized[name_key(company_name)] > 1)
        results.append(dict(company_id=company_id, name=company_name, status=status,
                            evaluated_on=evidence.captured_on, gaps=reasons,
                            discovery_source_ids=staged['source_ids'] if staged else [],
                            entry=entry.model_dump() if entry else None,
                            source_reports=[claim.model_dump() for claim in claims]))
    included = [row['entry'] for row in results if row['status'] == 'included']
    counts = Counter(row['status'] for row in results)
    reason_counts = Counter(reason for row in results if row['status'] == 'unresolved' for reason in row['gaps'])
    unresolved_ids = {row['company_id'] for row in results if row['status'] == 'unresolved'}
    named_round_one = {row.company_id for row in evidence.reports if row.company_id in unresolved_ids
                       and row.first_basis == 'publisher_round_one' and row.institutional_investor and seed_label(row.label)}
    evidence_by_source = Counter(report.source_id for report in evidence.reports)
    if any(record.company_id not in cases for record in evidence.registry_statuses):
        raise ValueError('Registry status references a company absent from the entry audit')
    included_ids = {entry['company_id'] for entry in included}
    documented_closed = {record.company_id for record in evidence.registry_statuses} & included_ids
    return dict(
        rule='nz-first-institutional-seed:1', evaluated_on=evidence.captured_on,
        window={'start':ENTRY_START, 'end':ENTRY_END}, candidate_records=len(results),
        discovery_leads=len(discovery['candidates']),
        discovery_source_families=len(discovery['organisations']),
        discovery_listings=len(discovery['listings']),
        discovery_listings_with_investment_date=sum(row['investment_date'] is not None for row in discovery['listings']),
        discovery_family_scope={org['name']:org['coverage_status'] for org in discovery['organisations']},
        counts={key:counts[key] for key in ('included','unresolved','outside_entry_window')},
        unresolved_by_gap=dict(sorted(reason_counts.items())),
        unresolved_with_named_round_one=len(named_round_one),
        included_by_vintage={str(year):sum(entry['date']['value'].startswith(str(year)) for entry in included)
                             for year in range(2012, 2023)},
        included_by_sector=dict(sorted(Counter(entry['sector'] for entry in included).items())),
        inclusion_basis=dict(sorted(Counter(entry['first_basis'] for entry in included).items())),
        evidence_rows_by_source=dict(sorted(evidence_by_source.items())),
        reported_vintages=sorted(Counter(r.date.value[:4] for r in evidence.reports if r.date.value).items()),
        input_sha256={'discovery':hashlib.sha256(discovery_raw).hexdigest(),
                      'entry_evidence':hashlib.sha256(evidence_raw).hexdigest()},
        benchmark_deal_counts=[row.model_dump() for row in evidence.benchmarks],
        follow_up={'status':'partial', 'registry_confirmed_closures':len(documented_closed),
                   'observed_at_36_months':None,
                   'registry_statuses':[record.model_dump() for record in evidence.registry_statuses]},
        outcome_gate='withheld', sources={key:source.model_dump() for key, source in evidence.sources.items()},
        decisions=results,
    )
