# Lex Talk Legal — Phase 2 Implementation

Implemented on the Phase 1 production snapshot without changing the common header, navigation or footer.

## Changes
- Article pages now load `assets/pages/article.css` as page-specific CSS.
- Article pages show a clear visible publication date/time in IST directly below the headline and an updated timestamp when available.
- `NewsArticle` JSON-LD now includes publisher logo, author URL, section, language, free-access flag and keywords.
- Article social metadata uses the article lead image when one exists.
- `BreadcrumbList` JSON-LD is added to article pages.
- Article Open Graph type is now `article` and article timing metadata is present.
- Article byline links to the Editorial Policy / Editorial Desk transparency page.
- Related legal coverage is generated from existing articles using conservative relevance scoring.
- Duplicate editorial records are deduplicated using normalized Blogger source URLs; legacy duplicate routes are converted into 301 redirects.
- Sitemap and News Sitemap are built from the deduplicated article set.
- Smoke tests now validate article SEO markers, duplicate source URLs and duplicate sitemap URLs.
- Editorial Policy now contains an Editorial Desk transparency section.
- Smoke validation warns (without silently rewriting editorial titles) if a current headline exceeds Google News guidance of 110 characters; such headlines should be reviewed in Blogger.

## Important architecture notes
- `scripts/build_site.py` remains the only common generator.
- `refresh_static_pages()` remains a compatibility hook and does not regenerate manual pages.
- Header, navigation and footer HTML/design were not redesigned.
- AdSense publisher ID was not duplicated or changed.
- PIB remains a discovery/editorial queue system; it is not converted into automatic article copying.

## Deployment
1. Replace repository files with this Phase 2 snapshot.
2. Commit and push to GitHub.
3. Run the normal Deploy Worker workflow.
4. Let the scheduled Editorial Sync run once, or run it manually.
5. After deployment, inspect one article with Search Console URL Inspection.
6. In Search Console, monitor the submitted sitemap and the Google News performance report when data becomes available.
