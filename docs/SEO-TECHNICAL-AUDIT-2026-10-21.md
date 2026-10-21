# Lex Talk Legal — Technical SEO & Repository Audit
**Audit date:** 21 October 2026  
**Scope:** GitHub repository tree, current editorial dataset, representative news/evergreen article HTML, homepage generator, sitemap generation, robots/ads configuration, build scripts, and all eight GitHub workflow definitions. Search Console, GA4 reports, AdSense account diagnostics, and field Core Web Vitals data were not connected, so rankings/indexing/revenue outcomes cannot be confirmed from this repository-only review.

## Executive summary
The site has a solid static-site foundation: canonical URLs, article metadata, NewsArticle JSON-LD on news articles, Article JSON-LD on evergreen guides, breadcrumbs, related-story links, an XML sitemap, a rolling 48-hour News sitemap, robots.txt, ads.txt, editorial policies, and build/smoke checks. Keep the eight workflows; each currently serves a distinct deployment, editorial sync, validation, timestamp, PIB, or manual-desk function.

The biggest growth risk is not missing basic SEO tags. It is uneven editorial depth across feed-derived articles, plus a few production/UX inconsistencies that should be corrected and measured.

## Findings and priorities

### P1 — Review thin feed-derived articles
The editorial dataset contains 39 article records. Sixteen records marked `youtube_auto_article` are under 300 words, and two are under 150 words. Their source metadata says the YouTube transcript was unavailable and the article was based on the upload feed description. Many do not include an official primary source in the article body.

Do not mass-delete these URLs. Review Search Console impressions/clicks first, then either:
1. expand valuable stories with primary records, verified chronology, attributed statements, meaningful context, and editor review; or
2. if a page adds no distinct value and has no meaningful search demand, consider consolidation or a carefully tested noindex/redirect decision.

Short articles are not automatically bad because of word count; the concern is whether they add original, accurate, useful information beyond the source post.

The initial review queue:
- Deepender Hooda Thanks Haryana for Rahul Gandhi's March for Democracy (142 words)
- Rahul Gandhi Asserts Resolve at March for Democracy (146)
- Prakash Raj Questions Youth Detentions During Tiranga March (155)
- Saurabh Bharadwaj Questions Police Escort for Vehicle in Delhi (155)
- Arvind Kejriwal Shares Video of 6-Year-Old Aditya from Bihar (160)
- Kapil Mishra Responds to Prashant Bhushan in Regime Change Row (165)
- Sanjay Singh Slams PM Modi Over Tricolour Row and Arrests (177)
- Sanjay Singh Issues Strong Warning Over Alleged Vote Chori (178)
- Prakash Raj Reacts to Judicial Custody Over Tiranga Protest (188)
- Political Protest Update: Slogans Raised for Gyanesh, Ashutosh, and Saurav (193)
- Saurabh Bharadwaj Compares 2026 Political Situation to 1975 Emergency (193)
- Jantar Mantar Protest Site Row: CJP Speaks on Right to Dissent (193)
- Pargat Singh Demands Justice for Sidhu Moose Wala and Parminder Singh Jhota (198)
- AAP Punjab Questions BJP Over Anti-Drug Campaign and Actions (208)
- Protest Call at Mandi House Highlights Debate Over Delhi Assembly Spaces (213)
- What is the DRA Exam? Debt Recovery Agent Certification Guide (253)

### Resolved during audit — Homepage title and subscription UX
The initial scan found a duplicated homepage title (“Lex Talk Legal | Lex Talk Legal”) and a newsletter form whose submit action only showed a placeholder alert. The build generator now uses “Legal News, Court Updates & Legal Explainers | Lex Talk Legal” with a more specific description. The fake email signup has been replaced by direct Telegram and YouTube follow links, so the public page no longer promises a non-existent subscription backend.

### P1 — Strengthen legal-news trust signals
For legal and public-affairs reporting, make the author/editor identity verifiable; link bylines to a genuine editorial/team profile; distinguish allegations from verified facts; cite the original order, notification, court record or official release wherever available; show meaningful publication/update dates; and record substantive edits. Do not invent credentials or claim expert review that did not occur.

### P2 — Sitemap and indexing
The sitemap builder creates canonical URLs for static pages, categories, news articles, and evergreen guides. The News sitemap builder intentionally includes only articles from the last 48 hours, which matches Google News sitemap guidance. Continue checking that generated sitemap URLs return indexable 200 responses and canonicalize to themselves. Keep `aibe-preparation/` excluded if it remains intentionally noindex.

A public crawl snapshot returned a homepage lead item that differed from the checked-in generated `index.html`. This may be crawler/edge-cache lag; verify the live homepage and sitemap after deployments and use Search Console URL Inspection before treating it as a production defect.

### P2 — AdSense and revenue hygiene
`ads.txt` contains the publisher record. Auto ads code is present in generated content pages. Do not optimize only for ad density: keep ads clearly separated from editorial content and avoid placing ads on thin, non-content, or utility-focused pages where they harm navigation or policy compliance. Review the actual AdSense Policy Center and page-level reports before changing placements. This repository audit cannot confirm account approval, ad serving, RPM, or earnings.

### P2 — Performance and accessibility
Run PageSpeed Insights / Search Console Core Web Vitals on the homepage, article, category, and utility pages on mobile and desktop. Prioritize LCP hero-image sizing, image dimensions/alt text, lazy loading below the fold, layout-shift prevention, script weight, contrast, keyboard focus, and tap targets. No lab or field performance scores were available during this audit.

### P2 — Security and architecture
The active Wrangler entry point is `src/index.js`; the `functions/` directory and `admin/` directory are excluded from the asset bundle, and the Worker redirects `/admin` to the homepage. Their legacy code has been preserved under `obsolete/`, not deleted. The archived `functions/_middleware.js` security-header policy was not part of the active Worker entry path. If adding a Content-Security-Policy later, explicitly test GA4, AdSense, YouTube embeds, images and any translation tools so security headers do not silently block required services.

## Automated site-audit result
The new CI audit completed successfully against **79 public HTML pages** and checked **4,593 internal links**. It reported: 0 missing titles/descriptions/canonicals, 0 duplicate title groups, 0 duplicate canonical groups, 0 invalid JSON-LD blocks, 0 broken internal links, 0 images missing alt attributes, and 0 noindex pages in the sitemap. The audit is non-blocking while legacy content-quality issues are reviewed; it is now wired into the SEO guard workflow.

## Housekeeping completed
- Archived eight historical hotfix/phase/validation documents under `obsolete/docs/`.
- Archived legacy `admin/` and Cloudflare Pages-style `functions/` code under `obsolete/` because the active deployment uses Wrangler Worker `src/index.js`.
- Archived six tracked Python bytecode files under `obsolete/scripts/__pycache__/`.
- Added `.gitignore` rules to prevent future Python bytecode, local secrets, virtual environments and build artifacts from being tracked.
- Added `obsolete/**` to `.assetsignore` so archived material is retained in Git but never published as website assets.
- No active workflow was removed.

## Next recommended phases
1. Use Search Console exports to prioritize content by impressions, CTR, clicks, position, indexing status and query intent.
2. Review and expand the 16 short feed-derived articles; keep historical URLs until data supports a change.
3. Test Core Web Vitals and ad placement; measure GA4 engagement and AdSense revenue separately.
4. Build topical clusters around SARFAESI, DRT/DRAT, case-status guidance and legal careers, with original expert-led explainers and contextual internal links.

## References
- Google helpful, reliable, people-first content: https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Google News sitemap guidance: https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap
- AdSense programme policies: https://support.google.com/adsense/answer/48182
