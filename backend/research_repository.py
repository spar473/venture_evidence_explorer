"""Read-only dossier graph views and lossless research exports.

Research records are never projected into B0's product-description corpus.
"""
import csv
import io
import json
import hashlib
from functools import wraps
from collections import defaultdict

NAMESPACE = 'research:0.2.1'
COLLECTION_KEYS = {
    'subjects':'subject_id','parties':'party_id','sources':'source_id',
    'observations':'observation_id','events':'event_id','event_reports':'report_id',
    'unknowns':'unknown_id','proposed_annotations':'annotation_id',
    'readiness':'readiness_id','reconciliation_cases':'case_id',
    'access_gaps':'gap_id','review_events':'review_event_id',
}
EXPORT_NAMES = (*COLLECTION_KEYS, 'requirements', 'conclusions', 'identity_mappings', 'date_intervals')


def read_consistently(function):
    @wraps(function)
    def wrapped(conn,*args,**kwargs):
        owns_snapshot=not conn.in_transaction
        if owns_snapshot:
            conn.execute('BEGIN')
        try:
            return function(conn,*args,**kwargs)
        finally:
            if owns_snapshot and conn.in_transaction:
                conn.execute('ROLLBACK')
    return wrapped


def _record_imports(conn,packet_sha256=None):
    sql='SELECT r.record_id,r.packet_sha256 FROM research_import_records r JOIN research_imports i ON i.namespace=r.namespace AND i.packet_sha256=r.packet_sha256 WHERE r.namespace=?'
    params=[NAMESPACE]
    if packet_sha256:
        sql+=' AND r.packet_sha256=?'; params.append(packet_sha256)
    sql+=' ORDER BY i.rowid,r.record_id'
    values=defaultdict(list)
    for row in conn.execute(sql,params):
        values[row['record_id']].append(row['packet_sha256'])
    return values


def _records(conn,packet_sha256=None):
    result={name:[] for name in COLLECTION_KEYS}
    if packet_sha256:
        sql='SELECT r.collection,r.record_json FROM research_records r JOIN research_import_records i ON i.namespace=r.namespace AND i.record_id=r.record_id WHERE r.namespace=? AND i.packet_sha256=? ORDER BY r.collection,r.record_id'
        params=(NAMESPACE,packet_sha256)
    else:
        sql='SELECT collection,record_json FROM research_records WHERE namespace=? ORDER BY collection,record_id'
        params=(NAMESPACE,)
    for row in conn.execute(sql,params):
        if row['collection'] in result:
            result[row['collection']].append(json.loads(row['record_json']))
    return result


def _context(conn, subject_id=None, packet_sha256=None):
    sql='SELECT i.packet_sha256,i.metadata_json FROM research_imports i'
    params=[NAMESPACE]
    if subject_id:
        sql+=' JOIN research_import_records r ON r.namespace=i.namespace AND r.packet_sha256=i.packet_sha256 WHERE i.namespace=? AND r.record_id=?'
        params.append(subject_id)
    else:
        sql+=' WHERE i.namespace=?'
    if packet_sha256:
        sql+=' AND i.packet_sha256=?'; params.append(packet_sha256)
    sql+=' ORDER BY i.rowid DESC LIMIT 1'
    row=conn.execute(sql,params).fetchone()
    return (row['packet_sha256'],json.loads(row['metadata_json'])) if row else (None,None)


def _subject_member(record, subject_id):
    return record.get('subject_id')==subject_id or subject_id in record.get('subject_ids',[])


@read_consistently
def subjects(conn,q='',review_state='',limit=25,offset=0,packet_sha256=None):
    records=_records(conn,packet_sha256)
    total_subjects=len(records['subjects'])
    record_imports=_record_imports(conn,packet_sha256)
    items=[]
    for subject in records['subjects']:
        if q.strip().casefold() not in subject['display_name'].casefold():
            continue
        if review_state and subject['review']['state']!=review_state:
            continue
        sid=subject['subject_id']
        items.append(dict(namespace=NAMESPACE,subject_id=sid,display_name=subject['display_name'],subject_kind=subject['subject_kind'],identity_link_status=subject['identity_link_status'],proposed_application_id=subject['proposed_application_id'],review_state=subject['review']['state'],observation_count=sum(r['subject_id']==sid for r in records['observations']),event_candidate_count=sum(r['subject_id']==sid for r in records['events']),unknown_count=sum(r['subject_id']==sid for r in records['unknowns']),open_case_count=sum(_subject_member(r,sid) and r['status']=='open' for r in records['reconciliation_cases']),packet_digest=record_imports[sid][-1]))
    items.sort(key=lambda r:(r['display_name'].casefold(),r['subject_id']))
    return dict(items=items[offset:offset+limit],total=len(items),total_subjects=total_subjects,limit=limit,offset=offset)


