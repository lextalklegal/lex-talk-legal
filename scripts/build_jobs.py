from pathlib import Path
import json
import html as H
from datetime import datetime, timezone

import build_site as site

ROOT=site.ROOT
DATA=ROOT/"data"/"jobs.json"
TEMPLATE=ROOT/"templates"/"jobs.html"
OUT=ROOT/"jobs"/"index.html"

def load_items():
    try:
        data=json.loads(DATA.read_text(encoding="utf8"))
    except Exception as exc:
        raise SystemExit(f"Unable to read {DATA}: {exc}")
    if not isinstance(data,list):
        raise SystemExit("data/jobs.json must contain a JSON array")
    return data

def card(x):
    title=str(x.get("title","")).strip()
    org=str(x.get("organization","")).strip()
    if not title: return ""
    meta=[]
    for key,label in [
        ("location","Location"),("employment_type","Type"),("experience","Experience"),
        ("eligibility","Eligibility"),("deadline","Deadline"),("posted_on","Posted"),
        ("status","Status")]:
        val=str(x.get(key,"")).strip()
        if val: meta.append(f"<div><strong>{label}:</strong> {H.escape(val)}</div>")
    actions=[]
    for key,label in [("apply_url","Apply ↗"),("official_url","Official source ↗")]:
        url=str(x.get(key,"")).strip()
        if url.startswith(("https://","http://")):
            actions.append(f'<a class="utility-link" href="{H.escape(url,quote=True)}" target="_blank" rel="noopener noreferrer">{label}</a>')
    return f'<article class="utility-card"><div class="icon">▣</div><div class="side-kicker">LEGAL CAREER</div><h3>{H.escape(title)}</h3><p><strong>{H.escape(org)}</strong></p><p style="font:11px Arial,sans-serif;line-height:1.65;color:var(--muted)">{"".join(meta)}</p><div class="card-actions">{" ".join(actions)}</div></article>'

def main():
    items=load_items()
    cards="".join(card(x) for x in items) or '<div class="empty">No legal job listings have been added to the board yet.</div>'
    t=TEMPLATE.read_text(encoding="utf8")
    t=t.replace("{{JOB_CARDS}}",cards).replace("{{UPDATED_AT}}",datetime.now(timezone.utc).date().isoformat())
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(site.page_shell(("Legal Jobs Board","/jobs/"),"Lex Talk Legal manually maintained legal jobs, internships and professional opportunities.",t),encoding="utf8")
    site.write_site_meta()
    print(f"Wrote {OUT}")
if __name__=="__main__":
    main()
