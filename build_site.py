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


COURTS_PAGE_CSS = '''<style id="courts-page-v2">
.courts-v2{width:min(var(--max),calc(100% - 42px));margin:0 auto;padding:28px 0 70px}
.courts-v2 *{box-sizing:border-box}
.courts-v2-crumb{font:800 10px Arial,sans-serif;letter-spacing:.8px;text-transform:uppercase;color:var(--muted);margin:0 0 12px}
.courts-v2-hero{position:relative;overflow:hidden;display:grid;grid-template-columns:minmax(0,1.25fr) minmax(320px,.75fr);gap:22px;align-items:stretch;padding:30px;border:1px solid var(--line);background:linear-gradient(135deg,var(--paper2) 0%,var(--paper) 70%);box-shadow:var(--shadow)}
.courts-v2-hero:before{content:"";position:absolute;width:320px;height:320px;right:-110px;top:-120px;border:1px solid color-mix(in srgb,var(--gold) 40%,transparent);border-radius:50%;box-shadow:0 0 0 28px color-mix(in srgb,var(--gold) 8%,transparent),0 0 0 56px color-mix(in srgb,var(--gold) 5%,transparent);pointer-events:none}
.courts-v2-kicker{font:900 10px Arial,sans-serif;letter-spacing:1.7px;color:var(--red);text-transform:uppercase;margin-bottom:8px}
.courts-v2-hero h1{font-size:clamp(50px,7vw,84px);line-height:.9;letter-spacing:-2.8px;margin:0 0 18px;max-width:800px}
.courts-v2-hero .hero-lead{font:16px Arial,sans-serif;line-height:1.65;color:var(--muted);max-width:800px;margin:0 0 20px}
.courts-v2-actions{display:flex;flex-wrap:wrap;gap:9px}
.courts-v2-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:0 15px;border:1px solid var(--text);font:900 10px Arial,sans-serif;letter-spacing:.55px;text-transform:uppercase}
.courts-v2-btn.primary{background:var(--text);color:var(--paper)}
.courts-v2-btn.primary:hover{background:var(--red);border-color:var(--red)}
.courts-v2-btn.secondary{background:var(--card);color:var(--text);border-color:var(--line)}
.courts-v2-btn.secondary:hover{border-color:var(--red);color:var(--red)}
.courts-v2-hero-card{position:relative;z-index:1;border:1px solid var(--line);background:var(--card);padding:22px;display:flex;flex-direction:column;justify-content:space-between;min-height:250px}
.courts-v2-hero-card .seal{width:58px;height:58px;border:1px solid var(--gold);border-radius:50%;display:grid;place-items:center;color:var(--gold);font-size:29px;margin-bottom:28px;background:var(--paper)}
.courts-v2-hero-card .mini-kicker{font:900 9px Arial,sans-serif;letter-spacing:1.1px;color:var(--gold);text-transform:uppercase}
.courts-v2-hero-card h2{font-size:24px;line-height:1.05;margin:6px 0 8px}
.courts-v2-hero-card p{font:12px Arial,sans-serif;color:var(--muted);line-height:1.55;margin:0}
.courts-v2-strip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin-top:18px}
.courts-v2-stat{background:var(--card);padding:16px 18px;min-height:112px;transition:transform .18s ease,background .18s ease}
.courts-v2-stat:hover{transform:translateY(-2px);background:var(--paper2)}
.courts-v2-stat .num{font:900 11px Arial,sans-serif;letter-spacing:1px;color:var(--gold)}
.courts-v2-stat h3{font-size:20px;line-height:1.06;margin:7px 0 5px}
.courts-v2-stat p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.45;margin:0}
.courts-v2-section{padding:42px 0 0}
.courts-v2-head{display:flex;align-items:end;justify-content:space-between;gap:18px;border-bottom:2px solid var(--text);padding-bottom:9px;margin-bottom:18px}
.courts-v2-head .eyebrow{font:900 9px Arial,sans-serif;color:var(--red);letter-spacing:1.3px;text-transform:uppercase;margin-bottom:3px}
.courts-v2-head h2{font-size:34px;line-height:1.02;margin:0}
.courts-v2-head p{max-width:430px;margin:0;font:11px Arial,sans-serif;color:var(--muted);line-height:1.5;text-align:right}
.courts-v2-map{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;border:1px solid var(--line);background:var(--line)}
.courts-v2-node{position:relative;background:var(--card);min-height:170px;padding:21px 20px 18px;overflow:hidden}
.courts-v2-node:after{content:"";position:absolute;right:-25px;bottom:-25px;width:86px;height:86px;border:1px solid color-mix(in srgb,var(--red) 23%,transparent);border-radius:50%}
.courts-v2-node .node-no{font:900 10px Arial,sans-serif;color:var(--gold);letter-spacing:1px}
.courts-v2-node .node-icon{font-size:25px;margin:16px 0 9px;filter:saturate(.85)}
.courts-v2-node h3{font-size:20px;line-height:1.05;margin:0 0 6px}
.courts-v2-node p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.5;margin:0;max-width:260px}
.courts-v2-journey{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;border:1px solid var(--line);background:var(--line)}
.courts-v2-journey-step{background:var(--paper2);padding:19px 18px;min-height:132px;position:relative}
.courts-v2-journey-step:not(:last-child):before{content:"→";position:absolute;right:-12px;top:50%;transform:translateY(-50%);width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:var(--text);color:var(--paper);font:900 13px Arial,sans-serif;z-index:2}
.courts-v2-journey-step .no{font:900 10px Arial,sans-serif;color:var(--red);letter-spacing:1px}
.courts-v2-journey-step h3{font-size:18px;line-height:1.08;margin:8px 0 0}
.courts-v2-journey-step p{font:10px Arial,sans-serif;color:var(--muted);line-height:1.45;margin:6px 0 0}
.courts-v2-timeline{position:relative;padding-left:30px}
.courts-v2-timeline:before{content:"";position:absolute;left:9px;top:5px;bottom:5px;width:1px;background:var(--line)}
.courts-v2-timeline-item{position:relative;display:grid;grid-template-columns:92px minmax(0,1fr);gap:20px;padding:0 0 22px}
.courts-v2-timeline-item:before{content:"";position:absolute;left:-26px;top:6px;width:10px;height:10px;border-radius:50%;background:var(--paper);border:2px solid var(--red)}
.courts-v2-timeline-item:last-child{padding-bottom:0}
.courts-v2-year{font:900 11px Arial,sans-serif;color:var(--gold);letter-spacing:1px;text-transform:uppercase;padding-top:2px}
.courts-v2-timeline-item h3{font-size:21px;margin:0 0 5px;line-height:1.05}
.courts-v2-timeline-item p{font:12px Arial,sans-serif;color:var(--muted);line-height:1.55;margin:0;max-width:850px}
.courts-v2-law-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.courts-v2-law{border:1px solid var(--line);background:var(--card);padding:21px;min-height:205px;display:flex;flex-direction:column;box-shadow:0 5px 16px rgba(0,0,0,.03)}
.courts-v2-law .law-type{font:900 9px Arial,sans-serif;letter-spacing:1.2px;color:var(--red);text-transform:uppercase}
.courts-v2-law h3{font-size:21px;line-height:1.05;margin:7px 0 9px}
.courts-v2-law p{font:12px Arial,sans-serif;color:var(--muted);line-height:1.55;margin:0 0 17px}
.courts-v2-law a{margin-top:auto;font:900 10px Arial,sans-serif;color:var(--red);text-transform:uppercase;letter-spacing:.45px}
.courts-v2-tools{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.courts-v2-tool{border:1px solid var(--line);background:var(--paper2);padding:20px;min-height:155px;display:flex;flex-direction:column;justify-content:space-between}
.courts-v2-tool .tool-icon{font-size:24px;margin-bottom:10px}
.courts-v2-tool h3{font-size:20px;line-height:1.05;margin:0 0 6px}
.courts-v2-tool p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.5;margin:0 0 15px}
.courts-v2-tool a{font:900 10px Arial,sans-serif;color:var(--red);text-transform:uppercase;letter-spacing:.45px}
.courts-v2-latest{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.courts-v2-latest .story-card{background:var(--card);border:1px solid var(--line);padding:0 0 15px;box-shadow:0 8px 22px rgba(0,0,0,.045);transition:transform .18s ease,box-shadow .18s ease}
.courts-v2-latest .story-card:hover{transform:translateY(-3px);box-shadow:var(--shadow)}
.courts-v2-latest .story-card .story-image{aspect-ratio:16/9;margin:0}
.courts-v2-latest .story-card .story-meta,.courts-v2-latest .story-card h3,.courts-v2-latest .story-card p{margin-left:15px;margin-right:15px}
.courts-v2-latest .story-card h3{font-size:20px;line-height:1.08;margin-top:7px}
.courts-v2-latest .story-card p{font-size:11px;line-height:1.45;color:var(--muted)}
.courts-v2-empty{border:1px dashed var(--line);padding:26px;background:var(--paper2);font:12px Arial,sans-serif;color:var(--muted);line-height:1.55}
.courts-v2-sources{display:flex;flex-wrap:wrap;gap:8px}
.courts-v2-sources a{display:inline-flex;padding:9px 12px;border:1px solid var(--line);background:var(--card);font:900 9px Arial,sans-serif;color:var(--text);text-transform:uppercase;letter-spacing:.35px}
.courts-v2-sources a:hover{color:var(--red);border-color:var(--red)}
.courts-v2-note{margin-top:26px;border-left:4px solid var(--gold);background:var(--paper2);padding:15px 16px;font:11px Arial,sans-serif;line-height:1.55;color:var(--muted)}
.courts-v2-note strong{color:var(--text)}
@media(max-width:1050px){.courts-v2-hero{grid-template-columns:1fr}.courts-v2-strip{grid-template-columns:repeat(2,minmax(0,1fr))}.courts-v2-map,.courts-v2-journey{grid-template-columns:repeat(2,minmax(0,1fr))}.courts-v2-journey-step:nth-child(2):before{display:none}.courts-v2-tools{grid-template-columns:1fr 1fr}.courts-v2-latest{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:700px){.courts-v2{width:min(var(--max),calc(100% - 28px));padding-top:18px}.courts-v2-hero{padding:22px}.courts-v2-hero h1{font-size:54px;letter-spacing:-1.8px}.courts-v2-hero .hero-lead{font-size:14px}.courts-v2-hero-card{min-height:210px}.courts-v2-strip,.courts-v2-map,.courts-v2-journey,.courts-v2-law-grid,.courts-v2-tools,.courts-v2-latest{grid-template-columns:1fr}.courts-v2-head{align-items:flex-start;flex-direction:column}.courts-v2-head h2{font-size:29px}.courts-v2-head p{text-align:left}.courts-v2-journey-step:not(:last-child):before{display:none}.courts-v2-timeline{padding-left:24px}.courts-v2-timeline-item{grid-template-columns:1fr;gap:5px;padding-bottom:18px}.courts-v2-timeline-item:before{left:-20px}}
@media(prefers-reduced-motion:reduce){.courts-v2-stat,.courts-v2-latest .story-card{transition:none}}
</style>'''


