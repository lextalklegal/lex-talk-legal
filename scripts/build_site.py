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

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'LexTalkLegalBot/1.0'})
    return urllib.request.urlopen(req, timeout=30).read()

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
    wrap.clear()
    frag=BeautifulSoup(nav_html(),'html.parser')
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
    try:
        return json.loads(VC_DATA_PATH.read_text(encoding='utf8'))
    except Exception:
        return {}

def _safe_url(u):
    if not u: return ''
    return u if re.match(r'^https?://', u, re.I) else ''

def write_courtrooms_page(vc_data=None):
    vc_data = vc_data or _load_vc_data()
    sc = vc_data.get('supreme_court', [])
    hcs = vc_data.get('high_courts', {})
    drt_vc = vc_data.get('drt', {})
    drat_vc = vc_data.get('drat', {})
    nclt_vc = vc_data.get('nclt', {})
    nclat_vc = vc_data.get('nclat', {})
    delhi_vc = vc_data.get('delhi_district', {})

    def vc_list_html(items, empty_text='VC link not available in the latest sync.'):
        items=[x for x in items if isinstance(x,dict) and _safe_url(x.get('url'))]
        if not items: return f'<div class="vc-empty">{H.escape(empty_text)}</div>'
        return '<div class="vc-link-grid">'+''.join(
            f'<a class="vc-link" href="{H.escape(x["url"],quote=True)}" target="_blank" rel="noopener">{H.escape(x.get("label") or "Join VC")}</a>'
            for x in items)+'</div>'

    def court_vc_card(icon,title,desc,links,official=''):
        actions=''
        if official: actions+=button('Official Court',official,'official')
        return f'<article class="utility-card court-card"><div><div class="court-icon">{icon}</div><h3>{H.escape(title)}</h3><p>{H.escape(desc)}</p>{vc_list_html(links)}</div><div class="card-actions">{actions}</div></article>'

    sc_cards=''.join(court_vc_card('⚖️', x.get('label','Supreme Court VC'), 'Direct public VC joining link extracted from the current rendered directory.', [x]) for x in sc)
    if not sc_cards:
        sc_cards = court_vc_card('⚖️','Supreme Court VC','Direct VC links are refreshed from the current public directory. Verify the courtroom against the Supreme Court cause list.',[], 'https://www.sci.gov.in/')

    hc_cards=''
    for name, url in COURTS['high_courts']:
        items=hcs.get(name,[])
        hc_cards += court_vc_card('🏛️', name, 'Official court website plus direct public VC joining links refreshed from the rendered directory.', items, url)

    def grouped_cards(data, prefix, icon, official_url=None):
        out=''
        if prefix=='DRT': names=COURTS['drt']
        elif prefix=='DRAT': names=COURTS['drat']
        elif prefix=='NCLT': names=COURTS['nclt']
        else: names=COURTS['nclat']
        for name in names:
            key=f'{prefix} — {name}'
            items=data.get(key, data.get(name, []))
            out += court_vc_card(icon,key,'Direct public VC joining links refreshed from the current public VC directory. Always verify the day’s cause list.', items, official_url or '')
        return out

    delhi_cards=''.join(court_vc_card('🎥', name, 'Direct public Delhi District Court VC links refreshed from the current public directory.', items, 'https://delhidistrictcourts.nic.in/') for name,items in delhi_vc.items())

    content=f'''<main class="utility-page directory-page"><div class="utility-kicker">LEGAL UTILITY</div><h1>COURTROOMS &amp; VIRTUAL HEARINGS</h1><p class="lead">Choose a court or tribunal and open its public courtroom / VC link directly. Lex Talk Legal does not route visitors through the OneCourt website; the public destination URLs are extracted from the rendered directory and published here.</p><div class="directory-alert"><strong>Important:</strong> VC links can change. Before joining, verify the court number, date and current VC details against the concerned court / tribunal cause list. The VC-directory data is informational only.</div>
<section class="court-section"><div class="section-head"><h2>Supreme Court of India</h2></div><div class="card-grid">{sc_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>High Courts</h2></div><div class="card-grid">{hc_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>Delhi District Courts</h2></div><div class="card-grid">{delhi_cards or court_vc_card('🎥','Delhi District Courts','Use the public VC directory data refreshed by the automated sync.',[], 'https://delhidistrictcourts.nic.in/')}</div></section>
<section class="court-section"><div class="section-head"><h2>DRT</h2></div><div class="card-grid">{grouped_cards(drt_vc,'DRT','⚖️',DRT_EFILING)}</div></section>
<section class="court-section"><div class="section-head"><h2>DRAT</h2></div><div class="card-grid">{grouped_cards(drat_vc,'DRAT','⚖️',DRT_EFILING)}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLT</h2></div><div class="card-grid">{grouped_cards(nclt_vc,'NCLT','🏢','https://nclt.gov.in/')}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLAT</h2></div><div class="card-grid">{grouped_cards(nclat_vc,'NCLAT','🏢','https://nclat.nic.in/')}</div></section></main>'''
    (ROOT/'courtrooms').mkdir(exist_ok=True); (ROOT/'courtrooms/index.html').write_text(page_shell(('Courtrooms & VC Links','/courtrooms/'),'Lex Talk Legal direct public courtroom and virtual hearing links for Indian courts and tribunals.',content),encoding='utf8')

