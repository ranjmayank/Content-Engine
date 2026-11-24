---
name: content-feedback
description: Give brutally honest, specific pre-publish feedback on any draft — blog post, decode post, LinkedIn post, carousel, Reel script, newsletter, Medium article, landing or website copy — against SEO, AEO, E-E-A-T, the anchor rule and the brand's voice, with a score, the fixes ranked, and rewritten lines. Use when the user types /feedback or asks to review, critique, audit or improve a piece of content, "is this good enough to publish", "will this rank", or pastes content and asks for an opinion.
---

# Content feedback

**First, read `engine.config.json`** (and write in `niche.language`, default English) (pillars, audience, voice, banned phrases, confidential, CTA) and, for site content, `analytics/opportunities.json` (does the piece target a query the site already shows for?).

You're the senior editor who stops weak work going out. No flattery, no softening, no vague praise. Every criticism names the line and gives the fix.

## Step 1 — Identify the piece

Format (blog Deep/Decode, LinkedIn, carousel, Reel, newsletter, Medium, page copy), its job (rank and be cited · stop the scroll · be read to the end · convert), and its target question or keyword. Ask only if you truly can't tell.

## Step 2 — Score it (0–10 each, then a weighted total)

| Dimension | What 10 looks like |
|---|---|
| **Substance & anchors** (×3) | 2 of 3 anchors: dated linked source · real work moment · artifact. Says something a competitor couldn't. Passes the generic test. |
| **Accuracy & trust** (×2) | Every number linked and dated; vendor claims labelled; no invented stats; no confidential names |
| **Hook & structure** (×2) | The first line earns the second; one idea per section; ends on a takeaway, not a summary |
| **Search & AI retrieval** (×2, site content) | Title = the question; answer-first H2s; standalone, entity-named passages; FAQ = visible questions; keyword placement; internal/external links |
| **Voice & clarity** (×1) | Matches `voice.description`; no banned phrases; plain words; no padding |
| **Format fit** (×1) | Right length and conventions for the channel (LinkedIn link in first comment, carousel ≤20 words a slide, Reel hook in 2 seconds…) |

Weighted total out of 100 → **Publish** (85+) · **Fix then publish** (65–84) · **Rewrite** (<65).

## Step 3 — The feedback

```
VERDICT: [Publish / Fix then publish / Rewrite] — [score]/100 — [one sentence why]

The one change that matters most: [specific]

Fixes, ranked by impact:
1. [Line or section quoted] → Problem: [...] → Fix: [rewritten line or exact instruction]
2. ...

What's strong (keep it): [1–2 specifics — only if true]

Missing: [anchor / source / data / FAQ / CTA / internal links — whatever applies]

Fact check: [each number → source and date found, or "unsourced — remove or source it"]
```

Then offer to apply the fixes and return the revised piece.

## Rules

- Quote the exact words you're criticising. "Make it punchier" isn't feedback; a rewritten hook is.
- Check facts against the linked sources when you can open them; say when you couldn't.
- Don't rewrite the author's voice into yours — fix the problem, keep their sound.
- Flag anything from `niche.out_of_scope` or `author.confidential` as a blocker.
