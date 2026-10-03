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

    changed = 0
    checked = 0
    failures = []
    for page in public_html_files():
        checked += 1
        text = page.read_text(encoding="utf-8")
        if 'class="updated-line"' not in text:
            failures.append(str(page.relative_to(ROOT)))
            continue
        updated, count = UPDATED_RE.subn(
            lambda m: f'{m.group(1)}{label} IST{m.group(2)}{epoch}{m.group(3)}{label} IST{m.group(5)}',
            text,
            count=1,
        )
        if count != 1:
            failures.append(str(page.relative_to(ROOT)))
            continue
        if updated != text:
            page.write_text(updated, encoding="utf-8")
            changed += 1

    if failures:
        raise SystemExit("Timestamp refresh failed for pages: " + ", ".join(failures[:10]))
    print(f"Site timestamp refreshed: {label} IST | checked={checked} changed={changed}")

if __name__ == "__main__":
    main()
