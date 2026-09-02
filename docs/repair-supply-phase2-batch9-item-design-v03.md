# Repair Supply Phase2 batch9 item design v0.3

This document supersedes v0.2 for Q1646 only. Q1647-Q1650 remain exactly as defined in `docs/repair-supply-phase2-batch9-item-design-v02.md`.

## Why v0.3 exists
Q1612 already uses `task=finding_interpretation` and `primary_ability=INTERPRET` on the same canonical Node KN1151. Under the current formal `classify_repair_confirmation()` contract, Q1646 cannot be STRONG against Q1612 if it uses the same task and primary ability. Therefore Q1646 is redesigned without changing the classifier, without changing Q1612, and without adding a reviewed STRONG override.

## Q1646 -> KN1151 (revised)
- Source family: Q1164 / Q1221 / Q1612
- Category: A-3-O
- Safety: none
- Task: assessment_selection
- Primary ability: MEASURE
- Secondary ability: INTERPRET
- Level: 3
- Key: E
- Title: 障害受容・受容期の評価所見
- Theme: 障害受容モデルの受容期を支持する追加面接所見を選ぶ
- Knowledge node: 障害受容の5段階はショック、否認、混乱、解決への努力、受容の順

### Stem
障害受容を「ショック、否認、混乱、解決への努力、受容」の5段階で整理するモデルを用いる。脊髄損傷から1年が経過した患者は職場復帰しており、生活上の工夫も継続している。現在が「受容期」に相当するかを評価するため、追加で確認する面接所見として最も適切なのはどれか。

### Choices
A. 受傷時の出来事をほとんど思い出せず茫然としている
B. 「すぐ元どおりになるので障害への対応は不要だ」と話す
C. 感情の揺れが強く、現状をどう捉えるか定まらない
D. 福祉用具や復職方法を具体的に探し始めたばかりである
E. 残る制約を理解したうえで、必要な工夫を生活の一部として受け入れ、今後の生活像を自分の言葉で語れる

### Rationale
提示された5段階モデルでは、障害を含む現在の自分と生活を現実として引き受け、その状態を前提に今後の生活を自分のものとして語れる所見は「受容」を支持する。Dは「解決への努力」を支持する所見であり、Q1612が直接問う段階である。本問は段階名を症例から直接当てるのではなく、受容期を評価するために追加で確認すべき所見を選択させるため、assessment_selection / MEASURE とする。実際の心理過程は個人差が大きく、必ず直線的に進むものではないことを解説に明記する。

### STRONG requirement
- Q1646 vs Q1164 = different_question_strong
- Q1646 vs Q1221 = different_question_strong
- Q1646 vs Q1612 = different_question_strong
- Existing Q1164/Q1221/Q1612 relationships must remain unchanged.
- No reviewed STRONG-pair override.
- No classifier change.
- No Q1612 mutation.

## Q1647-Q1650
Use v0.2 unchanged.

## QA contract addition
Focused tests must assert Q1646 exact tags as `assessment_selection / MEASURE`, secondary ability `INTERPRET`, key E, and STRONG against Q1164/Q1221/Q1612 under the unmodified classifier.
