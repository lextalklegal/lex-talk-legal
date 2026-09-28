# Lex Talk Legal — 28 September 2026 merged refinement

This release keeps the supplied existing repository as the base and adds the agreed professional-community foundation.

## Preserved

- Existing article archive and data
- Blogger/YouTube/courtroom/case-status sync logic
- Existing legal guides and policy pages
- Existing branding assets and navigation architecture

## Added/refined

- Legal Professionals navigation and homepage community panel
- Free advocate profile submission page
- Mandatory administrative review workflow
- Cloudflare Pages Functions routes
- Cloudflare D1 schema for profiles, submissions and audit log
- Public server-rendered advocate directory and profile pages
- Admin moderation console protected by Cloudflare Access identity
- No public ratings, rankings, success-rate claims or guaranteed outcomes
- Profile guidelines and informational disclaimer language
- Security headers and API no-store rules
- `security.txt`
- Cacheable external logo references instead of embedding the logo as base64 in every generated page
- `.gitignore` and local variable example
- Deployment checklist

## Important

The database ID and secrets are intentionally not included. Configure them in Cloudflare. Do not commit production secrets to GitHub.
