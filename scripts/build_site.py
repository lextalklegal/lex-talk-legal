from pathlib import Path
import os, re, json, html as H, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'assets/site.css').read_text(encoding='utf8')
JS = (ROOT / 'assets/site.js').read_text(encoding='utf8')
LOGO = '/assets/LexTalkLegal_Logo-wo-bg.png'
BLOGGER = os.getenv('BLOGGER_URL', 'https://lextalklegal.blogspot.com').rstrip('/')
HANDLE = os.getenv('YOUTUBE_HANDLE', '@lextalklegal')
CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID', '').strip()
NS = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}

NAV = [
    ('Latest', '/'), ('Courts', '/category/courts/'), ('Law & Policy', '/category/law-policy/'),
    ('Banking & Recovery', '/category/banking-law/'), ('Auctions', '/auctions/'),
    ('Legal Careers', '/category/legal-careers/'), ('DRA', '/category/dra/'),
    ('Case Help', '/case-help.html'), ('Videos', '/videos/')
]
MORE_NAV = [
    ('DRT / DRAT','/category/drt-drat/'), ('SARFAESI','/category/banking-law/'), ('Bare Acts','https://indiacode.gov.in/'),
    ('Courtrooms / VC','/courtrooms/'), ('Case Status','/case-status/'), ('Our Advocate Team','/team.html'),
    ('About Lex Talk Legal','/about.html')
]

CATEGORY_MAP = {
    'courts': ('Courts', {'supreme court', 'high court', 'courts', 'judiciary', 'case laws', 'case law'}),
    'law-policy': ('Law & Policy', {'law & policy', 'law and policy', 'law policy', 'policy', 'legislation'}),
    'banking-law': ('Banking Law', {'banking law', 'banking', 'sarfaesi', 'ibc', 'insolvency', 'recovery'}),
    'drt-drat': ('DRT / DRAT', {'drt', 'drat', 'drt / drat', 'sarfaesi'}),
    'legal-careers': ('Legal Careers', {'legal careers', 'aibe', 'bar council', 'cop', 'judiciary careers', 'judiciary'}),
    'dra': ('DRA', {'dra', 'debt recovery agent', 'debt recovery agents'}),
    'explained': ('Explained', {'legal explained', 'explained', 'case laws explained', 'legal explainers'}),
}

CASE_STATUS_GENERIC_HC = 'https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index&app_token=0dc6256584aa1dfddad859d53710b024acc973edfbbd1d5de5d935778a113e07'
DRT_EFILING = 'https://efiling.drt.gov.in/'
BARE_ACTS_URL = 'https://indiacode.gov.in/'
VC_DATA_PATH = ROOT / 'data/vc_links.json'

COURTS = {
    'high_courts': [
        ('Allahabad High Court', 'https://www.allahabadhighcourt.in/'),
        ('Andhra Pradesh High Court', 'https://aphc.gov.in/'),
        ('Bombay High Court', 'https://bombayhighcourt.nic.in/'),
        ('Calcutta High Court', 'https://www.calcuttahighcourt.gov.in/'),
        ('Chhattisgarh High Court', 'https://highcourt.cg.gov.in/'),
        ('Delhi High Court', 'https://www.delhihighcourt.nic.in/'),
        ('Gauhati High Court', 'https://ghconline.gov.in/'),
        ('Gujarat High Court', 'https://gujarathighcourt.nic.in/'),
        ('Himachal Pradesh High Court', 'https://hphighcourt.nic.in/'),
        ('Jammu & Kashmir and Ladakh High Court', 'https://jkhighcourt.nic.in/'),
        ('Jharkhand High Court', 'https://jharkhandhighcourt.nic.in/'),
        ('Karnataka High Court', 'https://karnatakajudiciary.kar.nic.in/'),
        ('Kerala High Court', 'https://highcourtofkerala.nic.in/'),
        ('Madhya Pradesh High Court', 'https://mphc.gov.in/'),
        ('Madras High Court', 'https://www.mhc.tn.gov.in/'),
        ('Manipur High Court', 'https://hcmimphal.nic.in/'),
        ('Meghalaya High Court', 'https://meghalayahighcourt.nic.in/'),
        ('Orissa High Court', 'https://orissahighcourt.nic.in/'),
        ('Patna High Court', 'https://patnahighcourt.gov.in/'),
        ('Punjab & Haryana High Court', 'https://highcourtchd.gov.in/'),
        ('Rajasthan High Court', 'https://hcraj.nic.in/'),
        ('Sikkim High Court', 'https://highcourtofsikkim.nic.in/'),
        ('Telangana High Court', 'https://hc.ts.nic.in/'),
        ('Tripura High Court', 'https://thc.nic.in/'),
        ('Uttarakhand High Court', 'https://highcourtofuttarakhand.gov.in/'),
    ],
    'drt': ['Ahmedabad','Allahabad','Aurangabad','Bengaluru','Chandigarh','Chennai','Cochin','Cuttack','Delhi','Guwahati','Hyderabad','Jaipur','Kolkata','Lucknow','Mumbai','Nagpur','Patna','Pune','Ranchi','Visakhapatnam'],
    'drat': ['Delhi','Allahabad','Chennai','Kolkata','Mumbai'],
    'nclt': ['Principal Bench / New Delhi','Ahmedabad','Allahabad','Amaravati','Bengaluru','Chandigarh','Chennai','Cuttack','Guwahati','Hyderabad','Indore','Jaipur','Kochi','Kolkata','Mumbai'],
    'nclat': ['Principal Bench / New Delhi','Chennai Bench'],
}


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'LexTalkLegalBot/1.0'})
    return urllib.request.urlopen(req, timeout=30).read()

