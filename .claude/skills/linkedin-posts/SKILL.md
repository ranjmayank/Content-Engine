---
name: linkedin-posts
description: Write LinkedIn posts and carousels for the author in engine.config.json — hook, rehook, body and CTA, carousel slide copy, and the matching Instagram caption, with the LinkedIn caption as the priority. Use when the user asks for a LinkedIn post, LinkedIn caption, carousel, or Instagram caption for the current topic.
---

# LinkedIn Posts, Carousels & Captions

**First, read `engine.config.json`** — `brand`, `author`, `niche.pillars`, `niche.audience`, `voice`, `hashtags`, `channels`, and `author.confidential`. Wherever this skill says *the author*, *the site* or *the pillars*, use those values. If the file is missing, run the `engine-setup` skill first.

You write the author's LinkedIn content for the current topic, plus carousel slide copy and the Instagram caption that goes with it. **The LinkedIn caption is the priority** — it's where their positioning is built.

**Who the author is on LinkedIn:** `author.role_line`, writing for `brand.site_name`. Their territories are the pillars in `niche.pillars`; anything in `niche.out_of_scope` doesn't belong here.

**Audience:** `niche.audience`.

## How the author works

- Topic approved first; one topic at a time. **Each post covers a different detail of the topic** (the main news, the number that surprises, the risk, what to do, the contrarian take) — never the same point twice.
- Built from current news (last few days). No designs unless they ask — carousel *copy* is fine; making it in Canva is a separate request.

## The anchor rule

Every post needs at least 2 of 3: a dated, linked source fact · an anonymized moment from their work · something they did or tested. No invented numbers. Generic test: could anyone in the niche have written it without this week's news or their job? If yes, rewrite.

## Step 1 — Pick the detail and the anchors

For each post, state in one line before writing: **the detail this post covers · the source fact it uses · the work moment (or `[YOUR LINE]`)**. If the series already has posts, check this detail isn't already covered.

## Step 2 — The LinkedIn caption

**Structure**

1. **Hook (lines 1–2).** The only job: stop the scroll. Under ~15 words a line. Must make sense on its own, before "…see more" (roughly the first 140 characters on mobile — keep the hook and the start of the rehook inside that).
   - Patterns that work: a surprising specific fact (a specific number or event from the source) · a contrast (what the vendor says vs what independent testing found) · a sharp claim the reader wants to argue with.
   - Never start with "I", the brand name, a question nobody's asking, or "In today's…".
2. **Rehook (2–3 lines).** Raise the stakes or add the second surprising fact, so "see more" feels necessary. Don't give the answer yet.
3. **Body.**
   - What happened, with the specific numbers and who said them (source named in the text).
   - Why it matters for the reader — the business translation.
   - Their experience line (the work moment), as a lesson, not a diary entry.
   - Short paragraphs (1–3 lines), white space between them. Use → or numbered lines for lists of 2–4 items.
4. **Takeaway.** One line worth screenshotting.
5. **CTA.** One, not several:
   - **Engagement question** (default) — specific and easy to answer from experience (a question the reader can answer from their own work). Not "Thoughts?".
   - Or **follow for the series** ("I'm breaking down one change a week — follow for the next one.").
6. **Hashtags.** 3–5, specific first (the niche-specific tags in `hashtags` before broad ones).
7. **First comment** (post it right away): the link to the the site post, with one line of why to click. **No links in the post body** — they reduce reach.

**Length:** 150–300 words for most posts. Up to ~1,300 characters is fine when the story needs it; cut anything that isn't the hook, the facts, the meaning or their line.

**Voice:** strategic but practical, direct, slightly conversational, proof-led. Confident without hype. Not influencer-style: no "🚀", no "Here's the thing:", no "Let that sink in", no "Agree?", no emoji bullets.

## Step 3 — Carousel slide copy (when asked)

LinkedIn carousel = a PDF document post; same copy works for Instagram at 1080×1350.

- **6–10 slides.** One idea per slide. Max ~20 words per slide; slide 1 max ~10.
- **Slide 1 — the hook** (must work alone in the feed). Specific, with tension.
- **Slide 2 — the news:** what happened, with the number and source.
- **Slides 3–6 — the detail:** one point each (why it's worse than it looks, the pattern, the vendor-vs-independent contrast).
- **Second-to-last — what to do:** 3 steps, verbs first.
- **Last — CTA:** "Full playbook → [brand.site_name] · [handle]".
- **Source footer** on any slide with a number: "Source: [who], [month year]".
- No "swipe →" filler, no emojis, no walls of text.
- Write the post caption that goes with it (Step 2 rules, shorter: 80–150 words, since the slides carry the detail).

## Step 4 — Instagram caption (same post, adapted)

- **First line is the hook** — only ~125 characters show before "more". Lead with the fact or contrast.
- 2–3 short paragraphs in plain words — Instagram readers are less technical; explain any term.
- "Full breakdown — link in bio."
- 3–5 hashtags, specific first, rotated between posts.
- Optional: a one-line Story poll idea that pairs with the post.
- Facebook gets the Instagram post automatically — no separate caption.

## Self-check before handing over

| Check | Pass? |
|---|---|
| Covers a detail no other post in the series covers | |
| Hook works alone in ~140 characters; doesn't start with "I" | |
| Rehook raises stakes without giving the answer | |
| Specific numbers, with the source named in the text | |
| 2 of 3 anchors (or `[YOUR LINE]` marked) | |
| One CTA; specific question or follow prompt | |
| No link in the body; link drafted for the first comment | |
| 3–5 hashtags | |
| Carousel: one idea per slide, ≤20 words, source footers | |
| No banned phrases; no confidential employer details (everything in `author.confidential` respected) | |

## Output format

```
POST [n] — [detail covered]
Anchors: [source fact + date] · [work moment / YOUR LINE]
Best day/time: [from the series plan, else weekday morning in `cadence.timezone`]

LINKEDIN
[caption]

First comment: [link + one line]

CAROUSEL (if requested)
Slide 1: ...
...
Caption: ...

INSTAGRAM CAPTION
[caption]
Hashtags: ...
Story poll (optional): ...

Sources: [date · link]
```

For a series, number the posts and list them in publishing order first.
