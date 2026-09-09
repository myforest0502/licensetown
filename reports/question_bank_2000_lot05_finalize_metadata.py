"""Normalize Lot05 editorial metadata before whole-lot validation.

This does not allocate formal IDs. It fills audit metadata already supported by the
chunk review and applies the planned 11-question safety augmentation.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'staging'/'question_bank_2000_lot05_chunks_v01'
SAFETY_OVERRIDES={
 'L05-C10-S01':'moderate',
 'L05-C11-S01':'moderate',
 'L05-C11-M01':'critical',
 'L05-C13-S01':'moderate',
 'L05-C18-S01':'moderate',
}
STEM_OVERRIDES={
 'L05-C9-M01':'20代女性。数か月前に片眼の視力低下が改善した既往がある。今回は反対側下肢に新たな感覚障害と痙性を認め、画像では脳と頸髄に複数の脱髄病変がみられた。最も考えられる疾患はどれか。'
}
def main():
    changed=0
    for n in range(1,7):
        path=DIR/f'chunk_{n:02d}.json'; p=json.loads(path.read_text(encoding='utf-8-sig'))
        for d in p['drafts']:
            review=d.get('semantic_review') if isinstance(d.get('semantic_review'),dict) else {}
            if not d.get('clinical_intent'):
                d['clinical_intent']=str(review.get('candidate_demand') or f"{d.get('proposed_task')}/{d.get('primary_ability')}")
                changed+=1
            if d.get('slot_type')!='new_node' and not review.get('reference_demand'):
                prior=', '.join(f"{x.get('task')}/{x.get('primary_ability')}" for x in d.get('existing_demands',[]))
                review['reference_demand']=prior or 'formal reference demand'
                d['semantic_review']=review; changed+=1
            if d['draft_id'] in SAFETY_OVERRIDES and d.get('safety')!=SAFETY_OVERRIDES[d['draft_id']]:
                d['safety']=SAFETY_OVERRIDES[d['draft_id']]; changed+=1
            if d['draft_id'] in STEM_OVERRIDES and d.get('question_text')!=STEM_OVERRIDES[d['draft_id']]:
                d['question_text']=STEM_OVERRIDES[d['draft_id']]; changed+=1
        path.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'changed_fields':changed,'safety_augmented_ids':sorted(SAFETY_OVERRIDES),'stem_overrides':sorted(STEM_OVERRIDES)},ensure_ascii=False))
    return 0
if __name__=='__main__': raise SystemExit(main())
