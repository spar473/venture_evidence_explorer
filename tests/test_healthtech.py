"""Healthtech pilot regressions; all mutations use disposable/synthetic fixtures."""
import copy
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from backend.database import ROOT, connect
from backend.ingestion import load_seed
from backend.main import create_app
from backend.research_adapter import EXAMPLE, dry_run_research, import_research
from backend.research_validation import validate_research_packet
from backend.healthtech import (SELECTION_PATH, Selections, HealthtechComparison,
    compare_healthtech, evidence_eligible, time_proves_by)
from backend.retrieval import compare

PACKET = ROOT / 'research/healthtech-pilot/packet.json'
AS_OF = '2026-11-19'
MRI = 'subj_ht_mri'


def snapshot(path):
    with sqlite3.connect(path) as conn:
        return {r[0]: conn.execute('SELECT * FROM "' + r[0] + '" ORDER BY rowid').fetchall()
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}


@pytest.fixture
def pilot(tmp_path):
    db = tmp_path / 'pilot.sqlite'
    load_seed(db)
    import_research(db, EXAMPLE, as_of=AS_OF)
    import_research(db, PACKET, as_of=AS_OF)
    return db


def test_packet_dry_run_idempotence_and_existing_corpus_preserved(tmp_path):
    packet = json.loads(PACKET.read_bytes())
    counts = validate_research_packet(packet, AS_OF)
    assert counts['subjects'] == 3 and counts['observations'] == 24
    missing = tmp_path / 'not-created.sqlite'
    assert dry_run_research(PACKET, missing, as_of=AS_OF)['writes'] == 0
    assert not missing.exists()
    db = tmp_path / 'existing.sqlite'
    load_seed(db)
    import_research(db, EXAMPLE, as_of=AS_OF)
    before = snapshot(db)
    with connect(db) as conn:
        baseline = compare(conn, query='clinical images software surgical planning')
    before_bytes = db.read_bytes()
    dry = dry_run_research(PACKET, db, as_of=AS_OF)
    assert dry['status'] == 'valid_dry_run' and dry['writes'] == 0
    assert dry['accounting']['totals']['unsupported'] == 0
    assert db.read_bytes() == before_bytes and snapshot(db) == before
    applied = import_research(db, PACKET, as_of=AS_OF)
    after = snapshot(db)
    import_research(db, PACKET, as_of=AS_OF)
    assert snapshot(db) == after
    for table in ['ventures', 'sources', 'observations', 'awards', 'annotations']:
        assert after[table] == before[table]
    for row in before['research_records']:
        assert row in after['research_records']
    with connect(db) as conn:
        result = compare(conn, query='clinical images software surgical planning')
    assert result['results'] == baseline['results']
    assert applied['counts'] == counts


def test_two_pathways_have_provenance_and_distinct_later_reports(pilot):
    before = snapshot(pilot)
    client = TestClient(create_app(pilot))
    response = client.get(f'/api/research/subjects/{MRI}/comparisons', params={'as_of': AS_OF})
    assert response.status_code == 200, response.text
    result = response.json()
    assert HealthtechComparison.model_validate(result).model_dump() == result
    assert result['status'] == 'pathway_precedents'
    assert result['same_stage_assessment'] == 'abstain'
    assert [p['subject_id'] for p in result['peers']] == ['subj_ht_volpara', 'subj_ht_formus']
    assert all(p['subject_id'] != MRI and p['early_stage_anchor'] is None for p in result['peers'])
    assert hashlib.sha256(PACKET.read_bytes()).hexdigest() in result['source_packet_sha256s']
    for peer in result['peers']:
        assert peer['classification'] == 'pathway_precedent'
        assert peer['unknowns'] and peer['unresolved_cases']
        assert peer['readiness']['independent_relevance_judgment'] is False
        reference = {e['observation']['observation_id'] for e in peer['reference_evidence']}
        later = {e['observation']['observation_id'] for e in peer['later_evidence']}
        assert not reference & later
        for evidence in peer['reference_evidence'] + peer['later_evidence']:
            assert evidence['observation']['locator']
            assert evidence['source']['publisher'] and evidence['source']['url'].startswith('https://')
            assert evidence['source']['retrieved_on'] == AS_OF
    formus = result['peers'][1]
    reports = {e['observation']['observation_id']: e for e in formus['later_evidence']}
    assert reports['obs_ht_formus_reg23']['observation']['effective_time']['value'] == '2023-03-31'
    assert reports['obs_ht_formus_reg23']['source']['published_time']['value'] is None
    assert reports['obs_ht_formus_reg26']['observation']['effective_time']['value'] is None
    assert reports['obs_ht_formus_reg26']['source']['published_time']['value'] == '2026-05-22'
    assert any(c['case_id'] == 'case_ht_formus_clearance' and not c['aggregation_allowed'] for c in formus['unresolved_cases'])
    assert reports['obs_ht_formus_validation23']['observation']['source_relationship'] == 'company'
    assert reports['obs_ht_formus_validation23']['source']['publisher_role'] == 'regulator'
    assert snapshot(pilot) == before


