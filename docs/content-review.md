# 公開コンテンツとAIレビュー

## 公開URL

- サービスサイト: https://kazumanishiwaki.github.io/pethome/
- AIレビュー用全文: https://kazumanishiwaki.github.io/pethome/ai-review.html
- プレーンテキスト: https://kazumanishiwaki.github.io/pethome/ai-review.txt
- Markdown: https://kazumanishiwaki.github.io/pethome/ai-review.md
- セルフチェック全48分岐: https://kazumanishiwaki.github.io/pethome/ai-review-states.json

## 編集する場所

本文は `index.html`、参考商品は `data/products.json`、補足ページは `privacy.html` / `terms.html` / `commercial.html` を編集します。
セルフチェックの実際の結果文言は `assets/js/site.js` が唯一の編集元です。

`python3 scripts/build.py` は同じ公開ソースからAIレビュー用HTML・TXT・Markdownを自動集約し、公開ファイルだけを `dist/` に出力します。`ai-review.*` を手で変更しないでください。本文は静的HTML内に含まれ、JavaScriptを実行しない読み手でも取得できます。

条件分岐の結果は `scripts/export_review_states.cjs` が実際のフォーム処理をネットワークなしの検証用DOMで実行して取り出します。7つの結果系統は全文テキストにまとめ、48通りの入力・確認事項・保存メモはJSONに保存します。

公開ソースのSHA-256 fingerprintを各出力に含めます。公開後のCIではHTML・テキスト・画像・JSON・CSS・JavaScriptを実際の配信URLから照合します。

## 写真の扱い

3枚は会話内で生成したAIコンセプト画像です。実際の施工事例、メーカー公認の設置図、特定製品の正確な写真として扱わないでください。植物、小物、ゲートの隙間、ステップの間隔などを推奨仕様と解釈しないことを本文でも明示しています。

- `assets/img/cat-wall.webp`: トップ・猫の壁面と窓辺
- `assets/img/cat-entrance.webp`: 猫の玄関と出入口
- `assets/img/dog-living.webp`: 犬の居場所

各画像は4:3の比率を維持した1408×1056pxと704×528pxのWebPです。`-small.webp` をsrcsetで使用します。ファイルはGitHub内に保存され、期限付きURLや外部画像ホストに依存しません。
`data/images.json` はサイズとSHA-256を記録します。差し替える場合は画像とマニフェストを同時更新してください。

## 集約対象外

非公開の事業計画、粗利・収益仮説、個人情報、顧客写真、認証情報、社内資料は入力対象にしません。レビュー用ページも公開ページです。`noindex` は閲覧制限ではありません。
