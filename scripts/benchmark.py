#!/usr/bin/env python3
"""SQL counts and warm local latency, never a SQLite scalability claim."""
import argparse
import tempfile
from contextlib import ExitStack, closing
import json
import statistics
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.database import connect
from backend.repository import browse
from backend.retrieval import compare


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=ROOT/'outputs/venture_evidence.sqlite')
    parser.add_argument('--repeats',type=int,default=50)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--synthetic-ventures',type=int,default=0,help='Additional temporary identities; never modifies the input DB')
    args=parser.parse_args()
    if args.repeats < 1:
        parser.error('--repeats must be positive')
    if not 0 <= args.synthetic_ventures <= 10000:
        parser.error('--synthetic-ventures must be 0..10000')
    with ExitStack() as stack:
        measured_db=args.db
        if args.synthetic_ventures:
            from backend.ingestion import load_seed
            temp=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='vee-synthetic-benchmark-')))
            payload=json.loads((ROOT/'data/seed.json').read_text())
            prototype=payload['ventures'][0]
            observation=next(o for o in payload['observations'] if o['field']=='product_description')
            for i in range(args.synthetic_ventures):
                vid=f'synthetic_benchmark_{i:05d}'
                payload['ventures'].append(dict(prototype,venture_id=vid,display_name=f'Synthetic benchmark {i:05d}',aliases=[]))
                payload['observations'].append(dict(observation,venture_id=vid,observation_id=vid+'_product',value_text='clinical image software surgery planning'))
            seed=temp/'synthetic.json'
            seed.write_text(json.dumps(payload))
            measured_db=temp/'synthetic.sqlite'
            load_seed(measured_db,seed)
        measurements=[]
        conn=stack.enter_context(closing(connect(measured_db)))
        counts={name:conn.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] for name in ('ventures','observations','sources')}
        for label,fn in [('directory',lambda:browse(conn)),('compare',lambda:compare(conn,query='clinical images software surgical planning'))]:
            statements=[]
            conn.set_trace_callback(statements.append)
            fn()
            conn.set_trace_callback(None)
            samples=[]
            for _ in range(args.repeats):
                start=time.perf_counter()
                fn()
                samples.append((time.perf_counter()-start)*1000)
            measurements.append({'operation':label,'selects':sum(s.lstrip().upper().startswith('SELECT') for s in statements),
                                 'repeats':args.repeats,'median_ms':round(statistics.median(samples),3),
                                 'p95_ms':round(sorted(samples)[min(len(samples)-1,int(len(samples)*.95))],3)})
    report={'scope':'Warm local engineering benchmark; declared synthetic additions are temporary, not research data. Not a production load test', 'synthetic_additions':args.synthetic_ventures,'rows':counts,'measurements':measurements}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
