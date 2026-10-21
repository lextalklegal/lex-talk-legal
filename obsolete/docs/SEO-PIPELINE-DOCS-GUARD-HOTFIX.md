# Lex Talk Legal — SEO Pipeline Docs Guard Hotfix

## Root cause
`docs/evergreen-article-template.html` is a source/documentation file, not a deployable public page. The timestamp synchronizer and smoke test were scanning every `*.html` file outside only a few source directories, so a documentation template was incorrectly treated as public HTML.

## Permanent fix
- `scripts/sync_public_timestamps.py` now excludes `docs/` and development/source directories from public-page scanning.
- `scripts/smoke_test.py` uses the same public-page exclusion policy.
- `.github/workflows/sync-editorial.yml` no longer stages every `*.html` file; it stages only known generated/editorial output paths.
- `.assetsignore` excludes `docs/` from Cloudflare Static Assets.
- `.github/workflows/deploy-worker.yml` ignores `docs/**` for deployment-trigger purposes so documentation-only changes do not cause unnecessary production deploys.

## Content ownership rule
- `content/evergreen/` = source-controlled evergreen article HTML.
- `article/evergreen/` = generated public evergreen output.
- `docs/` = internal documentation/templates only.
- Root `articles/` = not a supported production source directory and should not be recreated.
