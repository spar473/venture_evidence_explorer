"""Query boundaries and pagination, independent of evidence assertions."""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from backend.database import connect
from backend.main import create_app
from backend.repository import browse
from backend.retrieval import compare
from scripts.bootstrap import load_seed


@pytest.fixture
def database(tmp_path):
    path = tmp_path/'queries.sqlite'
    load_seed(path)
    return path


def test_directory_is_bounded_summaries_and_totals(database):
    client = TestClient(create_app(database))
    pages = [client.get('/api/ventures', params={'limit':3,'offset':i}).json() for i in (0,3,6,9,12)]
    assert [len(p['items']) for p in pages] == [3,3,3,1,0]
    assert all(p['total']==p['filtered_ventures']==p['total_ventures']==10 for p in pages)
    ids = [v['venture_id'] for p in pages for v in p['items']]
    assert len(ids)==len(set(ids))==10
    for p in pages:
        for item in p['items']:
            assert 'observations' not in item and 'proposed_annotations' not in item
            assert item['award_count']==len(item['recognitions'])
            assert isinstance(item['connection_types'],list)
    assert client.get('/api/ventures?programme=velocity_ideas&year=2026&limit=1').json()['total']==2
    for params in ('limit=0','limit=101','offset=-1'):
        assert client.get('/api/ventures?'+params).status_code==422


def test_directory_query_count_does_not_hydrate_profiles(database):
    with connect(database) as conn:
        statements=[]
        conn.set_trace_callback(statements.append)
        with patch('backend.repository.detail_many',side_effect=AssertionError('unexpected full profile hydration')):
            result = browse(conn,limit=100)
        assert len(result['items'])==10
        selects = [s for s in statements if s.lstrip().upper().startswith('SELECT')]
        assert len(selects)==5


def test_compare_hydrates_only_shortlist(database):
    import backend.retrieval as retrieval
    original = retrieval.detail_many
    hydrated=[]
    def track(conn, ids):
        hydrated.extend(ids)
        return original(conn,ids)
    with connect(database) as conn, patch('backend.retrieval.detail_many',side_effect=track):
        result=compare(conn,query='clinical images software surgical planning')
    assert hydrated==[r['venture']['venture_id'] for r in result['results']]
    assert len(hydrated)==2


def test_every_json_endpoint_has_a_typed_response_contract(database):
    schema=create_app(database).openapi()
    for path,methods in schema['paths'].items():
        if path.startswith('/api/') and not path.endswith('.csv'):
            for operation in methods.values():
                response=operation['responses']['200']['content']['application/json']['schema']
                assert '$ref' in response, (path,response)


def test_queries_remain_bounded_on_large_temporary_corpus(database):
    """A 1,010-identity synthetic fixture must not hydrate 1,010 profiles."""
    import copy
    import json
    import sqlite3
    from pathlib import Path
    from scripts.bootstrap import ROOT
    original = json.loads((ROOT/'data/seed.json').read_text())
    payload = copy.deepcopy(original)
    prototype = original['ventures'][0]
    observation = next(o for o in original['observations'] if o['field']=='product_description')
    for index in range(1000):
        vid = f'test_synthetic_{index:04d}'
        payload['ventures'].append(dict(prototype, venture_id=vid, display_name=f'Synthetic fixture {index:04d}', aliases=[]))
        payload['observations'].append(dict(observation,venture_id=vid,observation_id=vid+'_product',value_text='clinical image software surgery planning'))
    source = Path(database).with_suffix('.json')
    source.write_text(json.dumps(payload))
    with connect(database) as conn:
        statements=[]
        conn.set_trace_callback(statements.append)
        browse(conn)
        small_directory=sum(s.lstrip().upper().startswith('SELECT') for s in statements)
        statements.clear()
        compare(conn,query='clinical images software surgical planning')
        small_compare=sum(s.lstrip().upper().startswith('SELECT') for s in statements)
    load_seed(database,source)
    with connect(database) as conn:
        statements=[]
        conn.set_trace_callback(statements.append)
        page=browse(conn,limit=25,offset=500)
        large_directory=sum(s.lstrip().upper().startswith('SELECT') for s in statements)
        statements.clear()
        with patch('backend.retrieval.detail_many',wraps=__import__('backend.repository',fromlist=['detail_many']).detail_many) as hydration:
            result=compare(conn,query='clinical images software surgical planning')
        large_compare=sum(s.lstrip().upper().startswith('SELECT') for s in statements)
        table_count=conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()[0]
    assert page['total']==1010 and len(page['items'])==25
    assert small_directory==large_directory==5
    assert small_compare==large_compare
    assert large_compare <= table_count+20 # fixed hydration/policy overhead plus full-store digest per table
    assert len(hydration.call_args.args[1])==len(result['results'])==3


def test_historical_cohort_filter_needs_its_own_source_availability(database):
    import sqlite3
    from backend.repository import candidate_ids
    with sqlite3.connect(database) as conn:
        conn.execute("INSERT INTO source_availability VALUES ('src_100k_2025','2025-11-17','Synthetic fixture dated snapshot')")
        conn.execute("INSERT INTO awards VALUES ('synthetic_future_recognition','v_ivf_tool','velocity_ideas',2026,'Synthetic fixture',NULL,NULL,'src_ideas_2026','Fixture passage','source_checked_owner_review_pending')")
    with connect(database) as conn:
        assert 'v_ivf_tool' in candidate_ids(conn,programme='velocity_ideas',year=2026)
        assert 'v_ivf_tool' not in candidate_ids(conn,programme='velocity_ideas',year=2026,cutoff='2026-11-18')
    with sqlite3.connect(database) as conn:
        conn.execute("INSERT INTO source_availability VALUES ('src_ideas_2026','2026-11-17','Synthetic fixture dated snapshot')")
    with connect(database) as conn:
        assert 'v_ivf_tool' in candidate_ids(conn,programme='velocity_ideas',year=2026,cutoff='2026-11-18')
