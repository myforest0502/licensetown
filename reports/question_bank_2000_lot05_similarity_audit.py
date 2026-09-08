"""Audit completed Lot05 chunks against formal Q1-Q1953 stems."""
from __future__ import annotations
import argparse, json, re, unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'data'/'question_bank'
CHUNK_DIR=ROOT/'staging'/'question_bank_2000_lot05_chunks_v01'
OUT_DIR=ROOT/'reports'/'question_bank_2000_lot05_similarity_audits'
NEAR=0.65; HARD=0.78

def norm(text):
    value=unicodedata.normalize('NFKC',str(text or '')).lower()
    return re.sub(r'[^0-9a-zぁ-んァ-ヶ一-龠々ー]+','',value)

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))

def audit(chunk_no):
    formal=read(BANK/'questions.json')
    if max(int(x['id'][1:]) for x in formal)!=1953: raise ValueError('Lot05 audit requires Q1-Q1953')
    chunk=read(CHUNK_DIR/f'chunk_{chunk_no:02d}.json')
    if chunk.get('status')!='completed_chunk' or chunk.get('formal_baseline')!='Q1-Q1953': raise ValueError('completed Q1-Q1953 chunk required')
    formal_norm=[(q['id'],q.get('question_text',''),norm(q.get('question_text',''))) for q in formal]
    results=[]; exact_total=hard_total=near_total=0
    for d in chunk['drafts']:
        text=d['question_text']; n=norm(text); ranked=[]
        for qid,qtext,qn in formal_norm:
            if not qn: continue
            score=SequenceMatcher(None,n,qn,autojunk=False).ratio(); ranked.append((score,qid,qtext))
        ranked.sort(reverse=True)
        top=[{'qid':qid,'score':round(score,6),'question_text':qtext} for score,qid,qtext in ranked[:10]]
        exact=[x for x in top if x['score']==1.0]; hard=[x for x in top if x['score']>=HARD]; near=[x for x in top if x['score']>=NEAR]
        exact_total+=len(exact); hard_total+=len(hard); near_total+=len(near)
        results.append({'draft_id':d['draft_id'],'reference_question_ids':d.get('reference_question_ids',[]),'exact':exact,'hard_near':hard,'near':near,'top10':top})
    return {'formal_baseline':'Q1-Q1953','chunk':chunk_no,'thresholds':{'near':NEAR,'hard_near':HARD},'exact_total':exact_total,'hard_near_total':hard_total,'near_total':near_total,'results':results}

def main():
    p=argparse.ArgumentParser(); p.add_argument('chunk',type=int,choices=range(1,7)); a=p.parse_args(); payload=audit(a.chunk)
    OUT_DIR.mkdir(parents=True,exist_ok=True); out=OUT_DIR/f'chunk_{a.chunk:02d}.json'; out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'chunk':a.chunk,'exact_total':payload['exact_total'],'hard_near_total':payload['hard_near_total'],'near_total':payload['near_total'],'output':str(out.relative_to(ROOT))},ensure_ascii=False))
    if payload['exact_total']: raise SystemExit('exact formal duplicate detected')
    return 0
if __name__=='__main__': raise SystemExit(main())
