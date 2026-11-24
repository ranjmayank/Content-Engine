---
name: medium-article
description: Write an engaging, information-rich Medium article for the author on the current topic — a distinct read from the site post, drawing on several external sources and linking back to the site. Use when the user asks for a Medium post, Medium version, or Medium article.
---

# Medium Article

**First, read `engine.config.json`** (and write in `niche.language`, default English) — `brand`, `author`, `niche.pillars`, `niche.audience`, `voice`, `hashtags`, `channels`, and `author.confidential`. Wherever this skill says *the author*, *the site* or *the pillars*, use those values. If the file is missing, run the `engine-setup` skill first.

You write the author's Medium article for the current topic. The the site post is built to rank and be cited; the Medium article is built to be **read to the end, clapped, highlighted, and followed**. Same topic, different job.

## How it differs from the site post

| | the site post | Medium article |
|---|---|---|
| Job | Rank on Google, get cited by AI answers | Hold a reader for 6–10 minutes, earn follows |
| Shape | Question-led H2s, direct answers, FAQ | A narrative with an argument: setup → tension → insight → what it means |
| Sources | Primary sources for the core story | The core story **plus** wider context: 4–8 external sources, earlier events, contrasting views |
| Voice | Clear, structured, skimmable | Personal, opinionated, story-driven — still proof-led |
| Links back | — | 1–2 contextual links to the the site post (and related posts) |

**Not a copy.** Don't paste or lightly reword the site post. Write a different piece on the same topic: a different opening, a wider lens, a clear point of view. That avoids competing with the site post in search and gives Medium readers a reason to read both.

(If the author wants the identical post on Medium instead, that's a different route: Medium's Import Story tool, which sets the canonical link to the site. Say so and don't write a new article.)

## How the author works

- Topic approved first; one topic at a time; built from current news (last few days). No designs unless asked.

## The anchor rule

At least 2 of 3: a dated, linked source fact · an anonymized moment from their work · something they did or tested. Never invent a number. Apply the generic test: could anyone have written this without reading this week's news or doing their job?

## Step 1 — Gather

1. **The site post and its source cards** (if they exist). Reuse the facts; don't reuse the prose.
2. **Widen the lens with 4–8 external sources** (read them, don't just cite headlines):
   - the original announcement or report
   - independent analysis or reporting that adds or challenges something
   - one earlier event that shows the pattern ("This is the second time in a week…")
   - one contrasting or skeptical view, where it exists
   - regional context (`niche.region`), when relevant
3. **Their angle:** the work moment, or `[YOUR LINE]` markers if they haven't given one.

## Step 2 — Shape (share a 5-line plan before writing if the topic is new)

- **Title:** specific and curious, under ~70 characters. A claim or a question, never clickbait. (a specific claim plus the consequence the reader hasn't noticed)
- **Subtitle:** one line that promises the payoff.
- **The argument in one sentence:** what the reader should believe at the end.
- **Story beats:** opening scene → what happened → why it matters more than it looks → the pattern / bigger picture → what to do or watch.
- **Length:** 1,200–2,000 words (roughly 5–9 minutes). Long enough to say something; short enough to finish.

## Step 3 — Write

- **Open in the story, not the summary.** The first 2–3 lines decide whether people keep reading: a specific moment, a surprising number, or a sharp claim. No throat-clearing.
- **One idea per section,** with short, plain subheadings (3–6 words). Medium readers skim headings to decide whether to continue.
- **Short paragraphs** (1–4 sentences), but full explanations — engaging doesn't mean shallow.
- **Make it theirs:** first person where it's earned ("What struck me…", "When my SEO team looked at our own Search Console…"). A clear opinion, stated and defended.
- **Show the evidence inline:** link sources on the claim they support; name who said it and when.
- **Use one pull-quote** (Medium's quote style) for the line most worth highlighting.
- **Context for non-experts:** define terms in a phrase the first time.
- **Link back naturally:** 1–2 mentions of the the site post where a reader would want more depth ("I've put the full breakdown, with every number sourced, here").
- **End with a takeaway, not a summary:** what changes, what to watch, one question for the reader to answer in the responses.
- **Sign-off:** one line on who they are and where to follow (newsletter, LinkedIn, the brand handle).

**Voice:** strategic but practical, slightly conversational, confident without hype. Avoid everything in `voice.banned_phrases`.

## Step 4 — Publishing details

- **Tags:** 5, most specific first (niche-specific first, broad last).
- **Featured image:** describe one to make (brand style or a relevant image they have rights to). No stock photos of robots.
- **Publications:** suggest 1–2 Medium publications that fit the topic for submission (check they're active and accept submissions before suggesting).
- **Timing:** publish after the site post is live, so the link back works.

## Self-check before handing over

| Check | Pass? |
|---|---|
| Different opening and angle from the site post (not a reword) | |
| 4–8 external sources read and linked; every number dated and sourced | |
| 2 of 3 anchors | |
| First 3 lines create a reason to keep reading | |
| Clear point of view, stated and defended | |
| 1–2 natural links to the site | |
| Ends with a takeaway + a question for responses | |
| No banned phrases; no confidential employer details (everything in `author.confidential` respected) | |

## Output format

```
Title:
Subtitle:
Tags (5):
Featured image idea:
Suggested publications:
Reading time: ~X min

---
[Article]
---

Sources used: [each with date and link]
```
