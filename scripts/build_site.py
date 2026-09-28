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


GUIDES = {
    'courts': {
        'name': 'Courts', 'kicker': 'INDIAN JUDICIARY EXPLAINED',
        'intro': 'A practical guide to India’s judicial structure — Supreme Court, High Courts, District & Subordinate Courts, tribunals and digital court services.',
        'history': [
            ('1937', 'Federal Court', 'The Federal Court functioned during the pre-Constitution period and preceded the Supreme Court.'),
            ('1950', 'Supreme Court', 'The Supreme Court came into existence with the Constitution on 26 January 1950 and was inaugurated on 28 January 1950.'),
            ('1958', 'Present building', 'The Supreme Court moved from the old Parliament House to its present Tilak Marg building in New Delhi in 1958.'),
            ('Today', 'Multi-level system', 'India operates through the Supreme Court, High Courts and District & Subordinate Courts, alongside specialised tribunals created by statute.')
        ],
        'laws': [
            ('Constitution of India', 'Articles 124 onward deal with the Supreme Court; Article 214 deals with High Courts; Part VI and the constitutional framework govern the subordinate judiciary.', 'https://www.sci.gov.in/jurisdiction/'),
            ('Code of Civil Procedure, 1908', 'Core procedural framework for civil litigation, subject to special statutes and court rules.', 'https://indiacode.gov.in/'),
            ('Bharatiya Nagarik Suraksha Sanhita, 2023', 'Criminal procedure framework currently in force, subject to transition and case-specific provisions.', 'https://indiacode.gov.in/'),
            ('e-Courts services', 'Digital case information, cause lists and other court services are part of India’s e-Courts ecosystem.', 'https://doj.gov.in/')
        ],
        'flow': ['Cause / dispute', 'Trial or original forum', 'High Court / appellate forum', 'Supreme Court / final appellate or constitutional route'],
        'sources': [
            ('Supreme Court — History', 'https://www.sci.gov.in/about-department/history/'),
            ('Supreme Court — Jurisdiction', 'https://www.sci.gov.in/jurisdiction/'),
            ('Department of Justice', 'https://doj.gov.in/'),
            ('e-Courts Project', 'https://dashboard.doj.gov.in/ecourts-projects-phaseI/index.php')
        ]
    },
    'law-policy': {
        'name': 'Law & Policy', 'kicker': 'LAWMAKING & PUBLIC POLICY',
        'intro': 'Understand how policy ideas, Bills, Acts, rules, regulations, notifications and judicial interpretation interact in India.',
        'history': [
            ('1950', 'Constitutional framework', 'The Constitution became the foundation for institutions, fundamental rights, governance and the distribution of legislative and judicial powers.'),
            ('Parliament', 'Bill stage', 'Legislative proposals are introduced in the form of Bills and move through consideration and voting in Parliament.'),
            ('Assent', 'Act of Parliament', 'A Bill passed by both Houses and assented to by the President becomes an Act.'),
            ('Implementation', 'Rules & notifications', 'Delegated/subordinate legislation and administrative notifications may provide the operational framework under an Act.')
        ],
        'laws': [
            ('Constitution of India', 'Defines legislative fields, institutional powers, rights and the constitutional limits within which legislation operates.', 'https://legislative.gov.in/constitution-of-india/'),
            ('Parliamentary lawmaking', 'Digital Sansad explains Bills, readings, consideration, voting and the President’s assent.', 'https://sansad.in/rs/legislation/introduction'),
            ('Subordinate legislation', 'Rules, regulations, orders and notifications may be framed under authority delegated by an Act.', 'https://www.legislative.gov.in/'),
            ('India Code', 'Central Acts and related legislative material are available through the official India Code portal.', 'https://indiacode.gov.in/')
        ],
        'flow': ['Policy objective', 'Bill / legislative proposal', 'Parliamentary consideration', 'Presidential assent', 'Rules / notifications', 'Implementation & judicial review'],
        'sources': [
            ('Digital Sansad — How a Bill becomes an Act', 'https://sansad.in/ls/legislation/introduction'),
            ('Legislative Department', 'https://legislative.gov.in/'),
            ('India Code', 'https://indiacode.gov.in/'),
            ('Department of Justice', 'https://doj.gov.in/')
        ]
    },
    'banking-law': {
        'name': 'Banking Law', 'kicker': 'BANKING, CREDIT & RECOVERY',
        'intro': 'A practical legal map of banking regulation, loans, security enforcement, recovery, insolvency, customer protection and dispute resolution.',
        'history': [
            ('1934', 'RBI Act', 'The Reserve Bank of India Act, 1934 forms a foundational part of the statutory framework governing the central bank.'),
            ('1949', 'Banking Regulation Act', 'The Banking Regulation Act, 1949 consolidated and amended the law relating to banking.'),
            ('1993', 'Debt recovery tribunals', 'The Recovery of Debts and Bankruptcy Act framework created a specialised tribunal mechanism for expeditious adjudication and recovery of specified bank / financial-institution debts.'),
            ('2002', 'SARFAESI', 'SARFAESI created a statutory framework for securitisation, reconstruction and enforcement of security interests.'),
            ('2016', 'IBC', 'The Insolvency and Bankruptcy Code, 2016 consolidated the insolvency framework and established IBBI.')
        ],
        'laws': [
            ('RBI Act, 1934', 'Statutory foundation for the Reserve Bank and several monetary / regulatory functions.', 'https://indiacode.gov.in/'),
            ('Banking Regulation Act, 1949', 'Core banking regulation statute.', 'https://indiacode.gov.in/'),
            ('SARFAESI Act, 2002', 'Security-interest enforcement, securitisation and reconstruction framework.', 'https://www.indiacode.nic.in/indiacode/handle/123456789/2006?view_type=browse'),
            ('Recovery of Debts and Bankruptcy Act, 1993', 'Specialised tribunal framework for specified debt-recovery disputes.', 'https://www.indiacode.nic.in/indiacode/handle/123456789/1775?view_type=browse'),
            ('IBC, 2016', 'Insolvency resolution and liquidation framework, with different fora and rules for different debtor categories.', 'https://www.indiacode.nic.in/indiacode/handle/123456789/2154?view_type=browse')
        ],
        'flow': ['Loan / credit facility', 'Default / regulatory trigger', 'Notice / restructuring / recovery action', 'DRT / SARFAESI / IBC / civil forum as applicable', 'Order / recovery / resolution'],
        'sources': [
            ('India Code', 'https://indiacode.gov.in/'),
            ('RBI', 'https://www.rbi.org.in/'),
            ('DRT', 'https://drt.gov.in/'),
            ('IBBI', 'https://ibbi.gov.in/')
        ]
    },
    'drt-drat': {
        'name': 'DRT / DRAT', 'kicker': 'DEBT RECOVERY TRIBUNALS EXPLAINED',
        'intro': 'Understand what DRTs and DRATs do, how the 1993 debt-recovery framework evolved, and where SARFAESI / insolvency proceedings can intersect with tribunal practice.',
        'history': [
            ('1993', 'Tribunal framework', 'The Recovery of Debts Due to Banks and Financial Institutions Act, 1993 established a specialised mechanism for expeditious adjudication and recovery of specified debts.'),
            ('2002', 'SARFAESI', 'SARFAESI introduced a separate statutory security-enforcement framework with a remedy before DRT against specified measures.'),
            ('2016', 'RDB Act & DRAT framework', 'The debt-recovery statute is now titled the Recovery of Debts and Bankruptcy Act, 1993, with appellate tribunals for specified appeals.'),
            ('2016 onward', 'IBC era', 'IBC added a separate insolvency architecture; the competent forum depends on the debtor category and statutory provisions in force.')
        ],
        'laws': [
            ('Recovery of Debts and Bankruptcy Act, 1993', 'Primary tribunal statute for specified debt-recovery claims, procedure and appeals.', 'https://www.indiacode.nic.in/indiacode/handle/123456789/1775?view_type=browse'),
            ('SARFAESI Act, 2002', 'Includes the statutory remedy framework for challenging specified enforcement measures before the DRT.', 'https://www.indiacode.nic.in/indiacode/handle/123456789/2006?view_type=browse'),
            ('IBC, 2016', 'Provides insolvency processes and forum rules for different debtor categories.', 'https://www.indiacode.nic.in/indiacode/handle/123456789/2154?view_type=browse'),
            ('DRT e-filing / services', 'Public portal for tribunal services and electronic filing.', 'https://efiling.drt.gov.in/')
        ],
        'flow': ['Bank / financial claim', 'OA / SA or other statutory proceeding', 'DRT hearing & order', 'DRAT appeal where maintainable', 'Further statutory / judicial remedy where available'],
        'sources': [
            ('India Code — RDB Act', 'https://www.indiacode.nic.in/indiacode/handle/123456789/1775?view_type=browse'),
            ('India Code — SARFAESI', 'https://www.indiacode.nic.in/indiacode/handle/123456789/2006?view_type=browse'),
            ('DRT', 'https://drt.gov.in/'),
            ('DRT e-Filing', 'https://efiling.drt.gov.in/')
        ]
    },
    'legal-careers': {
        'name': 'Legal Careers', 'kicker': 'LAW CAREER ROADMAP',
        'intro': 'Explore the major pathways after LL.B. — litigation, law firms, in-house legal teams, compliance, judiciary, public-sector opportunities, academia and specialised legal practice.',
        'history': [
            ('Step 1', 'LL.B.', 'Complete a 3-year or 5-year LL.B. from a recognised institution, subject to the applicable rules for the pathway you choose.'),
            ('Step 2', 'Choose a track', 'Litigation, law firm practice, in-house, compliance, insolvency, banking law, policy, academia and judicial careers require different preparation.'),
            ('Step 3', 'Professional requirements', 'Advocacy practice involves State Bar Council enrolment and applicable BCI requirements; other roles follow their own recruitment or qualification rules.'),
            ('Step 4', 'Build proof of work', 'Internships, drafting, research, writing, mooting, court exposure, domain knowledge and a clear CV can help demonstrate capability to employers or chambers.')
        ],
        'laws': [
            ('Advocates Act, 1961', 'Statutory framework governing advocates and Bar Councils in India.', 'https://indiacode.gov.in/'),
            ('Bar Council / professional rules', 'Professional conduct and enrolment requirements are governed by applicable BCI and State Bar Council rules.', 'https://www.barcouncilofindia.org/'),
            ('AIBE', 'The official AIBE portal publishes current eligibility, notifications, registration and examination information.', 'https://www.allindiabarexamination.com/'),
            ('Judicial recruitment', 'Judicial service recruitment is conducted through the relevant State / High Court process and notifications.', 'https://doj.gov.in/')
        ],
        'flow': ['LL.B.', 'Career track selection', 'Skill building & internships', 'Eligibility / enrolment / recruitment', 'Applications & interviews', 'Practice / progression'],
        'sources': [
            ('AIBE — Official Portal', 'https://www.allindiabarexamination.com/'),
            ('Bar Council of India', 'https://www.barcouncilofindia.org/'),
            ('India Code', 'https://indiacode.gov.in/'),
            ('Department of Justice', 'https://doj.gov.in/')
        ],
        'career_cta': True
    },
    'dra': {
        'name': 'DRA', 'kicker': 'DEBT RECOVERY AGENT AWARENESS',
        'intro': 'A compliance-first guide for Debt Recovery Agents: role boundaries, borrower interaction, confidentiality, communication, documentation and RBI expectations.',
        'history': [
            ('Outsourcing', 'Regulated entities', 'Banks and other regulated entities may use service providers for recovery activity, while the regulated entity retains responsibility under applicable RBI directions.'),
            ('Code of conduct', 'Professional behaviour', 'RBI directions emphasise training, customer confidentiality and fair / lawful recovery practices.'),
            ('2022', 'Specific recovery-agent directions', 'RBI reiterated that regulated entities are responsible for agents and prohibited intimidation, harassment, privacy intrusion, inappropriate communications and calls before 8:00 a.m. or after 7:00 p.m. for overdue-loan recovery.'),
            ('Today', 'Documentation & auditability', 'A sound field process should use proper authorisation, identification, records and escalation channels rather than informal pressure.')
        ],
        'laws': [
            ('RBI directions on recovery agents', 'Regulated entities remain responsible for the actions of recovery agents they employ or outsource to.', 'https://www.rbi.org.in/'),
            ('Consumer protection & privacy principles', 'Recovery communication should respect borrower privacy, dignity and applicable legal / regulatory protections.', 'https://www.rbi.org.in/'),
            ('SARFAESI / recovery statutes', 'Agents must operate within the actual authority given by the regulated entity and the applicable legal process.', 'https://indiacode.gov.in/'),
            ('Escalation / grievance channels', 'Borrower grievances should be routed through the regulated entity’s complaint and escalation mechanism, and applicable RBI Ombudsman framework where eligible.', 'https://www.rbi.org.in/')
        ],
        'flow': ['Assignment / authorisation', 'Identification & communication', 'Lawful recovery effort', 'Documentation / receipt / escalation', 'Grievance resolution / closure'],
        'sources': [
            ('RBI recovery-agent directions', 'https://www.rbi.org.in/'),
            ('RBI — Regulatory framework', 'https://www.rbi.org.in/'),
            ('India Code', 'https://indiacode.gov.in/'),
            ('RBI Complaint Management System', 'https://cms.rbi.org.in/')
        ]
    }
}


