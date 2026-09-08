"""Split Lot05 into six authoring chunks and build formal reference packets.

Read-only against the formal Question Bank. Outputs remain staging/report artifacts.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'data'/'question_bank'
TEMPLATE=ROOT/'staging'/'question_bank_2000_lot05_template_v01.json'
CHUNK_DIR=ROOT/'staging'/'question_bank_2000_lot05_chunks_v01'
PACKET_DIR=ROOT/'reports'/'question_bank_2000_lot05_reference_packets_v01'
SIZES=(7,7,7,7,7,6)


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))

def main():
    template=read(TEMPLATE)
    questions={x['id']:x for x in read(BANK/'questions.json')}
    answers={x['id']:x for x in read(BANK/'answers.json')}
    explanations={x['id']:x for x in read(BANK/'explanations.json')}
    tags={x['id']:x for x in read(BANK/'question_tags.json')}
    drafts=template['drafts']
    if len(drafts)!=sum(SIZES): raise ValueError(len(drafts))
    CHUNK_DIR.mkdir(parents=True,exist_ok=True); PACKET_DIR.mkdir(parents=True,exist_ok=True)
    start=0
    manifest=[]
    for chunk_no,size in enumerate(SIZES,1):
        rows=json.loads(json.dumps(drafts[start:start+size],ensure_ascii=False))
        chunk={
            'lot':5,'chunk':chunk_no,'formal_baseline':template['formal_baseline'],
            'status':'authoring_chunk','production_write':False,'db_write':False,
            'drafts':rows,
        }
        cpath=CHUNK_DIR/f'chunk_{chunk_no:02d}.json'
        cpath.write_text(json.dumps(chunk,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        packet=[]
        for draft in rows:
            refs=[]
            for qid in draft.get('reference_question_ids',[]):
                if qid not in questions or qid not in tags: raise ValueError(f'missing ref {qid}')
                refs.append({
                    'question_id':qid,
                    'question':questions[qid],
                    'answer':answers[qid],
                    'explanation':explanations[qid],
                    'tag':tags[qid],
                })
            packet.append({
                'draft_id':draft['draft_id'],
                'slot_type':draft['slot_type'],
                'target_node_id':draft.get('target_node_id'),
                'target_node_label':draft.get('target_node_label'),
                'planned_task':draft['proposed_task'],
                'planned_primary_ability':draft['primary_ability'],
                'planned_level':draft['level'],
                'references':refs,
                'authoring_guard':'Do not copy the reference stem or test the same semantic demand.',
            })
        ppath=PACKET_DIR/f'chunk_{chunk_no:02d}_references.json'
        ppath.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        manifest.append({'chunk':chunk_no,'draft_ids':[x['draft_id'] for x in rows],'size':size})
        start+=size
    (ROOT/'reports'/'question_bank_2000_lot05_chunks_manifest_v01.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
