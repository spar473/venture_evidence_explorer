#!/usr/bin/env python3
"""Validate or stage the supplied discovery inventory; never promotes ventures."""
import argparse,json,sys
from pathlib import Path
from contextlib import closing
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from backend.discovery import PACK,decode_packet,validate_packet,import_discovery,import_decisions,promotion_preview
from backend.database import connect

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,default=PACK);p.add_argument('--db',type=Path);p.add_argument('--apply',action='store_true');p.add_argument('--as-of',default='2026-11-18');p.add_argument('--decisions',type=Path);p.add_argument('--promotion-id');p.add_argument('--research-packet',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
 if (a.apply or a.decisions or a.promotion_id) and a.db is None:p.error('--db required for staging/review/promotion preview')
 try:
  if a.promotion_id:
   with closing(connect(a.db)) as conn:result=promotion_preview(conn,a.promotion_id,a.research_packet,a.as_of)
  elif a.decisions:
   if not a.apply:p.error('--decisions requires explicit --apply (no promotion is performed)')
   result=import_decisions(a.db,a.decisions,a.as_of)
  elif a.apply:result=import_discovery(a.db,a.input,a.as_of)
  else:result={'status':'valid_dry_run','counts':validate_packet(decode_packet(a.input.read_bytes()),a.as_of),'writes':0,'accepted_nz_population':None,'promoted':0}
 except (ValueError,TypeError) as e:raise SystemExit(str(e))
 raw=json.dumps(result,indent=2)+'\n'
 if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(raw)
 print(raw)
if __name__=='__main__':main()
