from pathlib import Path
import os, re, json, html as H, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "assets/site.css").read_text(encoding="utf8")
JS = (ROOT / "assets/site.js").read_text(encoding="utf8")
LOGO = "data:image/png;base64," + __import__("base64").b64encode((ROOT / "assets/LexTalkLegal_Logo-wo-bg.png").read_bytes()).decode()
BLOGGER = os.getenv("BLOGGER_URL", "https://lextalklegal.blogspot.com").rstrip("/")
HANDLE = os.getenv("YOUTUBE_HANDLE", "@lextalklegal")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "").strip()
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}

NAV = [
    ("Latest", "/"), ("Courts", "/category/courts/"), ("Law & Policy", "/category/law-policy/"),
    ("Banking Law", "/category/banking-law/"), ("DRT / DRAT", "/category/drt-drat/"),
    ("Legal Careers", "/category/legal-careers/"), ("DRA", "/category/dra/"),
    ("Explained", "/category/explained/"), ("Courtrooms", "/courtrooms/"),
    ("Case Status", "/case-status/"), ("Videos", "/videos/")
]

CATEGORY_MAP = {
    "courts": ("Courts", {"supreme court", "high court", "courts", "judiciary", "case laws", "case law"}),
    "law-policy": ("Law & Policy", {"law & policy", "law and policy", "law policy", "policy", "legislation"}),
    "banking-law": ("Banking Law", {"banking law", "banking", "sarfaesi", "ibc", "insolvency", "recovery"}),
    "drt-drat": ("DRT / DRAT", {"drt", "drat", "drt / drat", "sarfaesi"}),
    "legal-careers": ("Legal Careers", {"legal careers", "aibe", "bar council", "cop", "judiciary careers", "judiciary"}),
    "dra": ("DRA", {"dra", "debt recovery agent", "debt recovery agents"}),
    "explained": ("Explained", {"legal explained", "explained", "case laws explained", "legal explainers"}),
}

ARTICLE_CSS = r"""
.article-wrap{max-width:920px;margin:32px auto;padding:38px 20px 60px}
.article-wrap h1{font-size:48px;line-height:1.08;margin:9px 0}
.article-meta{font:12px Arial;color:var(--muted);margin-bottom:24px}
.article-hero{width:100%;max-height:500px;object-fit:cover;margin-bottom:25px}
.article-body{font-size:19px;line-height:1.72}
.article-body img{max-width:100%;height:auto}
.article-body a{color:var(--red);text-decoration:underline}
@media(max-width:560px){.article-wrap{padding:25px 16px 45px}.article-wrap h1{font-size:32px}.article-body{font-size:17px}}
"""


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "LexTalkLegalBot/1.0"})
    return urllib.request.urlopen(req, timeout=30).read()


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-zA-Z0-9\s-]", "", s).strip().lower().replace(" ", "-"))[:90] or "article"


def clean(raw):
    soup = BeautifulSoup(raw or "", "html.parser")
    for x in soup(["script", "style", "iframe", "form", "object", "embed"]):
        x.decompose()
    for a in soup.find_all("a", href=True):
        a["target"] = "_blank"
        a["rel"] = "noopener"
    return str(soup)


def blogger():
    try:
        root = ET.fromstring(fetch(f"{BLOGGER}/feeds/posts/default?alt=atom&max-results=50"))
    except Exception as e:
        print("Blogger:", e)
        return []
    out = []
    for e in root.findall("a:entry", NS):
        title = e.findtext("a:title", default="", namespaces=NS).strip()
        link = ""
        for l in e.findall("a:link", NS):
            if l.attrib.get("rel") == "alternate":
                link = l.attrib.get("href", "")
        pub = e.findtext("a:published", default="", namespaces=NS) or e.findtext("a:updated", default="", namespaces=NS)
        c = e.find("a:content", NS)
        raw = c.text if c is not None else ""
        soup = BeautifulSoup(raw or "", "html.parser")
        img = soup.find("img")
        labels = [x.attrib.get("term", "") for x in e.findall("a:category", NS) if x.attrib.get("term")]
        text = " ".join(soup.stripped_strings)
        out.append({
            "title": title, "url": "/article/" + slug(title) + ".html", "source_url": link,
            "published": pub, "labels": labels, "category": labels[0] if labels else "Legal News",
            "image": img.get("src") if img else "", "excerpt": text[:210] + ("…" if len(text) > 210 else ""),
            "content": clean(raw)
        })
    return out


