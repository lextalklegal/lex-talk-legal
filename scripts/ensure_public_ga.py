from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
GA_ID = "G-3KT3SQPFXD"

GA_SNIPPET = f'''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>'''

LOADER_RE = re.compile(
    rf'<script\s+async\s+src=["\']https://www\.googletagmanager\.com/gtag/js\?id={re.escape(GA_ID)}["\']></script>',
    re.I,
)
CONFIG_RE = re.compile(rf"gtag\(['\"]config['\"],\s*['\"]{re.escape(GA_ID)}['\"]\s*\)\s*;?", re.I)


def public_html_files():
    for page in ROOT.rglob("*.html"):
        rel = page.relative_to(ROOT)
        if "templates" in rel.parts or "admin" in rel.parts:
            continue
        text = page.read_text(encoding="utf-8")
        if "<head" not in text.lower():
            continue
        yield page, text


def normalize(text: str) -> tuple[str, bool]:
    loader_count = len(LOADER_RE.findall(text))
    config_count = len(CONFIG_RE.findall(text))
    if loader_count == 1 and config_count == 1:
        return text, False

    # Only malformed pages are touched. Remove GA loader/config fragments and
    # install one canonical block immediately before </head>.
    cleaned = LOADER_RE.sub("", text)
    cleaned = CONFIG_RE.sub("", cleaned)
    head_match = re.search(r"</head>", cleaned, re.I)
    if not head_match:
        return text, False

    new_text = cleaned[:head_match.start()] + GA_SNIPPET + "\n" + cleaned[head_match.start():]
    return new_text, new_text != text


def main() -> None:
    checked = 0
    changed = 0
    for page, text in public_html_files():
        checked += 1
        new_text, did_change = normalize(text)
        if did_change:
            page.write_text(new_text, encoding="utf-8")
            changed += 1
    print(f"GA4 public-page guard: checked={checked}, changed={changed}, measurement_id={GA_ID}")


if __name__ == "__main__":
    main()
