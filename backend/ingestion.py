"""Strict, reusable input contracts and conflict-refusing offline import.

Version 1 is accepted byte-for-byte; version 2 adds explicit historical dates and
source-backed financial/event values. No model coerces numbers to identifiers.
"""
import calendar
import hashlib
import json
import re
import sqlite3
from datetime import date
from pathlib import Path
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StringConstraints, ValidationError, field_validator, model_validator
from .database import ROOT, migrate

Text = Annotated[str, StringConstraints(strict=True, min_length=1, pattern=r'\S')]
NullableText = Optional[Text]
Review = Literal['source_checked_owner_review_pending', 'unreviewed', 'accepted', 'rejected', 'needs_review']
TABLES = ('sources', 'ventures', 'observations', 'awards', 'connections', 'annotations')
KEYS = dict(zip(TABLES, ('source_id', 'venture_id', 'observation_id', 'award_id', 'connection_id', 'annotation_id')))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def day(value):
    require(isinstance(value, str) and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value)), 'Date must be YYYY-MM-DD')
    date.fromisoformat(value)
    return value


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')


FEATURE_FIELDS = (
    'identity', 'problem', 'solution', 'users', 'buyers', 'technology',
    'modality', 'business_model', 'validation', 'deployment', 'route_to_market',
    'milestones', 'financing', 'uoa_connections', 'community_connections',
)


class ResearchFeatureAssertion(StrictModel):
    """Sourced research assertion; unknown dimensions are omitted, never scored."""
    venture_id: Text
    dimension: Literal['identity', 'problem', 'solution', 'users', 'buyers',
                       'technology', 'modality', 'business_model', 'validation',
                       'deployment', 'route_to_market', 'milestones', 'financing',
                       'uoa_connections', 'community_connections']
    assertion_text: Text
    observation_ids: Annotated[list[Text], Field(min_length=1)]
    interpretation: Literal['source_assertion', 'analyst_interpretation']


class HistoricalDate(StrictModel):
    precision: Literal['unknown', 'day', 'month', 'year']
    lower_bound: Optional[Text]
    upper_bound: Optional[Text]

    @model_validator(mode='after')
    def valid_interval(self):
        lo, hi = self.lower_bound, self.upper_bound
        if self.precision == 'unknown':
            require(lo is None and hi is None, 'Unknown date has no invented bounds')
            return self
        require(lo is not None and hi is not None, 'Known dates require both bounds')
        day(lo); day(hi)
        lower, upper = date.fromisoformat(lo), date.fromisoformat(hi)
        require(lower <= upper, 'Reversed date interval')
        if self.precision == 'day':
            require(lo == hi, 'Day date must have equal bounds')
        elif self.precision == 'month':
            require(lower.day == 1 and lower.year == upper.year and lower.month == upper.month and upper.day == calendar.monthrange(lower.year, lower.month)[1], 'Month interval must use calendar bounds')
        else:
            require(lower.month == lower.day == 1 and upper.year == lower.year and upper.month == 12 and upper.day == 31, 'Year interval must use calendar bounds')
        return self


class Metadata(StrictModel):
    schema_version: Literal[1, 2]
    prepared_at: Text
    project: Text
    scope: Text
    selection: Text
    source_policy: Text
    time_policy: Text
    review_policy: Text
    outcome_labels_available: StrictBool

    @field_validator('schema_version', mode='before')
    @classmethod
    def strict_schema_version(cls, value):
        require(type(value) is int, 'Schema version must be an integer, never boolean or floating point')
        return value

    _prepared = field_validator('prepared_at')(day)


