"""Synthetic fixtures only: transaction, typed input and historical policy."""
import copy
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest
from backend import database
from backend.database import connect, migrate
from backend.evidence_policy import enrich_observations, select_observations
from backend.ingestion import HistoricalDate, load_seed, validate


@pytest.mark.parametrize('connection_options', [
    {}, {'isolation_level':None},
    pytest.param({'autocommit':True}, marks=pytest.mark.skipif(not hasattr(sqlite3,'LEGACY_TRANSACTION_CONTROL'), reason='sqlite3 autocommit option requires Python 3.12+')),
])
def test_migration_rollback_no_orphans_and_retry(tmp_path, monkeypatch, connection_options):
    directory=tmp_path/'schema/migrations'; directory.mkdir(parents=True)
    migration=directory/'001_probe.sql'
    setup='''CREATE TABLE migration_probe (id INTEGER);
CREATE VIEW probe_view AS SELECT * FROM migration_probe;
CREATE TRIGGER probe_trigger AFTER INSERT ON migration_probe BEGIN SELECT 1; END;
'''
    migration.write_text(setup+'INSERT INTO missing_table VALUES (1);\n')
    monkeypatch.setattr(database,'ROOT',tmp_path)
    conn=sqlite3.connect(tmp_path/'probe.sqlite',**connection_options)
    with pytest.raises(sqlite3.OperationalError,match='missing_table'):
        migrate(conn)
    assert not conn.in_transaction
    assert not conn.execute("SELECT name FROM sqlite_master WHERE name IN ('migration_probe','probe_view','probe_trigger')").fetchall()
    assert conn.execute('SELECT COUNT(*) FROM schema_migrations').fetchone()[0]==0
    migration.write_text(setup+'INSERT INTO migration_probe VALUES (1);\n')
    migrate(conn)
    assert conn.execute('SELECT * FROM migration_probe').fetchall()==[(1,)]
    assert conn.execute('SELECT COUNT(*) FROM schema_migrations').fetchone()[0]==1
    migration.write_text(setup+'INSERT INTO migration_probe VALUES (2);\n')
    with pytest.raises(ValueError,match='Applied migration changed'):
        migrate(conn)
    conn.close()


def test_migration_refuses_active_transaction(tmp_path):
    conn=sqlite3.connect(tmp_path/'active.sqlite')
    conn.execute('BEGIN')
    conn.execute('CREATE TABLE caller_owned(id)')
    with pytest.raises(ValueError,match='active transaction'):
        migrate(conn)
    assert conn.in_transaction
    conn.rollback()
    assert not conn.execute("SELECT * FROM sqlite_master WHERE name='caller_owned'").fetchall()


@pytest.fixture
def data():
    return json.loads((database.ROOT/'data/seed.json').read_bytes())


@pytest.mark.parametrize('table,key,value,location',[
    ('ventures','aliases',[123],'ventures.0.aliases.0'),
    ('ventures','aliases',[''],'ventures.0.aliases.0'),
    ('ventures','aliases','text','ventures.0.aliases'),
    ('ventures','venture_id',123,'ventures.0.venture_id'),
    ('ventures','display_name',[],'ventures.0.display_name'),
    ('ventures','legal_name',False,'ventures.0.legal_name'),
    ('observations','value_text',123,'observations.0.value_text'),
    ('awards','award_year',True,'awards.0.award_year'),
    ('sources','unexpected','bad','sources.0.unexpected'),
])
def test_nested_type_refusal_before_database_creation(tmp_path,data,table,key,value,location):
    data[table][0][key]=value
    input_path=tmp_path/'invalid.json'; input_path.write_text(json.dumps(data))
    db=tmp_path/'must-not-exist.sqlite'
    with pytest.raises(ValueError,match=location.replace('.',r'\.')):
        load_seed(db,input_path)
    assert not db.exists()


