# YouTube → automatic Lex Talk Legal blog publishing (Gemini free-tier setup)

## What this automation does

The existing `sync-editorial.yml` schedule checks the Lex Talk Legal YouTube channel every 30 minutes. For each new upload it:

1. Reads the public YouTube upload Atom feed (no YouTube Data API key required).
2. Attempts to retrieve public captions/transcript. If captions are blocked, it checks the description embedded in the upload feed first, then tries the public watch-page description. GitHub-hosted IPs can be blocked by YouTube, so transcript retrieval is best-effort.
3. Skips videos without enough source material rather than inventing a story; it retries them on the next run.
4. Uses the Gemini API model configured in the workflow (`gemini-2.5-flash-lite` by default) to create an original source-grounded article, clear SEO headline, unique meta description, excerpt, category and relevant labels. Free-tier availability and limits are controlled by Google and can change.
5. Saves a local copy of the YouTube thumbnail, embeds the original video using the privacy-enhanced YouTube domain, and stores generated article data in `data/youtube_articles.json`.
6. Builds the article page, adds article/video structured data, refreshes homepage/category/video pages and sitemaps, runs smoke tests, and commits generated outputs. The existing Cloudflare deploy workflow then publishes the changed site.

The existing global header/navigation/footer and manual/workflow-owned pages are not intentionally redesigned by this feature.

## One-time GitHub setup

In the repository, open **Settings → Secrets and variables → Actions → New repository secret**:

- **Name:** `GEMINI_API_KEY`
- **Value:** a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

The workflow uses the Gemini API free tier where Google makes it available. Free usage is subject to model eligibility, quotas, rate limits, regional availability and Google's current terms. The API key is not the same thing as a Gemini chat subscription. Do not configure a paid billing account if you want to keep this free-first; monitor Google AI Studio usage and stop the workflow if free quota is exhausted. This implementation does not call paid search-grounding tools.

No YouTube API key is required for the public channel feed. If the workflow cannot resolve the channel ID from `@lextalklegal`, add a repository variable named `YOUTUBE_CHANNEL_ID` containing the channel's `UC...` ID.

## SEO and editorial safeguards

- Article titles and descriptions are written for clarity and search intent, not keyword stuffing. Each generated article has a stable canonical route, internal category/homepage links, article metadata and `VideoObject` structured data; sitemap outputs are rebuilt by the existing site builder.
- The video thumbnail is copied to a stable local URL; it is not an AI-generated image. The original video is embedded with `youtube-nocookie.com`.
- The generator uses only the title, available transcript and/or description. It does not independently verify allegations, official responses, legal orders or breaking-news context. Political allegations and predictions must remain attributed to the speaker.
- If source material is too thin, the generator skips it rather than inventing legal facts. Human review is strongly recommended for political or legally consequential content.
- Search indexing, rich results and ranking cannot be guaranteed. Review the deployed article, canonical, sitemap and Google Search Console URL Inspection. Structured data makes a page eligible for certain search features but does not guarantee them.

## Manual test

Open **Actions → Lex Talk Legal - Editorial Sync → Run workflow**. Review the generator logs for `GENERATED`, `SKIP` or `ERROR`. After success, check the article URL in the commit, `https://lextalk.legal/sitemap.xml`, `https://lextalk.legal/news-sitemap.xml`, and Google Search Console URL Inspection.