def slug(s):
    return re.sub(r'-+', '-', re.sub(r'[^a-zA-Z0-9\s-]', '', s).strip().lower().replace(' ', '-'))[:90] or 'article'














def category_matches(a, key):
    labels = {str(x).strip().lower() for x in a.get("labels", [])}
    title = str(a.get("title", "")).lower()
    _, terms = CATEGORY_MAP[key]
    if labels & {str(t).strip().lower() for t in terms}:
        return True
    return any(str(term).strip().lower() in title for term in terms)


def write_category_pages(arts):
    template_map = {
        'courts': ROOT / 'templates/category/courts.html',
        'banking-law': ROOT / 'templates/category/banking-law.html',
        'dra': ROOT / 'templates/category/dra.html',
    }
    for key, (name, terms) in CATEGORY_MAP.items():
        items = [a for a in arts if category_matches(a, key)]
        if key in template_map and template_map[key].exists():
            cards = ''.join(article_card(a) for a in items[:12])
            if not cards:
                empty_class = {
                    'courts': 'courts-v2-empty',
                    'banking-law': 'banking-v1-empty',
                    'dra': 'dra-v1-empty'
                }.get(key, 'empty')
                cards = f'<div class="{empty_class}">No stories published in this section yet. Publish a Blogger post with the appropriate label and the next editorial sync will update this section.</div>'
            content = template_map[key].read_text(encoding='utf8').replace('{{LATEST_STORIES}}', cards)
            desc = f'Lex Talk Legal — {name}: legal information, practical guidance and latest stories.'
        else:
            cards = ''.join(article_card(a) for a in items[:30]) or '<div class="empty">No stories published in this section yet.</div>'
            content = f'<main class="utility-page"><div class="utility-kicker">LEX TALK LEGAL</div><h1>{H.escape(name)}</h1><p class="lead">Latest Lex Talk Legal stories in this section are synced automatically from Blogger.</p><div class="grid">{cards}</div></main>'
            desc = f'Lex Talk Legal — {name} news, updates and explainers.'
        p = ROOT / 'category' / key / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(page_shell((name, f'/category/{key}/'), desc, content), encoding='utf8')

def write_videos_page(videos):
    videos = videos[:30]
    if videos:
        featured = videos[0]
        f_thumb = H.escape(featured.get('thumbnail',''), quote=True)
        f_title = H.escape(featured.get('title','Lex Talk Legal'))
        f_date = H.escape(featured.get('published','')[:10])
        f_url = H.escape(featured.get('url','https://www.youtube.com/@LexTalkLegal'), quote=True)
        featured_media = (
            f'<a class="videos-v2-feature-media" href="{f_url}" target="_blank" rel="noopener noreferrer"><img src="{f_thumb}" alt="{f_title}" loading="eager" decoding="async"><span class="videos-v2-feature-badge">FEATURED VIDEO</span><span class="videos-v2-feature-play" aria-hidden="true">▶</span></a>'
            if f_thumb else
            f'<a class="videos-v2-feature-media" href="{f_url}" target="_blank" rel="noopener noreferrer"><div style="height:100%;display:grid;place-items:center;color:#fff;font:900 12px Arial,sans-serif;letter-spacing:1px">LEX TALK LEGAL</div><span class="videos-v2-feature-badge">FEATURED VIDEO</span><span class="videos-v2-feature-play" aria-hidden="true">▶</span></a>'
        )
        featured_copy = f'<div class="videos-v2-feature-copy"><div class="meta">{f_date} · Latest Upload</div><h3>{f_title}</h3><p>Watch the latest Lex Talk Legal video directly on YouTube.</p><a class="videos-v2-watch" href="{f_url}" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></div>'
        feature_html = f'<div class="videos-v2-featured">{featured_media}{featured_copy}</div>'
        rest = videos[1:]
    else:
        feature_html = '<div class="videos-v2-empty">No YouTube videos were returned in the latest sync.</div>'
        rest = []

    def vcard(v):
        thumb = H.escape(v.get('thumbnail',''), quote=True)
        title = H.escape(v.get('title','Lex Talk Legal'))
        date = H.escape(v.get('published','')[:10])
        url = H.escape(v.get('url','https://www.youtube.com/@LexTalkLegal'), quote=True)
        media = f'<img src="{thumb}" alt="{title}" loading="lazy" decoding="async">' if thumb else '<div></div>'
        return f'<article class="videos-v2-card"><a class="videos-v2-thumb" href="{url}" target="_blank" rel="noopener noreferrer">{media}<span class="videos-v2-play" aria-hidden="true">▶</span></a><div class="videos-v2-card-body"><div class="videos-v2-card-date">{date}</div><h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3></div></article>'

    grid = ''.join(vcard(v) for v in rest) if rest else '<div class="videos-v2-empty">The latest video library is currently empty.</div>'
    template = (ROOT / 'templates/videos.html').read_text(encoding='utf8')
    content = template.replace('{{FEATURED_HTML}}', feature_html).replace('{{VIDEO_GRID}}', grid).replace('{{VIDEO_COUNT}}', str(len(videos)))
    (ROOT / 'videos').mkdir(exist_ok=True)
    (ROOT / 'videos/index.html').write_text(
        page_shell(('Latest Videos','/videos/'),'Latest Lex Talk Legal videos, legal news and explainers.',content),
        encoding='utf8'
    )

