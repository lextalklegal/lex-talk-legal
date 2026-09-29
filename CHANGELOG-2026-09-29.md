# Lex Talk Legal — Maintenance Architecture Update (29 September 2026)

This build separates editorial refreshes from manually maintained desks and keeps page-specific designs independent of the shared site shell.

## Editorial sync
Blogger and YouTube are the only scheduled external editorial sources. The scheduled workflow refreshes article data, the homepage, editorial categories, the Videos page and the sitemap. It does not query OneCourt or other manual directories.

## Manual desks
VC links, auction listings and legal jobs are maintained in local JSON datasets and rebuilt only when those datasets or their templates change.

## Design safety
Approved page-specific templates/CSS live outside the shared shell. Header, navigation/menu and footer remain unchanged by the content-sync workflow.

## Stability fixes
- Removed the duplicate root build script.
- Removed obsolete scraped VC junk entries.
- Prevented older articles from disappearing when the Blogger feed contains only recent posts.
- Made homepage/sitemap generation deterministic so no-content-change syncs do not create needless deployments.
- Kept build/config files out of the Worker static-asset upload.
