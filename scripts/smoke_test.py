from pathlib import Path
import ast
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build_site.py"
BUILD_TEXT = BUILD.read_text(encoding="utf-8")
TREE = ast.parse(BUILD_TEXT)
FUNCTIONS = {node.name for node in ast.walk(TREE) if isinstance(node, ast.FunctionDef)}

REQUIRED_FUNCTIONS = {
    "category_matches",
    "write_category_pages",
    "write_videos_page",
    "sync_homepage",
    "refresh_static_pages",
    "write_news_sitemap",
    "write_sitemap",
    "load_evergreen_articles",
    "write_evergreen_articles",
    "main",
}
missing = REQUIRED_FUNCTIONS - FUNCTIONS
if missing:
    raise SystemExit(f"Missing build functions: {sorted(missing)}")

MAIN_NODE = next(
    (node for node in TREE.body if isinstance(node, ast.FunctionDef) and node.name == "main"),
    None,
)
if MAIN_NODE is None:
    raise SystemExit("main() function is missing")

# Permanent page-ownership guard: the common editorial builder must not rewrite
# protected manual/workflow-owned pages during a recurring content sync.
PROTECTED_WRITERS = {
    "write_courtrooms_page",
    "write_case_status_page",
    "write_team_page",
    "write_case_help_page",
    "write_auctions_page",
    "write_search_page",
    "under_construction_page",
}
main_calls = {
    node.func.id
    for node in ast.walk(MAIN_NODE)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
}
for forbidden in sorted(PROTECTED_WRITERS & main_calls):
    raise SystemExit(
        f"Protected page builder is still called by build_site.py main(): {forbidden}"
    )
if "extract_onecourt_vc" in main_calls:
    raise SystemExit("Automatic OneCourt extraction must not run in the common editorial builder")

if "PAGE_OWNERSHIP = {" not in BUILD_TEXT:
    raise SystemExit("PAGE_OWNERSHIP manifest is missing from build_site.py")

# Basic repository / indexing safeguards.
robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
for sitemap in (
    "https://lextalk.legal/sitemap.xml",
    "https://lextalk.legal/news-sitemap.xml",
):
    if sitemap not in robots:
        raise SystemExit(f"robots.txt is missing sitemap reference: {sitemap}")

for required_path in (
    ROOT / ".github/workflows/pib-radar.yml",
    ROOT / "scripts/fetch_pib.py",
    ROOT / "news-sitemap.xml",
):
    if not required_path.exists():
        raise SystemExit(f"Required SEO/PIB file is missing: {required_path.relative_to(ROOT)}")

if 'id="langBtn"' in BUILD_TEXT or "Adv. Gagann Jha" in BUILD_TEXT:
    raise SystemExit("Legacy Hindi control or personal-name content remains in generated build logic")

site_js = (ROOT / "assets/site.js").read_text(encoding="utf-8")
if "hydrateBuildTimestamp" not in site_js or "/data/site_meta.json" not in site_js:
    raise SystemExit("site.js is missing the unified exact timestamp loader")
if "toRelative" in site_js or "ago" in site_js:
    raise SystemExit("site.js contains relative timestamp logic")

if "G-3KT3SQPFXD" not in BUILD_TEXT:
    raise SystemExit("Google Analytics Measurement ID is missing from build_site.py")

# One site-wide timestamp is the single source of truth for every visible footer.
meta_path = ROOT / "data/site_meta.json"
try:
    site_meta = json.loads(meta_path.read_text(encoding="utf-8"))
except Exception as exc:
    raise SystemExit(f"Unable to read data/site_meta.json: {exc}")
site_timestamp = str(site_meta.get("built_at_ist", "")).strip()
site_epoch = str(site_meta.get("built_at_epoch", "")).strip()
if not site_timestamp or not site_epoch:
    raise SystemExit("data/site_meta.json must contain built_at_ist and built_at_epoch")

# Every public HTML page must carry exactly one GA4 tag. This prevents a future
# build/sync from silently dropping analytics coverage or injecting duplicates.
public_html = []
for page in ROOT.rglob("*.html"):
    rel = page.relative_to(ROOT)
    if any(part in rel.parts for part in ("templates", "content", "admin", "docs", ".git")):
        continue
    public_html.append(page)