BANKING_PAGE_CSS = """<style id="banking-page-v1">
.banking-v1{width:min(var(--max),calc(100% - 42px));margin:0 auto;padding:28px 0 72px}
.banking-v1 *{box-sizing:border-box}
.banking-v1-crumb{font:800 10px Arial,sans-serif;letter-spacing:.9px;text-transform:uppercase;color:var(--muted);margin:0 0 12px}
.banking-v1-hero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(320px,.65fr);gap:22px;align-items:stretch;padding:30px;border:1px solid var(--line);background:linear-gradient(135deg,var(--paper2) 0%,var(--paper) 68%);box-shadow:var(--shadow);position:relative;overflow:hidden}
.banking-v1-hero:before{content:"";position:absolute;width:360px;height:360px;right:-145px;top:-150px;border:1px solid color-mix(in srgb,var(--gold) 42%,transparent);border-radius:50%;box-shadow:0 0 0 24px color-mix(in srgb,var(--gold) 8%,transparent),0 0 0 50px color-mix(in srgb,var(--gold) 5%,transparent),0 0 0 76px color-mix(in srgb,var(--red) 4%,transparent);pointer-events:none}
.banking-v1-kicker{font:900 10px Arial,sans-serif;letter-spacing:1.7px;color:var(--red);text-transform:uppercase;margin-bottom:8px}
.banking-v1-hero h1{font-size:clamp(48px,7vw,82px);line-height:.9;letter-spacing:-2.8px;margin:0 0 18px;max-width:760px}
.banking-v1-lead{font:16px Arial,sans-serif;line-height:1.65;color:var(--muted);max-width:790px;margin:0 0 20px}
.banking-v1-actions{display:flex;flex-wrap:wrap;gap:9px}
.banking-v1-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:0 15px;border:1px solid var(--text);font:900 10px Arial,sans-serif;letter-spacing:.55px;text-transform:uppercase}
.banking-v1-btn.primary{background:var(--text);color:var(--paper)}
.banking-v1-btn.primary:hover{background:var(--red);border-color:var(--red)}
.banking-v1-btn.secondary{background:var(--card);color:var(--text);border-color:var(--line)}
.banking-v1-btn.secondary:hover{border-color:var(--red);color:var(--red)}
.banking-v1-hero-card{position:relative;z-index:1;background:var(--card);border:1px solid var(--line);padding:21px;display:flex;flex-direction:column;justify-content:space-between;min-height:250px}
.banking-v1-hero-card .ledger-mark{width:62px;height:62px;border:1px solid var(--gold);display:grid;place-items:center;color:var(--gold);font-size:28px;margin-bottom:22px;background:var(--paper)}
.banking-v1-hero-card .mini-kicker{font:900 9px Arial,sans-serif;letter-spacing:1.15px;color:var(--gold);text-transform:uppercase}
.banking-v1-hero-card h2{font-size:25px;line-height:1.03;margin:7px 0 9px}
.banking-v1-hero-card p{font:12px Arial,sans-serif;color:var(--muted);line-height:1.58;margin:0}
.banking-v1-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin-top:18px}
.banking-v1-metric{background:var(--card);padding:17px 17px 15px;min-height:112px;position:relative;overflow:hidden}
.banking-v1-metric:after{content:"";position:absolute;right:-25px;bottom:-25px;width:78px;height:78px;border:1px solid color-mix(in srgb,var(--gold) 27%,transparent);border-radius:50%}
.banking-v1-metric .code{font:900 10px Arial,sans-serif;color:var(--gold);letter-spacing:1px}
.banking-v1-metric h3{font-size:19px;line-height:1.05;margin:8px 0 6px}
.banking-v1-metric p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.45;margin:0;max-width:260px}
.banking-v1-section{padding:42px 0 0}
.banking-v1-head{display:flex;align-items:end;justify-content:space-between;gap:18px;border-bottom:2px solid var(--text);padding-bottom:9px;margin-bottom:18px}
.banking-v1-head .eyebrow{font:900 9px Arial,sans-serif;color:var(--red);letter-spacing:1.3px;text-transform:uppercase;margin-bottom:3px}
.banking-v1-head h2{font-size:34px;line-height:1.02;margin:0}
.banking-v1-head p{max-width:450px;margin:0;font:11px Arial,sans-serif;color:var(--muted);line-height:1.5;text-align:right}
.banking-v1-journey{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;border:1px solid var(--line);background:var(--line)}
.banking-v1-step{background:var(--paper2);padding:20px 17px;min-height:154px;position:relative}
.banking-v1-step:not(:last-child):before{content:"→";position:absolute;right:-12px;top:50%;transform:translateY(-50%);width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:var(--text);color:var(--paper);font:900 13px Arial,sans-serif;z-index:2}
.banking-v1-step .no{font:900 10px Arial,sans-serif;color:var(--red);letter-spacing:1px}
.banking-v1-step h3{font-size:18px;line-height:1.06;margin:9px 0 7px}
.banking-v1-step p{font:10px Arial,sans-serif;color:var(--muted);line-height:1.5;margin:0}
.banking-v1-frameworks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.banking-v1-law{display:grid;grid-template-columns:72px minmax(0,1fr);gap:15px;border:1px solid var(--line);background:var(--card);padding:19px;min-height:175px;box-shadow:0 5px 16px rgba(0,0,0,.03)}
.banking-v1-law .year{font:900 13px Arial,sans-serif;color:var(--gold);letter-spacing:.8px;padding-top:2px}
.banking-v1-law .tag{font:900 9px Arial,sans-serif;color:var(--red);letter-spacing:1.05px;text-transform:uppercase;margin-bottom:5px}
.banking-v1-law h3{font-size:21px;line-height:1.05;margin:0 0 7px}
.banking-v1-law p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.5;margin:0 0 14px}
.banking-v1-law a{font:900 9px Arial,sans-serif;letter-spacing:.5px;color:var(--red);text-transform:uppercase}
.banking-v1-timeline{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.banking-v1-timeline-item{padding:19px 15px;min-height:160px;position:relative;border-right:1px solid var(--line);background:var(--card)}
.banking-v1-timeline-item:last-child{border-right:0}
.banking-v1-timeline-item:before{content:"";position:absolute;left:15px;top:-5px;width:9px;height:9px;border-radius:50%;background:var(--paper);border:2px solid var(--red)}
.banking-v1-timeline-item .year{font:900 11px Arial,sans-serif;letter-spacing:1px;color:var(--gold);text-transform:uppercase;margin-bottom:10px}
.banking-v1-timeline-item h3{font-size:19px;line-height:1.05;margin:0 0 7px}
.banking-v1-timeline-item p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.5;margin:0}
.banking-v1-tools{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.banking-v1-tool{border:1px solid var(--line);background:var(--paper2);padding:18px;min-height:160px;display:flex;flex-direction:column;justify-content:space-between}
.banking-v1-tool .icon{font-size:24px;line-height:1;margin-bottom:12px}
.banking-v1-tool .kicker{font:900 9px Arial,sans-serif;letter-spacing:1.1px;color:var(--red);text-transform:uppercase}
.banking-v1-tool h3{font-size:19px;line-height:1.05;margin:5px 0 6px}
.banking-v1-tool p{font:10px Arial,sans-serif;color:var(--muted);line-height:1.5;margin:0 0 14px}
.banking-v1-tool a{font:900 9px Arial,sans-serif;letter-spacing:.5px;color:var(--red);text-transform:uppercase}
.banking-v1-latest{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.banking-v1-latest .story-card{background:var(--card);border:1px solid var(--line);padding:0 0 15px;box-shadow:0 8px 22px rgba(0,0,0,.045);transition:transform .18s ease,box-shadow .18s ease}
.banking-v1-latest .story-card:hover{transform:translateY(-3px);box-shadow:var(--shadow)}
.banking-v1-latest .story-card .story-image{aspect-ratio:16/9;margin:0}
.banking-v1-latest .story-card .story-meta,.banking-v1-latest .story-card h3,.banking-v1-latest .story-card p{margin-left:15px;margin-right:15px}
.banking-v1-latest .story-card h3{font-size:20px;line-height:1.08;margin-top:7px}
.banking-v1-latest .story-card p{font-size:11px;line-height:1.45;color:var(--muted)}
.banking-v1-empty{border:1px dashed var(--line);padding:26px;background:var(--paper2);font:12px Arial,sans-serif;color:var(--muted);line-height:1.55}
.banking-v1-sources{display:flex;flex-wrap:wrap;gap:8px}
.banking-v1-sources a{display:inline-flex;padding:9px 12px;border:1px solid var(--line);background:var(--card);font:900 9px Arial,sans-serif;color:var(--text);text-transform:uppercase;letter-spacing:.35px}
.banking-v1-sources a:hover{color:var(--red);border-color:var(--red)}
.banking-v1-note{margin-top:24px;border-left:4px solid var(--gold);background:var(--paper2);padding:15px 16px;font:11px Arial,sans-serif;line-height:1.55;color:var(--muted)}
.banking-v1-note strong{color:var(--text)}
@media(max-width:1050px){.banking-v1-hero{grid-template-columns:1fr}.banking-v1-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.banking-v1-journey{grid-template-columns:repeat(2,minmax(0,1fr))}.banking-v1-step:nth-child(2):before,.banking-v1-step:nth-child(4):before{display:none}.banking-v1-frameworks{grid-template-columns:1fr}.banking-v1-timeline{grid-template-columns:repeat(3,minmax(0,1fr))}.banking-v1-timeline-item:nth-child(3){border-right:0}.banking-v1-tools{grid-template-columns:repeat(2,minmax(0,1fr))}.banking-v1-latest{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:700px){.banking-v1{width:min(var(--max),calc(100% - 28px));padding-top:18px}.banking-v1-hero{padding:22px}.banking-v1-hero h1{font-size:54px;letter-spacing:-1.8px}.banking-v1-lead{font-size:14px}.banking-v1-metrics,.banking-v1-journey,.banking-v1-frameworks,.banking-v1-timeline,.banking-v1-tools,.banking-v1-latest{grid-template-columns:1fr}.banking-v1-head{align-items:flex-start;flex-direction:column}.banking-v1-head h2{font-size:29px}.banking-v1-head p{text-align:left}.banking-v1-step:not(:last-child):before{display:none}.banking-v1-timeline-item{border-right:0;border-bottom:1px solid var(--line)}.banking-v1-timeline-item:last-child{border-bottom:0}.banking-v1-timeline-item:before{top:-5px;left:15px}}
@media(prefers-reduced-motion:reduce){.banking-v1-latest .story-card{transition:none}}
</style>"""


