---
name: news-fast-lane
description: Turn one news item in your niche into the day's content — a 3-filter check, then a decode post, a 40-second faceless Reel script, a quote card line and captions. Use when the user shares a headline, link, launch or digest item and wants content from it.
---

# News Fast Lane

**First, read `engine.config.json`** (brand, author, `niche.pillars`, `niche.audience`, `niche.out_of_scope`, `voice`, `hashtags`, `channels`, `integrations`). If it's missing, run the `engine-setup` skill first.

You turn one news item into content for the site and the social channels switched on in `channels`. Pillars only; anything in `niche.out_of_scope` fails the filter.

The rule that makes this work: **never report news — interpret it.** Hundreds of accounts post "X launched Y" within the hour. The only thing worth posting is the translation for the audience: what this changes for them (money, time, results, risk) and the question nobody is asking.

## The anchor rule

At least **2 of 3**: a dated, linked source fact · an anonymized moment from the author's work (`author.work_context`) · an artifact (a test, a screenshot, a number from the site's own Search Console/GA4 in `analytics/reports/latest.md`). Generic test: could anyone have written it without reading this week's news or doing the author's job? If yes, it fails. Never invent a number.

## Step 0 — Read the source

Open the link (web fetch) and build a **source card**: published date · who says so (vendor / independent / journalist / survey) · what it says (2–3 sentences) · exact numbers · one quote · link (prefer the primary source; trace roundups to the original). If the page can't be read, try a second source, then ask the user to paste the text. Never write from a headline alone. If the item is a video, pull its transcript first (a YouTube transcriber skill, if installed).

## Step 1 — The 3-filter

1. **In the pillars, and does the audience care?** It must change something the audience does.
2. **Is there an angle?** What it does to their results · what to change this week · where money/time should move · what to stop or automate · what the site's own data shows.
3. **Can it be said in one sharp line?**
4. **Does it have 2 anchors?** The source card is one; ask the author for one line from their work, or mark `[YOUR LINE]`.

Fails → say why in one line and stop; suggest a better item from the same digest if visible. Older than ~5 days → flag and ask.

## Step 2 — The decode post (400–700 words)

Hand off to the `blog-post` skill's Decode tier, or write directly: title phrased as the question people search · TL;DR (3 bullets) · what happened (2–3 sentences, primary link, exact numbers) · what it means for the audience (2–3 short sections) · what to do this week · `[YOUR LINE]` · FAQ (3) · meta title (<60) and description (<155).

## Step 3 — Reel script (40 seconds, faceless) — if `channels.instagram` or `channels.youtube_shorts`

Two columns: **ON-SCREEN TEXT** (≤8 words per card) | **VOICEOVER** (conversational; jargon explained in 3 words or dropped).

| Time | Beat |
|---|---|
| 0–2s | **Hook** — the sharpest claim. No intro. |
| 2–8s | **Agitate** — why this costs the viewer something real |
| 8–30s | **Meat** — 3 points max, one card each |
| 30–40s | **Payoff** — the one-line takeaway |
| 40–45s | **CTA** — "Full breakdown — link in bio" (or the `reel` skill's comment-keyword CTA) |

## Step 4 — Supporting assets

- **Quote card line:** under 20 words, the 2–4 words to set in the accent colour marked **like this** (`python3 brand/scripts/make_brand.py --quote "…"` makes a quick card).
- **Instagram caption:** hook line first, 2–3 short paragraphs, "Full breakdown — link in bio", 5 hashtags from one of the `hashtags` sets (rotate A/B/C).
- **LinkedIn version** (if `channels.linkedin`): hook, rehook, short paragraphs, takeaway, question, 3–5 hashtags, link in the first comment.

## Production (end of output)

Voiceover (any TTS, same voice every time) → video template or the `reel` skill → colours and fonts from `style.md`. Scheduling: if `integrations.postzen` (or another scheduler connector) is true, offer to schedule — never schedule without an explicit go-ahead.

## Rules

- One news Reel a day at most unless a second item is 3/3. Cadence never overrides the filter.
- Every claim traces to the source card. End the output with the source card so the author can check numbers.
- Respect everything in `author.confidential`. No words from `voice.banned_phrases`; no hype.
- If a query in `analytics/opportunities.json` matches the story, name the post after that query and say so.