def guide_markup(key):
    g=GUIDES[key]
    timeline=''.join(f'<div class="timeline-item reveal"><div class="timeline-year">{H.escape(y)}</div><div><h3>{H.escape(t)}</h3><p>{H.escape(d)}</p></div></div>' for y,t,d in g['history'])
    laws=''.join(f'<article class="law-card reveal"><div class="law-card-kicker">LEGAL FRAMEWORK</div><h3>{H.escape(t)}</h3><p>{H.escape(d)}</p><a class="guide-link" href="{H.escape(u,quote=True)}" target="_blank" rel="noopener">Open Official Source ↗</a></article>' for t,d,u in g['laws'])
    flow=''.join(f'<div class="flow-step reveal"><span>{i+1:02d}</span><strong>{H.escape(x)}</strong></div>' for i,x in enumerate(g['flow']))
    sources=''.join(f'<a class="source-pill" href="{H.escape(u,quote=True)}" target="_blank" rel="noopener">{H.escape(t)} ↗</a>' for t,u in g['sources'])
    cta='''<section class="career-contact reveal"><div><div class="utility-kicker">CAREER OPPORTUNITY</div><h2>Want to work with Lex Talk Legal?</h2><p>Send your resume / CV to <strong>office.lextalklegal@gmail.com</strong>. Please mention the role, location preference and a short note about your experience.</p><small>Resume submission is for consideration only and does not create an offer, engagement or guarantee of selection.</small></div><a class="cta-button" href="mailto:office.lextalklegal@gmail.com?subject=Resume%20Submission%20-%20Lex%20Talk%20Legal">Send Resume ↗</a></section>''' if g.get('career_cta') else ''
    return f'''<main class="guide-page">
<section class="guide-hero"><div><div class="utility-kicker">{H.escape(g['kicker'])}</div><h1>{H.escape(g['name'])}</h1><p>{H.escape(g['intro'])}</p><div class="guide-hero-actions"><a class="cta-button" href="#explainer">Start Explainer ↓</a><a class="ghost-button" href="#latest">Latest {H.escape(g['name'])} Stories</a></div></div><div class="guide-badge"><div class="guide-badge-icon">⚖</div><strong>LEX TALK LEGAL</strong><span>Law Simplified for Everyone</span></div></section>
<section id="explainer" class="guide-section"><div class="section-head"><h2>Animated Explainer</h2><span class="section-tools">Scroll to reveal the legal journey</span></div><div class="flow-track">{flow}</div></section>
<section class="guide-section"><div class="section-head"><h2>Quick Timeline</h2></div><div class="timeline">{timeline}</div></section>
<section class="guide-section"><div class="section-head"><h2>Applicable Laws &amp; Framework</h2></div><div class="law-grid">{laws}</div></section>
{cta}
<section id="latest" class="guide-section"><div class="section-head"><h2>Latest {H.escape(g['name'])} Stories</h2></div><div class="grid" id="latest-guide-{key}"></div></section>
<section class="guide-section"><div class="section-head"><h2>Official References</h2></div><div class="source-pills">{sources}</div></section>
<section class="guide-note"><strong>Editorial note:</strong> This explainer is for general legal education. Statutes, rules, notifications, court decisions and regulatory directions may change; readers should verify the current position from the linked official source.</section>
</main>'''


