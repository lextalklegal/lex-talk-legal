# Timestamp Deployment Guard

`data/site_meta.json` is the authoritative site-wide publication timestamp.

Before deployment, GitHub Actions runs `scripts/sync_public_timestamps.py`.
This does not create a new timestamp; it only repairs any public HTML footer
markers that may have drifted from the authoritative `site_meta.json` value.

The strict smoke test then verifies that all public HTML pages match the same
site-wide timestamp. This keeps deployed HTML and the runtime `assets/site.js`
loader consistent without requiring a timestamp refresh on every deployment.
