from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import re

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "site_meta.json"
UPDATED_RE = re.compile(
    r'(<div class="updated-line"\s+data-built-at=")[^"]*("\s+data-built-epoch=")[^"]*(">Content last updated: )([^<]*)(</div>)'
)

def public_html_files():
    for page in ROOT.rglob("*.html"):
        rel = page.relative_to(ROOT)
        if "templates" in rel.parts or "admin" in rel.parts or ".git" in rel.parts:
            continue
        yield page

def main():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    label = now.strftime("%d %B %Y, %H:%M:%S")
    epoch = int(now.timestamp())
    META.parent.mkdir(exist_ok=True)
    META.write_text(json.dumps({
        "built_at_ist": f"{label} IST",
        "built_at_epoch": epoch,
        "generated_by": "Lex Talk Legal site-wide timestamp refresh"
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # The site-wide timestamp is intentionally stored only in data/site_meta.json.
    # Public pages read this value at runtime through assets/site.js, which avoids
    # rewriting dozens of HTML files and prevents partial commits from creating
    # timestamp drift between generated pages and the authoritative value.
    print(f"Site timestamp refreshed: {label} IST | source=data/site_meta.json")

if __name__ == "__main__":
    main()
