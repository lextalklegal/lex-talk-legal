from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "site_meta.json"
UPDATED_RE = re.compile(
    r'(<div class="updated-line"\s+data-built-at=")[^"]*("\s+data-built-epoch=")[^"]*(">Content last updated: )([^<]*)(</div>)'
)


def public_html_files():
    for page in ROOT.rglob("*.html"):
        rel = page.relative_to(ROOT)
        if any(part in rel.parts for part in ("templates", "content", "admin", "docs", ".git")):
            continue
        yield page


def write_meta(label: str, epoch: int) -> None:
    META.parent.mkdir(exist_ok=True)
    META.write_text(
        json.dumps(
            {
                "built_at_ist": label,
                "built_at_epoch": epoch,
                "generated_by": "Lex Talk Legal site-wide timestamp refresh",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def content_changes_present() -> bool:
    """Return True when the working tree has non-timestamp changes."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return True

    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path == "data/site_meta.json":
            continue
        # Documentation/template-only changes must not trigger a public-site timestamp refresh.
        if path == "docs" or path.startswith("docs/"):
            continue
        # The timestamp script itself is never modified by this check during a run.
        if path == "scripts/refresh_site_timestamp.py" and status == "??":
            continue
        return True
    return False


def sync_public_html(label: str, epoch: int) -> tuple[list[str], list[str]]:
    changed: list[str] = []
    missing: list[str] = []
    for page in sorted(public_html_files()):
        text = page.read_text(encoding="utf-8")
        match = UPDATED_RE.search(text)
        if not match:
            missing.append(str(page.relative_to(ROOT)))
            continue
        replacement = (
            f"{match.group(1)}{label}"
            f"{match.group(2)}{epoch}"
            f"{match.group(3)}{label}"
            f"{match.group(5)}"
        )
        new_text = text[: match.start()] + replacement + text[match.end() :]
        if new_text != text:
            page.write_text(new_text, encoding="utf-8")
            changed.append(str(page.relative_to(ROOT)))
    return changed, missing


def main() -> None:
    only_if_changed = "--if-content-changed" in sys.argv[1:]
    if only_if_changed and not content_changes_present():
        print("No non-timestamp content changes detected; site timestamp not refreshed.")
        return

    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    label = now.strftime("%d %B %Y, %H:%M:%S") + " IST"
    epoch = int(now.timestamp())
    write_meta(label, epoch)
    changed, missing = sync_public_html(label, epoch)

    print(f"Site timestamp refreshed: {label}")
    print("Authoritative source: data/site_meta.json")
    print(f"Public HTML synchronized: {len(changed)} file(s)")
    if missing:
        print("Public HTML missing timestamp marker:")
        for item in missing:
            print(f" - {item}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
