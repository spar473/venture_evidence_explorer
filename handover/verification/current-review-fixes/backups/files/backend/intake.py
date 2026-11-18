"""venture-intake:1: append-only local assertions, never accepted source facts."""
import hashlib
import json
import math
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime,timezone
from typing import Literal
from pydantic import Field,field_validator,model_validator
from .ingestion import StrictModel,Text,HistoricalDate,day
from .contracts import Contract,ComparisonResult
from .database import connect
from .repository import corpus_documents,candidate_ids,detail_many
from .retrieval import tokens,name_key,METHOD
from .comparison_runs import corpus_digest

UNKNOWN={'precision':'unknown','lower_bound':None,'upper_bound':None}

class SuppliedClaim(StrictModel):
    field: Literal['problem','solution','intended_user','buyer','technology','business_model','validation','deployment','other']
    text: Text=Field(max_length=5000)
    source_url: Text=Field(max_length=2000)
    source_title: Text=Field(max_length=500)
    publisher: Text=Field(max_length=500)
    locator: Text=Field(max_length=1000)
    source_relationship: Literal['entrant','company','university','customer','regulator','investor','project_team','other_identified']
    published_date: HistoricalDate
    retrieved_on: Text
    effective_date: HistoricalDate
    @model_validator(mode='after')
    def chronology(self):
        from urllib.parse import urlsplit
        url=urlsplit(self.source_url)
        if url.scheme!='https' or not url.netloc or url.username or any(c.isspace() for c in self.source_url):raise ValueError('A valid HTTPS source URL is required')
        day(self.retrieved_on)
        if self.published_date.lower_bound and self.published_date.lower_bound>self.retrieved_on:raise ValueError('Publication is after retrieval')
        return self

class DraftContent(StrictModel):
    format_version: Literal['venture-intake:1']='venture-intake:1'
    name: Text=Field(max_length=300)
    aliases: list[Text]=Field(default_factory=list,max_length=30)
    description: str=Field(default='',max_length=5000)
    claims: list[SuppliedClaim]=Field(default_factory=list,max_length=30)
    research_subject_id: str | None=None
    @field_validator('aliases')
    @classmethod
    def unique_aliases(cls,values):
        if len({name_key(v) for v in values})!=len(values):raise ValueError('Aliases must be distinct')
        return values

class SaveDraft(DraftContent):
    request_id: Text=Field(max_length=100)
    expected_revision: int | None=Field(default=None,ge=1)

class Duplicate(Contract):
    kind: str
    subject_id: str
    display_name: str
    basis: str
    accepted_identity: bool=False

class Draft(Contract):
    draft_id: str
    revision_id: str
    revision_number: int
    payload_sha256: str
    saved_at: str
    content: DraftContent
    duplicates: list[Duplicate]
    identity_state: Literal['unresolved']='unresolved'
    assertion_origin: Literal['local_user_assertion']='local_user_assertion'
    claim_disposition: Literal['user_supplied_source_attribution_unreviewed']='user_supplied_source_attribution_unreviewed'
    review_status: Literal['draft_unreviewed']='draft_unreviewed'
    unknowns: list[str]

class DuplicatePage(Contract):
    items: list[Duplicate]

class DraftPage(Contract):
    items: list[Draft]
    total: int

class IntakeComparison(Contract):
    wrapper_version: Literal['intake-b0-query-1.0']='intake-b0-query-1.0'
    baseline_version: str
    draft: Draft
    effective_query: str
    query_fields: list[str]
    policy: Literal['exploration','accepted']
    excluded_venture_ids: list[str]
    identity_limitation: str
    results: list[ComparisonResult]
    abstention_reason: str | None
    corpus_digest: str
    run_id: str

class DraftCompareRequest(StrictModel):
    policy: Literal['exploration','accepted']='exploration'
    mode: Literal['product_customer','commercialisation']='product_customer'

UNKNOWN_FACTS=['Legal identity','Operating status','Funding stage','Buyer and payer','Procurement authority','Commercial outcomes']

