# Google Analytics 4 — Lex Talk Legal

Measurement ID: `G-3KT3SQPFXD`

The Google tag is installed on public static pages and is included in `scripts/build_site.py` so future generated pages receive the same tag automatically.

## Verify after deployment
1. Open `https://lextalk.legal/`.
2. Use Google Tag Assistant to connect to the domain.
3. Confirm the Google tag ID `G-3KT3SQPFXD` appears.
4. In Google Analytics, open **Reports → Realtime** and confirm a current user/page view is visible after visiting the site.

Do not add a second Google Analytics snippet manually to individual pages. Keep the single measurement ID in `scripts/build_site.py` for generated pages.
