#!/usr/bin/env python3
"""Read-only, snapshot-consistent analytical exports of the research graph."""
import argparse
import hashlib
import json
import os
import sys
import tempfile
from contextlib import closing
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.database import DEFAULT_DB,connect
from backend.research_repository import EXPORT_NAMES,export_csv


def atomic_write(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    descriptor,pending=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
    try:
        with os.fdopen(descriptor,'wb') as stream:
            stream.write(raw)
        os.replace(pending,path)
    finally:
        if os.path.exists(pending):os.unlink(pending)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=DEFAULT_DB)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--subject-id')
    parser.add_argument('--packet-sha256')
    args=parser.parse_args()
    files=[]
    with closing(connect(args.db)) as conn:
        conn.execute('BEGIN')
        try:
            for name in EXPORT_NAMES:
                raw=export_csv(conn,name,subject_id=args.subject_id,packet_sha256=args.packet_sha256).encode()
                filename='research_'+name+'.csv'
                atomic_write(args.output_dir/filename,raw)
                files.append({'name':filename,'sha256':hashlib.sha256(raw).hexdigest()})
            sql='SELECT packet_sha256,raw_bytes FROM research_imports WHERE namespace=?'
            parameters=['research:0.2.1']
            if args.packet_sha256:
                sql+=' AND packet_sha256=?';parameters.append(args.packet_sha256)
            for digest,raw in conn.execute(sql+' ORDER BY packet_sha256',parameters):
                assert hashlib.sha256(raw).hexdigest()==digest
                filename='packet-'+digest+'.json'
                atomic_write(args.output_dir/filename,raw)
                files.append({'name':filename,'sha256':digest})
        finally:
            conn.execute('ROLLBACK')
    manifest={'namespace':'research:0.2.1','scope_subject_id':args.subject_id,'packet_sha256':args.packet_sha256,
              'grains':'One record per stable ID; subject views retain linked counterpart provenance. Event rows are candidates, not established distinct rounds.',
              'nulls':'Unknown values retain explicit reason/raw JSON; blanks are never invented zeros.',
              'files':files}
    atomic_write(args.output_dir/'manifest.json',(json.dumps(manifest,indent=2)+'\n').encode())
    print(json.dumps({'output_dir':str(args.output_dir),'files':len(files),'scope_subject_id':args.subject_id}))


if __name__=='__main__':
    main()
