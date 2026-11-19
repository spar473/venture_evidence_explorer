#!/usr/bin/env python3
"""Prepare a disposable healthtech demo, optionally export review inputs or serve.

Never open, migrate, back up or replace an existing user database. Output must be
new/empty and remains outside version control by default.
"""
import argparse
import csv
import hashlib
import json
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.database import connect
from backend.ingestion import load_seed
from backend.research_adapter import EXAMPLE, dry_run_research, import_research
from backend.healthtech import compare_healthtech, SELECTION_PATH

AS_OF = '2026-11-19'
PACKETS = (EXAMPLE, ROOT/'research/healthtech-pilot/packet.json', ROOT/'research/healthtech-pilot/extension.json')


def snapshot(db):
    with closing(sqlite3.connect(db)) as conn:
        return {r[0]: conn.execute('SELECT * FROM "'+r[0]+'" ORDER BY rowid').fetchall()
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}


def prepare_demo(output):
    if output.exists() and any(output.iterdir()):
        raise ValueError('Demo output must be new or empty; existing files and databases are never replaced.')
    output.mkdir(parents=True, exist_ok=True)
    db = output/'demo.sqlite'
    load_seed(db)
    summaries = []
    for packet in PACKETS:
        before = snapshot(db)
        before_hash = hashlib.sha256(db.read_bytes()).hexdigest()
        dry = dry_run_research(packet, db, as_of=AS_OF)
        if dry['status'] != 'valid_dry_run':
            raise ValueError('Packet dry run failed: '+str(packet))
        if dry['writes'] != 0 or snapshot(db) != before or hashlib.sha256(db.read_bytes()).hexdigest() != before_hash:
            raise RuntimeError('Dry run changed the demo database')
        applied = import_research(db, packet, as_of=AS_OF)
        after = snapshot(db)
        import_research(db, packet, as_of=AS_OF)
        if snapshot(db) != after:
            raise RuntimeError('Repeated import changed stored rows')
        for name,report in [('dry-run',dry), ('import',applied)]:
            (output/(packet.stem+'-'+name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
        summaries.append({'packet':str(packet.relative_to(ROOT)), 'sha256':applied['packet_sha256'],
            'counts':applied['counts'], 'dry_run_writes':0, 'repeat_import':'full-row equality'})
    with closing(connect(db)) as conn:
        if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or conn.execute('PRAGMA foreign_key_check').fetchall():
            raise RuntimeError('Demo database failed integrity checks')
        mri = compare_healthtech(conn, 'subj_ht_mri', as_of=AS_OF)
        if len(mri['peers']) != 2:
            raise RuntimeError('Expected two MRI pathway precedents')
    result = {'database':str(db.resolve()), 'research_as_of':AS_OF, 'imports':summaries,
        'ui_path':'Research dossiers → Automated Breast MRI Reporting → Provider evaluation comparison',
        'limits':'Source-checked pathway evidence; same-stage and historical comparisons abstain. Human judgments remain pending.'}
    (output/'demo-summary.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def export_evaluation(db, output):
    """Reuse the existing frozen B0/review workflow; preserve separate graph inputs."""
    from backend.evaluation_protocol import freeze, review_materials, run
    from backend.research_validation import decode_packet
    from backend.healthtech import POLICY
    tasks_path = ROOT/'evaluation/healthtech-pilot/research_tasks.json'
    tasks = decode_packet(tasks_path.read_bytes())
    freeze(db, output/'lexical-bundle', ROOT/'evaluation/healthtech-pilot/tasks.json', as_of=AS_OF)
    review_materials(output/'lexical-bundle', output/'lexical-review')
    baseline = run(output/'lexical-bundle', as_of=AS_OF, repeats=1)
    (output/'lexical-results.json').write_text(json.dumps(baseline,indent=2)+'\n')
    results = []
    with closing(connect(db)) as conn:
        conn.execute('BEGIN')
        for task in tasks['tasks']:
            results.append(dict(query_id=task['query_id'], result=compare_healthtech(conn, task['subject_id'], as_of=task['as_of'], view=task['view'])))
    report = {'format_version':'healthtech-development-run:1','policy':POLICY,
        'status':'not_evaluated','reason':'Human relevance, factual error and manual research observations have not been collected.',
        'selection_sha256':hashlib.sha256(SELECTION_PATH.read_bytes()).hexdigest(),
        'task_sha256':hashlib.sha256(tasks_path.read_bytes()).hexdigest(),
        'source_hashes':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['backend/healthtech.py','backend/research_repository.py','backend/research_adapter.py','backend/research_validation.py']},
        'results':results,'human_judgments':[], 'manual_research_observations':[],
        'limits':['Development tasks selected by the implementation author; no held-out validation.',
            'Curated pathways and B0 use different evidence corpora. This is a review exercise, not a measured ranking advantage.',
            'The frozen B0 bundle includes the same SQLite research records, but B0 eligibility and scoring remain unchanged.']}
    (output/'research-results.json').write_text(json.dumps(report,indent=2)+'\n')
    with (output/'research-review.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['query_id','subject_id','peer_subject_id','reviewer_id','relevance_grade','material_evidence_errors','rationale','supporting_observation_ids','reviewed_on','manual_research_minutes','useful_result_minutes'])
        for row in results:
            result=row['result']
            for peer in result['peers'] or [None]:
                writer.writerow([row['query_id'],result['subject_id'],peer['subject_id'] if peer else '',*(['']*8)])
    return {'status':'not_evaluated','tasks':len(results),'output':str(output.resolve()),'human_fields':'blank'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,help='New/empty directory; default is a fresh system temporary directory.')
    parser.add_argument('--evaluate',action='store_true',help='Export frozen B0 inputs, curated results and blank human-review materials.')
    parser.add_argument('--serve',action='store_true')
    parser.add_argument('--port',type=int,default=8001)
    args=parser.parse_args()
    if args.serve and not (ROOT/'frontend/dist/index.html').exists():
        parser.error('Build the frontend first: npm --prefix frontend ci && npm --prefix frontend run build')
    output=args.output_dir or Path(tempfile.mkdtemp(prefix='vee-healthtech-'))
    try:
        result=prepare_demo(output)
        if args.evaluate:
            result['evaluation']=export_evaluation(Path(result['database']),output/'evaluation')
    except (OSError,ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result,indent=2),flush=True)
    if args.serve:
        import uvicorn
        from backend.main import create_app
        print(f'Open http://127.0.0.1:{args.port} · disposable database {result["database"]}',flush=True)
        uvicorn.run(create_app(result['database']),host='127.0.0.1',port=args.port)


if __name__=='__main__':
    main()
