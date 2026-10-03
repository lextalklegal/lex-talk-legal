# Lex Talk Legal — Permanent Page Design Ownership

This repository uses one common editorial generator (`scripts/build_site.py`).
That generator must not silently overwrite an approved page design.

## Common shell lock

The shared Header, Navigation/Menu and Footer are part of the common page shell.
Do not redesign or replace them for page-specific work.

Page-specific visual work belongs under:

`assets/pages/*.css`

## Page ownership

| Public page | Current design source | Owner / writer | Allowed automatic rebuild |
|---|---|---|---|
| `/` | `scripts/build_site.py` | Editorial Sync | Yes |
| `/category/courts/` | `templates/category/courts.html` + `assets/pages/courts.css` | Editorial Sync | Yes |
| `/category/law-policy/` | `templates/category/law-policy.html` + `assets/pages/law-policy.css` | Editorial Sync | Yes |
| `/category/banking-law/` | `templates/category/banking-law.html` + `assets/pages/banking-law.css` | Editorial Sync | Yes |
| `/category/dra/` | `templates/category/dra.html` + `assets/pages/dra.css` | Editorial Sync | Yes |
| `/videos/` | `templates/videos.html` + `assets/pages/videos.css` | Editorial Sync | Yes, template-backed |
| `/courtrooms/` | `templates/courtrooms.html` + `assets/pages/courtrooms.css` | `scripts/build_vc.py` / Update Courtroom VC Links | Only through VC workflow |
| `/case-status/` | `templates/case-status.html` + `assets/pages/case-status.css` | Manual/static page | No common editorial rebuild |
| `/about.html` | `about.html` + `assets/pages/about.css` | Manual/static page | No common editorial rebuild |
| `/contact.html` | `contact.html` + `assets/pages/contact.css` | Manual/static page | No common editorial rebuild |
| `/auctions/` | `templates/auctions.html` | `scripts/build_auctions.py` | Only through Auctions workflow |
| `/jobs/` | `templates/jobs.html` | `scripts/build_jobs.py` | Only through Jobs workflow |

## Permanent rule

`build_site.py` may generate articles, categories, homepage, videos and SEO files.
It must not call the writers for protected manual/workflow-owned pages.

In particular, the common editorial build must never call:

- `write_courtrooms_page`
- `write_case_status_page`
- `write_team_page`
- `write_case_help_page`
- `write_auctions_page`
- `write_search_page`
- `under_construction_page`

Automatic OneCourt scraping is not part of the common editorial build.

## CI protection

`scripts/smoke_test.py` checks the approved page classes, page-specific CSS files,
protected page ownership, template presence, sitemap integrity and key Article SEO
markers. A future regression should fail the workflow before it can be committed
by the Editorial Sync workflow.
