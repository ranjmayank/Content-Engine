---
name: x-thread
description: Write an X (Twitter) thread or single post from a blog post or news item — hook tweet, 5–10 numbered posts, a closing post with the link, and alt text for any image. Use when the user asks for a tweet, X post, Twitter thread, or thread version of a post. (For YouTube Shorts and Instagram Reels, use the reel skill — the same vertical script works for both.)
---

# X thread

**First, read `engine.config.json`** (and write in `niche.language`, default English) (voice, pillars, audience, `brand.handles.x`, `hashtags`, confidential).

## Step 1 — Pick the detail and the anchor

One thread = one idea. Name the detail it covers and the sourced fact it's built on (link + date). If it's from a blog post, choose a detail that the LinkedIn posts didn't lead with.

## Step 2 — Write it

- **Post 1 (the hook):** under ~200 characters, stands alone: the specific surprising fact, a contrast, or a sharp claim. No "🧵", no "A thread:", no link (links in the first post cut reach).
- **Posts 2–8:** one point per post, each under 280 characters and readable on its own (people quote single posts). Numbers with their source named. Short sentences. Number them only if the order matters ("1/").
- **Second-to-last:** the takeaway — the line worth reposting.
- **Last post:** the link to the full post on the site + one line of why to click; optionally "Follow [handle] for…".
- **Hashtags:** 0–2, only if genuinely used in the niche, at the end of the last post.
- **Image:** suggest one (a chart, table screenshot or the quote card) for post 1 or 2, with alt text.

**Single post mode:** when asked for one post: the hook + the one fact + the takeaway in under 280 characters; link as a reply.

## Step 3 — Self-check

Hook works alone · every post stands alone · every number sourced · no link in post 1 · nothing from `voice.banned_phrases` or `author.confidential` · thread length fits the idea (5–10 posts, not padded).

## Output

```
THREAD — [detail] — source: [link, date]
1. ...
2. ...
...
Image for post [n]: [description] · Alt text: [...]
Best time: weekday morning in cadence.timezone
```

Scheduling: only through a connected scheduler and only with an explicit go-ahead.
