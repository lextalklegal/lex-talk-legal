"""
Update one VC entry in data/vc_links.json.

Actions:
- add_or_update: update matching URL or append a new entry
- replace_url: replace an existing URL with the supplied new URL and fields
- remove_url: remove an existing URL
All inputs are read from environment variables so GitHub Actions does not need
shell-escaped secrets or JSON fragments.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
import datetime as dt

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "vc_links.json"

def e(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()

def load():
    return json.loads(PATH.read_text(encoding="utf-8"))

def save(data):
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def target_list(data, section, court_name):
    if section == "supreme_court":
        return data.setdefault("supreme_court", [])
    if section == "high_court":
        return data.setdefault("high_courts", {}).setdefault(court_name, [])
    if section == "delhi_district":
        return data.setdefault("delhi_district", {}).setdefault(court_name, [])
    if section in {"drt", "drat", "nclt", "nclat"}:
        return data.setdefault(section, {}).setdefault(court_name, [])
    raise SystemExit(f"Unsupported VC section: {section}")

def make_entry():
    url = e("VC_URL")
    if not url.startswith(("https://", "http://")):
        raise SystemExit("VC_URL must start with http:// or https://")
    entry = {"label": e("VC_LABEL", "Join VC"), "url": url}
    for key in ("meeting_id", "password", "verified_on", "notes"):
        value = e("VC_" + key.upper())
        if value:
            entry[key] = value
    return entry

def main():
    action = e("VC_ACTION", "add_or_update")
    section = e("VC_SECTION")
    court_name = e("VC_COURT_NAME")
    data = load()
    items = target_list(data, section, court_name)

    if action == "remove_url":
        old = e("VC_OLD_URL")
        if not old:
            raise SystemExit("VC_OLD_URL is required for remove_url")
        before = len(items)
        items[:] = [x for x in items if not (isinstance(x, dict) and str(x.get("url","")).strip() == old)]
        if len(items) == before:
            raise SystemExit("No matching VC URL found; nothing removed.")
        save(data)
        print(f"Removed VC entry: {old}")
        return

    entry = make_entry()

    if action == "replace_url":
        old = e("VC_OLD_URL")
        if not old:
            raise SystemExit("VC_OLD_URL is required for replace_url")
        for i, item in enumerate(items):
            if isinstance(item, dict) and str(item.get("url","")).strip() == old:
                items[i] = entry
                save(data)
                print(f"Replaced VC entry: {old} -> {entry['url']}")
                return
        raise SystemExit("No matching VC_OLD_URL found.")

    if action == "add_or_update":
        for i, item in enumerate(items):
            if isinstance(item, dict) and str(item.get("url","")).strip() == entry["url"]:
                items[i] = entry
                save(data)
                print(f"Updated existing VC entry: {entry['url']}")
                return
        items.append(entry)
        save(data)
        print(f"Added VC entry: {entry['url']}")
        return

    raise SystemExit(f"Unsupported VC action: {action}")

if __name__ == "__main__":
    main()
