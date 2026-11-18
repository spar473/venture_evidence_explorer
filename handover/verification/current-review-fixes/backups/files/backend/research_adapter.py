"""Transactional, loss-accounted research 0.2.1 graph ingestion.

Research records remain separate from the original B0 corpus. A proposed brand
mapping never supplies legal identity or a factual acceptance.
"""
import calendar
import hashlib
import json
import re
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator
from .database import ROOT, connect, migrate
from .ingestion import HistoricalDate, StrictModel, Text, day
from .research_validation import COLLECTIONS, ResearchValidationError, decode_packet, pointer, validate_research_packet

NAMESPACE='research:0.2.1'
EXAMPLE=ROOT/'research/framework-v0.2.1/Two_Dossier_Research_Example.json'
TABLES=('research_records','research_imports','research_import_records','research_links','research_time_values','research_identity_mappings','research_mapping_documents')


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)


def research_time_interval(value):
    precision=value['precision']; raw=value['value']
    if precision=='unknown':
        result={'precision':'unknown','lower_bound':None,'upper_bound':None}
    else:
        if precision=='day':
            lower=upper=day(raw)
        elif precision=='month':
            year,month=map(int,raw.split('-'))
            lower=f'{year:04d}-{month:02d}-01'
            upper=f'{year:04d}-{month:02d}-{calendar.monthrange(year,month)[1]:02d}'
        elif precision=='year':
            year=int(raw); lower=f'{year:04d}-01-01'; upper=f'{year:04d}-12-31'
        else:
            raise ValueError('Unsupported research date precision')
        result={'precision':precision,'lower_bound':lower,'upper_bound':upper}
    HistoricalDate.model_validate(result)
    return result


class MappingDecision(StrictModel):
    mapping_id: Text
    subject_id: Text
    venture_id: Text
    state: Literal['resolved','rejected']
    scope: Literal['brand_project_only']
    actor_role: Literal['owner','independent_reviewer']
    actor_id: Text
    decided_on: Text
    evidence_ids: Annotated[list[Text],Field(min_length=1)]
    rationale: Text
    supersedes_mapping_id: Text
    _day=field_validator('decided_on')(day)


class MappingDocument(StrictModel):
    format_version: Literal['identity-mappings:1']
    decisions: list[MappingDecision]


def _records(packet):
    result=[]
    for collection,key in COLLECTIONS.items():
        result.extend((collection,row[key],row) for row in packet[collection])
    for readiness in packet['readiness']:
        result.extend(('requirements',row['requirement_id'],row) for row in readiness['requirements'])
        result.extend(('conclusions',row['conclusion_id'],row) for row in readiness['supported_conclusions'])
    return result


REFERENCE_FIELDS={
    'subject_id','subject_ids','required_subject_ids','source_id','source_ids','inspected_source_ids',
    'related_party_id','observation_ids','basis_observation_ids','supporting_observation_ids',
    'event_id','event_ids','state_basis_report_ids','missing_unknown_ids','conflict_ids',
    'unresolved_case_ids','access_gap_ids','acceptance_review_id','target_id','requirement_id','conclusion_id',
}


def _walk(value,parts=()):
    if isinstance(value,dict):
        if not value:
            yield parts,value
        else:
            for key,item in value.items():
                yield from _walk(item,parts+(key,))
    elif isinstance(value,list):
        if not value:
            yield parts,value
        else:
            for index,item in enumerate(value):
                yield from _walk(item,parts+(index,))
    else:
        yield parts,value


def _time_values(value,parts=()):
    if isinstance(value,dict):
        if {'value','precision','basis','unknown_reason'} <= value.keys():
            yield pointer(parts),value
        else:
            for key,item in value.items():
                yield from _time_values(item,parts+(key,))
    elif isinstance(value,list):
        for index,item in enumerate(value):
            yield from _time_values(item,parts+(index,))


def _links(record,owner_id,ids):
    for parts,value in _walk(record):
        key=next((part for part in reversed(parts) if isinstance(part,str)),None)
        if key in REFERENCE_FIELDS and isinstance(value,str) and value in ids and value != owner_id:
            yield pointer(parts),value


