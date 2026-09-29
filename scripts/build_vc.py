from pathlib import Path
import json
import html as H
from datetime import datetime, timezone

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

def vc_card(item, icon="⚖️", title_override=""):
    url = safe_url(item.get("url"))
    label = str(item.get("label") or title_override or "Join VC").strip()
    if not url:
        return ""
    details = []
    if item.get("meeting_id"):
        details.append(f"<div><strong>Meeting ID:</strong> {H.escape(str(item['meeting_id']))}</div>")
    if item.get("password"):
        details.append(f"<div><strong>Password:</strong> {H.escape(str(item['password']))}</div>")
    if item.get("verified_on"):
        details.append(f"<div><strong>Last verified:</strong> {H.escape(str(item['verified_on']))}</div>")
    if item.get("notes"):
        details.append(f"<div>{H.escape(str(item['notes']))}</div>")
    meta = "".join(details)
    meta_html = f'<div class="vc-meta">{meta}</div>' if meta else ""
    return (
        f'<article class="utility-card court-card"><div><div class="court-icon">{icon}</div>'
        f'<h3>{H.escape(label)}</h3>{meta_html}'
        f'<div class="vc-link-grid"><a class="vc-link" href="{H.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">Join VC ↗</a></div>'
        f'</div></article>'
    )

def cards_for_list(items, icon="⚖️"):
    return "".join(vc_card(x, icon=icon) for x in items if isinstance(x, dict)) or '<div class="vc-empty">No verified VC entry is currently listed for this section.</div>'

def cards_for_map(data, names, icon="🏛️"):
    out = []
    for name in names:
        items = data.get(name, []) if isinstance(data, dict) else []
        if items:
            out.append(
                f'<article class="utility-card court-card"><div><div class="court-icon">{icon}</div>'
                f'<h3>{H.escape(name)}</h3>'
                f'<p>Manually maintained public VC details. Verify against the concerned court / tribunal cause list before joining.</p>'
                f'<div class="vc-link-grid">{"".join(_link_chip(x) for x in items if isinstance(x,dict))}</div></div></article>'
            )
        else:
            out.append(
                f'<article class="utility-card court-card"><div><div class="court-icon">{icon}</div>'
                f'<h3>{H.escape(name)}</h3><p>VC details have not been entered for this court yet.</p></div></article>'
            )
    return "".join(out)

def _link_chip(item, index=1):
    url = safe_url(item.get("url"))
    if not url:
        return ""
    label = item.get("label") or f"Public VC Link {index:02d}"
    extra=[]
    if item.get("meeting_id"):
        extra.append(f' <small style="display:block;color:var(--muted)">ID: {H.escape(str(item["meeting_id"]))}</small>')
    if item.get("password"):
        extra.append(f' <small style="display:block;color:var(--muted)">Password: {H.escape(str(item["password"]))}</small>')
    return f'<a class="vc-link" href="{H.escape(url,quote=True)}" target="_blank" rel="noopener noreferrer">{H.escape(str(label))} ↗{"".join(extra)}</a>'

def count_items(mapping):
    if not isinstance(mapping, dict):
        return 0
    total = 0
    for value in mapping.values():
        if isinstance(value, list):
            total += sum(1 for x in value if isinstance(x, dict) and safe_url(x.get("url")))
    return total


def count_locations(mapping):
    if not isinstance(mapping, dict):
        return 0
    return len(mapping)