for page in sorted(public_html):
    text = page.read_text(encoding="utf-8")
    if "<head" not in text.lower():
        continue
    timestamp_match = re.search(
        r'<div class="updated-line"\s+data-built-at="([^"]*)"\s+data-built-epoch="([^"]*)">Content last updated: ([^<]*)</div>',
        text,
    )
    if not timestamp_match:
        raise SystemExit(f"Unified footer timestamp marker is missing: {page.relative_to(ROOT)}")
    baked_time = str(timestamp_match.group(1)).strip()
    baked_epoch = str(timestamp_match.group(2)).strip()
    baked_label = str(timestamp_match.group(3)).strip()
    if "data-built-at=" not in timestamp_match.group(0) or "data-built-epoch=" not in timestamp_match.group(0):
        raise SystemExit(f"Unified footer timestamp attributes are missing: {page.relative_to(ROOT)}")
    if baked_time != site_timestamp or baked_epoch != site_epoch or baked_label != site_timestamp:
        raise SystemExit(
            f"Timestamp inconsistency: {page.relative_to(ROOT)} "
            f"does not match data/site_meta.json"
        )
    src_count = text.count('https://www.googletagmanager.com/gtag/js?id=G-3KT3SQPFXD')
    config_count = text.count("gtag('config', 'G-3KT3SQPFXD')")
    if src_count != 1 or config_count != 1:
        raise SystemExit(
            f"Google Analytics tag coverage error: {page.relative_to(ROOT)} "
            f"has {src_count} loader + {config_count} config occurrence(s)"
        )

# Evergreen source/public ownership and SEO contracts.
evergreen_source = ROOT / "content/evergreen"
if not evergreen_source.exists():
    raise SystemExit("Evergreen source directory is missing: content/evergreen")
evergreen_files = sorted(evergreen_source.glob("*.html"))
if not evergreen_files:
    raise SystemExit("No evergreen source articles found in content/evergreen")
for source in evergreen_files:
    raw = source.read_text(encoding="utf-8")
    if "Lex Talk Legal Evergreen Metadata" not in raw:
        raise SystemExit(f"Evergreen metadata block is missing: {source.relative_to(ROOT)}")
    if "<h1>" not in raw.lower() or "<article" not in raw.lower():
        raise SystemExit(f"Evergreen source article structure is incomplete: {source.relative_to(ROOT)}")

evergreen_public = sorted((ROOT / "article" / "evergreen").glob("*.html"))
if len(evergreen_public) != len(evergreen_files):
    raise SystemExit(f"Evergreen output count mismatch: source={len(evergreen_files)} public={len(evergreen_public)}")
for page in evergreen_public:
    page_text = page.read_text(encoding="utf-8")
    for marker in (
        "/assets/pages/article.css",
        "\"datePublished\"",
        "\"dateModified\"",
        "Lex Talk Legal Editorial Desk",
        "Evergreen legal guide",
    ):
        if marker not in page_text:
            raise SystemExit(f"Evergreen SEO marker missing: {page.relative_to(ROOT)} -> {marker}")
    if '"@type": "NewsArticle"' in page_text:
        raise SystemExit(f"Evergreen page must use Article, not NewsArticle: {page.relative_to(ROOT)}")

# Approved page-design contracts. A future sync/build must fail before commit if
# any approved page falls back to a generic legacy <main> class or loses its CSS.
PAGE_DESIGN_CONTRACTS = {
    "about.html": ("about.css", "about-v3"),
    "contact.html": ("contact.css", "contact-v4"),
    "category/courts/index.html": ("courts.css", "courts-v2"),
    "category/law-policy/index.html": ("law-policy.css", "lawpolicy-v2"),
    "category/banking-law/index.html": ("banking-law.css", "banking-v1"),
    "category/dra/index.html": ("dra.css", "dra-v1"),
    "videos/index.html": ("videos.css", "videos-v2"),
    "case-status/index.html": ("case-status.css", "case-status-v2"),
    "courtrooms/index.html": ("courtrooms.css", "courtrooms-page"),
    "category/explained/index.html": ("explained.css", "explained-v1"),
}


def main_classes(page_text: str):
    match = re.search(r'<main\b[^>]*\bclass="([^"]+)"', page_text)
    return set(match.group(1).split()) if match else set()


for rel, (css, expected_class) in PAGE_DESIGN_CONTRACTS.items():
    page_path = ROOT / rel
    if not page_path.exists():
        raise SystemExit(f"Approved page is missing: {rel}")
    page_text = page_path.read_text(encoding="utf-8")
    if f"/assets/pages/{css}" not in page_text:
        raise SystemExit(f"Page-specific stylesheet is missing: {rel}")
    if expected_class not in main_classes(page_text):
        raise SystemExit(f"Approved page design marker is missing: {rel} -> {expected_class}")

