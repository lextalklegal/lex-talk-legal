# Lex Talk Legal — Deployment Checklist

## GitHub Actions secrets

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

Never commit or paste the token into source code.

## Production deployment

1. Commit changes to `main`.
2. `Deploy Lex Talk Legal Worker` runs automatically.
3. Check the latest Worker deployment in Cloudflare.
4. Verify `https://lextalk.legal`.

## Editorial sync

`sync-editorial.yml` syncs Blogger and YouTube only. It does not run Playwright or query OneCourt.

## Manual desks

- VC: edit `data/vc_links.json`; `update-vc.yml` rebuilds only Courtrooms.
- Auctions: edit `data/auctions.json`; `update-auctions.yml` rebuilds only Auctions.
- Jobs: edit `data/jobs.json`; `update-jobs.yml` rebuilds only the Jobs Board.

## Design safety

Approved page-specific CSS and templates are source-controlled. Do not replace the whole `scripts/build_site.py` for a single page change.
