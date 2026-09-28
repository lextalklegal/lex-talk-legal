from pathlib import Path
import ast
import json

root = Path(__file__).resolve().parents[1]
script = root / "scripts" / "build_site.py"
text = script.read_text(encoding="utf-8")
tree = ast.parse(text)
funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
required = {"category_matches", "write_category_pages", "write_videos_page", "sync_homepage", "refresh_static_pages", "main"}
missing = required - funcs
if missing:
    raise SystemExit(f"Missing build functions: {sorted(missing)}")

wrangler_path = root / "wrangler.jsonc"
wrangler = json.loads(wrangler_path.read_text(encoding="utf-8"))
if wrangler.get("name") != "lex-talk-legal":
    raise SystemExit("Unexpected Worker name")
if wrangler.get("workers_dev") is not True:
    raise SystemExit("workers_dev must remain enabled for the legacy-browser compatibility bridge")
if wrangler.get("vars", {}).get("SITE_URL") != "https://lextalk.legal":
    raise SystemExit("Canonical SITE_URL is incorrect")

worker = (root / "src" / "index.js").read_text(encoding="utf-8")
required_worker_markers = [
    'lex-talk-legal.office-lextalklegal.workers.dev',
    'https://lextalk.legal/__legacy-bridge/',
    'status: 302',
    '"Cache-Control": "no-store"',
]
for marker in required_worker_markers:
    if marker not in worker:
        raise SystemExit(f"Legacy bridge marker missing from src/index.js: {marker}")

site_js = (root / "assets" / "site.js").read_text(encoding="utf-8")
if "/__legacy-bridge/" not in site_js or "history.replaceState" not in site_js:
    raise SystemExit("Legacy bridge URL cleanup is missing from assets/site.js")

if 'id="langBtn"' in text or 'Adv. Gagann Jha' in text:
    raise SystemExit("Legacy Hindi control or personal-name content remains in generated build logic")

print("Lex Talk Legal build smoke test passed.")