# Template-backed page contracts.
for template in (
    ROOT / "templates/videos.html",
    ROOT / "templates/courtrooms.html",
    ROOT / "templates/case-status.html",
):
    if not template.exists():
        raise SystemExit(f"Protected page source template is missing: {template.relative_to(ROOT)}")

video_template = (ROOT / "templates/videos.html").read_text(encoding="utf-8")
for marker in ("{{VIDEO_COUNT}}", "{{FEATURED_HTML}}", "{{VIDEO_GRID}}", "videos-v2"):
    if marker not in video_template:
        raise SystemExit(f"Videos template marker is missing: {marker}")

explained_template = (ROOT / "templates/category/explained.html").read_text(encoding="utf-8")
for marker in ("{{EVERGREEN_GUIDES}}", "{{LATEST_STORIES}}", "explained-v1"):
    if marker not in explained_template:
        raise SystemExit(f"Explained template marker is missing: {marker}")

# Ensure protected generated pages contain no unresolved template placeholders.
for rel in ("videos/index.html", "case-status/index.html", "courtrooms/index.html"):
    text = (ROOT / rel).read_text(encoding="utf-8")
    unresolved = re.findall(r"\{\{[A-Z0-9_]+\}\}", text)
    if unresolved:
        raise SystemExit(f"Unresolved template placeholders remain in {rel}: {unresolved[:5]}")

# Courtroom builder compatibility: the page_shell already supplies courtrooms.css
# via PAGE_STYLE_MAP, so build_vc.py must not use an obsolete extra_head argument.
build_vc = (ROOT / "scripts/build_vc.py").read_text(encoding="utf-8")
if "extra_head=" in build_vc:
    raise SystemExit("scripts/build_vc.py still uses obsolete page_shell(extra_head=...) compatibility")
if '"templates" / "courtrooms.html"' not in build_vc:
    raise SystemExit("Courtrooms builder is not template-backed")

# Law & Policy remains a template-backed approved category.
law_policy = (ROOT / "category/law-policy/index.html").read_text(encoding="utf-8")
if "/assets/pages/law-policy.css" not in law_policy or "<main class=\"lawpolicy-v2\"" not in law_policy:
    raise SystemExit("Law & Policy approved template/design is not present")

# Editorial data / sitemap consistency.
try:
    articles = json.loads((ROOT / "data/articles.json").read_text(encoding="utf-8"))
except Exception as exc:
    raise SystemExit(f"Unable to read data/articles.json: {exc}")
if not isinstance(articles, list):
    raise SystemExit("data/articles.json must contain a JSON array")

if any(isinstance(a, dict) and a.get("published") for a in articles):
    news_xml = (ROOT / "news-sitemap.xml").read_text(encoding="utf-8")
    recent_titles = [str(a.get("title", "")) for a in articles if isinstance(a, dict) and a.get("title")]
    if not recent_titles or not any(title in news_xml for title in recent_titles):
        raise SystemExit("news-sitemap.xml does not contain any current article titles")

source_keys = []
for item in articles:
    if isinstance(item, dict) and item.get("source_url"):
        source_keys.append(str(item["source_url"]).split("#")[0].split("?")[0].rstrip("/").lower())
if len(source_keys) != len(set(source_keys)):
    raise SystemExit("Duplicate article source URLs remain after editorial dedupe")

article_rows = [a for a in articles if isinstance(a, dict)]
article_urls = [a.get("url") for a in article_rows]
if len(article_urls) != len(set(article_urls)):
    raise SystemExit("Duplicate article URLs remain after editorial dedupe")