def write_category_pages(arts):
    for key,(name,_) in CATEGORY_MAP.items():
        if key in GUIDES:
            g=GUIDES[key]
            items=[a for a in arts if category_matches(a,key)]
            cards=''.join(article_card(a) for a in items[:12]) or '<div class="empty">No stories published in this section yet. Publish a Blogger post with the appropriate label and the next automated sync will update this section.</div>'
            content=guide_markup(key).replace(f'<div class="grid" id="latest-guide-{key}"></div>', f'<div class="grid">{cards}</div>')
            desc=f'Lex Talk Legal — {g["name"]}: history, legal framework, practical explainer and latest stories.'
        else:
            items=[a for a in arts if category_matches(a,key)]
            cards=''.join(article_card(a) for a in items[:30]) or '<div class="empty">No stories published in this section yet.</div>'
            content=f'<main class="utility-page"><div class="utility-kicker">LEX TALK LEGAL</div><h1>{H.escape(name)}</h1><p class="lead">Latest Lex Talk Legal stories in this section are synced automatically from Blogger.</p><div class="grid">{cards}</div></main>'
            desc=f'Lex Talk Legal — {name} news, updates and explainers.'
        p=ROOT/'category'/key/'index.html'; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(page_shell((name,f'/category/{key}/'),desc,content),encoding='utf8')

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
                if 'NCLT' in text_title or 'nclt' in u.lower():
                    data.setdefault('nclt',{})[text_title]=links
                elif 'NCLAT' in text_title or 'nclat' in u.lower():
                    data.setdefault('nclat',{})[text_title]=links
                elif 'districtcourts' in u.lower():
                    data.setdefault('delhi_district',{})[text_title]=links
                else:
                    matched=None; low=text_title.lower()
                    for name,_ in COURTS['high_courts']:
                        stem=name.lower().replace(' high court','')
                        if stem in low or name.lower() in low:
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


def under_construction_page():
    content='''<main class="utility-page under-page"><div class="guide-badge large"><div class="guide-badge-icon">🏦</div><strong>LEX TALK LEGAL</strong><span>Utility Module</span></div><div class="utility-kicker">COMING SOON</div><h1>Today's Bank Auction</h1><p class="lead">The searchable bank-auction directory is currently under construction. We are preparing a structured module for bank / authorised-officer auction notices, location filters and source links.</p><div class="under-box"><h2>What will appear here?</h2><div class="under-grid"><div>🏠 Property Auctions</div><div>🏢 Commercial Assets</div><div>🚗 Vehicle Auctions</div><div>📍 Location Filters</div><div>🏦 Bank / Institution</div><div>📄 Official Notice Links</div></div></div><a class="cta-button" href="/">Return to Lex Talk Legal ↗</a></main>'''
    (ROOT/'under-construction.html').write_text(page_shell(("Today's Bank Auction",'/under-construction.html'),'Lex Talk Legal bank auction directory — currently under construction.',content),encoding='utf8')




# ---------- v5 presentation/build layer ----------
SITE_URL='https://lextalk.legal'
LOGO='/assets/LexTalkLegal_Logo-wo-bg.png'

NAV=[
 ('Latest','/'),('Courts','/category/courts/'),('Law & Policy','/category/law-policy/'),
 ('Banking Law','/category/banking-law/'),('DRT / DRAT','/category/drt-drat/'),
 ('Legal Careers','/category/legal-careers/'),('DRA','/category/dra/'),
 ('Legal Professionals','/advocates/'),('Bare Acts',BARE_ACTS_URL),('Courtrooms','/courtrooms/'),
 ('Case Status','/case-status/'),('Videos','/videos/')]

def category_matches(a,key):
    labels={str(x).strip().lower() for x in a.get('labels',[])}
    title=str(a.get('title','')).lower()
    _,terms=CATEGORY_MAP[key]
    return bool(labels & terms) or any(t in title for t in terms)

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

def nav_html():
    return ''.join(f'<a href="{H.escape(u,quote=True)}"'+((' target="_blank" rel="noopener noreferrer"') if u.startswith('http') else '')+f'>{H.escape(x)}</a>' for x,u in NAV)

