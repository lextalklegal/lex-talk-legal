# Lex Talk Legal — Google-targeted Evergreen SEO Publishing Pipeline

## Objective

Build useful, original, search-intent-focused evergreen legal pages that can earn organic traffic over time. No workflow or article can guarantee a #1 Google ranking.

Google's people-first guidance favors content that adds substantial value, avoids simply copying other sources, has descriptive titles, demonstrates expertise and sourcing, and is useful enough that readers would bookmark or recommend it.

## Publishing architecture

Blogger remains the source for current news.

GitHub `content/evergreen/` is the source of truth for owned evergreen guides.

`scripts/build_site.py` is the single generator.

`content/evergreen/*.html` -> build -> `article/evergreen/*.html` -> sitemap -> production.

## What every evergreen article should contain

1. One clear primary search intent.
2. A direct answer in the opening paragraph.
3. One H1 and a logical H2/H3 structure.
4. Plain-language explanation, not keyword repetition.
5. Primary-source links (prefer official government/court/statute sources).
6. Relevant internal links to Lex Talk Legal category and related guides.
7. Practical checklist, timeline, table or examples where useful.
8. Author/editorial transparency and an educational-use note.
9. Accurate publication and updated dates.
10. Original analysis/context; never copy or lightly rewrite another publisher's article.

## Quality gate

`scripts/validate_evergreen.py` checks:
- required metadata
- exactly one H1
- intro paragraph
- minimum source length
- internal links
- external/primary-source links
- generated output
- canonical
- JSON-LD
- BreadcrumbList
- article CSS

Warnings are deliberately used for title/meta-length review instead of hard-coded ranking limits.

## Google alignment

Google's current documentation states that useful, reliable, people-first content should provide substantial value and original analysis rather than merely copying or rewriting other sources. Article structured data can help Google understand article title, images, authors and dates, but it is not a guarantee of any special search placement.

## Publishing rhythm

Do not mass-produce dozens of near-duplicate pages. Build one strong page for each genuinely distinct search intent, then update it when the law, rules or practical process materially changes.

## Recommended cluster for the current library

DRT pillar -> SARFAESI 13(2) -> SARFAESI 13(4) -> possession notice -> DRT/SARFAESI remedy -> Recovery Certificate -> DRAT appeal.

Case-status utility stays a separate utility-intent page with links to the official eCourts services.

## Source policy

Use official statute/court/government sources where available. Keep primary-source links in the published article so readers can verify current text and developments.