def _references(value):
    if isinstance(value,str):
        yield value
    elif isinstance(value,list):
        for item in value:
            yield from _references(item)
    elif isinstance(value,dict):
        for item in value.values():
            yield from _references(item)


def _closure(records,subject_id):
    """Root membership, then exact-ID references; do not infer identity matches.

    Cross-subject questions retain their full evidence lineage. A referenced
    second subject does not cause all of that subject's unrelated rows to enter.
    """
    indexed={row[COLLECTION_KEYS[name]]:(name,row) for name,values in records.items() for row in values}
    nested={}
    for ready in records['readiness']:
        for row in [*ready['requirements'],*ready['supported_conclusions']]:
            nested[row.get('requirement_id',row.get('conclusion_id'))]=ready['readiness_id']
    selected={key for key,(name,row) in indexed.items() if _subject_member(row,subject_id) or (name=='subjects' and key==subject_id)}
    while True:
        previous=len(selected)
        refs=set()
        for key in selected:
            refs.update(_references(indexed[key][1]))
        selected.update(ref for ref in refs if ref in indexed)
        selected.update(nested[ref] for ref in refs if ref in nested)
        for row in records['review_events']:
            if row['target_id'] in selected or nested.get(row['target_id']) in selected:
                selected.add(row['review_event_id'])
        if len(selected)==previous:
            break
    return {name:[row for row in values if row[COLLECTION_KEYS[name]] in selected] for name,values in records.items()}


def _identity_mapping(conn,subject_id):
    row=conn.execute('SELECT * FROM research_identity_mappings WHERE namespace=? AND subject_id=? ORDER BY rowid DESC LIMIT 1',(NAMESPACE,subject_id)).fetchone()
    if not row:
        return None
    result=dict(row)
    result['evidence_ids']=json.loads(result.pop('evidence_ids_json'))
    return result


def date_intervals(packet):
    from .research_adapter import research_time_interval
    values=[]
    def walk(value,path,collection,record_id):
        if isinstance(value,dict):
            if set(('value','precision','basis','unknown_reason'))<=set(value):
                interval=research_time_interval(value)
                values.append(dict(collection=collection,record_id=record_id,field_path=path,value=value['value'],basis=value['basis'],unknown_reason=value['unknown_reason'],**interval))
            else:
                for key,item in value.items():
                    walk(item,(path+'.' if path else '')+key,collection,record_id)
        elif isinstance(value,list):
            for index,item in enumerate(value):
                walk(item,path+'['+str(index)+']',collection,record_id)
    for name,key in COLLECTION_KEYS.items():
        for row in packet[name]:
            walk(row,'',name,row[key])
    return values