def write_case_status_page():
    hc_cards=''.join(utility_card('🔎',name,'Open the official court website or the national eCourts case-status service.',[
        ('Court Website',url,'official'),('Case Status',CASE_STATUS_GENERIC_HC,'official')]) for name,url in COURTS['high_courts'])
    drt_cards=''.join(utility_card('🔎',f'DRT — {city}','Official DRT e-filing / case-service entry point.',[
        ('DRT Case Services',DRT_EFILING,'official')]) for city in COURTS['drt'])
    drat_cards=''.join(utility_card('🔎',f'DRAT — {city}','Official DRT e-filing / case-service entry point.',[
        ('DRAT / DRT Portal',DRT_EFILING,'official')]) for city in COURTS['drat'])
    nclt_cards=''.join(utility_card('🔎',f'NCLT — {bench}','Official NCLT case-status service with bench selection and access controls.',[
        ('Case Status','https://efiling.nclt.gov.in/nclt/public/case_status.php','official'),('Case History','https://efiling.nclt.gov.in/casehistorybeforeloginmenutrue.drt','official')]) for bench in COURTS['nclt'])
    nclat_cards=''.join(utility_card('🔎',name,'Official NCLAT public case / listing service.',[
        ('Case Status','https://nclat.nic.in/display-board/cases','official'),('e-Filing Portal','https://efiling.nclat.gov.in/mainPage.drt','official')]) for name in COURTS['nclat'])
    content=f'''<main class="utility-page directory-page"><div class="utility-kicker">LEGAL UTILITY</div><h1>CASE STATUS</h1><p class="lead">Choose the court or tribunal and open the relevant official public case-status service.</p><div class="directory-alert"><strong>Official portal note:</strong> some services use CAPTCHA or other access controls. This site links to the public portal and does not bypass those controls.</div>
<section class="court-section"><div class="section-head"><h2>Supreme Court of India</h2></div><div class="card-grid">{utility_card('🔎','Supreme Court Case Status','Official Supreme Court case-status and court-services entry point.', [('Case Status','https://www.sci.gov.in/case-status-court/','official'),('Supreme Court Website','https://www.sci.gov.in/','official')])}</div></section>
<section class="court-section"><div class="section-head"><h2>High Courts</h2></div><div class="card-grid">{hc_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>DRT</h2></div><div class="card-grid">{drt_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>DRAT</h2></div><div class="card-grid">{drat_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLT</h2></div><div class="card-grid">{nclt_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLAT</h2></div><div class="card-grid">{nclat_cards}</div></section></main>'''
    (ROOT/'case-status').mkdir(exist_ok=True); (ROOT/'case-status/index.html').write_text(page_shell(('Case Status','/case-status/'),'Lex Talk Legal official public case-status entry points for Indian courts and tribunals.',content),encoding='utf8')

