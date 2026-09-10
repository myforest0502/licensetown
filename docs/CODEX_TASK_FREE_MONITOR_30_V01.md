# Codex Task — Free Monitor 30 v0.1

## 最重要：開始条件

**使用量の残数に対して途中で残数不足になるようなら開始してはならない。**

開始前に、この作業を最後まで完了できるだけのCodex使用量が残っていると判断できる場合だけ開始すること。
**使用量が途中で0になり、作業が中断する可能性があると判断した場合は、何も変更せず作業を開始しないこと。**
その場合は「残使用量の都合で開始していない」とだけ報告すること。

---

## 作業branch

`feature/free-monitor-30-v01`

必ずremoteをfetchし、このbranchの最新HEADから作業すること。force push禁止。

## 今回のゴール

1. 公開HPで **「無料モニター 先着30名限定」** と明確に告知できるようにする。
2. 無料モニター枠をDBで最大30名に制限し、**31人目の新規利用者が無料利用を開始できない**ようにする。
3. 既存利用者の学習・履歴・通常利用を壊さない。
4. 告知と制限機構は同じreleaseで本番反映できる状態にする。告知だけ先行公開しない。

## 商品成立の判定条件

- HPを初めて見た人が「無料モニターは先着30名」と理解できる。
- 30枠が埋まった状態で新規31人目は登録完了できない。
- 同時登録でも30を超えない（race conditionを許さない）。
- 同一LINE user_idは再登録・リセットで新しい枠を重複消費しない。
- 既存の利用者は今回の変更で突然利用不能にならない。
- 既存の学習履歴、question_attempts、合格への道、通常学習フローに意味変更がない。
- 公開HPの既存レスポンシブレイアウトを壊さない。
- 関連テスト・全体テスト・Question Bank validatorが通る。

## 今回はやらないこと

- HP全面リニューアル
- 課金・Stripe本格実装
- 残り人数のリアルタイム公開表示
- 待機リスト機能
- メール通知
- Phase11の本番昇格
- Question Bank本文・正答・選択肢の変更
- 合格への道UIの再配置
- SEO対策（このtask完了後に別taskで行う）
- 無関係なrefactor / cleanup

---

# 1. HP告知

公開HPのfrozen preview HTMLを直接改変せず、現在の`site_ui.py`のpublic runtime transformation方針を維持すること。

公開ページに以下の趣旨を明確に表示する。

**主見出し**
`無料モニター 先着30名限定`

**説明文**
`正式公開前の無料モニターとして、先着30名まで月額料金なしでご利用いただけます。実際に使っていただきながら、学習に役立つサービスへ改善していきます。`

必要なら短い補足として、
`※30名に達した時点で、新規の無料モニター受付を終了します。`

を使用してよい。

### 表示ルール

- PC / mobileの双方で自然に見えること。
- 既存デザインの白＋緑、やさしいが軽すぎないLicenseTownの世界観を壊さない。
- CTA付近または現在の「料金・提供条件」案内の位置を優先し、同じ意味の告知を何箇所も乱立させない。
- `残り○名`は今回表示しない。DB連動残数表示は今回の範囲外。
- 「永久無料」「全機能永久無料」等の未確定な約束は禁止。
- 現在の古い「料金・提供条件は公開準備中」等と矛盾する場合は、今回確定した無料モニター条件に合わせて最小限更新する。

---

# 2. 30名制限の正式仕様

## 枠の定義

「30名」は単なる`user_profiles COUNT(*)`ではなく、**無料モニターとして確保された一意のLINE user_idを最大30**とする。

同一user_idは常に1枠のみ。
`ふりだしにもどる`等の学習初期化を行っても、その人の無料モニター枠は解放しない。

## DB方式

race conditionを避けるため、推奨設計は30行固定のslot table。
例：

`free_monitor_slots`
- `slot_number SMALLINT PRIMARY KEY`（1〜30）
- `user_id TEXT UNIQUE NULL`
- `claimed_at TIMESTAMPTZ NULL`

`init_database()`等、既存の安全なschema initialization方針に合わせて
`CREATE TABLE IF NOT EXISTS`し、1〜30のslot rowをidempotentに準備する。

### atomic claim

新規user_idのslot claimはtransaction内で行う。

概念例：

```sql
WITH candidate AS (
  SELECT slot_number
  FROM free_monitor_slots
  WHERE user_id IS NULL
  ORDER BY slot_number
  FOR UPDATE SKIP LOCKED
  LIMIT 1
)
UPDATE free_monitor_slots AS slots
SET user_id = %s,
    claimed_at = NOW()
FROM candidate
WHERE slots.slot_number = candidate.slot_number
RETURNING slots.slot_number;
```

