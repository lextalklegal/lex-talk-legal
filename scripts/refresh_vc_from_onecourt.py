#!/usr/bin/env python3
"""Refresh known public VC directory entries from OneCourt.

The script is deliberately conservative: each source page must yield a substantial
number of named, unique destinations before its matching data section is replaced.
If OneCourt changes its frontend or is unavailable, the current directory is kept.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "vc_links.json"
USER_AGENT = "LexTalkLegal-VC-Directory/1.0 (+https://lextalk.legal/courtrooms/)"

SOURCES = [
    ("supreme_court", None, "https://onecourt.in/Supreme_Court_VC_Hearing_Links", 12),
    ("high_courts", "Delhi High Court", "https://onecourt.in/Delhi_High_Court_VC_Hearing_Link", 20),
    ("high_courts", "Chhattisgarh High Court", "https://onecourt.in/vc-links/cg/Chhattisgarh_High_Court_VC_Hearing_Links.html", 5),
    ("nclt", "NCLT — NCLT VC Hearing Links", "https://onecourt.in/vc-links/nclt/NCLT_VC_Hearing_Links", 15),
    ("nclat", "NCLAT — NCLAT VC Hearing Links", "https://onecourt.in/vc-links/nclat/NCLAT_VC_Hearing_Links", 4),
    ("delhi_district", "Central District — Tis Hazari", "https://onecourt.in/vc-links/delhi/districtcourts/Central_District_VC_Links.html", 50),
    ("delhi_district", "South-East District — Saket", "https://onecourt.in/vc-links/delhi/districtcourts/South-East_District_VC_Links.html", 30),
    ("delhi_district", "South-West District — Dwarka", "https://onecourt.in/vc-links/delhi/districtcourts/South-West_District_VC_Links.html", 35),
    ("delhi_district", "North-West District — Rohini", "https://onecourt.in/vc-links/delhi/districtcourts/North-West_District_VC_Links.html", 18),
]

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)
MEETING_HOSTS = ("webex.com", "zoom.us", "zoom.com", "teams.microsoft.com", "meet.google.com")


def load_data():
    return json.loads(DATA.read_text(encoding="utf-8"))


def get_url_from_element(element):
    """Look for a meeting URL on the clicked element, its ancestors, or a visible dialog."""
    candidates = []
    try:
        candidates += element.evaluate("""el => {
          const out = [];
          let n = el;
          for (let i=0; n && i<7; i++, n=n.parentElement) {
            for (const a of ['href','data-url','data-href','data-vc-url','data-link','onclick']) {
              const v = n.getAttribute && n.getAttribute(a);
              if (v) out.push(v);
            }
          }
          return out;
        }""")
    except Exception:
        pass
    for value in candidates:
        for url in URL_RE.findall(value):
            clean = url.rstrip("),.;")
            if any(host in urlparse(clean).netloc.lower() for host in MEETING_HOSTS):
                return clean
    return ""


def label_from_element(element):
    try:
        lines = element.evaluate("""el => {
          let n=el;
          for (let i=0; n && i<6; i++, n=n.parentElement) {
            const t=(n.innerText||'').trim();
            if (t.length>8 && t.length<420 && /join vc/i.test(t)) {
              return t.split('\\n').map(x=>x.trim()).filter(Boolean);
            }
          }
          return [];
        }""")
    except Exception:
        lines = []
    ignore = {"join vc", "join vc hearing link", "open vc", "copy", "webex", "zoom", "microsoft teams", "google meet"}
    for line in lines:
        if line.lower() in ignore or line.lower().startswith("item "):
            continue
        if len(line) > 180:
            continue
        if re.search(r"verify against|information purpose|always verify", line, re.I):
            continue
        return line
    return ""


def scrape_page(browser, source_url, min_count):
    page = browser.new_page(user_agent=USER_AGENT, viewport={"width": 1440, "height": 1000})
    try:
        response = page.goto(source_url, wait_until="domcontentloaded", timeout=60000)
        if response and response.status >= 400:
            raise RuntimeError(f"Source returned HTTP {response.status}: {source_url}")
        page.wait_for_timeout(1800)
        # Direct anchors are cheapest and preserve the URL exactly.
        direct = page.locator("a[href]")
        records = []
        count = direct.count()
        for i in range(count):
            el = direct.nth(i)
            try:
                href = el.get_attribute("href") or ""
                host = urlparse(href).netloc.lower()
                if not href.startswith("http") or not any(h in host for h in MEETING_HOSTS):
                    continue
                label = label_from_element(el) or (el.inner_text(timeout=500).strip() if el else "")
                if not label or label.lower() in {"join vc", "join vc hearing link", "open vc"}:
                    label = ""
                records.append({"label": label, "url": href, "source_url": source_url,
                                "verified_on": datetime.now().astimezone().date().isoformat()})
            except Exception:
                continue

        # Some OneCourt pages expose the target only after the Join VC confirmation modal opens.
        if len({x["url"] for x in records}) < min_count:
            buttons = page.locator("button, [role='button']")
            nbuttons = min(buttons.count(), 600)
            for i in range(nbuttons):
                button = buttons.nth(i)
                try:
                    if not button.is_visible(timeout=300):
                        continue
                    text = (button.inner_text(timeout=300) or "").strip().lower()
                    if not text or "join vc" not in text:
                        continue
                    label = label_from_element(button)
                    url = get_url_from_element(button)
                    if not url:
                        button.click(timeout=900, no_wait_after=True)
                        page.wait_for_timeout(120)
                        dialog = page.locator('[role="dialog"]:visible, .modal:visible, [aria-modal="true"]:visible').last
                        if dialog.count():
                            url = get_url_from_element(dialog)
                            if not url:
                                url = dialog.evaluate("""el => {
                                  const nodes=[...el.querySelectorAll('a[href],button,[data-url],[data-href],[data-vc-url]')];
                                  for (const n of nodes) {
                                    const vals=[n.href,n.getAttribute('data-url'),n.getAttribute('data-href'),n.getAttribute('data-vc-url'),n.getAttribute('onclick')].filter(Boolean);
                                    for(const v of vals){const m=String(v).match(/https?:\\/\\/[^\\s\"'<>]+/); if(m && /webex|zoom|teams.microsoft|meet.google/i.test(m[0])) return m[0];}
                                  }
                                  return '';
                                }""")
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(80)
                    if url and any(h in urlparse(url).netloc.lower() for h in MEETING_HOSTS):
                        records.append({"label": label, "url": url, "source_url": source_url,
                                        "verified_on": datetime.now().astimezone().date().isoformat()})
                except Exception:
                    continue

        unique, seen = [], set()
        for item in records:
            url = item["url"]
            if url in seen:
                continue
            seen.add(url)
            if not item.get("label"):
                pathpart = urlparse(url).path.rstrip("/").split("/")[-1]
                item["label"] = pathpart.replace("-", " ").replace("_", " ").title() or "Public VC room"
            unique.append(item)
        if len(unique) < min_count:
            raise RuntimeError(f"Safety check failed: only {len(unique)} destinations found (minimum {min_count}) at {source_url}")
        return unique
    finally:
        page.close()


def assign(data, section, key, records):
    if section == "supreme_court":
        data[section] = records
    else:
        data.setdefault(section, {})[key] = records


def main():
    data = load_data()
    updated = []
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for section, key, url, min_count in SOURCES:
                try:
                    records = scrape_page(browser, url, min_count)
                    assign(data, section, key, records)
                    updated.append((section, key or "Supreme Court", len(records)))
                    print(f"OK {section} / {key or 'Supreme Court'}: {len(records)} destinations")
                except Exception as exc:
                    errors.append((section, key or "Supreme Court", str(exc)))
                    print(f"WARN {section} / {key or 'Supreme Court'}: {exc}")
        finally:
            browser.close()
    # Require at least one successful source; failed sources remain unchanged.
    if not updated:
        raise SystemExit("No OneCourt sources could be refreshed; existing VC database has been preserved.")
    # Re-read fresh data and merge only successful sources so failures never wipe a category.
    fresh = load_data()
    for section, key, count in updated:
        if section == "supreme_court":
            fresh[section] = data[section]
        else:
            fresh.setdefault(section, {})[key] = data[section][key]
    DATA.write_text(json.dumps(fresh, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {len(updated)} source page(s); {len(errors)} source page(s) kept their previous data.")
    if errors:
        print("Sources requiring review:")
        for section, key, error in errors:
            print(f" - {section} / {key}: {error}")


if __name__ == "__main__":
    main()
