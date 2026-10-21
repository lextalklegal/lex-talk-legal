# GA4 Workflow Hotfix

The Editorial Sync workflow intentionally does **not** run the full smoke test before the Blogger/YouTube build. Generated article HTML may be stale at checkout and can legitimately lack the current GA4 tag until `scripts/build_site.py` regenerates the article pages.

The workflow now:

1. Compiles the build scripts.
2. Repairs stale public GA4 tags with `scripts/ensure_public_ga.py`.
3. Runs the Blogger/YouTube sync.
4. Repairs GA4 coverage again after generation.
5. Runs the full smoke test only on the generated build.
6. Commits the editorial outputs and the GA guard.

The deployment workflow also runs the GA guard and the full smoke test before Cloudflare deployment. This prevents missing analytics tags from reaching production while avoiding the old false failure caused by validating stale generated HTML before the sync.
