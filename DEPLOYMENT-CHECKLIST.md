# Lex Talk Legal — Deployment Checklist

This repository is the merged production codebase built from the exact existing GitHub repository supplied for refinement. Existing articles, data, court/VC utilities, case-status pages, YouTube/Blogger automation and official brand assets are retained.

## 1. Cloudflare Worker
The live architecture is Cloudflare Workers Static Assets with `src/index.js` as the Worker entry point. Static site files are served from the `assets.directory` root, while `/api/*`, `/admin/*` and `/advocates/*` are handled by the Worker.

Deploy with the repository's `wrangler.jsonc`. Keep the `workers.dev` URL for testing until the custom domain is ready. For production, use the custom domain and consider disabling the public `workers.dev` URL after the custom domain is active.

## 2. D1 profile database
Create a Cloudflare D1 database and bind it in `wrangler.jsonc` as:

```jsonc
"d1_databases": [
  { "binding": "DB", "database_name": "lex-talk-legal-profiles", "database_id": "REPLACE_WITH_REAL_DATABASE_ID" }
]
```

Apply `db/schema.sql` to the database. Do not put a real database ID, token or credential in source-control unless it is intended to be public metadata; secrets must remain in Cloudflare/GitHub secret storage.

Until `DB` is bound, profile pages and submission endpoints deliberately show a configuration message and do not create partial records.

## 3. Admin security — mandatory
Protect these paths with Cloudflare Access:

- `/admin/*`
- `/api/admin/*`

The Worker also uses Cloudflare Access identity (`ctx.access.getIdentity()`) as a defense-in-depth check and only permits emails listed in the `ADMIN_EMAILS` Worker variable. A browser-supplied `CF-Access-Authenticated-User-Email` header is not trusted by the Worker.

Set:

```text
ADMIN_EMAILS=your-authorized-email@example.com
RATE_LIMIT_SALT=<random-long-value>
```

as Cloudflare Worker variables/secrets. Never commit real secret values.

## 4. Professional profiles
Public directory: `/advocates/`

Application: `/advocates/apply.html`

Profile lifecycle:

`Pending → Under Review → Published / Rejected / Suspended`

Material profile edits are intended to return to moderation. The public profile design deliberately avoids paid ranking, star ratings, success-rate claims, guaranteed outcomes and “best lawyer” labels.

## 5. Hindi / English UI
The website chrome now uses a deterministic local language switch. It does not depend on Google's legacy website-translation widget and it does not automatically machine-translate user-submitted professional profiles or full editorial articles.

The language preference is stored locally in the browser. The current code version includes a one-time migration key so an earlier translation state cannot silently force the new UI into the wrong initial language.

## 6. Security / privacy
Before accepting production profile submissions, review the live Privacy Policy, Terms, Profile Guidelines and Corrections / Grievance process. Uploaded identity documents are not part of the public profile model. Public profiles expose only the information intentionally published by the profile holder after review.

## 7. Automated sync
`.github/workflows/sync.yml` continues the existing scheduled Blogger, YouTube and public VC synchronization. The sync script also regenerates category pages, the homepage and sitemap.

The sync script has a fallback for VC extraction failures so a temporary Playwright/browser/network problem does not erase the previously cached VC directory.

## 8. Final production checks
After deployment, test:

1. Home page and mobile layout.
2. Hindi ↔ English toggle and Dark mode.
3. Existing article URLs and category pages.
4. YouTube section and Courtroom / Case Status utilities.
5. `/advocates/` directory and `/advocates/apply.html`.
6. D1 profile submission after database binding.
7. Cloudflare Access protection on `/admin/*` and `/api/admin/*`.
8. Admin approve/reject/suspend/note actions.
9. `robots.txt`, `sitemap.xml`, canonical tags and profile structured data.
10. `lextalk.legal` custom domain before treating the `workers.dev` URL as production.