def button(label,url,kind='official'):
    return f'<a class="link-button {kind}" href="{H.escape(url,quote=True)}" target="_blank" rel="noopener">{H.escape(label)}</a>'

def utility_card(icon,title,text,links):
    links_html=''.join(button(label,url,kind) for label,url,kind in links)
    return f'<article class="utility-card court-card"><div><div class="court-icon">{icon}</div><h3>{H.escape(title)}</h3><p>{H.escape(text)}</p></div><div class="card-actions">{links_html}</div></article>'








def under_construction_page():
    content='''<main class="utility-page under-page"><div class="guide-badge large"><div class="guide-badge-icon">🏦</div><strong>AUCTION LISTINGS</strong><span>Directory module in preparation</span></div><div class="utility-kicker">COMING SOON</div><h1>Public Auction Listings</h1><p class="lead">A searchable directory for bank, financial-institution and authority auction notices is being prepared. Until the directory is live, the Auction Assistance Desk can help with participation-process information.</p><div class="under-box"><h2>What will appear here?</h2><div class="under-grid"><div>🏠 Property Auctions</div><div>🏢 Commercial Assets</div><div>🚗 Vehicle Auctions</div><div>📍 Location Filters</div><div>🏦 Bank / Institution</div><div>📄 Official Notice Links</div></div></div><a class="primary-btn" href="/auctions/">Visit Auction Assistance Desk ↗</a></main>'''
    (ROOT/'under-construction.html').write_text(page_shell(("Public Auction Listings",'/under-construction.html'),'Lex Talk Legal public auction listings module — currently in preparation.',content),encoding='utf8')


# ---------- v5 presentation/build layer ----------
SITE_URL='https://lextalk.legal'
LOGO='/assets/LexTalkLegal_Logo-wo-bg.png'

# Presentation navigation mirrors the publication's compact information architecture.
NAV=[
 ('Latest','/'),('Courts','/category/courts/'),('Auctions','/auctions/'),('Banking & Recovery','/category/banking-law/'),
 ('Legal Careers','/category/legal-careers/'),('DRA','/category/dra/'),('Courtrooms','/courtrooms/'),('Case Status','/case-status/'),('Videos','/videos/')]
MEGA_GROUPS=[
 ('NEWSROOM',[('Latest','/'),('Courts','/category/courts/'),('Law & Policy','/category/law-policy/'),('Explained','/category/explained/')]),
 ('BANKING & RECOVERY',[('Banking Law','/category/banking-law/'),('DRT / DRAT','/category/drt-drat/'),('SARFAESI','/category/banking-law/'),('DRA','/category/dra/'),('Auctions','/auctions/')]),
 ('LEGAL CAREERS',[('Legal Careers','/category/legal-careers/'),('AIBE','/category/legal-careers/'),('Bare Acts',BARE_ACTS_URL)]),
 ('UTILITIES',[('Courtrooms / VC','/courtrooms/'),('Case Status','/case-status/'),('Search','/search.html')]),
 ('COMMUNITY & CONTACT',[('Case Information','/case-help.html'),('Our Advocate Team','/team.html'),('About','/about.html'),('Contact','/contact.html')]),
 ('MEDIA',[('Videos','/videos/'),('YouTube','https://www.youtube.com/@LexTalkLegal'),('Advertise','/advertise.html')])]

CATEGORY_MAP={
 'courts':('Courts',{'supreme court','high court','courts','judiciary','case laws','case law'}),
 'law-policy':('Law & Policy',{'law & policy','law and policy','law policy','policy','legislation'}),
 'banking-law':('Banking Law',{'banking law','banking','sarfaesi','ibc','insolvency','recovery'}),
 'drt-drat':('DRT / DRAT',{'drt','drat','drt / drat','sarfaesi'}),
 'legal-careers':('Legal Careers',{'legal careers','aibe','bar council','cop','judiciary careers','judiciary'}),
 'dra':('DRA',{'dra','debt recovery agent','debt recovery agents'}),
 'explained':('Explained',{'legal explained','explained','case laws explained','legal explainers'})}

def clean(raw, remove_first_image=False):
    soup=BeautifulSoup(raw or '','html.parser')
    for x in soup(['script','style','iframe','form','object','embed','video']): x.decompose()
    if remove_first_image:
        first=soup.find('img')
        if first:first.decompose()
    for a in soup.find_all('a',href=True):
        a['target']='_blank'; a['rel']='noopener noreferrer'
    for img in soup.find_all('img'):
        img['loading']='lazy'; img['decoding']='async'
    return str(soup).strip()

def normalize_articles(arts):
    out=[]
    for a in arts or []:
        x=dict(a)
        soup=BeautifulSoup(x.get('content','') or '','html.parser')
        first=soup.find('img')
        if first:first.decompose()
        for img in soup.find_all('img'):
            img['loading']='lazy';img['decoding']='async'
        x['content']=str(soup).strip()
        out.append(x)
    return out

