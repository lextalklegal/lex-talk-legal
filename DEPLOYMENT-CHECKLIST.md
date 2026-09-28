# Lex Talk Legal v8 — Deployment Checklist

1. Upload/replace the complete repository on GitHub `main`.
2. Confirm `index.html`, `assets/site.css`, `assets/site.js`, `scripts/build_site.py`, `src/index.js` and `wrangler.jsonc` are the latest files.
3. Run the existing GitHub Actions sync once.
4. Hard-refresh the Cloudflare deployment and check the homepage at desktop and mobile widths.
5. Check `/auctions/`, `/case-help.html`, `/team.html`, `/search.html`, `/courtrooms/`, `/case-status/` and `/videos/`.
6. Confirm article pages show one lead image and no duplicated copy of that image in the article body.
7. Confirm the light/dark toggle works and the old Hindi/translation UI is absent.
8. In Google AdSense, add the production site and complete site verification/review before expecting ads to serve. Keep `ads.txt` aligned with the final publisher account.
9. After the domain is moved to Cloudflare DNS, connect the production domain and use the custom domain as the public canonical URL.
10. Before enabling any future case-file upload, configure private object storage, authenticated access, file limits, malware screening, retention/deletion, audit logging and the applicable privacy/consent notices.
