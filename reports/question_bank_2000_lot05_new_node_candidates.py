"""Audit candidate new Knowledge Nodes for Lot05 against formal Q1-Q1953.

This is a read-only collision audit. It never allocates Node IDs or formal Q IDs.
"""
from __future__ import annotations
import json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'data'/'question_bank'
OUT=ROOT/'reports'/'question_bank_2000_lot05_new_node_candidates.json'
CANDIDATES=[
 {"key":"C1_A","category_small":1,"label":"腓腹神経は主に脛骨神経由来の内側腓腹皮神経と総腓骨神経由来の交通枝から形成され、外果後方を走行する"},
 {"key":"C1_B","category_small":1,"label":"肩甲上神経は肩甲切痕で上肩甲横靱帯の下を通り、棘上筋と棘下筋を支配する"},
 {"key":"C1_C","category_small":1,"label":"橈骨神経深枝は回外筋を通過した後に後骨間神経となり、前腕伸筋群の多くを支配する"},
 {"key":"C1_D","category_small":1,"label":"大腿神経の伏在神経は運動枝を持たない純粋な感覚枝で、下腿内側から足部内側の知覚を担う"},
 {"key":"C2_A","category_small":2,"label":"低酸素肺血管収縮では肺胞低酸素の領域で肺小動脈が収縮し、血流を換気の良い肺胞へ再配分する"},
 {"key":"C2_B","category_small":2,"label":"Hering-Breuer肺膨張反射では肺伸展受容器から迷走神経を介する入力が吸息を抑制する"},
 {"key":"C2_C","category_small":2,"label":"末梢化学受容器である頸動脈小体は動脈血酸素分圧低下に強く反応し換気を促進する"},
 {"key":"C2_D","category_small":2,"label":"Bohr効果では二酸化炭素分圧上昇やpH低下によりヘモグロビンの酸素親和性が低下し組織への酸素放出が促進する"},
 {"key":"C7_A","category_small":7,"label":"Virchowの三徴は血流停滞、血管内皮障害、凝固能亢進であり静脈血栓形成の主要因となる"},
 {"key":"C7_B","category_small":7,"label":"アミロイドはCongo red染色で橙赤色に染まり、偏光下でapple-green birefringenceを示す"},
 {"key":"C7_C","category_small":7,"label":"乾酪壊死は結核などの肉芽腫性炎症でみられ、組織構築を失った白色チーズ状の壊死を形成する"},
 {"key":"C7_D","category_small":7,"label":"異形成では細胞の大小不同や核異型、極性の乱れがみられるが基底膜を越えた浸潤は必須ではない"},
]

def norm(s):
 s=unicodedata.normalize('NFKC',str(s or '')).lower()
 return re.sub(r'[^0-9a-zぁ-んァ-ヶ一-龠々ー]+','',s)

def read(name): return json.loads((BANK/name).read_text(encoding='utf-8-sig'))

def top(label, rows, text_key, id_key, n=5):
 a=norm(label); out=[]
 for r in rows:
  b=norm(r.get(text_key,''))
  if not b: continue
  score=SequenceMatcher(None,a,b,autojunk=False).ratio()
  out.append((score,str(r.get(id_key,'')),str(r.get(text_key,''))))
 out.sort(reverse=True)
 return [{"score":round(s,6),"id":i,"text":t} for s,i,t in out[:n]]

def main():
 nodes=read('knowledge_nodes.json'); questions=read('questions.json')
 if max(int(q['id'][1:]) for q in questions)!=1953: raise ValueError('requires Q1-Q1953')
 report=[]
 for c in CANDIDATES:
  nt=top(c['label'],nodes,'label','knowledge_node_id')
  qt=top(c['label'],questions,'question_text','id')
  report.append({**c,'top_nodes':nt,'top_questions':qt,'max_node_similarity':nt[0]['score'] if nt else 0,'max_question_similarity':qt[0]['score'] if qt else 0})
 OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps([{"key":r['key'],"node":r['max_node_similarity'],"question":r['max_question_similarity'],"top_node":r['top_nodes'][0]['id'] if r['top_nodes'] else None} for r in report],ensure_ascii=False,indent=2))
 return 0
if __name__=='__main__': raise SystemExit(main())
