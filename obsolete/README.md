# Obsolete / Archived Repository Material

This folder preserves source files that are not part of the active production build. It is excluded from Cloudflare static assets by `.assetsignore`.

- `docs/`: historical implementation notes, hotfix reports and validation snapshots. Current operating guidance remains in `README.md`, `docs/`, and the evergreen/editorial setup guides at the repository root.
- `admin/` and `functions/`: legacy Cloudflare Pages-style admin/profile code. Production is a Cloudflare Worker configured by `wrangler.jsonc` with `src/index.js` as its entry point; the root `.assetsignore` excludes these paths and the Worker redirects `/admin` to `/`.
- `scripts/__pycache__/`: generated Python bytecode, not source. `.gitignore` now prevents future Python cache artifacts from being added.

Archived files are retained for reference and should only be permanently deleted after a later review confirms they are no longer needed.