class Source(StrictModel):
    source_id: Text
    title: Text
    url: Text
    publisher: Text
    source_type: Literal['institutional_news', 'company_report', 'registry', 'publication', 'archive', 'other_public']
    published_at: Optional[Text]
    retrieved_at: Text
    content_version: Text
    archive_path: NullableText
    limitations: Text
    publication_date: Optional[HistoricalDate] = None
    available_at: Optional[Text] = None
    availability_evidence: Optional[Text] = None

    _retrieved = field_validator('retrieved_at')(day)

    @model_validator(mode='after')
    def valid_dates(self):
        require(self.url.startswith('https://'), 'Source needs HTTPS URL')
        if self.published_at is not None:
            day(self.published_at)
            require(self.published_at <= self.retrieved_at, 'Publication after retrieval')
        if self.publication_date:
            d = self.publication_date
            if self.published_at is not None:
                require(d.precision == 'day' and d.lower_bound == self.published_at, 'published_at conflicts with publication_date')
            if d.lower_bound:
                require(d.lower_bound <= self.retrieved_at, 'Publication interval definitely after retrieval')
        require((self.available_at is None) == (self.availability_evidence is None), 'Availability date needs evidence locator')
        if self.available_at:
            day(self.available_at)
            require(self.available_at <= self.retrieved_at, 'Availability after retrieval')
        return self


class Venture(StrictModel):
    venture_id: Text
    display_name: Text
    aliases: list[Text]
    entity_type: Literal['venture_or_project', 'company', 'project']
    legal_name: NullableText
    registration_id: NullableText
    current_operating_status: NullableText
    current_funding_stage: NullableText
    selection_bucket: Text
    identity_review_status: Literal['needs_owner_review', 'unreviewed', 'accepted', 'rejected', 'needs_review']


class FinancialValue(StrictModel):
    raw_amount: Text
    currency: Optional[Annotated[str, StringConstraints(strict=True, pattern=r'^[A-Z]{3}$')]]
    amount_qualifier: Literal['exact', 'approximately', 'at_least', 'up_to', 'range', 'unspecified']
    scope: Text
    event_date: HistoricalDate


class EventValue(StrictModel):
    event_type: Text
    description: Text
    event_date: HistoricalDate


class Observation(StrictModel):
    observation_id: Text
    venture_id: Text
    field: Text
    value_text: Text
    source_id: Text
    locator: Text
    assertion_type: Literal['publisher_report']
    effective_at: NullableText
    date_basis: Text
    review_status: Review
    effective_date: Optional[HistoricalDate] = None
    announcement_date: Optional[HistoricalDate] = None
    financial_value: Optional[FinancialValue] = None
    event_value: Optional[EventValue] = None

    @model_validator(mode='after')
    def effective_consistent(self):
        if self.effective_at:
            day(self.effective_at)
            if self.effective_date:
                require(self.effective_date.precision == 'day' and self.effective_date.lower_bound == self.effective_at, 'effective_at conflicts with effective_date')
        require(not (self.financial_value and self.event_value), 'Use one typed value per observation')
        return self


class Award(StrictModel):
    award_id: Text
    venture_id: Text
    programme: Literal['velocity_100k', 'velocity_ideas']
    award_year: Annotated[StrictInt, Field(ge=1000, le=9999)]
    award_label: Text
    place: Optional[Annotated[StrictInt, Field(gt=0)]]
    event_date: NullableText
    source_id: Text
    locator: Text
    review_status: Review
    event_date_interval: Optional[HistoricalDate] = None

    @model_validator(mode='after')
    def validate_event(self):
        if self.event_date:
            day(self.event_date)
            require(date.fromisoformat(self.event_date).year == self.award_year, 'Event year mismatch')
            if self.event_date_interval:
                require(self.event_date_interval.precision == 'day' and self.event_date_interval.lower_bound == self.event_date, 'event_date conflicts with interval')
        if self.event_date_interval and self.event_date_interval.lower_bound:
            require(date.fromisoformat(self.event_date_interval.lower_bound).year == date.fromisoformat(self.event_date_interval.upper_bound).year == self.award_year, 'Event interval year mismatch')
        return self


class Connection(StrictModel):
    connection_id: Text
    venture_id: Text
    connection_type: Text
    institution: Text
    observation_id: Text


class Annotation(StrictModel):
    annotation_id: Text
    venture_id: Text
    field: Text
    value_text: Text
    basis_observation_ids: Annotated[list[Text], Field(min_length=1)]
    origin: Literal['analyst_proposed']
    review_status: Literal['proposed']
    purpose: Text


