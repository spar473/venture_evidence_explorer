from pathlib import Path
import argparse,json,sqlite3,tempfile,sys
sys.dont_write_bytecode=True
parser=argparse.ArgumentParser(description='Synthetic mapping chronology probe; writes only temporary DBs and an optional output file.')
parser.add_argument('--repository',type=Path,required=True)
parser.add_argument('--output',type=Path)
args=parser.parse_args()
sys.path.insert(0,str(args.repository.resolve()))
from backend.ingestion import load_seed
from backend.research_adapter import EXAMPLE,import_research,dry_run_research,_proposal_id
from backend.database import connect
results=[]
with tempfile.TemporaryDirectory(prefix='vee-review-mapping-') as temp:
 root=Path(temp);db=root/'probe.sqlite';load_seed(db);import_research(db,EXAMPLE,as_of='2026-11-18')
 for kind,eid in [('source','src_rl_pricing'),('observation','obs_rl_solution')]:
  p={'format_version':'identity-mappings:1','decisions':[dict(mapping_id='synthetic-review-'+kind,subject_id='subj_rosterlab',venture_id='v_rosterlab',state='resolved',scope='brand_project_only',actor_role='owner',actor_id='Synthetic review probe only',decided_on='2020-01-01',evidence_ids=[eid],rationale='Synthetic chronology probe, not an actual identity acceptance.',supersedes_mapping_id=_proposal_id('subj_rosterlab'))]}
  f=root/(kind+'.json');f.write_text(json.dumps(p));preview=dry_run_research(EXAMPLE,db_path=db,as_of='2026-11-18',mapping_decisions_path=f)
  result={'evidence_kind':kind,'evidence_id':eid,'decision_date':'2020-01-01','underlying_source_retrieval':'2026-11-18','dry_run_status':preview['status'],'errors':preview['mapping_errors']}
  if kind=='observation':
   imported=import_research(db,EXAMPLE,as_of='2026-11-18',mapping_decisions_path=f)
   with connect(db) as c:
    row=c.execute("SELECT state,decided_on,evidence_ids_json FROM research_identity_mappings WHERE mapping_id=?",('synthetic-review-'+kind,)).fetchone()
    result['stored_decision']=dict(row)
  results.append(result)
print(json.dumps(results,indent=2))
if args.output:args.output.write_text(json.dumps(results,indent=2)+'\n')