def _accounting(packet, errors=None):
    errors=errors or []
    if not isinstance(packet,dict):
        return {'leaf_count':1,'totals':{'mapped':0,'preserved_research_only':0,'quarantined':0,'unsupported':1},'fields':[{'path':'/','category':'unsupported','reason':'Research packet must be an object.'}],'collections':{}}
    entries=[]
    for parts,value in _walk(packet):
        path=pointer(parts)
        collection=parts[0] if parts else ''
        top_supported=collection in ('metadata',*COLLECTIONS)
        unsupported=not top_supported
        for error in errors:
            if error['category']=='unsupported' and (path==error['path'] or path.startswith(error['path'].rstrip('/')+'/')):
                # AdditionalProperties identifies its containing object. Any
                # unknown name is still preserved in report with its exact path.
                if 'Additional properties' in error['message']:
                    bad_names=re.findall(r"'([^']+)'",error['message'])
                    unsupported=unsupported or any(name in parts for name in bad_names)
                elif path==error['path'] or path.startswith(error['path'].rstrip('/')+'/'):
                    unsupported=True
        if unsupported:
            category='unsupported';reason='Outside the supported research 0.2.1 schema; import refused.'
        elif any(key in parts for key in ('proposed_application_id','identity_link_status')):
            category='quarantined';reason='Unresolved external brand/project link; retained, never an accepted/legal mapping.'
        elif collection=='events' and isinstance(packet.get('events'),list) and isinstance(parts[1] if len(parts)>1 else None,int) and isinstance(packet['events'][parts[1]],dict) and packet['events'][parts[1]].get('identity_resolution')=='unresolved_possible_duplicate':
            category='quarantined';reason='Possible duplicate event retained, excluded from established-event aggregates.'
        elif parts and (parts[-1] in set(COLLECTIONS.values())|{'requirement_id','conclusion_id'} or any(part in REFERENCE_FIELDS for part in parts if isinstance(part,str))):
            category='mapped';reason='Stable namespace identity / validated reference mapped to the research graph.'
        else:
            category='preserved_research_only';reason='Exact semantic field retained in immutable research record/raw packet; no legacy/B0 projection.'
        entries.append({'path':path,'category':category,'reason':reason})
    totals={category:sum(e['category']==category for e in entries) for category in ('mapped','preserved_research_only','quarantined','unsupported')}
    return {'leaf_count':len(entries),'totals':totals,'fields':entries,
            'collections':{name:{'count':len(value) if isinstance(value,list) else 1,'storage':'research_records + original packet' if name!='metadata' else 'research_imports.metadata_json + original packet'} for name,value in packet.items()}}


def _load(packet_path,as_of,mapping_decisions_path=None):
    raw=Path(packet_path).read_bytes();packet=decode_packet(raw)
    counts=validate_research_packet(packet,as_of)
    decisions=[];decision_raw=None
    if mapping_decisions_path:
        decision_raw=Path(mapping_decisions_path).read_bytes()
        document=MappingDocument.model_validate(decode_packet(decision_raw))
        ids={rid for _,rid,_ in _records(packet)}
        subjects={r['subject_id']:r for r in packet['subjects']}
        mapping_ids=set()
        for decision in document.decisions:
            if decision.mapping_id in mapping_ids:
                raise ValueError('Duplicate mapping decision ID')
            mapping_ids.add(decision.mapping_id)
            if decision.subject_id not in subjects or not set(decision.evidence_ids)<=ids:
                raise ValueError('Mapping decision subject/evidence reference missing')
            if decision.decided_on > as_of:
                raise ValueError('Mapping decision after external validation date')
            decisions.append(decision.model_dump())
    return {'packet':packet,'raw':raw,'counts':counts,'records':_records(packet),
            'packet_sha256':hashlib.sha256(raw).hexdigest(),'semantic_sha256':hashlib.sha256(canonical(packet).encode()).hexdigest(),
            'decisions':decisions,'decision_raw':decision_raw,'as_of':as_of}