class ObservationRelation(StrictModel):
    relation_id: Text
    observation_id: Text
    replacement_id: Text
    relation_type: Literal['supersedes', 'corrects']
    reviewer: Text
    recorded_at: Text
    rationale: Text
    _recorded = field_validator('recorded_at')(day)


class ImportDocument(StrictModel):
    metadata: Metadata
    sources: list[Source]
    ventures: list[Venture]
    observations: list[Observation]
    awards: list[Award]
    connections: list[Connection]
    annotations: list[Annotation]
    observation_relations: list[ObservationRelation] = Field(default_factory=list)

    @model_validator(mode='after')
    def relational_checks(self):
        data = self.model_dump()
        indexes = {}
        for table in TABLES:
            ids = [r[KEYS[table]] for r in data[table]]
            require(len(ids) == len(set(ids)), 'Duplicate IDs in '+table)
            indexes[table] = {r[KEYS[table]]: r for r in data[table]}
        if self.metadata.schema_version == 1:
            require(not self.observation_relations, 'observation_relations require input schema 2')
            for source in self.sources:
                require(source.published_at is not None, 'Schema 1 requires a publication day')
                require(source.publication_date is None and source.available_at is None, 'Historical metadata requires input schema 2')
            for obs in self.observations:
                require(all(getattr(obs,k) is None for k in ('effective_date','announcement_date','financial_value','event_value')), 'Historical values require input schema 2')
            require(all(a.event_date_interval is None for a in self.awards), 'Historical dates require input schema 2')
        for table in ('observations','awards','connections','annotations'):
            for row in data[table]:
                require(row['venture_id'] in indexes['ventures'], 'Unknown venture in '+table)
        for row in data['observations']+data['awards']:
            require(row['source_id'] in indexes['sources'], 'Unknown source')
        for row in data['awards']:
            source = indexes['sources'][row['source_id']]
            publication = source['published_at'] or (source['publication_date'] or {}).get('upper_bound')
            if publication:
                require(row['award_year'] <= date.fromisoformat(publication).year, 'Award year after report')
                event_lower = row['event_date'] or (row['event_date_interval'] or {}).get('lower_bound')
                if event_lower:
                    require(event_lower <= publication, 'Award event after report')
        for row in data['connections']:
            obs = indexes['observations'].get(row['observation_id'])
            require(obs is not None and obs['venture_id']==row['venture_id'], 'Connection evidence subject mismatch')
            require(obs['field']=='uoa_connection', 'Connection needs relationship evidence')
        for row in data['annotations']:
            for oid in row['basis_observation_ids']:
                obs = indexes['observations'].get(oid)
                require(obs is not None and obs['venture_id']==row['venture_id'], 'Annotation evidence subject mismatch')
        relation_ids = set()
        graph = {}
        for row in data['observation_relations']:
            require(row['relation_id'] not in relation_ids, 'Duplicate relation ID')
            relation_ids.add(row['relation_id'])
            old, new = indexes['observations'].get(row['observation_id']), indexes['observations'].get(row['replacement_id'])
            require(old is not None and new is not None and old['venture_id']==new['venture_id'] and old['field']==new['field'], 'Correction/supersession evidence subject or field mismatch')
            require(old['observation_id']!=new['observation_id'], 'Self supersession refused')
            graph.setdefault(row['observation_id'],[]).append(row['replacement_id'])
        def visit(node, trail):
            require(node not in trail, 'Cyclic observation relations')
            for nxt in graph.get(node,[]): visit(nxt, trail|{node})
        for node in graph: visit(node,set())
        return self


def validate(data):
    """Validate before touching SQLite, with nested error locations retained."""
    try:
        document = ImportDocument.model_validate(data)
    except ValidationError as error:
        raise ValueError('Invalid input columns/types or values: '+str(error)) from error
    return {t:{r[KEYS[t]]:r for r in data[t]} for t in TABLES}


def db_record(row):
    return {key+'_json' if isinstance(value,list) else key:
            json.dumps(value,ensure_ascii=False,separators=(',',':')) if isinstance(value,list) else value
            for key,value in row.items()}


