# Lex Talk Legal — Deployment Checklist

## Before deployment
- `scripts/build_site.py` compiles
- `scripts/smoke_test.py` passes
- Required page-specific CSS exists
- Header/menu/footer are unchanged

## GitHub Actions
- `deploy-worker.yml` is the only workflow using Wrangler
- `sync-editorial.yml` handles Blogger + YouTube only
- `update-vc.yml` handles manual VC data only
- `update-auctions.yml` handles manual auction data only
- `update-jobs.yml` handles manual job data only

## Secrets
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

Never commit the API token.

## Analytics & timestamp
- Verify GA4 Measurement ID `G-3KT3SQPFXD` is present on public pages.
- Verify `data/site_meta.json` exists and the footer displays the exact IST timestamp.
- Do not add a second GA4 tag manually.

## Production
Verify:
- `https://lextalk.legal/`
- `https://www.lextalk.legal/`
- important redesigned pages
- `https://lextalk.legal/robots.txt`
- `https://lextalk.legal/sitemap.xml`
- `https://lextalk.legal/category/explained/`
- `https://lextalk.legal/jobs/`
- `https://lextalk.legal/advertise.html`
- `https://lextalk.legal/ads.txt`
