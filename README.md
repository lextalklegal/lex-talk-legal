# Lex Talk Legal — Complete Merged Editorial Build v5

This repository is based on the current Lex Talk Legal source repository. Existing Blogger/YouTube/article/category/court utility structures are preserved while the presentation layer is rebuilt into a cleaner editorial layout.

## Key changes
- Removed Google Translate and the Hindi toggle completely.
- Removed the homepage hero slider and text-over-image headline treatment.
- Fixed article lead-image duplication by removing the first inline body image during build and again defensively during article rendering.
- Homepage now uses a fixed editorial hierarchy: 1 lead story, 3 secondary stories, 6 latest cards, a small utility sidebar, one professional-community band and 6 videos.
- Added mobile navigation and responsive grids.
- Added free Legal Professional profiles with administrative review.
- Added Cloudflare Worker + D1 foundation, audit logs and rate limiting.
- Admin access is intended to be protected with Cloudflare Access.

## D1 / Admin
Create D1, bind it as `DB`, run `db/schema.sql`, set `ADMIN_EMAILS`, and create the secret `RATE_SALT`. Without D1, the profile form remains safely unavailable rather than storing submissions in an unprotected third-party endpoint.
