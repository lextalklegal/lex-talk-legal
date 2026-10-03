# Lex Talk Legal — Permanent Footer Timestamp Architecture

The footer timestamp is now governed by one file:

`data/site_meta.json`

All normal builders (`scripts/build_site.py`, `scripts/build_vc.py`, `scripts/build_jobs.py`, `scripts/build_auctions.py`) read and preserve this shared timestamp. They do not create separate timestamps when a page is rebuilt.

The visible footer is also hydrated by `assets/site.js` from the same file, so the browser always uses one authoritative value.

To intentionally change the site-wide timestamp, use the GitHub Actions workflow:

**Refresh Lex Talk Legal Site Timestamp**

That workflow:

1. Creates one new IST timestamp.
2. Writes it to `data/site_meta.json`.
3. Updates only the existing `.updated-line` timestamp values in public HTML.
4. Runs the full smoke test.
5. Commits the synchronized timestamp update.

The smoke test now fails if any public page has a different footer timestamp, so a future workflow cannot silently reintroduce the inconsistency.

This avoids the old behaviour where the editorial, VC, jobs and auction builders each generated their own clock value.
