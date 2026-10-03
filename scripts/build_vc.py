from pathlib import Path
import json
import html as H
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import build_site as site

ROOT = site.ROOT
DATA = ROOT / "data" / "vc_links.json"
TEMPLATE = ROOT / "templates" / "courtrooms.html"
OUT = ROOT / "courtrooms" / "index.html"


def load_data():
    try:
        data = json.loads(DATA.read_text(encoding="utf8"))
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        raise SystemExit(f"Unable to read {DATA}: {exc}")


def safe_url(value):
    value = str(value or "").strip()
    return value if value.startswith(("https://", "http://")) else ""


def platform_name(url):
    host = urlparse(url).netloc.lower()
    if "zoom" in host:
        return "Zoom"
    if "teams.microsoft" in host:
        return "Microsoft Teams"
    if "meet.google" in host:
        return "Google Meet"
    if "webex" in host:
        return "Webex"
    return host.replace("www.", "") or "External VC"


def reference_from_url(url):
    patterns = [
        (r"registrarcourt(?:[-_.]?)(\d+)", "Registrar Court No. {:02d}"),
        (r"courtroom(?:[-_. ]?)(\d+)", "Courtroom No. {:02d}"),
        (r"courtno[-_. ]?(\d+)", "Court No. {:02d}"),
        (r"court[-_. ]?(\d+)(?:\D|$)", "Courtroom No. {:02d}"),
        (r"(?:northwest|north[-_. ]west)(?:[-_. ]?)(\d+)", "North-West VC Room {:02d}"),
    ]
    low = str(url or "").lower()
    for pat, label in patterns:
        match = re.search(pat, low)
        if match:
            return label.format(int(match.group(1)))
    return ""


def entry_reference(item, url, index):
    for key in ("courtroom", "room_reference", "room", "court_number", "court_no"):
        value = str(item.get(key) or "").strip()
        if value:
            return value
    return reference_from_url(url) or f"VC Link {index:02d}"


def unique_items(items):
    seen = set()
    out = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        url = safe_url(item.get("url"))
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(item)
    return out


def json_attr(value):
    return H.escape(json.dumps(value, ensure_ascii=False), quote=True)


def court_detail_html(venue, forum_label, items):
    if not items:
        return (
            f'<div class="cr-detail-head"><div class="cr-detail-forum">{H.escape(forum_label)}</div>'
            f'<h3>{H.escape(venue)}</h3><p>No public VC destination is currently stored for this court in the manual directory.</p></div>'
            f'<div class="cr-detail-links"><div class="cr-no-links">No VC link is currently listed. Check the concerned court / tribunal website or cause list for its current virtual-hearing instructions.</div></div>'
        )
    rows = []
    for i, item in enumerate(unique_items(items), 1):
        url = safe_url(item.get("url"))
        ref = entry_reference(item, url, i)
        platform = platform_name(url)
        meta = []
        if item.get("meeting_id"):
            meta.append(f'<div><span>Meeting ID</span><strong>{H.escape(str(item["meeting_id"]))}</strong></div>')
        if item.get("password"):
            meta.append(f'<div><span>Password</span><strong>{H.escape(str(item["password"]))}</strong></div>')
        if item.get("verified_on"):
            meta.append(f'<div><span>Verified</span><strong>{H.escape(str(item["verified_on"]))}</strong></div>')
        if item.get("notes"):
            meta.append(f'<div><span>Notes</span><strong>{H.escape(str(item["notes"]))}</strong></div>')
        meta_html = f'<div class="cr-vc-meta">{"".join(meta)}</div>' if meta else ''
        rows.append(
            f'<article class="cr-vc-row">'
            f'<div class="cr-vc-row-top"><div class="cr-vc-ref">{H.escape(ref)}</div><div class="cr-vc-platform">{H.escape(platform)}</div></div>'
            f'{meta_html}'
            f'<div class="cr-vc-actions"><button class="cr-open-vc" type="button" data-vc-url="{H.escape(url, quote=True)}" data-vc-ref="{H.escape(ref, quote=True)}">Open VC ↗</button>'
            f'<button class="cr-copy" type="button" data-copy="{H.escape(url, quote=True)}">Copy</button></div>'
            f'</article>'
        )
    return (
        f'<div class="cr-detail-head"><div class="cr-detail-forum">{H.escape(forum_label)}</div>'
        f'<h3>{H.escape(venue)}</h3><p>{len(rows)} public VC destination{'' if len(rows)==1 else 's'} stored in the current directory. Review the relevant room reference and hearing instructions before joining.</p></div>'
        f'<div class="cr-detail-links">{"".join(rows)}</div>'
    )


