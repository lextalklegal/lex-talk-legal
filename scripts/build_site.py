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
    ('Explained', '/category/explained/'), ('Courtrooms', '/courtrooms/'),
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

CASE_STATUS_GENERIC_HC = 'https://hcservices.ecourts.gov.in/ecourtindiaHC/index_highcourt.php'
ONECOURT_HC_VC = 'https://onecourt.in/VC_Hearing_Links.html'
ONECOURT_SC_VC = 'https://onecourt.in/Supreme_Court_VC_Hearing_Links.html'
ONECOURT_NCLT_VC = 'https://onecourt.in/vc-links/nclt/NCLT_VC_Hearing_Links.html'

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
    return ''.join(f'<a href="{u}">{H.escape(x)}</a>' for x,u in NAV)

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

def write_courtrooms_page():
    sc_chips=''.join(f'<span class="court-chip">Court No. {i}</span>' for i in range(1,18))+''.join(f'<span class="court-chip">Registrar R-{i}</span>' for i in range(1,3))
    hc_cards=''.join(utility_card('🏛️',name,'Official court website and national eCourts case-status entry point.',[
        ('Official Court',url,'official'),('Case Status',CASE_STATUS_GENERIC_HC,'official'),('VC Directory',ONECOURT_HC_VC,'directory')]) for name,url in COURTS['high_courts'])
    drt_cards=''.join(utility_card('⚖️',f'DRT — {city}','Use the official e-DRT portal to choose the tribunal, case service and current cause list / hearing information.',[
        ('e-DRT Portal','https://drt.etribunals.gov.in/','official'),('DRT Website','https://drt.gov.in/','official')]) for city in COURTS['drt'])
    drat_cards=''.join(utility_card('⚖️',f'DRAT — {city}','Official DRT/DRAT service entry point. Select the concerned tribunal and consult the current listing/cause information.',[
        ('e-DRT Portal','https://drt.etribunals.gov.in/','official'),('DRT Website','https://drt.gov.in/','official')]) for city in COURTS['drat'])
    nclt_cards=''.join(utility_card('🏢',f'NCLT — {bench}','Official NCLT bench information plus a current all-bench VC directory.',[
        ('NCLT Website','https://nclt.gov.in/','official'),('VC Directory',ONECOURT_NCLT_VC,'directory')]) for bench in COURTS['nclt'])
    nclat_cards=''.join(utility_card('🏢',name,'Official NCLAT bench information and case / cause-list services.',[
        ('NCLAT Website','https://nclat.nic.in/','official'),('Cause / Case Status','https://nclat.nic.in/display-board/cases','official')]) for name in COURTS['nclat'])
    delhi_cards=''.join(utility_card('🎥',name,'Public VC directory page; verify against the day\'s official cause list before joining.',[('Open VC Directory',url,'directory')]) for name,url in DELHI_DISTRICT_VC)
    content=f'''<main class="utility-page directory-page"><div class="utility-kicker">LEGAL UTILITY</div><h1>COURTROOMS &amp; VIRTUAL HEARINGS</h1><p class="lead">Court and tribunal access points in one place. Official court links are prioritised; third-party VC directories are clearly marked and should be checked against the current official cause list.</p><div class="directory-alert"><strong>Before joining a hearing:</strong> verify the court number, date and current VC details from the concerned court / tribunal cause list. VC links can change.</div>
<section class="court-section"><div class="section-head"><h2>Supreme Court of India</h2></div><div class="featured-utility"><div><div class="court-icon large">⚖️</div><h3>Supreme Court Courtroom VC Directory</h3><p>Public directory covering Court Nos. 1–17 and Registrar Courts R-1/R-2. Use the official Supreme Court cause list to identify your courtroom before joining.</p><div class="chip-row">{sc_chips}</div></div><div class="card-actions">{button('Official Supreme Court','https://www.sci.gov.in/','official')}{button('Cause List','https://www.sci.gov.in/','official')}{button('VC Directory',ONECOURT_SC_VC,'directory')}</div></div></section>
<section class="court-section"><div class="section-head"><h2>High Courts</h2></div><div class="section-tools"><span>25 High Courts</span>{button('High Court VC Directory',ONECOURT_HC_VC,'directory')}</div><div class="card-grid">{hc_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>Delhi District Courts — Featured VC Directories</h2></div><div class="card-grid">{delhi_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>DRT</h2></div><div class="card-grid">{drt_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>DRAT</h2></div><div class="card-grid">{drat_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLT</h2></div><div class="section-tools"><span>15 Regional / Principal locations listed by NCLT</span>{button('NCLT VC Directory',ONECOURT_NCLT_VC,'directory')}</div><div class="card-grid">{nclt_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLAT</h2></div><div class="card-grid">{nclat_cards}</div></section></main>'''
    (ROOT/'courtrooms').mkdir(exist_ok=True); (ROOT/'courtrooms/index.html').write_text(page_shell(('Courtrooms & VC Links','/courtrooms/'),'Lex Talk Legal courtrooms, virtual hearing and court access directory.',content),encoding='utf8')

