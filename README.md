# Lex Talk Legal — complete merged Cloudflare Pages repository

This repository preserves the existing Lex Talk Legal editorial site and adds a moderated, free professional-profile system for advocates. The site remains static-first, while Cloudflare Pages Functions + D1 power the profile submission, public profile pages and admin moderation routes.

## Existing systems preserved

- Blogger article sync and generated article/category pages
- YouTube feed sync
- Courtroom / VC destination directory
- Court-wise case-status utility
- Banking / DRT / SARFAESI / career / DRA explainers
- Existing policies, logo, articles and data files
- GitHub Actions content sync

## New profile system

Public:
- `/advocates/` — approved advocate directory
- `/advocates/apply.html` — free profile submission
- `/advocates/<slug>/` — server-rendered approved profile with ProfilePage structured data
- `/profile-guidelines.html` — profile rules

Admin:
- `/admin/profiles` — moderation console
- `/api/admin/profiles` — admin API protected by Cloudflare Access identity + `ADMIN_EMAILS`

Submission flow:
`Submit → Pending → Admin Review → Approved → Public`

Every material admin action is recorded in D1 `audit_log`.

## Cloudflare setup

1. Use a Cloudflare Pages project connected to this GitHub repository and keep `main` as the production branch.
2. Create a D1 database, for example:

```bash
npx wrangler d1 create lex-talk-legal-profiles
```

3. Apply the schema remotely:

```bash
npx wrangler d1 execute lex-talk-legal-profiles --remote --file=db/schema.sql
```

4. In Cloudflare Pages → Settings → Bindings, add a D1 binding named **`DB`** pointing to the new database for production and preview as needed. Pages Functions access D1 through `context.env.DB`.
5. Add a plain-text variable `ADMIN_EMAILS` containing one or more comma-separated admin email addresses.
6. Add a long random `RATE_LIMIT_SALT` secret/variable. Do not commit it to GitHub.
7. Configure Cloudflare Access for `/admin/*` and `/api/admin/*`, allowing only the designated admin email(s). The function still checks the Access-authenticated email against `ADMIN_EMAILS`.
8. Optionally add Turnstile later; the form already includes a honeypot field and server-side rate limiting.

## Local development

Wrangler Pages Functions can be developed with:

```bash
npx wrangler pages dev .
```

For local D1, use a preview binding as documented by Cloudflare or pass the binding on the command line. Do not put production credentials in `.dev.vars` committed to the repository.

## Important safety design

The profile system intentionally does **not** provide:

- paid rankings
- “best lawyer” labels
- star ratings
- guaranteed results
- success-rate fields
- client-review marketplace features
- public publication without admin review

Profiles are informational. Profile holders remain responsible for the accuracy of submitted information and for compliance with professional-conduct rules applicable to them.

## Deployment note

The repository uses the Cloudflare Pages `pages_build_output_dir` configuration with the repository root as the output directory. Cloudflare Pages Functions are discovered from the `/functions` directory.

Do not hard-code database IDs or secrets into source files. Configure bindings/variables in Cloudflare.

## Existing automation

`.github/workflows/sync.yml` periodically runs `scripts/build_site.py` to refresh Blogger, YouTube and public courtroom/case-status data. The build script also preserves the professional-community section and includes profile-related public routes in the static sitemap.
