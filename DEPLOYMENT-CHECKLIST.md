# Lex Talk Legal — Cloudflare Deployment Checklist

## Required GitHub Actions secrets

Create these repository secrets:

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

Do **not** put the token in source code, `wrangler.jsonc`, a `.env` file, or any committed file.

## Token scope

Use a dedicated Cloudflare API token with the minimum permissions required to deploy the existing `lex-talk-legal` Worker. Cloudflare's current GitHub Actions guidance uses the **Edit Cloudflare Workers** permission policy and recommends narrowing the token to the account actually used by the deployment.

## Deployment flow

1. Upload/push the repository contents to the `main` branch.
2. `.github/workflows/deploy-worker.yml` deploys the Worker and static assets.
3. `.github/workflows/sync.yml` refreshes Blogger, YouTube and public court/VC data every 30 minutes. When it commits generated changes, it deploys the same committed build in the same workflow run.
4. Check the deployment under Cloudflare Workers > `lex-talk-legal` > Deployments.
5. Verify:
   - `https://lextalk.legal`

## Existing custom domain

The `lextalk.legal` custom domain is expected to already be attached to the production Worker. Custom Domains route the hostname directly to the Worker and are the appropriate production setup for this site.

## Legacy browser compatibility

Some visitors may have an old browser-cached permanent redirect from an earlier deployment that pointed `lextalk.legal` to the former `workers.dev` hostname. The Worker keeps the production `workers.dev` endpoint available only as a compatibility bridge: it returns a temporary redirect to a canonical-domain bridge path, and the shared site JavaScript silently restores the visible address bar to `https://lextalk.legal/`.

This compatibility path is intentionally temporary-redirect based (`302`) and uses `Cache-Control: no-store`; it does not create another permanent redirect.

## Wrangler source of truth

`wrangler.jsonc` intentionally keeps `"workers_dev": true` for the legacy compatibility bridge. Cloudflare recommends production Workers run on a custom domain or route rather than relying on `workers.dev`.

Do not manually disable `workers.dev` in the dashboard while the legacy bridge is still needed. If you later want to retire the bridge after the old cached redirects have aged out, first remove the bridge code and test the site across fresh profiles.

## Important security note

If a Cloudflare API token or R2 access credential is ever pasted into chat, source code, GitHub, or another exposed location, revoke/rotate it and create a replacement. Never commit credentials to the repository.
