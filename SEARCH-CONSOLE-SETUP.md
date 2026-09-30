# Lex Talk Legal — Google Search Console Setup

## One-time setup

### 1. Add the Domain property

1. Open Google Search Console: https://search.google.com/search-console
2. Click the property selector at the top-left.
3. Click **+ Add property**.
4. Select **Domain**.
5. Enter exactly:

   `lextalk.legal`

   Do not enter `https://`, `www`, or a page path. A Domain property covers the domain across protocols and subdomains.

6. Google will show a DNS **TXT** verification value.
7. In Cloudflare, open the `lextalk.legal` zone → **DNS → Records → Add record**.
8. Choose **TXT**.
9. Set **Name** to `@` (or the root, depending on the Cloudflare UI).
10. Paste Google’s exact `google-site-verification=...` value into **Content**.
11. Save the record.
12. Return to Search Console and click **Verify**.

Do not invent or reuse a verification token. The token must be the exact value Google gives to this Search Console property.

### 2. Submit both sitemaps

After verification, open **Sitemaps** and submit these paths one at a time:

- `sitemap.xml`
- `news-sitemap.xml`

Google’s Search Console documentation recommends the Sitemaps report for submitting and monitoring sitemaps. Sitemaps help discovery but do not guarantee indexing.

### 3. Run URL Inspection

Inspect these important URLs first:

- `https://lextalk.legal/`
- `https://lextalk.legal/category/courts/`
- `https://lextalk.legal/category/law-policy/`
- `https://lextalk.legal/category/banking-law/`
- `https://lextalk.legal/category/drt-drat/`
- `https://lextalk.legal/courtrooms/`
- `https://lextalk.legal/case-status/`
- one current article URL

For important newly published pages, use **Request indexing** after confirming the live URL is accessible and canonical.

## What this repository now provides

- Standard sitemap: `/sitemap.xml`
- News sitemap: `/news-sitemap.xml` for recent news articles
- `robots.txt` references both sitemaps
- Article pages use `NewsArticle` structured data
- Blogger `updated` timestamps feed article `dateModified` where available
- PIB releases go into `data/pib_queue.json` and are **not automatically republished**
- The Editorial Sync workflow now commits `news-sitemap.xml` whenever it is regenerated
- Approved page-specific CSS mappings are preserved during recurring editorial builds
- Footer timestamp remains an exact build date/time instead of being rewritten to relative text
