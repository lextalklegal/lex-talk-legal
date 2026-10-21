# Lex Talk Legal — Stable Production Architecture

Lex Talk Legal is a digital legal-information and media platform, a media initiative of LEXBOTICS AI MEDIA LLP.

## Canonical site

https://lextalk.legal

## Non-negotiable design rule

The existing global header, navigation/menu and footer are shared site-wide and must not be changed during page-specific redesigns.

Approved page designs are isolated in:
- `assets/pages/*.css` — page-specific CSS
- `templates/` — generated page layouts
- static HTML files — manually maintained pages such as About and Contact

For a single-page redesign, change only that page's HTML/template and page CSS. Do not replace the entire build system.

## Data ownership and workflows

### Editorial sync — automatic
`.github/workflows/sync-editorial.yml` runs every 30 minutes and can also be started manually.

It fetches only:
- Blogger editorial posts
- YouTube channel feed for the Videos page

**YouTube-to-blog auto-generation was retired on 21 October 2026.** The recurring workflow no longer executes the Gemini-based article generator. Previously generated articles remain published; deleting an API key alone is not the mechanism used to stop the workflow. See `YOUTUBE-AUTO-BLOG-SETUP.md` for historical details.

It rebuilds only:
- existing article pages and Blogger-sourced article content
- editorial category pages
- Videos page
- homepage content selection
- sitemap

It does not fetch or scrape OneCourt, auction portals, job portals, or other manual desks.

### Courtrooms / VC — manual
Source of truth: `data/vc_links.json`

Use `.github/workflows/update-vc.yml` from **Actions → Run workflow** to add/update/replace/remove one VC entry. The manual workflow is intentionally on-demand; it does not poll or scrape anything. Inputs support:
- section
- court/bench
- VC URL
- display label
- meeting ID (optional)
- password (optional)
- verification date
- notes

The workflow rebuilds only `/courtrooms/` and commits the changed data + generated page.

There is no OneCourt or Playwright dependency.

### Auctions — manual
Source of truth: `data/auctions.json`

Use `.github/workflows/update-auctions.yml` to add/update/remove one listing. The workflow is intentionally on-demand. It rebuilds only `/auctions/`.

### Legal jobs — manual
Source of truth: `data/jobs.json`

Use `.github/workflows/update-jobs.yml` to add/update/remove one listing. The workflow is intentionally on-demand. It rebuilds only `/jobs/`.

## Deployment

`.github/workflows/deploy-worker.yml` is the only workflow that calls Wrangler.

It runs automatically after pushes to `main` and can also be started manually.

Required repository secrets:
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

## Asset safety

`.assetsignore` excludes:
- source code
- GitHub workflow files
- Python/build scripts
- templates
- manual/private datasets
- `node_modules`
- Wrangler/build artifacts
- local configuration examples

Only public runtime assets are intended for the Worker asset bundle.

## Current approved page designs

- About
- Courts
- Banking Law
- DRA
- Videos
- Contact

Header, navigation/menu and footer remain shared and unchanged.

## Future design workflow

For each new page:
1. review the current page
2. redesign the main content only
3. add or update that page's CSS
4. test the page
5. commit
6. move to the next page

Manual desks and editorial sync are intentionally separated so content updates do not unexpectedly overwrite unrelated page designs.


## X-post newsroom publishing

`data/x_articles.json` is the source of truth for researched articles that begin with an X/Twitter post supplied by the editor. Adding or editing a record triggers the existing editorial build, which writes the article page, category/homepage cards, canonical/Open Graph/NewsArticle metadata, related links and both sitemaps. The deployment workflow intentionally skips a source-data-only change; the generated output commit triggers the Worker deployment. See `docs/X-POST-PUBLISHING-WORKFLOW.md`.

Automatic YouTube-to-blog generation is retired. This X workflow is editorial-input driven; it does not watch or automatically republish YouTube uploads.
