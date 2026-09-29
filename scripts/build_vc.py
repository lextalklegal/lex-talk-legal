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
    meta_html = f'<div class="vc-meta" style="font:11px Arial,sans-serif;line-height:1.55;color:var(--muted);margin-top:10px">{meta}</div>' if meta else ""
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

def _link_chip(item):
    url = safe_url(item.get("url"))
    if not url:
        return ""
    label = item.get("label") or "Join VC"
    extra=[]
    if item.get("meeting_id"):
        extra.append(f' <small style="display:block;color:var(--muted)">ID: {H.escape(str(item["meeting_id"]))}</small>')
    if item.get("password"):
        extra.append(f' <small style="display:block;color:var(--muted)">Password: {H.escape(str(item["password"]))}</small>')
    return f'<a class="vc-link" href="{H.escape(url,quote=True)}" target="_blank" rel="noopener noreferrer">{H.escape(str(label))} ↗{"".join(extra)}</a>'

def main():
    data = load_data()
    template = TEMPLATE.read_text(encoding="utf8")
    sc = cards_for_list(data.get("supreme_court", []), "⚖️")

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
            links = "".join(_link_chip(x) for x in items if isinstance(x, dict))
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

    html = template
    html = html.replace("{{SC_CARDS}}", sc)
    html = html.replace("{{HC_CARDS}}", hc)
    html = html.replace("{{DELHI_CARDS}}", delhi_cards)
    html = html.replace("{{DRT_CARDS}}", tribunal_cards(drt, "DRT", "⚖️", site.COURTS["drt"]))
    html = html.replace("{{DRAT_CARDS}}", tribunal_cards(drat, "DRAT", "⚖️", site.COURTS["drat"]))
    html = html.replace("{{NCLT_CARDS}}", tribunal_cards(nclt, "NCLT", "🏢", nclt_names))
    html = html.replace("{{NCLAT_CARDS}}", tribunal_cards(nclat, "NCLAT", "🏢", nclat_names))

    title = "Courtrooms & VC Links"
    desc = "Lex Talk Legal public courtroom and virtual hearing links, maintained from supplied public VC details."
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(site.page_shell((title, "/courtrooms/"), desc, html), encoding="utf8")
    print(f"Wrote {OUT} at {datetime.now(timezone.utc).isoformat()}")

if __name__ == "__main__":
    main()
