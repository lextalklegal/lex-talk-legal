#!/usr/bin/env python3
"""Read-only audit of public HTML SEO basics, structured data, and internal links."""
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE_HOST = "lextalk.legal"
EXCLUDED = {"templates", "content", "obsolete", "admin", "docs", "functions", "src", "scripts", ".github"}
DYNAMIC_PATHS = {"/creator-studio/grap", "/api/private/grap-script"}
REDIRECTS = set()
redirect_file = ROOT / "_redirects"
if redirect_file.exists():
    for line in redirect_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            REDIRECTS.add(line.split()[0])

def public_html_files():
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED for part in rel.parts):
            continue
        yield path

def resolve_local_path(url_path):
    path = unquote(url_path or "/").split("?", 1)[0]
    if not path.startswith("/"):
        path = "/" + path
    if path in REDIRECTS or path in DYNAMIC_PATHS:
        return True
    candidates = []
    if path == "/":
        candidates.append(ROOT / "index.html")
    else:
        candidates.append(ROOT / path.lstrip("/"))
        if path.endswith("/"):
            candidates.append(ROOT / path.lstrip("/") / "index.html")
            candidates.append(ROOT / (path.lstrip("/")[:-1] + ".html"))
        else:
            candidates.append(ROOT / (path.lstrip("/") + "/index.html"))
            if not Path(path).suffix:
                candidates.append(ROOT / (path.lstrip("/") + ".html"))
    return any(p.is_file() for p in candidates)

def main():
    pages = list(public_html_files())
    title_counts = Counter()
    canonical_map = defaultdict(list)
    warnings = []
    invalid_jsonld = []
    missing = Counter()
    image_alt_missing = 0
    link_count = 0
    broken_links = []
    sitemap_locs = set()
    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists():
        sitemap_locs = set(re.findall(r"<loc>(.*?)</loc>", sitemap.read_text(encoding="utf-8")))
    noindex_canonicals = set()

    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        raw = page.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(raw, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        desc_tag = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
        desc = (desc_tag.get("content") or "").strip() if desc_tag else ""
        canonical_tag = soup.find("link", rel=lambda v: v and "canonical" in v)
        canonical = (canonical_tag.get("href") or "").strip() if canonical_tag else ""
        h1_count = len(soup.find_all("h1"))
        if not title: missing["title"] += 1; warnings.append(f"{rel}: missing title")
        else: title_counts[title] += 1
        if not desc: missing["description"] += 1; warnings.append(f"{rel}: missing meta description")
        if not canonical: missing["canonical"] += 1; warnings.append(f"{rel}: missing canonical")
        elif SITE_HOST not in urlparse(canonical).netloc:
            warnings.append(f"{rel}: canonical host is not {SITE_HOST}: {canonical}")
        else:
            canonical_map[canonical].append(rel)
        if h1_count != 1:
            warnings.append(f"{rel}: expected one H1, found {h1_count}")
        robots = soup.find("meta", attrs={"name": re.compile("^robots$", re.I)})
        if robots and "noindex" in (robots.get("content") or "").lower() and canonical:
            noindex_canonicals.add(canonical)
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                json.loads(script.string or script.get_text())
            except Exception as exc:
                invalid_jsonld.append(f"{rel}: invalid JSON-LD ({exc})")
        for img in soup.find_all("img"):
            if not img.has_attr("alt"):
                image_alt_missing += 1
        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            parsed = urlparse(href)
            if parsed.scheme and parsed.scheme not in ("http", "https"):
                continue
            if parsed.netloc and SITE_HOST not in parsed.netloc:
                continue
            if parsed.netloc and SITE_HOST in parsed.netloc:
                target_path = parsed.path or "/"
            else:
                target_path = parsed.path or "/"
            link_count += 1
            if not resolve_local_path(target_path):
                broken_links.append(f"{rel} -> {href}")

    duplicate_titles = {k:v for k,v in title_counts.items() if v > 1}
    duplicate_canonicals = {k:v for k,v in canonical_map.items() if len(v) > 1}
    sitemap_noindex = sorted(url for url in sitemap_locs if url in noindex_canonicals)
    print("LEX TALK LEGAL — PUBLIC SITE AUDIT")
    print(f"Public HTML files scanned: {len(pages)}")
    print(f"Internal links checked: {link_count}")
    print(f"Images missing alt attributes: {image_alt_missing}")
    print(f"Missing title / description / canonical: {missing['title']} / {missing['description']} / {missing['canonical']}")
    print(f"Duplicate title groups: {len(duplicate_titles)}")
    print(f"Duplicate canonical groups: {len(duplicate_canonicals)}")
    print(f"Invalid JSON-LD blocks: {len(invalid_jsonld)}")
    print(f"Broken internal links: {len(broken_links)}")
    print(f"Noindex pages found in sitemap: {len(sitemap_noindex)}")
    for label, rows in (("WARNINGS", warnings), ("DUPLICATE TITLES", [f"{k} ({len(v)} pages)" for k,v in duplicate_titles.items()]), ("DUPLICATE CANONICALS", [f"{k}: {', '.join(v)}" for k,v in duplicate_canonicals.items()]), ("INVALID JSON-LD", invalid_jsonld), ("BROKEN INTERNAL LINKS", broken_links), ("NOINDEX IN SITEMAP", sitemap_noindex)):
        if rows:
            print(f"\n{label}:")
            for row in rows[:100]:
                print(f" - {row}")
            if len(rows) > 100:
                print(f" ... and {len(rows)-100} more")
    # Audit is intentionally non-blocking while legacy issues are triaged.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
