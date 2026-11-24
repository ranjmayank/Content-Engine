---
name: blog-cascade
description: Turn one finished deep blog post into its full distribution set — 2 LinkedIn posts, a newsletter section, an 8-slide carousel, a Reel script, a quote card, and the publishing checklist for the site and Medium. Use when a blog post is done and needs distributing.
---

# Blog Cascade

**First, read `engine.config.json`** — `channels` decides which assets to make (skip any channel that's off), `brand.handles` goes in CTAs, `hashtags`, `voice` and `author.confidential` apply to everything.

You turn one finished **deep post** into every asset it should feed. One post, written once, distributed everywhere. Ask for the post (text or link) if it isn't provided.

**The core rule:** same idea, different entry point for every asset. Never open two assets the same way; never make one asset a summary of another.

## Step 0 — Check the post's anchors

List every source the post cites (link + fact) and every work moment or artifact. Flag any number without a linked source. If the post has fewer than 2 anchors (dated source · work moment · artifact), say so first and suggest what to add — distributing a generic post six ways makes six generic posts. Every asset must carry at least one concrete sourced fact or work moment, not just the framework.

## The assets, in publishing order

### 1. LinkedIn post A — the framework (publish day)
Core framework as a standalone post. Hook under 15 words (never starting with "I" or the brand name) · rehook (2–3 lines before "see more") · short paragraphs, numbered steps · one takeaway · an engagement question · 3–5 hashtags · **blog link in the first comment, never the body.**

### 2. Newsletter section (if `channels.newsletter`)
150–250 words in the author's personal letter voice ("This week I broke down…"): why they wrote it, the one idea worth stealing, one link. Not the intro pasted.

### 3. LinkedIn post B — a different angle (2 days later)
One of: the contrarian take · the proof/example · "what most people get wrong" · the stat that surprised them. Lead with the most specific anchor. Must not summarise post A.

### 4. Carousel — 8 slides (1080×1350; also a LinkedIn PDF)
1 Hook (6–10 words) · 2 The problem (one stat or scenario) · 3 Why it's worse than you think · 4 The shift · 5 The framework (3–4 steps, verbs first) · 6 Proof or example · 7 This week (one action) · 8 CTA ("Full playbook → [brand.site_name]" + handle). Max 20 words a slide; source footer on any slide with a number. Then the Instagram caption with 5 hashtags.

### 5. Reel script — 40 seconds, faceless (if Instagram or Shorts)
The post's most surprising element. ON-SCREEN TEXT (≤8 words) | VOICEOVER. Hook in 2 seconds, 3 points, payoff, CTA. For a full produced reel, hand to the `reel` skill.

### 6. Quote card
The most quotable sentence (under 20 words), 2–4 words marked for the accent colour.

### 7. Publishing checklist
**Site first:** title = the search question · TL;DR · FAQ + FAQ/Article/Person schema · meta + OG image · internal links both ways · every stat linked · author block + last updated · submitted in Search Console and Bing · in the pillars · matching question/striking-distance queries from `analytics/reports/latest.md` answered as H2 or FAQ.
**Medium (if on, 2–3 days later):** Import Story only (sets the canonical); fix formatting; 5 tags.

### 8. Production and scheduling
Carousel and quote card in Canva from the brand kit (if `integrations.canva`) or from `brand/`; Reel via the `reel` skill; scheduling via a connected scheduler (if `integrations.postzen` or similar) — **ask before scheduling anything**; tasks into Notion (if `integrations.notion`).

## Output

One document, assets in the order above, each ready to copy, ending with suggested publishing dates for the week (based on `cadence`).

## Rules
- Respect `author.confidential`. No `voice.banned_phrases`. Don't invent stats — flag unsourced numbers instead of repeating them.