@read_consistently
def dossier(conn,subject_id,packet_sha256=None):
    records=_records(conn,packet_sha256)
    subject=next((r for r in records['subjects'] if r['subject_id']==subject_id),None)
    if subject is None:
        return None
    digest,metadata=_context(conn,subject_id,packet_sha256)
    packet=dict(metadata=metadata,**_closure(records,subject_id))
    record_imports=_record_imports(conn,packet_sha256)
    selected_ids={row[COLLECTION_KEYS[name]] for name,values in packet.items() if name!='metadata' for row in values}
    imported_hashes=sorted({h for key in selected_ids for h in record_imports[key]})
    graph_sha256=hashlib.sha256(json.dumps(packet,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    return dict(packet_view_kind='subject_reference_closure',is_standalone_import_packet=False,namespace=NAMESPACE,subject=subject,packet=packet,source_packet_sha256s=imported_hashes,graph_sha256=graph_sha256,identity_mapping=_identity_mapping(conn,subject_id),packet_digest=digest,date_intervals=date_intervals(packet),counts={name:len(rows) for name,rows in packet.items() if name!='metadata'},limitations=[
        'Research source checks are assistant extraction checks; they are not independent factual acceptance or relevance judgments.',
        'Linked cross-subject question evidence is retained. Counts refer to records in this graph, not a venture population or distinct completed transactions.',
        'Event records are candidates; targets are not occurrences and unresolved financing candidates must not be summed.',
        'Identity links remain proposed at brand/project scope; legal identity, payer and procurement authority remain separately unknown.',
        'Publication labels and research-as-of cutoffs do not establish historical archive availability.',
    ])


@read_consistently
def export_rows(conn,name,subject_id=None,packet_sha256=None):
    if name not in EXPORT_NAMES:
        raise KeyError(name)
    if subject_id:
        result=dossier(conn,subject_id,packet_sha256)
        if result is None:
            raise LookupError(subject_id)
        packet=result['packet']
        digest=result['packet_digest']
    else:
        digest,metadata=_context(conn,packet_sha256=packet_sha256)
        packet=dict(metadata=metadata,**_records(conn,packet_sha256))
    record_imports=_record_imports(conn,packet_sha256)
    if name=='identity_mappings':
        mappings=[_identity_mapping(conn,r['subject_id']) for r in packet['subjects'] if subject_id is None or r['subject_id']==subject_id]
        return [dict(m,namespace=NAMESPACE,packet_sha256=m['source_packet_sha256'],scope_subject_id=subject_id,review_state=m['state'],review_actor_role=m['actor_role'],decision_missing_reason='proposal_no_human_decision' if m['state']=='proposed' else None,record_json=json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':'))) for m in mappings if m]
    if name=='date_intervals':
        owners={r[COLLECTION_KEYS[collection]]:r for collection,values in packet.items() if collection!='metadata' for r in values}
        projections=[]
        for row in date_intervals(packet):
            owner=owners[row['record_id']]
            review=owner.get('review',{})
            hashes=record_imports.get(row['record_id'],[])
            projections.append(dict(row,namespace=NAMESPACE,packet_sha256=hashes[-1] if hashes else digest,source_packet_sha256s=hashes,scope_subject_id=subject_id,review_state=review.get('state'),review_actor_role=review.get('actor_role'),review_missing_reason=None if review else 'source_reference_has_no_acceptance_review',record_json=json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':'))))
        return projections
    if name in ('requirements','conclusions'):
        key='requirements' if name=='requirements' else 'supported_conclusions'
        values=[dict(row,readiness_id=ready['readiness_id']) for ready in packet['readiness'] for row in ready[key]]
    else:
        values=packet[name]
    source_map={s['source_id']:s for s in packet['sources']}
    output=[]
    for row in values:
        record=dict(row)
        record['scope_subject_id']=subject_id
        record['namespace']=NAMESPACE
        rid=row.get(COLLECTION_KEYS.get(name,''),row.get('requirement_id',row.get('conclusion_id')))
        hashes=record_imports.get(rid,[])
        record['packet_sha256']=hashes[-1] if hashes else digest
        record['source_packet_sha256s']=hashes
        record['record_json']=json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':'))
        review=row.get('review',{})
        record.update(review_state=review.get('state'),review_actor_role=review.get('actor_role'),review_checked_on=review.get('checked_on'),review_rationale=review.get('rationale'),acceptance_review_id=review.get('acceptance_review_id'))
        if row.get('source_id') in source_map:
            source=source_map[row['source_id']]
            record.update(source_url=source['url'],publisher=source['publisher'],publisher_role=source['publisher_role'],access_status=source['access_status'],retrieved_on=source['retrieved_on'],publication_precision=source['published_time']['precision'],publication_value=source['published_time']['value'])
        money=row.get('money')
        if money:
            record.update(amount=money['amount'],currency=money['currency']['value'],currency_unknown_reason=money['currency']['unknown_reason'],money_scope=money['scope'],unit=money['unit'],billing_interval=money['billing_interval'],amount_qualifier=money['qualifier'])
        for field in ('published_time','updated_time','effective_time','context_time','target_time','occurrence_time','reported_occurrence_time','reported_target_time'):
            if field in row:
                from .research_adapter import research_time_interval
                value=row[field]
                interval=research_time_interval(value)
                record.update({field+'_'+k:v for k,v in dict(value=value['value'],basis=value['basis'],unknown_reason=value['unknown_reason'],**interval).items()})
        output.append(record)
    return output


def export_csv(conn,name,subject_id=None,packet_sha256=None):
    records=export_rows(conn,name,subject_id,packet_sha256)
    # Stable ID and provenance columns first; nested originals remain JSON cells.
    leading=['namespace','packet_sha256',COLLECTION_KEYS.get(name,{'requirements':'requirement_id','conclusions':'conclusion_id','identity_mappings':'mapping_id'}.get(name,'record_id'))]
    columns=list(dict.fromkeys(leading+sorted({key for row in records for key in row})))
    output=io.StringIO(newline='')
    writer=csv.DictWriter(output,fieldnames=columns)
    writer.writeheader()
    for row in records:
        normalized={}
        for key,value in row.items():
            if isinstance(value,(dict,list)):
                value=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
            if isinstance(value,str) and value.startswith(('=','+','-','@','\t','\r')):
                value="'"+value
            normalized[key]=value
        writer.writerow(normalized)
    return output.getvalue()


def raw_packet(conn,packet_sha256):
    row=conn.execute('SELECT raw_bytes FROM research_imports WHERE namespace=? AND packet_sha256=?',(NAMESPACE,packet_sha256)).fetchone()
    return row['raw_bytes'] if row else None
