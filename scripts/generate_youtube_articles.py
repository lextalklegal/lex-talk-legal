#!/usr/bin/env python3
"""Create an original, transcript-grounded article for each new Lex Talk Legal upload.

Requires OPENAI_API_KEY. Articles are generated only when a transcript or a meaningful
YouTube description is available. Claims are attributed to the speaker/source; the
script never invents dates, locations, quotes, legal holdings, or independent verification.
"""
from __future__ import annotations
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDLE = os.getenv("YOUTUBE_HANDLE", "@lextalklegal")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "").strip()
API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
SITE = "https://lextalk.legal"
FEED_NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
STATE_PATH = ROOT / "data/youtube_articles.json"
IMAGE_DIR = ROOT / "assets/images/youtube-blog"


def fetch(url: str, timeout: int = 25) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; LexTalkLegalEditorialBot/1.0)"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def channel_id() -> str:
    if CHANNEL_ID:
        return CHANNEL_ID
    page = fetch("https://www.youtube.com/" + HANDLE + "/videos").decode("utf-8", "ignore")
    match = re.search(r'<meta itemprop="channelId" content="(UC[^"]+)"', page) or re.search(r'"channelId":"(UC[^"]+)"', page) or re.search(r'"externalId":"(UC[^"]+)"', page)
    if not match:
        raise RuntimeError("Could not resolve YouTube channel ID; set YOUTUBE_CHANNEL_ID repository variable.")
    return match.group(1)


def get_uploads() -> list[dict]:
    root = ET.fromstring(fetch("https://www.youtube.com/feeds/videos.xml?channel_id=" + urllib.parse.quote(channel_id())))
    videos = []
    for entry in root.findall("a:entry", FEED_NS):
        title = entry.findtext("a:title", default="", namespaces=FEED_NS).strip()
        link = entry.find("a:link", FEED_NS)
        published = entry.findtext("a:published", default="", namespaces=FEED_NS)
        video_id = entry.findtext("yt:videoId", default="", namespaces=FEED_NS)
        url = link.attrib.get("href", "") if link is not None else ("https://www.youtube.com/watch?v=" + video_id if video_id else "")
        if video_id and title and url:
            videos.append({"title": title, "url": url, "published": published, "video_id": video_id})
    return videos


def video_description(video_id: str) -> str:
    """Extract public video description as fallback if captions are unavailable."""
    try:
        page = fetch("https://www.youtube.com/watch?v=" + urllib.parse.quote(video_id)).decode("utf-8", "ignore")
        match = re.search(r'"shortDescription"\s*:\s*("(?:\\.|[^"\\])*")', page)
        if match:
            return str(json.loads(match.group(1))).strip()
    except Exception as exc:
        print(f"Metadata fallback unavailable for {video_id}: {exc}")
    return ""


def transcript_text(video_id: str) -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=["en", "hi", "en-US", "hi-IN"])
        pieces = []
        for item in transcript:
            text = getattr(item, "text", "")
            if text:
                pieces.append(str(text))
        return re.sub(r"\s+", " ", " ".join(pieces)).strip()
    except Exception as exc:
        print(f"Transcript unavailable for {video_id}: {exc}")
        return ""


def safe_slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\s-]", "", value).strip().lower().replace(" ", "-")
    return re.sub(r"-+", "-", value)[:100].strip("-") or "youtube-video"


def save_thumbnail(video_id: str) -> str:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    target = IMAGE_DIR / f"{video_id}.jpg"
    if not target.exists():
        try:
            target.write_bytes(fetch(f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"))
        except Exception as exc:
            print(f"Thumbnail download failed for {video_id}: {exc}")
            return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    return f"{SITE}/assets/images/youtube-blog/{video_id}.jpg"


def call_model(video: dict, source_text: str, source_type: str) -> dict:
    instructions = """You are the editorial writer for Lex Talk Legal, an Indian legal-news and public-affairs website.
Create an original, accurate, search-friendly article based ONLY on the supplied YouTube title and transcript/description.
Return one JSON object with exactly these keys: headline, meta_description, excerpt, category, labels, html.
Rules:
- headline: clear, descriptive, factual, about 45-75 characters when possible; do not use clickbait.
- meta_description: useful summary, ideally 140-160 characters.
- excerpt: 1-2 sentence summary for article cards.
- category: one of Courts, Law & Policy, Banking Law, DRT / DRAT, Legal Careers, DRA, Explained, Legal News.
- labels: array of 2-5 short relevant topical labels, include the selected category as one label.
- html: valid article body fragment using only <p>, <h2>, <h3>, <ul>, <ol>, <li>, <blockquote>, <strong>, <em>, <a>. No <html>, <body>, scripts, images or iframe.
- Write in clear English. Explain Hindi speech in English and translate only when clear from the source. Do not invent quotes or present uncertain translations as verbatim.
- Attribute political statements, allegations, predictions and disputed claims to the speaker/channel. Say when the video does not independently establish a claim.
- Do not add facts, dates, locations, statistics, official responses, legal conclusions or context absent from the supplied material.
- If the video is primarily a public statement, describe who said what and why it matters, without endorsing it. Keep a short video summary focused, usually 250-450 words; do not pad or repeat keywords.
- Include an ending paragraph noting the article is based on the linked video and that material claims should be checked against primary records where relevant.
- Do not make claims about rankings or guarantee search visibility.
"""
    payload = {
        "model": MODEL,
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": json.dumps({"video_title": video["title"], "video_url": video["url"], "published_at": video["published"], "source_type": source_type, "source_material": source_text[:22000]}, ensure_ascii=False)}
        ]
    }
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=json.dumps(payload).encode("utf-8"), headers={"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json", "User-Agent": "LexTalkLegalEditorialBot/1.0"}, method="POST")
    with urllib.request.urlopen(req, timeout=90) as response:
        result = json.loads(response.read().decode("utf-8"))
    content = result["choices"][0]["message"]["content"]
    data = json.loads(content)
    for key in ("headline", "meta_description", "excerpt", "category", "labels", "html"):
        if key not in data:
            raise ValueError("Model response missing " + key)
    if data["category"] not in {"Courts", "Law & Policy", "Banking Law", "DRT / DRAT", "Legal Careers", "DRA", "Explained", "Legal News"}:
        data["category"] = "Legal News"
    if not isinstance(data["labels"], list):
        data["labels"] = [data["category"]]
    if data["category"] not in data["labels"]:
        data["labels"].insert(0, data["category"])
    return data