def youtube():
    channel_id = CHANNEL_ID
    try:
        if not channel_id:
            p = fetch("https://www.youtube.com/" + HANDLE + "/videos").decode("utf8", "ignore")
            m = re.search(r'<meta itemprop="channelId" content="(UC[^"]+)"', p) or re.search(r'"channelId":"(UC[^"]+)"', p) or re.search(r'"externalId":"(UC[^"]+)"', p)
            if not m:
                raise RuntimeError("YouTube channel ID not found")
            channel_id = m.group(1)
        root = ET.fromstring(fetch("https://www.youtube.com/feeds/videos.xml?channel_id=" + channel_id))
        out = []
        for e in root.findall("a:entry", NS):
            title = e.findtext("a:title", default="", namespaces=NS)
            link_el = e.find("a:link", NS)
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            pub = e.findtext("a:published", default="", namespaces=NS)
            vid = e.findtext("yt:videoId", default="", namespaces=NS)
            out.append({"title": title, "url": link, "published": pub, "video_id": vid,
                        "thumbnail": "https://i.ytimg.com/vi/" + vid + "/hqdefault.jpg" if vid else ""})
        return out
    except Exception as e:
        print("YouTube:", e)
        try:
            return json.loads((ROOT / "data/youtube.json").read_text(encoding="utf8"))
        except Exception:
            return []


def nav_html():
    return "".join(f'<a href="{u}">{H.escape(x)}</a>' for x, u in NAV)


def article(a):
    im = f'<img class="article-hero" src="{H.escape(a["image"], quote=True)}" alt="">' if a["image"] else ""
    body = f'''<main class="article-wrap">
<div class="meta">{H.escape(a["category"])} · {H.escape(a["published"][:10])}</div>
<h1>{H.escape(a["title"])}</h1>
<div class="article-meta">Lex Talk Legal · <a href="{H.escape(a["source_url"], quote=True)}" target="_blank" rel="noopener">Original Blogger post</a></div>
{im}<div class="article-body">{a["content"]}</div>
<div class="notice">For educational and informational use. Verify important legal facts, orders and case status from the concerned official source.</div>
</main>'''
    return page_shell((a["title"], a["url"]), a["excerpt"], body)


