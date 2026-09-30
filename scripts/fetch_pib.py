from pathlib import Path
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import html
import json
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / 'data' / 'pib_queue.json'
FEED_URL = 'https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1'
MAX_QUEUE = 120
KEEP_DAYS = 14

LEGAL_TERMS = {
    'law', 'laws', 'legal', 'legislation', 'legislative', 'bill', 'act', 'acts',
    'ordinance', 'notification', 'regulation', 'regulatory', 'rule', 'rules',
    'justice', 'judiciary', 'court', 'courts', 'tribunal', 'tribunals',
    'supreme court', 'high court', 'parliament', 'constitution',
    'ministry of law', 'department of legal affairs', 'legislative department',
    'policy', 'legal framework', 'gazette', 'amendment', 'consumer protection',
    'data protection', 'digital personal data', 'cyber', 'criminal', 'civil'
}
BANKING_TERMS = {
    'rbi', 'reserve bank', 'banking', 'banks', 'financial services', 'finance',
    'nbfc', 'sebi', 'irda', 'pfrda', 'insurance', 'insolvency', 'bankruptcy',
    'drt', 'drat', 'nclt', 'nclat', 'sarfaesi', 'recovery', 'loan', 'credit',
    'capital market', 'securities'
}
COURT_TERMS = {
    'supreme court', 'high court', 'court', 'courts', 'judiciary', 'judicial',
    'tribunal', 'tribunals', 'drt', 'drat', 'nclt', 'nclat'
}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'LexTalkLegal-PIBRadar/1.0 (+https://lextalk.legal/)'
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def strip_html(value: str) -> str:
    value = html.unescape(value or '')
    value = re.sub(r'<[^>]+>', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()


def text_of(parent, names):
    for name in names:
        node = parent.find(name)
        if node is not None and node.text:
            return node.text.strip()
    return ''


def parse_date(value: str):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc)
    except Exception:
        return None


def classify(title: str, description: str) -> str:
    text = f'{title} {description}'.lower()
    if any(term in text for term in COURT_TERMS):
        return 'Courts'
    if any(term in text for term in BANKING_TERMS):
        return 'Banking & Recovery'
    return 'Law & Policy'


def relevant(title: str, description: str) -> bool:
    text = f'{title} {description}'.lower()
    return any(term in text for term in LEGAL_TERMS | BANKING_TERMS)


def read_feed(raw: bytes):
    root = ET.fromstring(raw)
    rows = []
    for item in root.findall('.//item'):
        title = text_of(item, ['title'])
        link = text_of(item, ['link'])
        guid = text_of(item, ['guid']) or link or title
        pub = text_of(item, ['pubDate', 'published', 'updated'])
        desc = text_of(item, ['description', 'summary'])
        description = strip_html(desc)
        dt = parse_date(pub)
        if title and link and relevant(title, description):
            rows.append({
                'id': guid,
                'title': strip_html(title),
                'url': link,
                'published': dt.isoformat().replace('+00:00', 'Z') if dt else pub,
                'category': classify(title, description),
                'source': 'Press Information Bureau (PIB)',
                'source_feed': FEED_URL,
                'summary': description[:500],
                'status': 'review',
                'editorial_action': 'Review the official release, add Lex Talk Legal context, verify details, then publish through Blogger. Do not auto-republish the feed item.',
            })
    return rows


def load_queue():
    try:
        data = json.loads(QUEUE_PATH.read_text(encoding='utf8'))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def main():
    try:
        feed = fetch(FEED_URL)
        fresh = read_feed(feed)
    except Exception as exc:
        print(f'PIB feed fetch failed: {exc}')
        return 0

    existing = load_queue()
    by_id = {}
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=KEEP_DAYS)

    for item in existing:
        stamp = parse_date(item.get('published', ''))
        if stamp is None or stamp >= cutoff:
            by_id[str(item.get('id') or item.get('url') or item.get('title') or '')] = item

    for item in fresh:
        key = str(item.get('id') or item.get('url') or item.get('title') or '')
        if key:
            item['detected_at'] = now.isoformat().replace('+00:00', 'Z')
            by_id[key] = {**by_id.get(key, {}), **item}

    queue = list(by_id.values())
    queue.sort(key=lambda x: parse_date(x.get('published', '')) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    queue = queue[:MAX_QUEUE]

    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(f'PIB radar: {len(fresh)} relevant release(s) found; {len(queue)} item(s) in editorial queue.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
