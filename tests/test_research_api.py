"""Read-only pilot API; all factual fixtures come from the supplied packet."""
import csv
import hashlib
import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from backend.database import ROOT
from backend.main import create_app
from backend.research_contracts import ResearchPacket
from backend.research_repository import EXPORT_NAMES
from scripts.bootstrap import load_seed

PACKET_PATH=ROOT/'research/framework-v0.2.1/Two_Dossier_Research_Example.json'


@pytest.fixture
def pilot(tmp_path):
    from backend.research_adapter import import_research
    db=tmp_path/'pilot.sqlite'
    load_seed(db)
    import_research(db,PACKET_PATH,as_of='2026-11-18')
    return TestClient(create_app(db)),db,json.loads(PACKET_PATH.read_text())


def test_authoritative_schema_response_models_round_trip_every_field():
    packet=json.loads(PACKET_PATH.read_text())
    assert ResearchPacket.model_validate(packet).model_dump()==packet
    bad=dict(packet,unexpected_field='must not disappear')
    with pytest.raises(ValueError):
        ResearchPacket.model_validate(bad)


def test_two_dossier_summaries_filters_and_unknown_identity(pilot):
    client,_,packet=pilot
    response=client.get('/api/research/subjects')
    assert response.status_code==200
    result=response.json()
    assert result['total']==result['total_subjects']==2
    assert {row['subject_id'] for row in result['items']}=={'subj_rosterlab','subj_quickmas'}
    for row in result['items']:
        assert row['namespace']=='research:0.2.1'
        assert row['identity_link_status']=='proposed_unresolved'
        assert row['review_state']=='source_checked'
        assert row['observation_count']==sum(o['subject_id']==row['subject_id'] for o in packet['observations'])
    assert client.get('/api/research/subjects?q=roster').json()['items'][0]['subject_id']=='subj_rosterlab'
    assert client.get('/api/research/subjects?review_state=accepted').json()['total']==0
    assert client.get('/api/research/subjects?review_state=source_checked&limit=1').json()['total']==2
    assert len(client.get('/api/research/subjects?offset=1&limit=1').json()['items'])==1
    assert client.get('/api/research/subjects?namespace=other').status_code==422
    assert client.get('/api/research/subjects?limit=0').status_code==422
    assert client.get('/api/research/subjects?review_state=invented').status_code==422
    for sid in ('subj_rosterlab','subj_quickmas'):
        body=client.get('/api/research/subjects/'+sid).json()
        assert body['subject']==next(s for s in packet['subjects'] if s['subject_id']==sid)
        mapping=body['identity_mapping']
        assert mapping['state']=='proposed' and mapping['scope']=='brand_project_only'
        assert mapping['actor_id'] is None and mapping['decided_on'] is None
        assert mapping['legal_identity_state']=='unresolved'
        assert body['subject']['legal_name']['value'] is None
        assert body['subject']['registration_id']['value'] is None


def test_dossier_graph_is_lossless_with_cross_subject_lineage(pilot):
    client,_,packet=pilot
    for sid in ('subj_rosterlab','subj_quickmas'):
        response=client.get('/api/research/subjects/'+sid)
        assert response.status_code==200
        body=response.json()
        graph=body['packet']
        for name in packet:
            if name=='metadata':
                assert graph[name]==packet[name]
                continue
            for record in graph[name]:
                assert record in packet[name],(name,record)
        observations={o['observation_id']:o for o in graph['observations']}
        sources={s['source_id']:s for s in graph['sources']}
        events={e['event_id']:e for e in graph['events']}
        for observation in observations.values():
            assert observation['source_id'] in sources
        for report in graph['event_reports']:
            assert report['event_id'] in events
            assert report['source_id'] in sources
            for oid in report['observation_ids']:
                observation=observations[oid]
                assert observation['source_id']==report['source_id']
                assert observation['subject_id']==report['subject_id']
                assert observation['source_relationship']==report['source_relationship']
                assert observation['assertion_nature']==report['assertion_nature']
        for row in graph['readiness']:
            assert not row['independent_relevance_judgment']
            for conclusion in row['supported_conclusions']:
                assert set(conclusion['source_ids'])=={observations[oid]['source_id'] for oid in conclusion['basis_observation_ids']}
                assert conclusion['review']['state']=='source_checked'
        assert graph['metadata']['accepted_records_count']==0
        assert graph['review_events']==[]


