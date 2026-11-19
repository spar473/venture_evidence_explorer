import copy
import json
import sqlite3

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.ingestion import load_seed
from backend.main import create_app
from backend.reference_pool import EventDate, PoolPacket, coverage, import_pool, outcome_status


def sample():
    return {
        'format_version':'nz-reference-pool:1','kind':'fixture','as_of':'2026-11-20',
        'companies':[dict(company_id='test_company',display_name='Synthetic company',sector='Testing',
            origin_source_id='entry_source',origin_passage='Fixture opening',entry_event_id='seed_event',
            entry_basis='Test-only earliest institutional seed',aliases=['Synthetic brand'],
            follow_up=dict(searched_on='2026-11-20',scope='Synthetic fixture only.',activity_event_id='seed_event'))],
        'sources':[dict(source_id='entry_source',title='Synthetic seed release',publisher='Test author',
            url='https://example.org/seed',kind='press_release',published_on='2020-02-29',retrieved_on='2026-11-20')],
        'witnesses':[dict(witness_id='entry_date',source_id='entry_source',kind='publisher_dated',
            available_on='2020-02-29',url='https://example.org/seed',locator='Version dateline')],
        'events':[dict(event_id='seed_event',company_id='test_company',kind='seed',
            date={'value':'2020-02-29','precision':'day'},date_basis='completed_at_announcement',
            source_id='entry_source',passage='Opening',claim='Synthetic raise',round_label='Seed round',
            institutional_investor='Synthetic fund',instrument='priced_equity')],
        'snapshots':[dict(snapshot_id='entry_snapshot',company_id='test_company',stage_event_id='seed_event',
            as_of='2020-02-29',features=[dict(name='description',value='Synthetic description',
                source_id='entry_source',witness_id='entry_date',passage='Opening')])],
    }


def test_old_date_on_mutable_page_does_not_witness_snapshot():
    raw = sample()
    raw['sources'][0]['kind'] = 'portfolio_page'
    with pytest.raises(ValidationError, match='dated version'):
        PoolPacket.model_validate(raw)
    raw['witnesses'] = []
    with pytest.raises(ValidationError, match='source-version evidence'):
        PoolPacket.model_validate(raw)
    raw['witnesses'] = [dict(witness_id='entry_date',source_id='entry_source',kind='archived_capture',
        captured_at='2020-03-01T00:00:00Z',available_on='2020-03-01',url='https://archive.example.org/20200301',
        locator='Synthetic archived dateline')]
    with pytest.raises(ValidationError, match='on or before'):
        PoolPacket.model_validate(raw)
    raw['witnesses'][0].update(captured_at='2020-02-29T00:00:00Z',available_on='2020-02-29')
    assert coverage(PoolPacket.model_validate(raw))['sources']['archived_capture'] == 1


def test_revised_publisher_version_cannot_witness_earlier_cutoff():
    raw = sample()
    raw['sources'][0]['revised_on'] = '2021-01-01'
    with pytest.raises(ValidationError, match='dated version'):
        PoolPacket.model_validate(raw)
    raw['witnesses'][0]['available_on'] = '2021-01-01'
    with pytest.raises(ValidationError, match='on or before'):
        PoolPacket.model_validate(raw)


def test_closure_and_partial_outcomes_are_evidence_required():
    raw = sample()
    raw['companies'][0]['follow_up'] = None
    closure = dict(raw['events'][0],event_id='closure',kind='closed_register_removal',
        date={'value':'2021-Q2','precision':'quarter'},date_basis='reported_occurrence',
        source_id='closure_source',round_label=None,closure_evidence='register_removal')
    raw['events'].append(closure)
    raw['sources'].append(dict(raw['sources'][0],source_id='closure_source',kind='news_article',
        published_on='2021-07-15',url='https://example.org/closure'))
    with pytest.raises(ValidationError, match='Closure requires'):
        PoolPacket.model_validate(raw)
    raw['sources'][-1]['kind'] = 'registry_record'
    packet = PoolPacket.model_validate(raw)
    assert outcome_status(packet.companies[0],packet.events)[0] == 'closed_before_outcome'
    assert EventDate(value='2020-Q1',precision='quarter').bounds() == ('2020-01-01','2020-03-31')
    raw['events'].append(dict(closure,event_id='round_a',kind='series_a',round_label='Series A',
        closure_evidence=None,date={'value':'2021-04-03','precision':'day'}))
    packet = PoolPacket.model_validate(raw)
    assert outcome_status(packet.companies[0],packet.events)[0] == 'unknown'
    raw['events'][-1]['round_label'] = 'Pre-Series A'
    with pytest.raises(ValidationError, match='letter-stage'):
        PoolPacket.model_validate(raw)


def test_fixture_dry_run_idempotent_and_no_rates(tmp_path):
    data = tmp_path/'fixture.json'
    data.write_text(json.dumps(sample()))
    db = tmp_path/'pool.sqlite'
    assert import_pool(data,db)['writes'] == 0 and not db.exists()
    load_seed(db)
    before = db.read_bytes()
    assert import_pool(data,db)['writes'] == 0 and db.read_bytes() == before
    applied = import_pool(data,db,apply=True)
    assert applied['status'] == 'applied'
    assert applied['coverage']['statuses']['lost_to_follow_up'] == 1
    after = db.read_bytes()
    assert import_pool(data,db,apply=True)['status'] == 'already_applied'
    assert db.read_bytes() == after
    with sqlite3.connect(db) as conn:
        assert conn.execute('PRAGMA foreign_key_check').fetchall() == []
        assert conn.execute('SELECT raw_bytes FROM pool_imports').fetchone()[0] == data.read_bytes()
        with pytest.raises(sqlite3.IntegrityError, match='immutable'):
            conn.execute("UPDATE pool_witnesses SET available_on='2025-01-01'")
    client = TestClient(create_app(db))
    for route in ('rates','survival','cumulative-incidence'):
        assert client.get('/api/reference-pool/'+route).status_code == 404
    raw = copy.deepcopy(sample())
    raw['kind'] = 'cohort'
    with pytest.raises(ValidationError):
        PoolPacket.model_validate(raw)
