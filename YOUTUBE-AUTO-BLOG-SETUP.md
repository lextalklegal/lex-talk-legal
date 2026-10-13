# YouTube → automatic Lex Talk Legal blog publishing

## What the workflow does

The existing `sync-editorial.yml` schedule now checks the Lex Talk Legal YouTube channel every 30 minutes. For each new upload it:

1. Reads the public YouTube upload feed.
2. Attempts to obtain the video's public captions/transcript; if unavailable, it tries the public YouTube description.
3. Skips the video safely if neither source provides enough material. The next scheduled run retries it.
4. Uses the configured OpenAI model to prepare a unique headline, meta description, excerpt, topical category, and original summary grounded in the supplied source material. Political allegations remain attributed; the generator is instructed not to invent facts.
5. Downloads the YouTube thumbnail into `assets/images/youtube-blog/` as a stable, locally hosted blog image.
6. Adds a privacy-enhanced YouTube embed to the article page.
7. Builds the article page, adds Article/NewsArticle and VideoObject JSON-LD, refreshes homepage/category/video pages and both sitemaps, runs smoke tests, and commits the generated changes. The existing Cloudflare deploy workflow then publishes the changed site.

The existing header, navigation/footer, manual auctions/jobs/courtroom pages, and their separate workflows are not intentionally changed by this feature.

## One-time GitHub setup required

In the repository, open **Settings → Secrets and variables → Actions → New repository secret**:

- Name: `OPENAI_API_KEY`
- Value: an API key from the OpenAI API platform.

The text generation API is usage-billed separately from a ChatGPT subscription. Set a budget/usage limit on the API account. The workflow uses `gpt-4.1-mini` by default; change `OPENAI_MODEL` in `.github/workflows/sync-editorial.yml` if desired.

No YouTube API key is required for the public channel feed. If the workflow cannot resolve the channel ID from the handle, add a repository variable named `YOUTUBE_CHANNEL_ID` containing the channel's `UC...` ID.

## Important operating notes

- This workflow publishes generated articles automatically after the repository's build/smoke-test gate passes. It does not send a human approval request. For politically sensitive or legally consequential videos, manual review before publication is safer; the source video and its claims are attributed in the generated article.
- A video without public captions and without a sufficiently detailed description is skipped, not turned into a guessed article. It will be retried on the next scheduled run.
- The article's hero image is the video's YouTube thumbnail, copied to a stable local path. This is not a newly generated AI illustration.
- The generator only uses the transcript/description and title. It does not independently verify allegations, official responses, legal orders, or breaking-news context.
- Google indexing and rankings cannot be guaranteed. Search engines choose what to index and rank. The workflow adds unique titles/descriptions, canonical URLs, internal category/homepage links, article structured data, video structured data and sitemap entries; monitor the result in Google Search Console.
- The generated article is a blog article with an embedded video. It may be eligible for ordinary text/image results, but Google does not necessarily treat every blog post as a dedicated video watch page.

## Manual test

After committing the workflow and adding the secret, open **Actions → Lex Talk Legal - Editorial Sync → Run workflow**. Review the run log for `GENERATED`, `SKIP`, or `ERROR`. After a successful run, check the article URL from the commit, `https://lextalk.legal/sitemap.xml`, `https://lextalk.legal/news-sitemap.xml`, and Google Search Console URL Inspection.
