from pathlib import Path
import os, re, json, html as H, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
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


def category_matches(a, key):
    labels = {str(x).strip().lower() for x in a.get("labels", [])}
    title = str(a.get("title", "")).lower()
    _, terms = CATEGORY_MAP[key]
    if labels & {str(t).strip().lower() for t in terms}:
        return True
    return any(str(term).strip().lower() in title for term in terms)


def write_category_pages(arts):
    for key,(name,_) in CATEGORY_MAP.items():
        items=[a for a in arts if category_matches(a,key)]
        if key in CATEGORY_TEMPLATE_MAP:
            template_path=CATEGORY_TEMPLATE_MAP[key]
            template=template_path.read_text(encoding='utf8')
            if items:
                cards=''.join(article_card(a) for a in items[:CATEGORY_TEMPLATE_LIMIT])
            else:
                empty_class=CATEGORY_TEMPLATE_EMPTY_CLASS.get(key, 'empty')
                cards=f'<div class="{empty_class}">No stories published in this section yet. Publish a Blogger post with the appropriate label and the next editorial sync will update this section.</div>'
            content=template.replace('{{LATEST_STORIES}}', cards)
            desc=f'Lex Talk Legal — {name} news, updates, explainer and official references.'
        elif key in GUIDES:
            g=GUIDES[key]
            cards=''.join(article_card(a) for a in items[:12]) or '<div class="empty">No stories published in this section yet. Publish a Blogger post with the appropriate label and the next automated sync will update this section.</div>'
            content=guide_markup(key).replace(f'<div class="grid" id="latest-guide-{key}"></div>', f'<div class="grid">{cards}</div>')
            desc=f'Lex Talk Legal — {g["name"]}: history, legal framework, practical explainer and latest stories.'
        else:
            cards=''.join(article_card(a) for a in items[:30]) or '<div class="empty">No stories published in this section yet.</div>'
            content=f'<main class="utility-page"><div class="utility-kicker">LEX TALK LEGAL</div><h1>{H.escape(name)}</h1><p class="lead">Latest Lex Talk Legal stories in this section are synced automatically from Blogger.</p><div class="grid">{cards}</div></main>'
            desc=f'Lex Talk Legal — {name} news, updates and explainers.'
        p=ROOT/'category'/key/'index.html'
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(page_shell((name,f'/category/{key}/'),desc,content),encoding='utf8')

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

# Page-specific assets are resolved from the canonical path so recurring builds
# preserve the approved design of each manual/static page.
PAGE_STYLE_MAP = {
    '/about.html': 'about.css',
    '/about': 'about.css',
    '/contact.html': 'contact.css',
    '/contact': 'contact.css',
    '/category/courts/': 'courts.css',
    '/category/law-policy/': 'law-policy.css',
    '/category/banking-law/': 'banking-law.css',
    '/category/dra/': 'dra.css',
    '/videos/': 'videos.css',
    '/case-status/': 'case-status.css',
    '/courtrooms/': 'courtrooms.css',
}

CATEGORY_TEMPLATE_MAP = {
    'courts': ROOT / 'templates/category/courts.html',
    'law-policy': ROOT / 'templates/category/law-policy.html',
    'banking-law': ROOT / 'templates/category/banking-law.html',
    'dra': ROOT / 'templates/category/dra.html',
}

CATEGORY_TEMPLATE_EMPTY_CLASS = {
    'courts': 'courts-v2-empty',
    'law-policy': 'lawpolicy-v2-empty',
    'banking-law': 'banking-v1-empty',
    'dra': 'dra-v1-empty',
}

CATEGORY_TEMPLATE_LIMIT = 12

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
        upd=e.findtext('a:updated',default='',namespaces=NS)
        c=e.find('a:content',NS);raw=c.text if c is not None else ''
        soup=BeautifulSoup(raw or '','html.parser');img=soup.find('img')
        labels=[x.attrib.get('term','') for x in e.findall('a:category',NS) if x.attrib.get('term')]
        text=' '.join(soup.stripped_strings)
        out.append({'title':title,'url':'/article/'+slug(title)+'.html','source_url':link,'published':pub,'updated':upd,'labels':labels,'category':labels[0] if labels else 'Legal News','image':img.get('src') if img else '','excerpt':text[:230]+('…' if len(text)>230 else ''),'content':clean(raw,remove_first_image=True)})
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