def _table_exists(conn,name):
    return conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(name,)).fetchone() is not None


def _conflicts(conn,prepared):
    if not _table_exists(conn,'research_records'):
        return []
    existing={row['record_id']:(row['collection'],row['record_json']) for row in map(dict,conn.execute('SELECT * FROM research_records WHERE namespace=?',(NAMESPACE,)))}
    return [{'record_id':rid,'collection':collection,'reason':'Immutable research ID already has different semantic content'}
            for collection,rid,record in prepared['records'] if rid in existing and existing[rid]!=(collection,canonical(record))]


def _mapping_errors(conn,prepared):
    """Validate supplied decision lineage/external targets before any writes."""
    errors=[]
    if not prepared['decisions']:
        return errors
    if conn is None:
        return [{'path':'/mapping_decisions','message':'A database with the proposed application targets is required to validate supplied mapping decisions.'}]
    rows={rid:(collection,row) for collection,rid,row in prepared['records']}
    subjects={row['subject_id']:row for row in prepared['packet']['subjects']}
    known={}
    if _table_exists(conn,'research_identity_mappings'):
        known={row['mapping_id']:dict(row) for row in map(dict,conn.execute('SELECT * FROM research_identity_mappings WHERE namespace=?',(NAMESPACE,)))}
    for subject in subjects.values():
        target=subject['proposed_application_id']
        if target and conn.execute('SELECT 1 FROM ventures WHERE venture_id=?',(target,)).fetchone():
            known.setdefault(_proposal_id(subject['subject_id']),{'namespace':NAMESPACE,'subject_id':subject['subject_id'],'venture_id':target,'scope':'brand_project_only','decided_on':None})
    for index,decision in enumerate(prepared['decisions']):
        path='/mapping_decisions/'+str(index)
        previous=known.get(decision['supersedes_mapping_id'])
        expected=(NAMESPACE,decision['subject_id'],decision['venture_id'],decision['scope'])
        actual=tuple(previous[k] for k in ('namespace','subject_id','venture_id','scope')) if previous else None
        if actual!=expected:
            errors.append({'path':path,'message':'Decision must supersede a matching supplied brand/project proposal or decision.'})
            continue
        if previous.get('decided_on') and decision['decided_on']<previous['decided_on']:
            errors.append({'path':path,'message':'Mapping decision predates its prior decision.'})
        source_ids={o['source_id'] for o in prepared['packet']['observations'] if o['subject_id']==decision['subject_id']}
        for evidence_id in decision['evidence_ids']:
            collection,row=rows[evidence_id]
            relevant=(collection=='subjects' and row['subject_id']==decision['subject_id']) or (collection=='sources' and evidence_id in source_ids) or row.get('subject_id')==decision['subject_id'] or decision['subject_id'] in row.get('subject_ids',[])
            if not relevant:
                errors.append({'path':path+'/evidence_ids','message':'Mapping evidence outside the mapped research subject.'})
            if collection=='sources' and row['retrieved_on']>decision['decided_on']:
                errors.append({'path':path+'/decided_on','message':'Decision predates its cited source inspection.'})
        old=known.get(decision['mapping_id'])
        if old and old.get('state') is not None:
            expected_values={**decision,'namespace':NAMESPACE,'evidence_ids_json':canonical(decision['evidence_ids']),'legal_identity_state':'unresolved'}
            for key in ('subject_id','venture_id','state','scope','actor_role','actor_id','decided_on','rationale','supersedes_mapping_id','evidence_ids_json'):
                if old.get(key)!=expected_values[key]:
                    errors.append({'path':path,'message':'Conflicting immutable mapping decision ID.'})
                    break
        known[decision['mapping_id']]={**decision,'namespace':NAMESPACE}
    return errors