def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)

def duplicate_candidates(conn,name,aliases=(),exclude_draft=None):
    keys={name_key(n) for n in [name,*aliases]}
    result=[]
    for r in conn.execute('SELECT venture_id,display_name,aliases_json FROM ventures ORDER BY venture_id'):
        if keys & {name_key(n) for n in [r['display_name'],*json.loads(r['aliases_json'])]}:
            result.append(dict(kind='application',subject_id=r['venture_id'],display_name=r['display_name'],basis='Name/alias candidate only',accepted_identity=False))
    for r in conn.execute("SELECT record_id,record_json FROM research_records WHERE collection='subjects' ORDER BY record_id"):
        value=json.loads(r['record_json'])
        if name_key(value['display_name']) in keys:result.append(dict(kind='research',subject_id=r['record_id'],display_name=value['display_name'],basis='Research brand/project candidate only',accepted_identity=False))
    for r in conn.execute('SELECT r.* FROM intake_revisions r WHERE revision_number=(SELECT MAX(revision_number) FROM intake_revisions WHERE draft_id=r.draft_id) ORDER BY draft_id'):
        v=json.loads(r['payload_json'])
        if r['draft_id']!=exclude_draft and keys & {name_key(n) for n in [v['name'],*v['aliases']]}:
            result.append(dict(kind='draft',subject_id=r['draft_id'],display_name=v['name'],basis='Unresolved saved draft name/alias',accepted_identity=False))
    return result

def get_draft(conn,draft_id):
    row=conn.execute('SELECT * FROM intake_revisions WHERE draft_id=? ORDER BY revision_number DESC LIMIT 1',(draft_id,)).fetchone()
    if row is None:return None
    row=dict(row);content=json.loads(row['payload_json'])
    return {k:row[k] for k in ('draft_id','revision_id','revision_number','payload_sha256','saved_at')}|dict(content=content,duplicates=duplicate_candidates(conn,content['name'],content['aliases'],draft_id),identity_state='unresolved',assertion_origin='local_user_assertion',claim_disposition='user_supplied_source_attribution_unreviewed',review_status='draft_unreviewed',unknowns=UNKNOWN_FACTS)

def list_drafts(conn):
    ids=[r[0] for r in conn.execute('SELECT draft_id FROM intake_drafts ORDER BY created_at DESC,draft_id LIMIT 100')]
    return dict(items=[get_draft(conn,i) for i in ids],total=conn.execute('SELECT COUNT(*) FROM intake_drafts').fetchone()[0])

def save_draft(path,body,draft_id=None,failure_injector=None):
    content=DraftContent.model_validate(body.model_dump(exclude={'request_id','expected_revision'})).model_dump()
    raw=canonical(content);digest=hashlib.sha256(raw.encode()).hexdigest()
    with closing(sqlite3.connect('file:'+str(path)+'?mode=rw',uri=True)) as conn:
        conn.row_factory=sqlite3.Row;conn.execute('PRAGMA foreign_keys=ON');conn.execute('BEGIN IMMEDIATE')
        try:
            previous=conn.execute('SELECT * FROM intake_revisions WHERE request_id=?',(body.request_id,)).fetchone()
            if previous:
                if previous['payload_sha256']!=digest or (draft_id and previous['draft_id']!=draft_id):raise ValueError('Request ID reused for different input')
                result=get_draft(conn,previous['draft_id']);conn.execute('ROLLBACK');return result
            if content['research_subject_id'] and not conn.execute("SELECT 1 FROM research_records WHERE namespace='research:0.2.1' AND collection='subjects' AND record_id=?",(content['research_subject_id'],)).fetchone():raise ValueError('Research subject not found')
            now=datetime.now(timezone.utc).isoformat()
            if draft_id:
                latest=conn.execute('SELECT MAX(revision_number) FROM intake_revisions WHERE draft_id=?',(draft_id,)).fetchone()[0]
                if latest is None:raise LookupError('Draft not found')
                if body.expected_revision!=latest:raise ValueError('Draft changed; reopen before saving')
                number=latest+1
            else:
                if body.expected_revision is not None:raise ValueError('New drafts cannot have expected_revision')
                draft_id='draft_'+uuid.uuid4().hex;number=1
                conn.execute('INSERT INTO intake_drafts VALUES (?,?)',(draft_id,now))
            if failure_injector:failure_injector(conn)
            conn.execute('INSERT INTO intake_revisions VALUES (?,?,?,?,?,?,?)',('revision_'+uuid.uuid4().hex,draft_id,number,body.request_id,raw,digest,now))
            result=get_draft(conn,draft_id);conn.execute('COMMIT');return result
        except BaseException:
            if conn.in_transaction:conn.execute('ROLLBACK')
            raise

