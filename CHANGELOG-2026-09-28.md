# Lex Talk Legal — corrected final merged build

This build is based on the exact existing GitHub repository ZIP supplied by the user and is intended to be copied back into the existing `main` repository.

## Visible/refinement changes
- Added **Legal Professionals** to the main navigation, homepage community area, sidebar and quick links.
- Added a free professional profile application flow with mandatory administrative review.
- Added public approved-profile pages with `ProfilePage`/`Person` structured-data foundation and clear informational disclaimers.
- Added moderation states: pending, under review, approved/published, rejected and suspended.
- Added admin moderation actions and audit logging.
- Replaced the unreliable Google Translate widget dependency with a deterministic local Hindi/English UI switch.
- Added a one-time language migration key so an older saved language state does not silently control the newly deployed UI.
- Removed the redundant client-side article/video JSON injection script to reduce duplicate work and avoid inserting unescaped Blogger data into HTML.
- Switched generated pages from embedded CSS/JS/base64-logo payloads to cacheable `/assets/site.css`, `/assets/site.js` and the official logo asset.

## Security / infrastructure changes
- Added Cloudflare Worker runtime routing for `/api/*`, `/admin/*` and `/advocates/*`.
- Added `.assetsignore` so source code, build scripts, functions and database files are not exposed as public static assets.
- Added stronger response security headers and no-store/noindex controls for admin/API routes.
- Admin operations now require a real Cloudflare Access identity in the Worker context and then check that identity against `ADMIN_EMAILS`; a browser-supplied Access email header is not trusted by itself.
- Added D1 schema for professional profiles, submissions and moderation audit logs.
- Added rate limiting/honeypot/origin validation to profile submissions.
- Added a fallback so a temporary Playwright/browser/network failure during VC extraction does not wipe the previously cached VC directory.

## Deployment note
The profile database is intentionally not enabled until a real Cloudflare D1 database is created and bound as `DB`. The admin UI is intentionally not usable until Cloudflare Access protects `/admin/*` and `/api/admin/*` and the authorized email(s) are placed in `ADMIN_EMAILS`.

The application is configured to serve production through the existing `lextalk.legal` Custom Domain. The `workers.dev` production endpoint is intentionally kept enabled as a temporary legacy-browser compatibility bridge for visitors who may still have an older cached permanent redirect. The bridge uses a `302` response and a dedicated canonical-domain bridge path, then silently restores the visible address to `https://lextalk.legal/`.

## 2026-09-28 — deployment/routing hardening
- Fixed the build generator so scheduled syncs no longer overwrite the Worker routing configuration or legacy-browser compatibility code.
- Added the missing GitHub Actions deployment workflow using the Cloudflare Wrangler Action.
- Updated the scheduled sync workflow to validate the build before and after generation and deploy generated changes in the same run.
- Added a canonical-domain bridge for browsers that still hold the old `lextalk.legal` → `workers.dev` permanent redirect in cache.
- Versioned the shared site JavaScript reference so the bridge cleanup code is refreshed for newly served pages.
