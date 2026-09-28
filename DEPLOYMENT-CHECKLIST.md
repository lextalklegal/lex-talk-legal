# Lex Talk Legal — Production Deployment Checklist

1. Upload the complete repository contents to the existing GitHub `main` branch.
2. Verify these files were updated: `index.html`, `assets/site.css`, `assets/site.js`, `scripts/build_site.py`, `src/index.js`, `wrangler.jsonc`.
3. Run the existing GitHub Actions sync once.
4. Cloudflare Worker must have the `ASSETS` binding defined by `wrangler.jsonc`.
5. Create a Cloudflare D1 database and run `db/schema.sql`; bind it as `DB`.
6. For admin review, put the admin email in `ADMIN_EMAILS`, set `TEAM_DOMAIN` to the Cloudflare Access team URL, and set `POLICY_AUD` to the Access application audience tag. Protect `/admin/*` with the corresponding Cloudflare Access application.
7. Keep `RATE_SALT` as a random secret value; do not commit secrets to GitHub.
8. Test: home, article, categories, videos, `/advocates/`, `/advocates/apply`, `/admin/`, search, mobile menu, and old article URLs.
9. Check `robots.txt`, `sitemap.xml`, and `/.well-known/security.txt`.
10. Only after successful preview testing should `lextalk.legal` be pointed to the Worker.