BUILD_DT=datetime.now(ZoneInfo('Asia/Kolkata'))
BUILD_TIME=BUILD_DT.strftime('%d %B %Y, %H:%M:%S')
BUILD_EPOCH=int(BUILD_DT.timestamp())

def page_shell(title,description,content):
    t=title[0] if isinstance(title,tuple) else title
    canonical=title[1] if isinstance(title,tuple) else '/'
    robots='index,follow,max-image-preview:large'
    nav=nav_html()
    style_file=PAGE_STYLE_MAP.get(canonical, '')
    page_css=f'<link rel="stylesheet" href="/assets/pages/{H.escape(style_file,quote=True)}">' if style_file else ''
    schema={"@context":"https://schema.org","@type":"WebSite","name":"Lex Talk Legal","url":SITE_URL+"/","description":"Law Simplified for Everyone.","publisher":{"@type":"Organization","name":"LEXBOTICS AI MEDIA LLP","url":SITE_URL+"/"}}
    schema_json=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="{H.escape(description,quote=True)}"><meta name="robots" content="{robots}">
<link rel="canonical" href="{SITE_URL}{H.escape(canonical,quote=True)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Lex Talk Legal"><meta property="og:title" content="{H.escape(t,quote=True)}"><meta property="og:description" content="{H.escape(description,quote=True)}"><meta property="og:url" content="{SITE_URL}{H.escape(canonical,quote=True)}"><meta property="og:image" content="{SITE_URL}/assets/LexTalkLegal_Logo-wo-bg.png"><meta name="twitter:card" content="summary_large_image">
<title>{H.escape(t)} | Lex Talk Legal</title><link rel="stylesheet" href="/assets/site.css">{page_css}<script type="application/ld+json">{schema_json}</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3161673810996421" crossorigin="anonymous"></script></head><body>
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
    schema={'@context':'https://schema.org','@type':'NewsArticle','headline':a.get('title',''),'datePublished':a.get('published',''),'dateModified':a.get('updated') or a.get('published',''),'mainEntityOfPage':{'@type':'WebPage','@id':SITE_URL+a.get('url','')},'author':{'@type':'Organization','name':'Lex Talk Legal Editorial Desk','url':SITE_URL+'/'},'publisher':{'@type':'Organization','name':'LEXBOTICS AI MEDIA LLP','url':SITE_URL+'/'},'description':a.get('excerpt','')}
    if image:schema['image']=[image]
    schema_json=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    desc=a.get('excerpt','')
    body=f'''<main class="article-wrap"><div class="utility-kicker">{H.escape(a.get('category','Legal News'))}</div><div class="story-meta">{H.escape(a.get('published','')[:10])}</div><h1>{H.escape(a.get('title',''))}</h1><div class="article-meta">By Lex Talk Legal Editorial Desk <span>·</span> Educational &amp; informational coverage <span>·</span> <a href="{H.escape(a.get('source_url',''),quote=True)}" target="_blank" rel="noopener noreferrer">Original source</a></div>{hero}<div class="article-body">{body_html}</div><div class="notice"><strong>Editorial note:</strong> This content is for general legal information and education. Verify important legal facts, orders, dates and current procedural requirements from the concerned official source.</div><div class="article-source">Source reference: Original Blogger publication linked above. Lex Talk Legal does not represent that linked third-party content is error-free or current in every respect.</div></main>'''
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
    updated=f'{BUILD_TIME} IST'
    content=f'''<main class="home home-v9"><section class="home-breaking"><div class="wrap ticker-inner"><span class="breaking">LATEST</span><span class="tick">Court updates · Judgments · Banking &amp; Recovery · Auctions · Legal Careers · Practical Legal Awareness</span></div></section><div class="wrap"><section class="home-front section"><div class="home-front-grid"><div>{lead_html}</div><div class="home-secondary-list">{secondary}</div></div><div class="front-fresh">Front page selection: the latest {len(pool) if pool else 0} recent stories are prioritised here; older stories remain available in their sections.</div></section><div class="home-ad ad-wrap"><div class="ad-slot"><span>ADVERTISEMENT</span></div></div><section class="section home-news-section"><div class="home-main-grid"><div><div class="section-head"><div><span class="section-kicker">NEWS DESK</span><h2>Latest Legal News</h2></div><p>Updated {H.escape(updated)}</p></div><div class="home-latest-grid">{latest_html}</div><div class="section-more"><a class="text-link" href="/search.html">View more legal news ↗</a></div></div><aside class="home-quick-rail"><div class="quick-rail-sticky"><div class="quick-rail-title"><span>QUICK DESK</span><strong>Useful links</strong></div><a class="quick-card" href="/auctions/"><span class="quick-icon">🏦</span><span><b>Today’s Auctions</b><small>Bank · FI · Authority</small></span><em>↗</em></a><a class="quick-card" href="/courtrooms/"><span class="quick-icon">⚖</span><span><b>Courtrooms / VC</b><small>Public hearing links</small></span><em>↗</em></a><a class="quick-card" href="/case-status/"><span class="quick-icon">⌕</span><span><b>Case Status</b><small>Official court portals</small></span><em>↗</em></a><a class="quick-card" href="/category/legal-careers/"><span class="quick-icon">▣</span><span><b>Latest Jobs</b><small>Legal careers &amp; opportunities</small></span><em>↗</em></a><div class="ad-slot rail-ad">ADVERTISEMENT</div></div></aside></div></section><section class="section"><div class="section-head"><div><span class="section-kicker">AUCTION DESK</span><h2>Bank, FI &amp; Authority Auctions</h2></div><a class="text-link" href="/auctions/">Open Auction Desk ↗</a></div><div class="auction-home-grid"><article><div class="auction-home-icon">🏦</div><h3>Bank Auctions</h3><p>Residential, commercial and industrial assets notified for public sale.</p></article><article><div class="auction-home-icon">🏢</div><h3>Financial Institution Auctions</h3><p>Publicly notified assets and participation information.</p></article><article><div class="auction-home-icon">🏛</div><h3>Authority Auctions</h3><p>Government and institutional auction notices and updates.</p></article></div><div class="auction-disclaimer">Always read and independently verify the issuing authority’s original auction notice, bidder eligibility, EMD, title/possession position, dues and sale conditions.</div></section><section class="section"><div class="home-service-grid"><article class="home-service case-info"><span class="section-kicker">CASE INFORMATION DESK</span><h2>Have a case file you need to understand?</h2><p>Send a brief description or email relevant documents for consideration. Any review, advice, representation or professional routing is subject to separate consideration and acceptance.</p><div class="service-actions"><a class="primary-btn" href="/case-help.html">Case Information Desk ↗</a><a class="ghost-btn dark-ghost" href="mailto:office.lextalklegal@gmail.com?subject=Case%20Information%20Request">Email the Office</a></div></article><article class="home-service team-info"><span class="section-kicker">OUR ADVOCATE TEAM</span><h2>Courts, Forums &amp; Practice Areas</h2><p>Meet the advocates associated with the platform and view factual information about identified courts/forums and practice areas.</p><div class="team-mini-row"><span>COURTS</span><span>DRT / DRAT</span><span>BANKING &amp; RECOVERY</span><span>CIVIL &amp; COMMERCIAL</span></div><div class="service-actions"><a class="text-link" href="/team.html">Meet the Team ↗</a></div></article></div></section><section class="section"><div class="section-head"><div><span class="section-kicker">EXPLAINED</span><h2>Legal Concepts, Simply Explained</h2></div><a class="text-link" href="/category/explained/">Explore explainers ↗</a></div><div class="explainer-home-grid"><a href="/category/explained/"><span>01</span><b>Understand a Court Order</b><small>Observations, directions &amp; operative portions</small></a><a href="/category/banking-law/"><span>02</span><b>SARFAESI &amp; Recovery</b><small>Process, notices, possession &amp; remedies</small></a><a href="/category/legal-careers/"><span>03</span><b>AIBE &amp; Legal Careers</b><small>Exams, enrolment &amp; practical guidance</small></a></div></section><section class="section"><div class="section-head"><div><span class="section-kicker">WATCH</span><h2>Latest on YouTube</h2></div><a class="text-link" href="/videos/">View all videos ↗</a></div><div class="video-grid home-video-grid">{vid_html}</div></section></div></main><section class="newsletter home-newsletter"><div class="wrap newsletter-inner"><div><span class="section-kicker">THE LEGAL BRIEF</span><h2>Stay updated with important legal developments</h2><p>Selected court updates, judgments, explainers and career information.</p></div><form class="newsletter-form" onsubmit="event.preventDefault();alert('Newsletter signup will be connected to the selected mailing provider before public launch.');"><input type="email" required placeholder="Your email address" aria-label="Your email address"><button class="primary-btn" type="submit">Subscribe</button></form></div></section>'''
    (ROOT/'index.html').write_text(page_shell(('Lex Talk Legal','/'),'Fresh legal news, court updates, judgments, legal education and practical legal awareness.',content),encoding='utf8')


