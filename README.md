# pethome — service concept preview

2026-09-22 content review. Plain HTML/CSS/JavaScript, no build dependency.

## Positioning

既製品を売るのではなく、商品選定・既存家具との配置・取付前の確認を整理する空間プランニング。初期は猫の壁面／猫の出入口／犬の室内の居場所。床全面張り替え・屋外工事・大規模造作は標準範囲から外す。

商品・場所が決まっている取付相談と、組み合わせを考える空間プランを区分する。正式料金・施工店・受付先は未確定なので、販売価格や提携実績を表示しない。

## Current behavior

- Pre-launch notice is visible. No contact transmission, photo upload, payment, analytics, or browser storage.
- Self-check computes a general starting point in the browser and can save a text memo. It is not a safety diagnosis or quotation.
- Product references are in `data/products.json`; no affiliation or stock is asserted.
- Illustrations are explicitly conceptual, not completed works or installation drawings.
- The original `site.css` is retained; scoped content refinements are in `review.css`.

## Local preview

```sh
python3 scripts/build.py
python3 -m http.server 8080 --directory dist
```

Open http://localhost:8080/ . Use an HTTP server for the product JSON; do not rely on file://.

## Publishing

GitHub Pages: Settings → Pages → Source: GitHub Actions. The workflow builds and validates before publishing `dist` only. An independent `pethome-preview` artifact remains available even if Pages is not enabled.

Public repository visibility does not itself enable Pages. The connector used for content edits does not expose Pages administration. Do not add elevated tokens to the repository or workflow to work around setup.

GitHub Pages restricts hosting online businesses or sites primarily facilitating commercial transactions. This repository contains a non-transactional, pre-launch concept preview. Confirm the actual use against the policy; use a suitable host such as Cloudflare for the customer-acquisition/ordering service rather than assuming that no checkout means all commercial use is allowed.

- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

For Cloudflare, use the static `dist` directory. No vendor-specific runtime is required.

## Before accepting enquiries

Confirm operator and contact information, privacy/AI processing and retention, service and cancellation terms, actual partner coverage and insurance, procurement/returns responsibilities, and validated pricing. Implement and test a real private intake endpoint. Remove noindex only after the launch review. Do not collect room photos through public GitHub issues.

Keep internal margin assumptions, client data, credentials, and partner-negotiation details outside this public repository.