def extract_onecourt_vc():
    data=_load_vc_data()
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        print('OneCourt extraction unavailable (Playwright import):', e)
        return data

    HOST='https://onecourt.in'
    def norm(h):
        return urllib.parse.urljoin(HOST,h) if h else ''
    def is_direct(h):
        if not h or 'onecourt.in' in h.lower(): return False
        return any(x in h.lower() for x in ['webex.com','teams.live.com','teams.microsoft.com','meet.google.com','zoom.us','vcourts.gov.in'])

    def extract_on_page(page):
        rows=page.locator('a,button,[role="button"]').evaluate_all('''els => els.map(el=>({tag:el.tagName,text:(el.innerText||el.textContent||'').trim(),href:el.getAttribute('href')||'',dataUrl:el.getAttribute('data-url')||'',dataHref:el.getAttribute('data-href')||'',onclick:el.getAttribute('onclick')||'',context:(el.closest('article,tr,li,.card,.court-card')?.innerText||el.parentElement?.innerText||'').trim()}))''')
        out=[]
        for r in rows:
            if 'join vc' not in r.get('text','').lower(): continue
            candidates=[r.get('href',''),r.get('dataUrl',''),r.get('dataHref','')]
            m=re.search(r"https?://[^'\\\"\\s)]+",r.get('onclick',''))
            if m: candidates.append(m.group(0))
            url=next((norm(c) for c in candidates if is_direct(norm(c))), '')
            if url:
                ctx=(r.get('context') or r.get('text') or 'Join VC').split('\\n')
                label=next((z.strip() for z in ctx if z.strip() and 'join vc' not in z.lower()), 'Join VC')
                out.append({'label':label[:120],'url':url})
        buttons=page.locator('button,[role="button"]').filter(has_text=re.compile('Join VC',re.I))
        count=buttons.count()
        for i in range(min(count,300)):
            try:
                b=buttons.nth(i)
                if b.get_attribute('disabled'): continue
                b.click(timeout=1500)
                page.wait_for_timeout(100)
                links=page.locator('a').filter(has_text=re.compile('Join VC hearing link',re.I))
                if links.count():
                    u=links.last.get_attribute('href') or ''
                    u=norm(u)
                    if is_direct(u):
                        ctx=(b.inner_text() or '').strip() or 'Join VC'
                        if not any(x.get('url')==u for x in out): out.append({'label':ctx,'url':u})
                canc=page.locator('button').filter(has_text=re.compile('Cancel|×',re.I))
                if canc.count(): canc.last.click(timeout=1000)
            except Exception:
                continue
        return out

    def load(page,url):
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(2500)
        try:
            if 'Unpacking' in page.locator('body').inner_text(): page.wait_for_timeout(4000)
        except Exception: pass

    pages=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(user_agent='Mozilla/5.0 LexTalkLegal VC Directory Sync')
        page=context.new_page()
        try:
            load(page,ONECOURT_SC_VC)
            links=extract_on_page(page)
            if links: data['supreme_court']=links
            load(page,ONECOURT_ROOT_VC)
            hrefs=page.locator('a[href]').evaluate_all('els => els.map(a=>a.href)')
            for h in hrefs:
                if h.startswith(HOST) and '/vc-links/' in h and h not in pages: pages.append(h)
            for _,u in DELHI_DISTRICT_VC:
                if u not in pages: pages.append(u)
            for u in [ONECOURT_NCLT_VC,ONECOURT_NCLAT_VC]:
                if u not in pages: pages.append(u)
            for u in pages:
                try:
                    load(page,u); links=extract_on_page(page)
                except Exception as e:
                    print('OneCourt page failed:',u,e); continue
                try: title=page.locator('h1').first.inner_text().strip()
                except Exception: title=''
                text_title=title or u
                low=text_title.lower()
                ulow=u.lower()
                if 'nclt' in low or 'nclt' in ulow:
                    matched=None
                    for bench in COURTS['nclt']:
                        stem=bench.lower().replace('principal bench / ','').replace('bench','').strip()
                        if stem and stem in low:
                            matched=bench; break
                    data.setdefault('nclt',{})[f'NCLT — {matched or text_title}']=links
                elif 'nclat' in low or 'nclat' in ulow:
                    matched=None
                    for bench in COURTS['nclat']:
                        stem=bench.lower().replace('principal bench / ','').replace('bench','').strip()
                        if stem and stem in low:
                            matched=bench; break
                    data.setdefault('nclat',{})[f'NCLAT — {matched or text_title}']=links
                elif 'districtcourts' in ulow:
                    data.setdefault('delhi_district',{})[text_title]=links
                elif 'drat' in low or 'drat' in ulow or 'debt recovery appellate' in low:
                    matched=None
                    for city in COURTS['drat']:
                        if city.lower() in low: matched=city; break
                    data.setdefault('drat',{})[f'DRAT — {matched or text_title}']=links
                elif 'drt' in low or '/drt/' in ulow or 'debt recovery tribunal' in low:
                    matched=None
                    for city in COURTS['drt']:
                        if city.lower() in low: matched=city; break
                    data.setdefault('drt',{})[f'DRT — {matched or text_title}']=links
                else:
                    matched=None
                    for name,_ in COURTS['high_courts']:
                        lowname=name.lower()
                        stem=lowname.replace(' high court','')
                        if lowname in low or stem in low:
                            matched=name; break
                    if matched: data.setdefault('high_courts',{})[matched]=links
        finally:
            browser.close()
    VC_DATA_PATH.parent.mkdir(exist_ok=True)
    VC_DATA_PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    total=0
    for v in data.values():
        if isinstance(v,list): total += len(v)
        elif isinstance(v,dict): total += sum(len(x) for x in v.values() if isinstance(x,list))
    print('OneCourt direct VC destinations extracted:', total)
    return data