def blogger():
    if os.getenv('LOCAL_BUILD') == '1':
        try:return json.loads((ROOT/'data/articles.json').read_text(encoding='utf8'))
        except Exception:return []
    try: root=ET.fromstring(fetch(f'{BLOGGER}/feeds/posts/default?alt=atom&max-results=50'))
    except Exception as e: print('Blogger:',e); return []
    out=[]
    for e in root.findall('a:entry',NS):
        title=e.findtext('a:title',default='',namespaces=NS).strip();link=''
        for l in e.findall('a:link',NS):
            if l.attrib.get('rel')=='alternate':link=l.attrib.get('href','')
        pub=e.findtext('a:published',default='',namespaces=NS) or e.findtext('a:updated',default='',namespaces=NS)
        c=e.find('a:content',NS);raw=c.text if c is not None else ''
        soup=BeautifulSoup(raw or '','html.parser');img=soup.find('img')
        labels=[x.attrib.get('term','') for x in e.findall('a:category',NS) if x.attrib.get('term')]
        text=' '.join(soup.stripped_strings)
        out.append({'title':title,'url':'/article/'+slug(title)+'.html','source_url':link,'published':pub,'labels':labels,'category':labels[0] if labels else 'Legal News','image':img.get('src') if img else '','excerpt':text[:230]+('…' if len(text)>230 else ''),'content':clean(raw,remove_first_image=True)})
    return normalize_articles(out)

def youtube():
    # Deterministic local builds/tests should never require YouTube network access.
    if os.getenv('LOCAL_BUILD') == '1':
        try:
            data = json.loads((ROOT/'data/youtube.json').read_text(encoding='utf8'))
            return data if isinstance(data, list) else []
        except Exception:
            return []
    channel_id=CHANNEL_ID
    try:
        if not channel_id:
            p=fetch('https://www.youtube.com/'+HANDLE+'/videos').decode('utf8','ignore')
            m=re.search(r'<meta itemprop="channelId" content="(UC[^"]+)"',p) or re.search(r'"channelId":"(UC[^"]+)"',p) or re.search(r'"externalId":"(UC[^"]+)"',p)
            if not m:raise RuntimeError('YouTube channel ID not found')
            channel_id=m.group(1)
        root=ET.fromstring(fetch('https://www.youtube.com/feeds/videos.xml?channel_id='+channel_id));out=[]
        for e in root.findall('a:entry',NS):
            title=e.findtext('a:title',default='',namespaces=NS);le=e.find('a:link',NS);link=le.attrib.get('href','') if le is not None else '';pub=e.findtext('a:published',default='',namespaces=NS);vid=e.findtext('yt:videoId',default='',namespaces=NS)
            out.append({'title':title,'url':link,'published':pub,'video_id':vid,'thumbnail':'https://i.ytimg.com/vi/'+vid+'/hqdefault.jpg' if vid else ''})
        return out
    except Exception as e:
        print('YouTube:',e)
        try:return json.loads((ROOT/'data/youtube.json').read_text(encoding='utf8'))
        except Exception:return []

def mega_menu_html():
    groups=[]
    for title,items in MEGA_GROUPS:
        links=''.join(f'<a href="{H.escape(u,quote=True)}">{H.escape(x)}</a>' for x,u in items)
        groups.append(f'<section class="mega-group"><h3>{H.escape(title)}</h3>{links}</section>')
    return ''.join(groups)

def nav_html():
    main=''.join(f'<a href="{H.escape(u,quote=True)}">{H.escape(x)}</a>' for x,u in NAV)
    mega=mega_menu_html()
    return f'<button class="menu-trigger" id="menuTrigger" type="button" aria-expanded="false" aria-controls="megaMenu" aria-label="Open site menu"><span class="hamburger-lines"><i></i><i></i><i></i></span><span class="menu-trigger-label">MENU</span></button><div class="nav-links">{main}</div><a class="nav-search" href="/search.html" aria-label="Search">⌕ <span>SEARCH</span></a><div class="mega-menu" id="megaMenu" hidden><div class="mega-menu-inner">{mega}</div></div>'

def build_timestamp():
    return datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d %B %Y, %H:%M:%S')

BUILD_TIME=build_timestamp()
BUILD_EPOCH=int(datetime.now(ZoneInfo('Asia/Kolkata')).timestamp())

PAGE_STYLE_MAP = {
    "/about.html": "about.css",
    "/about": "about.css",
    "/contact.html": "contact.css",
    "/contact": "contact.css",
    "/category/courts/": "courts.css",
    "/category/banking-law/": "banking-law.css",
    "/category/dra/": "dra.css",
    "/videos/": "videos.css",
}




def page_style_head(canonical):
    css_file = PAGE_STYLE_MAP.get(canonical)
    return f'<link rel="stylesheet" href="/assets/pages/{css_file}">' if css_file else ''

def page_shell(title,description,content,extra_head=""):
    t=title[0] if isinstance(title,tuple) else title
    canonical=title[1] if isinstance(title,tuple) else '/'
    robots='index,follow,max-image-preview:large'
    nav=nav_html()
    schema={"@context":"https://schema.org","@type":"WebSite","name":"Lex Talk Legal","url":SITE_URL+"/","description":"Law Simplified for Everyone.","publisher":{"@type":"Organization","name":"LEXBOTICS AI MEDIA LLP","url":SITE_URL+"/"}}
    schema_json=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="{H.escape(description,quote=True)}"><meta name="robots" content="{robots}">
