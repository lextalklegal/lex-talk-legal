from pathlib import Path
import os,re,json,html as H,urllib.request,xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/"assets/site.css").read_text(encoding="utf8")
JS=(ROOT/"assets/site.js").read_text(encoding="utf8")
LOGO="data:image/png;base64,"+__import__("base64").b64encode((ROOT/"assets/LexTalkLegal_Logo-wo-bg.png").read_bytes()).decode()
BLOGGER=os.getenv("BLOGGER_URL","https://lextalklegal.blogspot.com").rstrip("/")
HANDLE=os.getenv("YOUTUBE_HANDLE","@lextalklegal")
NS={"a":"http://www.w3.org/2005/Atom","yt":"http://www.youtube.com/xml/schemas/2015"}

ARTICLE_CSS=r"""
body{margin:0;background:#f5f7fb;color:#111827;font-family:Arial,Helvetica,sans-serif;line-height:1.7}
.article-site-header{background:#fff;border-bottom:1px solid #dbe2ea}
.article-header-inner{max-width:1180px;margin:0 auto;padding:12px 24px;display:flex;align-items:center;justify-content:center}
.article-logo{display:block;width:auto;max-width:280px;height:auto;max-height:78px;object-fit:contain}
.article-nav{background:#111;color:#fff;border-bottom:3px solid #d4a72c}
.article-nav-inner{max-width:1180px;margin:0 auto;padding:10px 18px;display:flex;gap:18px;flex-wrap:wrap}
.article-nav a{color:#fff;text-decoration:none;font-size:13px;font-weight:700}
.article-nav a:hover{color:#d4a72c}
.article-wrap{width:min(900px,92%);margin:35px auto 60px;background:#fff;padding:35px 45px;border:1px solid #e1e6ed;box-shadow:0 8px 25px rgba(15,23,42,.07)}
.article-wrap .meta{font-size:13px;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.article-wrap h1{font-size:42px;line-height:1.18;margin:10px 0 12px;color:#111827}
.article-meta{font-size:13px;color:#64748b;margin-bottom:22px}
.article-meta a{color:#0b3b78}
.article-hero{display:block;width:100%;max-height:520px;object-fit:cover;border-radius:8px;margin:0 0 28px}
.article-body{font-size:18px;line-height:1.8}
.article-body img{max-width:100%;height:auto}
.article-body h2,.article-body h3{line-height:1.3;margin-top:30px}
.article-body p{margin:0 0 18px}
.notice{margin-top:35px;padding:15px 18px;background:#f1f5f9;border-left:4px solid #d4a72c;font-size:14px;color:#475569}
.article-footer{background:#0b1220;color:#dbe4f0;padding:30px 20px;text-align:center;font-size:13px}
@media(max-width:700px){
  .article-header-inner{padding:10px 15px}
  .article-logo{max-width:230px;max-height:68px}
  .article-nav-inner{gap:10px;padding:9px 12px}
  .article-wrap{padding:24px 18px;margin-top:20px}
  .article-wrap h1{font-size:30px}
  .article-body{font-size:16px}
}
"""

def fetch(u):
    r=urllib.request.Request(u,headers={"User-Agent":"LexTalkLegalBot/1.0"})
    return urllib.request.urlopen(r,timeout=30).read()

def slug(s):
    return re.sub(r"-+","-",re.sub(r"[^a-zA-Z0-9\s-]","",s).strip().lower().replace(" ","-"))[:90] or "article"

def clean(raw):
    s=BeautifulSoup(raw or "","html.parser")
    for x in s(["script","style","iframe","form","object","embed"]): x.decompose()
    for a in s.find_all("a",href=True):
        a["target"]="_blank"; a["rel"]="noopener"
    return str(s)

def blogger():
    try: root=ET.fromstring(fetch(f"{BLOGGER}/feeds/posts/default?alt=atom&max-results=30"))
    except Exception as e: print("Blogger:",e); return []
    out=[]
    for e in root.findall("a:entry",NS):
        title=e.findtext("a:title",default="",namespaces=NS).strip(); link=""
        for l in e.findall("a:link",NS):
            if l.attrib.get("rel")=="alternate": link=l.attrib.get("href","")
        pub=e.findtext("a:published",default="",namespaces=NS) or e.findtext("a:updated",default="",namespaces=NS)
        c=e.find("a:content",NS); raw=c.text if c is not None else ""
        soup=BeautifulSoup(raw or "","html.parser"); img=soup.find("img")
        labels=[x.attrib.get("term","") for x in e.findall("a:category",NS) if x.attrib.get("term")]
        text=" ".join(soup.stripped_strings)
        out.append({"title":title,"url":"/article/"+slug(title)+".html","source_url":link,"published":pub,
                    "labels":labels,"category":labels[0] if labels else "Legal News","image":img.get("src") if img else "",
                    "excerpt":text[:210]+("…" if len(text)>210 else ""),"content":clean(raw)})
    return out