def refresh_static_pages():
    """Compatibility hook for build validation.

    Static/manual pages are intentionally not regenerated here. This keeps
    independently approved page designs stable during editorial syncs.
    """
    return


def write_team_page():
    data=[];tp=ROOT/'data/team.json'
    if tp.exists():
        try:data=json.loads(tp.read_text(encoding='utf8'))
        except Exception:data=[]
    cards=[]
    for member in data:
        name=str(member.get('name','')).strip()
        if not name: continue
        photo=str(member.get('photo','')).strip(); initials=''.join(x[0] for x in name.replace('Adv. ','').split()[:2]).upper() or 'LT'
        media=(f'<div class="team-photo media-frame" style="--media-image:url(&quot;{H.escape(photo,quote=True)}&quot;)"><img src="{H.escape(photo,quote=True)}" alt="{H.escape(name,quote=True)}" loading="lazy" decoding="async"></div>' if photo else f'<div class="team-photo"><div class="team-placeholder">{H.escape(initials)}</div></div>')
        tags=''.join(f'<span>{H.escape(str(t))}</span>' for t in member.get('practice_areas',[])[:5])
        cards.append(f'<article class="team-card">{media}<div class="team-card-body"><div class="team-role">{H.escape(member.get("role","Advocate"))}</div><h2>{H.escape(name)}</h2><p><strong>Courts / Forums:</strong> {H.escape(member.get("courts","To be updated"))}</p><p><strong>Practice Areas:</strong> {H.escape(member.get("areas","To be updated"))}</p><div class="team-tags">{tags}</div></div></article>')
    content=f'''<main class="utility-page"><section class="team-hero"><div><span class="utility-kicker">OUR ADVOCATE TEAM</span><h1>Advocates, Courts &amp; Practice</h1><p>Meet the advocates associated with Lex Talk Legal. This page provides factual professional information for identification and context. It is not a ranking, endorsement, certification or guarantee of outcome.</p></div><div class="team-badge"><strong>LEX TALK LEGAL</strong><span>Law Simplified for Everyone</span></div></section><section class="section"><div class="section-head"><div><span class="section-kicker">THE TEAM</span><h2>Our Advocates</h2></div></div><div class="team-grid">{''.join(cards) if cards else '<div class="empty">Official team photographs and particulars will appear here after they are provided for publication.</div>'}</div></section><section class="notice"><strong>Professional information:</strong> The details displayed are for general identification and context. Lex Talk Legal does not rank or certify advocates and does not guarantee legal results. Credentials and engagement should be independently verified.</section></main>'''
    (ROOT/'team.html').write_text(page_shell(('Our Advocate Team','/team.html'),'Meet the advocates associated with Lex Talk Legal, including courts/forums and areas of practice.',content),encoding='utf8')

