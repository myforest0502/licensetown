"""Merge six completed Lot05 chunks into one staging payload."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CHUNK_DIR=ROOT/'staging'/'question_bank_2000_lot05_chunks_v01'
OUT=ROOT/'staging'/'question_bank_2000_lot05_v01.json'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    drafts=[]
    for n in range(1,7):
        p=read(CHUNK_DIR/f'chunk_{n:02d}.json')
        if p.get('status')!='completed_chunk' or p.get('formal_baseline')!='Q1-Q1953': raise ValueError(f'chunk {n} not completed')
        drafts.extend(p.get('drafts',[]))
    drafts.sort(key=lambda d:int(d['draft_order']))
    if len(drafts)!=41 or [int(d['draft_order']) for d in drafts]!=list(range(1,42)): raise ValueError('draft order/count mismatch')
    if len({d['draft_id'] for d in drafts})!=41 or any(d.get('status')!='accepted' for d in drafts): raise ValueError('accepted/unique contract mismatch')
    payload={'batch':'question_bank_2000_production_lot05_v01','formal_baseline':'Q1-Q1953','q_ids_reserved':False,'production_write':False,'db_write':False,'accepted_target_count':41,'status':'staging_only','drafts':drafts}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'merged':41,'output':str(OUT.relative_to(ROOT))},ensure_ascii=False))
    return 0
if __name__=='__main__': raise SystemExit(main())
