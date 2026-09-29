# Lex Talk Legal — Manual Desk Data

These datasets are intentionally maintained manually. They are not fetched from OneCourt, auction portals, job portals, or other third-party sites by the scheduled editorial sync.

## 1. VC links — data/vc_links.json

Existing court/tribunal structure is retained. Each VC entry may contain:
- label
- url
- meeting_id (optional)
- password (optional)
- verified_on (optional)
- notes (optional)

Example:
{
  "label": "Court No. 12",
  "url": "https://example.com/meeting",
  "meeting_id": "123 456 789",
  "password": "optional",
  "verified_on": "2026-09-29",
  "notes": "Verify against today's cause list."
}

To update: edit `data/vc_links.json` and commit. The VC workflow rebuilds only the Courtrooms page.

## 2. Auctions — data/auctions.json

Use one object per listing:
{
  "id": "auction-001",
  "title": "Property title",
  "institution": "Bank / FI / Authority",
  "property_type": "Residential / Commercial / Industrial",
  "location": "City, State",
  "auction_date": "2026-10-15",
  "inspection_date": "2026-10-10",
  "reserve_price": "₹...",
  "emd": "₹...",
  "official_url": "https://...",
  "notice_url": "https://...",
  "status": "Open",
  "verified_on": "2026-09-29"
}

Commit the JSON. The Auctions workflow rebuilds only `/auctions/`.

## 3. Legal jobs — data/jobs.json

Use one object per opportunity:
{
  "id": "job-001",
  "title": "Legal Associate",
  "organization": "Organisation name",
  "location": "New Delhi",
  "employment_type": "Full-time",
  "experience": "0-2 years",
  "eligibility": "LL.B",
  "deadline": "2026-10-10",
  "posted_on": "2026-09-29",
  "apply_url": "https://...",
  "official_url": "https://...",
  "status": "Open"
}

Commit the JSON. The Jobs workflow rebuilds only `/jobs/`.

## Workflow principle

Editorial sync: Blogger + YouTube only.

VC workflow: local `data/vc_links.json` only. No OneCourt / Playwright.

Auctions workflow: local `data/auctions.json` only.

Jobs workflow: local `data/jobs.json` only.

Deployment: a successful commit to `main` triggers the deployment workflow.