def test_historical_and_sparse_subjects_abstain_without_leaking(pilot):
    client = TestClient(create_app(pilot))
    for cutoff in ['2010-10-07', '2022-02-02', '2026-11-18', AS_OF]:
        result = client.get(f'/api/research/subjects/{MRI}/comparisons', params={'as_of': cutoff, 'view': 'historical'}).json()
        assert result['status'] == 'abstain'
        assert result['subject_evidence'] == result['peers'] == []
        assert 'availability witness' in result['gaps'][0]
        assert 'K213272' not in json.dumps(result)
        assert 'acquisition' not in json.dumps(result)
    early = client.get(f'/api/research/subjects/{MRI}/comparisons', params={'as_of':'2026-11-18'}).json()
    assert early['peers'] == early['subject_evidence'] == []
    for sid in ['subj_quickmas', 'subj_rosterlab', 'subj_ht_formus']:
        result = client.get(f'/api/research/subjects/{sid}/comparisons', params={'as_of': AS_OF}).json()
        assert result['peers'] == [] and result['status'] == 'abstain'
        assert 'Shared healthcare wording alone' in result['gaps'][0]
    assert client.get('/api/research/subjects/missing/comparisons', params={'as_of':AS_OF}).status_code == 404
    for params in [{'as_of':'2026-02-30'}, {'as_of':AS_OF,'view':'guess'}, {}]:
        assert client.get(f'/api/research/subjects/{MRI}/comparisons', params=params).status_code == 422


def test_partial_date_upper_bound_and_future_evidence_exclusion():
    packet = json.loads(PACKET.read_bytes())
    observation = packet['observations'][0]
    source = next(s for s in packet['sources'] if s['source_id'] == observation['source_id'])
    assert evidence_eligible(observation, source, AS_OF, 'research')
    for key in ['published_time','updated_time']:
        s = copy.deepcopy(source)
        s[key] = dict(value='2026',precision='year',basis='Synthetic unresolved partial date.',unknown_reason=None)
        assert not evidence_eligible(observation, s, AS_OF, 'research')
    for key in ['context_time','effective_time']:
        o = copy.deepcopy(observation)
        o[key] = dict(value='2026-11',precision='month',basis='Synthetic partial date.',unknown_reason=None)
        assert not evidence_eligible(o, source, AS_OF, 'research')
    s = copy.deepcopy(source); s['retrieved_on'] = '2026-11-20'
    assert not evidence_eligible(observation, s, AS_OF, 'research')
    o = copy.deepcopy(observation); o['review']['checked_on'] = '2026-11-20'
    assert not evidence_eligible(o, source, AS_OF, 'research')
    for value, cutoff, expected in [('2026','2026-12-31',True),('2026','2026-11-19',False),('2026-02','2026-02-28',True),(None,AS_OF,False)]:
        precision = {4:'year',7:'month'}.get(len(value or ''),'unknown')
        assert time_proves_by(dict(value=value,precision=precision,basis='Synthetic.',unknown_reason=None if value else 'not_researched_this_pass'),cutoff) == expected
    # Even falsifying the boolean cannot replace a dated witness with a locator.
    s = copy.deepcopy(source); s['historical_availability_verified'] = True
    assert not evidence_eligible(observation, s, AS_OF, 'historical')


def test_selection_manifest_rejects_self_duplicates_and_excess_peers():
    original = json.loads(SELECTION_PATH.read_bytes())
    Selections.model_validate(original)
    for mutation in ['self','duplicate','excess']:
        value = copy.deepcopy(original)
        selection = value['selections'][0]
        if mutation == 'self': selection['peers'][0]['subject_id'] = selection['subject_id']
        elif mutation == 'duplicate': selection['peers'][1]['subject_id'] = selection['peers'][0]['subject_id']
        else: selection['peers'] *= 2
        with pytest.raises(ValidationError): Selections.model_validate(value)


def test_missing_or_future_basis_withholds_whole_claimed_analogy(pilot, monkeypatch):
    from backend import healthtech
    from backend.research_repository import dossier
    with connect(pilot) as conn:
        base = dossier(conn, MRI)
    for field in ['missing', 'future', 'partial']:
        graph = copy.deepcopy(base)
        o = next(o for o in graph['packet']['observations'] if o['observation_id']=='obs_ht_formus_validation23')
        if field == 'missing': graph['packet']['observations'].remove(o)
        elif field == 'future': o['review']['checked_on'] = '2026-11-20'
        else: o['context_time'] = dict(value='2026',precision='year',basis='Synthetic partial context.',unknown_reason=None)
        monkeypatch.setattr(healthtech, 'dossier', lambda *args: graph)
        with connect(pilot) as conn:
            result = compare_healthtech(conn, MRI, as_of=AS_OF)
        assert [p['subject_id'] for p in result['peers']] == ['subj_ht_volpara']
        assert result['gaps']