DRA_PAGE_CSS = '''<style id="dra-page-v1">
.dra-v1{width:min(var(--max),calc(100% - 42px));margin:0 auto;padding:28px 0 74px}
.dra-v1 *{box-sizing:border-box}
.dra-v1-crumb{font:800 10px Arial,sans-serif;letter-spacing:.9px;text-transform:uppercase;color:var(--muted);margin:0 0 12px}
.dra-v1-hero{position:relative;overflow:hidden;display:grid;grid-template-columns:minmax(0,1.25fr) minmax(320px,.75fr);gap:22px;padding:30px;border:1px solid var(--line);background:linear-gradient(135deg,var(--paper2) 0%,var(--paper) 72%);box-shadow:var(--shadow)}
.dra-v1-hero:before{content:"";position:absolute;width:340px;height:340px;right:-130px;top:-140px;border:1px solid color-mix(in srgb,var(--gold) 42%,transparent);border-radius:50%;box-shadow:0 0 0 24px color-mix(in srgb,var(--gold) 7%,transparent),0 0 0 48px color-mix(in srgb,var(--red) 4%,transparent);pointer-events:none}
.dra-v1-kicker{font:900 10px Arial,sans-serif;letter-spacing:1.7px;color:var(--red);text-transform:uppercase;margin-bottom:8px}
.dra-v1-hero h1{font-size:clamp(54px,7vw,86px);line-height:.88;letter-spacing:-3px;margin:0 0 17px}
.dra-v1-lead{font:16px Arial,sans-serif;line-height:1.65;color:var(--muted);max-width:790px;margin:0 0 20px}
.dra-v1-actions{display:flex;flex-wrap:wrap;gap:9px}
.dra-v1-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:0 15px;border:1px solid var(--text);font:900 10px Arial,sans-serif;letter-spacing:.55px;text-transform:uppercase}
.dra-v1-btn.primary{background:var(--text);color:var(--paper)}
.dra-v1-btn.primary:hover{background:var(--red);border-color:var(--red)}
.dra-v1-btn.secondary{background:var(--card);color:var(--text);border-color:var(--line)}
.dra-v1-btn.secondary:hover{border-color:var(--red);color:var(--red)}
.dra-v1-hero-card{position:relative;z-index:1;background:var(--card);border:1px solid var(--line);padding:22px;display:flex;flex-direction:column;justify-content:space-between;min-height:258px}
.dra-v1-mark{width:64px;height:64px;border:1px solid var(--gold);border-radius:16px;display:grid;place-items:center;color:var(--gold);font-size:30px;margin-bottom:24px;background:var(--paper);box-shadow:inset 0 0 0 6px color-mix(in srgb,var(--gold) 4%,transparent)}
.dra-v1-mini{font:900 9px Arial,sans-serif;letter-spacing:1.15px;color:var(--gold);text-transform:uppercase}
.dra-v1-hero-card h2{font-size:25px;line-height:1.03;margin:7px 0 9px}
.dra-v1-hero-card p{font:12px Arial,sans-serif;color:var(--muted);line-height:1.58;margin:0}
.dra-v1-focus{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin-top:18px}
.dra-v1-focus-card{position:relative;background:var(--card);padding:18px;min-height:132px;overflow:hidden}
.dra-v1-focus-card:after{content:"";position:absolute;right:-23px;bottom:-23px;width:72px;height:72px;border:1px solid color-mix(in srgb,var(--gold) 24%,transparent);border-radius:50%}
.dra-v1-focus-card .code{font:900 10px Arial,sans-serif;color:var(--gold);letter-spacing:1px}
.dra-v1-focus-card h3{font-size:20px;line-height:1.04;margin:8px 0 6px}
.dra-v1-focus-card p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.48;margin:0}
.dra-v1-section{padding-top:44px}
.dra-v1-head{display:flex;align-items:end;justify-content:space-between;gap:18px;border-bottom:2px solid var(--text);padding-bottom:9px;margin-bottom:18px}
.dra-v1-head .eyebrow{font:900 9px Arial,sans-serif;color:var(--red);letter-spacing:1.3px;text-transform:uppercase;margin-bottom:3px}
.dra-v1-head h2{font-size:34px;line-height:1.02;margin:0}
.dra-v1-head p{max-width:470px;margin:0;font:11px Arial,sans-serif;color:var(--muted);line-height:1.5;text-align:right}
.dra-v1-compass{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.dra-v1-compass-card{border:1px solid var(--line);background:var(--card);padding:21px;min-height:175px;display:grid;grid-template-columns:48px minmax(0,1fr);gap:15px;box-shadow:0 5px 16px rgba(0,0,0,.03)}
.dra-v1-compass-card .ico{width:42px;height:42px;display:grid;place-items:center;border:1px solid var(--gold);color:var(--gold);font-size:20px;background:var(--paper)}
.dra-v1-compass-card .tag{font:900 9px Arial,sans-serif;letter-spacing:1.05px;color:var(--red);text-transform:uppercase}
.dra-v1-compass-card h3{font-size:21px;line-height:1.05;margin:6px 0 7px}
.dra-v1-compass-card p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.55;margin:0}
.dra-v1-do-grid{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line);border:1px solid var(--line)}
.dra-v1-do{background:var(--card);padding:22px}
.dra-v1-do.do{border-top:4px solid var(--gold)}
.dra-v1-do.dont{border-top:4px solid var(--red)}
.dra-v1-do .eyebrow{font:900 9px Arial,sans-serif;letter-spacing:1.2px;text-transform:uppercase;color:var(--red);margin-bottom:5px}
.dra-v1-do.do .eyebrow{color:var(--gold)}
.dra-v1-do h3{font-size:26px;margin:0 0 12px}
.dra-v1-do ul{margin:0;padding-left:18px;color:var(--muted);font:12px Arial,sans-serif;line-height:1.65}
.dra-v1-do li{margin-bottom:5px}
.dra-v1-journey{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;border:1px solid var(--line);background:var(--line)}
.dra-v1-step{position:relative;background:var(--paper2);padding:20px 17px;min-height:168px}
.dra-v1-step:not(:last-child):before{content:"→";position:absolute;right:-12px;top:50%;transform:translateY(-50%);width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:var(--text);color:var(--paper);font:900 13px Arial,sans-serif;z-index:2}
.dra-v1-step .no{font:900 10px Arial,sans-serif;color:var(--red);letter-spacing:1px}
.dra-v1-step h3{font-size:18px;line-height:1.06;margin:9px 0 7px}
.dra-v1-step p{font:10px Arial,sans-serif;color:var(--muted);line-height:1.5;margin:0}
.dra-v1-timeline{position:relative;padding-left:28px}
.dra-v1-timeline:before{content:"";position:absolute;left:8px;top:4px;bottom:4px;width:1px;background:var(--line)}
.dra-v1-timeline-item{position:relative;display:grid;grid-template-columns:96px minmax(0,1fr);gap:18px;padding:0 0 21px}
.dra-v1-timeline-item:last-child{padding-bottom:0}
.dra-v1-timeline-item:before{content:"";position:absolute;left:-25px;top:5px;width:10px;height:10px;border-radius:50%;background:var(--paper);border:2px solid var(--red)}
.dra-v1-year{font:900 11px Arial,sans-serif;color:var(--gold);letter-spacing:1px;text-transform:uppercase;padding-top:2px}
.dra-v1-timeline-item h3{font-size:21px;line-height:1.05;margin:0 0 5px}
.dra-v1-timeline-item p{font:12px Arial,sans-serif;color:var(--muted);line-height:1.55;margin:0;max-width:860px}
.dra-v1-laws{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.dra-v1-law{border:1px solid var(--line);background:var(--card);padding:20px;min-height:180px;display:flex;flex-direction:column;box-shadow:0 5px 16px rgba(0,0,0,.03)}
.dra-v1-law .tag{font:900 9px Arial,sans-serif;letter-spacing:1.05px;color:var(--red);text-transform:uppercase}
.dra-v1-law h3{font-size:21px;line-height:1.05;margin:7px 0 8px}
.dra-v1-law p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.55;margin:0 0 15px}
.dra-v1-law a{margin-top:auto;font:900 9px Arial,sans-serif;letter-spacing:.5px;color:var(--red);text-transform:uppercase}
.dra-v1-resources{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.dra-v1-resource{border:1px solid var(--line);background:var(--paper2);padding:18px;min-height:154px;display:flex;flex-direction:column;justify-content:space-between}
.dra-v1-resource .icon{font-size:24px;margin-bottom:10px}
.dra-v1-resource .tag{font:900 9px Arial,sans-serif;letter-spacing:1.1px;color:var(--red);text-transform:uppercase}
.dra-v1-resource h3{font-size:19px;line-height:1.05;margin:5px 0 6px}
.dra-v1-resource p{font:10px Arial,sans-serif;color:var(--muted);line-height:1.5;margin:0 0 14px}
.dra-v1-resource a{font:900 9px Arial,sans-serif;letter-spacing:.5px;color:var(--red);text-transform:uppercase}
.dra-v1-latest{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.dra-v1-latest .story-card{background:var(--card);border:1px solid var(--line);padding:0 0 15px;box-shadow:0 8px 22px rgba(0,0,0,.045);transition:transform .18s ease,box-shadow .18s ease}
.dra-v1-latest .story-card:hover{transform:translateY(-3px);box-shadow:var(--shadow)}
.dra-v1-latest .story-card .story-image{aspect-ratio:16/9;margin:0}
.dra-v1-latest .story-card .story-meta,.dra-v1-latest .story-card h3,.dra-v1-latest .story-card p{margin-left:15px;margin-right:15px}
.dra-v1-latest .story-card h3{font-size:20px;line-height:1.08;margin-top:7px}
.dra-v1-latest .story-card p{font-size:11px;line-height:1.45;color:var(--muted)}
.dra-v1-empty{border:1px dashed var(--line);padding:28px;background:var(--paper2);font:12px Arial,sans-serif;color:var(--muted);line-height:1.55}
.dra-v1-sources{display:flex;flex-wrap:wrap;gap:8px}
.dra-v1-sources a{display:inline-flex;padding:9px 12px;border:1px solid var(--line);background:var(--card);font:900 9px Arial,sans-serif;color:var(--text);text-transform:uppercase;letter-spacing:.35px}
.dra-v1-sources a:hover{color:var(--red);border-color:var(--red)}
.dra-v1-note{margin-top:24px;border-left:4px solid var(--gold);background:var(--paper2);padding:15px 16px;font:11px Arial,sans-serif;line-height:1.55;color:var(--muted)}
.dra-v1-note strong{color:var(--text)}
@media(max-width:1050px){.dra-v1-hero{grid-template-columns:1fr}.dra-v1-focus{grid-template-columns:repeat(2,minmax(0,1fr))}.dra-v1-journey{grid-template-columns:repeat(2,minmax(0,1fr))}.dra-v1-step:nth-child(2):before,.dra-v1-step:nth-child(4):before{display:none}.dra-v1-laws{grid-template-columns:1fr}.dra-v1-resources{grid-template-columns:1fr 1fr}.dra-v1-latest{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:700px){.dra-v1{width:min(var(--max),calc(100% - 28px));padding-top:18px}.dra-v1-hero{padding:22px}.dra-v1-hero h1{font-size:56px;letter-spacing:-2px}.dra-v1-lead{font-size:14px}.dra-v1-focus,.dra-v1-compass,.dra-v1-do-grid,.dra-v1-journey,.dra-v1-laws,.dra-v1-resources,.dra-v1-latest{grid-template-columns:1fr}.dra-v1-head{align-items:flex-start;flex-direction:column}.dra-v1-head h2{font-size:29px}.dra-v1-head p{text-align:left}.dra-v1-step:not(:last-child):before{display:none}.dra-v1-timeline{padding-left:23px}.dra-v1-timeline-item{grid-template-columns:1fr;gap:4px}.dra-v1-timeline-item:before{left:-20px}.dra-v1-compass-card{grid-template-columns:42px 1fr}}
@media(prefers-reduced-motion:reduce){.dra-v1-latest .story-card{transition:none}}
</style>'''


