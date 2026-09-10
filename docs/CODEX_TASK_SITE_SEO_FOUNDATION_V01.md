# LicenseTown SITE SEO Foundation v0.1

## 最重要：Codex使用量ルール

**使用量の残数に対して途中で残数不足になるようなら開始してはならない。**

開始前に、この作業を最後まで完了できるだけのCodex使用量があるか確認すること。使用量が途中で0になり作業中断の可能性があるなら、何も変更せず開始しないこと。

---

## 今回のゴール

LicenseTown公式HPを、検索エンジンが「理学療法士国家試験の学習サービス」と正しく理解できるSEO基礎状態へする。

## 商品成立の判定条件

1. `/site` のtitleに「理学療法士国家試験」を自然に含める。
2. descriptionに「理学療法士国家試験」「問題演習」「弱点分析」「LINE」等、実際のサービス内容を誇張なく含める。
3. canonicalが1つだけ正しく出力される。
4. OGP/Twitter相当の基本メタ情報を整える。存在しない画像URLは作らない。
5. `/robots.txt` が200で返り、公開トップとsitemapをクロール可能にする。
6. `/sitemap.xml` が200/XMLで返り、少なくとも公開対象の正式ページだけを列挙する。
7. iframe内部のpreview/source/asset向け公開補助URLは検索結果の重複候補にならないよう `noindex,follow` 等の適切な制御を行う。ただし表示や既存機能を壊さない。
8. `/site` 親HTMLに、検索エンジンとアクセシビリティに意味のあるLicenseTownの説明情報をserver-renderedで持たせる。検索順位操作目的の隠しテキストは作らない。既存iframe表示を壊さない方法に限定する。
9. JSON-LDを入れる場合は、実在情報だけを使い、`WebSite` とサービス説明として妥当な最小構成にする。架空のレビュー・評価・価格・組織属性は書かない。
10. 既存HPのPC/mobile見た目を変えない。
11. 既存の無料モニター先着30名表示・CTA・法務ページを壊さない。
12. 関連テストと全体テスト、`git diff --check` がPASSする。

## 今回の主対象キーワード

Primary:
- 理学療法士 国家試験
- PT 国試

Secondary:
- 理学療法士 国家試験 勉強
- 理学療法士 国家試験 問題
- 理学療法士 国家試験 過去問
- 理学療法士 国家試験 勉強法

注意：キーワードを不自然に詰め込まない。既存サービス内容に合う範囲だけ使用する。

## 推奨title案

`理学療法士国家試験の学習をサポート | LicenseTown（ライセンスタウン）`

必要なら文字数・自然さを見て微調整してよいが、「理学療法士国家試験」と「LicenseTown」は必須。

## 推奨description案

`LicenseTown（ライセンスタウン）は、理学療法士国家試験の合格を目指す受験生向け学習サービスです。問題演習、弱点分析、学習ナビをLINE中心で利用でき、今やるべき学習を整理して合格まで伴走します。`

誇張や未実装機能を追加しないこと。

## 重要な現状

- `/site` の親HTMLは現在iframe中心。
- 親HTMLにはtitle/description/OGPはあるが、「資格取得」寄りでPT国試への専門性が弱い。
- PC preview内には、理学療法士国家試験・問題演習・弱点分析・合格への道・LINE・見守り等の実体ある本文が存在する。
- `robots.txt` と `sitemap.xml` は現行repo検索では確認できていない。
- preview HTMLそのものはデザイン回帰用に凍結扱い。直接の全面編集は禁止。

## 実装方針

### A. top-level `/site` metadata

`templates/site/home.html` と必要なFlask側のみを最小変更する。

追加/確認対象：
- title
- meta description
- canonical
- og:title
- og:description
- og:type
- og:url
- robots meta（index,follow）
- 必要ならTwitter Card最小構成

canonical/og:urlは、productionの正式URLを安全に生成すること。環境変数を導入する場合はfail-safeな設計にし、javascript等を許可しない。既存の公開URL設計を壊さない。

### B. crawlable semantic context

iframeだけの親HTMLというSEO弱点を改善する。ただし検索エンジンを欺くhidden keyword blockは禁止。

方法は、server-renderedな短い意味のある説明・headingを親ページに持たせつつ、既存画面の見た目を変えない安全な実装を選ぶこと。アクセシビリティ上正当な方法のみ。

必要ならiframe titleやHTML構造も改善してよいが、PC/mobile完成デザインを動かさない。

### C. robots.txt

正式ルートを追加し200 text/plainで返す。

- `/site` をクロール可
- `/sitemap.xml` の場所を記載
- private learner dashboardやLINE webhook等を検索対象として積極的に案内しない

robots.txtだけをセキュリティ制御に使わないこと。

### D. sitemap.xml

200 application/xml で返す。

公開・正式・検索結果に出す意味があるページだけを含める。
少なくとも `/site` を含める。
法務ページを含める場合は公開ルートの実在を確認してから。
preview/source/debug/developer/dashboard個人ページは含めない。

### E. duplicate/noindex control

以下のような内部表示用URL群は、必要に応じてレスポンスヘッダまたはmetaで `noindex,follow` を付与して、親 `/site` と競合しにくくする：
- `/site/view/pc`
- `/site/view/mobile`
- `/site/source/pc`
- `/site/source/mobile`
- preview asset/document routes

ただしiframe表示自体をブロックしない。`X-Frame-Options`等を誤って付けない。

### F. structured data

入れるなら最小・事実ベース。
推奨：`WebSite`
- name: LicenseTown
- alternateName: ライセンスタウン
- url: canonical URL
- description: 実際のサービス説明

架空のAggregateRating、Review、Offer、料金、受賞、資格認定などは禁止。

## 今回はやらないこと

- HP全面リニューアル
- preview HTMLのデザイン変更
- ブログ機能の新設
- SEO記事量産
- 被リンク施策
- Search Consoleアカウント操作
- GA/GTM全面導入
- 課金実装
- 残り無料枠数表示
- Question Bank変更
- 合格への道変更
- Phase11変更
- unrelated refactor

## テスト要件

最低限追加するテスト：
1. `/site` が200
2. titleに `理学療法士国家試験` と `LicenseTown`
3. meta descriptionが存在し空でない
4. canonicalが1つ
5. canonicalがHTTPSまたは安全なテストURLとして期待どおり
6. `/robots.txt` が200 text/plain
7. robotsにsitemap宣言
8. `/sitemap.xml` が200 XML
9. sitemapに `/site`
10. preview/source routesにnoindex制御
11. `/site` はindex,follow
12. 無料モニター30名表示が従来通り維持
13. 公開CTAが従来通り機能

その後、関連テスト、全体pytest、Question Bank validator（必要な既存手順）、`git diff --check`。

## 完了時の報告

1. 原因/現状
2. 変更ファイル
3. final title
4. final description
5. canonical実装
6. robots.txt
7. sitemap.xml
8. noindex対象
9. JSON-LD有無と内容
10. iframe親ページ対策
11. 関連テスト結果
12. 全体テスト結果
13. validator結果
14. git diff --check
15. commit SHA
16. push結果
17. 商品成立 YES/NO
18. blocker/non-blocker

商品成立条件を満たしたら、それ以上のSEO改善へ広げず停止すること。
