# Lex Talk Legal — Stable Production Architecture

Lex Talk Legal is a digital legal-information and media platform operated as a media initiative of LEXBOTICS AI MEDIA LLP.

## Canonical site

`https://lextalk.legal`

## Non-negotiable design rule

The existing global header, navigation/menu and footer are shared site-wide and must not be changed during page-specific redesigns.

Approved page designs are isolated in:

- `assets/pages/*.css` — page-specific styling
- `templates/` — generated page layouts
- static HTML files — manually maintained pages such as About/Contact

Do not replace the entire `scripts/build_site.py` for a single page redesign.

## Automated editorial workflow

`.github/workflows/sync-editorial.yml` runs every 30 minutes and can also be started manually. It fetches only:

- Blogger editorial posts
- YouTube feed

It rebuilds only editorial outputs: article pages, editorial categories, Videos, homepage content selection and sitemap.

It does **not** query OneCourt, auction portals, job portals, or other manual directories. It does not rebuild About, Contact, Team, Case Status, Courtrooms, Auctions, Jobs, policy pages, or Cloudflare configuration.

## Manual desks

### Courtrooms / VC
Edit `data/vc_links.json` and commit. `update-vc.yml` rebuilds only `/courtrooms/`.

Each VC entry may contain `label`, `url`, `meeting_id`, `password`, `verified_on`, and `notes`.

### Auctions
Edit `data/auctions.json` and commit. `update-auctions.yml` rebuilds only `/auctions/`.

### Legal Jobs
Edit `data/jobs.json` and commit. `update-jobs.yml` rebuilds only `/jobs/`.

See `MANUAL-DATA-GUIDE.md` for exact examples.

## Deployment

`.github/workflows/deploy-worker.yml` is the only deployment workflow. It runs automatically after pushes to `main` and can be started manually.

Required repository secrets:

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

## Asset safety

`.assetsignore` excludes source code, build scripts, templates, private/manual datasets, `node_modules` and Wrangler/build artefacts from public static-asset upload.

## Deliberately retained future modules

The repository still contains an inactive professional-profile/admin scaffold (`admin/`, `advocates/`, `functions/`, `db/schema.sql`, `dev.vars.example`). These are excluded from the Worker asset upload and can be removed later if the Advocate Panel project is permanently abandoned.

## Safe cleanup already performed

- removed duplicate root `build_site.py`
- removed obsolete `court-data.json`
- removed obsolete README/VC fix notes
- removed generated Python caches
- removed unused logo SVG
- removed empty `data/team.json` and its asset note
- removed stale OneCourt scrape junk entries from VC data

See `ARCHITECTURE-REPAIR-2026-09-29.md` for the rationale and workflow design.