VIDEOS_PAGE_CSS = '''<style id="videos-page-v2">
.videos-v2{width:min(var(--max),calc(100% - 42px));margin:0 auto;padding:28px 0 72px;color:var(--text)}
.videos-v2 *{box-sizing:border-box}.videos-v2 a{text-decoration:none}
.videos-v2-hero{position:relative;overflow:hidden;display:grid;grid-template-columns:minmax(0,1.25fr) minmax(300px,.75fr);gap:22px;padding:30px;border:1px solid var(--line);background:linear-gradient(135deg,var(--paper2) 0%,var(--paper) 72%);box-shadow:var(--shadow)}
.videos-v2-hero:before{content:"";position:absolute;right:-90px;top:-110px;width:330px;height:330px;border:1px solid color-mix(in srgb,var(--red) 26%,transparent);border-radius:50%;box-shadow:0 0 0 30px color-mix(in srgb,var(--gold) 7%,transparent),0 0 0 60px color-mix(in srgb,var(--gold) 4%,transparent);pointer-events:none}
.videos-v2-kicker{font:900 10px Arial,sans-serif;letter-spacing:1.7px;text-transform:uppercase;color:var(--red);margin-bottom:9px}
.videos-v2-hero h1{font-size:clamp(48px,7vw,82px);line-height:.91;letter-spacing:-2.7px;max-width:820px;margin:0 0 16px}
.videos-v2-lead{font:16px Arial,sans-serif;line-height:1.65;color:var(--muted);max-width:780px;margin:0 0 20px}
.videos-v2-actions{display:flex;flex-wrap:wrap;gap:9px}.videos-v2-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:0 15px;border:1px solid var(--text);font:900 10px Arial,sans-serif;letter-spacing:.55px;text-transform:uppercase}
.videos-v2-btn.primary{background:var(--text);color:var(--paper)}.videos-v2-btn.primary:hover{background:var(--red);border-color:var(--red)}
.videos-v2-btn.secondary{background:var(--card);color:var(--text);border-color:var(--line)}.videos-v2-btn.secondary:hover{color:var(--red);border-color:var(--red)}
.videos-v2-panel{position:relative;z-index:1;border:1px solid var(--line);background:var(--card);padding:22px;display:flex;flex-direction:column;justify-content:space-between;min-height:255px}
.videos-v2-panel .play-mark{width:62px;height:62px;border-radius:50%;display:grid;place-items:center;background:var(--red);color:#fff;font-size:25px;box-shadow:0 10px 22px rgba(0,0,0,.14);margin-bottom:34px}
.videos-v2-panel .small{font:900 9px Arial,sans-serif;letter-spacing:1.1px;text-transform:uppercase;color:var(--gold)}
.videos-v2-panel h2{font-size:24px;line-height:1.05;margin:6px 0 8px}.videos-v2-panel p{font:12px Arial,sans-serif;line-height:1.55;color:var(--muted);margin:0}
.videos-v2-panel-bottom{margin-top:18px;padding-top:14px;border-top:1px solid var(--line);font:900 10px Arial,sans-serif;letter-spacing:.7px;text-transform:uppercase;color:var(--text)}
.videos-v2-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;border:1px solid var(--line);background:var(--line);margin-top:18px}
.videos-v2-stat{background:var(--card);padding:15px 17px;min-height:92px}.videos-v2-stat .num{font:900 11px Arial,sans-serif;letter-spacing:1px;color:var(--gold)}.videos-v2-stat h3{font-size:19px;line-height:1.05;margin:6px 0 0}
.videos-v2-section{padding-top:42px}.videos-v2-head{display:flex;align-items:end;justify-content:space-between;gap:18px;border-bottom:2px solid var(--text);padding-bottom:9px;margin-bottom:18px}
.videos-v2-head .eyebrow{font:900 9px Arial,sans-serif;letter-spacing:1.3px;color:var(--red);text-transform:uppercase;margin-bottom:3px}.videos-v2-head h2{font-size:34px;line-height:1.02;margin:0}.videos-v2-head p{font:11px Arial,sans-serif;line-height:1.5;color:var(--muted);margin:0;max-width:430px;text-align:right}
.videos-v2-featured{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(290px,.65fr);gap:20px;border:1px solid var(--line);background:var(--card);overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.04)}
.videos-v2-feature-media{display:block;background:#111;aspect-ratio:16/9;position:relative;overflow:hidden}.videos-v2-feature-media img{width:100%;height:100%;object-fit:contain;background:#111}
.videos-v2-feature-badge{position:absolute;left:14px;top:14px;display:inline-flex;align-items:center;padding:7px 10px;background:var(--text);color:var(--paper);font:900 9px Arial,sans-serif;letter-spacing:1px;text-transform:uppercase}
.videos-v2-feature-play{position:absolute;left:16px;bottom:16px;width:52px;height:38px;border-radius:8px;background:var(--red);color:#fff;display:grid;place-items:center;font-size:19px;box-shadow:0 8px 18px rgba(0,0,0,.25)}
.videos-v2-feature-copy{padding:23px 22px;display:flex;flex-direction:column;justify-content:center}.videos-v2-feature-copy .meta{font:900 10px Arial,sans-serif;letter-spacing:.6px;text-transform:uppercase;color:var(--muted)}
.videos-v2-feature-copy h3{font-size:30px;line-height:1.05;margin:8px 0 11px}.videos-v2-feature-copy p{font:12px Arial,sans-serif;line-height:1.55;color:var(--muted);margin:0 0 17px}
.videos-v2-watch{display:inline-flex;align-items:center;gap:7px;font:900 10px Arial,sans-serif;letter-spacing:.55px;text-transform:uppercase;color:var(--red)}
.videos-v2-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.videos-v2-card{border:1px solid var(--line);background:var(--card);overflow:hidden;box-shadow:0 7px 19px rgba(0,0,0,.035);transition:transform .18s ease,box-shadow .18s ease}.videos-v2-card:hover{transform:translateY(-3px);box-shadow:var(--shadow)}
.videos-v2-thumb{display:block;aspect-ratio:16/9;background:#111;position:relative;overflow:hidden}.videos-v2-thumb img{width:100%;height:100%;object-fit:contain;background:#111}
.videos-v2-play{position:absolute;left:11px;bottom:11px;width:39px;height:29px;border-radius:7px;background:var(--red);color:#fff;display:grid;place-items:center;font:800 14px Arial,sans-serif;box-shadow:0 6px 14px rgba(0,0,0,.22)}
.videos-v2-card-body{padding:13px 14px 15px}.videos-v2-card-date{font:900 9px Arial,sans-serif;letter-spacing:.65px;text-transform:uppercase;color:var(--muted)}.videos-v2-card h3{font-size:19px;line-height:1.12;margin:5px 0 0}
.videos-v2-more{display:flex;align-items:center;justify-content:space-between;gap:15px;margin-top:19px;padding-top:13px;border-top:1px solid var(--line)}.videos-v2-more p{font:11px Arial,sans-serif;line-height:1.5;color:var(--muted);margin:0}
.videos-v2-source{margin-top:36px;border-left:4px solid var(--gold);background:var(--paper2);padding:15px 16px;font:11px Arial,sans-serif;line-height:1.55;color:var(--muted)}.videos-v2-source strong{color:var(--text)}
.videos-v2-empty{border:1px dashed var(--line);padding:28px;background:var(--paper2);font:12px Arial,sans-serif;color:var(--muted)}
@media(max-width:1050px){.videos-v2-hero{grid-template-columns:1fr}.videos-v2-featured{grid-template-columns:1fr}.videos-v2-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:700px){.videos-v2{width:min(var(--max),calc(100% - 28px));padding-top:18px}.videos-v2-hero{padding:22px}.videos-v2-hero h1{font-size:54px;letter-spacing:-1.8px}.videos-v2-lead{font-size:14px}.videos-v2-stats{grid-template-columns:1fr}.videos-v2-head{align-items:flex-start;flex-direction:column}.videos-v2-head h2{font-size:29px}.videos-v2-head p{text-align:left}.videos-v2-grid{grid-template-columns:1fr}.videos-v2-feature-copy h3{font-size:25px}}
@media(prefers-reduced-motion:reduce){.videos-v2-card{transition:none}}
</style>'''