def test_wrong_array_and_top_level_refused(data):
    data['sources']={}
    with pytest.raises(ValueError,match='sources'):
        validate(data)
    data['sources']=[]; data['arbitrary']='ignored?'
    with pytest.raises(ValueError,match='arbitrary'):
        validate(data)


@pytest.mark.parametrize('value',[
 {'precision':'unknown','lower_bound':'2020-01-01','upper_bound':None},
 {'precision':'month','lower_bound':'2024-02-01','upper_bound':'2024-02-28'},
 {'precision':'year','lower_bound':'2024-01-01','upper_bound':'2024-11-30'},
 {'precision':'day','lower_bound':'2024-01-01','upper_bound':'2024-01-02'},
 {'precision':'day','lower_bound':'2024-2-01','upper_bound':'2024-2-01'},
])
def test_false_date_precision_refused(value):
    with pytest.raises(ValueError):
        HistoricalDate.model_validate(value)


def version2(data):
    data=copy.deepcopy(data); data['metadata']['schema_version']=2
    data['sources'][0]['published_at']=None
    data['sources'][0]['publication_date']={'precision':'unknown','lower_bound':None,'upper_bound':None}
    data['sources'][1]['published_at']=None
    data['sources'][1]['publication_date']={'precision':'month','lower_bound':'2024-10-01','upper_bound':'2024-10-31'}
    data['awards'][0]['event_date']=None
    data['awards'][0]['event_date_interval']={'precision':'year','lower_bound':'2025-01-01','upper_bound':'2025-12-31'}
    return data


def test_v2_unknown_partial_dates_and_raw_bytes(tmp_path,data):
    data=version2(data)
    obs=data['observations'][0]
    obs['financial_value']={'raw_amount':'about $5m','currency':None,'amount_qualifier':'approximately','scope':'Synthetic fixture only; no real financing assertion','event_date':{'precision':'unknown','lower_bound':None,'upper_bound':None}}
    raw=json.dumps(data,indent=3).encode()+b'\n'
    input_path=tmp_path/'v2.json'; input_path.write_bytes(raw)
    db=tmp_path/'v2.sqlite'; load_seed(db,input_path); load_seed(db,input_path)
    with connect(db) as conn:
        preserved=conn.execute('SELECT raw_bytes FROM import_documents WHERE seed_sha256=?',(hashlib.sha256(raw).hexdigest(),)).fetchone()[0]
        assert preserved==raw
        selected=select_observations(conn)
        item=next(o for o in selected if o['source_id']==data['sources'][0]['source_id'])
        assert item['published_at'] is None and item['publication_date']['precision']=='unknown'
        assert item['publication_date']['lower_bound'] is None
        assert len(selected)==20
        assert not select_observations(conn,cutoff='2026-11-18')
        assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'


def test_review_supersession_and_cutoff_policy(tmp_path,data):
    data['metadata']['schema_version']=2
    original=data['observations'][0]
    replacement=dict(original,observation_id='synthetic_correction',value_text='Synthetic corrected wording; test fixture only')
    data['observations'].append(replacement)
    data['observation_relations']=[{'relation_id':'synthetic_relation','observation_id':original['observation_id'],'replacement_id':'synthetic_correction','relation_type':'corrects','reviewer':'Synthetic test fixture','recorded_at':'2026-11-17','rationale':'Not a real reviewer judgment'}]
    source=next(s for s in data['sources'] if s['source_id']==original['source_id'])
    source['available_at']='2025-10-17'; source['availability_evidence']='Synthetic archived fixture witness, not a real archive'
    input_path=tmp_path/'policy.json'; input_path.write_text(json.dumps(data)); db=tmp_path/'policy.sqlite'; load_seed(db,input_path)
    with sqlite3.connect(db) as conn:
        conn.execute('INSERT INTO review_events VALUES (?,?,?,?,?,?,?)',('synthetic_review',replacement['observation_id'],None,'accepted','Synthetic test reviewer','2026-11-18','Synthetic test only'))
    with connect(db) as conn:
        raw=enrich_observations(conn,[dict(r) for r in conn.execute('SELECT o.*,s.published_at FROM observations o JOIN sources s USING(source_id)')])
        assert any(r['observation_id']==original['observation_id'] and r['superseded'] for r in raw)
        assert not any(r['observation_id']==original['observation_id'] for r in select_observations(conn))
        assert [r['observation_id'] for r in select_observations(conn,'accepted')]==['synthetic_correction']
        assert not select_observations(conn,'accepted',cutoff='2026-11-17')
        assert any(r['observation_id']==original['observation_id'] for r in select_observations(conn,cutoff='2026-11-16'))
    with sqlite3.connect(db) as conn:
        conn.execute('INSERT INTO review_events VALUES (?,?,?,?,?,?,?)',('synthetic_rejection',replacement['observation_id'],None,'rejected','Synthetic test reviewer','2026-11-19','Synthetic test only'))
    with connect(db) as conn:
        assert not select_observations(conn,'accepted')
        assert [r['observation_id'] for r in select_observations(conn,'accepted',cutoff='2026-11-18')]==['synthetic_correction']


