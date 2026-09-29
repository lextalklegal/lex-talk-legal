LEX TALK LEGAL — ONE-TIME PAGE CSS ARCHITECTURE REPAIR

Replace/upload ONLY these paths into the existing GitHub repository:

scripts/build_site.py
assets/pages/about.css
assets/pages/courts.css
assets/pages/banking-law.css
assets/pages/dra.css
assets/pages/videos.css
about.html
category/courts/index.html
category/banking-law/index.html
category/dra/index.html
videos/index.html

Do NOT replace site.css, site.js, header/menu/footer files separately, API secrets, DNS or Cloudflare settings.

Purpose:
- Restores the approved designs for About, Courts, Banking Law, DRA and Videos.
- Moves page-specific CSS into assets/pages/*.css.
- build_site.py now regenerates these CSS files on every sync.
- page_shell automatically links the correct page CSS by canonical path.
- Header/navigation/footer remain the shared global shell.
- Future page-specific design work should be isolated to its own CSS file and generator/content function.