def insert_immutable(conn, table, record, key):
    allowed = {r[1] for r in conn.execute('PRAGMA table_info('+table+')')}
    require(set(record)==allowed, 'Unexpected or missing columns in '+table)
    columns = sorted(allowed)
    existing = conn.execute('SELECT '+','.join(columns)+' FROM '+table+' WHERE '+key+'=?',(record[key],)).fetchone()
    values = tuple(record[c] for c in columns)
    if existing is not None:
        require(tuple(existing)==values, 'Conflicting immutable record: '+table+'/'+str(record[key]))
        return
    conn.execute('INSERT INTO '+table+' ('+','.join(columns)+') VALUES ('+','.join('?' for _ in columns)+')',values)


EXTENSIONS = {'sources': {'publication_date','available_at','availability_evidence'},
              'observations': {'effective_date','announcement_date','financial_value','event_value'},
              'awards': {'event_date_interval'}}


def adapt_records(data):
    """Explicit v1/v2 adapter; original input object and bytes remain untouched."""
    result = {}
    for table in TABLES:
        result[table] = []
        for row in data[table]:
            original = {k:v for k,v in row.items() if k not in EXTENSIONS.get(table,set())}
            # Legacy sources have NOT NULL publication strings. Unknown/partial is
            # represented only in the additive evidence_dates canonical relation.
            if table == 'sources' and original['published_at'] is None:
                original['published_at'] = ''
            result[table].append(original)
    return result


def store_extensions(conn, data):
    for table,kind,roles in (
        ('sources','source',{'publication_date':'publication'}),
        ('observations','observation',{'effective_date':'effective','announcement_date':'announcement'}),
        ('awards','award',{'event_date_interval':'event'})):
        for row in data[table]:
            for field,role in roles.items():
                value = row.get(field)
                if value:
                    key = kind+'/'+row[KEYS[table]]+'/'+role
                    record = {'date_id':key,'owner_kind':kind,'owner_id':row[KEYS[table]],'date_role':role,**value}
                    insert_immutable(conn,'evidence_dates',record,'date_id')
    for row in data['sources']:
        if row.get('available_at'):
            insert_immutable(conn,'source_availability',{'source_id':row['source_id'],'available_at':row['available_at'],'evidence_locator':row['availability_evidence']},'source_id')
    for row in data['observations']:
        for kind in ('financial_value','event_value'):
            if row.get(kind):
                insert_immutable(conn,'observation_values',{'observation_id':row['observation_id'],'value_type':kind,'value_json':json.dumps(row[kind],sort_keys=True,separators=(',',':'))},'observation_id')
    for row in data.get('observation_relations',[]):
        insert_immutable(conn,'observation_relations',row,'relation_id')


def load_seed(db_path, seed_path=None):
    raw = Path(seed_path or ROOT/'data/seed.json').read_bytes()
    data = json.loads(raw)
    validate(data)
    records = adapt_records(data)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True,exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute('PRAGMA foreign_keys=ON')
        conn.executescript((ROOT/'schema/schema.sql').read_text())
        migrate(conn)
        # Schema migrations intentionally precede the atomic data-import boundary.
        conn.execute('BEGIN IMMEDIATE')
        try:
            for table in TABLES:
                for row in records[table]:
                    insert_immutable(conn,table,db_record(row),KEYS[table])
            for row in data['annotations']:
                for oid in row['basis_observation_ids']:
                    conn.execute('INSERT OR IGNORE INTO annotation_evidence VALUES (?,?)',(row['annotation_id'],oid))
            store_extensions(conn,data)
            digest = hashlib.sha256(raw).hexdigest()
            conn.execute('INSERT OR IGNORE INTO imports VALUES (?,?,?)',(digest,data['metadata']['schema_version'],data['metadata']['prepared_at']))
            insert_immutable(conn,'import_documents',{'seed_sha256':digest,'raw_bytes':raw},'seed_sha256')
            require(not conn.execute('PRAGMA foreign_key_check').fetchall(),'Foreign-key check failed')
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
    finally:
        conn.close()
    return data
