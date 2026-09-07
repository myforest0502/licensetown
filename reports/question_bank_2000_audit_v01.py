"""Offline audit: read tracked bank data, write only this audit's docs/reports.

Run from repository root: python -B reports/question_bank_2000_audit_v01.py
No app/database import, network, bank writes, or question creation.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from itertools import combinations
from question_bank import CATEGORY_NAMES, CATEGORY_LARGE_BY_SMALL
from knowledge_node_canonical import canonicalize_knowledge_node_id as canonical
from knowledge_node_repairability import build_repairability_audit, summarize_repairability
from knowledge_node_repair_evidence import classify_repair_confirmation, DIFFERENT_QUESTION_STRONG
from scripts.validate_question_bank import validate_question_bank
from scripts.check_question_bank_schema_manifest import check_schema_manifest

BANK = ROOT / 'data/question_bank'
def read(name):
    return json.loads((BANK / name).read_text(encoding='utf-8-sig'))
def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args]).decode('utf-8').strip()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

tracked = [ROOT / p for p in git('ls-files').splitlines() if not p.startswith(('docs/', 'reports/'))]
before = {str(p.relative_to(ROOT)): sha(p) for p in tracked}
validation = {'question_bank': validate_question_bank(), 'schema_manifest': check_schema_manifest()}
questions = read('questions.json')
tags = {t['id']: t for t in read('question_tags.json')}
qmap = {q['id']: q for q in questions}
expected = {f'Q{i}' for i in range(1, 1738)}
for filename in ['questions.json', 'answers.json', 'explanations.json', 'question_tags.json']:
    rows = read(filename)
    assert len(rows) == 1737 and {r['id'] for r in rows} == expected, filename
assert read('bank_manifest.json')['question_count'] == 1737
for q in questions:
    c = q['category_small']
    assert q['category_large'] == CATEGORY_LARGE_BY_SMALL[c]
    assert {'O': 'original', 'P': 'past_exam'}[q['source']] == tags[q['id']]['source']

TASKS = ['assessment_selection','device_selection','fact_recall','finding_interpretation','functional_goal_decision','intervention_selection','prognosis_prediction','safety_priority']
ABILITIES = ['KNOW','MEASURE','INTERPRET','PREDICT','PRESCRIBE','DECIDE']
TASK_PRIMARY = dict(zip(TASKS, ['MEASURE','PRESCRIBE','KNOW','INTERPRET','DECIDE','PRESCRIBE','PREDICT','DECIDE']))
for t in tags.values():
    assert TASK_PRIMARY[t['task']] == t['primary_ability']

# Editorial proposal, not fitted exam weights or generated question/tag records.
ADDS = [12,16,4,7,4,8,10,25,28,7,12,10,10,10,14,20,28,32]
TASK_PLAN = [
 [2,0,2,8,0,0,0,0], [2,0,2,9,0,1,1,1], [1,0,0,1,1,1,0,0],
 [2,0,0,2,1,1,1,0], [0,0,0,1,1,2,0,0], [1,0,0,2,1,1,0,3],
 [1,0,1,5,0,1,1,1], [4,0,0,6,1,5,2,7], [5,1,0,7,2,6,3,4],
 [1,0,0,2,1,1,0,2], [2,1,0,3,1,2,1,2], [2,0,0,3,2,2,0,1],
 [2,1,1,5,0,1,0,0], [3,0,0,4,0,2,1,0], [3,1,0,5,2,2,1,0],
 [3,2,0,4,1,5,1,4], [10,0,0,8,2,3,2,3], [3,3,0,4,4,10,2,6],
]
SINGLE_PLAN = [9,11,2,5,3,5,7,18,20,4,8,8,7,4,10,14,21,23]
MULTI_PLAN = [3,4,2,1,0,2,3,6,7,2,2,0,3,0,3,5,6,8]
SAFETY_PLAN = [(0,0),(0,2),(0,0),(0,1),(0,1),(1,3),(0,2),(6,7),(4,6),(1,2),(2,3),(0,2),(0,1),(0,1),(0,3),(4,4),(3,5),(5,10)]
REASONS = [
 '166問あるが132問が再生。新事実の羅列より既存概念の所見・評価への接続。',
 '159/170が再生、155問がLevel1。生理反応の解釈を優先し既存singletonを補強。',
 '25問で少数だがstrongあり。学習・行動の解釈と目標設定を限定補完。',
 '34問、再生25問。発達の観察・評価・見通しへ需要を変える。',
 '6問、original 0。教育場面の選択を小規模補完し、均等化はしない。',
 '51/69が再生。倫理・制度・管理の判断へ展開する。',
 '62/82が再生。病態の所見解釈へ接続する。',
 '170問中101問が再生。臨床判断・Safetyと既存概念の別問題を優先。',
 '118問でもstrong node 0。singleton・weak-onlyの異なる需要を最優先。',
 '40問中30問がLevel1。観察・対応判断の小規模補完。',
 '46問中40 singleton。発達だけでなく評価・介入・Safetyを接続。',
 '13問すべてpast_exam・singleton。評価・所見解釈・対応を補完。',
 '52/82が再生。力学の解釈・測定選択を厚くする。',
 '4問・original 0。分類境界確認後に臨床運動学固有の評価・解釈を補完。',
 'originalが95/120で既に厚い。量より未共有概念の別需要・目標判断に限定。',
 '113問に対しstrong nodeが4。再評価・介入・Safetyで別問題を用意。',
 '174問、139 singleton。評価選択→所見解釈→次の判断の独立した問題を補強。',
 '305問と最多だが271 singleton。広い新概念追加より既存治療概念のrepair供給。',
]
EXAM_IMPORTANCE = ['高・人体構造の基盤','高・機能理解の基盤','補完・心理/行動','中・発達/小児の基盤','補完・管理/教育','中・管理/制度','高・病態の基盤','高・内部障害','高・神経疾患','中・精神障害','中〜高・小児','中・臨床心理','高・運動学の基盤','高・運動学の応用','高・評価/動作','高・骨関節障害','高・評価学','高・治療学']
ADAPTIVE_IMPORTANCE = ['高・基礎から応用へ','高・再生偏重の是正','中・既存strongあり','中・singleton補完','中・少数を選択補完','中・判断の補完','高・所見への接続','高・Safety/解釈','最優先・strong不在','中・需要多様化','高・singleton/Safety','高・全singleton','高・測定/解釈','高・分類確認が先','中〜高・original既に厚い','最優先・repair薄い','最優先・評価/解釈','最優先・供給薄い']

nodes = build_repairability_audit()
node_by_id = {n['canonical_node_id']: n for n in nodes}
registry = read('knowledge_nodes.json')
groups = [r for r in registry if r['status'] == 'confirmed_shared']
global_counts = {}
for dim in ['source','task','primary_ability','secondary_ability','level','safety']:
    global_counts[dim] = dict(Counter(str(t.get(dim)) if t.get(dim) is not None else 'null' for t in tags.values()))
assert global_counts['source'] == {'original':643,'past_exam':1094}
categories = []
for c, name in CATEGORY_NAMES.items():
    qs = [q for q in questions if q['category_small'] == c]
    ids = {q['id'] for q in qs}
    ns = [n for n in nodes if ids.intersection(n['question_ids'])]
    within = [pair for n in ns for pair in n['strong_alt_pairs'] if set(pair) <= ids]
    incident = [pair for n in ns for pair in n['strong_alt_pairs'] if ids.intersection(pair)]
    local_strong_questions = {qid for p in incident for qid in p if qid in ids}
    local_counts = Counter(canonical(tags[qid]['knowledge_node_id']) for qid in ids)
    record = dict(category_small=c, category_large=CATEGORY_LARGE_BY_SMALL[c], category=name,total=len(qs))
    for dim, values in [('source',['original','past_exam']),('task',TASKS),('primary_ability',ABILITIES),('secondary_ability',ABILITIES+['null']),('level',['1','2','3','4']),('safety',['none','moderate','critical'])]:
        counts = Counter(str(tags[qid].get(dim)) if tags[qid].get(dim) is not None else 'null' for qid in ids)
        record[dim] = {v: counts[v] for v in values}
        assert sum(record[dim].values()) == len(qs)
    record.update(original_ratio=record['source']['original']/len(qs),past_exam_ratio=record['source']['past_exam']/len(qs),
      canonical_nodes=len(ns),singleton_nodes=sum(n['question_count']==1 for n in ns),multi_nodes=sum(n['question_count']>1 for n in ns),
      local_singleton_nodes=sum(v==1 for v in local_counts.values()),local_multi_nodes=sum(v>1 for v in local_counts.values()),
      questions_per_node=len(qs)/len(ns),strong_pairs_within_category=len(within),strong_pairs_incident=len(incident),
      nodes_with_strong_pair=sum(bool(n['strong_alt_pairs']) for n in ns),
      weak_only_nodes=sum(n['classification']=='weak_alt_question_only' for n in ns),
      questions_with_strong_alternative=len(local_strong_questions),question_strong_coverage=len(local_strong_questions)/len(qs),
      node_ids=[n['canonical_node_id'] for n in ns],
      recheck_repair_structure=f'{len(local_strong_questions)}/{len(qs)}問にstrong別問題あり。その他は同一問題の再確認またはweak/candidateに留まる。',
      exam_importance=EXAM_IMPORTANCE[c-1],adaptive_importance=ADAPTIVE_IMPORTANCE[c-1],
      proposed_original=ADDS[c-1],after_original_addition=len(qs)+ADDS[c-1],allocation_reason=REASONS[c-1],
      proposed_tasks=dict(zip(TASKS,TASK_PLAN[c-1])),
      proposed_nodes={'existing_singleton_second':SINGLE_PLAN[c-1],'existing_multi_reinforce':MULTI_PLAN[c-1],'new_node':ADDS[c-1]-SINGLE_PLAN[c-1]-MULTI_PLAN[c-1]})
    assert sum(TASK_PLAN[c-1]) == ADDS[c-1]
    l1 = record['proposed_tasks']['fact_recall']
    l4 = round(ADDS[c-1]*(0.25 if c in [8,9,11,16,17,18] else 0.15))
    l2 = round(ADDS[c-1]*0.32)
    record['proposed_levels'] = {'1':l1,'2':l2,'3':ADDS[c-1]-l1-l2-l4,'4':l4}
    critical, moderate = SAFETY_PLAN[c-1]
    record['proposed_safety'] = {'critical':critical,'moderate':moderate,'none':ADDS[c-1]-critical-moderate}
    assert critical+moderate >= record['proposed_tasks']['safety_priority']
    record['priority'] = 'A' if c in [8,9,11,12,14,16,17,18] else 'B'
    candidates = sorted((n for n in ns if n['question_count']==1),key=lambda n:(-max({'none':0,'moderate':1,'critical':2}[s] for s in n['safety']),n['canonical_node_id']))
    record['example_singleton_candidates']=[{'node':n['canonical_node_id'],'question_ids':n['question_ids'],'label':n['knowledge_node_labels'][0],'task':n['tasks'],'safety':n['safety']} for n in candidates[:2]]
    record['example_weak_only_candidates']=[{'node':n['canonical_node_id'],'question_ids':n['question_ids']} for n in ns if n['classification']=='weak_alt_question_only'][:2]
    assert record['proposed_nodes']['existing_singleton_second']<=record['singleton_nodes']
    assert all(v>=0 for d in ['proposed_nodes','proposed_levels','proposed_safety'] for v in record[d].values())
    categories.append(record)

plan = {}
for dim in ['proposed_tasks','proposed_levels','proposed_nodes','proposed_safety']:
    count=Counter()
    for c in categories: count.update(c[dim])
    assert sum(count.values())==257
    plan[dim]=dict(count)
plan['primary_ability']=dict(Counter())
ability=Counter()
for task,n in plan['proposed_tasks'].items(): ability[TASK_PRIMARY[task]]+=n
plan['primary_ability']=dict(ability)
plan['priority']={p:sum(c['proposed_original'] for c in categories if c['priority']==p) for p in ['A','B','C']}
plan['overlapping_intent']={'strong_pair_forming_questions':224,'singleton_strong_questions':179,'multi_strong_questions':45,'distinct_weak_only_nodes_target':40,'safety_questions':sum(plan['proposed_safety'][k] for k in ['critical','moderate'])}
assert sum(ADDS)==257 and 643+257==900 and 1094+6==1100 and 1737+257+6==2000

# Bipartite capacity check: a cross-category weak node must not consume two slots.
# This proves only structural feasibility; it does not approve clinical content.
slots=[(c['category_small'],i) for c in categories for i in range(c['proposed_nodes']['existing_multi_reinforce'])]
eligible={n['canonical_node_id']:{qmap[qid]['category_small'] for qid in n['question_ids']} for n in nodes if n['classification']=='weak_alt_question_only' and n['canonical_node_id']!='KN0779'}
matched={}
def match(node,seen):
    for slot in slots:
        if slot[0] not in eligible[node] or slot in seen: continue
        seen.add(slot)
        if slot not in matched or match(matched[slot],seen):
            matched[slot]=node
            return True
    return False
capacity=sum(match(node,set()) for node in sorted(eligible))
assert capacity>=40
validation['distinct_weak_node_capacity_within_category_multi_slots']=capacity

exam_index=defaultdict(list)
exam_counts=Counter()
exam_by_category=defaultdict(Counter)
for q in questions:
    if tags[q['id']]['source']=='past_exam':
        e=q['exam']; assert e and set(['exam_no','session','question_no'])<=set(e)
        key=f"{e['exam_no']}{e['session']}{e['question_no']}"
        exam_index[key].append(q['id']); exam_counts[e['exam_no']]+=1
        exam_by_category[e['exam_no']][str(q['category_small'])]+=1
source_audits={p.name:json.loads(p.read_text(encoding='utf-8-sig')) for p in BANK.glob('*source_audit.json')}
holds=[]
for filename,rows in source_audits.items():
    for row in rows:
        if row.get('decision')=='HOLD':
            holds.append({'audit_file':filename,'source_key':row.get('source_key'),'reason':row.get('reason',row.get('change_reason')),'currently_present_question_ids':exam_index.get(row.get('source_key'),[])})
all_strong={tuple(sorted(p)) for n in nodes for p in n['strong_alt_pairs']}
cross_pairs=[p for p in all_strong if qmap[p[0]]['category_small']!=qmap[p[1]]['category_small']]
cross_nodes=[n for n in nodes if len({qmap[qid]['category_small'] for qid in n['question_ids']})>1]
canonical_registry={canonical(n['knowledge_node_id']) for n in registry}
unrepresented=sorted(canonical_registry-set(node_by_id))
summary=summarize_repairability(nodes)
summary.update(registry_raw_nodes=len(registry),registry_canonical_nodes=len(canonical_registry),unrepresented_canonical_nodes=unrepresented,confirmed_shared_registry_groups=len(groups),confirmed_shared_registry_questions=len({qid for n in groups for qid in n['question_ids']}),strong_unordered_pairs=len(all_strong),cross_category_strong_pairs=len(cross_pairs),cross_category_nodes=len(cross_nodes),question_with_strong_alternative_count=len({qid for p in all_strong for qid in p}))
cross_source={}
for source in ['original','past_exam']:
    cross_source[source]={dim:dict(Counter(str(t.get(dim)) if t.get(dim) is not None else 'null' for t in tags.values() if t['source']==source)) for dim in ['task','primary_ability','secondary_ability','level','safety']}
facts={'baseline_main_sha':git('merge-base','HEAD','origin/main'),'manifest':read('bank_manifest.json'),'current':global_counts,'knowledge_nodes':summary,'categories':categories,'source_cross_tabs':cross_source,'proposal':plan,'node_evidence':nodes,'exam_counts':dict(sorted(exam_counts.items())),'exam_category_counts':{str(k):dict(v) for k,v in sorted(exam_by_category.items())},'duplicate_exam_keys':{k:v for k,v in exam_index.items() if len(v)>1},'past_exam_hold_evidence':holds,'input_sha256':before,'validation':validation,'definitions':{'singleton':'global canonical question count == 1','multi':'global canonical question count >= 2','strong_pair':'unordered distinct same-canonical pair classified by current production function','weak_only':'multi node with no strong pair','within_category':'both endpoints in category; additive','incident':'at least one endpoint in category; cross-category pair is counted twice across rows','category_node_counts':'incidence; cross-category nodes overlap','question_per_node':'category questions / category represented canonical nodes','clinical_reasoning_proxy':'task metadata; not content quality or psychometric validation','db_access':'none'}}

OUT=ROOT/'reports'
OUT.mkdir(exist_ok=True)
(OUT/'question_bank_2000_gap_analysis_v01.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
flat=[]
for c in categories:
    row={k:v for k,v in c.items() if not isinstance(v,(list,dict))}
    for k,v in c.items():
        if isinstance(v,dict): row.update({f'{k}.{a}':b for a,b in v.items()})
    flat.append(row)
with (OUT/'question_bank_2000_distribution_v01.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)

def table(headers, rows):
    def cell(x):return str(x).replace('|','／').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(cell,headers))+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(cell,row))+' |' for row in rows])+'\n'
def pct(n,d):return f'{n/d*100:.1f}%'
def dimtable(dim, keys):
    return table(['ID','分野']+keys,[[c['category_small'],c['category']]+[c[dim][k] for k in keys] for c in categories])
def mix(dim, proposed):
    rows=[]
    for key,add in proposed.items():
        cur=global_counts[dim].get(key,0)
        rows.append([key,cur,pct(cur,1737),add,cur+add,pct(cur+add,1994)])
    return table(['項目','現行','現行比率','追加案','+257後','+257後比率'],rows)

sections=[]
def section(n,title,text):sections.append(f'## {n}. {title}\n\n{text.strip()}\n')
section(1,'Executive Summary',f'''
監査基準は現行main `{facts['baseline_main_sha']}`。Q1〜Q1737を四ストアから再集計し、original 643 / past_exam 1094 / total 1737を確認した。問題・タグ・Node・answers・explanations・DB・Productionの変更は一切行わない。

最大の不足は問題総数ではなく、canonical Node 1508中1305（{pct(1305,1508)}）がsingletonであること。strong別問題ありは149 Node、weak-onlyは54 Node、strong unordered pairは177。神経医学は118問あるのにstrong pairが0、治療各論は305問あってもstrongありは6 Nodeである。

original +257は既存singletonの2問目179、既存multi補強57、新規Node21に配分。単純再生は6問に限定し、Level2〜4を251問とする。strong pair形成224問、Safety補強{plan['overlapping_intent']['safety_questions']}問はこれらに重なる設計意図であり、別枠加算しない。

不足TOP5は治療各論、神経医学、評価各論、運動器、臨床運動学。過多TOP5は「不要な分野」ではなく再生型の供給集中として、生理学、解剖学、内科学、病理学、医学概論。教育学・臨床心理学の少数性も別途補完する。
''')
section(2,'Current State Q1-Q1737',f'''
{table(['検査','結果'],[['範囲/件数','Q1〜Q1737 / 1737'],['questions / answers / explanations / question_tags','各1737・ID集合一致・重複/欠番0'],['source整合','questions: O/P と tags: original/past_exam が全件一致'],['分類整合','category_small 1〜18とcategory_large A/B/Cが全件一致'],['task/primary整合','現行の8 task / 6 ability対応と全件一致'],['DB接続','0（app/databaseをimportしない）']])}
入力は data/question_bank 配下と既存の読み取り専用モジュール。保存済みquestion_tags_audit.txtを数値の代用にせず、実データを集計した。全体task/ability/level/safety、registry 1538・canonical 1508・singleton 1305・multi 203・confirmed-shared 186/385は依頼時の参考値と一致。

再現: リポジトリルートで `python -B reports/question_bank_2000_audit_v01.py`。標準ライブラリと既存の読み取り専用bank/Node関数のみ使用。入力ハッシュ、全Nodeのpair根拠、分野別全件数は補助JSONに保存する。本稿はタグによる構造監査であり、1737問の医学的妥当性・正答率・識別力を全件審査した結果ではない。
''')
section(3,'18-Category Distribution',f'''
正式マッピングは `question_bank.py:CATEGORY_NAMES / CATEGORY_LARGE_BY_SMALL`。分類キーはquestions.jsonのcategory_smallであり、titleや文章から再分類しない。依頼の「解剖」は正式表示「解剖学」、「神経」は「神経医学」、「動作分析」は「動作分析学」に対応する。A=1〜6 基礎、B=7〜12 専門基礎、C=13〜18 専門。

{table(['ID','群','正式分野','総数','original','past_exam','original比率','past_exam比率'],[[c['category_small'],c['category_large'],c['category'],c['total'],c['source']['original'],c['source']['past_exam'],pct(c['source']['original'],c['total']),pct(c['source']['past_exam'],c['total'])] for c in categories])}
18分野合計=1737。後続のtask・ability・level・safetyは各分野の総数と一致する（secondaryのnullも1件として含む）。
''')
section(4,'Source Balance',f'''
original 643（{pct(643,1737)}）、past_exam 1094（{pct(1094,1737)}）。教育学・臨床心理学・臨床運動学はoriginalが0。生理学は19/170に対して動作分析学は95/120であり、sourceを一律50:50に揃える設計は採らない。

{table(['source','再生','評価選択','所見解釈','介入選択','Level1','Safety critical/moderate'],[[s,*[cross_source[s]['task'].get(t,0) for t in ['fact_recall','assessment_selection','finding_interpretation','intervention_selection']],cross_source[s]['level'].get('1',0),f"{cross_source[s]['safety'].get('critical',0)}/{cross_source[s]['safety'].get('moderate',0)}"] for s in ['original','past_exam']])}
original/past_examと質を同一視しない。過去問の事実確認にも試験範囲を支える価値があり、originalは独立した需要・場面を補う役割に使う。+257だけの時点では900/1094/1994、過去問+6を別工程で受け入れて900/1100/2000となる。
''')
section(5,'Task / Ability Balance',f'''
taskを臨床推論の代理指標として使用する。fact_recall 881/1737={pct(881,1737)}。assessment・finding・interventionは合計704問。functional_goal_decision 17、prognosis_prediction 5は少ないが、予後を断定できる設問を無理に増やす根拠にはしない。

### task別：18分野
{dimtable('task',TASKS)}
### primary ability別：18分野
{dimtable('primary_ability',ABILITIES)}
### secondary ability別：18分野
{dimtable('secondary_ability',ABILITIES+['null'])}
secondary nullは1189/1737。未付与を直ちに欠陥としない。追加時も真に要求する副次能力だけを付与し、nullを埋めるためのタグ追加はしない。primaryはtaskとの現行対応を維持する。タグ上INTERPRETでも文章・選択肢が答えを示唆していれば臨床推論の実効性は低い。作問時の内容レビューが必要。
''')
section(6,'Difficulty Balance',f'''
Level1 859、Level2 188、Level3 593、Level4 97。Level1比率は{pct(859,1737)}。生理・解剖・病理のLevel1集中と、Level2の橋渡し問題不足を優先して扱う。

{dimtable('level',['1','2','3','4'])}
levelは既存タグの段階でありIRT難易度や実測正答率ではない。今回の配分は設計目標で、文章を長くすることでLevelを上げない。既存levelは変更しない。
''')
section(7,'Safety Balance',f'''
critical 65、moderate 232、none 1440。安全関連は297/1737={pct(297,1737)}。safety_priority task（86）とSafety属性（297）は異なる軸である。

{dimtable('safety',['critical','moderate','none'])}
解剖・生理などのnoneを一律に埋めない。臨床上のリスクを判断する内科・神経・評価・治療・運動器を中心に補強する。Safety付与も正答を明白にする危険な誤選択肢の水増しも避ける。

追加Safety案（task/Node配分と重複する）：{json.dumps(plan['proposed_safety'],ensure_ascii=False)}。Safetyあり{plan['overlapping_intent']['safety_questions']}問。分野別配分はCSV/JSONに記録。安全性を必要としない問題への形式的タグ付与は禁止。
''')
section(8,'Knowledge Node Coverage',f'''
{table(['指標','再集計'],[[k,v] for k,v in summary.items() if k in ['registry_raw_nodes','registry_canonical_nodes','canonical_node_count','singleton_node_count','multi_question_node_count','confirmed_shared_registry_groups','confirmed_shared_registry_questions','strong_unordered_pairs','cross_category_nodes','cross_category_strong_pairs','question_with_strong_alternative_count']])}
**1538−1508=30を未収録Nodeと解釈してはいけない。** raw registryを正式canonical aliasで解決すると1508になり、質問未対応のcanonical registry Nodeは0。30はalias解決による差である。registry coverageは100%でも、国家試験出題基準の概念coverageが100%とは限らない。新規Node21枠は後工程で出題基準と既存最小概念を照合する予算であり、現時点で21概念の欠落を確定したものではない。

全体問題/Node=1737/1508={1737/1508:.3f}。以下の分野別Node数は**所属する問題があるNodeの延べ数**。複数分野Nodeがあるため列合計を全体1508と比較しない。singleton/multiはバンク全体で判定。問題/Nodeは分野内問題数÷その分野のNode数。CSVには分野内だけでsingleton判定した別指標も保存する。

{table(['ID','分野','canonical','global singleton','global multi','分野内問題/Node'],[[c['category_small'],c['category'],c['canonical_nodes'],c['singleton_nodes'],c['multi_nodes'],f"{c['questions_per_node']:.3f}"] for c in categories])}
''')
section(9,'Singleton / Repair Opportunity Analysis',f'''
現行 `knowledge_node_repair_evidence.classify_repair_confirmation` で同一canonical内の異なるID全組合せを判定した。STRONGは正式reviewed pair、またはtask/primary需要が異なるpair。無向pairは1回だけ数え、同じ問題の反復は含めない。意味の似た文章を機械的に同一Nodeとみなさない。

strong pair=177、strongありNode=149、weak-only=54。1359 Nodeにstrong別問題がない。分野内pairは両端が同じ分野、関連pairは少なくとも片端がその分野。後者とNode列は分野間重複あり。strong対象問数はその問に直接strong edgeがある場合のみ数える（Nodeの別の2問にstrongがあるだけでは対象としない）。

{table(['ID','分野','分野内strong pair','関連strong pair','strongありNode','weak-only Node','strong対象問/総数'],[[c['category_small'],c['category'],c['strong_pairs_within_category'],c['strong_pairs_incident'],c['nodes_with_strong_pair'],c['weak_only_nodes'],f"{c['questions_with_strong_alternative']}/{c['total']}"] for c in categories])}
{sum(c['strong_pairs_within_category'] for c in categories)}分野内pair + {len(cross_pairs)}分野間pair = 177。weak-onlyは「複数問あるがstrongがないNode」であり、singletonは含めない。

recheckは同じ問題でも想起確認として利用できるが、repair完了の別問題evidenceとは別。PREREQUISITE/TRANSFER候補・written候補は現行実装上正式repairに自動昇格しない。KN0779（Q787/Q1579）は意図的WEAKであり、本案でも強制STRONG化しない。DBの誤答履歴・自信・cooldown・修復中状態にはアクセスしていないため、今回の「可能」は静的供給であり、利用者ごとの出題可能性・repair完了実績ではない。

### 内容レビュー開始点（未承認の参照候補、問題の作成/変更なし）
{table(['分野','singleton参照Node / 既存Q','weak-only参照Node / 既存Q'],[[c['category'],'; '.join(x['node']+' '+','.join(x['question_ids']) for x in c['example_singleton_candidates']),'; '.join(x['node']+' '+','.join(x['question_ids']) for x in c['example_weak_only_candidates']) or 'なし'] for c in categories])}
上表はSafety高→Node ID順の例であり257問の確定作問対象ではない。ラベル・既存task・Safety・全pairはJSONで追跡可能。後工程では同じ最小知識を別の場面/需要で試せるかを全候補で確認する。
''')
section(10,'Weak Areas',f'''
構造・教育価値の総合不足TOP5（編集判断、国家試験の公式順位ではない）：

{table(['順位','分野','不足の根拠','処方'],[[1,'理学療法治療各論','305問/271 singleton/strongあり6 Node','同一概念の再評価・介入変更・Safety'],[2,'神経医学','118問/105 singleton/strong pair 0','異なる需要によるrepair供給'],[3,'理学療法評価各論','174問/139 singleton','評価選択と解釈の独立問題'],[4,'運動器','113問/92 singleton/strongあり4 Node','臨床判断・repair補強'],[5,'臨床運動学','4問/original 0/strong 0','分類境界確認後の少数分野補強']])}
絶対数の少ない順は臨床運動学4、教育学6、臨床心理学13、心理学25、人間発達学34。少数だから他分野と同数にするのではなく、試験範囲との関係とadaptiveの供給構造を別々に評価する。

### 試験上の重要性とadaptive上の重要性
{table(['分野','国家試験上の設計評価','adaptive上の評価'],[[c['category'],c['exam_importance'],c['adaptive_importance']] for c in categories])}
根拠資料は[厚労省・令和6年版出題基準](https://www.mhlw.go.jp/content/10803000/000920163.pdf)の対応表（PDF p8）とPT専門分野（PDF p23〜39）、および[国家試験の試験科目](https://www.mhlw.go.jp/kouseiroudoushou/shikaku_shiken/rigakuryouhoushi/)（参照2026-09-08）。評価・治療・運動学・臨床医学・管理/教育が対象範囲に含まれることを確認した。上表の高/中/補完は本監査の設計判断で、18分類別の公式出題率ではない。全国出題頻度・配点の18分類再集計は実施していない。

臨床運動学の4問はQ562/Q997/Q1037/Q1280で、評価選択2・再生2。動作分析120問や基礎運動学82問に関連概念が存在し得るため、分類ラベルの希少性だけで臨床運動学の学習内容が完全に欠けていると断定しない。既存分類の変更は行わない。
''')
over=sorted(categories,key=lambda c:c['task']['fact_recall']**2/c['total'],reverse=True)[:5]
section(11,'Overrepresented Areas',f'''
「過多」は不要な分野・削除候補を意味しない。fact_recall件数×分野内fact_recall比率を供給集中の単純な説明指標として順位付けした（国家試験重みではない）。

{table(['順位','分野','総数','再生数/比率','Level1数/比率'],[[i,c['category'],c['total'],f"{c['task']['fact_recall']} / {pct(c['task']['fact_recall'],c['total'])}",f"{c['level']['1']} / {pct(c['level']['1'],c['total'])}"] for i,c in enumerate(over,1)])}
生理・解剖は試験基盤として維持するが再生の横増しは抑制。内科は量があってもSafetyと所見解釈が不足し得るため+25を配分。治療各論は最多305問だが、singleton過多のため追加を止めず補強先を既存概念に絞る。動作分析学はoriginal比率79.2%と高いため+14に抑え、別需要のrepairに限定する。
''')
section(12,'Proposed +257 Original Question Allocation',f'''
均等配分ではなく、臨床判断・Safety・repairが重要な分野に重点配分する。数値は編集上の予算案であり、問題やタグを確定したものではない。カテゴリ境界を尊重し、原稿の内容が別分類になるなら実装前に配分表全体を再整合する。

{table(['ID','分野','現在総数','original','past_exam','追加original','追加後総数','追加理由'],[[c['category_small'],c['category'],c['total'],c['source']['original'],c['source']['past_exam'],c['proposed_original'],c['after_original_addition'],c['allocation_reason']] for c in categories]+[['合計','',1737,643,1094,257,1994,'過去問+6は別工程']])}
''')
section(13,'Proposed Task Mix for +257',f'''
{mix('task',plan['proposed_tasks'])}
合計257。fact_recallは6/257で、追加後887/1994={pct(887,1994)}。過去問6が全て再生でも893/2000=44.65%となり現行50.72%を下回る。評価・所見解釈・介入の合計は{sum(plan['proposed_tasks'][t] for t in ['assessment_selection','finding_interpretation','intervention_selection'])}問。

### 分野×追加task（各行はその分野の追加数と一致）
{dimtable('proposed_tasks',TASKS)}
### task対応から導く追加primary ability
{mix('primary_ability',plan['primary_ability'])}
secondaryは個々の設問で必要性を判断し、無意味な比率目標を置かない。taskとprimaryは現行対応を維持。予後は提示情報で妥当な見通しを選べる問題に限り、曖昧な予測を作らない。
''')
section(14,'Proposed Difficulty Mix for +257',f'''
{mix('level',plan['proposed_levels'])}
合計257、Level2〜4は251問。分野ごとにLevel2を約32%、Level4を臨床重点分野では約25%・他では約15%とした初期予算で、残りをLevel3に配分。Level1は基礎的な独立概念の再生6問のみとした。丸めは分野ごとの整数で処理し、各行の残数をLevel3に置く。

{dimtable('proposed_levels',['1','2','3','4'])}
既存のlevel値を再推定しない。追加項目の最終levelは既存schema/内容レビューと一致させ、現場での正答率・識別力の評価は別工程とする。
''')
section(15,'Proposed Knowledge Node Strategy',f'''
### Exclusive allocation（排他的・合計257）
{table(['用途','追加問数','設計条件'],[['既存singleton Nodeの2問目',179,'179個の異なる既存singletonへ各1問。異なる需要でstrongを狙う'],['既存multi Nodeの補強',57,'weak-only40 Nodeへの各1問を第一目標、残り17問は既存strong Nodeの第三需要等'],['新規Knowledge Node',21,'既存最小概念との重複/aliasを否定できた場合のみ。未確定のcoverage予算']])}
{dimtable('proposed_nodes',['existing_singleton_second','existing_multi_reinforce','new_node'])}
### Overlapping intent（上表に重なる目的・加算不可）
- strong repair pair形成を狙う追加問題224問 = singleton179 + multi45。multi45のうち40は異なるweak-only Nodeの補強、5は既存strong Nodeの追加需要。224はpair総数ではなく、少なくとも1本の新しいstrong edgeを狙う問題数である。1問から複数pairが生じても問数を増やさない。
- Safety補強{plan['overlapping_intent']['safety_questions']}問 = critical {plan['proposed_safety']['critical']} + moderate {plan['proposed_safety']['moderate']}。strong形成224問や新規Node21問との重複を許す。taskのsafety_priorityとは同一ではない。
- singleton減少・臨床推論の強化は同じ257問の効果で、追加枠ではない。

既存weak-onlyは54 Node。KN0779は除外し、残る53から40の異なるNodeを後工程で選ぶ。分野別multi57枠は分野をまたぐNodeを重複選択しないよう照合し、1問が既存の両方の誤答問題に対して独立した理解を要求するか確認する。正式STRONG判定だけで医学的/教育的にstrongと認定しない。

179 singletonがすべてstrong化し、新規Node21がすべて独立して各1問なら、+257時点でcanonical 1529、singleton 1147、multi 382、問題/Node=1994/1529={1994/1529:.3f}。weak-only40が別Nodeとしてstrong化した場合、strongありNodeは149+179+40=368、weak-onlyは54−40=14。これらはレビュー成功時の設計シナリオであり実績でも保証でもない。過去問+6によるNode変化は未確定なので含めない。
''')
section(16,'Priority A / B / C',f'''
{table(['優先度','追加枠','範囲/判断'],[['A',plan['priority']['A'],'内科・神経・小児・臨床心理・臨床運動学・運動器・評価各論・治療各論。Safety/repair/臨床判断を優先'],['B',plan['priority']['B'],'基礎概念の応用、人間発達・教育・医学概論・精神・動作分析などの補完'],['C',0,'同一需要の単語再生追加、既存場面の数値だけ変更、無関係な新規Node。今回は配分しない']])}
Aは合格・adaptiveの設計上の効果を重視した分類であり実証済みの合格率改善ではない。A分野でも独立性が乏しい個別原稿は採用しない。B分野のSafety/強いrepair候補が見つかれば作業順は繰り上げてよい。総枠257と各分野配分を変更する場合は改訂版で再計算する。
''')
section(17,'Past Exam +6 Candidate Strategy',f'''
今回は作成・追加しない。1094件のexam（回数・午前午後・問番号）は全件存在し、重複キーは{len(facts['duplicate_exam_keys'])}件。以下は収録実績であり、200問から差し引いた数を「欠損」と断定しない。画像問題・採点除外・OCR品質・収録方針が未確認のためである。

{table(['試験回','暦年（1965+回数）','収録数'],[[n,1965+n,v] for n,v in sorted(exam_counts.items())])}
第一探索群は第60回（2025、63問）・第59回（2024、91問）・第61回（2026、117問）。最近の範囲と既存少数収録を併せて探索する。第53回（2018）は収録0であるが、未収録理由を調べる探索枠であって自動優先採用枠ではない。第47〜51回は過去監査があるため出典追跡が容易だが、HOLDを採用済みと扱わない。

6枠の探索方針は、神経2、評価1、内科1、臨床心理または臨床運動学1、治療Safety1（合計6）。採用される過去問の正式分類に従う探索枠であり、分野や年度に合うよう問題を改変しない。優先する欠損タイプは、本文と正答が公式資料で確認可能な未収録問題、OCR再抽出で完全復元できるもの、既存singleton/weak-onlyと最小概念が一致し独立した需要を持つもの。図欠損・解答訂正・複数概念・既収録キーは別扱いにする。

既存source auditのHOLDは{len(holds)}記録（同じsource_keyの重複記録あり）。例：50午前93は既存Nodeとの最小概念不一致、49午後48は複数尺度、51午後99は症候と髄液所見の不一致。単なる未取得ではなく意味上の保留なので再利用に厳格な確認が必要。EXCLUDED_DUPLICATEは追加候補に戻さない。公式問題・最終正答・採点除外情報を突合し、回/午前午後/問番号と本文近似の双方で重複を除外する。今回、具体的な6問の採用適否や公式原本との一致は確定していない。
''')
section(18,'Risks','''
- 分類名の少数性と概念欠損は異なる。特に臨床運動学・動作分析・基礎運動学の境界を内容レビューする。分類を勝手に変更しない。
- raw registry 1538とcanonical 1508の差30は未収録枠ではない。Nodeの粒度・alias・confirmed_sharedは別軸。
- STRONGは現行メタデータ上の静的関係。自信のある誤答、修復中、cooldown等の実際の需要を読んでいないため、学習者別の供給不足TOP5ではない。
- fact_recall以外のtaskや高levelでも質を保証しない。焼き直し、正答の手掛かり、危険すぎる誤選択肢を内容レビューで除外する。
- 257問の整数配分は最適化モデルの解ではなく設計判断。公式18分野出題頻度や学習ログの効果測定に基づく配点ではない。
- strong形成224/Safety補強は重なる目的。exclusive 179+57+21だけが問題数の分割。新規Node21の意味的不足は未確定。
- KN0779の意図的WEAKを維持。書面/関係Node経由を勝手に正式repairへ昇格しない。
- 後工程の問題追加にはmanifest/schemaの1737件上限などの契約変更が必要になるが、今回変更しない。Q番号やタグを先行発行しない。
- 過去問6のtask/level/source以外の属性は未確定。最終2000問時点の正確なtask/level内訳を捏造しない。
''')
section(19,'Recommended Creation Order','''
1. 神経・治療・評価・運動器のsingleton/weak-onlyから、Safetyを含む最小概念が明確な対象を選ぶ。最初は8〜12問程度の小ロットで独立性を確認する。
2. 同じNodeの既存問題とtask/primary/必要な思考を比較し、strong形成を狙う。weak-only40 Nodeの補強はKN0779を避け、全体で重複を除く。
3. 内科・小児の評価/所見/介入とSafetyを補強する。A分野の臨床心理・臨床運動学は分類境界を確認してから進める。
4. B分野の基礎概念を応用へ接続し、既存singleton179・multi57の枠を充足する。原稿ごとに正答根拠、全誤選択肢、別問題としての独立性、既存正式Node適合を確認する。
5. coverage照合後にのみ新規Node21枠を判断する。重複する概念しか見つからない場合は無理に新設せず配分改訂案を作る。
6. 過去問+6は別トラックで公式原本・最終正答・欠損/重複を確認する。各ロットの受入時に257枠残数、分野/task/level/Nodeの合計を再監査する。

以上は将来の作問順であり、このPRでは原稿・解答・解説・タグ・Nodeを追加しない。
''')
section(20,'Final Exact Totals',f'''
{table(['指標','整数確認'],[['current total',1737],['current original',643],['current past_exam',1094],['planned new original',257],['planned additional past_exam',6],['final original','643 + 257 = 900'],['final past_exam','1094 + 6 = 1100'],['final total','1737 + 257 + 6 = 2000'],['18分野の追加合計',sum(ADDS)],['追加task合計',sum(plan['proposed_tasks'].values())],['追加level合計',sum(plan['proposed_levels'].values())],['exclusive Node配分','179 + 57 + 21 = 257'],['Priority配分',f"{plan['priority']['A']} + {plan['priority']['B']} + 0 = 257"]])}
追加ファイルは `docs/question-bank-2000-audit-v01.md`、`reports/question_bank_2000_distribution_v01.csv`、`reports/question_bank_2000_gap_analysis_v01.json`、再現用 `reports/question_bank_2000_audit_v01.py` のみ。既存Question Bank本体・answers・explanations・question_tags・Knowledge Node・Production・DBの変更0。再現スクリプトはdocs/reports以外の追跡ファイルを実行前後にハッシュ照合し、既存入力の不変性を検査する。
''')
rendered='# Question Bank 2000: Gap Audit v01\n\n分析・監査・配分設計のみ / 2026-09-08\n\n'+'\n'.join(sections)
rendered=re.sub(r'(### [^\n]+)\n(?=[|*-])',r'\1\n\n',rendered)
rendered += f'\n検証: 既存Question Bank validatorとschema/manifest checkerはPASS。分野別multi枠57内で、KN0779を除外し分野間Node重複を排除したweak-only Nodeの構造上の割当可能数は{capacity}。目標40は容量内だが、作問可能性・臨床的独立性は別途レビューする。\n'
(ROOT/'docs/question-bank-2000-audit-v01.md').write_text(rendered,encoding='utf-8')
assert before == {str(p.relative_to(ROOT)):sha(p) for p in tracked}, 'Tracked non-report file changed'
assert sum(c['total'] for c in categories)==1737
assert sum(c['strong_pairs_within_category'] for c in categories)+len(cross_pairs)==177
print(json.dumps({'status':'PASS','current':global_counts,'nodes':summary,'plan':plan,'outputs':4},ensure_ascii=True,indent=2))