def page_shell(title, description, content):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{H.escape(description, quote=True)}"><link rel="canonical" href="https://lextalk.legal{title[1] if isinstance(title,tuple) else ''}">
<title>{H.escape(title[0] if isinstance(title,tuple) else title)} | Lex Talk Legal</title>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3161673810996421" crossorigin="anonymous"></script>
<style>{CSS}{ARTICLE_CSS}</style></head><body><div class="top"></div>
<div class="utility"><div class="wrap"><div class="live-info"><span class="dot">●</span><span id="dateLabel">--</span><span>|</span><span id="timeLabel">--:--:-- IST</span><span>|</span><span>New Delhi, India</span></div><div class="controls"><button class="control" id="langBtn">हिन्दी</button><button class="control" id="themeBtn">☾ Dark</button></div></div></div>
<header class="masthead"><a href="/"><img src="{LOGO}" alt="Lex Talk Legal"></a></header>
<nav class="nav"><div class="wrap">{nav_html()}</div></nav>{content}
<footer><div class="copy">© 2026 LEXBOTICS AI MEDIA LLP | Lex Talk Legal | For Educational & Informational Use Only</div></footer>
<div id="google_translate_element" aria-hidden="true"></div>
<script>{JS}</script>
<script>function googleTranslateElementInit(){{new google.translate.TranslateElement({{pageLanguage:'en',includedLanguages:'en,hi',autoDisplay:false}},'google_translate_element');window.lexGoogleTranslateReady=true;if(window.lexApplyLanguage)window.lexApplyLanguage();}}</script>
<script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
</body></html>'''


def article_card(a):
    image = f'<div class="cardimg"><img src="{H.escape(a["image"], quote=True)}" alt="" loading="lazy"></div>' if a.get("image") else '<div class="thumb">LEGAL NEWS</div>'
    return f'<article class="card">{image}<div class="meta">{H.escape(a["category"])} · {H.escape(a["published"][:10])}</div><h3><a href="{a["url"]}">{H.escape(a["title"])}</a></h3><p>{H.escape(a["excerpt"])}</p></article>'


def video_card(v):
    thumb = H.escape(v.get("thumbnail", ""), quote=True)
    title = H.escape(v.get("title", "Lex Talk Legal"))
    date = H.escape(v.get("published", "")[:10])
    url = H.escape(v.get("url", "https://www.youtube.com/@lextalklegal"), quote=True)
    return f'''<article class="yt-card"><a href="{url}" target="_blank" rel="noopener"><div class="video-thumb">{('<img src="'+thumb+'" alt="" loading="lazy">') if thumb else '<div class="yt-mark">▶</div>'}<span class="play">▶</span></div></a><div class="meta">{date}</div><h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3><a class="button redbtn" href="{url}" target="_blank" rel="noopener">Watch on YouTube</a></article>'''


def category_matches(a, key):
    labels = {str(x).strip().lower() for x in a.get("labels", [])}
    title = a.get("title", "").lower()
    name, terms = CATEGORY_MAP[key]
    if labels & terms:
        return True
    return any(t in title for t in terms)


def write_category_pages(arts):
    for key, (name, _) in CATEGORY_MAP.items():
        items = [a for a in arts if category_matches(a, key)]
        cards = "".join(article_card(a) for a in items[:30])
        if not cards:
            cards = '<div class="empty">No stories published in this section yet. Publish a Blogger post with the appropriate label and the next automated sync will update this page.</div>'
        content = f'<main class="utility-page"><h1>{H.escape(name)}</h1><p class="lead">Latest Lex Talk Legal stories in this section are synced automatically from Blogger.</p><div class="grid">{cards}</div></main>'
        p = ROOT / "category" / key / "index.html"; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(page_shell((name, f"/category/{key}/"), f"Lex Talk Legal — {name} news, updates and explainers.", content), encoding="utf8")


def write_videos_page(videos):
    cards = "".join(video_card(v) for v in videos[:30]) or '<div class="empty">No YouTube videos were returned in the latest sync.</div>'
    content = f'<main class="utility-page"><h1>LATEST VIDEOS</h1><p class="lead">Latest Lex Talk Legal videos are synced automatically from YouTube.</p><div class="yt-grid">{cards}</div></main>'
    (ROOT / "videos").mkdir(exist_ok=True)
    (ROOT / "videos/index.html").write_text(page_shell(("Latest Videos", "/videos/"), "Latest Lex Talk Legal videos, legal news and explainers.", content), encoding="utf8")


def patch_shared_assets():
    # Refresh shared CSS/JS and the Google Translate widget on existing HTML pages.
    translate_block = '''<div id="google_translate_element" aria-hidden="true"></div>