def sanitize_html(fragment: str) -> str:
    """Allow only a small editorial HTML vocabulary from model output."""
    allowed = {"p", "h2", "h3", "ul", "ol", "li", "blockquote", "strong", "em", "a"}
    soup = BeautifulSoup(str(fragment or ""), "html.parser")
    for node in list(soup.find_all(True)):
        if node.name not in allowed:
            node.unwrap()
            continue
        attrs = {}
        if node.name == "a":
            href = str(node.get("href", "")).strip()
            if href.startswith("https://"):
                attrs = {"href": href, "target": "_blank", "rel": "noopener noreferrer"}
        node.attrs = attrs
    return str(soup).strip()


def load_state() -> list[dict]:
    try:
        value = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []
    except Exception:
        return []


def main() -> int:
    if not API_KEY:
        print("OPENAI_API_KEY is not set. Skipping auto-article generation; regular YouTube sync can still run.")
        return 0
    state = load_state()
    known = {str(a.get("video_id", "")) for a in state}
    uploads = get_uploads()
    new_count = 0
    for video in uploads[:15]:
        if video["video_id"] in known:
            continue
        text = transcript_text(video["video_id"])
        source_type = "video transcript"
        if len(text) < 80:
            text = video_description(video["video_id"])
            source_type = "public YouTube description (transcript unavailable)"
        if len(text.strip()) < 120:
            print(f"SKIP {video['video_id']}: no transcript or sufficiently detailed description; will retry on next scheduled run.")
            continue
        try:
            article = call_model(video, text, source_type)
            published = video.get("published") or datetime.now(timezone.utc).isoformat()
            # Preserve YouTube's published timestamp and a stable canonical path.
            url = "/article/" + safe_slug(article["headline"]) + ".html"
            image = save_thumbnail(video["video_id"])
            video_id = video["video_id"]
            video_embed = (f'<section class="article-video-embed" aria-label="Watch the original video"><h2>Watch the original video</h2>'
                           f'<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%">'
                           f'<iframe src="https://www.youtube-nocookie.com/embed/{video_id}" title="{html.escape(article["headline"], quote=True)}" '
                           f'loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
                           f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen style="position:absolute;inset:0;width:100%;height:100%;border:0"></iframe></div></section>')
            content = sanitize_html(article["html"]) + video_embed
            state.append({
                "title": str(article["headline"]).strip(),
                "url": url,
                "source_url": video["url"],
                "published": published,
                "updated": published,
                "labels": article["labels"],
                "category": article["category"],
                "image": image,
                "excerpt": str(article["excerpt"]).strip(),
                "meta_description": str(article["meta_description"]).strip(),
                "content": content,
                "video_id": video_id,
                "video_title": video["title"],
                "video_embed_url": f"https://www.youtube-nocookie.com/embed/{video_id}",
                "video_upload_date": published,
                "youtube_auto_article": True,
                "editorial_source_type": source_type
            })
            known.add(video_id)
            new_count += 1
            print(f"GENERATED: {article['headline']} [{video_id}]")
        except Exception as exc:
            print(f"ERROR generating article for {video['video_id']}: {exc}")
            # Do not mark as processed; next scheduled run retries it.
    if new_count:
        # Most recent first; keep historical generated posts rather than deleting older pages.
        state.sort(key=lambda item: str(item.get("published", "")), reverse=True)
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"YouTube auto-articles: {new_count} new article(s); {len(state)} total stored.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"YouTube article generator failed safely: {exc}")
        sys.exit(1)