def guide_markup(key):
    g=GUIDES[key]
    timeline=''.join(f'<div class="courts-v2-timeline-item"><div class="courts-v2-year">{H.escape(y)}</div><div><h3>{H.escape(t)}</h3><p>{H.escape(d)}</p></div></div>' for y,t,d in g['history'])
    laws=''.join(f'<article class="courts-v2-law"><div class="law-type">LEGAL FRAMEWORK</div><h3>{H.escape(t)}</h3><p>{H.escape(d)}</p><a href="{H.escape(u,quote=True)}" target="_blank" rel="noopener noreferrer">Open Official Source ↗</a></article>' for t,d,u in g['laws'])
    flow=''.join(f'<article class="courts-v2-journey-step"><div class="no">STEP {i+1:02d}</div><h3>{H.escape(x)}</h3><p>The applicable forum and procedure depend on the dispute, statute and jurisdiction.</p></article>' for i,x in enumerate(g['flow']))
    sources=''.join(f'<a href="{H.escape(u,quote=True)}" target="_blank" rel="noopener noreferrer">{H.escape(t)} ↗</a>' for t,u in g['sources'])

    if key == 'banking-law':
        law_years={'RBI Act, 1934':'1934','Banking Regulation Act, 1949':'1949','SARFAESI Act, 2002':'2002','Recovery of Debts and Bankruptcy Act, 1993':'1993','IBC, 2016':'2016'}
        laws_v1=''.join(f'<article class="banking-v1-law"><div class="year">{H.escape(law_years.get(t,''))}</div><div><div class="tag">LEGAL FRAMEWORK</div><h3>{H.escape(t)}</h3><p>{H.escape(d)}</p><a href="{H.escape(u,quote=True)}" target="_blank" rel="noopener noreferrer">Open Official Source ↗</a></div></article>' for t,d,u in g['laws'])
        timeline_v1=''.join(f'<article class="banking-v1-timeline-item"><div class="year">{H.escape(y)}</div><h3>{H.escape(t)}</h3><p>{H.escape(d)}</p></article>' for y,t,d in g['history'])
        flow_v1=''.join(f'<article class="banking-v1-step"><div class="no">STEP {i+1:02d}</div><h3>{H.escape(x)}</h3><p>The applicable forum and procedure depend on the dispute, statute and jurisdiction.</p></article>' for i,x in enumerate(g['flow']))
        return f'''<main class="banking-v1">
<div class="banking-v1-crumb">Lex Talk Legal / Banking, Credit &amp; Recovery</div>
<section class="banking-v1-hero">
  <div>
    <div class="banking-v1-kicker">BANKING, CREDIT &amp; RECOVERY</div>
    <h1>Banking Law</h1>
    <p class="banking-v1-lead">{H.escape(g['intro'])}</p>
    <div class="banking-v1-actions">
      <a class="banking-v1-btn primary" href="#journey">Explore the Recovery Map ↓</a>
      <a class="banking-v1-btn secondary" href="/category/drt-drat/">DRT / DRAT ↗</a>
      <a class="banking-v1-btn secondary" href="/auctions/">Bank Auctions ↗</a>
    </div>
  </div>
  <aside class="banking-v1-hero-card">
    <div>
      <div class="ledger-mark">₹</div>
      <div class="mini-kicker">THE BANKING LAW DESK</div>
      <h2>From credit to recovery, follow the legal framework.</h2>
      <p>Use this page as a structured starting point for banking regulation, security enforcement, debt-recovery forums, insolvency and practical legal resources.</p>
    </div>
    <div class="mini-kicker">Law · Context · Clarity.</div>
  </aside>
</section>
<section class="banking-v1-metrics" aria-label="Banking law areas">
  <article class="banking-v1-metric"><div class="code">01 / REGULATION</div><h3>Banking Regulation</h3><p>Core statutory and regulatory structures governing banking activity.</p></article>
  <article class="banking-v1-metric"><div class="code">02 / CREDIT</div><h3>Loans &amp; Credit</h3><p>Credit facilities, default triggers, restructuring and related legal issues.</p></article>
  <article class="banking-v1-metric"><div class="code">03 / RECOVERY</div><h3>Security Enforcement</h3><p>SARFAESI, recovery proceedings and specialised tribunal pathways.</p></article>
  <article class="banking-v1-metric"><div class="code">04 / INSOLVENCY</div><h3>IBC &amp; Resolution</h3><p>Insolvency resolution and liquidation within the applicable framework.</p></article>
</section>
<section id="journey" class="banking-v1-section">
  <div class="banking-v1-head"><div><div class="eyebrow">A PRACTICAL VIEW</div><h2>The banking recovery journey</h2></div><p>A matter can move through different legal routes depending on the facts, statute, security, debtor category, forum and procedural stage.</p></div>
  <div class="banking-v1-journey">{flow_v1}</div>
</section>
<section class="banking-v1-section">
  <div class="banking-v1-head"><div><div class="eyebrow">KEY STATUTES</div><h2>Five legal frameworks</h2></div><p>The core statutes mapped in this section, presented as a reference-first dashboard with official source links.</p></div>
  <div class="banking-v1-frameworks">{laws_v1}</div>
</section>
<section class="banking-v1-section">
  <div class="banking-v1-head"><div><div class="eyebrow">QUICK TIMELINE</div><h2>How the framework evolved</h2></div><p>Key milestones from the existing Banking Law explainer, arranged as an editorial timeline.</p></div>
  <div class="banking-v1-timeline">{timeline_v1}</div>
</section>
<section class="banking-v1-section">
  <div class="banking-v1-head"><div><div class="eyebrow">LEGAL UTILITIES</div><h2>Where should you go next?</h2></div><p>Open the relevant Lex Talk Legal section or verify details through the official portal before relying on them.</p></div>
  <div class="banking-v1-tools">
    <article class="banking-v1-tool"><div><div class="icon">⚖</div><div class="kicker">TRIBUNALS</div><h3>DRT / DRAT</h3><p>Explore the specialised debt-recovery tribunal section.</p></div><a href="/category/drt-drat/">Explore DRT / DRAT ↗</a></article>
    <article class="banking-v1-tool"><div><div class="icon">🏦</div><div class="kicker">ASSET SALES</div><h3>Auctions</h3><p>Find publicly notified bank, FI and authority auction information.</p></div><a href="/auctions/">Open Auction Desk ↗</a></article>
    <article class="banking-v1-tool"><div><div class="icon">⌕</div><div class="kicker">CASE SERVICE</div><h3>Case Status</h3><p>Use official court and tribunal portals for current case information.</p></div><a href="/case-status/">Check Case Status ↗</a></article>
    <article class="banking-v1-tool"><div><div class="icon">🎥</div><div class="kicker">HEARINGS</div><h3>Courtrooms / VC</h3><p>Open public courtroom and virtual-hearing destinations.</p></div><a href="/courtrooms/">Open Courtrooms ↗</a></article>
  </div>
</section>
<section id="latest" class="banking-v1-section">
  <div class="banking-v1-head"><div><div class="eyebrow">NEWS DESK</div><h2>Latest Banking Law Stories</h2></div><p>Current banking-law coverage appears here when synced content carries a relevant label or matches the section.</p></div>
  <div class="banking-v1-latest" id="latest-guide-banking-law"></div>
</section>
<section class="banking-v1-section">
  <div class="banking-v1-head"><div><div class="eyebrow">OFFICIAL REFERENCES</div><h2>Primary sources</h2></div><p>Use the linked official portals to verify statutes, regulatory positions, tribunal information and current developments.</p></div>
  <div class="banking-v1-sources">{sources}</div>
  <div class="banking-v1-note"><strong>Editorial note:</strong> This page is for general legal education and information. Statutes, rules, notifications, regulatory directions and case law may change. Readers should verify the current position from the concerned official source.</div>
</section>
</main>'''
    if key == 'dra':
        timeline_dra=''.join(f'<div class="dra-v1-timeline-item"><div class="dra-v1-year">{H.escape(y)}</div><div><h3>{H.escape(t)}</h3><p>{H.escape(d)}</p></div></div>' for y,t,d in g['history'])
        laws_dra=''.join(f'<article class="dra-v1-law"><div class="tag">LEGAL / REGULATORY FRAMEWORK</div><h3>{H.escape(t)}</h3><p>{H.escape(d)}</p><a href="{H.escape(u,quote=True)}" target="_blank" rel="noopener noreferrer">Open Official Source ↗</a></article>' for t,d,u in g['laws'])
        flow_dra=''.join(f'<article class="dra-v1-step"><div class="no">STEP {i+1:02d}</div><h3>{H.escape(x)}</h3><p>The process should remain within the authority given by the regulated entity and the applicable legal / regulatory framework.</p></article>' for i,x in enumerate(g['flow']))
        sources_dra=''.join(f'<a href="{H.escape(u,quote=True)}" target="_blank" rel="noopener noreferrer">{H.escape(t)} ↗</a>' for t,u in g['sources'])
        return f'''<main class="dra-v1">
<div class="dra-v1-crumb">Lex Talk Legal / Debt Recovery Agent Awareness</div>
<section class="dra-v1-hero">
  <div>
    <div class="dra-v1-kicker">DEBT RECOVERY AGENT AWARENESS</div>
    <h1>DRA</h1>
    <p class="dra-v1-lead">{H.escape(g['intro'])}</p>
    <div class="dra-v1-actions">
      <a class="dra-v1-btn primary" href="#journey">Explore the DRA Journey ↓</a>
      <a class="dra-v1-btn secondary" href="#framework">RBI &amp; Legal Framework ↗</a>
      <a class="dra-v1-btn secondary" href="#latest">Latest DRA Stories ↓</a>
    </div>
  </div>
  <aside class="dra-v1-hero-card">
    <div>
      <div class="dra-v1-mark">✓</div>
      <div class="dra-v1-mini">THE DRA COMPLIANCE DESK</div>
      <h2>Recovery work begins with authority, identity and responsible conduct.</h2>
      <p>This guide focuses on role boundaries, borrower interaction, confidentiality, communication, documentation and escalation within the applicable regulatory framework.</p>
    </div>
    <div class="dra-v1-mini">Law · Context · Clarity.</div>
  </aside>
</section>
<section class="dra-v1-focus" aria-label="DRA focus areas">
  <article class="dra-v1-focus-card"><div class="code">01 / ROLE</div><h3>Authority &amp; Identity</h3><p>Work within the assignment or authorisation provided by the regulated entity and identify yourself appropriately.</p></article>
  <article class="dra-v1-focus-card"><div class="code">02 / CONDUCT</div><h3>Respectful Communication</h3><p>Communication should remain fair, lawful and consistent with the applicable recovery-agent directions.</p></article>
  <article class="dra-v1-focus-card"><div class="code">03 / PRIVACY</div><h3>Confidentiality</h3><p>Borrower information and interactions should be handled with appropriate confidentiality and privacy awareness.</p></article>
  <article class="dra-v1-focus-card"><div class="code">04 / RECORDS</div><h3>Documentation &amp; Escalation</h3><p>Maintain proper records, receipts and escalation channels rather than relying on informal pressure.</p></article>
</section>
<section class="dra-v1-section">
  <div class="dra-v1-head"><div><div class="eyebrow">COMPLIANCE COMPASS</div><h2>The four essentials</h2></div><p>A concise view of the practices that shape a responsible recovery interaction, based on the existing DRA awareness material.</p></div>
  <div class="dra-v1-compass">
    <article class="dra-v1-compass-card"><div class="ico">01</div><div><div class="tag">AUTHORISATION</div><h3>Know the assignment</h3><p>Understand the scope of the recovery assignment and remain within the authority delegated by the regulated entity.</p></div></article>
    <article class="dra-v1-compass-card"><div class="ico">02</div><div><div class="tag">COMMUNICATION</div><h3>Identify &amp; communicate clearly</h3><p>Use proper identification and clear, lawful communication when interacting with a borrower.</p></div></article>
    <article class="dra-v1-compass-card"><div class="ico">03</div><div><div class="tag">CONFIDENTIALITY</div><h3>Protect borrower information</h3><p>Respect customer confidentiality and avoid conduct that intrudes on privacy or dignity.</p></div></article>
    <article class="dra-v1-compass-card"><div class="ico">04</div><div><div class="tag">AUDITABILITY</div><h3>Document and escalate</h3><p>Use records, receipts and formal escalation channels so the recovery process remains traceable.</p></div></article>
  </div>
</section>
<section class="dra-v1-section">
  <div class="dra-v1-head"><div><div class="eyebrow">FIELD CONDUCT</div><h2>What responsible recovery looks like</h2></div><p>The following is a practical awareness summary of the conduct principles reflected in the current DRA material.</p></div>
  <div class="dra-v1-do-grid">
    <article class="dra-v1-do do"><div class="eyebrow">DO</div><h3>Use a documented process</h3><ul><li>Carry appropriate authorisation and identification.</li><li>Communicate fairly and lawfully.</li><li>Protect customer confidentiality.</li><li>Maintain records and receipts.</li><li>Use the regulated entity&#39;s grievance / escalation mechanism.</li></ul></article>
    <article class="dra-v1-do dont"><div class="eyebrow">AVOID</div><h3>Prohibited or inappropriate conduct</h3><ul><li>Intimidation or harassment.</li><li>Unwarranted intrusion into privacy.</li><li>Inappropriate communications.</li><li>Recovery calls before 8:00 a.m. or after 7:00 p.m. for overdue-loan recovery, as stated in the cited RBI directions.</li></ul></article>
  </div>
</section>
<section id="journey" class="dra-v1-section">
  <div class="dra-v1-head"><div><div class="eyebrow">A PRACTICAL VIEW</div><h2>The DRA interaction journey</h2></div><p>The sequence can vary by assignment and facts, but the process should stay within the applicable authority and regulatory framework.</p></div>
  <div class="dra-v1-journey">{flow_dra}</div>
</section>
<section class="dra-v1-section">
  <div class="dra-v1-head"><div><div class="eyebrow">QUICK TIMELINE</div><h2>How the guidance evolved</h2></div><p>Key milestones retained from the existing DRA explainer, presented as an editorial timeline.</p></div>
  <div class="dra-v1-timeline">{timeline_dra}</div>
</section>
<section id="framework" class="dra-v1-section">
  <div class="dra-v1-head"><div><div class="eyebrow">LEGAL &amp; REGULATORY FRAMEWORK</div><h2>Know the governing references</h2></div><p>Start with the official RBI and India Code material before relying on any general summary.</p></div>
  <div class="dra-v1-laws">{laws_dra}</div>
</section>
<section class="dra-v1-section">
  <div class="dra-v1-head"><div><div class="eyebrow">PRACTICAL RESOURCES</div><h2>Where to go next</h2></div><p>Use these destinations for current regulatory references, legal texts and grievance information.</p></div>
  <div class="dra-v1-resources">
    <article class="dra-v1-resource"><div><div class="icon">⚖</div><div class="tag">RECOVERY AGENTS</div><h3>RBI directions</h3><p>Review the regulator&#39;s current recovery-agent directions and related guidance.</p></div><a href="https://www.rbi.org.in/" target="_blank" rel="noopener noreferrer">Open RBI ↗</a></article>
    <article class="dra-v1-resource"><div><div class="icon">▣</div><div class="tag">PRIMARY TEXTS</div><h3>India Code</h3><p>Check the statutory text and related central legislation from the official portal.</p></div><a href="https://indiacode.gov.in/" target="_blank" rel="noopener noreferrer">Open India Code ↗</a></article>
    <article class="dra-v1-resource"><div><div class="icon">⌁</div><div class="tag">BORROWER GRIEVANCE</div><h3>RBI Complaint Management</h3><p>Use the applicable complaint and escalation channels where eligible.</p></div><a href="https://cms.rbi.org.in/" target="_blank" rel="noopener noreferrer">Open CMS ↗</a></article>
  </div>
</section>
<section id="latest" class="dra-v1-section">
  <div class="dra-v1-head"><div><div class="eyebrow">NEWS DESK</div><h2>Latest DRA Stories</h2></div><p>Current DRA coverage appears here when synced content carries a relevant label or matches the section.</p></div>
  <div class="dra-v1-latest" id="latest-guide-dra"></div>
</section>
<section class="dra-v1-section">
  <div class="dra-v1-head"><div><div class="eyebrow">OFFICIAL REFERENCES</div><h2>Primary sources</h2></div><p>Use the linked official portals to verify the current regulatory position and available grievance channels.</p></div>
  <div class="dra-v1-sources">{sources_dra}</div>
  <div class="dra-v1-note"><strong>Editorial note:</strong> This page is for general legal education and information. RBI directions, statutes, notifications and other regulatory requirements may change; readers should verify the current position from the relevant official source.</div>
</section>
</main>'''
    if key == 'courts':
        return f'''<main class="courts-v2">
<div class="courts-v2-crumb">Lex Talk Legal / Indian Judiciary Explained</div>
<section class="courts-v2-hero">
  <div>
    <div class="courts-v2-kicker">INDIAN JUDICIARY EXPLAINED</div>
    <h1>Courts</h1>
    <p class="hero-lead">{H.escape(g['intro'])}</p>
    <div class="courts-v2-actions">
      <a class="courts-v2-btn primary" href="#latest">Explore Court Updates ↓</a>
      <a class="courts-v2-btn secondary" href="/case-status/">Check Case Status ↗</a>
      <a class="courts-v2-btn secondary" href="/courtrooms/">Courtrooms &amp; VC ↗</a>
    </div>
  </div>
  <aside class="courts-v2-hero-card">
    <div>
      <div class="seal">⚖</div>
      <div class="mini-kicker">THE COURTS DESK</div>
      <h2>Understand the forum before the filing.</h2>
      <p>Explore the judicial structure, common procedural pathways, key legal frameworks and current court coverage from one place.</p>
    </div>
    <div class="mini-kicker" style="margin-top:18px">Law · Context · Clarity.</div>
  </aside>
</section>
<section class="courts-v2-strip" aria-label="Courts overview">
  <article class="courts-v2-stat"><div class="num">01 / APEX</div><h3>Supreme Court</h3><p>Final appellate and constitutional jurisdiction within the constitutional framework.</p></article>
  <article class="courts-v2-stat"><div class="num">02 / STATE</div><h3>High Courts</h3><p>State-level constitutional courts with appellate and writ jurisdiction as provided by law.</p></article>
  <article class="courts-v2-stat"><div class="num">03 / TRIAL</div><h3>District &amp; Subordinate Courts</h3><p>Trial and other original-jurisdiction forums operating within the subordinate judiciary.</p></article>
  <article class="courts-v2-stat"><div class="num">04 / SPECIALISED</div><h3>Tribunals &amp; e-Courts</h3><p>Specialised statutory forums and digital public court-services form part of the wider justice ecosystem.</p></article>
</section>
<section class="courts-v2-section" id="explainer">
  <div class="courts-v2-head"><div><div class="eyebrow">A COMMON PROCEDURAL VIEW</div><h2>The legal journey</h2></div><p>A matter does not always follow one identical path. The applicable forum depends on the nature of the dispute, statute and jurisdiction.</p></div>
  <div class="courts-v2-journey">{flow}</div>
</section>
<section class="courts-v2-section">
  <div class="courts-v2-head"><div><div class="eyebrow">COURT SYSTEM</div><h2>Where the forums fit</h2></div><p>A practical visual map of the principal court layers and specialised services readers encounter most often.</p></div>
  <div class="courts-v2-map">
    <article class="courts-v2-node"><div class="node-no">01</div><div class="node-icon">⚖</div><h3>Supreme Court</h3><p>India's apex constitutional court and final appellate forum within its jurisdiction.</p></article>
    <article class="courts-v2-node"><div class="node-no">02</div><div class="node-icon">🏛</div><h3>High Courts</h3><p>Constitutional courts serving States and, where applicable, Union Territories.</p></article>
    <article class="courts-v2-node"><div class="node-no">03</div><div class="node-icon">▣</div><h3>District Judiciary</h3><p>District and subordinate courts hear matters assigned under the applicable law and procedure.</p></article>
    <article class="courts-v2-node"><div class="node-no">04</div><div class="node-icon">◈</div><h3>Specialised Forums</h3><p>Statutory tribunals and digital court services operate alongside the court structure.</p></article>
  </div>
</section>
<section class="courts-v2-section">
  <div class="courts-v2-head"><div><div class="eyebrow">HISTORY</div><h2>Quick timeline</h2></div><p>Key moments from the existing Courts explainer, presented as a visual editorial timeline.</p></div>
  <div class="courts-v2-timeline">{timeline}</div>
</section>
<section class="courts-v2-section">
  <div class="courts-v2-head"><div><div class="eyebrow">LAW &amp; PROCEDURE</div><h2>Applicable frameworks</h2></div><p>Core constitutional, procedural and digital-service references linked to official sources.</p></div>
  <div class="courts-v2-law-grid">{laws}</div>
</section>
<section class="courts-v2-section">
  <div class="courts-v2-head"><div><div class="eyebrow">LEGAL UTILITIES</div><h2>Need a court-related service?</h2></div><p>Use Lex Talk Legal as a starting point, then verify current details on the relevant official portal.</p></div>
  <div class="courts-v2-tools">
    <article class="courts-v2-tool"><div><div class="tool-icon">⌕</div><h3>Case Status</h3><p>Find official case-status entry points for courts and tribunals.</p></div><a href="/case-status/">Open Case Status ↗</a></article>
    <article class="courts-v2-tool"><div><div class="tool-icon">🎥</div><h3>Courtrooms &amp; VC</h3><p>Open publicly available courtroom and virtual-hearing destinations.</p></div><a href="/courtrooms/">Open Courtrooms ↗</a></article>
    <article class="courts-v2-tool"><div><div class="tool-icon">⌕</div><h3>Search Coverage</h3><p>Search Lex Talk Legal for judgments, court updates and explainers.</p></div><a href="/search.html">Search the site ↗</a></article>
  </div>
</section>
<section class="courts-v2-section" id="latest">
  <div class="courts-v2-head"><div><div class="eyebrow">NEWS DESK</div><h2>Latest Courts Stories</h2></div><p>Current court coverage appears here when a synced article carries a Courts-related label or matches the Courts section.</p></div>
  <div class="courts-v2-latest" id="latest-guide-courts"></div>
</section>
<section class="courts-v2-section">
  <div class="courts-v2-head"><div><div class="eyebrow">OFFICIAL REFERENCES</div><h2>Primary sources</h2></div><p>Use the linked official source to verify current jurisdiction, statutes, services and historical information.</p></div>
  <div class="courts-v2-sources">{sources}</div>
  <div class="courts-v2-note"><strong>Editorial note:</strong> This page is for general legal education and information. Statutes, rules, notifications, court decisions and digital services may change. Readers should verify the current position from the concerned official source.</div>
</section>
</main>'''
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
        extra_css=''
        if key in GUIDES:
            g=GUIDES[key]
            items=[a for a in arts if category_matches(a,key)]
            cards=''.join(article_card(a) for a in items[:12]) or '<div class="empty">No stories published in this section yet. Publish a Blogger post with the appropriate label and the next automated sync will update this section.</div>'
            content=guide_markup(key)
            if key == "courts":
                content=content.replace('<div class="courts-v2-latest" id="latest-guide-courts"></div>', f'<div class="courts-v2-latest">{cards}</div>')
                extra_css=''
            elif key == "banking-law":
                if not items:
                    cards='<div class="banking-v1-empty">No stories published in this section yet. Publish a Blogger post with the appropriate label and the next automated sync will update this section.</div>'
                content=content.replace('<div class="banking-v1-latest" id="latest-guide-banking-law"></div>', f'<div class="banking-v1-latest">{cards}</div>')
                extra_css=''
            elif key == "dra":
                if not items:
                    cards='<div class="dra-v1-empty">No DRA stories are published in this section yet. Publish a Blogger post with the appropriate DRA label and the next automated sync will update this section.</div>'
                content=content.replace('<div class="dra-v1-latest" id="latest-guide-dra"></div>', f'<div class="dra-v1-latest">{cards}</div>')
                extra_css=''
            else:
                content=content.replace(f'<div class="grid" id="latest-guide-{key}"></div>', f'<div class="grid">{cards}</div>')
                extra_css=''
            desc=f'Lex Talk Legal — {g["name"]}: history, legal framework, practical explainer and latest stories.'
        else:
            items=[a for a in arts if category_matches(a,key)]
            cards=''.join(article_card(a) for a in items[:30]) or '<div class="empty">No stories published in this section yet.</div>'
            content=f'<main class="utility-page"><div class="utility-kicker">LEX TALK LEGAL</div><h1>{H.escape(name)}</h1><p class="lead">Latest Lex Talk Legal stories in this section are synced automatically from Blogger.</p><div class="grid">{cards}</div></main>'
            desc=f'Lex Talk Legal — {name} news, updates and explainers.'
        p=ROOT/'category'/key/'index.html'; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(page_shell((name,f'/category/{key}/'),desc,content,extra_css),encoding='utf8')