def sync_homepage(arts,videos):
    p=ROOT/'index.html'
    if not p.exists(): return
    s=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
    sync_nav(s)
    style=s.find('style',{'data-embedded':'lex-talk-legal'})
    if style: style.string=CSS
    old=s.find('script',{'data-embedded':'lex-talk-legal'})
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
    skip={'index.html'}
    for p in ROOT.rglob('*.html'):
        rel=p.relative_to(ROOT).as_posix()
        if rel.startswith('article/'): continue
        if rel in {'videos/index.html','courtrooms/index.html','case-status/index.html'}: continue
        try: s=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
        except Exception: continue
        sync_nav(s)
        style=s.find('style',{'data-embedded':'lex-talk-legal'}); script=s.find('script',{'data-embedded':'lex-talk-legal'})
        changed=True
        if style: style.string=CSS; changed=True
        if script: script.string=JS; changed=True
        if changed: p.write_text(str(s),encoding='utf8')

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
    write_category_pages(arts); write_videos_page(videos); vc_data=extract_onecourt_vc(); write_courtrooms_page(vc_data); write_case_status_page(); sync_homepage(arts,videos); refresh_static_pages()
    urls=['/','/courtrooms/','/case-status/','/videos/']+[f'/category/{k}/' for k in CATEGORY_MAP]+[a['url'] for a in arts]
    now=datetime.now(timezone.utc).date().isoformat(); xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'; xml+=''.join(f'<url><loc>https://lextalk.legal{u}</loc><lastmod>{now}</lastmod></url>' for u in dict.fromkeys(urls))+'</urlset>'; (ROOT/'sitemap.xml').write_text(xml,encoding='utf8')
    print(f'Synced {len(arts)} Blogger articles and {len(videos)} YouTube videos; refreshed courtrooms and case-status directories.')

if __name__=='__main__': main()
