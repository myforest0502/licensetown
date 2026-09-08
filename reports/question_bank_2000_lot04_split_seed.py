"""Split Lot04 authoring seed into six 8-draft authoring chunks."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'staging'/'question_bank_2000_lot04_authoring_seed_v01.json'
OUT=ROOT/'staging'/'question_bank_2000_lot04_chunks_v01'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def main():
    seed=read(SEED)
    if seed.get('formal_baseline')!='Q1-Q1905' or len(seed.get('drafts',[]))!=48: raise ValueError('Lot04 seed invalid')
    OUT.mkdir(parents=True,exist_ok=True)
    for i in range(6):
        drafts=seed['drafts'][i*8:(i+1)*8]
        payload={'batch':'question_bank_2000_production_lot04_v01','formal_baseline':'Q1-Q1905','status':'authoring_chunk','chunk_index':i+1,'chunk_count':6,'drafts':drafts,'q_ids_reserved':False,'production_write':False,'db_write':False}
        (OUT/f'chunk_{i+1:02d}.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'chunks':6,'drafts':48,'output':str(OUT.relative_to(ROOT))}); return 0
if __name__=='__main__': raise SystemExit(main())