def write_videos_page(videos):
    videos=videos[:30]
    if videos:
        featured=videos[0]
        f_thumb=H.escape(featured.get('thumbnail',''),quote=True)
        f_title=H.escape(featured.get('title','Lex Talk Legal'))
        f_date=H.escape(featured.get('published','')[:10])
        f_url=H.escape(featured.get('url','https://www.youtube.com/@LexTalkLegal'),quote=True)
        featured_media=(f'<a class="videos-v2-feature-media" href="{f_url}" target="_blank" rel="noopener noreferrer"><img src="{f_thumb}" alt="{f_title}" loading="eager" decoding="async"><span class="videos-v2-feature-badge">FEATURED VIDEO</span><span class="videos-v2-feature-play" aria-hidden="true">▶</span></a>' if f_thumb else f'<a class="videos-v2-feature-media" href="{f_url}" target="_blank" rel="noopener noreferrer"><div style="height:100%;display:grid;place-items:center;color:#fff;font:900 12px Arial,sans-serif;letter-spacing:1px">LEX TALK LEGAL</div><span class="videos-v2-feature-badge">FEATURED VIDEO</span><span class="videos-v2-feature-play" aria-hidden="true">▶</span></a>')
        featured_copy=f'<div class="videos-v2-feature-copy"><div class="meta">{f_date} · Latest Upload</div><h3>{f_title}</h3><p>Watch the latest Lex Talk Legal video directly on YouTube.</p><a class="videos-v2-watch" href="{f_url}" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></div>'
        feature_html=f'<div class="videos-v2-featured">{featured_media}{featured_copy}</div>'
        rest=videos[1:]
    else:
        feature_html='<div class="videos-v2-empty">No YouTube videos were returned in the latest sync.</div>'
        rest=[]

    def vcard(v):
        thumb=H.escape(v.get('thumbnail',''),quote=True)
        title=H.escape(v.get('title','Lex Talk Legal'))
        date=H.escape(v.get('published','')[:10])
        url=H.escape(v.get('url','https://www.youtube.com/@LexTalkLegal'),quote=True)
        media=f'<img src="{thumb}" alt="{title}" loading="lazy" decoding="async">' if thumb else '<div></div>'
        return f'<article class="videos-v2-card"><a class="videos-v2-thumb" href="{url}" target="_blank" rel="noopener noreferrer">{media}<span class="videos-v2-play" aria-hidden="true">▶</span></a><div class="videos-v2-card-body"><div class="videos-v2-card-date">{date}</div><h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3></div></article>'

    cards=''.join(vcard(v) for v in rest) if rest else ''
    count=len(videos)
    content=f'''<main class="videos-v2">
<div class="videos-v2-hero">
  <div>
    <div class="videos-v2-kicker">LEX TALK LEGAL · VIDEO DESK</div>
    <h1>Watch.<br>Understand.<br>Stay Informed.</h1>
    <p class="videos-v2-lead">Explore the latest Lex Talk Legal videos covering legal developments, court updates, practical legal education and explainers. The library is refreshed automatically from the official YouTube channel.</p>
    <div class="videos-v2-actions">
      <a class="videos-v2-btn primary" href="https://www.youtube.com/@LexTalkLegal" target="_blank" rel="noopener noreferrer">Visit YouTube Channel ↗</a>
      <a class="videos-v2-btn secondary" href="/">Back to Latest News</a>
    </div>
  </div>
  <aside class="videos-v2-panel">
    <div>
      <div class="play-mark">▶</div>
      <div class="small">THE VIDEO DESK</div>
      <h2>Legal information, in a format you can watch.</h2>
      <p>Short updates, explainers and longer-form legal coverage — presented through the Lex Talk Legal video library.</p>
    </div>
    <div class="videos-v2-panel-bottom">Law · Courts · Recovery · Careers</div>
  </aside>
</div>
<div class="videos-v2-stats">
  <div class="videos-v2-stat"><div class="num">01</div><h3>{count} recent videos</h3></div>
  <div class="videos-v2-stat"><div class="num">02</div><h3>Updated from YouTube</h3></div>
  <div class="videos-v2-stat"><div class="num">03</div><h3>Open directly on YouTube</h3></div>
</div>
<section class="videos-v2-section">
  <div class="videos-v2-head"><div><div class="eyebrow">LATEST DROP</div><h2>Featured Video</h2></div><p>Start with the latest upload, then browse the video library below.</p></div>
  {feature_html}
</section>
<section class="videos-v2-section" id="latest-videos">
  <div class="videos-v2-head"><div><div class="eyebrow">VIDEO LIBRARY</div><h2>Latest Videos</h2></div><p>Recent videos appear first. Select any thumbnail or title to watch it on YouTube.</p></div>
  <div class="videos-v2-grid">{cards if cards else '<div class="videos-v2-empty">The latest video library is currently empty.</div>'}</div>
  <div class="videos-v2-more"><p>Video listings are automatically refreshed from the Lex Talk Legal YouTube feed.</p><a class="videos-v2-watch" href="https://www.youtube.com/@LexTalkLegal" target="_blank" rel="noopener noreferrer">Open YouTube ↗</a></div>
</section>
<div class="videos-v2-source"><strong>Editorial note:</strong> Video links open on YouTube. Titles and publication dates displayed on this page are sourced from the current YouTube feed used by Lex Talk Legal. Availability of third-party video content is controlled by YouTube.</div>
</main>'''
    (ROOT/'videos').mkdir(exist_ok=True)
    (ROOT/'videos/index.html').write_text(page_shell(('Latest Videos','/videos/'),'Latest Lex Talk Legal videos, legal news and explainers.',content,''),encoding='utf8')

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
    "/category/courts/": "courts.css",
    "/category/banking-law/": "banking-law.css",
    "/category/dra/": "dra.css",
    "/videos/": "videos.css",
}

