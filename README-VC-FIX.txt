LEX TALK LEGAL - COURTROOM VC CLEANUP

Replace these existing repository files:
1. scripts/build_site.py
2. assets/site.js
3. assets/site.css
4. data/vc_links.json

Then run the existing GitHub Actions workflow.

Changes:
- Courtroom/VC labels are taken from the court/courtroom context or the confirmation modal instead of repeating "Join VC".
- Supreme Court labels preserve "Court No. X" when exposed by the public directory popup.
- Delhi District Court VC entries are displayed individually where distinct public destinations are exposed.
- Direct VC destinations are never shown as OneCourt URLs.
- VC buttons no longer navigate immediately. They first show a confirmation modal; "Proceed to VC" opens the public destination in a new tab.
- Where no direct VC destination is available, the VC button opens an informational modal only. It advises checking the cause list or contacting the Court Registrar / Courtroom Master / Reader.
- The existing YouTube/Blogger sync flow is preserved.

Important: direct VC URLs can change. The automated workflow re-checks the public directory; users should still verify the day's official cause list before joining.