locs = re.findall(r"<loc>(.*?)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
if len(locs) != len(set(locs)):
    raise SystemExit("Duplicate URLs remain in sitemap.xml")
news_locs = re.findall(r"<loc>(.*?)</loc>", (ROOT / "news-sitemap.xml").read_text(encoding="utf-8"))
if len(news_locs) != len(set(news_locs)):
    raise SystemExit("Duplicate URLs remain in news-sitemap.xml")

# Phase 2 article SEO / Google News readiness checks.
article_files = sorted((ROOT / "article").glob("*.html"))
if article_files:
    sample = article_files[0].read_text(encoding="utf-8")
    for marker in (
        "/assets/pages/article.css",
        '"@type": "NewsArticle"',
        '"datePublished"',
        '"dateModified"',
        '"@type": "BreadcrumbList"',
        "Published:",
        "Lex Talk Legal Editorial Desk",
    ):
        if marker not in sample:
            raise SystemExit(f"Phase 2 article SEO marker missing: {marker}")

long_headlines = [
    str(a.get("title", ""))
    for a in article_rows
    if len(str(a.get("title", ""))) > 110
]
if long_headlines:
    print(
        f"Warning: {len(long_headlines)} current article headline(s) exceed Google News' "
        "110-character best-practice threshold; review them in Blogger."
    )

redirects = (ROOT / "_redirects").read_text(encoding="utf-8")
for old_url, new_url in (
    (
        "/article/blog00111.html",
        "/article/delhi-high-court-slaps-1-lakh-costs-on-advocate-for-attending-hearing-from-a-moving-car.html",
    ),
    (
        "/article/india-bloc-meet-on-gyanesh-kumar-election-commission-row-sir-controversy-explained.html",
        "/article/india-block-meet-on-gyanesh-kumar-election-commission-row-sir-controversy-explained.html",
    ),
):
    if f"{old_url} {new_url} 301" not in redirects:
        raise SystemExit(f"Legacy article redirect missing: {old_url}")

print("Lex Talk Legal SEO + PIB smoke test passed.")
print("Page-design ownership contracts: PASS")

# Sponsored campaign safeguards: the active Pass The Bar promotion must be
# traceable, clearly labelled, and present only on approved relevant surfaces.
campaign_path = ROOT / "data/partner_campaigns.json"
if not campaign_path.exists():
    raise SystemExit("Sponsored campaign configuration is missing")
try:
    campaign_data = json.loads(campaign_path.read_text(encoding="utf-8"))
except Exception as exc:
    raise SystemExit(f"Sponsored campaign configuration is invalid: {exc}")
ptb = campaign_data.get("pass-the-bar-aibe100", {})
if not isinstance(ptb, dict) or not ptb.get("active"):
    raise SystemExit("Pass The Bar campaign is not marked active")
if str(ptb.get("promo_code")) != "AIBE100" or str(ptb.get("offer")) != "Save ₹100":
    raise SystemExit("Pass The Bar offer/code configuration is incorrect")

for rel in ("index.html", "category/legal-careers/index.html"):
    page_text = (ROOT / rel).read_text(encoding="utf-8")
    for marker in ("SPONSORED PROMOTION", "AIBE100", "Save ₹100", 'rel="sponsored noopener noreferrer"'):
        if marker not in page_text:
            raise SystemExit(f"Sponsored campaign marker missing from {rel}: {marker}")

landing = ROOT / "aibe-preparation/index.html"
if not landing.exists():
    raise SystemExit("AIBE sponsored landing page is missing")
landing_text = landing.read_text(encoding="utf-8")
for marker in (
    'noindex,follow,max-image-preview:large',
    '/assets/pages/aibe-preparation.css',
    "AIBE100",
    "Save ₹100",
    "SPONSORED PARTNER",
    'rel="sponsored noopener noreferrer"',
):
    if marker not in landing_text:
        raise SystemExit(f"AIBE landing page marker missing: {marker}")
if "ca-pub-3161673810996421" in landing_text:
    raise SystemExit("AIBE sponsored landing must not add AdSense code")

# A paid external campaign CTA should use Google's sponsored link qualification.
article_css = (ROOT / "assets/pages/article.css").read_text(encoding="utf-8")
if ".ltl-sponsored-article-aibe" not in article_css:
    raise SystemExit("Article sponsor placement CSS is missing")

print("Sponsored campaign safeguards: PASS")

adv = (ROOT / "advertise.html").read_text(encoding="utf-8")
if "/assets/pages/advertise.css" not in adv:
    raise SystemExit("Advertise page CSS is missing")
for marker in ("Monthly Sponsorship", "Campaign Partnership", "Request the current media kit", "Advertising Desk"):
    if marker not in adv:
        raise SystemExit(f"Advertise media-kit marker missing: {marker}")

js_text = (ROOT / "assets/site.js").read_text(encoding="utf-8")
for marker in ("hydrateBuildTimestamp", "sponsor_click", "youtube_click", "external_link_click"):
    if marker not in js_text:
        raise SystemExit(f"GA/timestamp runtime marker missing: {marker}")

if article_rows:
    import importlib.util as _importlib_util
    _spec = _importlib_util.spec_from_file_location("lex_build_site", BUILD)
    _mod = _importlib_util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    _category_matches = _mod.category_matches
    for _key in ("courts", "law-policy", "banking-law", "drt-drat", "legal-careers"):
        _matches=[a for a in article_rows if _category_matches(a,_key)]
        if _matches:
            _page=(ROOT/"category"/_key/"index.html").read_text(encoding="utf-8")
            if not any(str(a.get("title","")) in _page for a in _matches[:3]):
                raise SystemExit(f"Category mapping failed to surface current {_key} article")
