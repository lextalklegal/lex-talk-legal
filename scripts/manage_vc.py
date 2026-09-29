from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "vc_links.json"


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))


def save(data):
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def valid_url(value: str) -> str:
    value = (value or "").strip()
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise SystemExit("VC URL must be a complete http:// or https:// URL.")
    return value


def iter_items(obj, path=()):
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict):
                yield path + (i,), item
            else:
                yield from iter_items(item, path + (i,))
    elif isinstance(obj, dict):
        for key, value in obj.items():
            yield from iter_items(value, path + (key,))


def set_details(item, meeting_id, password, verified_on, notes):
    if meeting_id != "":
        item["meeting_id"] = meeting_id
    if password != "":
        item["password"] = password
    if verified_on != "":
        item["verified_on"] = verified_on
    if notes != "":
        item["notes"] = notes


action = os.getenv("VC_ACTION", "rebuild_existing").strip()
old_url = os.getenv("VC_OLD_URL", "").strip()
new_url = os.getenv("VC_URL", "").strip()
meeting_id = os.getenv("VC_MEETING_ID", "").strip()
password = os.getenv("VC_PASSWORD", "").strip()
verified_on = os.getenv("VC_VERIFIED_ON", "").strip()
notes = os.getenv("VC_NOTES", "").strip()
label = os.getenv("VC_LABEL", "").strip() or "Join VC"
section = os.getenv("VC_SECTION", "").strip()
court_name = os.getenv("VC_COURT_NAME", "").strip()

data = load()

if action == "rebuild_existing":
    print("Using existing data/vc_links.json as the baseline. No data changes requested.")

elif action == "add_or_update":
    url = valid_url(new_url)
    matches = [(p, item) for p, item in iter_items(data) if item.get("url") == url]
    if matches:
        for _, item in matches:
            item["label"] = label
            set_details(item, meeting_id, password, verified_on, notes)
        print(f"Updated {len(matches)} existing VC record(s) for {url}")
    else:
        if not section or not court_name:
            raise SystemExit("For a new VC entry, Section and Court/Bench name are required.")
        if section == "supreme_court":
            container = data.setdefault("supreme_court", [])
        else:
            container = data.setdefault(section, {})
            if not isinstance(container, dict):
                raise SystemExit(f"Section {section} is not a map in vc_links.json.")
            container = container.setdefault(court_name, [])
        item = {"label": label, "url": url}
        set_details(item, meeting_id, password, verified_on, notes)
        container.append(item)
        print(f"Added VC record under {section} / {court_name or 'Supreme Court'}")

elif action == "replace_url":
    if not old_url:
        raise SystemExit("Old VC URL is required for replace_url.")
    new_url = valid_url(new_url)
    count = 0
    for _, item in iter_items(data):
        if item.get("url") == old_url:
            item["url"] = new_url
            set_details(item, meeting_id, password, verified_on, notes)
            count += 1
    if not count:
        raise SystemExit("Old VC URL was not found in data/vc_links.json.")
    print(f"Replaced {count} VC record(s).")

elif action == "remove_url":
    if not old_url:
        raise SystemExit("Old VC URL is required for remove_url.")

    def prune(obj):
        if isinstance(obj, list):
            kept = []
            removed = 0
            for item in obj:
                if isinstance(item, dict) and item.get("url") == old_url:
                    removed += 1
                else:
                    new_item, n = prune(item)
                    kept.append(new_item)
                    removed += n
            return kept, removed
        if isinstance(obj, dict):
            total = 0
            new = {}
            for k, v in obj.items():
                nv, n = prune(v)
                new[k] = nv
                total += n
            return new, total
        return obj, 0

    data, count = prune(data)
    if not count:
        raise SystemExit("Old VC URL was not found in data/vc_links.json.")
    print(f"Removed {count} VC record(s).")

elif action == "update_details":
    if not old_url:
        raise SystemExit("Existing VC URL is required for update_details.")
    count = 0
    for _, item in iter_items(data):
        if item.get("url") == old_url:
            set_details(item, meeting_id, password, verified_on, notes)
            if label:
                item["label"] = label
            count += 1
    if not count:
        raise SystemExit("Existing VC URL was not found in data/vc_links.json.")
    print(f"Updated details for {count} VC record(s).")

else:
    raise SystemExit(f"Unsupported VC action: {action}")

save(data)