def test_extension_conflict_rolls_back_entire_import(tmp_path,data):
    data=version2(data); input_path=tmp_path/'v2.json'; input_path.write_text(json.dumps(data)); db=tmp_path/'v2.sqlite'; load_seed(db,input_path)
    data['sources'].append(dict(data['sources'][0],source_id='new_source_before_refusal'))
    data['sources'][0]['publication_date']={'precision':'day','lower_bound':'2025-12-31','upper_bound':'2025-12-31'}
    input_path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='Conflicting immutable record: evidence_dates'):
        load_seed(db,input_path)
    with connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM sources WHERE source_id='new_source_before_refusal'").fetchone()[0]==0
        assert conn.execute('SELECT COUNT(*) FROM imports').fetchone()[0]==1


def test_accepted_label_without_review_is_not_accepted_matching(tmp_path,data):
    data['observations'][0]['review_status']='accepted'
    path=tmp_path/'label.json'; path.write_text(json.dumps(data)); db=tmp_path/'test.sqlite'; load_seed(db,path)
    with connect(db) as conn:
        assert not select_observations(conn,'accepted')
        assert not any(o['observation_id']==data['observations'][0]['observation_id'] for o in select_observations(conn))


def test_partial_chronology_retains_compatible_uncertainty(data):
    data['metadata']['schema_version']=2
    source=data['sources'][0]
    source['published_at']=None
    source['publication_date']={'precision':'year','lower_bound':'2026-01-01','upper_bound':'2026-12-31'}
    # A November retrieval does not make a year-only label impossible.
    validate(data)
    source['publication_date']={'precision':'year','lower_bound':'2027-01-01','upper_bound':'2027-12-31'}
    with pytest.raises(ValueError,match='definitely after retrieval'):
        validate(data)
    source.pop('publication_date'); source['published_at']='2025-10-17'
    award=data['awards'][0]
    award['event_date']=None
    award['event_date_interval']={'precision':'year','lower_bound':'2025-01-01','upper_bound':'2025-12-31'}
    # A year-only event can precede an October report without inventing a day.
    validate(data)
    award['event_date_interval']={'precision':'month','lower_bound':'2025-11-01','upper_bound':'2025-11-30'}
    with pytest.raises(ValueError,match='Award event after report'):
        validate(data)


@pytest.mark.parametrize('value', [True, False, 1.0, '1'])
def test_schema_version_refuses_noninteger_before_writes(tmp_path, data, value):
    data['metadata']['schema_version']=value
    source=tmp_path/'invalid-version.json'
    source.write_text(json.dumps(data))
    db=tmp_path/'must-not-exist.sqlite'
    with pytest.raises(ValueError,match=r'metadata.schema_version'):
        load_seed(db,source)
    assert not db.exists()