ABOUT_PAGE_CSS = '.about-page{--about-max:1260px;color:var(--text);background:var(--paper);overflow:hidden}\n.about-page *{box-sizing:border-box}\n.about-wrap{width:min(var(--about-max),calc(100% - 42px));margin:0 auto}\n.about-hero{position:relative;padding:28px 0 0;background:linear-gradient(135deg,var(--paper2),var(--paper) 68%);border-bottom:1px solid var(--line)}\n.about-hero:before{content:"";position:absolute;right:-160px;top:-190px;width:560px;height:560px;border:1px solid color-mix(in srgb,var(--gold) 34%,transparent);border-radius:50%;box-shadow:0 0 0 35px color-mix(in srgb,var(--gold) 7%,transparent),0 0 0 70px color-mix(in srgb,var(--red) 4%,transparent);pointer-events:none}\n.about-hero-grid{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(320px,.75fr);gap:28px;align-items:stretch;padding:28px 0 32px;position:relative;z-index:1}\n.about-eyebrow,.about-kicker{font:900 10px Arial,sans-serif;letter-spacing:1.4px;text-transform:uppercase;color:var(--gold)}\n.about-hero h1{font-size:clamp(52px,7.2vw,94px);line-height:.86;letter-spacing:-4px;margin:12px 0 18px;max-width:900px}\n.about-hero h1 span{display:inline-block;color:var(--red)}\n.about-hero-deck{font:16px Arial,sans-serif;line-height:1.7;color:var(--muted);max-width:840px;margin:0 0 20px}\n.about-hero-actions,.about-links{display:flex;gap:9px;flex-wrap:wrap}\n.about-mini-btn{display:inline-flex;align-items:center;justify-content:center;border:1px solid var(--line);padding:10px 13px;background:var(--card);font:900 9px Arial,sans-serif;letter-spacing:.65px;text-transform:uppercase;color:var(--text);transition:.18s ease}\n.about-mini-btn:hover{border-color:var(--red);color:var(--red);transform:translateY(-1px)}\n.about-mini-btn.primary{background:var(--text);border-color:var(--text);color:var(--paper)}\n.about-mini-btn.primary:hover{background:var(--red);border-color:var(--red)}\n.about-brand-card{background:var(--card);border:1px solid var(--line);box-shadow:var(--shadow);padding:24px;display:flex;flex-direction:column;justify-content:space-between;min-height:280px;position:relative;overflow:hidden}\n.about-brand-card:after{content:"⚖";position:absolute;right:18px;top:8px;font-size:120px;line-height:1;color:color-mix(in srgb,var(--gold) 16%,transparent)}\n.brand-mark{font:900 10px Arial,sans-serif;letter-spacing:1.4px;color:var(--gold);text-transform:uppercase;position:relative;z-index:1}\n.brand-name{font-size:35px;line-height:1.02;margin-top:12px;position:relative;z-index:1}\n.brand-sub{margin-top:9px;font:11px Arial,sans-serif;line-height:1.5;color:var(--muted);max-width:250px;position:relative;z-index:1}\n.brand-philosophy{border-top:1px solid var(--line);padding-top:14px;font-size:22px;line-height:1.08;position:relative;z-index:1}\n.brand-philosophy small{display:block;font:11px Arial,sans-serif;color:var(--muted);margin-top:6px;letter-spacing:.1px}\n.about-rule{height:5px;border-top:2px solid var(--text);border-bottom:1px solid var(--line)}\n.about-section{padding:54px 0 0}\n.about-section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:22px;border-bottom:2px solid var(--text);padding-bottom:10px;margin-bottom:20px}\n.about-section-head h2{font-size:34px;line-height:1.03;margin:4px 0 0;max-width:720px}\n.about-section-head>p{font:11px Arial,sans-serif;line-height:1.55;color:var(--muted);max-width:450px;text-align:right;margin:0}\n.about-intro{font-size:22px;line-height:1.42;max-width:1000px;margin:0;color:var(--text)}\n.about-grid-2{display:grid;grid-template-columns:1fr 1fr;gap:14px}\n.about-card{border:1px solid var(--line);background:var(--card);padding:25px;min-height:285px;display:flex;flex-direction:column;box-shadow:0 8px 24px rgba(0,0,0,.035);position:relative;overflow:hidden}\n.about-card:after{content:"01";position:absolute;right:-8px;bottom:-28px;font:900 92px Arial,sans-serif;color:color-mix(in srgb,var(--gold) 11%,transparent)}\n.about-vision-card:after{content:"02"}\n.about-card .num{font:900 9px Arial,sans-serif;letter-spacing:1.15px;color:var(--red)}\n.about-card h3{font-size:28px;line-height:1.07;max-width:520px;margin:10px 0 9px;position:relative;z-index:1}\n.about-card>p{font:13px Arial,sans-serif;color:var(--muted);line-height:1.62;max-width:640px;position:relative;z-index:1}\n.quote{margin-top:auto;border-left:4px solid var(--gold);padding:11px 13px;background:var(--paper2);font:12px Georgia,serif;line-height:1.5;position:relative;z-index:1}\n.about-pillars{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line)}\n.about-pillar{background:var(--card);padding:21px;min-height:165px;position:relative}\n.about-pillar:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--gold)}\n.about-pillar strong{display:block;font-size:23px;line-height:1;margin-bottom:9px}\n.about-pillar p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.55;margin:0;max-width:320px}\n.about-coverage{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}\n.about-coverage-card{display:grid;grid-template-columns:52px minmax(0,1fr);gap:14px;border:1px solid var(--line);background:var(--paper2);padding:18px;align-items:start;transition:.18s ease}\n.about-coverage-card:hover{transform:translateY(-2px);background:var(--card);border-color:var(--gold);box-shadow:0 8px 20px rgba(0,0,0,.04)}\n.about-coverage-num{width:40px;height:40px;display:grid;place-items:center;border:1px solid var(--gold);background:var(--card);font:900 11px Arial,sans-serif;color:var(--gold)}\n.about-coverage-card h3{font-size:21px;line-height:1.05;margin:0 0 6px}\n.about-coverage-card p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.5;margin:0}\n.about-audience{display:grid;grid-template-columns:1.05fr .95fr;gap:14px}\n.about-audience-list{border:1px solid var(--line);background:var(--line);display:grid;grid-template-columns:1fr 1fr;gap:1px}\n.about-audience-item{background:var(--card);padding:21px;min-height:150px}\n.about-audience-item h3{font-size:21px;margin:0 0 6px}\n.about-audience-item p{font:11px Arial,sans-serif;color:var(--muted);line-height:1.52;margin:0}\n.about-quote-panel{border:1px solid var(--text);background:var(--text);color:var(--paper);padding:27px;display:flex;flex-direction:column;justify-content:center;min-height:300px;position:relative;overflow:hidden}\n.about-quote-panel:after{content:"LAW";position:absolute;right:-12px;bottom:-38px;font:900 120px Arial,sans-serif;color:color-mix(in srgb,var(--gold) 18%,transparent)}\n.big-quote{font-size:30px;line-height:1.06;margin:0 0 16px;position:relative;z-index:1}\n.big-quote span{color:#e1b94e}\n.about-quote-panel>p:last-child{font:12px Arial,sans-serif;line-height:1.6;color:#c8cdd1;max-width:470px;position:relative;z-index:1}\n.about-process{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;border:1px solid var(--line);background:var(--line)}\n.about-process-step{background:var(--card);padding:21px;min-height:190px;position:relative}\n.about-process-step:not(:last-child):after{content:"→";position:absolute;right:-12px;top:50%;transform:translateY(-50%);width:24px;height:24px;border-radius:50%;background:var(--text);color:var(--paper);display:grid;place-items:center;font:900 13px Arial,sans-serif;z-index:2}\n.about-step-num{font:900 10px Arial,sans-serif;letter-spacing:1px;color:var(--red)}\n.about-process-step h3{font-size:23px;margin:9px 0 7px}\n.about-process-step p{font:11px Arial,sans-serif;line-height:1.55;color:var(--muted);margin:0}\n.about-ai{display:grid;grid-template-columns:1.1fr .9fr;gap:14px}\n.about-ai-main,.about-ai-side{border:1px solid var(--line);background:var(--card);padding:24px}\n.about-ai-main h3,.about-ai-side h3{font-size:26px;line-height:1.08;margin:0 0 8px}\n.about-ai-main>p,.about-ai-side li{font:12px Arial,sans-serif;line-height:1.6;color:var(--muted)}\n.about-note{border-left:4px solid var(--gold);background:var(--paper2);padding:15px;margin-top:20px}\n.about-note h3{font-size:20px;margin:0 0 4px}\n.about-note p{margin:0;font:11px Arial,sans-serif;line-height:1.55;color:var(--muted)}\n.about-ai-side{background:var(--text);color:var(--paper)}\n.side-label{font:900 9px Arial,sans-serif;color:#e1b94e;letter-spacing:1.1px;text-transform:uppercase;margin-bottom:7px}\n.about-ai-side h3{color:#fff}\n.about-ai-side ul{margin:14px 0 0;padding-left:18px}\n.about-ai-side li{color:#c7ccd0;margin-bottom:7px}\n.about-smallprint{margin-top:15px;font:11px Arial,sans-serif;line-height:1.55;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}\n.about-cta{margin:54px auto 72px;border:1px solid var(--text);background:var(--text);color:var(--paper);padding:27px 29px;display:flex;align-items:center;justify-content:space-between;gap:18px;position:relative;overflow:hidden}\n.about-cta:after{content:"LEX";position:absolute;right:-5px;bottom:-48px;font:900 130px Arial,sans-serif;color:rgba(255,255,255,.07);pointer-events:none}\n.about-cta h2{font-size:34px;line-height:1;margin:0 0 7px;position:relative;z-index:1}\n.about-cta p{font:12px Arial,sans-serif;line-height:1.55;color:#c9ced3;margin:0;max-width:700px;position:relative;z-index:1}\n.about-cta>a{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 15px;background:var(--red);border:1px solid var(--red);color:#fff;font:900 10px Arial,sans-serif;text-transform:uppercase;position:relative;z-index:1;white-space:nowrap}\n@media(max-width:1050px){.about-hero-grid{grid-template-columns:1fr}.about-brand-card{min-height:230px}.about-pillars{grid-template-columns:repeat(2,minmax(0,1fr))}.about-process{grid-template-columns:repeat(2,minmax(0,1fr))}.about-process-step:nth-child(2):after{display:none}.about-audience{grid-template-columns:1fr}.about-ai{grid-template-columns:1fr}}\n@media(max-width:700px){.about-wrap{width:min(var(--about-max),calc(100% - 28px))}.about-hero{padding-top:18px}.about-hero-grid{padding:20px 0 24px}.about-hero h1{font-size:54px;letter-spacing:-2px}.about-hero-deck{font-size:14px}.about-section{padding-top:38px}.about-section-head{align-items:flex-start;flex-direction:column}.about-section-head h2{font-size:29px}.about-section-head>p{text-align:left}.about-intro{font-size:19px}.about-grid-2,.about-pillars,.about-coverage,.about-audience-list,.about-process{grid-template-columns:1fr}.about-process-step:not(:last-child):after{display:none}.about-card h3{font-size:24px}.about-ai-main h3,.about-ai-side h3{font-size:23px}.big-quote{font-size:26px}.about-cta{align-items:flex-start;flex-direction:column;margin-bottom:48px}.about-cta h2{font-size:29px}.about-cta>a{width:100%}}'