def page_shell(title,description,content,noindex=False):
    t=title[0] if isinstance(title,tuple) else title
    canonical=title[1] if isinstance(title,tuple) else '/'
    robots='noindex,nofollow' if noindex else 'index,follow,max-image-preview:large'
    nav=nav_html()
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="{H.escape(description,quote=True)}"><meta name="robots" content="{robots}">
<link rel="canonical" href="{SITE_URL}{H.escape(canonical,quote=True)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Lex Talk Legal"><meta property="og:title" content="{H.escape(t,quote=True)}"><meta property="og:description" content="{H.escape(description,quote=True)}"><meta property="og:url" content="{SITE_URL}{H.escape(canonical,quote=True)}"><meta property="og:image" content="{SITE_URL}{LOGO}"><meta name="twitter:card" content="summary_large_image">
<title>{H.escape(t)} | Lex Talk Legal</title><link rel="stylesheet" href="/assets/site.css">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3161673810996421" crossorigin="anonymous"></script></head><body>
<div class="site-accent"></div><div class="utility-bar"><div class="wrap utility-inner"><div class="utility-left"><span class="live-dot">●</span><span id="dateLabel">--</span><span class="utility-sep">|</span><span id="timeLabel">--:--:-- IST</span><span class="utility-sep">|</span><span>New Delhi, India</span></div></div></div>
<header class="masthead"><div class="wrap masthead-inner"><a href="/" aria-label="Lex Talk Legal home"><img src="{LOGO}" alt="Lex Talk Legal"></a></div></header>
<nav class="nav"><div class="wrap nav-inner"><div class="nav-links">{nav}</div><button class="menu-toggle" id="menuBtn" type="button" aria-expanded="false" aria-controls="mobileMenu">☰ Menu</button></div><div class="wrap mobile-menu" id="mobileMenu">{nav}</div></nav>
{content}
<footer class="footer"><div class="footergrid"><div><h3>Lex Talk Legal</h3><p>Law Simplified for Everyone.</p><p>Digital Legal News &amp; Legal Education Platform.</p><p>Adv. Gagann Jha, Advocate, Supreme Court of India<br>LEXBOTICS AI MEDIA LLP</p></div><div><h3>Explore</h3><ul><li><a href="/">Latest</a></li><li><a href="/category/courts/">Courts</a></li><li><a href="/category/law-policy/">Law &amp; Policy</a></li><li><a href="/category/banking-law/">Banking Law</a></li><li><a href="/category/drt-drat/">DRT / DRAT</a></li><li><a href="/category/legal-careers/">Legal Careers</a></li></ul></div><div><h3>Community</h3><ul><li><a href="/advocates/">Legal Professionals</a></li><li><a href="/advocates/apply">Create Free Profile</a></li><li><a href="/profile-guidelines.html">Profile Guidelines</a></li><li><a href="/videos/">Latest Videos</a></li><li><a href="/courtrooms/">Courtrooms / VC</a></li><li><a href="/case-status/">Case Status</a></li></ul></div><div><h3>Connect</h3><ul><li><a href="https://www.youtube.com/@LexTalkLegal" target="_blank" rel="noopener noreferrer">YouTube</a></li><li><a href="https://www.instagram.com/lex_talk_legal" target="_blank" rel="noopener noreferrer">Instagram</a></li><li><a href="https://x.com/Lex_Talk_Legal" target="_blank" rel="noopener noreferrer">X</a></li><li><a href="https://in.linkedin.com/company/lextalklegal" target="_blank" rel="noopener noreferrer">LinkedIn</a></li><li><a href="https://t.me/lextalklegal" target="_blank" rel="noopener noreferrer">Telegram</a></li></ul></div><div><h3>Legal &amp; Contact</h3><p>+91-8368268507<br>+91-9318445957<br>office.lextalklegal@gmail.com</p><ul><li><a href="/privacy-policy.html">Privacy</a></li><li><a href="/terms-of-use.html">Terms</a></li><li><a href="/disclaimer.html">Disclaimer</a></li><li><a href="/editorial-policy.html">Editorial Policy</a></li><li><a href="/copyright-policy.html">Copyright / Takedown</a></li><li><a href="/corrections-grievance.html">Corrections &amp; Grievance</a></li><li><a href="/ai-content-policy.html">AI Content Policy</a></li></ul></div></div><div class="copy">© 2026 LEXBOTICS AI MEDIA LLP | Lex Talk Legal | For Educational &amp; Informational Use Only</div></footer><script src="/assets/site.js" defer></script></body></html>'''

def article(a):
    image=a.get('image','')
    hero=f'<figure class="article-hero"><img src="{H.escape(image,quote=True)}" alt="{H.escape(a.get("title", ""),quote=True)}" loading="eager"></figure>' if image else ''
    soup=BeautifulSoup(a.get('content','') or '','html.parser')
    first=soup.find('img')
    if first:first.decompose()
    body_html=str(soup)
    schema={'@context':'https://schema.org','@type':'NewsArticle' if 'news' in str(a.get('category','')).lower() else 'Article','headline':a.get('title',''),'datePublished':a.get('published',''),'dateModified':a.get('published',''),'mainEntityOfPage':{'@type':'WebPage','@id':SITE_URL+a.get('url','')},'author':{'@type':'Organization','name':'Lex Talk Legal','url':SITE_URL+'/'},'publisher':{'@type':'Organization','name':'LEXBOTICS AI MEDIA LLP','url':SITE_URL+'/'},'description':a.get('excerpt','')}
    if image:schema['image']=[image]
    schema_json=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    desc=a.get('excerpt','')
    body=f'''<main class="article-wrap"><div class="utility-kicker">{H.escape(a.get('category','Legal News'))}</div><div class="story-meta">{H.escape(a.get('published','')[:10])}</div><h1>{H.escape(a.get('title',''))}</h1><div class="article-meta">Lex Talk Legal · Educational &amp; informational coverage <span>·</span> <a href="{H.escape(a.get('source_url',''),quote=True)}" target="_blank" rel="noopener noreferrer">Original source</a></div>{hero}<div class="article-body">{body_html}</div><div class="notice"><strong>Editorial note:</strong> This content is for general legal information and education. Verify important legal facts, orders, dates and current procedural requirements from the concerned official source.</div><div class="article-source">Source reference: Original Blogger publication linked above. Lex Talk Legal does not represent that linked third-party content is error-free or current in every respect.</div></main>'''
    return page_shell((a.get('title',''),a.get('url','')),desc,body).replace('</head>','<script type="application/ld+json">'+schema_json+'</script></head>')

def article_card(a,variant='standard'):
    image=a.get('image',''); media=f'<a class="story-image" href="{H.escape(a["url"],quote=True)}"><img src="{H.escape(image,quote=True)}" alt="" loading="lazy" decoding="async"></a>' if image else '<div class="story-image"></div>'
    compact=' compact' if variant=='compact' else ''
    return f'<article class="story-card{compact}">{media}<div class="story-meta">{H.escape(a.get("category","Legal News"))} · {H.escape(a.get("published","")[:10])}</div><h3><a href="{H.escape(a["url"],quote=True)}">{H.escape(a.get("title",""))}</a></h3><p>{H.escape(a.get("excerpt",""))}</p></article>'

def secondary_card(a):
    image=a.get('image','');media=f'<a class="secondary-image" href="{H.escape(a["url"],quote=True)}"><img src="{H.escape(image,quote=True)}" alt="" loading="lazy" decoding="async"></a>' if image else '<div class="secondary-image"></div>'
    return f'<article class="secondary-story">{media}<div class="secondary-copy"><div class="story-meta">{H.escape(a.get("category","Legal News"))} · {H.escape(a.get("published","")[:10])}</div><h3><a href="{H.escape(a["url"],quote=True)}">{H.escape(a.get("title",""))}</a></h3><p>{H.escape(a.get("excerpt",""))}</p></div></article>'

def video_card(v):
    thumb=H.escape(v.get('thumbnail',''),quote=True); title=H.escape(v.get('title','Lex Talk Legal')); date=H.escape(v.get('published','')[:10]);url=H.escape(v.get('url','https://www.youtube.com/@LexTalkLegal'),quote=True); visual=f'<img src="{thumb}" alt="" loading="lazy" decoding="async">' if thumb else '<div></div>'
    return f'<article class="video-card"><a href="{url}" target="_blank" rel="noopener noreferrer"><div class="video-thumb">{visual}<span class="video-play">▶</span></div></a><div class="video-card-body"><div class="story-meta">{date}</div><h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3></div></article>'

def global_widget_markup(): return ''
def auction_widget_markup(): return '<article class="utility-card"><div class="icon">🏦</div><div class="side-kicker">FEATURED UTILITY</div><h3><a href="/under-construction.html">Today’s Bank Auction</a></h3><p>The searchable auction directory is being prepared with source and verification controls.</p><a class="utility-link" href="/under-construction.html">Explore auction module ↗</a></article>'
def homepage_sidebar_markup():
    return f'''<article class="utility-card"><div class="icon">🎥</div><div class="side-kicker">LEGAL UTILITY</div><h3><a href="/courtrooms/">Official courtroom &amp; VC links</a></h3><p>Open public virtual-hearing destinations and courtroom information.</p><a class="utility-link" href="/courtrooms/">Open Courtrooms ↗</a></article><article class="utility-card"><div class="icon">🔎</div><div class="side-kicker">LEGAL UTILITY</div><h3><a href="/case-status/">Official case-status portals</a></h3><p>Quick links for courts and tribunals. CAPTCHA and access controls remain with the official portal.</p><a class="utility-link" href="/case-status/">Check Case Status ↗</a></article><article class="utility-card"><div class="icon">📚</div><div class="side-kicker">LEGAL KNOWLEDGE</div><h3><a href="/category/drt-drat/">DRT, DRAT, SARFAESI &amp; Banking Law</a></h3><p>Practical explainers, history and current legal coverage.</p><a class="utility-link" href="/category/banking-law/">Explore Banking Law ↗</a></article>{auction_widget_markup()}'''

def sync_homepage(arts,videos):
    arts=normalize_articles(arts); lead=arts[:1]; secondaries=arts[1:4]; latest=arts[4:10]; most=arts[:5]; vids=videos[:6]
    lead_html=''
    if lead:
        a=lead[0]; img=f'<div class="lead-image"><a href="{H.escape(a["url"],quote=True)}"><img src="{H.escape(a.get("image",""),quote=True)}" alt="" loading="eager" decoding="async"></a></div>' if a.get('image') else ''
        lead_html=f'<article class="lead-story">{img}<div class="story-meta">{H.escape(a.get("category","Legal News"))} · {H.escape(a.get("published","")[:10])}</div><h1><a href="{H.escape(a["url"],quote=True)}">{H.escape(a.get("title",""))}</a></h1><p class="excerpt">{H.escape(a.get("excerpt",""))}</p><a class="read-link" href="{H.escape(a["url"],quote=True)}">Read full story ↗</a></article>'
    else: lead_html='<article class="lead-story"><div class="lead-image"></div><div class="story-meta">LEX TALK LEGAL</div><h1>Law, Courts &amp; Justice — Explained in Simple Language</h1><p class="excerpt">Legal news, judgments, court updates and practical explainers.</p></article>'
    sec=''.join(secondary_card(a) for a in secondaries) or '<div class="empty">More stories will appear after the next editorial sync.</div>'
    latest_html=''.join(article_card(a) for a in latest) or '<div class="empty">No latest stories are available right now.</div>'
    most_html=''.join(f'<li><a href="{H.escape(a["url"],quote=True)}">{H.escape(a.get("title",""))}</a></li>' for a in most) or '<li>No stories available yet.</li>'
    vid_html=''.join(video_card(v) for v in vids) or '<div class="empty">No videos returned in the latest sync.</div>'
    content=f'''<main class="home"><div class="wrap"><section class="section"><div class="lead-layout"><div>{lead_html}</div><div class="secondary-list">{sec}</div></div><div class="topic-strip"><a class="topic-chip" href="/category/courts/">Supreme Court</a><a class="topic-chip" href="/category/courts/">High Courts</a><a class="topic-chip" href="/category/drt-drat/">DRT / DRAT</a><a class="topic-chip" href="/category/banking-law/">SARFAESI</a><a class="topic-chip" href="/category/legal-careers/">AIBE</a><a class="topic-chip" href="/category/dra/">DRA</a><a class="topic-chip" href="/advocates/">Legal Professionals</a><a class="topic-chip" href="/videos/">Videos</a></div></section><div class="ad-wrap"><div class="ad-slot">ADVERTISEMENT</div></div><section class="section"><div class="content-layout"><div><div class="section-head"><div><span class="section-kicker">LATEST COVERAGE</span><h2>Latest Legal News</h2></div><p>Fresh updates from Lex Talk Legal</p></div><div class="story-grid">{latest_html}</div></div><aside class="sidebar"><div class="side-box"><span class="side-kicker">MOST READ</span><h3>Legal Reads</h3><ul class="side-list">{most_html}</ul></div><div class="ad-slot tall">ADVERTISEMENT</div><div style="height:18px"></div>{homepage_sidebar_markup()}</aside></div></section><section class="section"><div class="professional-banner"><div><span class="section-kicker">LEGAL COMMUNITY</span><h2>Legal Professional Profiles — Free to Create</h2><p>Build an informational professional profile on Lex Talk Legal. Profiles are reviewed before publication and are not ranked, rated or promoted as “best” lawyers.</p><div class="professional-points"><div class="professional-point">FREE PROFILE</div><div class="professional-point">ADMIN REVIEW</div><div class="professional-point">NO PAID RANKING</div><div class="professional-point">NETWORKING FOCUSED</div></div></div><div class="professional-actions"><a class="primary-btn" href="/advocates/apply">Create Free Profile ↗</a></div></div></section><section class="section"><div class="section-head"><div><span class="section-kicker">WATCH</span><h2>Lex Talk Legal Videos</h2></div><p><a class="text-link" href="/videos/">View all videos ↗</a></p></div><div class="video-grid">{vid_html}</div></section></div></main><section class="newsletter"><div class="wrap newsletter-inner"><div><span class="section-kicker">NEWSLETTER</span><h2>Get Legal Updates</h2><p>News, judgments, explainers and career updates delivered by email.</p></div><form class="newsletter-form" onsubmit="event.preventDefault();alert('Newsletter signup will be connected to the selected mailing provider before public launch.');"><input type="email" required placeholder="Your email address" aria-label="Your email address"><button class="primary-btn" type="submit">Subscribe</button></form></div></section>'''
    p=ROOT/'index.html';p.write_text(page_shell(('Lex Talk Legal','/'),'Digital legal news, court updates, legal education and legal professional networking in simple language.',content),encoding='utf8')

def refresh_static_pages():
    preserve={'advocates/index.html','advocates/apply.html','admin/index.html','profile-guidelines.html'}
    for p in sorted(ROOT.rglob('*.html')):
        rel=p.relative_to(ROOT).as_posix()
        if rel in preserve or rel.startswith('article/') or rel.startswith('category/') or rel in {'index.html','videos/index.html','courtrooms/index.html','case-status/index.html'}: continue
        try:s=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
        except Exception:continue
        main=s.find('main')
        if not main: continue
        title=s.title.string.split('|')[0].strip() if s.title and s.title.string else p.stem.replace('-',' ').title()
        desc=s.find('meta',attrs={'name':'description'}); desc=desc.get('content','Lex Talk Legal') if desc else 'Lex Talk Legal'
        p.write_text(page_shell((title,'/'+rel),desc,str(main)),encoding='utf8')

def profile_layout(title,subtitle,body,canonical,noindex=False):
    return page_shell((title,canonical),subtitle,body,noindex=noindex)

def write_profile_pages():
    directory='''<main class="utility-page"><div class="profile-hero"><span class="utility-kicker">LEGAL PROFESSIONAL COMMUNITY</span><h1>Legal Professional Profiles</h1><p class="lead">Free informational professional profiles published by Lex Talk Legal after administrative review. The directory does not rank, rate, recommend or endorse professionals.</p><div class="notice"><strong>Profile principle:</strong> Information is submitted by the profile holder and reviewed for publication. Publication is not certification, endorsement, legal advice, solicitation or a guarantee of outcome.</div></div><div class="profile-search"><input id="profileQuery" type="search" maxlength="80" placeholder="Search name, city, state or practice area"><button class="primary-btn" id="profileSearchBtn" type="button">Search</button></div><div id="profileStatus" class="form-status"></div><div id="profileList" class="profile-list"><div class="empty">Loading published profiles…</div></div><div class="notice"><strong>No paid placement:</strong> Lex Talk Legal does not offer paid profile ranking, star ratings, “best lawyer” labels or guaranteed leads. Users should independently verify professional credentials and suitability.</div></main><script>(async function(){const q=document.getElementById("profileQuery"),b=document.getElementById("profileSearchBtn"),list=document.getElementById("profileList"),st=document.getElementById("profileStatus");const esc=v=>String(v??'').replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));async function load(){list.innerHTML='<div class="empty">Loading published profiles…</div>';try{const r=await fetch("/api/profiles?q="+encodeURIComponent(q.value.trim()));const d=await r.json();if(!r.ok)throw new Error(d.error||"Profile service is temporarily unavailable.");if(!d.profiles.length){list.innerHTML='<div class="empty">No published profiles found. Be among the first to submit a free profile.</div>';return;}list.innerHTML=d.profiles.map(p=>{const chips=(p.practice_areas||"").split(",").map(x=>x.trim()).filter(Boolean).slice(0,4).map(x=>`<span class=\"profile-chip\">${esc(x)}</span>`).join("");const photo=esc(p.photo_url||'/assets/LexTalkLegal_Logo-wo-bg.png');return `<article class=\"profile-card\"><div class=\"profile-card-top\"><img class=\"profile-avatar\" src=\"${photo}\" alt=\"\" loading=\"lazy\"><div><h3><a href=\"/advocates/${encodeURIComponent(p.slug)}/\">${esc(p.full_name)}</a></h3><div class=\"profile-sub\">${esc(p.designation||'Legal Professional')} · ${esc(p.city||'')}${p.state?', '+esc(p.state):''}</div></div></div><div class=\"profile-chip-row\">${chips}</div></article>`}).join("")}catch(e){list.innerHTML='<div class="empty">Published profiles are temporarily unavailable. Please try again later.</div>';st.textContent=e.message;st.classList.add("show")}}b.addEventListener("click",load);q.addEventListener("keydown",e=>{if(e.key==='Enter')load()});load()})();</script>'''
    (ROOT/'advocates').mkdir(exist_ok=True)
    (ROOT/'advocates/index.html').write_text(profile_layout('Legal Professional Profiles','Free informational legal-professional profiles reviewed for publication.',directory, '/advocates/'),encoding='utf8')
    form='''<main class="utility-page"><div class="profile-hero"><span class="utility-kicker">FREE PROFESSIONAL PROFILE</span><h1>Create Your Professional Profile</h1><p class="lead">Submit factual professional information for review. Every profile is reviewed before publication.</p><div class="notice"><strong>Before submitting:</strong> do not include client-confidential information, case-sensitive material, exaggerated credentials, success-rate claims, guarantees, rankings or promotional statements that may conflict with applicable professional-conduct requirements.</div></div><div id="formStatus" class="form-status"></div><form id="profileForm" class="profile-form"><div class="field"><label>Full name *</label><input name="full_name" required maxlength="120"></div><div class="field"><label>Designation / status *</label><select name="designation" required><option value="">Select</option><option>Advocate</option><option>Law Student</option><option>Legal Researcher</option><option>Legal Academic</option><option>Legal Professional</option><option>Compliance Professional</option></select></div><div class="field"><label>State Bar Council</label><input name="state_bar_council" maxlength="120"></div><div class="field"><label>Enrolment number</label><input name="enrolment_number" maxlength="80"></div><div class="field"><label>Year of enrolment</label><input name="enrolment_year" inputmode="numeric" pattern="\\d{4}" maxlength="4"></div><div class="field"><label>Qualification *</label><input name="qualification" required maxlength="160" placeholder="e.g. LL.B."></div><div class="field"><label>City *</label><input name="city" required maxlength="80"></div><div class="field"><label>State *</label><input name="state" required maxlength="80"></div><div class="field"><label>Public profile photo URL</label><input name="photo_url" type="url" maxlength="500" placeholder="https://..."></div><div class="field"><label>Professional website / LinkedIn</label><input name="professional_url" type="url" maxlength="500" placeholder="https://..."></div><div class="field full"><label>Practice areas</label><input name="practice_areas" maxlength="300" placeholder="e.g. Civil, DRT, SARFAESI, Banking Law"></div><div class="field full"><label>Courts / forums</label><input name="courts_forums" maxlength="300" placeholder="e.g. Delhi High Court, District Courts, DRT"></div><div class="field full"><label>Professional overview</label><textarea name="bio" maxlength="1400" placeholder="Keep this factual and professional."></textarea></div><div class="field"><label>Review email *</label><input name="email" type="email" required maxlength="160"></div><div class="field"><label>Optional phone</label><input name="phone" maxlength="30"></div><div class="field full"><label>Website profile slug</label><input name="slug_hint" maxlength="90" placeholder="Optional — e.g. rahul-sharma"></div><div class="field full"><label class="check-row"><input name="confirm_accuracy" type="checkbox" required><span>I confirm that the information submitted is accurate to the best of my knowledge and I am authorised to submit it for publication.</span></label><label class="check-row"><input name="confirm_publication" type="checkbox" required><span>I understand that the profile may be publicly searchable after administrative review and that publication is not endorsement, recommendation, certification or a guarantee.</span></label><label class="check-row"><input name="confirm_conduct" type="checkbox" required><span>I will not use the profile to make prohibited or misleading claims, disclose confidential information or seek improper solicitation through the platform.</span></label></div><div class="field full"><div class="form-actions"><button class="primary-btn" type="submit">Submit for Review ↗</button><a class="ghost-btn" href="/profile-guidelines.html">Read Profile Guidelines</a></div></div></form><script>(function(){const f=document.getElementById('profileForm'),st=document.getElementById('formStatus');f.addEventListener('submit',async e=>{e.preventDefault();st.classList.add('show');st.textContent='Submitting securely for administrative review…';const fd=new FormData(f),o={};for(const [k,v] of fd.entries())o[k]=v;try{const r=await fetch('/api/profile-submit',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(o)});const d=await r.json();if(!r.ok)throw new Error(d.error||'Unable to submit the profile.');st.textContent='Profile submitted successfully. Your application is pending administrative review.';f.reset()}catch(err){st.textContent=err.message}})})();</script></main>'''
    (ROOT/'advocates/apply.html').write_text(profile_layout('Create Free Professional Profile','Submit a free professional profile for administrative review on Lex Talk Legal.',form,'/advocates/apply',noindex=True),encoding='utf8')
    guidelines=(ROOT/'profile-guidelines.html')
    guidelines.write_text(profile_layout('Professional Profile Guidelines','Rules for free legal-professional profiles on Lex Talk Legal.','''<main class="section-page"><span class="utility-kicker">LEX TALK LEGAL</span><h1>Professional Profile Guidelines</h1><p class="section-lead">Profiles are informational and are published only after administrative review.</p><div class="profile-notice"><strong>Permitted:</strong> factual professional information, qualification, enrolment information, practice areas, courts/forums and professional links that can be appropriately published.</div><div class="profile-notice"><strong>Not permitted:</strong> rankings, “best lawyer” or “No. 1” claims, success-rate claims, guarantees, misleading credentials, confidential/client information, impersonation or prohibited promotional content.</div><div class="notice"><strong>Review process:</strong> Submission → administrative review → publication or return for changes. Material changes may be re-reviewed. “Reviewed for Publication” is an editorial status and is not certification or endorsement.</div><div class="notice"><strong>Privacy:</strong> Do not submit Aadhaar, PAN, residential address, client-confidential records or other unnecessary sensitive documents in the public form. Review email is used for submission communication and is not displayed publicly.</div></main>''','/profile-guidelines.html'),encoding='utf8')
    admin='''<main class="utility-page"><div class="profile-hero"><span class="utility-kicker">ADMINISTRATOR CONSOLE</span><h1>Professional Profile Review</h1><p class="lead">This console is protected by Cloudflare Access and intended only for authorised Lex Talk Legal administrators.</p></div><div id="adminStatus" class="form-status"></div><div id="adminList"><div class="empty">Loading pending profiles…</div></div><script>(async function(){const status=document.getElementById('adminStatus'),list=document.getElementById('adminList');async function load(){try{const r=await fetch('/api/admin/profiles');const d=await r.json();if(!r.ok)throw new Error(d.error||'Admin access required.');if(!d.profiles.length){list.innerHTML='<div class="empty">No profiles are awaiting review.</div>';return;}list.innerHTML=d.profiles.map(p=>`<article class=\"profile-card\" style=\"margin-bottom:12px\"><h3>${p.full_name}</h3><div class=\"profile-sub\">${p.designation||''} · ${p.city||''}, ${p.state||''} · ${p.email||''}</div><p>${p.bio||''}</p><div class=\"card-actions\"><button class=\"primary-btn\" data-id=\"${p.id}\" data-action=\"approved\">Approve</button><button class=\"ghost-btn\" data-id=\"${p.id}\" data-action=\"rejected\">Reject</button><button class=\"ghost-btn\" data-id=\"${p.id}\" data-action=\"suspended\">Suspend</button></div></article>`).join('');}catch(e){list.innerHTML='<div class=\"empty\">Admin console unavailable.</div>';status.textContent=e.message;status.classList.add('show')}}list.addEventListener('click',async e=>{const b=e.target.closest('button[data-id]');if(!b)return;const id=b.dataset.id,action=b.dataset.action;if(!confirm(`Change this profile status to ${action}?`))return;const r=await fetch('/api/admin/profiles',{method:'PATCH',headers:{'content-type':'application/json'},body:JSON.stringify({id,status:action})});const d=await r.json();status.textContent=d.message||d.error||'Done';status.classList.add('show');if(r.ok)load()});load()})();</script></main>'''
    (ROOT/'admin').mkdir(exist_ok=True);(ROOT/'admin/index.html').write_text(profile_layout('Admin — Professional Profiles','Authorised administrator console.',''+admin,'/admin/',noindex=True),encoding='utf8')

def api_slug(s): return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',s.lower())).strip('-')[:80]

def write_worker_and_schema():
    (ROOT/'db').mkdir(exist_ok=True)
    (ROOT/'db/schema.sql').write_text('''PRAGMA foreign_keys=ON;\nCREATE TABLE IF NOT EXISTS profiles (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT NOT NULL UNIQUE, full_name TEXT NOT NULL, designation TEXT NOT NULL, state_bar_council TEXT, enrolment_number TEXT, enrolment_year INTEGER, qualification TEXT NOT NULL, city TEXT NOT NULL, state TEXT NOT NULL, photo_url TEXT, professional_url TEXT, practice_areas TEXT, courts_forums TEXT, bio TEXT, email TEXT NOT NULL, phone TEXT, email_hash TEXT, status TEXT NOT NULL DEFAULT \'pending\' CHECK(status IN (\'pending\',\'under_review\',\'approved\',\'rejected\',\'suspended\')), created_at TEXT NOT NULL, updated_at TEXT NOT NULL);\nCREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles(status);\nCREATE INDEX IF NOT EXISTS idx_profiles_name ON profiles(full_name);\nCREATE INDEX IF NOT EXISTS idx_profiles_location ON profiles(city,state);\nCREATE TABLE IF NOT EXISTS admin_audit (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER, action TEXT NOT NULL, actor_email TEXT, note TEXT, created_at TEXT NOT NULL);\nCREATE INDEX IF NOT EXISTS idx_admin_audit_profile ON admin_audit(profile_id);\n''',encoding='utf8')
    worker=r'''const JSON_HEADERS={'content-type':'application/json; charset=UTF-8','cache-control':'no-store'};
function json(data,status=200,extra={}){return new Response(JSON.stringify(data),{status,headers:{...JSON_HEADERS,...extra}})}
function cleanText(v,max){return String(v??'').replace(/[<>]/g,'').trim().slice(0,max)}
function slugify(v){return String(v||'').toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,70)}
async function shortHash(s){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('').slice(0,8)}
function adminEmails(env){return String(env.ADMIN_EMAILS||'').split(',').map(x=>x.trim().toLowerCase()).filter(Boolean)}
function b64url(s){const pad='='.repeat((4-s.length%4)%4);return atob(s.replace(/-/g,'+').replace(/_/g,'/')+pad)}
function decodeJson(s){try{return JSON.parse(b64url(s))}catch(e){return null}}
async function verifyAccessJWT(request,env){const token=request.headers.get('cf-access-jwt-assertion');if(!token||!env.TEAM_DOMAIN||!env.POLICY_AUD)return null;const parts=token.split('.');if(parts.length!==3)return null;const head=decodeJson(parts[0]),payload=decodeJson(parts[1]);if(!head||!payload||!head.kid)return null;if(payload.exp&&Date.now()/1000>=Number(payload.exp))return null;if(payload.nbf&&Date.now()/1000<Number(payload.nbf))return null;const iss=String(payload.iss||'').replace(/\/$/,'');const team=String(env.TEAM_DOMAIN).replace(/\/$/,'');if(iss!==team)return null;const aud=Array.isArray(payload.aud)?payload.aud.map(String):[String(payload.aud||'')];if(!aud.includes(String(env.POLICY_AUD)))return null;try{const jwks=await fetch(team+'/cdn-cgi/access/certs',{headers:{'accept':'application/json'}}).then(r=>r.ok?r.json():null);const jwk=(jwks?.keys||[]).find(k=>k.kid===head.kid);if(!jwk)return null;const key=await crypto.subtle.importKey('jwk',jwk,{name:'RSASSA-PKCS1-v1_5',hash:'SHA-256'},false,['verify']);const data=new TextEncoder().encode(parts[0]+'.'+parts[1]);const sig=Uint8Array.from(b64url(parts[2]),c=>c.charCodeAt(0));const ok=await crypto.subtle.verify('RSASSA-PKCS1-v1_5',key,sig,data);return ok?payload:null}catch(e){return null}}
async function adminIdentity(request,env){const payload=await verifyAccessJWT(request,env);const email=String(payload?.email||'').trim().toLowerCase();return email&&adminEmails(env).includes(email)?{email}:null}
function safeHttpUrl(v){try{const u=new URL(String(v||''));return ['https:','http:'].includes(u.protocol)?u.toString():''}catch(e){return ''}}
function publicProfile(p){return {id:p.id,slug:p.slug,full_name:p.full_name,designation:p.designation,state_bar_council:p.state_bar_council,enrolment_year:p.enrolment_year,qualification:p.qualification,city:p.city,state:p.state,photo_url:safeHttpUrl(p.photo_url),professional_url:safeHttpUrl(p.professional_url),practice_areas:p.practice_areas,courts_forums:p.courts_forums,bio:p.bio}}
async function profiles(request,env){if(!env.DB)return json({error:'The secure profile database is not active yet.'},503);const u=new URL(request.url);const q=cleanText(u.searchParams.get('q'),80);let stmt;if(q){const like=`%${q.replace(/[%_]/g,'')}%`;stmt=env.DB.prepare("SELECT * FROM profiles WHERE status='approved' AND (full_name LIKE ? OR city LIKE ? OR state LIKE ? OR practice_areas LIKE ?) ORDER BY full_name LIMIT 60").bind(like,like,like,like)}else stmt=env.DB.prepare("SELECT * FROM profiles WHERE status='approved' ORDER BY full_name LIMIT 60");const {results}=await stmt.all();return json({profiles:(results||[]).map(publicProfile)},200,{'cache-control':'public, max-age=60'})}
async function submit(request,env){if(!env.DB)return json({error:'The secure profile database is not active yet. The administrator must activate the D1 profile database before submissions can open.'},503);if(request.method!=='POST')return json({error:'Method not allowed.'},405);let b;try{b=await request.json()}catch(e){return json({error:'Invalid submission.'},400)}const ip=(request.headers.get('CF-Connecting-IP')||'unknown').slice(0,80);const email=cleanText(b.email,160).toLowerCase();const honeypot=String(b.website||'').trim();if(honeypot)return json({message:'Submission received.'},200);if(!email||!email.includes('@'))return json({error:'A valid review email is required.'},400);const full_name=cleanText(b.full_name,120),designation=cleanText(b.designation,60),qualification=cleanText(b.qualification,160),city=cleanText(b.city,80),state=cleanText(b.state,80);if(!full_name||!designation||!qualification||!city||!state)return json({error:'Please complete all required fields.'},400);const now=new Date().toISOString();const key=await shortHash((env.RATE_SALT||'set-a-real-secret')+'|'+ip+'|'+email);const recent=await env.DB.prepare("SELECT COUNT(*) AS c FROM profiles WHERE created_at >= ? AND email_hash = ?").bind(new Date(Date.now()-60*60*1000).toISOString(),key).first().catch(()=>null);if(recent&&Number(recent.c)>3)return json({error:'Too many submissions from this source. Please try again later.'},429);let slug=slugify(cleanText(b.slug_hint,90))||slugify(full_name);slug=`${slug}-${key.slice(0,6)}`;const data={full_name,designation,state_bar_council:cleanText(b.state_bar_council,120),enrolment_number:cleanText(b.enrolment_number,80),enrolment_year:(String(b.enrolment_year||'').match(/^\d{4}$/)?Number(b.enrolment_year):null),qualification,city,state,photo_url:safeHttpUrl(cleanText(b.photo_url,500)),professional_url:safeHttpUrl(cleanText(b.professional_url,500)),practice_areas:cleanText(b.practice_areas,300),courts_forums:cleanText(b.courts_forums,300),bio:cleanText(b.bio,1400),email,phone:cleanText(b.phone,30),email_hash:key,slug,status:'pending',created_at:now,updated_at:now};try{await env.DB.prepare("INSERT INTO profiles (slug,full_name,designation,state_bar_council,enrolment_number,enrolment_year,qualification,city,state,photo_url,professional_url,practice_areas,courts_forums,bio,email,phone,status,created_at,updated_at,email_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)").bind(data.slug,data.full_name,data.designation,data.state_bar_council,data.enrolment_number,data.enrolment_year,data.qualification,data.city,data.state,data.photo_url,data.professional_url,data.practice_areas,data.courts_forums,data.bio,data.email,data.phone,data.status,data.created_at,data.updated_at,data.email_hash).run();return json({ok:true})}catch(e){return json({error:'The profile could not be submitted. Please check the details and try again.'},500)}}
async function adminProfiles(request,env,ctx){const actor=await adminIdentity(request,env);if(!actor)return json({error:'Admin access required.'},403);if(!env.DB)return json({error:'D1 database is not configured.'},503);if(request.method==='GET'){const {results}=await env.DB.prepare("SELECT id,slug,full_name,designation,city,state,email,practice_areas,courts_forums,bio,status,created_at FROM profiles WHERE status IN ('pending','under_review') ORDER BY created_at DESC LIMIT 100").all();return json({profiles:results||[]})}if(request.method==='PATCH'){let b;try{b=await request.json()}catch(e){return json({error:'Invalid request.'},400)}const id=Number(b.id),status=['pending','under_review','approved','rejected','suspended'].includes(b.status)?b.status:null;if(!id||!status)return json({error:'Invalid profile or status.'},400);const now=new Date().toISOString();const p=await env.DB.prepare("SELECT id,slug FROM profiles WHERE id=?").bind(id).first();if(!p)return json({error:'Profile not found.'},404);await env.DB.prepare('UPDATE profiles SET status=?,updated_at=? WHERE id=?').bind(status,now,id).run();await env.DB.prepare('INSERT INTO admin_audit(profile_id,action,actor_email,note,created_at) VALUES (?,?,?,?,?)').bind(id,status,actor.email,'Status changed from admin console.',now).run();return json({ok:true,message:`Profile ${status}.`})}return json({error:'Method not allowed.'},405)}
async function dynamicProfile(request,env){if(!env.DB)return new Response('Profile database is not configured yet.',{status:503,headers:{'content-type':'text/plain; charset=UTF-8'}});const path=new URL(request.url).pathname.replace(/\/$/,'');const slug=decodeURIComponent(path.split('/').pop()||'');if(!slug)return env.ASSETS.fetch(new Request(new URL('/advocates/',request.url),request));const p=await env.DB.prepare("SELECT * FROM profiles WHERE slug=? AND status='approved' LIMIT 1").bind(slug).first();if(!p)return env.ASSETS.fetch(new Request(new URL('/404.html',request.url),request));return new Response(profileHtml(p),{status:200,headers:{'content-type':'text/html; charset=UTF-8','cache-control':'public, max-age=120'}})}
function profileHtml(p){const e=x=>String(x??'').replace(/[&<>\"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[m]));const chips=String(p.practice_areas||'').split(',').map(x=>x.trim()).filter(Boolean).slice(0,10).map(x=>`<span class="profile-chip">${e(x)}</span>`).join('');const photo=e(p.photo_url||'/assets/LexTalkLegal_Logo-wo-bg.png');const external=p.professional_url?`<a class="primary-btn" href="${e(p.professional_url)}" target="_blank" rel="noopener noreferrer">Professional Link ↗</a>`:'';const canonical='https://lextalk.legal/advocates/'+e(p.slug)+'/';const schema=JSON.stringify({'@context':'https://schema.org','@type':'ProfilePage','mainEntity':{'@type':'Person','name':p.full_name,'image':photo,'jobTitle':p.designation||'Legal Professional','url':canonical}}).replace('</','<\\/');return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="${e(p.full_name)} — informational legal-professional profile on Lex Talk Legal."><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="${canonical}"><title>${e(p.full_name)} | Legal Professional Profile | Lex Talk Legal</title><link rel="stylesheet" href="/assets/site.css"><script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3161673810996421" crossorigin="anonymous"></script><script type="application/ld+json">${schema}</script></head><body><div class="site-accent"></div><div class="utility-bar"><div class="wrap utility-inner"><div class="utility-left"><span class="live-dot">●</span><span id="dateLabel">--</span><span class="utility-sep">|</span><span id="timeLabel">--:--:-- IST</span><span class="utility-sep">|</span><span>New Delhi, India</span></div></div></div><header class="masthead"><div class="wrap masthead-inner"><a href="/"><img src="/assets/LexTalkLegal_Logo-wo-bg.png" alt="Lex Talk Legal"></a></div></header><nav class="nav"><div class="wrap nav-inner"><div class="nav-links"><a href="/">Latest</a><a href="/advocates/" class="active">Legal Professionals</a><a href="/category/courts/">Courts</a><a href="/videos/">Videos</a></div><button class="menu-toggle" id="menuBtn" type="button">☰ Menu</button></div><div class="wrap mobile-menu"><a href="/">Latest</a><a href="/advocates/">Legal Professionals</a><a href="/category/courts/">Courts</a><a href="/videos/">Videos</a></div></nav><main class="profile-page"><div class="utility-kicker">LEGAL PROFESSIONAL COMMUNITY</div><div class="profile-header"><img class="profile-large-avatar" src="${photo}" alt=""><div class="profile-title"><h1>${e(p.full_name)}</h1><div class="profile-sub">${e(p.designation||'Legal Professional')} · ${e(p.city||'')}${p.state?', '+e(p.state):''}</div><div style="margin-top:8px"><span class="review-badge">Reviewed for Publication</span></div></div></div><div class="profile-details"><section class="profile-detail-box"><h2>Professional Information</h2><p><strong>Qualification:</strong> ${e(p.qualification)}</p><p><strong>State / Bar Council:</strong> ${e(p.state_bar_council||'Not provided')}</p><p><strong>Year of Enrolment:</strong> ${e(p.enrolment_year||'Not provided')}</p><p><strong>Enrolment Number:</strong> ${e(p.enrolment_number||'Not provided')}</p><p><strong>Location:</strong> ${e(p.city)}, ${e(p.state)}</p></section><section class="profile-detail-box"><h2>Practice &amp; Forums</h2><div class="profile-chip-row">${chips||'<span class="profile-chip">Professional information</span>'}</div><p>${e(p.courts_forums||'Courts / forums not specified.')}</p>${external?`<div style="margin-top:10px">${external}</div>`:''}</section><section class="profile-detail-box" style="grid-column:1/-1"><h2>Professional Overview</h2><p>${e(p.bio||'No additional overview has been provided.')}</p></section></div><div class="profile-disclaimer"><strong>Profile disclaimer:</strong> Information on this page has been submitted by the profile holder and published following Lex Talk Legal’s review process. Publication does not constitute endorsement, recommendation, certification, legal advice, solicitation or a guarantee of outcome. Users should independently verify professional credentials and suitability.</div></main><footer class="footer"><div class="copy">© 2026 LEXBOTICS AI MEDIA LLP | Lex Talk Legal | For Educational &amp; Informational Use Only</div></footer><script src="/assets/site.js" defer></script></body></html>`}
export default {async fetch(request,env,ctx){try{const p=new URL(request.url).pathname;if(p==='/api/profiles')return profiles(request,env);if(p==='/api/profile-submit')return submit(request,env);if(p==='/api/admin/profiles')return adminProfiles(request,env,ctx);if(p==='/admin'||p==='/admin/')return (await adminIdentity(request,env))?env.ASSETS.fetch(new Request(new URL('/admin/index.html',request.url),request)):json({error:'Admin access required.'},403);if(p==='/advocates/apply'||p==='/advocates/apply/')return env.ASSETS.fetch(new Request(new URL('/advocates/apply.html',request.url),request));if(p.startsWith('/advocates/')&&p!='/advocates/')return dynamicProfile(request,env);return env.ASSETS.fetch(request)}catch(e){return json({error:'Unexpected server error.'},500)}}};
'''
    (ROOT/'src').mkdir(exist_ok=True);(ROOT/'src/index.js').write_text(worker,encoding='utf8')


