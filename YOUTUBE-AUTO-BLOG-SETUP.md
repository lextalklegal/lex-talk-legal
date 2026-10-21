# YouTube → automatic Lex Talk Legal blog publishing — RETIRED

> **Retired on 21 October 2026.** This document is a historical record, not an active setup guide.
> The `.github/workflows/sync-editorial.yml` workflow no longer runs `scripts/generate_youtube_articles.py` and no longer passes `GEMINI_API_KEY` to scheduled runs. Regular Blogger editorial sync and YouTube feed sync remain enabled. Existing generated YouTube article records have been preserved.
>
> Do not follow the historical steps below to re-enable automatic YouTube-to-blog publishing unless the site owner explicitly requests it. Removing an API key alone is not the automation control.

## Historical implementation notes

The retired automation used to read the public YouTube Atom feed, try to retrieve a transcript or description, call Gemini to draft an article, store data in `data/youtube_articles.json`, and rebuild article pages, sitemaps and related listings. The generator script and historic data remain in the repository for audit/rollback only.

Manual X-post-based publishing is separate and will start only from a post/embed code supplied by the site owner.
