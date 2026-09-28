# Lex Talk Legal — Cloudflare Deployment Checklist

## Required GitHub Actions secrets

Create these repository secrets:

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

Do **not** put the token in source code, `wrangler.jsonc`, a `.env` file, or any committed file.

## Token scope

Use a dedicated Cloudflare API token with the minimum permissions required to deploy the existing `lex-talk-legal` Worker. Cloudflare recommends limiting CI/CD tokens to the account/resources actually used by the deployment.

## Deployment flow

1. Push/commit to `main`.
2. `Deploy Lex Talk Legal Worker` runs.
3. Wrangler deploys the Worker and the static assets defined in `wrangler.jsonc`.
4. Check the deployment under Cloudflare Workers > `lex-talk-legal` > Deployments.
5. Verify:
   - `https://lextalk.legal`
   - `https://lex-talk-legal.office-lextalklegal.workers.dev`

## Existing custom domain

The `lextalk.legal` custom domain is expected to already be attached to the production Worker. Do not recreate the custom domain during routine content deployments.

## Important security note

If a Cloudflare API token or R2 access credential is ever pasted into chat, source code, GitHub, or another exposed location, revoke/rotate it and create a replacement. Never commit credentials to the repository.
