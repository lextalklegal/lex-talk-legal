# Lex Talk Legal — Google Search Console Setup

## One-time setup

1. Open Google Search Console and add a **Domain property** for `lextalk.legal`.
2. Verify the domain through the DNS method Google provides for the property.
3. After verification, open **Sitemaps** and submit:
   - `https://lextalk.legal/sitemap.xml`
   - `https://lextalk.legal/news-sitemap.xml`
4. Use **URL Inspection** for the homepage and a few representative articles/category pages and request indexing where appropriate.
5. Return to Search Console periodically and monitor indexing, performance, queries, impressions, clicks and CTR.

Google says sitemaps help discovery but do not guarantee indexing, and recrawling/reindexing can take time. Keep the sitemap URLs submitted and use URL Inspection for important newly published pages. 

## Recommended first URLs to inspect

- https://lextalk.legal/
- https://lextalk.legal/category/courts/
- https://lextalk.legal/category/law-policy/
- https://lextalk.legal/category/banking-law/
- https://lextalk.legal/category/drt-drat/
- https://lextalk.legal/courtrooms/
- https://lextalk.legal/case-status/
- one recent article URL

## What this repository now provides

- Standard sitemap: `/sitemap.xml`
- News sitemap: `/news-sitemap.xml` for articles from the most recent 48 hours
- `robots.txt` references both sitemaps
- Article pages use `NewsArticle` structured data
- Blogger `updated` timestamps are captured for article `dateModified`
- PIB releases are collected into a private-to-site editorial queue at `data/pib_queue.json` and are **not automatically republished**
