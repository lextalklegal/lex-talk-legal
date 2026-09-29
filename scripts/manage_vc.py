from __future__ import annotations
import datetime as dt
import json
import os
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "vc_links.json"


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def load_data():
    try:
        data = json.loads(DATA.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Unable to read {DATA}: {exc}")
    if not isinstance(data, dict):
        raise SystemExit("data/vc_links.json must contain a JSON object")
    return data


def save_data(data):
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_url(value: str) -> str:
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise SystemExit("VC URL must be a complete http:// or https:// URL")
    return value


def find_url_entries(node, target_url):
    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and str(item.get("url", "")).strip() == target_url:
                yield item
            else:
                yield from find_url_entries(item, target_url)
    elif isinstance(node, dict):
        for value in node.values():
            yield from find_url_entries(value, target_url)


def section_list(data, section, court_name):
    if section == "supreme_court":
        return data.setdefault("supreme_court", [])
    if section == "high_court":
        if not court_name:
            raise SystemExit("Court/Bench name is required for a High Court entry")
        return data.setdefault("high_courts", {}).setdefault(court_name, [])
    if section == "delhi_district":
        if not court_name:
            raise SystemExit("Court/Bench name is required for a Delhi District entry")
        return data.setdefault("delhi_district", {}).setdefault(court_name, [])
    if section in {"drt", "drat", "nclt", "nclat"}:
        if not court_name:
            raise SystemExit("Court/Bench name is required for this tribunal entry")
        return data.setdefault(section, {}).setdefault(court_name, [])
    raise SystemExit(f"Unsupported VC section: {section}")


def build_entry():
    url = validate_url(env("VC_URL"))
    entry = {"label": env("VC_LABEL", "Join VC") or "Join VC", "url": url}
    for key in ("meeting_id", "password", "verified_on", "notes"):
        value = env("VC_" + key.upper())
        if value:
            entry[key] = value
    return entry


def main():
    action = env("VC_ACTION", "rebuild_existing")
    data = load_data()

    # No data edit: rebuild the already-fetched baseline exactly as-is.
    if action == "rebuild_existing":
        print("Using existing data/vc_links.json as the baseline; no VC data changed.")
        return

    if action == "update_details":
        old_url = validate_url(env("VC_OLD_URL"))
        matches = list(find_url_entries(data, old_url))
        if not matches:
            raise SystemExit("Existing VC URL was not found in data/vc_links.json")
        label = env("VC_LABEL")
        for item in matches:
            if label:
                item["label"] = label
            for key in ("meeting_id", "password", "verified_on", "notes"):
                value = env("VC_" + key.upper())
                if value:
                    item[key] = value
        save_data(data)
        print(f"Updated details for {len(matches)} matching VC record(s).")
        return

    if action == "replace_url":
        old_url = validate_url(env("VC_OLD_URL"))
        new_entry = build_entry()
        matches = list(find_url_entries(data, old_url))
        if not matches:
            raise SystemExit("Existing VC URL was not found in data/vc_links.json")
        for item in matches:
            item.clear()
            item.update(new_entry)
        save_data(data)
        print(f"Replaced {len(matches)} matching VC record(s).")
        return

    if action == "remove_url":
        old_url = validate_url(env("VC_OLD_URL"))

        def prune(node):
            removed = 0
            if isinstance(node, list):
                kept = []
                for item in node:
                    if isinstance(item, dict) and str(item.get("url", "")).strip() == old_url:
                        removed += 1
                    else:
                        new_item, n = prune(item)
                        kept.append(new_item)
                        removed += n
                return kept, removed
            if isinstance(node, dict):
                new = {}
                for key, value in node.items():
                    new_value, n = prune(value)
                    new[key] = new_value
                    removed += n
                return new, removed
            return node, 0

        data, removed = prune(data)
        if not removed:
            raise SystemExit("Existing VC URL was not found in data/vc_links.json")
        save_data(data)
        print(f"Removed {removed} matching VC record(s).")
        return

    if action == "add_or_update":
        entry = build_entry()
        section = env("VC_SECTION")
        court_name = env("VC_COURT_NAME")
        items = section_list(data, section, court_name)
        for index, item in enumerate(items):
            if isinstance(item, dict) and str(item.get("url", "")).strip() == entry["url"]:
                items[index] = entry
                save_data(data)
                print("Updated existing VC record.")
                return
        items.append(entry)
        save_data(data)
        print("Added new VC record.")
        return

    raise SystemExit(f"Unsupported VC action: {action}")


if __name__ == "__main__":
    main()