def block(venue, forum_key, forum_label, items):
    items = unique_items(items)
    platforms = sorted({platform_name(safe_url(x.get("url"))) for x in items if safe_url(x.get("url"))})
    chips = ''.join(f'<span class="cr-platform-chip">{H.escape(p)}</span>' for p in platforms[:3]) or '<span class="cr-platform-chip">No VC stored</span>'
    summary = ' · '.join(platforms[:3]) if platforms else 'No public VC destination currently stored'
    detail = court_detail_html(venue, forum_label, items)
    search_text = f"{forum_label} {venue} {summary} {" ".join(entry_reference(x, safe_url(x.get("url")), i) for i,x in enumerate(items,1))}".lower()
    return (
        f'<article class="cr-court-card" data-forum="{H.escape(forum_key)}" data-forum-label="{H.escape(forum_label, quote=True)}" data-court-name="{H.escape(venue, quote=True)}" data-search="{H.escape(search_text, quote=True)}" data-detail="{H.escape(detail, quote=True)}">'
        f'<div class="cr-court-top"><span class="cr-court-forum">{H.escape(forum_label)}</span><span class="cr-court-count">{len(items)} link{'' if len(items)==1 else 's'}</span></div>'
        f'<h3>{H.escape(venue)}</h3><p class="cr-court-summary">{H.escape(summary)}</p><div class="cr-platforms">{chips}</div>'
        f'<button type="button" class="cr-view-court">View VC links →</button></article>'
    )


def build_courts(data):
    blocks = []
    blocks.append(block("Supreme Court of India", "supreme", "Supreme Court", data.get("supreme_court", [])))
    high = data.get("high_courts", {}) or {}
    for name, _ in site.COURTS.get("high_courts", []):
        blocks.append(block(name, "high", "High Courts", high.get(name, [])))
    delhi = data.get("delhi_district", {}) or {}
    for name in delhi.keys():
        blocks.append(block(name, "delhi", "Delhi District Courts", delhi.get(name, [])))
    # Stable forum lists come from build_site.py, while current links come from manual data.
    for prefix, key, label, names in [
        ("DRT", "drt", "Debt Recovery Tribunals", site.COURTS.get("drt", [])),
        ("DRAT", "drat", "Debt Recovery Appellate Tribunals", site.COURTS.get("drat", [])),
        ("NCLT", "nclt", "NCLT", site.COURTS.get("nclt", [])),
        ("NCLAT", "nclat", "NCLAT", site.COURTS.get("nclat", [])),
    ]:
        mapping = data.get(key, {}) or {}
        for name in names:
            full = f"{prefix} — {name}"
            items = mapping.get(full, mapping.get(name, [])) if isinstance(mapping, dict) else []
            blocks.append(block(full, key, label, items))
    return ''.join(blocks)


def main():
    data = load_data()
    template = TEMPLATE.read_text(encoding="utf8")
    content = template.replace("{{COURT_BLOCKS}}", build_courts(data))
    extra_head = '<link rel="stylesheet" href="/assets/pages/courtrooms.css">'
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        site.page_shell(
            ("Courtrooms & VC Links", "/courtrooms/"),
            "Lex Talk Legal public courtroom and virtual-hearing directory, organised by court and forum with manual VC details.",
            content,
            extra_head=extra_head,
        ),
        encoding="utf8",
    )
    print(f"Wrote {OUT} at {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