def write_case_help_page():
    content='''<main class="utility-page"><span class="utility-kicker">CASE INFORMATION</span><h1>Case Information &amp; Document Review</h1><p class="lead">Share a brief description of your matter with our office. Where appropriate and separately accepted, we may consider the documents for preliminary review and discuss whether a suitable professional can be connected through our team.</p><div class="assist-grid" style="margin-top:22px"><article class="assist-card"><h2>Submit by Email</h2><p>For now, the safer workflow is email-based submission while a dedicated secure document-upload facility is being configured.</p><ul><li>Briefly describe the matter, court/forum and present stage.</li><li>Send only documents you are authorised to share.</li><li>Remove unnecessary personal information where possible.</li><li>Do not send passwords, OTPs, card details or banking credentials.</li></ul><div class="contact-actions"><a class="primary-btn" href="mailto:office.lextalklegal@gmail.com?subject=Case%20Information%20-%20Preliminary%20Review">Email Case Information ↗</a></div></article><article class="assist-card"><h2>Secure Upload — Coming Next</h2><p>A direct upload facility will be activated only after private storage, access controls, retention rules and deletion workflows are configured. This avoids putting case files into an unsecured public form.</p><div class="auction-note">Publication of this page does not create an advocate-client relationship, legal engagement or guarantee of advice/representation. Any engagement is subject to separate acceptance and applicable professional requirements.</div></article></div><div class="notice"><strong>Privacy reminder:</strong> Case files may contain personal, financial and other confidential information. Share only what is necessary. We will not ask for OTPs, passwords or payment credentials through this page.</div></main>'''
    (ROOT/'case-help.html').write_text(page_shell(('Case Information & Document Review','/case-help.html'),'Share case information for preliminary document review and possible professional routing, subject to separate acceptance.',content),encoding='utf8')

