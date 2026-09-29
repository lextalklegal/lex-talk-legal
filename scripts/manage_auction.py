"""
Add/update/remove one manual auction listing.
Inputs come from environment variables.
"""
from __future__ import annotations
import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "auctions.json"

def e(name, default=""): return os.getenv(name, default).strip()

FIELDS = [
    "title","institution","property_type","location","auction_date",
    "inspection_date","reserve_price","emd","official_url","notice_url",
    "status","verified_on"
]

def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list): raise SystemExit("data/auctions.json must be a JSON array")
    action = e("AUCTION_ACTION","add_or_update")
    item_id = e("AUCTION_ID")
    if not item_id: raise SystemExit("AUCTION_ID is required")
    if action == "remove":
        new = [x for x in data if str(x.get("id","")) != item_id]
        if len(new) == len(data): raise SystemExit("Auction ID not found.")
        PATH.write_text(json.dumps(new, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print("Removed auction:", item_id); return
    item = {"id": item_id}
    for f in FIELDS:
        v=e("AUCTION_"+f.upper())
        if v: item[f]=v
    item.setdefault("title", item_id)
    for i,x in enumerate(data):
        if isinstance(x,dict) and str(x.get("id","")) == item_id:
            data[i]=item
            PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
            print("Updated auction:", item_id); return
    data.append(item)
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Added auction:", item_id)

if __name__=="__main__": main()
