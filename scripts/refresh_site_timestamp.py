from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "site_meta.json"

def main():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    label = now.strftime("%d %B %Y, %H:%M:%S")
    epoch = int(now.timestamp())
    META.parent.mkdir(exist_ok=True)
    META.write_text(json.dumps({
        "built_at_ist": f"{label} IST",
        "built_at_epoch": epoch,
        "generated_by": "Lex Talk Legal site-wide runtime timestamp refresh"
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Site-wide runtime timestamp refreshed: {label} IST")
    print("Public HTML files are intentionally not rewritten; assets/site.js hydrates .updated-line from data/site_meta.json.")

if __name__ == "__main__":
    main()
