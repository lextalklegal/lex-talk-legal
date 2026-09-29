# Lex Talk Legal — Manual Desk Guide

These datasets are intentionally maintained manually. The scheduled editorial sync does not fetch OneCourt, auction portals, job portals, or other third-party directories.

## 1. Courtrooms / VC

Source:
`data/vc_links.json`

Recommended entry fields:
- `label`
- `url`
- `meeting_id` (optional)
- `password` (optional)
- `verified_on` (optional)
- `notes` (optional)

### Easier method
Go to:
**GitHub → Actions → Update Courtroom VC Links → Run workflow**

Choose the section and enter the court/bench, VC URL and optional meeting details.

Actions:
- `add_or_update` — updates a matching URL or appends it
- `replace_url` — replace a known old URL with a new one
- `remove_url` — remove a known old URL

The workflow rebuilds only `courtrooms/index.html`.

## 2. Auctions

Source:
`data/auctions.json`

Use:
**GitHub → Actions → Update Auction Listings → Run workflow**

Required:
- unique ID

Optional fields include title, institution, property type, location, auction date, inspection date, reserve price, EMD, official source, notice URL, status and verification date.

The workflow rebuilds only `auctions/index.html`.

## 3. Legal Jobs

Source:
`data/jobs.json`

Use:
**GitHub → Actions → Update Legal Jobs → Run workflow**

Required:
- unique ID

Optional fields include title, organisation, location, employment type, experience, eligibility, deadline, posted date, apply URL, official source and status.

The workflow rebuilds only `jobs/index.html`.

## 4. Important rule

Do not place confidential credentials in these JSON files.

VC meeting passwords may be shown on the public Courtrooms page if you explicitly choose to publish them. Only supply credentials intended for public display.

## 5. Design safety

Editorial sync owns article/category/video/homepage outputs.

Manual workflows own their own directory page only.

About, Contact, Team, Case Status, policy pages and the shared header/menu/footer are not rewritten by the editorial sync.

For redesign work, modify only the relevant page template/HTML and its page-specific CSS.


## Direct JSON edits
If you edit one of these JSON files directly in GitHub instead of using the workflow form, run the corresponding manual workflow afterwards. These desks are intentionally not polled automatically.
