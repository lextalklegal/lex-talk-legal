Lex Talk Legal — Stability Hotfix — 29 September 2026

Replace only these existing repository files:
.assetsignore
scripts/build_site.py
.github/workflows/update-vc.yml
.github/workflows/update-auctions.yml
.github/workflows/update-jobs.yml

Do NOT change header/menu/footer files.

Validated locally:
- Python compilation: PASS
- stable-architecture smoke test: PASS
- two consecutive offline editorial builds: identical
- manual VC builder: PASS
- manual Auctions builder: PASS
- manual Jobs builder: PASS

The manual desk workflows are workflow_dispatch-only so editing their data/templates does not unexpectedly trigger them. Deployment remains handled by deploy-worker.yml.
