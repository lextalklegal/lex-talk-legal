LEX TALK LEGAL - COURTROOMS / CASE STATUS / VC UPDATE

Replace these in the existing GitHub repo:
1. scripts/build_site.py
2. .github/workflows/sync.yml
3. wrangler.jsonc
4. _redirects
5. data/vc_links.json (new file; keep it in data/)

Then run Actions manually once.

What this update does:
- Navigation changes Explained -> Bare Acts and opens https://indiacode.gov.in/
- All High Court Case Status buttons use the supplied eCourts case-status URL.
- DRT/DRAT Case Status buttons use https://efiling.drt.gov.in/
- NCLT/NCLAT case-status URLs remain the existing official portals.
- Courtrooms page no longer links users to OneCourt at click time.
- GitHub Actions uses Playwright to render the public OneCourt VC directories during each sync, extracts the destination VC URLs, saves them to data/vc_links.json, and publishes those direct URLs on Lex Talk Legal.
- If an extraction run gets no direct destinations and existing VC data exists, the last known data is retained. If there is no prior data, the run may fail rather than deploying a Courtrooms page with broken/empty direct links.
- Users are still told to verify the day’s official cause list because VC links can change.