def write_page_style_assets():
    page_dir = ROOT / 'assets' / 'pages'
    page_dir.mkdir(parents=True, exist_ok=True)
    css_map = {
        'about.css': ABOUT_PAGE_CSS,
        'courts.css': COURTS_PAGE_CSS,
        'banking-law.css': BANKING_PAGE_CSS,
        'dra.css': DRA_PAGE_CSS,
        'videos.css': VIDEOS_PAGE_CSS,
    }
    for filename, block in css_map.items():
        # Accept the historical <style> constants used by earlier builds.
        css = re.sub(r'^<style[^>]*>\\s*', '', block.strip(), flags=re.S)
        css = re.sub(r'\\s*</style>\\s*$', '', css, flags=re.S)
        (page_dir / filename).write_text(css + '\\n', encoding='utf8')


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
    updated=f'{BUILD_TIME} IST'
    content=f'''<main class="home home-v9"><section class="home-breaking"><div class="wrap ticker-inner"><span class="breaking">LATEST</span><span class="tick">Court updates · Judgments · Banking &amp; Recovery · Auctions · Legal Careers · Practical Legal Awareness</span></div></section><div class="wrap"><section class="home-front section"><div class="home-front-grid"><div>{lead_html}</div><div class="home-secondary-list">{secondary}</div></div><div class="front-fresh">Front page selection: the latest {len(pool) if pool else 0} recent stories are prioritised here; older stories remain available in their sections.</div></section><div class="home-ad ad-wrap"><div class="ad-slot"><span>ADVERTISEMENT</span></div></div><section class="section home-news-section"><div class="home-main-grid"><div><div class="section-head"><div><span class="section-kicker">NEWS DESK</span><h2>Latest Legal News</h2></div><p>Updated {H.escape(updated)}</p></div><div class="home-latest-grid">{latest_html}</div><div class="section-more"><a class="text-link" href="/search.html">View more legal news ↗</a></div></div><aside class="home-quick-rail"><div class="quick-rail-sticky"><div class="quick-rail-title"><span>QUICK DESK</span><strong>Useful links</strong></div><a class="quick-card" href="/auctions/"><span class="quick-icon">🏦</span><span><b>Today’s Auctions</b><small>Bank · FI · Authority</small></span><em>↗</em></a><a class="quick-card" href="/courtrooms/"><span class="quick-icon">⚖</span><span><b>Courtrooms / VC</b><small>Public hearing links</small></span><em>↗</em></a><a class="quick-card" href="/case-status/"><span class="quick-icon">⌕</span><span><b>Case Status</b><small>Official court portals</small></span><em>↗</em></a><a class="quick-card" href="/category/legal-careers/"><span class="quick-icon">▣</span><span><b>Latest Jobs</b><small>Legal careers &amp; opportunities</small></span><em>↗</em></a><div class="ad-slot rail-ad">ADVERTISEMENT</div></div></aside></div></section><section class="section"><div class="section-head"><div><span class="section-kicker">AUCTION DESK</span><h2>Bank, FI &amp; Authority Auctions</h2></div><a class="text-link" href="/auctions/">Open Auction Desk ↗</a></div><div class="auction-home-grid"><article><div class="auction-home-icon">🏦</div><h3>Bank Auctions</h3><p>Residential, commercial and industrial assets notified for public sale.</p></article><article><div class="auction-home-icon">🏢</div><h3>Financial Institution Auctions</h3><p>Publicly notified assets and participation information.</p></article><article><div class="auction-home-icon">🏛</div><h3>Authority Auctions</h3><p>Government and institutional auction notices and updates.</p></article></div><div class="auction-disclaimer">Always read and independently verify the issuing authority’s original auction notice, bidder eligibility, EMD, title/possession position, dues and sale conditions.</div></section><section class="section"><div class="home-service-grid"><article class="home-service case-info"><span class="section-kicker">CASE INFORMATION DESK</span><h2>Have a case file you need to understand?</h2><p>Send a brief description or email relevant documents for consideration. Any review, advice, representation or professional routing is subject to separate consideration and acceptance.</p><div class="service-actions"><a class="primary-btn" href="/case-help.html">Case Information Desk ↗</a><a class="ghost-btn dark-ghost" href="mailto:office.lextalklegal@gmail.com?subject=Case%20Information%20Request">Email the Office</a></div></article><article class="home-service team-info"><span class="section-kicker">OUR ADVOCATE TEAM</span><h2>Courts, Forums &amp; Practice Areas</h2><p>Meet the advocates associated with the platform and view factual information about identified courts/forums and practice areas.</p><div class="team-mini-row"><span>COURTS</span><span>DRT / DRAT</span><span>BANKING &amp; RECOVERY</span><span>CIVIL &amp; COMMERCIAL</span></div><div class="service-actions"><a class="text-link" href="/team.html">Meet the Team ↗</a></div></article></div></section><section class="section"><div class="section-head"><div><span class="section-kicker">EXPLAINED</span><h2>Legal Concepts, Simply Explained</h2></div><a class="text-link" href="/category/explained/">Explore explainers ↗</a></div><div class="explainer-home-grid"><a href="/category/explained/"><span>01</span><b>Understand a Court Order</b><small>Observations, directions &amp; operative portions</small></a><a href="/category/banking-law/"><span>02</span><b>SARFAESI &amp; Recovery</b><small>Process, notices, possession &amp; remedies</small></a><a href="/category/legal-careers/"><span>03</span><b>AIBE &amp; Legal Careers</b><small>Exams, enrolment &amp; practical guidance</small></a></div></section><section class="section"><div class="section-head"><div><span class="section-kicker">WATCH</span><h2>Latest on YouTube</h2></div><a class="text-link" href="/videos/">View all videos ↗</a></div><div class="video-grid home-video-grid">{vid_html}</div></section></div></main><section class="newsletter home-newsletter"><div class="wrap newsletter-inner"><div><span class="section-kicker">THE LEGAL BRIEF</span><h2>Stay updated with important legal developments</h2><p>Selected court updates, judgments, explainers and career information.</p></div><form class="newsletter-form" onsubmit="event.preventDefault();alert('Newsletter signup will be connected to the selected mailing provider before public launch.');"><input type="email" required placeholder="Your email address" aria-label="Your email address"><button class="primary-btn" type="submit">Subscribe</button></form></div></section>'''
    (ROOT/'index.html').write_text(page_shell(('Lex Talk Legal','/'),'Fresh legal news, court updates, judgments, legal education and practical legal awareness.',content),encoding='utf8')


def refresh_static_pages():
    preserve={'team.html','case-help.html','auctions/index.html'}
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

def write_config():
    (ROOT/'wrangler.jsonc').write_text('''{
  "$schema":"https://unpkg.com/wrangler@latest/config-schema.json",
  "name":"lex-talk-legal",
  "main":"src/index.js",
  "compatibility_date":"2026-09-28",
  "workers_dev":true,
  "assets":{"directory":".","binding":"ASSETS"},
  "vars":{"SITE_URL":"https://lextalk.legal"}
}
''',encoding='utf8')
    (ROOT/'.assetsignore').write_text('''# Cloudflare Workers Static Assets exclusions
.git
.git/**
.github
.github/**
node_modules
node_modules/**
**/node_modules
.wrangler
.wrangler/**
src
src/**
db
db/**
admin
admin/**
advocates
advocates/**
functions
functions/**
scripts
scripts/**
*.py
*.pyc
__pycache__
__pycache__/**
*.md
README*.txt
wrangler.jsonc
package.json
package-lock.json
yarn.lock
pnpm-lock.yaml
.gitignore
.assetsignore
dev.vars*
''',encoding='utf8')
    (ROOT/'robots.txt').write_text('''User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/
Sitemap: https://lextalk.legal/sitemap.xml
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
      const host = url.hostname.toLowerCase();

      // Legacy compatibility bridge for browsers that still have an old
      // permanent redirect cached to the former workers.dev hostname.
      if (host === "lex-talk-legal.office-lextalklegal.workers.dev") {
        const target = new URL("https://lextalk.legal/__legacy-bridge/");
        target.searchParams.set("__to", url.pathname + url.search);
        return new Response(null, {
          status: 302,
          headers: {
            "Location": target.toString(),
            "Cache-Control": "no-store",
            "X-Robots-Tag": "noindex, nofollow, noarchive"
          }
        });
      }

      // Serve the original path through the canonical host. site.js silently
      // cleans the bridge URL from the browser address bar after the page loads.
      if (host === "lextalk.legal" && url.pathname === "/__legacy-bridge/") {
        let targetPath = url.searchParams.get("__to") || "/";
        try {
          const target = new URL(targetPath, "https://lextalk.legal");
          if (target.origin !== "https://lextalk.legal") targetPath = "/";
          else targetPath = target.pathname + target.search;
        } catch (_) {
          targetPath = "/";
        }
        const assetUrl = new URL(targetPath, "https://lextalk.legal");
        const assetRequest = new Request(assetUrl.toString(), request);
        const response = await env.ASSETS.fetch(assetRequest);
        const headers = new Headers(response.headers);
        headers.set("Cache-Control", "no-store");
        return new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers
        });
      }

      if (/^\/admin(?:\/|$)/.test(url.pathname)) {
        return Response.redirect(new URL('/', request.url), 302);
      }
      if (/^\/advocates(?:\/|$)/.test(url.pathname)) {
        return Response.redirect(new URL('/team.html', request.url), 301);
      }
      return await env.ASSETS.fetch(request);
    } catch (_) {
      return new Response("Lex Talk Legal — Temporary service error.", {
        status: 503,
        headers: {"content-type":"text/plain; charset=UTF-8"}
      });
    }
  }
};
''',encoding='utf8')

def main():
    write_page_style_assets()
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
    write_team_page();write_case_help_page();write_auctions_page();write_search_page();write_config();sync_homepage(arts,videos);refresh_static_pages()
    # Rebuild sitemap for the public editorial/site pages only.
    urls=['/','/courtrooms/','/case-status/','/videos/','/auctions/','/case-help.html','/team.html','/search.html']+[f'/category/{k}/' for k in CATEGORY_MAP]+[a['url'] for a in arts]
    now=datetime.now(timezone.utc).date().isoformat();xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{SITE_URL}{u}</loc><lastmod>{now}</lastmod></url>' for u in dict.fromkeys(urls))+'</urlset>';(ROOT/'sitemap.xml').write_text(xml,encoding='utf8')

if __name__=='__main__':main()
