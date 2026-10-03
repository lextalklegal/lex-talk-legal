# GA4 Revenue & Engagement Reporting — Lex Talk Legal

Measurement ID: `G-3KT3SQPFXD`

## What this build tracks

- `aibe_offer_click` — Pass The Bar / AIBE100 CTA
- `advertiser_enquiry` — Advertising Desk enquiry
- `media_kit_request` — Media Kit request
- `job_listing_submission` — employer/job listing email CTA
- `youtube_click` — YouTube outbound click
- `site_search` — internal site search
- `newsletter_signup_attempt` — current newsletter form interaction (not a confirmed subscription)
- `external_link_click` — relevant external destination click
- existing `contact_click`, `sponsor_click`, `whatsapp_click` events remain supported

## Recommended GA4 setup

1. Open **Google Analytics → Admin → Data display → Events** and wait for the new events to appear after real visits.
2. Mark the commercial-intent events below as **Key events** when you are ready to use them for reporting:
   - `advertiser_enquiry`
   - `media_kit_request`
   - `aibe_offer_click`
   - `job_listing_submission`
3. Do **not** mark `newsletter_signup_attempt` as a subscription conversion until a real mailing-provider signup is connected.
4. Use **Reports → Engagement → Events** to review event counts and event parameters.
5. Use the `placement`, `campaign`, `link_url`, and `link_text` parameters to compare campaign surfaces.

## Interpretation

These events measure user interactions, not confirmed sales or advertiser payments. Revenue should only be recorded after the corresponding commercial agreement, advertiser report, affiliate dashboard, or payment record confirms it.

## Design safety

This file changes analytics only. It does not redesign the shared header, navigation, footer, or page-specific layouts.
