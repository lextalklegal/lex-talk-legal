"""
Add/update/remove one manual legal-job listing.
Inputs come from environment variables.
"""
from __future__ import annotations
import json, os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"data"/"jobs.json"

def e(name, default=""): return os.getenv(name, default).strip()
FIELDS=["title","organization","location","employment_type","experience","eligibility","deadline","posted_on","apply_url","official_url","status"]

def main():
    data=json.loads(PATH.read_text(encoding="utf-8"))
    if not isinstance(data,list): raise SystemExit("data/jobs.json must be a JSON array")
    action=e("JOB_ACTION","add_or_update")
    item_id=e("JOB_ID")
    if not item_id: raise SystemExit("JOB_ID is required")
    if action=="remove":
        new=[x for x in data if str(x.get("id",""))!=item_id]
        if len(new)==len(data): raise SystemExit("Job ID not found.")
        PATH.write_text(json.dumps(new,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("Removed job:",item_id); return
    item={"id":item_id}
    for f in FIELDS:
        v=e("JOB_"+f.upper())
        if v: item[f]=v
    item.setdefault("title",item_id)
    for i,x in enumerate(data):
        if isinstance(x,dict) and str(x.get("id",""))==item_id:
            data[i]=item
            PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            print("Updated job:",item_id); return
    data.append(item)
    PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Added job:",item_id)

if __name__=="__main__": main()
