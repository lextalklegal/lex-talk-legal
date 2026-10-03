"""Synchronize all public HTML timestamp markers to data/site_meta.json.

This script intentionally does NOT create a new timestamp. It only repairs
baked footer values so the deploy guard and served HTML agree with the
authoritative site-wide timestamp already stored in data/site_meta.json.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "site_meta.json"
UPDATED_RE = re.compile(
    r'(<div class="updated-line"\s+data-built-at=")[^"]*("\s+data-built-epoch=")[^"]*(">Content last updated: )([^<]*)(</div>)'
)


def public_html_files():
    """Yield only deployable/public HTML files.

    Source, template, documentation, and development HTML must never be
    treated as public pages.
    """
    excluded_dirs = {
        "templates", "content", "admin", "docs", ".git", ".github",
        ".wrangler", "scripts", "node_modules", "src", "db", "functions",
    }
    for page in ROOT.rglob("*.html"):
        rel = page.relative_to(ROOT)
        if any(part in excluded_dirs for part in rel.parts):
            continue
        if any(part.startswith(".") for part in rel.parts):
            continue
        yield page


def load_meta():
    try:
        data = json.loads(META.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Unable to read data/site_meta.json: {exc}")
    label = str(data.get("built_at_ist", "")).strip()
    epoch = str(data.get("built_at_epoch", "")).strip()
    if not label or not epoch:
        raise SystemExit("data/site_meta.json must contain built_at_ist and built_at_epoch")
    return label, epoch


def main():
    label, epoch = load_meta()
    changed = []
    missing = []
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
        new_text = text[:match.start()] + replacement + text[match.end():]
        if new_text != text:
            page.write_text(new_text, encoding="utf-8")
            changed.append(str(page.relative_to(ROOT)))

    print(f"Public timestamp synchronization complete: {label}")
    print(f"Authoritative source: data/site_meta.json")
    print(f"Updated public HTML files: {len(changed)}")
    if changed:
        for item in changed:
            print(f" - {item}")
    if missing:
        print("Public HTML missing timestamp marker:")
        for item in missing:
            print(f" - {item}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