def write_auctions_page():
    content='''<main class="utility-page"><section class="guide-hero"><div><span class="utility-kicker">AUCTION DESK</span><h1>Bank, FI &amp; Authority Auctions</h1><p>Information on public auctions conducted by banks, financial institutions and authorities, with a dedicated team for participation and bidding-process assistance.</p><div class="guide-hero-actions"><a class="primary-btn" href="mailto:office.lextalklegal@gmail.com?subject=Auction%20Assistance%20Request">Request Assistance ↗</a><a class="ghost-btn" href="#auction-categories" style="color:var(--text);border-color:var(--line)">How It Works ↓</a></div></div><div class="guide-badge"><div class="guide-badge-icon">🏦</div><strong>AUCTION DESK</strong><span>Verify every original sale notice</span></div></section><section id="auction-categories" class="section"><div class="section-head"><div><span class="section-kicker">COVERAGE</span><h2>What the Auction Desk Can Help With</h2></div></div><div class="auction-grid"><article class="auction-card"><div class="utility-kicker">01</div><h2>Bank &amp; FI Auctions</h2><p>Assistance with locating notices, understanding bidder documentation and navigating the participation workflow.</p></article><article class="auction-card"><div class="utility-kicker">02</div><h2>Authority Auctions</h2><p>Information and participation support for publicly notified auctions, subject to the conditions of the issuing authority.</p></article><article class="auction-card"><div class="utility-kicker">03</div><h2>Document &amp; Notice Check</h2><p>Help organising the notice, deposit terms, timelines and bidder documents before participation.</p></article></div></section><section class="section"><div class="assist-grid"><article class="assist-card"><h2>Before You Bid</h2><ul><li>Read the original sale/auction notice.</li><li>Verify title, possession, dues, encumbrances and statutory disclosures independently.</li><li>Check EMD, eligibility, KYC and bid-deadline requirements.</li><li>Understand inspection, sale terms and payment schedule.</li></ul></article><article class="assist-card"><h2>Request Auction Assistance</h2><p>Send the auction notice or official link, your preferred location/asset type and the intended participation timeline.</p><div class="contact-actions"><a class="primary-btn" href="mailto:office.lextalklegal@gmail.com?subject=Auction%20Assistance%20Request">Email Auction Team ↗</a><a class="ghost-btn" style="color:var(--text);border-color:var(--line)" href="https://wa.me/918368268507?text=I%20need%20auction%20participation%20assistance." target="_blank" rel="noopener noreferrer">WhatsApp Team ↗</a></div></article></div><div class="auction-note"><strong>Important:</strong> Lex Talk Legal / its auction-assistance team does not guarantee allotment, title quality, possession, financing, bidding success or any financial outcome. Final decisions should be based on the issuing authority's original notice and independent due diligence.</div></section></main>'''
    (ROOT/'auctions').mkdir(exist_ok=True)
    (ROOT/'auctions/index.html').write_text(page_shell(('Auction Desk','/auctions/'),'Bank, financial institution and authority auction information with participation-process assistance.',content),encoding='utf8')

