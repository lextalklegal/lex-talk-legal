from pathlib import Path
import ast

root = Path(__file__).resolve().parents[1]
script = root / "scripts" / "build_site.py"
text = script.read_text(encoding="utf-8")
tree = ast.parse(text)
funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
required = {
    "category_matches",
    "write_category_pages",
    "write_videos_page",
    "sync_homepage",
    "refresh_static_pages",
    "write_news_sitemap",
    "write_sitemap",
    "main",
}
missing = required - funcs
if missing:
    raise SystemExit(f"Missing build functions: {sorted(missing)}")

robots = (root / "robots.txt").read_text(encoding="utf-8")
for sitemap in (
    "https://lextalk.legal/sitemap.xml",
    "https://lextalk.legal/news-sitemap.xml",
):
    if sitemap not in robots:
        raise SystemExit(f"robots.txt is missing sitemap reference: {sitemap}")

if not (root / ".github/workflows/pib-radar.yml").exists():
    raise SystemExit("PIB radar workflow is missing")
if not (root / "scripts/fetch_pib.py").exists():
    raise SystemExit("PIB fetcher is missing")
if not (root / "news-sitemap.xml").exists():
    raise SystemExit("news-sitemap.xml is missing")

if 'id="langBtn"' in text or 'Adv. Gagann Jha' in text:
    raise SystemExit("Legacy Hindi control or personal-name content remains in generated build logic")

print("Lex Talk Legal SEO + PIB smoke test passed.")
