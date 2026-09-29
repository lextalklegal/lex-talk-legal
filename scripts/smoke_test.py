from pathlib import Path
import ast
import json
import re

root = Path(__file__).resolve().parents[1]
script = root / "scripts" / "build_site.py"
text = script.read_text(encoding="utf-8")
tree = ast.parse(text)
funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
required = {"category_matches", "write_category_pages", "write_videos_page", "sync_homepage", "main", "page_shell"}
missing = required - funcs
if missing:
    raise SystemExit(f"Missing build functions: {sorted(missing)}")

# The editorial builder must never depend on third-party manual directory scraping.
for rel in [
    "scripts/build_site.py",
    "scripts/build_vc.py",
    "scripts/build_auctions.py",
    "scripts/build_jobs.py",
    ".github/workflows/sync-editorial.yml",
    ".github/workflows/update-vc.yml",
    ".github/workflows/update-auctions.yml",
    ".github/workflows/update-jobs.yml",
]:
    body = (root / rel).read_text(encoding="utf-8").lower()
    for forbidden in ("playwright", "onecourt.in", "extract_onecourt_vc"):
        if forbidden in body:
            raise SystemExit(f"{rel} contains forbidden dependency/reference: {forbidden}")

# Main editorial build may only own editorial outputs.
main_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
main_source = ast.get_source_segment(text, main_node) or ""
for forbidden in ("write_config(", "refresh_static_pages(", "write_courtrooms_page(", "write_auctions_page(", "write_team_page(", "write_case_help_page(", "write_case_status_page("):
    if forbidden in main_source:
        raise SystemExit(f"main() must not call manual/static rebuild: {forbidden}")

if (root / "build_site.py").exists():
    raise SystemExit("Duplicate root build_site.py is not allowed")

required_files = [
    "assets/site.css", "assets/site.js",
    "assets/pages/about.css", "assets/pages/contact.css",
    "assets/pages/courts.css", "assets/pages/banking-law.css",
    "assets/pages/dra.css", "assets/pages/videos.css",
    "templates/category/courts.html", "templates/category/banking-law.html",
    "templates/category/dra.html", "templates/videos.html",
    "templates/courtrooms.html", "templates/auctions.html", "templates/jobs.html",
    "data/vc_links.json", "data/auctions.json", "data/jobs.json",
    "scripts/manage_vc.py", "scripts/manage_auction.py", "scripts/manage_job.py",
    ".github/workflows/sync-editorial.yml", ".github/workflows/deploy-worker.yml",
    ".github/workflows/update-vc.yml", ".github/workflows/update-auctions.yml",
    ".github/workflows/update-jobs.yml",
]
for rel in required_files:
    if not (root / rel).exists():
        raise SystemExit(f"Required file missing: {rel}")

# Page-specific styles must be explicitly linked.
for rel, css in [
    ("about.html", "/assets/pages/about.css"),
    ("contact.html", "/assets/pages/contact.css"),
    ("category/courts/index.html", "/assets/pages/courts.css"),
    ("category/banking-law/index.html", "/assets/pages/banking-law.css"),
    ("category/dra/index.html", "/assets/pages/dra.css"),
    ("videos/index.html", "/assets/pages/videos.css"),
]:
    page = (root / rel).read_text(encoding="utf-8")
    if css not in page:
        raise SystemExit(f"{rel} is missing its page-specific stylesheet link: {css}")

# Generated templates must retain dynamic placeholders.
for rel, marker in [
    ("templates/category/courts.html", "{{LATEST_STORIES}}"),
    ("templates/category/banking-law.html", "{{LATEST_STORIES}}"),
    ("templates/category/dra.html", "{{LATEST_STORIES}}"),
    ("templates/videos.html", "{{FEATURED_HTML}}"),
    ("templates/videos.html", "{{VIDEO_GRID}}"),
    ("templates/courtrooms.html", "{{SC_CARDS}}"),
    ("templates/auctions.html", "{{AUCTION_CARDS}}"),
    ("templates/jobs.html", "{{JOB_CARDS}}"),
]:
    if marker not in (root / rel).read_text(encoding="utf-8"):
        raise SystemExit(f"Template placeholder missing: {rel} -> {marker}")

# Manual data shapes.
vc = json.loads((root / "data/vc_links.json").read_text(encoding="utf-8"))
if not isinstance(vc, dict):
    raise SystemExit("data/vc_links.json must be a JSON object")
for top, val in vc.items():
    if isinstance(val, dict):
        for key in val:
            if "onecourt" in str(key).lower() or "checking your browser" in str(key).lower():
                raise SystemExit(f"Stale OneCourt scrape key remains in VC data: {top} -> {key}")
for name in ("auctions", "jobs"):
    data = json.loads((root / "data" / f"{name}.json").read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"data/{name}.json must be a JSON array")

# Static/manual/build-only files must not be published as Worker assets.
ignore = (root / ".assetsignore").read_text(encoding="utf-8").lower()
for item in ("node_modules", "templates", "data", "functions", "scripts", "src", "wrangler.jsonc", "site-config.json"):
    if item not in ignore:
        raise SystemExit(f".assetsignore missing: {item}")

# Production deployment workflow must be the only workflow using Wrangler.
deploy = (root / ".github/workflows/deploy-worker.yml").read_text(encoding="utf-8")
if "wrangler-action@v4" not in deploy or "CLOUDFLARE_API_TOKEN" not in deploy or "CLOUDFLARE_ACCOUNT_ID" not in deploy:
    raise SystemExit("Production deployment workflow is missing Wrangler credentials/action")
for wf in ("sync-editorial.yml", "update-vc.yml", "update-auctions.yml", "update-jobs.yml"):
    body = (root / ".github/workflows" / wf).read_text(encoding="utf-8").lower()
    if "wrangler-action" in body or "wrangler deploy" in body:
        raise SystemExit(f"{wf} must not deploy the Worker directly")

# Manual workflows should be dispatchable and provide their intended data fields.
for wf, markers in {
    "update-vc.yml": ["workflow_dispatch", "VC_URL", "VC_MEETING_ID", "VC_PASSWORD", "data/vc_links.json"],
    "update-auctions.yml": ["workflow_dispatch", "AUCTION_ID", "AUCTION_OFFICIAL_URL", "data/auctions.json"],
    "update-jobs.yml": ["workflow_dispatch", "JOB_ID", "JOB_APPLY_URL", "data/jobs.json"],
}.items():
    body = (root / ".github/workflows" / wf).read_text(encoding="utf-8")
    for marker in markers:
        if marker not in body:
            raise SystemExit(f"{wf} is missing manual-input marker: {marker}")

# Manual data desks are intentionally on-demand only; no scheduled/push polling.
for wf in ("update-vc.yml", "update-auctions.yml", "update-jobs.yml"):
    body = (root / ".github/workflows" / wf).read_text(encoding="utf-8")
    on_block = body.split("permissions:", 1)[0]
    if "schedule:" in on_block or "push:" in on_block:
        raise SystemExit(f"{wf} must be manual/on-demand only")

print("Lex Talk Legal stable-architecture smoke test passed.")
