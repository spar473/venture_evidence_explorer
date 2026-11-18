"""Synthetic numerical/role fixtures only; shipped human review files remain blank."""
import copy,csv,json
from pathlib import Path
import pytest
from backend.database import ROOT
from backend.ingestion import load_seed
from backend.evaluation_protocol import freeze,load_bundle,review_materials,run,task_bank,query_metrics,compare_reports,paired_bootstrap

@pytest.fixture
def bundle(tmp_path):
 db=tmp_path/'source.sqlite';load_seed(db);output=tmp_path/'bundle';freeze(db,output);return output

def test_freeze_reproduce_blank_metrics_and_review_export(bundle,tmp_path):
 first=run(bundle,repeats=1);second=run(bundle,repeats=1)
 assert first['status']=='not_evaluated' and first['reason']=='judgments_missing'
 assert all(q['aggregate_metrics']['ndcg_at_3'] is None and not q['metrics'] for q in first['queries'])
 assert [q['run'] for q in first['queries']]==[q['run'] for q in second['queries']]
 assert first['coverage']['tasks_run']==6
 held=run(bundle,split='held_out',repeats=1)
 assert not held['queries'] and held['tasks_pending']==['heldout_unseen_cohort_01'] and held['coverage']['result_coverage'] is None
 materials=review_materials(bundle,tmp_path/'materials');assert materials['review_rows']==60
 rows=list(csv.DictReader((tmp_path/'materials/review_sheet.csv').open()))
 assert all(not r['relevance_grade'] and not r['reviewer_id'] for r in rows)
 assert json.loads((tmp_path/'materials/reviewers.json').read_text())==[]
 comparison=compare_reports(first,second);assert comparison['mean_difference'] is None and comparison['uncertainty']['interval'] is None

def test_manifest_drift_and_leakage_refused(bundle,tmp_path):
 with (bundle/'corpus.json').open('a') as f:f.write(' ')
 with pytest.raises(ValueError,match='drift'):load_bundle(bundle)
 tasks=json.loads((ROOT/'evaluation/protocol-v1/tasks.json').read_text());ids={i for t in tasks['tasks'] for i in t['identity_group_ids']}
 tasks['tasks'][1]['split']='held_out';p=tmp_path/'leak.json';p.write_text(json.dumps(tasks))
 with pytest.raises(ValueError,match='leaks'):task_bank(p,ids)
 tasks['tasks'][1]['group_id']='renamed_group';p.write_text(json.dumps(tasks))
 with pytest.raises(ValueError,match='identity leaks'):task_bank(p,ids)

def synthetic_materials(bundle,tmp_path):
 manifest,corpus,bank=load_bundle(bundle)
 registry=tmp_path/'reviewers.json';registry.write_text(json.dumps([{'reviewer_id':'synthetic_unit_fixture','role':'analyst','independent_of_author':False,'is_human':True}]))
 labels=tmp_path/'labels.csv'
 with labels.open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['query_id','venture_id','reviewer_id','relevance_grade','rationale','supporting_observation_ids','reviewed_on'])
  for t in bank.tasks:
   if t.status=='runnable':
    for v in corpus:w.writerow([t.query_id,v['venture_id'],'synthetic_unit_fixture',1,'Synthetic code-verification fixture only; not an actual human judgment',v['observations'][0]['observation_id'],'2026-11-18'])
 return labels,registry

def test_real_label_shape_gate_and_no_silent_missing_grades(bundle,tmp_path):
 labels,registry=synthetic_materials(bundle,tmp_path)
 report=run(bundle,labels,registry,repeats=1)
 assert report['status']=='human_judgments_partial_or_complete'
 assert any(q['metrics'] and q['metrics'][0]['ndcg_at_3'] is not None for q in report['queries'])
 assert all(q['metrics'][0]['reason']=='abstention_no_relevance_score' for q in report['queries'] if not q['ranked_ids'])
 rows=list(csv.DictReader(labels.open()));rows[0]['relevance_grade']='4'
 with labels.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 with pytest.raises(ValueError,match='grade'):run(bundle,labels,registry,repeats=1)

@pytest.mark.parametrize('field,value,reason',[('reviewer_id','invented_missing_registry','reviewer'),('supporting_observation_ids','missing_observation','evidence'),('reviewed_on','2099-01-01','date')])
def test_malformed_human_input_refused(bundle,tmp_path,field,value,reason):
 labels,registry=synthetic_materials(bundle,tmp_path);rows=list(csv.DictReader(labels.open()));rows[0][field]=value
 with labels.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 with pytest.raises(ValueError,match=reason):run(bundle,labels,registry,repeats=1)

def test_metric_edge_cases_and_paired_refusal(bundle):
 row={'relevance_grade':0}
 labels={('q','a','fixture'):row,('q','b','fixture'):row}
 metrics=query_metrics('q',['a'],['a','b'],labels)[0]
 assert metrics['ndcg_at_3'] is None and metrics['reason']=='zero_ideal_gain' and metrics['precision_at_3_returned_denominator']==0
 assert query_metrics('q',['a','c'],['a','b','c'],labels)[0]['precision_at_3_returned_denominator'] is None
 report=run(bundle,repeats=1);other=copy.deepcopy(report);other['input_hashes']['tasks.json']='different'
 with pytest.raises(ValueError,match='identical'):compare_reports(report,other)
 assert paired_bootstrap({'only_group':.2})['interval'] is None
 # Constant synthetic paired effects verify clustering code only, not research quality.
 assert paired_bootstrap({str(i):.25 for i in range(8)})['interval']==[.25,.25]


def test_disagreements_audit_and_unsupported_metric_refusal(bundle,tmp_path):
 labels,registry=synthetic_materials(bundle,tmp_path)
 people=json.loads(registry.read_text());second=dict(people[0],reviewer_id='synthetic_second_fixture',role='independent_reviewer',independent_of_author=True)
 people.append(second);registry.write_text(json.dumps(people))
 rows=list(csv.DictReader(labels.open()));extra=dict(rows[0],reviewer_id=second['reviewer_id'],relevance_grade='0')
 with labels.open('a',newline='') as f:csv.DictWriter(f,fieldnames=rows[0]).writerow(extra)
 report=run(bundle,labels,registry,repeats=1)
 assert report['disagreements'] and report['disagreements'][0]['adjudication']=='not_supplied'
 assert {r['grade'] for r in report['disagreements'][0]['independent_records']}=={0,1}
 assert report['factual_audit']['counts'] is None
 blank=run(bundle,repeats=1);tampered=copy.deepcopy(blank);tampered['queries'][0]['metrics']=[{'ndcg_at_3':1.0}]
 with pytest.raises(ValueError,match='Unsupported reported'):compare_reports(blank,tampered)
 audit=tmp_path/'audit.csv'
 with audit.open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['query_id','venture_id','observation_id','reviewer_id','entailment_status','rationale','reviewed_on'])
  writer.writerow([rows[0]['query_id'],rows[0]['venture_id'],rows[0]['supporting_observation_ids'],rows[0]['reviewer_id'],'insufficient','Synthetic audit fixture only','2026-11-18'])
 audited=run(bundle,labels,registry,repeats=1,factual_audit=audit)
 assert audited['factual_audit']['counts']['insufficient']==1