def _identity_preview(conn,packet):
    all_ventures=[]
    legacy_sources=[]
    if conn is not None:
        all_ventures=[dict(r) for r in conn.execute('SELECT venture_id,display_name,aliases_json,legal_name,registration_id FROM ventures ORDER BY venture_id')]
        legacy_sources=[dict(r) for r in conn.execute('SELECT DISTINCT o.venture_id,s.source_id,s.url FROM observations o JOIN sources s USING(source_id)')]
    def key(text):return re.sub('[^a-z0-9]','',text.lower())
    result=[]
    for subject in packet['subjects']:
        proposed=subject['proposed_application_id']
        named=[v['venture_id'] for v in all_ventures if key(subject['display_name']) in {key(v['display_name']),*(key(x) for x in json.loads(v['aliases_json']))}]
        target=next((v for v in all_ventures if v['venture_id']==proposed),None)
        subject_sources={o['source_id'] for o in packet['observations'] if o['subject_id']==subject['subject_id']}
        matches=[{'research_source_id':source['source_id'],'application_source_id':legacy['source_id'],'url':source['url']} for source in packet['sources'] if source['source_id'] in subject_sources for legacy in legacy_sources if legacy['venture_id']==proposed and source['url']==legacy['url']]
        result.append({'subject_id':subject['subject_id'],'proposed_application_id':proposed,'state':'proposed',
                       'scope':'brand_project_only','legal_identity_state':'unresolved','candidate_name_matches':named,
                       'target_exists':target is not None if conn else None,'source_url_matches':matches,'conflicting_matches':[x for x in named if x!=proposed],
                       'rationale':subject['identity_basis'],'decision_actor':None,'decision_date':None,
                       'quarantine_reason':'No genuine brand/project identity decision supplied; research remains inspectable under subject ID.'})
    return result


def _prepared_report(prepared, connection):
    conflicts = _conflicts(connection, prepared) if connection else []
    mapping_errors = _mapping_errors(connection, prepared)
    return {'status':'rejected' if conflicts or mapping_errors else 'valid_dry_run','namespace':NAMESPACE,
            'format_version':'0.2.1','packet_sha256':prepared['packet_sha256'],'semantic_sha256':prepared['semantic_sha256'],
            'validation_as_of':prepared['as_of'],'counts':prepared['counts'],
            'derived_records':len(prepared['records'])-sum(prepared['counts'].values()),
            'accounting':_accounting(prepared['packet']),
            'identity_mappings':_identity_preview(connection,prepared['packet']),
            'immutable_conflicts':conflicts,'mapping_decisions_supplied':len(prepared['decisions']),
            'mapping_errors':mapping_errors,'writes':0,
            'evidence_boundary':'Research-only graph; zero automatic factual acceptances, identity resolutions or B0 feature additions.'}


def dry_run_research(packet_path=EXAMPLE,db_path=None,as_of=None,mapping_decisions_path=None):
    as_of=as_of or date.today().isoformat()
    try:
        prepared=_load(packet_path,as_of,mapping_decisions_path)
    except ResearchValidationError as error:
        raw=Path(packet_path).read_bytes()
        try:packet=decode_packet(raw)
        except ResearchValidationError:packet={}
        return {'status':'rejected','namespace':NAMESPACE,'errors':error.errors,
                'accounting':_accounting(packet,error.errors),'writes':0}
    connection=None
    try:
        if db_path is not None and Path(db_path).exists():
            connection=connect(db_path)
        return _prepared_report(prepared,connection)
    finally:
        if connection:
            connection.close()


def _insert(conn,table,record,keys,ignore_existing=()):
    if table not in TABLES:
        raise ValueError('Unsupported research storage table')
    columns=sorted(record)
    predicate=' AND '.join(key+'=?' for key in keys)
    existing=conn.execute('SELECT '+','.join(columns)+' FROM '+table+' WHERE '+predicate,tuple(record[key] for key in keys)).fetchone()
    if existing is not None:
        original=dict(zip(columns,tuple(existing)))
        if any(original[key]!=record[key] for key in columns if key not in ignore_existing):
            raise ValueError('Conflicting immutable research record: '+table+'/'+str(tuple(record[k] for k in keys)))
        return
    conn.execute('INSERT INTO '+table+' ('+','.join(columns)+') VALUES ('+','.join('?' for _ in columns)+')',tuple(record[key] for key in columns))


