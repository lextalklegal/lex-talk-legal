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


# The timestamp is intentionally fixed to the build time in the HTML.
site_js = (root / "assets/site.js").read_text(encoding="utf-8")
if "el.textContent='Content last updated: '+label" in site_js:
    raise SystemExit("site.js is still rewriting the exact timestamp into relative time")

law_policy = (root / "category/law-policy/index.html").read_text(encoding="utf-8")
if '/assets/pages/law-policy.css' not in law_policy:
    raise SystemExit("Law & Policy page-specific stylesheet is missing")
if '<main class="lawpolicy-v2">' not in law_policy:
    raise SystemExit("Law & Policy approved template is not being used")

for rel, css in {
    "category/courts/index.html": "courts.css",
    "category/banking-law/index.html": "banking-law.css",
    "category/dra/index.html": "dra.css",
    "about.html": "about.css",
    "contact.html": "contact.css",
}.items():
    page = (root / rel).read_text(encoding="utf-8")
    if f"/assets/pages/{css}" not in page:
        raise SystemExit(f"Page-specific stylesheet is missing: {rel}")

articles = []
try:
    import json
    articles = json.loads((root / "data/articles.json").read_text(encoding="utf-8"))
except Exception:
    pass
if any(a.get("published") for a in articles if isinstance(a, dict)):
    news_xml = (root / "news-sitemap.xml").read_text(encoding="utf-8")
    recent_titles = [str(a.get("title", "")) for a in articles if isinstance(a, dict) and a.get("title")]
    if not recent_titles or not any(title in news_xml for title in recent_titles):
        raise SystemExit("news-sitemap.xml does not contain any current article titles")


# Phase 2 article SEO / Google News readiness checks.
article_files=sorted((root / "article").glob("*.html"))
if article_files:
    sample=article_files[0].read_text(encoding="utf-8")
    for required in (
        "/assets/pages/article.css",
        '"@type": "NewsArticle"',
        '"datePublished"',
        '"dateModified"',
        '"@type": "BreadcrumbList"',
        'Published:',
        'Lex Talk Legal Editorial Desk',
    ):
        if required not in sample:
            raise SystemExit(f"Phase 2 article SEO marker missing: {required}")

source_keys=[]
for item in articles:
    if isinstance(item,dict) and item.get("source_url"):
        source_keys.append(str(item["source_url"]).split("#")[0].split("?")[0].rstrip("/").lower())
if len(source_keys) != len(set(source_keys)):
    raise SystemExit("Duplicate article source URLs remain after editorial dedupe")

article_rows=[a for a in articles if isinstance(a,dict)]
if len(set(a.get("url") for a in article_rows)) != len(article_rows):
    raise SystemExit("Duplicate article URLs remain after editorial dedupe")

import re as _re
locs=_re.findall(r"<loc>(.*?)</loc>", (root/"sitemap.xml").read_text(encoding="utf-8"))
if len(locs) != len(set(locs)):
    raise SystemExit("Duplicate URLs remain in sitemap.xml")
news_locs=_re.findall(r"<loc>(.*?)</loc>", (root/"news-sitemap.xml").read_text(encoding="utf-8"))
if len(news_locs) != len(set(news_locs)):
    raise SystemExit("Duplicate URLs remain in news-sitemap.xml")

long_headlines=[str(a.get("title","")) for a in article_rows if len(str(a.get("title","")))>110]
if long_headlines:
    print(f"Warning: {len(long_headlines)} current article headline(s) exceed Google News' 110-character best-practice threshold; review them in Blogger.")

redirects=(root/"_redirects").read_text(encoding="utf-8")
for old_url,new_url in (
    ("/article/blog00111.html", "/article/delhi-high-court-slaps-1-lakh-costs-on-advocate-for-attending-hearing-from-a-moving-car.html"),
    ("/article/india-bloc-meet-on-gyanesh-kumar-election-commission-row-sir-controversy-explained.html", "/article/india-block-meet-on-gyanesh-kumar-election-commission-row-sir-controversy-explained.html"),
):
    if f"{old_url} {new_url} 301" not in redirects:
        raise SystemExit(f"Legacy article redirect missing: {old_url}")
