# pethome

帰ってきた部屋に、居場所がある。

静的HTML/CSS/JavaScriptのコンセプト公開版。個別相談・写真受付・決済はありません。

## 編集

- `index.html`: 公開コピー・プラン・導線
- `privacy.html`, `terms.html`, `commercial.html`: 補足ページ
- `data/check-results.json`: 4問と8種類の結果、共通修飾子
- `assets/js/check-engine.js`: 純粋な分岐ロジック
- `data/products.json`: 参考商品の確認先・説明
- `data/images.json`: 画像の出自・サイズ・ハッシュ

```sh
python3 scripts/build.py
python3 -m http.server 8080 --directory dist
```

`http://localhost:8080/` で表示。PythonとNode.jsの標準ライブラリのみでビルドできます。

## 公開

GitHub PagesのSourceをGitHub Actionsに設定。mainへのpushで、4問の192入力組み合わせ・8結果・リンク・画像を検証して公開。
公開後に配信ファイルをハッシュ照合します。Cloudflareにも同じdistを配置できます。
本営業の利用開始時はホスティングの利用条件も再確認してください。

## レビュー

`ai-review.html` / `.txt` / `.md` はビルド時に最新の公開コピーから自動生成します。
一般向けナビからリンクしません。アクセス制限ではないので、非公開の事業情報を入力に追加しないでください。

## プライバシー

セルフチェック回答はブラウザのメモリ内だけで処理。Cookie、ローカルストレージ、サーバー送信、解析タグはありません。
TXTは利用者がボタンを押したときだけ生成します。クエリやフラグメントによる初期選択は許可した値だけを扱います。

## 公開前提

サービス準備中、料金未確定、施工パートナー未定。掲載画像は生成イメージで、施工実績や特定商品の再現ではありません。
