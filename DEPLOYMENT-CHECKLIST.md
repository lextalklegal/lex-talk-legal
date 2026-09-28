# Lex Talk Legal — Deployment Checklist

## Before pushing to GitHub

- Confirm `site-config.json` uses `https://lextalk.legal`.
- Confirm no real secrets are present in source.
- Keep `dev.vars` local only; `.gitignore` excludes it.
- Keep the existing official logo assets in `assets/`.

## Cloudflare Pages

1. Connect the GitHub repository to the Cloudflare Pages project.
2. Production branch: `main`.
3. Build output directory: repository root (`.`) when using the current Wrangler Pages configuration.
4. Ensure Pages Functions are enabled/discovered from `/functions`.

## D1 profile database

Create the database:

```bash
npx wrangler d1 create lex-talk-legal-profiles
```

Apply schema:

```bash
npx wrangler d1 execute lex-talk-legal-profiles --remote --file=db/schema.sql
```

Then bind the database as **`DB`** in Cloudflare Pages → Settings → Bindings for production (and preview if required).

## Admin protection

Set a Pages/Worker variable:

`ADMIN_EMAILS=your-admin@example.com`

Set a long random variable/secret:

`RATE_LIMIT_SALT=<long-random-value>`

Configure Cloudflare Access so that these paths are restricted to the admin email(s):

- `/admin/*`
- `/api/admin/*`

The application also checks the Cloudflare Access-authenticated email against `ADMIN_EMAILS`.

## Recommended launch checks

- Submit a test profile.
- Confirm it stays `pending` and is not public.
- Open `/admin/profiles` while authenticated through Cloudflare Access.
- Approve the test profile.
- Confirm `/advocates/` shows it.
- Confirm `/advocates/<slug>/` is server-rendered.
- Confirm the profile URL has a canonical link and ProfilePage JSON-LD.
- Reject a second test profile and confirm it is not public.
- Test suspension and restoration.
- Test invalid URLs, oversized submissions and repeated submissions.
- Confirm `/admin/` and `/api/admin/` are not indexed/cached publicly.
- Confirm existing Blogger, YouTube, Courtroom and Case Status pages still work.
- Confirm the official logo renders from `/assets/LexTalkLegal_Logo-wo-bg.png`.