def _proposal_id(subject_id):
    return NAMESPACE+':proposal:'+subject_id


def _write_graph(conn,prepared,failure_injector=None):
    packet,records=prepared['packet'],prepared['records'];digest=prepared['packet_sha256']
    timestamp=datetime.now(timezone.utc).isoformat()
    # Insert all record identities before FK links; the supplied graph was fully
    # validated first. Every write below belongs to one caller-owned transaction.
    first_source=True
    for collection,rid,record in records:
        _insert(conn,'research_records',{'namespace':NAMESPACE,'collection':collection,'record_id':rid,'record_json':canonical(record)},('namespace','record_id'))
        if collection=='sources' and first_source:
            first_source=False
            if failure_injector:failure_injector('after_source',conn)
    _insert(conn,'research_imports',{'namespace':NAMESPACE,'packet_sha256':digest,'format_version':'0.2.1','raw_bytes':prepared['raw'],
        'metadata_json':canonical(packet['metadata']),'semantic_sha256':prepared['semantic_sha256'],
        'validation_as_of':prepared['as_of'],'imported_at':timestamp},('namespace','packet_sha256'),ignore_existing=('imported_at','validation_as_of'))
    ids={rid for _,rid,_ in records}
    for order,(collection,rid,record) in enumerate(records):
        _insert(conn,'research_import_records',{'namespace':NAMESPACE,'packet_sha256':digest,'record_id':rid,'record_order':order},('namespace','packet_sha256','record_id'))
        for path,target in _links(record,rid,ids):
            _insert(conn,'research_links',{'namespace':NAMESPACE,'owner_id':rid,'field_path':path,'target_id':target},('namespace','owner_id','field_path','target_id'))
        for path,value in _time_values(record):
            _insert(conn,'research_time_values',{'namespace':NAMESPACE,'owner_id':rid,'field_path':path,
                'raw_value':value['value'],**research_time_interval(value),'basis':value['basis'],'unknown_reason':value['unknown_reason']},('namespace','owner_id','field_path'))
        if collection=='events' and failure_injector:
            failure_injector('during_events',conn)
    # Keep external missing targets quarantined rather than invent an app venture.
    for subject in packet['subjects']:
        target=subject['proposed_application_id']
        if target and conn.execute('SELECT 1 FROM ventures WHERE venture_id=?',(target,)).fetchone():
            evidence=[o['observation_id'] for o in packet['observations'] if o['subject_id']==subject['subject_id']]
            _insert(conn,'research_identity_mappings',{'mapping_id':_proposal_id(subject['subject_id']),'namespace':NAMESPACE,
                'subject_id':subject['subject_id'],'venture_id':target,'state':'proposed','scope':'brand_project_only',
                'actor_role':'supplied_proposal','actor_id':None,'decided_on':None,'evidence_ids_json':canonical(evidence),
                'rationale':subject['identity_basis'],'source_packet_sha256':digest,'legal_identity_state':'unresolved',
                'decision_document_sha256':None,'supersedes_mapping_id':None},('mapping_id',),ignore_existing=('source_packet_sha256',))
    if prepared['decision_raw'] is not None:
        decision_hash=hashlib.sha256(prepared['decision_raw']).hexdigest()
        _insert(conn,'research_mapping_documents',{'decision_sha256':decision_hash,'raw_bytes':prepared['decision_raw'],
            'validation_as_of':prepared['as_of'],'imported_at':timestamp},('decision_sha256',),ignore_existing=('imported_at','validation_as_of'))
        for decision in prepared['decisions']:
            previous=conn.execute('SELECT namespace,subject_id,venture_id,scope FROM research_identity_mappings WHERE mapping_id=?',(decision['supersedes_mapping_id'],)).fetchone()
            if previous is None or tuple(previous)!=(NAMESPACE,decision['subject_id'],decision['venture_id'],decision['scope']):
                raise ValueError('Mapping decision must supersede a matching supplied brand/project proposal or decision')
            _insert(conn,'research_identity_mappings',{'mapping_id':decision['mapping_id'],'namespace':NAMESPACE,
                'subject_id':decision['subject_id'],'venture_id':decision['venture_id'],'state':decision['state'],'scope':decision['scope'],
                'actor_role':decision['actor_role'],'actor_id':decision['actor_id'],'decided_on':decision['decided_on'],
                'evidence_ids_json':canonical(decision['evidence_ids']),'rationale':decision['rationale'],
                'source_packet_sha256':digest,'decision_document_sha256':decision_hash,
                'supersedes_mapping_id':decision['supersedes_mapping_id'],'legal_identity_state':'unresolved'},('mapping_id',),
                ignore_existing=('source_packet_sha256','decision_document_sha256'))


