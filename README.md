# Lex Talk Legal — Editorial Platform v10

Lex Talk Legal is a digital legal news, legal education and public-information platform operated as a media initiative of LEXBOTICS AI MEDIA LLP.

## v10 product direction

This build is intentionally editorial-first and monetisation-ready. The homepage is a fresh front page, not an archive: it shows one lead story, up to three secondary stories and a small latest-story set. Older articles remain available through category and article pages.

Primary business/content pillars:

- Legal news, judgments and practical explainers
- Bank, financial-institution and authority auction information with an assistance desk
- Case-information/document-review requests by email; a private upload system can be added only after secure storage, access, retention and deletion controls are configured
- Factual advocate team page with courts/forums and practice areas
- YouTube integration and video discovery
- Search and official legal utilities

## Monetisation readiness

The site includes an AdSense verification/ads.txt foundation and clearly separated advertisement slots. Actual AdSense serving requires Google site review/approval and policy compliance; revenue is not guaranteed from day one.

## Content model

Blogger remains the editorial publishing source. The scheduled GitHub Action syncs Blogger, YouTube and public court/VC data, rebuilds article/category/video pages and refreshes the homepage. The homepage is capped so older content naturally falls out of the front page.

## Image handling

Article and homepage images use contained media frames with a blurred backdrop so the full source image can remain visible without forced cropping or zooming. Article generation removes copies of the lead image from the article body to prevent duplication.

## Theme

The website has a light default theme with a manual light/dark toggle. The v10 theme preference uses a new localStorage key so older versions cannot force the new site into a stale theme state.

## Team photographs

Add official team photographs under `assets/team/` and set the corresponding `photo` field in `data/team.json`. Do not add unverified images or professional claims.

## Cloudflare

The repository is prepared for Cloudflare Workers + Static Assets using `src/index.js` and `wrangler.jsonc`. Production is served through the `lextalk.legal` Custom Domain. The `workers.dev` production endpoint remains enabled as a legacy-browser compatibility bridge so visitors with an older cached redirect can be returned to the canonical domain without manual browser-cache cleanup.

The deployment workflow uses GitHub Actions with `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` secrets. The scheduled sync workflow also deploys committed content changes in the same run, preventing generated files from getting out of sync with the live Worker.

No public advocate directory or profile-approval database is included in v10; that earlier concept has been removed.

## Build reliability
The deployment and scheduled-sync workflows run Python syntax checks and a regression smoke test before and after the generator runs. The smoke test also verifies the canonical-domain/legacy-bridge contract so the scheduled generator cannot silently overwrite the routing fix.

## Cloudflare deployment
Production deployment is handled by `.github/workflows/deploy-worker.yml` using GitHub Actions secrets. Credentials are intentionally not stored in the repository.
