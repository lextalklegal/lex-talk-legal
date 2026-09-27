from pathlib import Path
import os,re,json,html as H,urllib.request,xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]; CSS=(ROOT/"assets/site.css").read_text(encoding="utf8"); JS=(ROOT/"assets/site.js").read_text(encoding="utf8"); LOGO="data:image/png;base64,"+__import__("base64").b64encode((ROOT/"assets/LexTalkLegal_Logo-wo-bg.png").read_bytes()).decode(); BLOGGER=os.getenv("BLOGGER_URL","https://lextalklegal.blogspot.com").rstrip("/"); HANDLE=os.getenv("YOUTUBE_HANDLE","@lextalklegal"); NS={"a":"http://www.w3.org/2005/Atom","yt":"http://www.youtube.com/xml/schemas/2015"}
def fetch(u):
 r=urllib.request.Request(u,headers={"User-Agent":"LexTalkLegalBot/1.0"}); return urllib.request.urlopen(r,timeout=30).read()
def slug(s): return re.sub(r"-+","-",re.sub(r"[^a-zA-Z0-9\s-]","",s).strip().lower().replace(" ","-"))[:90] or "article"
def clean(raw):
 s=BeautifulSoup(raw or "","html.parser")
 for x in s(["script","style","iframe","form","object","embed"]):x.decompose()
 for a in s.find_all("a",href=True): a["target"]="_blank";a["rel"]="noopener"
 return str(s)
def blogger():
 try: root=ET.fromstring(fetch(f"{BLOGGER}/feeds/posts/default?alt=atom&max-results=30"))
 except Exception as e: print("Blogger:",e); return []
 out=[]
 for e in root.findall("a:entry",NS):
  title=e.findtext("a:title",default="",namespaces=NS).strip(); link=""
  for l in e.findall("a:link",NS):
   if l.attrib.get("rel")=="alternate":link=l.attrib.get("href","")
  pub=e.findtext("a:published",default="",namespaces=NS) or e.findtext("a:updated",default="",namespaces=NS); c=e.find("a:content",NS); raw=c.text if c is not None else ""; soup=BeautifulSoup(raw or "","html.parser"); img=soup.find("img"); labels=[x.attrib.get("term","") for x in e.findall("a:category",NS) if x.attrib.get("term")]; text=" ".join(soup.stripped_strings); out.append({"title":title,"url":"/article/"+slug(title)+".html","source_url":link,"published":pub,"labels":labels,"category":labels[0] if labels else "Legal News","image":img.get("src") if img else "","excerpt":text[:210]+("…" if len(text)>210 else ""),"content":clean(raw)})
 return out
def youtube():
 try:
  p=fetch("https://www.youtube.com/"+HANDLE+"/videos").decode("utf8","ignore"); m=re.search(r'<meta itemprop="channelId" content="(UC[^"]+)"',p) or re.search(r'"channelId":"(UC[^"]+)"',p)
  if not m: raise RuntimeError("channel id not found")
  root=ET.fromstring(fetch("https://www.youtube.com/feeds/videos.xml?channel_id="+m.group(1))); out=[]
  for e in root.findall("a:entry",NS):
   title=e.findtext("a:title",default="",namespaces=NS); link=e.find("a:link",NS).attrib.get("href",""); pub=e.findtext("a:published",default="",namespaces=NS); vid=e.findtext("yt:videoId",default="",namespaces=NS); out.append({"title":title,"url":link,"published":pub,"thumbnail":"https://i.ytimg.com/vi/"+vid+"/hqdefault.jpg"})
  return out
 except Exception as e:
  print("YouTube:",e)
  try:return json.loads((ROOT/"data/youtube.json").read_text())
  except:return []
def article(a):
 nav=[("Latest","/"),("Courts","/category/courts/"),("Law & Policy","/category/law-policy/"),("Banking Law","/category/banking-law/"),("DRT / DRAT","/category/drt-drat/"),("Legal Careers","/category/legal-careers/"),("DRA","/category/dra/"),("Explained","/category/explained/"),("Courtrooms","/courtrooms/"),("Case Status","/case-status/"),("Videos","/videos/")]; n="".join(f'<a href="{u}">{x}</a>' for x,u in nav); im=f'<img class="article-hero" src="{H.escape(a["image"],quote=True)}" alt="">' if a["image"] else ""; body=f'<main class="article-wrap"><div class="meta">{H.escape(a["category"])} · {H.escape(a["published"][:10])}</div><h1>{H.escape(a["title"])}</h1><div class="article-meta">Lex Talk Legal · <a href="{H.escape(a["source_url"],quote=True)}" target="_blank">Original Blogger post</a></div>{im}<div class="article-body">{a["content"]}</div><div class="notice">For educational and informational use. Verify important legal facts, orders and case status from the concerned official source.</div></main>'; return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{H.escape(a["excerpt"],quote=True)}"><title>{H.escape(a["title"])} | Lex Talk Legal</title><script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3161673810996421" crossorigin="anonymous"></script><style>{CSS}</style></head><body><div class="top"></div><header class="masthead"><a href="/"><img src="{LOGO}" alt="Lex Talk Legal"></a></header><nav class="nav"><div class="wrap">{n}</div></nav>{body}<footer><div class="copy">© 2026 LEXBOTICS AI MEDIA LLP | Lex Talk Legal</div></footer><script>{JS}</script></body></html>'
def main():
 ap=ROOT/"data/articles.json"; arts=blogger()
 if not arts:
  try: arts=json.loads(ap.read_text())
  except: arts=[]
 ap.write_text(json.dumps(arts,ensure_ascii=False,indent=2),encoding="utf8"); (ROOT/"data/youtube.json").write_text(json.dumps(youtube(),ensure_ascii=False,indent=2),encoding="utf8")
 d=ROOT/"article";d.mkdir(exist_ok=True)
 for f in d.glob("*.html"):f.unlink()
 for a in arts:(d/(slug(a["title"])+".html")).write_text(article(a),encoding="utf8")
 urls=["/","/courtrooms/","/case-status/","/videos/"]+[a["url"] for a in arts]; (ROOT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join("<url><loc>https://lextalk.legal"+u+"</loc></url>" for u in urls)+"</urlset>",encoding="utf8")
if __name__=="__main__":main()
