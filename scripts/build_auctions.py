from pathlib import Path
import json
import html as H
from datetime import datetime, timezone

import build_site as site

ROOT = site.ROOT
DATA = ROOT / "data" / "auctions.json"
TEMPLATE = ROOT / "templates" / "auctions.html"
OUT = ROOT / "auctions" / "index.html"

def load_items():
    try:
        data=json.loads(DATA.read_text(encoding="utf8"))
    except Exception as exc:
        raise SystemExit(f"Unable to read {DATA}: {exc}")
    if not isinstance(data,list):
        raise SystemExit("data/auctions.json must contain a JSON array")
    return data

def card(x):
    title=str(x.get("title","")).strip()
    if not title: return ""
    parts=[]
    for key,label in [
        ("institution","Institution"),("property_type","Property"),("location","Location"),
        ("auction_date","Auction date"),("reserve_price","Reserve price"),("emd","EMD"),
        ("inspection_date","Inspection"),("status","Status")]:
        val=str(x.get(key,"")).strip()
        if val: parts.append(f"<div><strong>{label}:</strong> {H.escape(val)}</div>")
    meta="".join(parts)
    official=site.H.escape(str(x.get("official_url","")),quote=True) if x.get("official_url") else ""
    notice=site.H.escape(str(x.get("notice_url","")),quote=True) if x.get("notice_url") else ""
    actions=""
    if official: actions += f'<a class="utility-link" href="{official}" target="_blank" rel="noopener noreferrer">Official source ↗</a>'
    if notice and notice != official: actions += f' <a class="utility-link" href="{notice}" target="_blank" rel="noopener noreferrer">Auction notice ↗</a>'
    return f'<article class="utility-card"><div class="icon">🏦</div><div class="side-kicker">AUCTION LISTING</div><h3>{H.escape(title)}</h3><p class="auction-meta" style="font:11px Arial,sans-serif;line-height:1.65;color:var(--muted)">{meta}</p><div class="card-actions">{actions}</div></article>'

def main():
    items=load_items()
    cards="".join(card(x) for x in items) or '<div class="empty">No auction listings have been added to the desk yet.</div>'
    t=TEMPLATE.read_text(encoding="utf8")
    t=t.replace("{{AUCTION_CARDS}}",cards).replace("{{UPDATED_AT}}",datetime.now(timezone.utc).date().isoformat())
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(site.page_shell(("Auction Desk","/auctions/"),"Lex Talk Legal manually maintained public auction listings.",t),encoding="utf8")
    site.write_site_meta()
    print(f"Wrote {OUT}")
if __name__=="__main__":
    main()
