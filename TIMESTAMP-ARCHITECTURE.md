# Lex Talk Legal — Permanent Footer Timestamp Architecture

The visible footer timestamp has one authoritative source:

`data/site_meta.json`

Every public page already contains the existing `.updated-line` footer element. `assets/site.js` hydrates that element at runtime from `data/site_meta.json` with `cache: no-store`, so every page displays the same exact site-wide timestamp.

The timestamp refresh workflow updates only `data/site_meta.json`. It intentionally does **not** rewrite every HTML page on every refresh. This prevents stale generated HTML from causing unrelated workflow failures and avoids unnecessary repository-wide timestamp churn.

The baked timestamp in a page is only a fallback for the time before JavaScript hydration. The smoke test therefore validates the presence of the footer marker and the runtime hydration contract rather than requiring every historical HTML file to contain the current meta timestamp.

Cloudflare is also instructed not to cache `data/site_meta.json`, so the browser receives the latest authoritative timestamp after a successful timestamp refresh.

To intentionally change the site-wide timestamp, run the GitHub Actions workflow:

**Refresh Lex Talk Legal Site Timestamp**

This creates one new IST timestamp and commits only the shared metadata file. The live footer on all pages then converges to that exact value through the existing site.js hydration code.
