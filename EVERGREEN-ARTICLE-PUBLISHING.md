# Lex Talk Legal — Evergreen Article Publishing

## Where evergreen articles live

Store original long-form guides in `content/evergreen/`. Do not put these source files in the public `article/` directory.

## How publication works

`content/evergreen/*.html` -> `scripts/build_site.py` -> `article/evergreen/*.html` -> `sitemap.xml` -> live website.

Blogger remains the primary source for current news. Evergreen guides remain owned and version-controlled in GitHub.

## Adding a new guide

1. Copy an existing file in `content/evergreen/`.
2. Change the metadata block: Title, Slug, Meta Description, Section, Labels, Published, Updated.
3. Replace the article body. Keep official-source links and the editorial note.
4. Commit and push. The existing Editorial Sync workflow detects changes under `content/evergreen/**` and uses the single common `scripts/build_site.py` generator.
5. Generated output appears under `article/evergreen/`; the raw `content/` source is excluded from Cloudflare static assets.

## SEO rules

Use a clear search-intent title, answer the query directly, link to primary sources, add useful internal links, avoid keyword stuffing, and do not create near-duplicate pages only to target keyword variations. No ranking position is guaranteed.
