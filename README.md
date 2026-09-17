# pethome

既製品から始める、ペット空間のオンライン設計サービスのMVPサイトです。

## Positioning

- ペット用品ECではなく「空間プラン」起点
- 自社在庫を持たず、国内で調達しやすい既製品をメーカー横断で選定
- オンラインで写真・条件を整理し、必要に応じて地域施工パートナーへ引き継ぐ
- 初期商品は CAT: 壁面ステップ / 脱走対策、DOG: ゲート / 滑りに配慮した床
- 施工契約は顧客と地域施工店の直接契約を基本とする想定

## Files

```text
/
├── index.html
├── privacy.html
├── terms.html
├── commercial.html
├── assets/
│   ├── css/site.css
│   └── js/site.js
├── data/products.json
├── .github/workflows/pages.yml
└── .nojekyll
```

## Local preview

`fetch()` で `data/products.json` を読むため、file:// 直開きではなく簡易HTTPサーバーを使用します。

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080/`.

## GitHub Pages

Workflow is prepared for GitHub Pages.

1. Repository `Settings` → `Pages`
2. `Build and deployment` → `Source` を `GitHub Actions` に設定
3. `main` へ push すると `.github/workflows/pages.yml` がデプロイ

このリポジトリは作成時点で private のため、契約プランによっては Pages 公開条件を満たすために repository visibility の変更が必要です。

## Before public launch

- [ ] フォームを Tally / Formspree / Cloudflare Workers 等の実バックエンドへ接続
- [ ] `hello@example.com` 等の仮リンクを削除（初版JSでは送信を停止）
- [ ] 運営主体・住所・電話番号を `commercial.html` に記載
- [ ] `privacy.html` を実際のAI・フォーム・保存先に合わせて確定
- [ ] `terms.html` に有料プランのキャンセル/修正回数/納期を追加
- [ ] 実績写真または許諾済み/自社生成のBefore/Afterビジュアルへ差し替え
- [ ] 商品価格・仕様を公開直前にメーカー公式情報で再確認
- [ ] 施工パートナーの保険・経験・対応エリアを確認

## Product data policy

`data/products.json` は提案用の商品候補DBです。価格・仕様は固定値として保証せず、必ずメーカー・販売元の最新情報を優先します。

## Safety wording

オンラインプランは完成イメージ・商品配置の提案です。壁内部の構造、下地、施工可否を保証するものではありません。施工前に施工パートナーが現地確認し、メーカー施工基準に従って固定方法を決定します。