def test_extension_shares_stable_reference_records_and_all_projects_are_selectable(pilot):
    extension = ROOT/'research/healthtech-pilot/extension.json'
    before = snapshot(pilot)
    before_bytes = pilot.read_bytes()
    dry = dry_run_research(extension, pilot, as_of=AS_OF)
    assert dry['status'] == 'valid_dry_run' and dry['writes'] == 0
    assert pilot.read_bytes() == before_bytes
    import_research(pilot, extension, as_of=AS_OF)
    after = snapshot(pilot)
    import_research(pilot, extension, as_of=AS_OF)
    assert snapshot(pilot) == after
    for table in ['ventures','sources','observations','awards','annotations']:
        assert after[table] == before[table]
    assert all(row in after['research_records'] for row in before['research_records'])
    client = TestClient(create_app(pilot))
    directory = client.get('/api/research/subjects').json()
    assert directory['total_subjects'] == 10
    expected = {'subj_ht_neurofanos':['subj_ht_formus'], 'subj_ht_ivf':['subj_ht_formus'],
        'subj_ht_vistavision':['subj_ht_toku'], 'subj_ht_pulsemap':[]}
    for subject_id, peers in expected.items():
        record = next(s for s in directory['items'] if s['subject_id'] == subject_id)
        dossier = client.get('/api/research/subjects/'+subject_id).json()
        assert dossier['subject']['proposed_application_id'] and dossier['subject']['legal_name']['value'] is None
        assert dossier['packet']['observations'] and dossier['packet']['unknowns']
        result = client.get('/api/research/subjects/'+subject_id+'/comparisons',params={'as_of':AS_OF,'packet_sha256':record['packet_digest']}).json()
        assert [p['subject_id'] for p in result['peers']] == peers
        assert all(p['subject_id'] != subject_id for p in result['peers'])
    pulse = client.get('/api/research/subjects/subj_ht_pulsemap/comparisons',params={'as_of':AS_OF}).json()
    assert pulse['status']=='abstain' and 'measurement modality' in pulse['gaps'][0]
    neuro = client.get('/api/research/subjects/subj_ht_neurofanos').json()
    grant = next(o for o in neuro['packet']['observations'] if o['observation_id']=='obs_ht_neuro_grant')
    assert grant['money'] is None and grant['field']=='outcome'
    assert grant['effective_time']['value']=='2023-09' and grant['effective_time']['precision']=='month'
    assert 'research team' in grant['paraphrase'] and 'not a reported equity investment' in grant['paraphrase']
    assert not any(e['event_kind']=='financing' and e['subject_id']=='subj_ht_neurofanos' for e in neuro['packet']['events'])
    ivf = client.get('/api/research/subjects/subj_ht_ivf').json()
    assert ivf['subject']['proposed_application_id']=='v_ivf_tool'
    intention = next(o for o in ivf['packet']['observations'] if o['observation_id']=='obs_ht_ivf_evaluation_plan')
    assert intention['assertion_nature']=='intention_target' and intention['effective_time']['value'] is None


def test_disposable_demo_and_existing_evaluation_workflow_keep_human_fields_blank(tmp_path):
    import csv
    import importlib.util
    spec=importlib.util.spec_from_file_location('healthtech_demo',ROOT/'scripts/healthtech_demo.py')
    demo=importlib.util.module_from_spec(spec);spec.loader.exec_module(demo)
    output=tmp_path/'demo'
    summary=demo.prepare_demo(output)
    assert len(summary['imports'])==4
    before=snapshot(Path(summary['database']))
    with pytest.raises(ValueError,match='never replaced'): demo.prepare_demo(output)
    assert snapshot(Path(summary['database']))==before
    result=demo.export_evaluation(Path(summary['database']),output/'evaluation')
    assert result['status']=='not_evaluated' and result['tasks']==6
    research=json.loads((output/'evaluation/research-results.json').read_text())
    assert research['human_judgments']==research['manual_research_observations']==[]
    rows=list(csv.DictReader((output/'evaluation/research-review.csv').open()))
    assert len(rows)==10
    human_fields=['reviewer_id','relevance_grade','material_evidence_errors','rationale','supporting_observation_ids','reviewed_on','manual_research_minutes','useful_result_minutes']
    assert all(not row[field] for row in rows for field in human_fields)
    baseline=json.loads((output/'evaluation/lexical-results.json').read_text())
    assert baseline['status']=='not_evaluated' and baseline['reason']=='judgments_missing'
    assert baseline['coverage']['tasks_run']==6
    assert all(q['aggregate_metrics']['ndcg_at_3'] is None for q in baseline['queries'])
    sparse=next(r for r in research['results'] if r['query_id']=='ht_pulsemap')
    assert sparse['result']['peers']==[] and sparse['result']['status']=='abstain'


