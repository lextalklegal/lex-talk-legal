from pathlib import Path
import ast

root = Path(__file__).resolve().parents[1]
script = root / "scripts" / "build_site.py"
text = script.read_text(encoding="utf-8")
tree = ast.parse(text)
funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
required = {"category_matches", "write_category_pages", "write_videos_page", "sync_homepage", "refresh_static_pages", "main"}
missing = required - funcs
if missing:
    raise SystemExit(f"Missing build functions: {sorted(missing)}")
if 'id="langBtn"' in text or 'Adv. Gagann Jha' in text:
    raise SystemExit("Legacy Hindi control or personal-name content remains in generated build logic")
print("Lex Talk Legal build smoke test passed.")