def compare_draft(conn,draft_id,body):
    owns=not conn.in_transaction
    if owns:conn.execute('BEGIN')
    try:
        draft=get_draft(conn,draft_id)
        if draft is None:raise LookupError('Draft not found')
        content=draft['content'];excluded=[]
        if content['research_subject_id']:
            mapping=conn.execute("SELECT * FROM research_identity_mappings WHERE namespace='research:0.2.1' AND subject_id=? ORDER BY rowid DESC LIMIT 1",(content['research_subject_id'],)).fetchone()
            if mapping and mapping['state']=='resolved':excluded=[mapping['venture_id']]
        # Input is a query, never corpus evidence, including under accepted policy.
        fields=['description'] if content['description'].strip() else []
        query=content['description'].strip()
        if content['claims']:
            query+=' '+' '.join(c['text'] for c in content['claims']);fields.append('user_supplied_source_attributions')
        documents=corpus_documents(conn,policy=body.policy)
        qt=tokens(query);sets={v['venture_id']:set().union(*(tokens(o['value_text']) for o in v['observations'] if o['field'] in METHOD['fields'][body.mode])) for v in documents}
        idf={t:1+math.log((len(documents)+1)/(1+sum(t in d for d in sets.values()))) for t in sorted(qt)}
        scored=[]
        for v in documents:
            if v['venture_id'] in excluded:continue
            matched=qt&sets[v['venture_id']]
            if len(matched)<2 or len(matched)/len(qt)<.15:continue
            scored.append((math.fsum(idf[t] for t in sorted(matched))/math.fsum(idf.values()),v,matched))
        scored.sort(key=lambda row:(-row[0],row[1]['venture_id']))
        profiles=detail_many(conn,[v['venture_id'] for _,v,_ in scored[:3]])
        results=[]
        for score,v,matched in scored[:3]:
            vid=v['venture_id'];results.append(dict(venture=profiles[vid],ranking_score=round(score,6),query_token_coverage=round(len(matched)/len(qt),4),matched_terms=sorted(matched),evidence=[dict(observation=o,matched_terms=sorted(qt&tokens(o['value_text']))) for o in v['observations'] if o['field'] in METHOD['fields'][body.mode] and qt&tokens(o['value_text'])],wording_differences=dict(query_only_terms=sorted(qt-sets[vid]),candidate_only_terms=sorted(sets[vid]-qt),meaning='Recorded wording only; unmentioned features remain unknown.'),unavailable_evidence=UNKNOWN_FACTS,brief='Shared sourced wording; inspect evidence before inferring relevance.'))
        record=dict(wrapper_version='intake-b0-query-1.0',baseline_version=METHOD['version'],draft=draft,effective_query=query.strip(),query_fields=fields,policy=body.policy,excluded_venture_ids=excluded,identity_limitation='Only a genuinely resolved research mapping excludes the same app subject. Name/alias candidates remain unresolved; input is not trusted corpus evidence.',results=results,abstention_reason=None if results else 'No eligible candidate meets the lexical overlap rules; missing evidence is not irrelevance.',corpus_digest=corpus_digest(conn))
        return dict(record,run_id=hashlib.sha256(canonical(record).encode()).hexdigest())
    finally:
        if owns and conn.in_transaction:conn.execute('ROLLBACK')
