from pathlib import Path
import os, re, json, html as H, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'assets/site.css').read_text(encoding='utf8')
JS = (ROOT / 'assets/site.js').read_text(encoding='utf8')
LOGO = 'data:image/png;base64,' + __import__('base64').b64encode((ROOT / 'assets/LexTalkLegal_Logo-wo-bg.png').read_bytes()).decode()
BLOGGER = os.getenv('BLOGGER_URL', 'https://lextalklegal.blogspot.com').rstrip('/')
HANDLE = os.getenv('YOUTUBE_HANDLE', '@lextalklegal')
CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID', '').strip()
NS = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}

NAV = [
    ('Latest', '/'), ('Courts', '/category/courts/'), ('Law & Policy', '/category/law-policy/'),
    ('Banking Law', '/category/banking-law/'), ('DRT / DRAT', '/category/drt-drat/'),
    ('Legal Careers', '/category/legal-careers/'), ('DRA', '/category/dra/'),
    ('Bare Acts', 'https://indiacode.gov.in/'), ('Courtrooms', '/courtrooms/'),
    ('Case Status', '/case-status/'), ('Videos', '/videos/')
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
ONECOURT_ROOT_VC = 'https://onecourt.in/VC_Hearing_Links.html'
ONECOURT_SC_VC = 'https://onecourt.in/Supreme_Court_VC_Hearing_Links.html'
ONECOURT_NCLT_VC = 'https://onecourt.in/vc-links/nclt/NCLT_VC_Hearing_Links.html'
ONECOURT_NCLAT_VC = 'https://onecourt.in/vc-links/nclat/NCLAT_VC_Hearing_Links.html'
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

DELHI_DISTRICT_VC = [
    ('Central District — Tis Hazari', 'https://onecourt.in/vc-links/delhi/districtcourts/Central_District_VC_Links.html'),
    ('South-East District — Saket', 'https://onecourt.in/vc-links/delhi/districtcourts/South-East_District_VC_Links.html'),
    ('South-West District — Dwarka', 'https://onecourt.in/vc-links/delhi/districtcourts/South-West_District_VC_Links.html'),
    ('North-West District — Rohini', 'https://onecourt.in/vc-links/delhi/districtcourts/North-West_District_VC_Links.html'),
]

DIRECT_VC_DOMAINS = (
    'webex.com', 'meet.google.com', 'zoom.us', 'teams.live.com', 'teams.microsoft.com', 'vcourts.gov.in'
)

GENERIC_LABELS = {
    'join vc', 'district court join vc', 'family court join vc', 'digital court join vc',
    'digital traffic court join vc', 'join vc hearing link', 'vc hearing links', 'vc link'
}


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 LexTalkLegalBot/2.0'})
    return urllib.request.urlopen(req, timeout=45).read()


def slug(s):
    return re.sub(r'-+', '-', re.sub(r'[^a-zA-Z0-9\s-]', '', s).strip().lower().replace(' ', '-'))[:90] or 'article'


def clean(raw):
    soup = BeautifulSoup(raw or '', 'html.parser')
    for x in soup(['script','style','iframe','form','object','embed']): x.decompose()
    for a in soup.find_all('a', href=True):
        a['target'] = '_blank'; a['rel'] = 'noopener'
    return str(soup)


def blogger():
    try: root = ET.fromstring(fetch(f'{BLOGGER}/feeds/posts/default?alt=atom&max-results=50'))
    except Exception as e: print('Blogger:', e); return []
    out=[]
    for e in root.findall('a:entry', NS):
        title=e.findtext('a:title', default='', namespaces=NS).strip(); link=''
        for l in e.findall('a:link', NS):
            if l.attrib.get('rel')=='alternate': link=l.attrib.get('href','')
        pub=e.findtext('a:published', default='', namespaces=NS) or e.findtext('a:updated', default='', namespaces=NS)
        c=e.find('a:content', NS); raw=c.text if c is not None else ''
        soup=BeautifulSoup(raw or '', 'html.parser'); img=soup.find('img')
        labels=[x.attrib.get('term','') for x in e.findall('a:category', NS) if x.attrib.get('term')]
        text=' '.join(soup.stripped_strings)
        out.append({'title':title,'url':'/article/'+slug(title)+'.html','source_url':link,'published':pub,'labels':labels,'category':labels[0] if labels else 'Legal News','image':img.get('src') if img else '','excerpt':text[:210]+('…' if len(text)>210 else ''),'content':clean(raw)})
    return out


def youtube():
    channel_id=CHANNEL_ID
    try:
        if not channel_id:
            p=fetch('https://www.youtube.com/'+HANDLE+'/videos').decode('utf8','ignore')
            m=re.search(r'<meta itemprop="channelId" content="(UC[^"]+)"',p) or re.search(r'"channelId":"(UC[^"]+)"',p) or re.search(r'"externalId":"(UC[^"]+)"',p)
            if not m: raise RuntimeError('YouTube channel ID not found')
            channel_id=m.group(1)
        root=ET.fromstring(fetch('https://www.youtube.com/feeds/videos.xml?channel_id='+channel_id)); out=[]
        for e in root.findall('a:entry', NS):
            title=e.findtext('a:title', default='', namespaces=NS); link_el=e.find('a:link', NS); link=link_el.attrib.get('href','') if link_el is not None else ''
            pub=e.findtext('a:published', default='', namespaces=NS); vid=e.findtext('yt:videoId', default='', namespaces=NS)
            out.append({'title':title,'url':link,'published':pub,'video_id':vid,'thumbnail':'https://i.ytimg.com/vi/'+vid+'/hqdefault.jpg' if vid else ''})
        return out
    except Exception as e:
        print('YouTube:', e)
        try: return json.loads((ROOT/'data/youtube.json').read_text(encoding='utf8'))
        except Exception: return []


def nav_html():
    parts=[]
    for x,u in NAV:
        extra=' target="_blank" rel="noopener"' if u.startswith('http') else ''
        parts.append(f'<a href="{H.escape(u,quote=True)}"{extra}>{H.escape(x)}</a>')
    return ''.join(parts)


def sync_nav(s):
    nav=s.find('nav', class_='nav')
    if not nav: return
    wrap=nav.find(class_='wrap')
    if not wrap: return
    wrap.clear(); frag=BeautifulSoup(nav_html(),'html.parser')
    for node in list(frag.contents): wrap.append(node)


def page_shell(title, description, content):
    t=title[0] if isinstance(title,tuple) else title
    canonical=title[1] if isinstance(title,tuple) else ''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{H.escape(description,quote=True)}"><link rel="canonical" href="https://lextalk.legal{canonical}">
<title>{H.escape(t)} | Lex Talk Legal</title>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3161673810996421" crossorigin="anonymous"></script>
<style data-embedded="lex-talk-legal">{CSS}</style></head><body><div class="top"></div>
<div class="utility"><div class="wrap"><div class="live-info"><span class="dot">●</span><span id="dateLabel">--</span><span>|</span><span id="timeLabel">--:--:-- IST</span><span>|</span><span>New Delhi, India</span></div><div class="controls"><button class="control" id="langBtn">हिन्दी</button><button class="control" id="themeBtn">☾ Dark</button></div></div></div>
<header class="masthead"><a href="/" aria-label="Lex Talk Legal Home"><img src="{LOGO}" alt="Lex Talk Legal"></a></header>
<nav class="nav"><div class="wrap">{nav_html()}</div></nav>{content}
<footer><div class="footergrid"><div><h3>Lex Talk Legal</h3><p>Law Simplified for Everyone.<br>Digital Legal News &amp; Legal Education Platform.</p><p>Adv. Gagann Jha, Advocate, Supreme Court of India<br>LEXBOTICS AI MEDIA LLP</p></div><div><h3>Utilities</h3><ul><li><a href="/courtrooms/">Courtrooms / VC</a></li><li><a href="/case-status/">Case Status</a></li><li><a href="/videos/">Latest Videos</a></li><li><a href="/category/drt-drat/">DRT / DRAT</a></li></ul></div><div><h3>Connect</h3><ul><li><a href="https://www.youtube.com/@lextalklegal" target="_blank" rel="noopener">YouTube</a></li><li><a href="https://www.instagram.com/lex_talk_legal" target="_blank" rel="noopener">Instagram</a></li><li><a href="https://x.com/Lex_Talk_Legal" target="_blank" rel="noopener">X</a></li><li><a href="https://in.linkedin.com/company/lextalklegal" target="_blank" rel="noopener">LinkedIn</a></li><li><a href="https://t.me/lextalklegal" target="_blank" rel="noopener">Telegram</a></li></ul></div><div><h3>Contact &amp; Legal</h3><p>+91-8368268507<br>+91-9318445957<br>office.lextalklegal@gmail.com</p><ul><li><a href="/privacy-policy.html">Privacy</a></li><li><a href="/terms-of-use.html">Terms</a></li><li><a href="/disclaimer.html">Disclaimer</a></li><li><a href="/editorial-policy.html">Editorial Policy</a></li><li><a href="/copyright-policy.html">Copyright Policy</a></li><li><a href="/corrections-grievance.html">Corrections &amp; Grievance</a></li><li><a href="/ai-content-policy.html">AI Content Policy</a></li></ul></div></div><div class="copy">© 2026 LEXBOTICS AI MEDIA LLP | Lex Talk Legal | For Educational &amp; Informational Use Only</div></footer>
<div id="google_translate_element" aria-hidden="true"></div><script data-embedded="lex-talk-legal">{JS}</script></body></html>'''


def article(a):
    im=f'<img class="article-hero" src="{H.escape(a["image"],quote=True)}" alt="">' if a['image'] else ''
    body=f'''<main class="article-wrap"><div class="meta">{H.escape(a["category"])} · {H.escape(a["published"][:10])}</div><h1>{H.escape(a["title"])}</h1><div class="article-meta">Lex Talk Legal · <a href="{H.escape(a["source_url"],quote=True)}" target="_blank" rel="noopener">Original Blogger post</a></div>{im}<div class="article-body">{a["content"]}</div><div class="notice">For educational and informational use. Verify important legal facts, orders and case status from the concerned official source.</div></main>'''
    return page_shell((a['title'],a['url']),a['excerpt'],body)


def article_card(a):
    image=f'<div class="cardimg"><img src="{H.escape(a["image"],quote=True)}" alt="" loading="lazy"></div>' if a.get('image') else '<div class="thumb">LEGAL NEWS</div>'
    return f'<article class="card">{image}<div class="meta">{H.escape(a["category"])} · {H.escape(a["published"][:10])}</div><h3><a href="{a["url"]}">{H.escape(a["title"])}</a></h3><p>{H.escape(a["excerpt"])}</p></article>'


def video_card(v):
    thumb=H.escape(v.get('thumbnail',''),quote=True); title=H.escape(v.get('title','Lex Talk Legal')); date=H.escape(v.get('published','')[:10]); url=H.escape(v.get('url','https://www.youtube.com/@lextalklegal'),quote=True)
    visual = f'<img src="{thumb}" alt="" loading="lazy">' if thumb else '<div class="yt-mark">▶</div>'
    return f'<article class="yt-card"><a href="{url}" target="_blank" rel="noopener"><div class="video-thumb">{visual}<span class="play">▶</span></div></a><div class="meta">{date}</div><h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3><a class="button redbtn" href="{url}" target="_blank" rel="noopener">Watch on YouTube</a></article>'


def category_matches(a,key):
    labels={str(x).strip().lower() for x in a.get('labels',[])}; title=a.get('title','').lower(); _,terms=CATEGORY_MAP[key]
    return bool(labels & terms) or any(t in title for t in terms)


def write_category_pages(arts):
    for key,(name,_) in CATEGORY_MAP.items():
        items=[a for a in arts if category_matches(a,key)]; cards=''.join(article_card(a) for a in items[:30]) or '<div class="empty">No stories published in this section yet. Publish a Blogger post with the appropriate label and the next automated sync will update this page.</div>'
        content=f'<main class="utility-page"><div class="utility-kicker">LEX TALK LEGAL</div><h1>{H.escape(name)}</h1><p class="lead">Latest Lex Talk Legal stories in this section are synced automatically from Blogger.</p><div class="grid">{cards}</div></main>'
        p=ROOT/'category'/key/'index.html'; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(page_shell((name,f'/category/{key}/'),f'Lex Talk Legal — {name} news, updates and explainers.',content),encoding='utf8')


def write_videos_page(videos):
    cards=''.join(video_card(v) for v in videos[:30]) or '<div class="empty">No YouTube videos were returned in the latest sync.</div>'
    content=f'<main class="utility-page"><div class="utility-kicker">LEX TALK LEGAL</div><h1>LATEST VIDEOS</h1><p class="lead">Latest Lex Talk Legal videos are synced automatically from YouTube.</p><div class="yt-grid">{cards}</div></main>'
    (ROOT/'videos').mkdir(exist_ok=True); (ROOT/'videos/index.html').write_text(page_shell(('Latest Videos','/videos/'),'Latest Lex Talk Legal videos, legal news and explainers.',content),encoding='utf8')


def button(label,url,kind='official'):
    return f'<a class="link-button {kind}" href="{H.escape(url,quote=True)}" target="_blank" rel="noopener">{H.escape(label)}</a>'


def utility_card(icon,title,text,links):
    links_html=''.join(button(label,url,kind) for label,url,kind in links)
    return f'<article class="utility-card court-card"><div><div class="court-icon">{icon}</div><h3>{H.escape(title)}</h3><p>{H.escape(text)}</p></div><div class="card-actions">{links_html}</div></article>'


def _load_vc_data():
    try: return json.loads(VC_DATA_PATH.read_text(encoding='utf8'))
    except Exception: return {}


def _safe_url(u):
    if not u: return ''
    try:
        p=urllib.parse.urlparse(u)
        if p.scheme.lower()!='https' or not p.netloc: return ''
        host=p.netloc.lower().split(':')[0]
        if 'onecourt.in' in host: return ''
        return u
    except Exception: return ''


def _is_direct_vc(u):
    u=_safe_url(u)
    if not u: return False
    host=urllib.parse.urlparse(u).netloc.lower().split(':')[0]
    return any(host==d or host.endswith('.'+d) for d in DIRECT_VC_DOMAINS)


def _clean_vc_label(label):
    label=re.sub(r'\s+',' ',(label or '')).strip(' |:-')
    label=re.sub(r'\[?Join VC\]?\s*', '', label, flags=re.I).strip(' |:-')
    label=re.sub(r'https?://\S+','',label).strip(' |:-')
    return label[:140]


def _dedupe_items(items):
    out=[]; seen=set()
    for x in items or []:
        if not isinstance(x,dict): continue
        u=_safe_url(x.get('url',''))
        if not _is_direct_vc(u): continue
        label=_clean_vc_label(x.get('label',''))
        key=(label.lower(),u)
        if key in seen: continue
        seen.add(key); out.append({'label':label,'url':u})
    return out


def _fallback_label_from_context(txt):
    lines=[re.sub(r'\s+',' ',z).strip() for z in (txt or '').splitlines()]
    banned=('join vc','verify against','information purpose','clicking join','i confirm','applicable laws','cancel','direct public vc','vc link not available')
    for z in lines:
        zl=z.lower()
        if not z or len(z)<2 or any(b in zl for b in banned): continue
        if re.match(r'^(courtrooms?|virtual hearings?)$',z,re.I): continue
        if re.match(r'^[A-Z0-9 .&()\-/,]+$',z) and len(z)<120: return z
        if len(z)<140: return z
    return ''


def extract_onecourt_vc():
    old=_load_vc_data()
    data={}
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        print('OneCourt extraction unavailable (Playwright import):', e)
        return old

    HOST='https://onecourt.in'
    def norm(h): return urllib.parse.urljoin(HOST,h) if h else ''

    def dialog_text(page):
        selectors=['[role="dialog"]:visible','dialog:visible','.modal:visible','.popup:visible','[class*="modal"]:visible']
        for sel in selectors:
            try:
                loc=page.locator(sel)
                if loc.count():
                    txt=loc.last.inner_text(timeout=800)
                    if txt and txt.strip(): return txt.strip()
            except Exception: pass
        return ''

    def dialog_direct_links(page):
        candidates=[]
        selectors=['[role="dialog"]:visible a','dialog:visible a','.modal:visible a','.popup:visible a','[class*="modal"]:visible a']
        for sel in selectors:
            try:
                loc=page.locator(sel)
                for i in range(min(loc.count(),20)):
                    a=loc.nth(i); href=a.get_attribute('href') or ''; txt=(a.inner_text() or '').strip()
                    if _is_direct_vc(norm(href)):
                        candidates.append((norm(href),txt))
            except Exception: pass
        # If the modal uses an anchor elsewhere in the page after opening, look for visible direct VC anchors.
        if not candidates:
            try:
                loc=page.locator('a:visible')
                for i in range(min(loc.count(),300)):
                    a=loc.nth(i); href=a.get_attribute('href') or ''; txt=(a.inner_text() or '').strip()
                    if _is_direct_vc(norm(href)) and ('join vc' in txt.lower() or 'hearing' in txt.lower() or 'webex' in txt.lower() or 'meet' in txt.lower()):
                        candidates.append((norm(href),txt))
            except Exception: pass
        return candidates

    def label_for(page, base_context, page_title='', supreme=False):
        txt=dialog_text(page)
        # Supreme Court: explicitly retain courtroom number from modal heading.
        for source in [txt, base_context, page_title]:
            m=re.search(r'Court\s*(?:No\.?|Number)\s*[:\-]?\s*(\d+)', source or '', re.I)
            if m: return f'Court No. {m.group(1)}'
            m=re.search(r'(Registrar(?:\'s)? Court(?:\s*[-–]?\s*\d+)?)', source or '', re.I)
            if m: return re.sub(r'\s+',' ',m.group(1)).strip()
        # Other courts/tribunals: use a meaningful first line from the modal, then card context.
        for source in [txt, base_context, page_title]:
            z=_fallback_label_from_context(source)
            if z: return z
        return ''

    def close_modal(page):
        for sel in ['button','[role="button"]']:
            try:
                loc=page.locator(sel).filter(has_text=re.compile(r'^(Cancel|Close|×)$',re.I))
                if loc.count(): loc.last.click(timeout=800); page.wait_for_timeout(100); return
            except Exception: pass
        try: page.keyboard.press('Escape'); page.wait_for_timeout(100)
        except Exception: pass

    def extract_on_page(page, page_title='', supreme=False):
        out=[]
        # Direct anchors and buttons. We click buttons to resolve popup/modal destinations and labels.
        elements=page.locator('a,button,[role="button"]')
        count=min(elements.count(),600)
        for i in range(count):
            try:
                el=elements.nth(i)
                if not el.is_visible(): continue
                txt=(el.inner_text() or el.text_content() or '').strip()
                href=el.get_attribute('href') or ''
                data_url=el.get_attribute('data-url') or el.get_attribute('data-href') or ''
                onclick=el.get_attribute('onclick') or ''
                direct_candidates=[norm(href),norm(data_url)]
                mm=re.search(r'https://[^\"\'\s)]+',onclick)
                if mm: direct_candidates.append(norm(mm.group(0)))
                direct=next((u for u in direct_candidates if _is_direct_vc(u)), '')
                base=''
                try:
                    base=el.locator('xpath=ancestor::*[self::article or self::tr or contains(@class,"card") or contains(@class,"court")][1]').inner_text(timeout=600)
                except Exception: base=txt
                is_join=('join vc' in txt.lower()) or ('join vc' in (el.get_attribute('aria-label') or '').lower()) or ('join vc' in onclick.lower())
                if direct:
                    lab=label_for(page,base,page_title,supreme) or _clean_vc_label(txt) or 'VC Link'
                    out.append({'label':lab,'url':direct})
                    continue
                if not is_join: continue
                # Resolve via popup/modal.
                try:
                    el.click(timeout=1500)
                    page.wait_for_timeout(220)
                    for u, modal_txt in dialog_direct_links(page):
                        lab=label_for(page,base,page_title,supreme) or _clean_vc_label(modal_txt) or _clean_vc_label(txt) or 'VC Link'
                        out.append({'label':lab,'url':u})
                except Exception:
                    pass
                finally:
                    close_modal(page)
            except Exception:
                continue
        return _dedupe_items(out)

    def load(page,url):
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(2800)
        try:
            body=page.locator('body').inner_text(timeout=1000)
            if 'Unpacking' in body: page.wait_for_timeout(4500)
        except Exception: pass

    pages=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':1200}, user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) LexTalkLegalBot/2.0')
        page=context.new_page()
        try:
            # Supreme Court
            load(page,ONECOURT_SC_VC)
            title=''
            try: title=page.locator('h1').first.inner_text().strip()
            except Exception: pass
            sc_links=extract_on_page(page,title,True)
            if sc_links: data['supreme_court']=sc_links

            # Root VC directory: discover all directory pages, then extract court-wise items.
            load(page,ONECOURT_ROOT_VC)
            hrefs=page.locator('a[href]').evaluate_all('els => els.map(a=>a.href)')
            for h in hrefs:
                if h.startswith(HOST) and '/vc-links/' in h and h not in pages: pages.append(h)
            for _,u in DELHI_DISTRICT_VC:
                if u not in pages: pages.append(u)
            for u in [ONECOURT_NCLT_VC,ONECOURT_NCLAT_VC]:
                if u not in pages: pages.append(u)

            for u in pages:
                try: load(page,u)
                except Exception as e:
                    print('OneCourt page failed:',u,e); continue
                try: title=page.locator('h1').first.inner_text().strip()
                except Exception: title=''
                links=extract_on_page(page,title,False)
                low=(title or u).lower(); ulow=u.lower()
                if 'districtcourts' in ulow:
                    district_name=next((n for n,du in DELHI_DISTRICT_VC if du==u), title or u)
                    if links: data.setdefault('delhi_district',{})[district_name]=links
                elif 'nclt' in low or 'nclt' in ulow:
                    matched=None
                    for bench in COURTS['nclt']:
                        stem=bench.lower().replace('principal bench / ','').replace('bench','').strip()
                        if stem and stem in low: matched=bench; break
                    data.setdefault('nclt',{})[f'NCLT — {matched or title or "Bench"}']=links
                elif 'nclat' in low or 'nclat' in ulow:
                    matched=None
                    for bench in COURTS['nclat']:
                        stem=bench.lower().replace('principal bench / ','').replace('bench','').strip()
                        if stem and stem in low: matched=bench; break
                    data.setdefault('nclat',{})[f'NCLAT — {matched or title or "Bench"}']=links
                elif 'drat' in low or 'drat' in ulow or 'debt recovery appellate' in low:
                    matched=None
                    for city in COURTS['drat']:
                        if city.lower() in low: matched=city; break
                    data.setdefault('drat',{})[f'DRAT — {matched or title or "Tribunal"}']=links
                elif 'drt' in low or '/drt/' in ulow or 'debt recovery tribunal' in low:
                    matched=None
                    for city in COURTS['drt']:
                        if city.lower() in low: matched=city; break
                    data.setdefault('drt',{})[f'DRT — {matched or title or "Tribunal"}']=links
                else:
                    matched=None
                    for name,_ in COURTS['high_courts']:
                        stem=name.lower().replace(' high court','')
                        if name.lower() in low or stem in low: matched=name; break
                    if matched: data.setdefault('high_courts',{})[matched]=links
        finally:
            browser.close()

    # Keep prior working data only where a page could not be refreshed, but always sanitize it.
    if not data:
        data=old
    else:
        for key,val in old.items():
            if key not in data: data[key]=val
            elif isinstance(val,dict):
                for k,v in val.items():
                    if k not in data[key]: data[key][k]=v

    def sanitise(obj):
        if isinstance(obj,list): return _dedupe_items(obj)
        if isinstance(obj,dict): return {k:sanitise(v) for k,v in obj.items() if isinstance(v,(dict,list))}
        return obj
    data=sanitise(data)
    VC_DATA_PATH.parent.mkdir(exist_ok=True)
    VC_DATA_PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    total=sum(len(v) if isinstance(v,list) else sum(len(x) for x in v.values() if isinstance(x,list)) if isinstance(v,dict) else 0 for v in data.values())
    print('OneCourt direct VC destinations extracted/refreshed:', total)
    return data


def vc_button(item, kind='link'):
    label=_clean_vc_label(item.get('label','')) or 'VC Link'
    url=_safe_url(item.get('url',''))
    if kind=='link' and _is_direct_vc(url):
        return f'<button class="vc-link" type="button" data-vc-title="{H.escape(label,quote=True)}" data-vc-url="{H.escape(url,quote=True)}"><span class="vc-icon">↗</span><span>{H.escape(label)}</span><small>Open VC</small></button>'
    return f'<button class="vc-link vc-unavailable" type="button" data-vc-title="{H.escape(label or "This court",quote=True)}"><span class="vc-icon">i</span><span>{H.escape(label or "VC Link")}</span><small>Not available</small></button>'


def write_courtrooms_page(vc_data=None):
    vc_data=vc_data or _load_vc_data(); sc=_dedupe_items(vc_data.get('supreme_court',[])); hcs=vc_data.get('high_courts',{})
    drt_vc=vc_data.get('drt',{}); drat_vc=vc_data.get('drat',{}); nclt_vc=vc_data.get('nclt',{}); nclat_vc=vc_data.get('nclat',{}); delhi_vc=vc_data.get('delhi_district',{})

    def card(title, icon, desc, links=None, official=''):
        links=_dedupe_items(links or [])
        if links:
            if len(links)==1:
                vc_html=vc_button(links[0])
            else:
                vc_html='<div class="vc-directory-list">'+''.join(vc_button(x) for x in links)+'</div>'
        else:
            vc_html=vc_button({'label':'VC Link not available'})
        official_html=button('Official Court',''+official,'official') if official else ''
        return f'<article class="utility-card court-card vc-court-card"><div><div class="court-icon">{icon}</div><div class="vc-card-kicker">PUBLIC VC ACCESS</div><h3>{H.escape(title)}</h3><p>{H.escape(desc)}</p>{vc_html}</div><div class="card-actions">{official_html}</div></article>'

    sc_cards=''.join(card(x.get('label') or 'Supreme Court VC','⚖️','Direct public VC destination. Verify the courtroom and the day’s cause list before joining.',[x]) for x in sc)
    if not sc_cards:
        sc_cards=card('Supreme Court VC','⚖️','No direct VC destination was available in the latest public sync. Verify the official cause list / court website.',[], 'https://www.sci.gov.in/')

    hc_cards=''
    for name,url in COURTS['high_courts']:
        items=hcs.get(name,[]) if isinstance(hcs,dict) else []
        hc_cards+=card(name,'🏛️','Public VC destinations where available; verify against the current cause list.',items,url)

    delhi_cards=''
    district_names=[]
    for configured_name, u in DELHI_DISTRICT_VC:
        district_names.append(configured_name)
        items=delhi_vc.get(configured_name,[]) if isinstance(delhi_vc,dict) else []
        delhi_cards+=card(configured_name,'🎥','Court-wise public VC links are listed individually where available.',items,'https://delhidistrictcourts.nic.in/')
    if isinstance(delhi_vc,dict):
        for name,items in delhi_vc.items():
            if name not in district_names: delhi_cards+=card(name,'🎥','Public VC directory entry.',items,'https://delhidistrictcourts.nic.in/')

    def grouped_cards(data,prefix,icon,official_url,desc):
        out=''; names=COURTS[prefix.lower()]
        for name in names:
            key=f'{prefix.upper()} — {name}'; items=data.get(key,data.get(name,[])) if isinstance(data,dict) else []
            out+=card(key,icon,desc,items,official_url)
        return out

    content=f'''<main class="utility-page directory-page"><div class="utility-kicker">LEGAL UTILITY</div><h1>COURTROOMS &amp; VIRTUAL HEARINGS</h1><p class="lead">Open a public courtroom / VC destination without routing through OneCourt. Where a court-wise or courtroom-wise destination is available, it is shown separately.</p><div class="directory-alert"><strong>Before joining:</strong> VC details can change. Verify the court number, date and current VC details against the concerned court / tribunal cause list. Where a direct public VC destination is unavailable, refer to the cause list or contact the concerned court office / courtroom master / reader.</div>
<section class="court-section"><div class="section-head"><h2>Supreme Court of India</h2><div class="section-tools">{len(sc)} direct public courtroom destination(s) refreshed</div></div><div class="card-grid">{sc_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>High Courts</h2></div><div class="card-grid">{hc_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>Delhi District Courts</h2></div><div class="card-grid">{delhi_cards or card('Delhi District Courts','🎥','Use the official cause list / public VC information.',[],'https://delhidistrictcourts.nic.in/')}</div></section>
<section class="court-section"><div class="section-head"><h2>Debt Recovery Tribunals (DRT)</h2></div><div class="card-grid">{grouped_cards(drt_vc,'drt','⚖️',DRT_EFILING,'Public VC destination where available. Verify the daily cause list before joining.')}</div></section>
<section class="court-section"><div class="section-head"><h2>Debt Recovery Appellate Tribunals (DRAT)</h2></div><div class="card-grid">{grouped_cards(drat_vc,'drat','⚖️',DRT_EFILING,'Public VC destination where available. Verify the daily cause list before joining.')}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLT</h2></div><div class="card-grid">{grouped_cards(nclt_vc,'nclt','🏢','https://nclt.gov.in/','Public VC destination where available. Verify the bench-wise cause list.')}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLAT</h2></div><div class="card-grid">{grouped_cards(nclat_vc,'nclat','🏢','https://nclat.nic.in/','Public VC destination where available. Verify the bench-wise cause list.')}</div></section></main>'''
    (ROOT/'courtrooms').mkdir(exist_ok=True); (ROOT/'courtrooms/index.html').write_text(page_shell(('Courtrooms & VC Links','/courtrooms/'),'Lex Talk Legal direct public courtroom and virtual hearing links for Indian courts and tribunals.',content),encoding='utf8')


def write_case_status_page():
    hc_cards=''.join(utility_card('🔎',name,'Open the official court website or the public eCourts case-status service.',[('Court Website',url,'official'),('Case Status',CASE_STATUS_GENERIC_HC,'official')]) for name,url in COURTS['high_courts'])
    drt_cards=''.join(utility_card('🔎',f'DRT — {city}','Official DRT e-filing / case-service entry point.',[('DRT Case Services',DRT_EFILING,'official')]) for city in COURTS['drt'])
    drat_cards=''.join(utility_card('🔎',f'DRAT — {city}','Official DRT e-filing / case-service entry point.',[('DRAT / DRT Portal',DRT_EFILING,'official')]) for city in COURTS['drat'])
    nclt_cards=''.join(utility_card('🔎',f'NCLT — {bench}','Official NCLT case-status service with bench selection and access controls.',[('Case Status','https://efiling.nclt.gov.in/nclt/public/case_status.php','official'),('Case History','https://efiling.nclt.gov.in/casehistorybeforeloginmenutrue.drt','official')]) for bench in COURTS['nclt'])
    nclat_cards=''.join(utility_card('🔎',name,'Official NCLAT public case / listing service.',[('Case Status','https://nclat.nic.in/display-board/cases','official'),('e-Filing Portal','https://efiling.nclat.gov.in/mainPage.drt','official')]) for name in COURTS['nclat'])
    content=f'''<main class="utility-page directory-page"><div class="utility-kicker">LEGAL UTILITY</div><h1>CASE STATUS</h1><p class="lead">Choose the court or tribunal and open the relevant official public case-status service.</p><div class="directory-alert"><strong>Official portal note:</strong> some services use CAPTCHA or other access controls. This site links to the public portal and does not bypass those controls.</div>
<section class="court-section"><div class="section-head"><h2>Supreme Court of India</h2></div><div class="card-grid">{utility_card('🔎','Supreme Court Case Status','Official Supreme Court case-status and court-services entry point.', [('Case Status','https://www.sci.gov.in/case-status-court/','official'),('Supreme Court Website','https://www.sci.gov.in/','official')])}</div></section>
<section class="court-section"><div class="section-head"><h2>High Courts</h2></div><div class="card-grid">{hc_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>DRT</h2></div><div class="card-grid">{drt_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>DRAT</h2></div><div class="card-grid">{drat_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLT</h2></div><div class="card-grid">{nclt_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLAT</h2></div><div class="card-grid">{nclat_cards}</div></section></main>'''
    (ROOT/'case-status').mkdir(exist_ok=True); (ROOT/'case-status/index.html').write_text(page_shell(('Case Status','/case-status/'),'Lex Talk Legal official public case-status entry points for Indian courts and tribunals.',content),encoding='utf8')


def sync_homepage(arts,videos):
    p=ROOT/'index.html'
    if not p.exists(): return
    s=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser'); sync_nav(s)
    style=s.find('style',{'data-embedded':'lex-talk-legal'}); old=s.find('script',{'data-embedded':'lex-talk-legal'})
    if style: style.string=CSS
    if old: old.string=JS
    if not s.find(id='google_translate_element'):
        holder=s.new_tag('div',id='google_translate_element'); holder['aria-hidden']='true';
        if s.body: s.body.append(holder)
    lg=s.find(id='latestGrid')
    if lg:
        lg.clear(); latest=arts[:8]
        if latest:
            for a in latest: lg.append(BeautifulSoup(article_card(a),'html.parser'))
        else: lg.append(BeautifulSoup('<div class="empty">No Blogger stories returned in the latest sync.</div>','html.parser'))
    vg=s.find(id='videoGrid')
    if vg:
        vg.clear(); latest_videos=videos[:6]
        if latest_videos:
            for v in latest_videos: vg.append(BeautifulSoup(video_card(v),'html.parser'))
        else: vg.append(BeautifulSoup('<div class="empty">No YouTube videos returned in the latest sync.</div>','html.parser'))
    p.write_text(str(s),encoding='utf8')


def refresh_static_pages():
    for p in ROOT.rglob('*.html'):
        rel=p.relative_to(ROOT).as_posix()
        if rel.startswith('article/') or rel in {'videos/index.html','courtrooms/index.html','case-status/index.html'}: continue
        try: s=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
        except Exception: continue
        sync_nav(s)
        style=s.find('style',{'data-embedded':'lex-talk-legal'}); script=s.find('script',{'data-embedded':'lex-talk-legal'})
        if style: style.string=CSS
        if script: script.string=JS
        p.write_text(str(s),encoding='utf8')


def main():
    ap=ROOT/'data/articles.json'; arts=blogger()
    if not arts:
        try: arts=json.loads(ap.read_text(encoding='utf8'))
        except Exception: arts=[]
    arts.sort(key=lambda x:x.get('published',''),reverse=True); ap.parent.mkdir(exist_ok=True); ap.write_text(json.dumps(arts,ensure_ascii=False,indent=2),encoding='utf8')
    videos=youtube(); videos.sort(key=lambda x:x.get('published',''),reverse=True); (ROOT/'data/youtube.json').write_text(json.dumps(videos,ensure_ascii=False,indent=2),encoding='utf8')
    d=ROOT/'article'; d.mkdir(exist_ok=True)
    for f in d.glob('*.html'): f.unlink()
    for a in arts: (d/(slug(a['title'])+'.html')).write_text(article(a),encoding='utf8')
    vc_data=extract_onecourt_vc(); write_category_pages(arts); write_videos_page(videos); write_courtrooms_page(vc_data); write_case_status_page(); sync_homepage(arts,videos); refresh_static_pages()
    urls=['/','/courtrooms/','/case-status/','/videos/']+[f'/category/{k}/' for k in CATEGORY_MAP]+[a['url'] for a in arts]
    now=datetime.now(timezone.utc).date().isoformat(); xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'; xml+=''.join(f'<url><loc>https://lextalk.legal{u}</loc><lastmod>{now}</lastmod></url>' for u in dict.fromkeys(urls))+'</urlset>'; (ROOT/'sitemap.xml').write_text(xml,encoding='utf8')
    print(f'Synced {len(arts)} Blogger articles and {len(videos)} YouTube videos; refreshed courtrooms and case-status directories.')

if __name__=='__main__': main()
