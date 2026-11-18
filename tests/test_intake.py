"""Only disposable synthetic local assertions; no manufactured source acceptance."""
import json,sqlite3
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.database import connect
from backend.ingestion import load_seed
from backend.main import create_app
from backend.intake import SaveDraft,save_draft

@pytest.fixture
def db(tmp_path):
 p=tmp_path/'intake.sqlite';load_seed(p);return p
@pytest.fixture
def client(db):return TestClient(create_app(db))
def payload(**kw):return dict(request_id='synthetic-create',name='Synthetic draft',aliases=['Synthetic alias'],description='clinical images software surgical planning',**kw)
def rows(db):
 with sqlite3.connect(db) as c:return {r[0]:c.execute('SELECT * FROM "'+r[0]+'" ORDER BY rowid').fetchall() for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}

def test_save_reopen_retry_and_revision_preserve_history(client,db):
 before=rows(db);p=payload();a=client.post('/api/intake/drafts',json=p)
 assert a.status_code==200,a.text
 a=a.json();assert a['review_status']=='draft_unreviewed' and a['assertion_origin']=='local_user_assertion'
 assert client.post('/api/intake/drafts',json=p).json()==a
 assert client.get('/api/intake/drafts/'+a['draft_id']).json()==a
 p.update(request_id='synthetic-revision',expected_revision=1,description='Synthetic revised query')
 b=client.post('/api/intake/drafts/'+a['draft_id']+'/revisions',json=p).json();assert b['revision_number']==2
 assert client.post('/api/intake/drafts/'+a['draft_id']+'/revisions',json=dict(p,request_id='stale-request')).status_code==409
 after=rows(db)
 for t in before:
  if not t.startswith('intake_'):assert before[t]==after[t],t
 assert len(after['intake_revisions'])==2
 with sqlite3.connect(db) as c:
  with pytest.raises(sqlite3.IntegrityError):c.execute('UPDATE intake_revisions SET payload_json=?',('{}',))

def test_duplicate_candidates_no_auto_identity_or_corpus_promotion(client):
 p=payload();p.update(name='FormusLabs')
 a=client.post('/api/intake/drafts',json=p).json()
 assert any(d['subject_id']=='v_formus' for d in a['duplicates'])
 assert a['identity_state']=='unresolved'
 assert client.get('/api/ventures').json()['total']==10
 result=client.post('/api/intake/drafts/'+a['draft_id']+'/compare',json={}).json()
 assert result['wrapper_version']=='intake-b0-query-1.0' and result['results']
 assert result['excluded_venture_ids']==[]
 assert result['query_fields']==['description']
 accepted=client.post('/api/intake/drafts/'+a['draft_id']+'/compare',json={'policy':'accepted'}).json()
 assert not accepted['results'] and accepted['abstention_reason']

@pytest.mark.parametrize('change',[{'name':12},{'aliases':[3]},{'review_status':'accepted'},{'claims':[{'text':'unattributed'}]}])
def test_malformed_input_never_writes(client,db,change):
 before=rows(db);p=payload();p.update(change)
 assert client.post('/api/intake/drafts',json=p).status_code==422
 assert rows(db)==before

def test_failed_persistence_rolls_back_and_refuses_cross_origin(db,client):
 before=rows(db)
 def fail(c):raise sqlite3.OperationalError('Injected failure')
 with pytest.raises(sqlite3.OperationalError):save_draft(db,SaveDraft(**payload()),failure_injector=fail)
 assert rows(db)==before
 assert client.post('/api/intake/drafts',json=payload(),headers={'Origin':'https://untrusted.invalid'}).status_code==403
 assert rows(db)==before

def test_valid_source_attribution_keeps_dates_origin_and_unknowns(client):
 p=payload();p['claims']=[dict(field='solution',text='Synthetic source assertion only',source_url='https://example.org/source',source_title='Synthetic test source',publisher='Synthetic publisher',locator='Test passage',source_relationship='company',published_date={'precision':'year','lower_bound':'2025-01-01','upper_bound':'2025-12-31'},retrieved_on='2026-11-18',effective_date={'precision':'unknown','lower_bound':None,'upper_bound':None})]
 a=client.post('/api/intake/drafts',json=p);assert a.status_code==200,a.text
 body=a.json();assert body['content']['claims']==p['claims']
 assert body['claim_disposition']=='user_supplied_source_attribution_unreviewed'
 assert body['unknowns']
 p['request_id']='invalid-source';p['claims'][0]['source_url']='https://invalid url'
 assert client.post('/api/intake/drafts',json=p).status_code==422
 p['claims'][0]['source_url']='https://example.org/';p['claims'][0]['published_date']['upper_bound']='2025-02-01'
 assert client.post('/api/intake/drafts',json=p).status_code==422

def test_genuinely_supplied_mapping_excludes_same_subject(db,client,tmp_path):
 from backend.research_adapter import EXAMPLE,import_research,_proposal_id
 import_research(db,EXAMPLE,as_of='2026-11-18')
 p=payload();p.update(name='Synthetic rostering draft',description='healthcare staff rostering software',research_subject_id='subj_rosterlab')
 a=client.post('/api/intake/drafts',json=p).json();url='/api/intake/drafts/'+a['draft_id']+'/compare'
 assert 'v_rosterlab' in [r['venture']['venture_id'] for r in client.post(url,json={}).json()['results']]
 document={'format_version':'identity-mappings:1','decisions':[dict(mapping_id='synthetic-test-resolution',subject_id='subj_rosterlab',venture_id='v_rosterlab',state='resolved',scope='brand_project_only',actor_role='owner',actor_id='Synthetic fixture only',decided_on='2026-11-18',evidence_ids=['obs_rl_solution'],rationale='Synthetic fixture only',supersedes_mapping_id=_proposal_id('subj_rosterlab'))]}
 path=tmp_path/'decision.json';path.write_text(json.dumps(document));import_research(db,EXAMPLE,as_of='2026-11-18',mapping_decisions_path=path)
 result=client.post(url,json={}).json()
 assert result['excluded_venture_ids']==['v_rosterlab']
 assert all(r['venture']['venture_id']!='v_rosterlab' for r in result['results'])


def test_retry_returns_original_revision_after_a_later_edit(client):
 p=payload();a=client.post('/api/intake/drafts',json=p).json()
 later=dict(p,request_id='synthetic-later',expected_revision=1,description='Synthetic later content')
 assert client.post('/api/intake/drafts/'+a['draft_id']+'/revisions',json=later).json()['revision_number']==2
 retry=client.post('/api/intake/drafts',json=p).json()
 assert retry['draft_id']==a['draft_id'] and retry['revision_number']==1
 assert retry['content']==a['content']
 assert client.get('/api/intake/drafts/'+a['draft_id']).json()['revision_number']==2
