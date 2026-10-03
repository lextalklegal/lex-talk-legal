# Lex Talk Legal — Hybrid Publishing Architecture

Blogger remains the primary source for current/editorial news. `content/evergreen/*.html` is the source of truth for original long-form legal guides. `scripts/build_site.py` is the only common generator.

Generated evergreen pages are published under `article/evergreen/`, are included in `sitemap.xml`, and are intentionally excluded from `news-sitemap.xml`. The source `content/` directory is excluded from Cloudflare static assets.

## Adding a guide
Create a new `.html` source file in `content/evergreen/` by copying an existing guide. Keep the metadata block and update Title, Slug, Meta Description, Section, Labels, Published and Updated. Use one of the existing section keys: `courts`, `banking-law`, `drt-drat`, `legal-careers`, `dra`, or `explained`.

Do not place evergreen source files inside the public `article/` folder. The Editorial Sync workflow rebuilds the evergreen output when files under `content/evergreen/**` change.