def write_search_page():
    content='''<main class="utility-page"><span class="utility-kicker">SEARCH</span><h1>Search Lex Talk Legal</h1><p class="lead">Search recent articles, explainers and legal updates published on Lex Talk Legal.</p><div class="search-box"><input id="siteSearchInput" type="search" placeholder="Search a topic, case, section or keyword" autocomplete="off"><button class="primary-btn" id="siteSearchBtn" type="button">Search</button></div><div id="searchMeta" class="search-meta"></div><div id="searchResults" class="search-results"><div class="empty">Type a keyword to search the latest indexed Lex Talk Legal content.</div></div></main><script>fetch('/data/articles.json').then(r=>r.json()).then(items=>{const input=document.getElementById('siteSearchInput'),btn=document.getElementById('siteSearchBtn'),results=document.getElementById('searchResults'),meta=document.getElementById('searchMeta');const run=()=>{const q=input.value.trim().toLowerCase();if(!q){results.innerHTML='<div class=\"empty\">Type a keyword to search the latest indexed Lex Talk Legal content.</div>';meta.textContent='';return;}const out=items.filter(a=>((a.title||'')+' '+(a.excerpt||'')+' '+(a.category||'')).toLowerCase().includes(q)).slice(0,20);meta.textContent=out.length+' result'+(out.length===1?'':'s');results.innerHTML=out.length?out.map(a=>'<article class=\"search-result\"><div class=\"story-meta\">'+(a.category||'Legal News')+' · '+(a.published||'').slice(0,10)+'</div><h2><a href=\"'+a.url+'\">'+(a.title||'')+'</a></h2><p>'+((a.excerpt||'').replace(/</g,'&lt;'))+'</p></article>').join(''):'<div class=\"empty\">No matching stories found.</div>';};btn.addEventListener('click',run);input.addEventListener('keydown',e=>{if(e.key==='Enter')run();});}).catch(()=>{document.getElementById('searchResults').innerHTML='<div class=\"empty\">Search is temporarily unavailable.</div>';});</script>'''
    (ROOT/'search.html').write_text(page_shell(('Search','/search.html'),'Search Lex Talk Legal for legal news, judgments, explainers and updates.',content),encoding='utf8')

def _article_datetime(value):
    """Parse common ISO/RFC 2822 publication timestamps into an aware UTC datetime."""
    if not value:
        return None
    text=str(value).strip()
    try:
        dt=datetime.fromisoformat(text.replace('Z','+00:00'))
        if dt.tzinfo is None:
            dt=dt.replace(tzinfo=ZoneInfo('Asia/Kolkata'))
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    try:
        return parsedate_to_datetime(text).astimezone(timezone.utc)
    except Exception:
        return None


def write_news_sitemap(arts):
    """Write Google's News sitemap for articles published in the last 48 hours."""
    now=datetime.now(timezone.utc)
    cutoff=now-timedelta(days=2)
    rows=[]
    for a in arts or []:
        dt=_article_datetime(a.get('published'))
        url=str(a.get('url','')).strip()
        title=str(a.get('title','')).strip()
        if not dt or dt < cutoff or not url or not title:
            continue
        rows.append((dt,url,title))
    rows.sort(key=lambda x:x[0], reverse=True)
    rows=rows[:1000]
    items=[]
    for dt,url,title in rows:
        items.append(
            '<url><loc>'+H.escape(SITE_URL+url,quote=False)+'</loc>'
            '<news:news><news:publication><news:name>Lex Talk Legal</news:name>'
            '<news:language>en</news:language></news:publication>'
            '<news:publication_date>'+H.escape(dt.isoformat().replace('+00:00','Z'))+'</news:publication_date>'
            '<news:title>'+H.escape(title)+'</news:title></news:news></url>'
        )
    xml=('<?xml version="1.0" encoding="UTF-8"?>'
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
         'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'
         + ''.join(items) + '</urlset>')
    (ROOT/'news-sitemap.xml').write_text(xml,encoding='utf8')