<link rel="canonical" href="{SITE_URL}{H.escape(canonical,quote=True)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Lex Talk Legal"><meta property="og:title" content="{H.escape(t,quote=True)}"><meta property="og:description" content="{H.escape(description,quote=True)}"><meta property="og:url" content="{SITE_URL}{H.escape(canonical,quote=True)}"><meta property="og:image" content="{SITE_URL}/assets/LexTalkLegal_Logo-wo-bg.png"><meta name="twitter:card" content="summary_large_image">
<title>{H.escape(t)} | Lex Talk Legal</title><link rel="stylesheet" href="/assets/site.css">{page_style_head(canonical)}<script type="application/ld+json">{schema_json}</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3161673810996421" crossorigin="anonymous"></script>{extra_head}</head><body>
<div class="site-accent"></div><div class="utility-bar"><div class="wrap utility-inner"><div class="utility-left"><span class="live-dot">●</span><span id="dateLabel">--</span><span class="utility-sep">|</span><span id="timeLabel">--:--:-- IST</span></div><div class="utility-actions"><button class="control-btn" id="themeBtn" type="button" aria-label="Switch to dark mode">☾ Dark</button></div></div></div>
<header class="masthead"><div class="wrap masthead-inner"><a href="/" aria-label="Lex Talk Legal home"><img src="{LOGO}" alt="Lex Talk Legal"></a></div></header>
<nav class="nav"><div class="wrap nav-inner">{nav}</div></nav>
{content}
<footer class="footer"><div class="footergrid"><div><h3>Lex Talk Legal</h3><p>Law Simplified for Everyone.</p><p>Digital legal news, court updates, legal education and practical legal awareness.</p><p><b>LEXBOTICS AI MEDIA LLP</b></p></div><div><h3>Explore</h3><ul><li><a href="/">Latest</a></li><li><a href="/auctions/">Auctions</a></li><li><a href="/category/courts/">Courts</a></li><li><a href="/category/banking-law/">Banking &amp; Recovery</a></li><li><a href="/category/legal-careers/">Legal Careers</a></li><li><a href="/category/dra/">DRA</a></li></ul></div><div><h3>Utilities</h3><ul><li><a href="/courtrooms/">Courtrooms / VC</a></li><li><a href="/case-status/">Case Status</a></li><li><a href="/search.html">Search</a></li><li><a href="/category/drt-drat/">DRT / DRAT</a></li><li><a href="/case-help.html">Case Information</a></li></ul></div><div><h3>Connect</h3><ul><li><a href="https://www.youtube.com/@LexTalkLegal" target="_blank" rel="noopener noreferrer">YouTube</a></li><li><a href="https://www.instagram.com/lex_talk_legal" target="_blank" rel="noopener noreferrer">Instagram</a></li><li><a href="https://x.com/Lex_Talk_Legal" target="_blank" rel="noopener noreferrer">X</a></li><li><a href="https://in.linkedin.com/company/lextalklegal" target="_blank" rel="noopener noreferrer">LinkedIn</a></li><li><a href="https://t.me/lextalklegal" target="_blank" rel="noopener noreferrer">Telegram</a></li></ul></div><div><h3>Legal &amp; Contact</h3><p>+91-8368268507<br>+91-9318445957<br>office.lextalklegal@gmail.com</p><ul><li><a href="/privacy-policy.html">Privacy Policy</a></li><li><a href="/terms-of-use.html">Terms of Use</a></li><li><a href="/disclaimer.html">Disclaimer</a></li><li><a href="/editorial-policy.html">Editorial Policy</a></li><li><a href="/copyright-policy.html">Copyright / Takedown</a></li><li><a href="/corrections-grievance.html">Corrections &amp; Grievance</a></li><li><a href="/ai-content-policy.html">AI Content Policy</a></li></ul></div></div><div class="updated-line" data-built-at="{BUILD_TIME} IST" data-built-epoch="{BUILD_EPOCH}">Content last updated: {BUILD_TIME} IST</div><div class="copy">© 2026 LEXBOTICS AI MEDIA LLP | Lex Talk Legal | For Educational &amp; Informational Use Only</div></footer><script src="/assets/site.js" defer></script></body></html>'''

def article(a):
    image=a.get('image','')
    hero=f'<div class="article-hero media-frame" style="--media-image:url(&quot;{H.escape(image,quote=True)}&quot;)"><img src="{H.escape(image,quote=True)}" alt="{H.escape(a.get("title",""),quote=True)}" loading="eager" decoding="async"></div>' if image else ''
    soup=BeautifulSoup(a.get('content','') or '','html.parser')
    # Remove every in-body copy of the lead image, not just the first image.
    if image:
        norm=re.sub(r'[?#].*$','',image).rstrip('/')
        for im in soup.find_all('img'):
            src=(im.get('src') or '').split('#')[0].rstrip('/')
            if src==norm or (src and norm and src.endswith(norm.split('/')[-1])):
                im.decompose()
    body_html=str(soup)
    schema={'@context':'https://schema.org','@type':'NewsArticle','headline':a.get('title',''),'datePublished':a.get('published',''),'dateModified':a.get('published',''),'mainEntityOfPage':{'@type':'WebPage','@id':SITE_URL+a.get('url','')},'author':{'@type':'Organization','name':'Lex Talk Legal','url':SITE_URL+'/'},'publisher':{'@type':'Organization','name':'LEXBOTICS AI MEDIA LLP','url':SITE_URL+'/'},'description':a.get('excerpt','')}
    if image:schema['image']=[image]
    schema_json=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    desc=a.get('excerpt','')
    body=f'''<main class="article-wrap"><div class="utility-kicker">{H.escape(a.get('category','Legal News'))}</div><div class="story-meta">{H.escape(a.get('published','')[:10])}</div><h1>{H.escape(a.get('title',''))}</h1><div class="article-meta">Lex Talk Legal · Educational &amp; informational coverage <span>·</span> <a href="{H.escape(a.get('source_url',''),quote=True)}" target="_blank" rel="noopener noreferrer">Original source</a></div>{hero}<div class="article-body">{body_html}</div><div class="notice"><strong>Editorial note:</strong> This content is for general legal information and education. Verify important legal facts, orders, dates and current procedural requirements from the concerned official source.</div><div class="article-source">Source reference: Original Blogger publication linked above. Lex Talk Legal does not represent that linked third-party content is error-free or current in every respect.</div></main>'''
    return page_shell((a.get('title',''),a.get('url','')),desc,body).replace('</head>','<script type="application/ld+json">'+schema_json+'</script></head>')


def media_html(url, cls='story-image', alt=''):
    if not url:
        return f'<div class="{cls} media-frame"></div>'
    return f'<div class="{cls} media-frame" style="--media-image:url(&quot;{H.escape(url,quote=True)}&quot;)"><img src="{H.escape(url,quote=True)}" alt="{H.escape(alt,quote=True)}" loading="lazy" decoding="async"></div>'

def article_card(a,variant='standard'):
    media=media_html(a.get('image',''),'story-image',a.get('title',''))
    compact=' compact' if variant=='compact' else ''
    return f'<article class="story-card{compact}"><a href="{H.escape(a["url"],quote=True)}">{media}</a><div class="story-meta">{H.escape(a.get("category","Legal News"))} · {H.escape(a.get("published","")[:10])}</div><h3><a href="{H.escape(a["url"],quote=True)}">{H.escape(a.get("title",""))}</a></h3><p>{H.escape(a.get("excerpt",""))}</p></article>'

def secondary_card(a):
    media=media_html(a.get('image',''),'secondary-image',a.get('title',''))
    return f'<article class="secondary-story"><a href="{H.escape(a["url"],quote=True)}">{media}</a><div class="secondary-copy"><div class="story-meta">{H.escape(a.get("category","Legal News"))} · {H.escape(a.get("published","")[:10])}</div><h3><a href="{H.escape(a["url"],quote=True)}">{H.escape(a.get("title",""))}</a></h3><p>{H.escape(a.get("excerpt",""))}</p></div></article>'

def video_card(v):
    thumb=H.escape(v.get('thumbnail',''),quote=True); title=H.escape(v.get('title','Lex Talk Legal')); date=H.escape(v.get('published','')[:10]);url=H.escape(v.get('url','https://www.youtube.com/@LexTalkLegal'),quote=True); visual=f'<img src="{thumb}" alt="" loading="lazy" decoding="async">' if thumb else '<div></div>'
    return f'<article class="video-card"><a href="{url}" target="_blank" rel="noopener noreferrer"><div class="video-thumb">{visual}<span class="video-play">▶</span></div></a><div class="video-card-body"><div class="story-meta">{date}</div><h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3></div></article>'


def global_widget_markup(): return ''
def auction_widget_markup(): return '<article class="utility-card"><div class="icon">🏦</div><div class="side-kicker">FEATURED UTILITY</div><h3><a href="/under-construction.html">Today’s Bank Auction</a></h3><p>The searchable auction directory is being prepared with source and verification controls.</p><a class="utility-link" href="/under-construction.html">Explore auction module ↗</a></article>'
def homepage_sidebar_markup():
    return f'''<article class="utility-card"><div class="icon">🎥</div><div class="side-kicker">LEGAL UTILITY</div><h3><a href="/courtrooms/">Official courtroom &amp; VC links</a></h3><p>Open public virtual-hearing destinations and courtroom information.</p><a class="utility-link" href="/courtrooms/">Open Courtrooms ↗</a></article><article class="utility-card"><div class="icon">🔎</div><div class="side-kicker">LEGAL UTILITY</div><h3><a href="/case-status/">Official case-status portals</a></h3><p>Quick links for courts and tribunals. CAPTCHA and access controls remain with the official portal.</p><a class="utility-link" href="/case-status/">Check Case Status ↗</a></article><article class="utility-card"><div class="icon">📚</div><div class="side-kicker">LEGAL KNOWLEDGE</div><h3><a href="/category/drt-drat/">DRT, DRAT, SARFAESI &amp; Banking Law</a></h3><p>Practical explainers, history and current legal coverage.</p><a class="utility-link" href="/category/banking-law/">Explore Banking Law ↗</a></article>{auction_widget_markup()}'''

def sync_homepage(arts,videos):
    arts=normalize_articles(arts)
    now=datetime.now(timezone.utc)
    fresh=[]
    for a in arts:
        try:
            dt=datetime.fromisoformat(a.get('published','').replace('Z','+00:00'))
            if (now-dt).total_seconds() <= 7*24*3600: fresh.append(a)
        except Exception: pass
    pool=(fresh[:8] if fresh else arts[:8])
    lead=pool[:1]; side=pool[1:4]; latest=pool[4:8]; vids=videos[:4]
    if lead:
        a=lead[0]
        img=media_html(a.get('image',''),'home-lead-image',a.get('title','')) if a.get('image') else '<div class="home-lead-image media-frame"></div>'
        lead_html=f'<article class="home-lead-story"><a class="story-image-link" href="{H.escape(a["url"],quote=True)}">{img}</a><div class="story-meta">{H.escape(a.get("category","Legal News"))} · {H.escape(a.get("published","")[:10])}</div><h1><a href="{H.escape(a["url"],quote=True)}">{H.escape(a.get("title",""))}</a></h1><p>{H.escape(a.get("excerpt",""))}</p><a class="home-read-link" href="{H.escape(a["url"],quote=True)}">Read full story ↗</a></article>'
    else:
        lead_html='<article class="home-lead-story"><div class="home-lead-image media-frame"></div><div class="story-meta">LEX TALK LEGAL</div><h1>Law, Courts &amp; Justice — Explained in Simple Language</h1><p>Fresh legal news, court updates, judgments and practical legal explainers.</p></article>'
    secondary=''.join(f'<article class="home-secondary-story"><a href="{H.escape(a["url"],quote=True)}">{media_html(a.get("image",""),"home-secondary-image",a.get("title",""))}</a><div class="home-secondary-copy"><div class="story-meta">{H.escape(a.get("category","Legal News"))} · {H.escape(a.get("published","")[:10])}</div><h2><a href="{H.escape(a["url"],quote=True)}">{H.escape(a.get("title",""))}</a></h2><p>{H.escape(a.get("excerpt",""))}</p></div></article>' for a in side) or '<div class="empty">Fresh stories will appear after the next content sync.</div>'
    latest_html=''.join(article_card(a,'home-latest') for a in latest) or '<div class="empty">No additional recent stories are available right now.</div>'
    vid_html=''.join(video_card(v) for v in vids) or '<div class="empty">No recent YouTube videos are available right now.</div>'
    # Deterministic homepage timestamp: use the latest source publication date, not build time.
    # A scheduled sync therefore does not create a new commit/deployment when there is no content change.
    source_dates = []
    for item in (arts + videos):
        raw = str(item.get('published', ''))[:10]
        if re.match(r'^\d{4}-\d{2}-\d{2}$', raw):
            source_dates.append(raw)
    updated = max(source_dates) if source_dates else 'Latest available feed'
    content=f'''<main class="home home-v9"><section class="home-breaking"><div class="wrap ticker-inner"><span class="breaking">LATEST</span><span class="tick">Court updates · Judgments · Banking &amp; Recovery · Auctions · Legal Careers · Practical Legal Awareness</span></div></section><div class="wrap"><section class="home-front section"><div class="home-front-grid"><div>{lead_html}</div><div class="home-secondary-list">{secondary}</div></div><div class="front-fresh">Front page selection: the latest {len(pool) if pool else 0} recent stories are prioritised here; older stories remain available in their sections.</div></section><div class="home-ad ad-wrap"><div class="ad-slot"><span>ADVERTISEMENT</span></div></div><section class="section home-news-section"><div class="home-main-grid"><div><div class="section-head"><div><span class="section-kicker">NEWS DESK</span><h2>Latest Legal News</h2></div><p>Updated {H.escape(updated)}</p></div><div class="home-latest-grid">{latest_html}</div><div class="section-more"><a class="text-link" href="/search.html">View more legal news ↗</a></div></div><aside class="home-quick-rail"><div class="quick-rail-sticky"><div class="quick-rail-title"><span>QUICK DESK</span><strong>Useful links</strong></div><a class="quick-card" href="/auctions/"><span class="quick-icon">🏦</span><span><b>Today’s Auctions</b><small>Bank · FI · Authority</small></span><em>↗</em></a><a class="quick-card" href="/courtrooms/"><span class="quick-icon">⚖</span><span><b>Courtrooms / VC</b><small>Public hearing links</small></span><em>↗</em></a><a class="quick-card" href="/case-status/"><span class="quick-icon">⌕</span><span><b>Case Status</b><small>Official court portals</small></span><em>↗</em></a><a class="quick-card" href="/category/legal-careers/"><span class="quick-icon">▣</span><span><b>Latest Jobs</b><small>Legal careers &amp; opportunities</small></span><em>↗</em></a><div class="ad-slot rail-ad">ADVERTISEMENT</div></div></aside></div></section><section class="section"><div class="section-head"><div><span class="section-kicker">AUCTION DESK</span><h2>Bank, FI &amp; Authority Auctions</h2></div><a class="text-link" href="/auctions/">Open Auction Desk ↗</a></div><div class="auction-home-grid"><article><div class="auction-home-icon">🏦</div><h3>Bank Auctions</h3><p>Residential, commercial and industrial assets notified for public sale.</p></article><article><div class="auction-home-icon">🏢</div><h3>Financial Institution Auctions</h3><p>Publicly notified assets and participation information.</p></article><article><div class="auction-home-icon">🏛</div><h3>Authority Auctions</h3><p>Government and institutional auction notices and updates.</p></article></div><div class="auction-disclaimer">Always read and independently verify the issuing authority’s original auction notice, bidder eligibility, EMD, title/possession position, dues and sale conditions.</div></section><section class="section"><div class="home-service-grid"><article class="home-service case-info"><span class="section-kicker">CASE INFORMATION DESK</span><h2>Have a case file you need to understand?</h2><p>Send a brief description or email relevant documents for consideration. Any review, advice, representation or professional routing is subject to separate consideration and acceptance.</p><div class="service-actions"><a class="primary-btn" href="/case-help.html">Case Information Desk ↗</a><a class="ghost-btn dark-ghost" href="mailto:office.lextalklegal@gmail.com?subject=Case%20Information%20Request">Email the Office</a></div></article><article class="home-service team-info"><span class="section-kicker">OUR ADVOCATE TEAM</span><h2>Courts, Forums &amp; Practice Areas</h2><p>Meet the advocates associated with the platform and view factual information about identified courts/forums and practice areas.</p><div class="team-mini-row"><span>COURTS</span><span>DRT / DRAT</span><span>BANKING &amp; RECOVERY</span><span>CIVIL &amp; COMMERCIAL</span></div><div class="service-actions"><a class="text-link" href="/team.html">Meet the Team ↗</a></div></article></div></section><section class="section"><div class="section-head"><div><span class="section-kicker">EXPLAINED</span><h2>Legal Concepts, Simply Explained</h2></div><a class="text-link" href="/category/explained/">Explore explainers ↗</a></div><div class="explainer-home-grid"><a href="/category/explained/"><span>01</span><b>Understand a Court Order</b><small>Observations, directions &amp; operative portions</small></a><a href="/category/banking-law/"><span>02</span><b>SARFAESI &amp; Recovery</b><small>Process, notices, possession &amp; remedies</small></a><a href="/category/legal-careers/"><span>03</span><b>AIBE &amp; Legal Careers</b><small>Exams, enrolment &amp; practical guidance</small></a></div></section><section class="section"><div class="section-head"><div><span class="section-kicker">WATCH</span><h2>Latest on YouTube</h2></div><a class="text-link" href="/videos/">View all videos ↗</a></div><div class="video-grid home-video-grid">{vid_html}</div></section></div></main><section class="newsletter home-newsletter"><div class="wrap newsletter-inner"><div><span class="section-kicker">THE LEGAL BRIEF</span><h2>Stay updated with important legal developments</h2><p>Selected court updates, judgments, explainers and career information.</p></div><form class="newsletter-form" onsubmit="event.preventDefault();alert('Newsletter signup will be connected to the selected mailing provider before public launch.');"><input type="email" required placeholder="Your email address" aria-label="Your email address"><button class="primary-btn" type="submit">Subscribe</button></form></div></section>'''
    (ROOT/'index.html').write_text(page_shell(('Lex Talk Legal','/'),'Fresh legal news, court updates, judgments, legal education and practical legal awareness.',content),encoding='utf8')








def main():
    ap = ROOT / 'data/articles.json'
    try:
        existing_arts = json.loads(ap.read_text(encoding='utf8'))
        if not isinstance(existing_arts, list):
            existing_arts = []
    except Exception:
        existing_arts = []

    fetched_arts = blogger()
    if fetched_arts:
        # Merge the recent Blogger feed into the local archive instead of deleting
        # older articles that are outside the feed window.
        by_url = {
            str(a.get('url', '')): a
            for a in existing_arts
            if isinstance(a, dict) and a.get('url')
        }
        for a in fetched_arts:
            if isinstance(a, dict) and a.get('url'):
                by_url[str(a['url'])] = a
        arts = list(by_url.values())
    else:
        arts = existing_arts

    arts = normalize_articles(arts)
    arts.sort(key=lambda x: x.get('published', ''), reverse=True)
    ap.parent.mkdir(exist_ok=True)
    ap.write_text(json.dumps(arts, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

    yp = ROOT / 'data/youtube.json'
    try:
        existing_videos = json.loads(yp.read_text(encoding='utf8'))
        if not isinstance(existing_videos, list):
            existing_videos = []
    except Exception:
        existing_videos = []

    fetched_videos = youtube()
    if fetched_videos:
        # Keep known videos while replacing/updating entries returned by YouTube.
        by_video = {}
        for v in existing_videos:
            key = str(v.get('video_id') or v.get('url') or '')
            if key:
                by_video[key] = v
        for v in fetched_videos:
            key = str(v.get('video_id') or v.get('url') or '')
            if key:
                by_video[key] = v
        videos = list(by_video.values())
    else:
        videos = existing_videos

    videos.sort(key=lambda x: x.get('published', ''), reverse=True)
    yp.write_text(json.dumps(videos, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

    # Update/create current article files without deleting older published articles.
    d = ROOT / 'article'
    d.mkdir(exist_ok=True)
    for a in arts:
        out = d / (slug(a['title']) + '.html')
        out.write_text(article(a), encoding='utf8')

    # Editorial sync owns only editorial outputs. It does not rebuild manual
    # desks, static policy pages, configs, or manually maintained datasets.
    write_category_pages(arts)
    write_videos_page(videos)
    sync_homepage(arts, videos)

    # Deterministic sitemap: static/manual pages omit lastmod; editorial pages use
    # source publication dates. This avoids a new sitemap commit every 30 minutes.
    static_urls = [
        '/', '/about', '/contact', '/courtrooms/', '/case-status/', '/videos/',
        '/auctions/', '/jobs/', '/case-help.html', '/team.html', '/search.html',
        '/privacy-policy.html', '/terms-of-use.html', '/disclaimer.html',
        '/editorial-policy.html', '/copyright-policy.html', '/corrections-grievance.html',
        '/ai-content-policy.html', '/profile-guidelines.html'
    ]
    entries = [f'<url><loc>{SITE_URL}{u}</loc></url>' for u in static_urls]
    for key in CATEGORY_MAP:
        dates = []
        for a in arts:
            if category_matches(a, key):
                pub = str(a.get('published', ''))[:10]
                if re.match(r'^\d{4}-\d{2}-\d{2}$', pub):
                    dates.append(pub)
        last = max(dates) if dates else ''
        lastmod = f'<lastmod>{last}</lastmod>' if last else ''
        entries.append(f'<url><loc>{SITE_URL}/category/{key}/</loc>{lastmod}</url>')
    for a in arts:
        pub = str(a.get('published', ''))[:10]
        lastmod = f'<lastmod>{pub}</lastmod>' if re.match(r'^\d{4}-\d{2}-\d{2}$', pub) else ''
        entries.append(f'<url><loc>{SITE_URL}{a["url"]}</loc>{lastmod}</url>')

    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(entries) + '</urlset>'
    (ROOT / 'sitemap.xml').write_text(xml, encoding='utf8')

if __name__=='__main__':main()
