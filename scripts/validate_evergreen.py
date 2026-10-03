from pathlib import Path
import argparse
import re
import sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / 'content' / 'evergreen'
OUTPUT_DIR = ROOT / 'article' / 'evergreen'
META_RE = re.compile(r'<!--\s*Lex Talk Legal Evergreen Metadata\s*(.*?)-->', re.S)
ALLOWED_SECTIONS = {'courts','banking-law','drt-drat','legal-careers','dra','explained'}


def parse_meta(raw, path):
    m = META_RE.search(raw or '')
    if not m:
        raise ValueError(f'{path}: missing Evergreen Metadata block')
    data = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            data[k.strip().lower()] = v.strip()
    required = ['title','slug','meta description','section','labels','published','updated']
    missing = [x for x in required if not data.get(x)]
    if missing:
        raise ValueError(f'{path}: missing metadata: {", ".join(missing)}')
    if data['section'].lower() not in ALLOWED_SECTIONS:
        raise ValueError(f'{path}: unsupported section {data["section"]!r}')
    return data


def words(text):
    return len(re.findall(r"\b[\w’'-]+\b", text or ''))


def validate_source(path, verbose=False):
    raw = path.read_text(encoding='utf-8')
    meta = parse_meta(raw, path.relative_to(ROOT))
    soup = BeautifulSoup(raw, 'html.parser')
    h1s = soup.find_all('h1')
    h2s = soup.find_all('h2')
    intro = soup.select_one('.article-intro')
    article_root = soup.find('article')
    if not article_root:
        raise ValueError(f'{path}: missing <article> root')
    if len(h1s) != 1:
        raise ValueError(f'{path}: expected exactly one <h1>, found {len(h1s)}')
    if not intro:
        raise ValueError(f'{path}: missing .article-intro')
    body_text = article_root.get_text(' ', strip=True)
    word_count = words(body_text)
    if word_count < 600:
        raise ValueError(f'{path}: article body has only {word_count} words; minimum acceptable source length is 600')
    if word_count < 900:
        print(f'WARNING: {path}: article body has {word_count} words; aim for 900+ only when the topic genuinely needs that depth.')
    internal_links = [a.get('href','') for a in article_root.find_all('a', href=True) if a.get('href','').startswith('/') or 'lextalk.legal' in a.get('href','').lower()]
    external_links = [a.get('href','') for a in article_root.find_all('a', href=True) if a.get('href','').startswith(('https://','http://'))]
    if not internal_links:
        raise ValueError(f'{path}: no internal Lex Talk Legal links found')
    if not external_links:
        raise ValueError(f'{path}: no primary/external source links found')
    officialish = any(any(domain in href.lower() for domain in ('indiacode.nic.in','ecourts.gov.in','rbi.org.in','sebi.gov.in','dfs.gov.in','gov.in')) for href in external_links)
    if not officialish:
        print(f'WARNING: {path}: no obvious official government source domain found; review source links.')
    if 'Source note' not in body_text and 'Official sources' not in body_text:
        print(f'WARNING: {path}: no explicit source-note/official-sources heading found.')
    title_len = len(meta['title'])
    desc_len = len(meta['meta description'])
    if title_len > 90:
        print(f'WARNING: {path}: SEO title is {title_len} characters; consider a shorter, still-descriptive title.')
    if desc_len > 180:
        print(f'WARNING: {path}: meta description is {desc_len} characters; review for concise SERP copy.')
    if len(h2s) < 4:
        print(f'WARNING: {path}: only {len(h2s)} H2 headings; consider expanding structure.')
    if verbose:
        print(f'OK: {path.relative_to(ROOT)} | {words(body_text)} words | {len(h2s)} H2 | {len(internal_links)} internal links | {len(external_links)} external links')
    return meta


def validate_generated(source_path, meta):
    slug = re.sub(r'[^a-z0-9]+','-',meta['slug'].lower()).strip('-')
    out = OUTPUT_DIR / f'{slug}.html'
    if not out.exists():
        raise ValueError(f'{source_path}: generated file missing: {out.relative_to(ROOT)}')
    raw = out.read_text(encoding='utf-8')
    soup = BeautifulSoup(raw, 'html.parser')
    canonical = soup.find('link', rel='canonical')
    expected = f'/article/evergreen/{slug}.html'
    if not canonical or expected not in canonical.get('href',''):
        raise ValueError(f'{out.relative_to(ROOT)}: canonical mismatch; expected path {expected}')
    if not soup.find('script', type='application/ld+json'):
        raise ValueError(f'{out.relative_to(ROOT)}: missing JSON-LD')
    if not 'BreadcrumbList' in raw:
        raise ValueError(f'{out.relative_to(ROOT)}: missing BreadcrumbList JSON-LD')
    if not 'article.css' in raw:
        raise ValueError(f'{out.relative_to(ROOT)}: missing article.css')


def main():
    ap = argparse.ArgumentParser(description='Validate Lex Talk Legal evergreen SEO source and generated pages.')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()
    files = sorted(SOURCE_DIR.glob('*.html'))
    if not files:
        print('No evergreen sources found.')
        return 0
    errors = []
    for path in files:
        try:
            meta = validate_source(path, args.verbose)
            if OUTPUT_DIR.exists():
                validate_generated(path, meta)
        except Exception as exc:
            errors.append(str(exc))
    if errors:
        print('\nEVERGREEN SEO VALIDATION FAILED:')
        for err in errors:
            print(' -', err)
        return 1
    print(f'Evergreen SEO validation passed: {len(files)} source article(s).')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
