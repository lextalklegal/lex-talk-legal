# Lex Talk Legal — Permanent Site-Wide Timestamp Architecture

## Single source of truth
`data/site_meta.json` is the authoritative site-wide footer timestamp.

## How synchronization works
`scripts/refresh_site_timestamp.py` creates one IST timestamp and then synchronizes the existing `.updated-line` marker on every public HTML page. It changes only the timestamp attributes/text; it does not redesign or regenerate manual pages.

`assets/site.js` also hydrates `.updated-line` from `data/site_meta.json` at runtime with a no-cache request, so browser display remains aligned with the same source of truth.

## Workflow order
Content-changing workflows must build first, then run `refresh_site_timestamp.py`, then run `smoke_test.py`, and only then commit the synchronized outputs.

## Safety contract
`smoke_test.py` requires every public HTML page with a footer marker to match `data/site_meta.json` exactly. A mismatch blocks commit/deploy.

## Protected design
Timestamp synchronization uses a narrow regex replacement of the existing `.updated-line` only. Header, navigation, footer structure, page HTML layout and page-specific CSS remain untouched.