def write_config():
    (ROOT/'wrangler.jsonc').write_text('''{
  "$schema":"https://unpkg.com/wrangler@latest/config-schema.json",
  "name":"lex-talk-legal",
  "main":"src/index.js",
  "compatibility_date":"2026-09-28",
  "assets":{"directory":".","binding":"ASSETS","html_handling":"auto-trailing-slash","run_worker_first":["/api/*","/admin/*","/advocates/*"]},
  "vars":{"SITE_URL":"https://lextalk.legal"}
}
''',encoding='utf8')
    (ROOT/'.assetsignore').write_text('''.git\n.github\nsrc\ndb\nscripts\n*.py\n*.md\n*.txt\nwrangler.jsonc\n.gitignore\n.assetsignore\ndev.vars*\n''',encoding='utf8')
    (ROOT/'robots.txt').write_text('''User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /api/\nDisallow: /advocates/apply\nSitemap: https://lextalk.legal/sitemap.xml\n''',encoding='utf8')
    (ROOT/'_headers').write_text('''/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()\n  Strict-Transport-Security: max-age=31536000; includeSubDomains\n  X-Frame-Options: SAMEORIGIN\n''',encoding='utf8')
    (ROOT/'_redirects').write_text('/advocates/apply /advocates/apply 200\n/admin /admin/ 301\n',encoding='utf8')
    (ROOT/'.well-known').mkdir(exist_ok=True);(ROOT/'.well-known/security.txt').write_text('Contact: mailto:office.lextalklegal@gmail.com\nCanonical: https://lextalk.legal/.well-known/security.txt\nPreferred-Languages: en\n',encoding='utf8')