def main():
    data = load_data()
    template = TEMPLATE.read_text(encoding="utf8")

    sc_items = [x for x in (data.get("supreme_court", []) or []) if isinstance(x, dict) and safe_url(x.get("url"))]
    sc = "".join(vc_card({**x, "label": x.get("label") or f"Public VC Link {i:02d}"}, icon="⚖️") for i, x in enumerate(sc_items, 1))

    high_courts = data.get("high_courts", {}) or {}
    hc = cards_for_map(high_courts, [name for name,_ in site.COURTS["high_courts"]], "🏛️")

    delhi = data.get("delhi_district", {}) or {}
    delhi_cards = cards_for_map(delhi, list(delhi.keys()), "🎥") if delhi else '<div class="vc-empty">No Delhi District Court VC entries are currently listed.</div>'

    drt = data.get("drt", {}) or {}
    drat = data.get("drat", {}) or {}
    nclt = data.get("nclt", {}) or {}
    nclat = data.get("nclat", {}) or {}

    def tribunal_cards(mapping, prefix, icon, names):
        out=[]
        for name in names:
            key = f"{prefix} — {name}"
            items = mapping.get(key, mapping.get(name, []))
            links = "".join(_link_chip(x, i) for i, x in enumerate(items, 1) if isinstance(x, dict))
            if not links:
                links = '<span class="vc-empty">No VC entry currently listed.</span>'
            out.append(
                f'<article class="utility-card court-card"><div><div class="court-icon">{icon}</div>'
                f'<h3>{H.escape(key)}</h3><p>Manually maintained public VC details. Verify the day’s cause list before joining.</p>'
                f'<div class="vc-link-grid">{links}</div></div></article>'
            )
        return "".join(out)

    nclt_names = site.COURTS["nclt"]
    nclat_names = site.COURTS["nclat"]

    hc_link_count = count_items(high_courts)
    delhi_link_count = count_items(delhi)
    nclt_link_count = count_items(nclt)
    nclat_link_count = count_items(nclat)
    total_links = len(sc_items) + hc_link_count + delhi_link_count + count_items(nclt) + count_items(nclat) + count_items(drt) + count_items(drat)
    # DRT/DRAT and NCLT/NCLAT names are stable forum lists, while populated links come from manual data.
    total_sections = 7
    locations = 1 + len(site.COURTS["high_courts"]) + len(delhi) + len(site.COURTS["drt"]) + len(site.COURTS["drat"]) + len(nclt_names) + len(nclat_names)

    html = template
    replacements = {
        "{{SC_CARDS}}": sc,
        "{{HC_CARDS}}": hc,
        "{{DELHI_CARDS}}": delhi_cards,
        "{{DRT_CARDS}}": tribunal_cards(drt, "DRT", "⚖️", site.COURTS["drt"]),
        "{{DRAT_CARDS}}": tribunal_cards(drat, "DRAT", "⚖️", site.COURTS["drat"]),
        "{{NCLT_CARDS}}": tribunal_cards(nclt, "NCLT", "🏢", nclt_names),
        "{{NCLAT_CARDS}}": tribunal_cards(nclat, "NCLAT", "🏢", nclat_names),
        "{{SC_COUNT}}": str(len(sc_items)),
        "{{HC_COUNT}}": str(len(site.COURTS["high_courts"])),
        "{{HC_LINKS}}": str(hc_link_count),
        "{{DELHI_COUNT}}": str(len(delhi)),
        "{{DELHI_LINKS}}": str(delhi_link_count),
        "{{DRT_COUNT}}": str(len(site.COURTS["drt"])),
        "{{DRAT_COUNT}}": str(len(site.COURTS["drat"])),
        "{{NCLT_COUNT}}": str(len(nclt_names)),
        "{{NCLT_LINKS}}": str(nclt_link_count),
        "{{NCLAT_COUNT}}": str(len(nclat_names)),
        "{{NCLAT_LINKS}}": str(nclat_link_count),
        "{{TOTAL_LINKS}}": str(total_links),
        "{{TOTAL_SECTIONS}}": str(total_sections),
        "{{LOCATIONS}}": str(locations),
    }
    for old, new in replacements.items():
        html = html.replace(old, new)

    title = "Courtrooms & VC Links"
    desc = "Lex Talk Legal public courtroom and virtual hearing links, maintained from supplied public VC details."
    extra_head = '<link rel="stylesheet" href="/assets/pages/courtrooms.css">'
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(site.page_shell((title, "/courtrooms/"), desc, html, extra_head=extra_head), encoding="utf8")
    print(f"Wrote {OUT} at {datetime.now(timezone.utc).isoformat()}")

if __name__ == "__main__":
    main()
