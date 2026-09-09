"""Seal fully authored/reviewed Lot05 staging without human-expert approval."""
from __future__ import annotations
import json
from reports.question_bank_2000_lot05_validate import BANK,PROTECTED,STAGING,build_report,draft_fingerprint,file_fingerprint

def main():
    payload=json.loads(STAGING.read_text(encoding='utf-8-sig'))
    report=build_report(payload,require_seals=False)
    if report['hard_errors']:
        print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit('Lot05 pre-seal hard errors')
    payload['formal_hash_format']='sha256-lf-normalized-v1'
    payload['formal_input_sha256']={name:file_fingerprint(BANK/name) for name in PROTECTED}
    for draft in payload['drafts']: draft['reviewed_sha256']=draft_fingerprint(draft)
    STAGING.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    final=build_report(payload,require_seals=True)
    if final['hard_errors']:
        print(json.dumps(final,ensure_ascii=False,indent=2)); raise SystemExit('Lot05 seal invalid')
    print(json.dumps({'sealed':True,'accepted_count':final['accepted_count'],'structural_strong_formations':final['structural_strong_formations'],'warnings':final['warnings']},ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
