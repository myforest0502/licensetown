# LicenseTown Instagram 初期固定投稿

@licensetown / LicenseTown｜国家試験対策

## 投稿順と完成画像

1. **LicenseTownって何？** — 学習結果から次にやる問題を提案する価値。
   [01](post01_what_is_licensetown/01.png) · [02](post01_what_is_licensetown/02.png) · [03](post01_what_is_licensetown/03.png) · [04](post01_what_is_licensetown/04.png) · [05](post01_what_is_licensetown/05.png) · [06](post01_what_is_licensetown/06.png) / [caption](post01_what_is_licensetown/caption.txt)
2. **源さんと1問だけ** — 最初の一歩を軽くする。
   [01](post02_one_question/01.png) · [02](post02_one_question/02.png) · [03](post02_one_question/03.png) · [04](post02_one_question/04.png) · [05](post02_one_question/05.png) · [06](post02_one_question/06.png) / [caption](post02_one_question/caption.txt)
3. **なぜLicenseTownを作ったのか** — 家族に勧められる道具と寺子屋の理念。
   [01](post03_why_we_built_it/01.png) · [02](post03_why_we_built_it/02.png) · [03](post03_why_we_built_it/03.png) · [04](post03_why_we_built_it/04.png) · [05](post03_why_we_built_it/05.png) · [06](post03_why_we_built_it/06.png) / [caption](post03_why_we_built_it/caption.txt)

各フォルダの01.png〜06.pngがアップロード用。全18枚、1080×1350px、RGB PNG、4:5。preview/ のJPEGは確認用で、投稿には使いません。

## Instagramへの投稿方法

1. @licensetown で、プロフィールのリンク先をβ版の入口に設定しておく。
2. 新しい投稿を作成し、複数選択で対象フォルダの01→06を順に選ぶ。3投稿をそれぞれ別のカルーセルにする。
3. 縦長4:5で全体が入ることを確認する。フィルターや拡大トリミングをかけない。
4. 対応するcaption.txtを貼り付け、6枚の順序・プレビューを確認して公開する。
5. 上記の1→2→3の順で公開し、各投稿のメニューからプロフィール上部に固定する。固定後の表示順は実際のプロフィールで確認する。読み順の推奨は1→2→3。

UIの表記はアプリの版によって異なります。複数画像投稿とプロフィール固定については [Meta公式の複数画像投稿案内](https://about.fb.com/ja/news/2017/02/instagram_sharemultiple/) と [固定機能の案内](https://about.fb.com/ja/news/2022/06/grid_pinning_on_profile/amp/) を参照。今回は素材制作までで、Instagramへの公開操作は行っていません。

## デザインと既存asset

- 既存 `static/site/site.css` の白、緑 #16833b、深緑 #075c31、淡緑 #f2f8f2、文字 #171b18 を採用。
- `templates/site/home.html` の寺子屋・伴走・家族のためという雰囲気を参照。
- `static/images/characters/gensan_main.png` を目視確認してそのまま複製し、`src/assets/gensan_main.png` として利用。表示時のみ縮小と角丸マスクを適用。人物の生成・描き替えなし。
- 独立した既存ロゴ画像は見つからなかったため、サイトと同様にLicenseTownの文字を緑で表示。
- 本文43〜46px、見出し62〜84px。幅360pxの縮小表示では本文約14〜15px。共通の余白、ヘッダー、ページ番号、最終ページのCTAで統一。
- 指定文案を基に、画像の読みやすさに合わせて改行を調整。投稿1の3枚目に主要価値の「修復中」を追加。表紙の補助文を追加。captionは依頼文の内容を維持。
- β版・無料公開・機能に関する記述は依頼時の指定内容に基づく。

## 再生成

既存アプリに依存しないPython + Pillow方式です。ブラウザ・Webサイトの起動は不要です。HTML/CSS方式の代わりに日本語フォントと描画座標を固定しています。

Python 3.10以降とWindowsの游ゴシック（YuGothM.ttc / YuGothB.ttc）が必要です。フォントは再配布していません。同一出力には同じフォントファイル・Pillowバージョンを使用してください。

このディレクトリで、必要に応じて専用の仮想環境を作成します。

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r src/requirements.txt
.venv\Scripts\python src/generate.py
```

Pillowがある環境なら `python src/generate.py` だけで生成できます。フォントディレクトリを変える場合は `--fonts "フォントのディレクトリ"` を指定します。

編集元は `src/content.json`、レイアウトは `src/generate.py`。生成すると18 PNG、3 captions、3縮小一覧、`src/validation.json`を更新します。

## ファイル構成と検証

- `post01_what_is_licensetown/`: 01.png〜06.png、caption.txt
- `post02_one_question/`: 01.png〜06.png、caption.txt
- `post03_why_we_built_it/`: 01.png〜06.png、caption.txt
- `preview/`: post01_overview.jpg、post02_overview.jpg、post03_overview.jpg（各画像を幅360pxで表示）
- `src/`: generate.py、content.json、requirements.txt、validation.json、production-baseline.json、assets/gensan_main.png
- `README.md`、`.gitignore`

18/18枚のサイズ・PNG形式・RGB・本文描画範囲を生成スクリプトで検証済み。3投稿すべてを縮小一覧で目視し、日本語表示と文字の収まりを確認。各PNGのSHA-256はvalidation.jsonに記録。

新規追加はこのディレクトリ内のみ。Productionコード、既存CSS、app.py、DB、Render設定、LINE機能、既存依存関係、テスト・validatorの変更は0。既存の未コミット変更は保持しており、今回のコミットには含めません。production-baseline.jsonは作業開始時の既存変更ファイルのハッシュで、制作後も一致を確認しています。アプリを変更しないためProductionテストは実行していません。

ブランチ: `feature/instagram-launch-3posts-v01`。mainへの直接pushは行いません。