def write_sitemap(arts):
    """Write a stable XML sitemap with accurate content-derived lastmod values."""
    # Use the site's canonical extensionless routes where the platform redirects
    # the .html asset URL (notably About and Contact).
    static_urls=['/courtrooms/','/case-status/','/videos/','/auctions/','/case-help.html','/team.html','/search.html',
                 '/about','/contact','/privacy-policy.html','/terms-of-use.html','/disclaimer.html',
                 '/editorial-policy.html','/copyright-policy.html','/corrections-grievance.html','/ai-content-policy.html',
                 '/profile-guidelines.html']
    entries=['<url><loc>'+H.escape(SITE_URL+'/',quote=False)+'</loc></url>']
    latest_all=[]
    for a in arts or []:
        dt=_article_datetime(a.get('updated') or a.get('published'))
        if dt:
            latest_all.append(dt)
    if latest_all:
        entries[0]='<url><loc>'+H.escape(SITE_URL+'/',quote=False)+'</loc><lastmod>'+max(latest_all).date().isoformat()+'</lastmod></url>'
    entries += ['<url><loc>'+H.escape(SITE_URL+u,quote=False)+'</loc></url>' for u in static_urls]

    for key in CATEGORY_MAP:
        dates=[]
        for a in arts or []:
            if category_matches(a,key):
                dt=_article_datetime(a.get('updated') or a.get('published'))
                if dt: dates.append(dt)
        loc='<loc>'+H.escape(SITE_URL+f'/category/{key}/',quote=False)+'</loc>'
        last=(' <lastmod>'+max(dates).date().isoformat()+'</lastmod>') if dates else ''
        entries.append('<url>'+loc+last.replace(' ','')+'</url>')

    for a in arts or []:
        url=str(a.get('url','')).strip()
        if not url: continue
        loc='<loc>'+H.escape(SITE_URL+url,quote=False)+'</loc>'
        dt=_article_datetime(a.get('updated') or a.get('published'))
        last=f'<lastmod>{dt.date().isoformat()}</lastmod>' if dt else ''
        entries.append('<url>'+loc+last+'</url>')

    xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(entries)+'</urlset>'
    (ROOT/'sitemap.xml').write_text(xml,encoding='utf8')


def write_config():
    (ROOT/'wrangler.jsonc').write_text('''{
  "$schema":"https://unpkg.com/wrangler@latest/config-schema.json",
  "name":"lex-talk-legal",
  "main":"src/index.js",
  "compatibility_date":"2026-09-28",
  "assets":{"directory":".","binding":"ASSETS"},
  "vars":{"SITE_URL":"https://lextalk.legal"}
}
''',encoding='utf8')
    (ROOT/'.assetsignore').write_text('''.git
.github
src
db
admin
advocates
functions
scripts
*.py
*.md
README*.txt
wrangler.jsonc
.gitignore
.assetsignore
dev.vars*
''',encoding='utf8')
    (ROOT/'robots.txt').write_text('''User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/
Sitemap: https://lextalk.legal/sitemap.xml
Sitemap: https://lextalk.legal/news-sitemap.xml
''',encoding='utf8')
    (ROOT/'ads.txt').write_text('google.com, pub-3161673810996421, DIRECT, f08c47fec0942fa0\n',encoding='utf8')
    (ROOT/'_headers').write_text('''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  X-Frame-Options: SAMEORIGIN

/assets/*
  Cache-Control: public, max-age=86400
''',encoding='utf8')
    (ROOT/'_redirects').write_text('''/admin / 302
/advocates /team.html 301
/advocates/ /team.html 301
/advocates/apply /team.html 301
/advocates/apply/ /team.html 301
''',encoding='utf8')
    (ROOT/'.well-known').mkdir(exist_ok=True)
    (ROOT/'.well-known/security.txt').write_text('Contact: mailto:office.lextalklegal@gmail.com\nCanonical: https://lextalk.legal/.well-known/security.txt\nPreferred-Languages: en\n',encoding='utf8')
    (ROOT/'src/index.js').write_text('''export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      if (/^\\/admin(?:\\/|$)/.test(url.pathname)) return Response.redirect(new URL('/', request.url), 302);
      if (/^\\/advocates(?:\\/|$)/.test(url.pathname)) return Response.redirect(new URL('/team.html', request.url), 301);
      return await env.ASSETS.fetch(request);
    } catch (_) {
      return new Response("Lex Talk Legal — Temporary service error.", {status: 503, headers: {"content-type":"text/plain; charset=UTF-8"}});
    }
  }
};
''',encoding='utf8')

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
    write_team_page();write_case_help_page();write_auctions_page();write_search_page();write_config();sync_homepage(arts,videos);refresh_static_pages();write_news_sitemap(arts)
    # Rebuild the stable public sitemap. Lastmod is derived from content dates, not build time.
    write_sitemap(arts)

if __name__=='__main__':main()