def test_possible_shared_identity_and_later_review_decisions_cannot_supply_a_peer(pilot, monkeypatch):
    from backend import healthtech
    from backend.research_repository import dossier
    with connect(pilot) as conn:
        base = dossier(conn, MRI)
    graph = copy.deepcopy(base)
    next(s for s in graph['packet']['subjects'] if s['subject_id']=='subj_ht_formus')['proposed_application_id'] = graph['subject']['proposed_application_id']
    monkeypatch.setattr(healthtech, 'dossier', lambda *args: graph)
    with connect(pilot) as conn:
        result = compare_healthtech(conn, MRI, as_of=AS_OF)
    assert [p['subject_id'] for p in result['peers']] == ['subj_ht_volpara']
    assert any('self-comparison' in gap for gap in result['gaps'])
    for target_type, target_id in [('observation','obs_ht_formus_validation23'),('readiness','ready_ht_mri_formus'),('conclusion','conclusion_ht_mri_formus_1'),('subject','subj_ht_formus')]:
        graph = copy.deepcopy(base)
        graph['packet']['review_events']=[dict(review_event_id='review_synthetic',target_type=target_type,target_id=target_id,actor_role='owner',reviewer_id='synthetic_test_fixture',decision='disputed',reviewed_on=AS_OF,rationale='Synthetic code regression only.')]
        with connect(pilot) as conn:
            result = compare_healthtech(conn, MRI, as_of=AS_OF)
        assert [p['subject_id'] for p in result['peers']] == ['subj_ht_volpara']
        # A future review cannot change the earlier recorded review state.
        graph['packet']['review_events'][0]['reviewed_on']='2026-11-20'
        with connect(pilot) as conn:
            result = compare_healthtech(conn, MRI, as_of=AS_OF)
        assert len(result['peers'])==2


def test_coverage_counts_openable_pairs_across_imports_and_reviews(tmp_path):
    db = tmp_path / 'coverage.sqlite'
    load_seed(db)
    client = TestClient(create_app(db))
    endpoint = '/api/research/healthtech/coverage'
    studies = PACKET.with_name('clinical-studies.json')

    def check_counts(expected_counts):
        response = client.get(endpoint)
        assert response.status_code == 200
        summary = response.json()
        counts = ('project_count', 'projects_with_peers', 'distinct_reference_count', 'pair_count')
        assert tuple(summary[key] for key in counts) == expected_counts
        for project in summary['projects']:
            path = f"/api/research/subjects/{project['subject_id']}/comparisons"
            result = client.get(path, params={'as_of': summary['as_of']}).json()
            assert project['peers'] == [
                {'subject_id': peer['subject_id'], 'display_name': peer['display_name']}
                for peer in result['peers']]
        return summary

    check_counts((0, 0, 0, 0))
    # The clinical packet can arrive before the original packets.
    import_research(db, studies, as_of=AS_OF)
    check_counts((3, 3, 2, 3))
    import_research(db, PACKET, as_of=AS_OF)
    import_research(db, PACKET.with_name('extension.json'), as_of=AS_OF)
    initial = check_counts((5, 4, 5, 8))
    import_research(db, studies, as_of=AS_OF)
    assert check_counts((5, 4, 5, 8)) == initial
    mri = f'/api/research/subjects/{MRI}/comparisons'
    pinned = client.get(mri, params={'as_of': AS_OF, 'packet_sha256': hashlib.sha256(studies.read_bytes()).hexdigest()})
    assert [p['subject_id'] for p in pinned.json()['peers']] == ['subj_ht_wellumio']
    assert client.get(mri, params={'as_of': '2026-11-18'}).json()['peers'] == []

    packet = json.loads(studies.read_bytes())
    packet['review_events'].append(dict(review_event_id='review_synthetic_signal', target_type='observation',
        target_id='obs_ht_well_signal', actor_role='owner', reviewer_id='synthetic_test_fixture',
        decision='disputed', reviewed_on=AS_OF, rationale='Synthetic regression fixture.'))
    review_packet = tmp_path / 'review.json'
    review_packet.write_text(json.dumps(packet))
    import_research(db, review_packet, as_of=AS_OF)
    # One shared disputed result withholds both Wellumio pairs.
    check_counts((5, 4, 4, 6))
