# Google Analytics 4 — Lex Talk Legal

## Measurement ID

`G-3KT3SQPFXD`

## Current implementation

The GA4 Google tag is injected centrally by `scripts/build_site.py` and is present on public HTML pages. Protected/manual HTML pages are also kept covered by the repository smoke test.

## Events currently instrumented

- `sponsor_click` — paid partner / Pass The Bar link
- `youtube_click` — YouTube destination
- `contact_click` — mail/contact link
- `whatsapp_click` — WhatsApp destination
- `external_link_click` — selected external links opened in a new tab

## Verification

1. Open Google Analytics.
2. Select the Lex Talk Legal GA4 property.
3. Open **Reports → Realtime**.
4. Open `https://lextalk.legal/` in a separate browser tab.
5. Click a few pages and one external/YouTube link.
6. Return to Realtime and check that active users/events appear.

Do not add a second GA4 tag manually to the site's HTML. Future site builds should keep the tag through the central page shell and smoke-test protection.