def main():
    ap=ROOT/'data/articles.json';arts=blogger();
    if not arts:
        try:arts=json.loads(ap.read_text(encoding='utf8'))
        except Exception:arts=[]
    arts=normalize_articles(arts);arts.sort(key=lambda x:x.get('published',''),reverse=True);ap.parent.mkdir(exist_ok=True);ap.write_text(json.dumps(arts,ensure_ascii=False,indent=2),encoding='utf8')
    videos=youtube();videos.sort(key=lambda x:x.get('published',''),reverse=True);(ROOT/'data/youtube.json').write_text(json.dumps(videos,ensure_ascii=False,indent=2),encoding='utf8')
    d=ROOT/'article';d.mkdir(exist_ok=True)
    for f in d.glob('*.html'):f.unlink()
    for a in arts:(d/(slug(a['title'])+'.html')).write_text(article(a),encoding='utf8')
    write_category_pages(arts);write_videos_page(videos);under_construction_page();
    try:vc=extract_onecourt_vc()
    except Exception as e:print('VC extraction skipped:',e);vc=_load_vc_data()
    write_courtrooms_page(vc);write_case_status_page();
    write_profile_pages();sync_homepage(arts,videos);refresh_static_pages()
    # Rebuild sitemap: approved profiles are runtime generated and are intentionally not listed until published; directory is listed.
    urls=['/','/courtrooms/','/case-status/','/videos/','/under-construction.html','/advocates/','/profile-guidelines.html']+[f'/category/{k}/' for k in CATEGORY_MAP]+[a['url'] for a in arts]
    now=datetime.now(timezone.utc).date().isoformat();xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{SITE_URL}{u}</loc><lastmod>{now}</lastmod></url>' for u in dict.fromkeys(urls))+'</urlset>';(ROOT/'sitemap.xml').write_text(xml,encoding='utf8')

if __name__=='__main__':main()