def import_research(db_path,packet_path=EXAMPLE,as_of=None,mapping_decisions_path=None,*,connection=None,failure_injector=None):
    as_of=as_of or date.today().isoformat()
    prepared=_load(packet_path,as_of,mapping_decisions_path)
    if connection is not None and connection.in_transaction:
        raise ValueError('Research import refuses an active caller transaction')
    own=connection is None
    conn=connection
    if conn is None:
        # Explicitly bootstrap existing schema using the ordinary preserved seed.
        # Whole research graph and research ledger are the following transaction.
        from .ingestion import load_seed
        if not Path(db_path).exists():
            load_seed(db_path)
        conn=sqlite3.connect(db_path)
        conn.row_factory=sqlite3.Row
    old_row_factory=conn.row_factory
    conn.row_factory=sqlite3.Row
    try:
        conn.execute('PRAGMA foreign_keys=ON')
        migrate(conn)
        conflicts=_conflicts(conn,prepared)
        if conflicts:
            raise ValueError('Conflicting immutable research IDs: '+', '.join(r['record_id'] for r in conflicts))
        mapping_errors=_mapping_errors(conn,prepared)
        if mapping_errors:
            raise ValueError('; '.join(error['message'] for error in mapping_errors))
        conn.execute('BEGIN IMMEDIATE')
        try:
            _write_graph(conn,prepared,failure_injector)
            if conn.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Research import foreign-key check failed')
            # Report the validated bytes that were imported, never a second read
            # of a potentially changed input path. Keep connection-only imports
            # tied to their actual target for mapping validation and previews.
            report=_prepared_report(prepared,conn)
            conn.execute('COMMIT')
        except BaseException:
            if conn.in_transaction:conn.execute('ROLLBACK')
            raise
    finally:
        if own and conn is not None:conn.close()
        elif conn is not None:conn.row_factory=old_row_factory
    report.update(status='imported',writes='atomic graph and ledger; repeated rows remain unchanged')
    return report


def list_research_records(conn,collection,namespace=NAMESPACE):
    return [json.loads(row[0]) for row in conn.execute('SELECT record_json FROM research_records WHERE namespace=? AND collection=? ORDER BY record_id',(namespace,collection))]


def get_research_packet(conn,packet_sha256=None,namespace=NAMESPACE):
    if packet_sha256:
        row=conn.execute('SELECT raw_bytes FROM research_imports WHERE namespace=? AND packet_sha256=?',(namespace,packet_sha256)).fetchone()
    else:
        row=conn.execute('SELECT raw_bytes FROM research_imports WHERE namespace=? ORDER BY rowid DESC LIMIT 1',(namespace,)).fetchone()
    return decode_packet(row[0]) if row else None


def import_research_connection(conn,packet_path=EXAMPLE,as_of=None,mapping_decisions_path=None,failure_injector=None):
    """Connection form with explicit transaction ownership and caller refusal."""
    if conn.in_transaction:
        raise ValueError('Research import requires a connection without an active transaction')
    return import_research(None,packet_path,as_of=as_of,mapping_decisions_path=mapping_decisions_path,connection=conn,failure_injector=failure_injector)