<script>function googleTranslateElementInit(){{new google.translate.TranslateElement({{pageLanguage:'en',includedLanguages:'en,hi',autoDisplay:false}},'google_translate_element');window.lexGoogleTranslateReady=true;if(window.lexApplyLanguage)window.lexApplyLanguage();}}</script>
<script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>'''
    for p in ROOT.rglob("*.html"):
        if "/.git/" in str(p):
            continue
        try:
            txt=p.read_text(encoding="utf8")
        except Exception:
            continue
        if 'data-embedded="lex-talk-legal"' in txt:
            txt=re.sub(r'<style data-embedded="lex-talk-legal">.*?</style>', '<style data-embedded="lex-talk-legal">'+CSS+'</style>', txt, count=1, flags=re.S)
            txt=re.sub(r'<script data-embedded="lex-talk-legal">.*?</script>', '<script data-embedded="lex-talk-legal">'+JS+'</script>', txt, count=1, flags=re.S)
        if 'id="google_translate_element"' not in txt and '</body>' in txt:
            txt=txt.replace('</body>', translate_block+'\n</body>', 1)
        p.write_text(txt,encoding="utf8")


def update_homepage(arts, videos):
    p = ROOT / "index.html"
    if not p.exists():
        return
    s = BeautifulSoup(p.read_text(encoding="utf8"), "html.parser")
    lg = s.find(id="latestGrid")
    if lg:
        lg.clear()
        latest = arts[:8]
        if latest:
            for a in latest:
                frag = BeautifulSoup(article_card(a), "html.parser")
                lg.append(frag)
        else:
            lg.append(BeautifulSoup('<div class="empty">No Blogger stories returned in the latest sync.</div>', "html.parser"))
    vg = s.find(id="videoGrid")
    if vg:
        vg.clear()
        latest_videos = videos[:6]
        if latest_videos:
            for v in latest_videos:
                vg.append(BeautifulSoup(video_card(v), "html.parser"))
        else:
            vg.append(BeautifulSoup('<div class="empty">No YouTube videos returned in the latest sync.</div>', "html.parser"))
    # Keep public channel links aligned to the current handle.
    for a in s.find_all("a", href=True):
        if "youtube.com/@" in a["href"]:
            a["href"] = "https://www.youtube.com/@lextalklegal"
    p.write_text(str(s), encoding="utf8")


def main():
    ap = ROOT / "data/articles.json"
    arts = blogger()
    if not arts:
        try: arts = json.loads(ap.read_text(encoding="utf8"))
        except Exception: arts = []
    arts.sort(key=lambda x: x.get("published", ""), reverse=True)
    ap.parent.mkdir(exist_ok=True)
    ap.write_text(json.dumps(arts, ensure_ascii=False, indent=2), encoding="utf8")

    videos = youtube()
    videos.sort(key=lambda x: x.get("published", ""), reverse=True)
    (ROOT / "data/youtube.json").write_text(json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf8")

    d = ROOT / "article"; d.mkdir(exist_ok=True)
    for f in d.glob("*.html"): f.unlink()
    for a in arts:
        (d / (slug(a["title"]) + ".html")).write_text(article(a), encoding="utf8")

    write_category_pages(arts)
    write_videos_page(videos)
    update_homepage(arts, videos)
    patch_shared_assets()

    urls = ["/", "/courtrooms/", "/case-status/", "/videos/"]
    urls += [f"/category/{k}/" for k in CATEGORY_MAP]
    urls += [a["url"] for a in arts]
    now = datetime.now(timezone.utc).date().isoformat()
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += "".join(f"<url><loc>https://lextalk.legal{u}</loc><lastmod>{now}</lastmod></url>" for u in dict.fromkeys(urls))
    xml += "</urlset>"
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf8")

    # Cloudflare Workers Static Assets: explicitly proxy folder URLs to their
    # index.html files. This keeps /courtrooms/ and /case-status/ working
    # even if the asset router does not resolve nested index files as expected.
    (ROOT / "_redirects").write_text(
        "/courtrooms /courtrooms/ 301\n"
        "/case-status /case-status/ 301\n"
        "/courtrooms/ /courtrooms/index.html 200\n"
        "/case-status/ /case-status/index.html 200\n",
        encoding="utf8"
    )

    print(f"Synced {len(arts)} Blogger articles and {len(videos)} YouTube videos.")

if __name__ == "__main__":
    main()