ただし、まず同一`user_id`がすでにslotを持っていれば既存slotを返すこと。
実装詳細は既存DB abstractionに自然に合わせてよいが、**count-then-insertだけの非atomic実装は禁止**。

## 既存利用者の保護

Productionのread-only確認では、2026-09-10時点で：
- `user_profiles`: 4件
- name登録済み: 3件
- initial assessment completed: 1件
- `learning_events`で回答実績ありのunique user: 3件

既存の「実際に回答履歴があるuser_id」は、今回の導入で利用不能にならないよう、slot table初期化時に既存学習者をidempotentにfree-monitor slotへbackfillすること。

- `learning_events.answered_count > 0`のDISTINCT user_idを既存学習者として保護する案を第一候補とする。
- 既存user_idをログやテスト出力に露出させない。
- 30人を超える既存利用者が存在する異常ケースでは、黙って一部を切り捨てず安全側でfail / logすること。

## 登録タイミング

正式なslot claimは、LINE onboardingで名前登録を完了しようとするタイミングを基本とする。

現行`app.py`の`waiting_name`で `user_names[user_id] = user_message` を行う直前に、無料モニターアクセスを確定する設計を第一候補とする。

- 既にslotを持つuserはそのまま通す。
- 空きslotがあればatomic claimして登録を続行。
- 30枠満了なら名前登録を完了させず、新規無料利用へ入れない。
- 満了時は例として：
  `無料モニター30名の受付は終了しました。ご興味を持っていただきありがとうございます。今後の募集・正式公開についてはLicenseTown公式サイトでご案内します。`
  のように、丁寧で事実だけの案内を返す。
- 既存slot保有者の通常学習を各リクエストで毎回阻害するような重いgateにしない。

## resetの扱い

`ふりだしにもどる`は学習状態のリセットであり、無料モニター資格の退会ではない。
したがって`reset_user_profile()`等でfree monitor slotを削除・解放しない。
同一user_idが再オンボーディングした場合は、以前のslotを再利用する。

---

# 3. local/test fallback

DATABASE_URLなしの既存local test環境でも意味が壊れないよう、既存の`database.py`方針に合わせてlocal in-memory fallbackを用意すること。

最低限：
- 同一user_idのidempotent claim
- 30人まで成功
- 31人目はfull
- reset後もslot保持

をテスト可能にする。

---

# 4. テスト必須項目

## HP

- 公開HPに`無料モニター`と`先着30名限定`が現れる。
- 古い矛盾コピーが残らない。
- public PC/mobile双方に適用される。
- frozen preview source自体を変更していない。
- existing CTA/legal/public interaction testsを壊さない。

## DB / access

- 空きありでclaim成功。
- 同じuser_idを2回claimしても1枠。
- 30 unique usersまで成功。
- 31 unique userは拒否。
- concurrency / atomicityの意味を担保するテストを可能な範囲で入れる。
- 既存学習者backfillがidempotent。
- resetしてもslotが解放されない。

## onboarding

- 30未満：従来どおり名前登録→HOMEへ進める。
- 満了：31人目の名前登録を完了させない。
- 既存slot user：満了後でも再オンボーディング可能。
- 既存学習フローへの回帰なし。

---

# 5. 公開問題数について

今回の調査で`data/question_bank/question_tags.json`のQ1〜Q2000 source集計は
- original: 900
- past_exam: 1100
- total: 2000

と整合確認済み。
既存HPの900/1100/2000表示は今回この値を理由なく変更しない。
Question Bank本文・tagsのbulk editは禁止。

---

# 6. 完了時の報告形式

以下を必ず報告すること。

1. 原因 / 現状
2. 変更ファイル一覧
3. HPの最終表示文言
4. 30名制限のDB・atomic claim設計
5. 既存利用者backfillの扱い
6. reset時のslot保持確認
7. 関連テスト結果
8. 全体テスト結果
9. Question Bank validator結果
10. `git diff --check`結果
11. commit SHA
12. push結果 / remote HEAD SHA
13. **商品成立 YES / NO**
14. 残るものがあれば blocker / non-blocker を分離

## Stop rule

上記の商品成立条件を満たしたら、このtaskはそこで終了する。
細かな装飾・管理画面・残り人数表示・課金・待機リスト等へ勝手に広げない。