def write_case_status_page():
    hc_cards=''.join(utility_card('🔎',name,'Open the official court website or the national High Court eCourts case-status entry point.',[
        ('Court Website',url,'official'),('Case Status',CASE_STATUS_GENERIC_HC,'official')]) for name,url in COURTS['high_courts'])
    drt_cards=''.join(utility_card('🔎',f'DRT — {city}','Official e-DRT case-status portal. Select the tribunal and search by the available case / diary fields.',[
        ('e-DRT Case Status','https://drt.etribunals.gov.in/','official')]) for city in COURTS['drt'])
    drat_cards=''.join(utility_card('🔎',f'DRAT — {city}','Official DRT/DRAT service portal for case information and listing services.',[
        ('e-DRT Portal','https://drt.etribunals.gov.in/','official')]) for city in COURTS['drat'])
    nclt_cards=''.join(utility_card('🔎',f'NCLT — {bench}','Official NCLT case-status service with bench selection and CAPTCHA-protected search.',[
        ('Case Status','https://efiling.nclt.gov.in/nclt/public/case_status.php','official'),('Case History','https://efiling.nclt.gov.in/casehistorybeforeloginmenutrue.drt','official')]) for bench in COURTS['nclt'])
    nclat_cards=''.join(utility_card('🔎',name,'Official NCLAT case-status search. The portal may require case details / CAPTCHA.',[
        ('Case Status','https://nclat.nic.in/display-board/cases','official'),('e-Filing Portal','https://efiling.nclat.gov.in/mainPage.drt','official')]) for name in COURTS['nclat'])
    content=f'''<main class="utility-page directory-page"><div class="utility-kicker">LEGAL UTILITY</div><h1>CASE STATUS</h1><p class="lead">Choose the court or tribunal and open the relevant official public case-status service. Where a central selection portal is used, the portal will ask you to select the concerned court / bench.</p><div class="directory-alert"><strong>Official portal note:</strong> some case-status services use CAPTCHA or other access controls. This site links to the public portal and does not bypass those controls.</div>
<section class="court-section"><div class="section-head"><h2>Supreme Court of India</h2></div><div class="card-grid">{utility_card('🔎','Supreme Court Case Status','Official Supreme Court case-status and court-services entry point.',[('Case Status','https://www.sci.gov.in/case-status-court/','official'),('Supreme Court Website','https://www.sci.gov.in/','official')])}</div></section>
<section class="court-section"><div class="section-head"><h2>High Courts</h2></div><div class="card-grid">{hc_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>DRT</h2></div><div class="card-grid">{drt_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>DRAT</h2></div><div class="card-grid">{drat_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLT</h2></div><div class="card-grid">{nclt_cards}</div></section>
<section class="court-section"><div class="section-head"><h2>NCLAT</h2></div><div class="card-grid">{nclat_cards}</div></section></main>'''
    (ROOT/'case-status').mkdir(exist_ok=True); (ROOT/'case-status/index.html').write_text(page_shell(('Case Status','/case-status/'),'Lex Talk Legal official public case-status entry points for Indian courts and tribunals.',content),encoding='utf8')

def sync_homepage(arts,videos):
    p=ROOT/'index.html'
    if not p.exists(): return
    s=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
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
        style=s.find('style',{'data-embedded':'lex-talk-legal'}); script=s.find('script',{'data-embedded':'lex-talk-legal'})
        changed=False
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
    write_category_pages(arts); write_videos_page(videos); write_courtrooms_page(); write_case_status_page(); sync_homepage(arts,videos); refresh_static_pages()
    urls=['/','/courtrooms/','/case-status/','/videos/']+[f'/category/{k}/' for k in CATEGORY_MAP]+[a['url'] for a in arts]
    now=datetime.now(timezone.utc).date().isoformat(); xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'; xml+=''.join(f'<url><loc>https://lextalk.legal{u}</loc><lastmod>{now}</lastmod></url>' for u in dict.fromkeys(urls))+'</urlset>'; (ROOT/'sitemap.xml').write_text(xml,encoding='utf8')
    print(f'Synced {len(arts)} Blogger articles and {len(videos)} YouTube videos; refreshed courtrooms and case-status directories.')

if __name__=='__main__': main()