def test_target_occurrence_money_and_financing_limits_stay_explicit(pilot):
    client,_,_=pilot
    graph=client.get('/api/research/subjects/subj_quickmas').json()
    targets=[e for e in graph['packet']['events'] if e['scenario']=='target']
    assert targets and any(e['target_time']['value']=='2025' for e in targets)
    for target in targets:
        assert target['occurrence_time']['value'] is None
        assert target['event_state']!='completed'
        intervals=[d for d in graph['date_intervals'] if d['record_id']==target['event_id'] and d['field_path']=='target_time']
        assert intervals[0]['precision']=='year'
        assert intervals[0]['value']=='2025'
        assert intervals[0]['lower_bound']=='2025-01-01' and intervals[0]['upper_bound']=='2025-12-31'
    roster=client.get('/api/research/subjects/subj_rosterlab').json()['packet']
    prices=[o for o in roster['observations'] if o['field']=='advertised_price']
    assert prices and all(o['money']['currency']['value'] is None for o in prices)
    assert all(o['money']['currency']['unknown_reason'] for o in prices)
    rounds=[e for e in roster['events'] if e['event_kind']=='financing']
    assert len(rounds)==2 and all(e['identity_resolution']=='unresolved_possible_duplicate' for e in rounds)
    duplicate=next(c for c in roster['reconciliation_cases'] if c['case_kind']=='possible_duplicate_event')
    assert duplicate['status']=='open' and not duplicate['aggregation_allowed']
    assert len(duplicate['event_ids'])==2


def test_analytical_exports_keep_raw_fields_provenance_and_missingness(pilot):
    client,_,packet=pilot
    collection_ids={
        'subjects':'subject_id','parties':'party_id','sources':'source_id',
        'observations':'observation_id','events':'event_id','event_reports':'report_id',
        'unknowns':'unknown_id','proposed_annotations':'annotation_id',
        'readiness':'readiness_id','reconciliation_cases':'case_id','access_gaps':'gap_id','review_events':'review_event_id',
    }
    for name in EXPORT_NAMES:
        response=client.get('/api/research/exports/'+name+'.csv')
        assert response.status_code==200
        rows=list(csv.DictReader(io.StringIO(response.text)))
        if name in collection_ids:
            key=collection_ids[name]
            assert len(rows)==len(packet[name])
            assert len({row[key] for row in rows})==len(rows)
            for row in rows:
                raw=json.loads(row['record_json'])
                assert raw==next(r for r in packet[name] if r[key]==row[key])
                assert row['namespace']=='research:0.2.1'
    observations=list(csv.DictReader(io.StringIO(client.get('/api/research/exports/observations.csv').text)))
    price=next(r for r in observations if r['field']=='advertised_price')
    assert json.loads(price['money'])['currency']['value'] is None
    assert price['source_url'].startswith('https://')
    assert price['review_state']=='source_checked'
    assert 'effective_time_precision' in price and 'target_time_unknown_reason' in price
    unknowns=list(csv.DictReader(io.StringIO(client.get('/api/research/exports/unknowns.csv').text)))
    assert all(row['value']=='' and row['reason'] for row in unknowns)
    events=list(csv.DictReader(io.StringIO(client.get('/api/research/exports/events.csv').text)))
    target=next(row for row in events if row['scenario']=='target')
    assert target['target_time_value']=='2025' and target['target_time_precision']=='year'
    assert target['occurrence_time_value']=='' and target['occurrence_time_precision']=='unknown'
    assert not any('total_funding' in key for row in events for key in row)