def youtube():
    try:
        p=fetch("https://www.youtube.com/"+HANDLE+"/videos").decode("utf8","ignore")
        m=re.search(r'<meta itemprop="channelId" content="(UC[^"]+)"',p) or re.search(r'"channelId":"(UC[^"]+)"',p)
        if not m: raise RuntimeError("channel id not found")
        root=ET.fromstring(fetch("https://www.youtube.com/feeds/videos.xml?channel_id="+m.group(1))); out=[]
        for e in root.findall("a:entry",NS):
            title=e.findtext("a:title",default="",namespaces=NS); link=e.find("a:link",NS).attrib.get("href","")
            pub=e.findtext("a:published",default="",namespaces=NS); vid=e.findtext("yt:videoId",default="",namespaces=NS)
            out.append({"title":title,"url":link,"published":pub,"thumbnail":"https://i.ytimg.com/vi/"+vid+"/hqdefault.jpg"})
        return out
    except Exception as e:
        print("YouTube:",e)
        try: return json.loads((ROOT/"data/youtube.json").read_text())
        except: return []

def article(a):
    nav=[("Latest","/"),("Courts","/category/courts/"),("Law & Policy","/category/law-policy/"),
         ("Banking Law","/category/banking-law/"),("DRT / DRAT","/category/drt-drat/"),
         ("Legal Careers","/category/legal-careers/"),("DRA","/category/dra/"),
         ("Explained","/category/explained/"),("Courtrooms","/courtrooms/"),
         ("Case Status","/case-status/"),("Videos","/videos/")]
    n="".join(f'<a href="{u}">{x}</a>' for x,u in nav)
    im=f'<img class="article-hero" src="{H.escape(a["image"],quote=True)}" alt="">' if a["image"] else ""
    body=f"""<main class="article-wrap">
<div class="meta">{H.escape(a["category"])} · {H.escape(a["published"][:10])}</div>
<h1>{H.escape(a["title"])}</h1>
<div class="article-meta">Lex Talk Legal · <a href="{H.escape(a["source_url"],quote=True)}" target="_blank" rel="noopener">Original Blogger post</a></div>
{im}
<div class="article-body">{a["content"]}</div>
<div class="notice">For educational and informational use. Verify important legal facts, orders and case status from the concerned official source.</div>
</main>"""
    return f"""<!doctype html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{H.escape(a["excerpt"],quote=True)}">
<title>{H.escape(a["title"])} | Lex Talk Legal</title>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3161673810996421" crossorigin="anonymous"></script>
<style>{CSS}{ARTICLE_CSS}</style></head><body>
<header class="article-site-header"><div class="article-header-inner">
<a href="/" aria-label="Lex Talk Legal Home"><img class="article-logo" src="{LOGO}" alt="Lex Talk Legal"></a>
</div></header>
<nav class="article-nav"><div class="article-nav-inner">{n}</div></nav>
{body}
<footer class="article-footer">© 2026 LEXBOTICS AI MEDIA LLP | Lex Talk Legal | For Educational & Informational Use Only</footer>
<script>{JS}</script></body></html>"""

def main():
    ap=ROOT/"data/articles.json"; arts=blogger()
    if not arts:
        try: arts=json.loads(ap.read_text())
        except: arts=[]
    ap.write_text(json.dumps(arts,ensure_ascii=False,indent=2),encoding="utf8")
    (ROOT/"data/youtube.json").write_text(json.dumps(youtube(),ensure_ascii=False,indent=2),encoding="utf8")
    d=ROOT/"article"; d.mkdir(exist_ok=True)
    for f in d.glob("*.html"): f.unlink()
    for a in arts: (d/(slug(a["title"])+".html")).write_text(article(a),encoding="utf8")
    urls=["/","/courtrooms/","/case-status/","/videos/"]+[a["url"] for a in arts]
    (ROOT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        +"".join("<url><loc>https://lextalk.legal"+u+"</loc></url>" for u in urls)+"</urlset>",encoding="utf8")

if __name__=="__main__": main()
