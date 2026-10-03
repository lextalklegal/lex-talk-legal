# Lex Talk Legal — Sponsored Campaign Guide

## Current campaign

**Partner:** Pass The Bar  
**Campaign:** AIBE XXII preparation  
**Promo code:** `AIBE100`  
**Advertiser-provided offer:** Save ₹100  
**Destination:** `https://passthebar.org/`

Campaign configuration lives in:

`data/partner_campaigns.json`

## Automated placements

The active campaign is intentionally limited to relevant surfaces:

- Homepage sponsored promotion
- Legal Careers category sponsored promotion
- AIBE-related articles only
- Dedicated `/aibe-preparation/` conversion landing page

The placement is visibly labelled **Sponsored Promotion** and paid outbound CTA links use `rel="sponsored"`.

## Tracking

Outbound campaign links include:

- `utm_source=lex-talk-legal`
- `utm_medium=sponsored_promotion`
- `utm_campaign=aibe100`
- `utm_content=` placement identifier

Current placement identifiers include `homepage`, `legal-careers`, and `article-aibe`.

## Workflow safety

Do not add this campaign to every article or every page. Keep sponsorship contextually relevant and distinct from editorial content.

The common header, navigation/menu and footer are not changed by the campaign.