def test_filtered_export_keeps_linked_question_evidence_and_full_raw_download(pilot):
    client,_,packet=pilot
    dossier=client.get('/api/research/subjects/subj_quickmas').json()
    filtered=client.get('/api/research/exports/observations.csv?subject_id=subj_quickmas')
    rows=list(csv.DictReader(io.StringIO(filtered.text)))
    assert {row['observation_id'] for row in rows}=={o['observation_id'] for o in dossier['packet']['observations']}
    assert all(row['scope_subject_id']=='subj_quickmas' for row in rows)
    assert any(row['subject_id']=='subj_rosterlab' for row in rows) # Supporting cross-subject comparisons are not orphaned.
    digest=dossier['packet_digest']
    original=client.get('/api/research/packets/'+digest+'.json')
    assert original.content==PACKET_PATH.read_bytes()
    assert hashlib.sha256(original.content).hexdigest()==digest
    assert original.json()==packet
    selected=client.get('/api/research/subjects?packet_sha256='+digest).json()
    assert selected['total']==2
    assert client.get('/api/research/subjects?packet_sha256=missing').json()['total']==0


def test_research_reads_do_not_duplicate_records_and_reject_unknown_routes(pilot):
    import sqlite3
    client,db,_=pilot
    def snapshot():
        with sqlite3.connect(db) as conn:
            return {name:conn.execute('SELECT * FROM '+name+' ORDER BY 1,2').fetchall() for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    before=snapshot()
    for _ in range(2):
        client.get('/api/research/subjects')
        client.get('/api/research/subjects/subj_rosterlab')
        client.get('/api/research/exports/events.csv')
    assert snapshot()==before
    assert client.get('/api/research/subjects/missing').status_code==404
    assert client.get('/api/research/exports/missing.csv').status_code==404
    assert client.get('/api/research/exports/observations.csv?subject_id=missing').status_code==404
    assert client.get('/api/research/packets/missing.json').status_code==404
    assert client.get('/api/research/subjects?q=%27%20OR%201=1--').json()['total']==0
    assert client.get('/api/research/exports/observations.csv?subject_id=%27%20OR%201=1--').status_code==404


def test_supplied_brand_mapping_resolution_remains_separate_from_legal_and_fact_review(pilot,tmp_path):
    from backend.research_adapter import import_research,_proposal_id
    client,db,packet=pilot
    document={'format_version':'identity-mappings:1','decisions':[{
        'mapping_id':'synthetic_api_mapping','subject_id':'subj_rosterlab','venture_id':'v_rosterlab',
        'state':'resolved','scope':'brand_project_only','actor_role':'owner',
        'actor_id':'Synthetic fixture only; not a real decision','decided_on':'2026-11-18',
        'evidence_ids':['obs_rl_problem'],'rationale':'Synthetic API audit fixture only',
        'supersedes_mapping_id':_proposal_id('subj_rosterlab')}]}
    sidecar=tmp_path/'synthetic-mapping.json';sidecar.write_text(json.dumps(document))
    import_research(db,PACKET_PATH,as_of='2026-11-18',mapping_decisions_path=sidecar)
    body=client.get('/api/research/subjects/subj_rosterlab').json()
    assert body['identity_mapping']['state']=='resolved'
    assert body['identity_mapping']['legal_identity_state']=='unresolved'
    assert body['identity_mapping']['decision_document_sha256']
    assert body['subject']['identity_link_status']=='proposed_unresolved' # original research proposal preserved
    assert body['subject']['legal_name']['value'] is None
    assert body['packet']['metadata']['accepted_records_count']==0
    assert not body['packet']['review_events']
    assert not client.post('/api/compare',json={'query':'clinical image software','policy':'accepted'}).json()['results']
