# Lex Talk Legal — SEO Pipeline Docs Guard Fix

## Why this patch exists
`docs/evergreen-article-template.html` is an internal authoring template, not a public page. The timestamp/GA/public-HTML scanners previously treated every `*.html` file outside `templates/`, `content/`, and `admin/` as public. That caused the recurring Editorial Sync to fail on the internal docs template.

## Permanent behavior
The following scanners now exclude `docs/`:
- `scripts/refresh_site_timestamp.py`
- `scripts/sync_public_timestamps.py`
- `scripts/ensure_public_ga.py`
- `scripts/smoke_test.py`

Documentation-only changes under `docs/` also no longer trigger a public-site timestamp refresh.

Cloudflare static-asset publishing ignores `docs/**` via `.assetsignore`.

Editorial and manual timestamp commit globs explicitly exclude `docs/**`.

## What stays unchanged
- Common header
- Navigation
- Footer design
- Approved page-specific layouts
- `content/evergreen/` ownership model
- Blogger → Editorial Sync architecture
- Single `scripts/build_site.py`

## Verification
- Python compile: PASS
- Smoke test: PASS
- Page-design contracts: PASS
- Sponsored campaign safeguards: PASS
- Internal `docs/evergreen-article-template.html` simulation: excluded from all public scanners
