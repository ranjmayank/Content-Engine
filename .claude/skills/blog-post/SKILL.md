---
name: blog-post
description: Write AEO + SEO blog posts for the site in engine.config.json — topic card, outline, full draft, pre-publish audit and publish checklist — as Deep posts or short Decode posts, built from dated sources, the author's own work and the site's Search Console + GA4 data. Use when the user asks for a blog, blog outline, decode post, or to optimize or refresh a post.
---

# Blog post — AEO + SEO

**First, read `engine.config.json`** and write in `niche.language` (default English). Everything below that says *the site*, *the author*, *the pillars*, *the audience*, *the voice* or *the CTA* means the values there (`brand`, `author`, `niche.pillars`, `niche.audience`, `voice`, `cta`). If the file is missing, stop and run the `engine-setup` skill first.

You write the canonical blog post for the site. Every other format (Medium, LinkedIn, carousel, Reel, newsletter) is derived from it, so it has to be the most complete, best-sourced version.

The post must work for three readers at once:
1. **Search engines and AI answer engines** (Google, Bing, AI Overviews / AI Mode, ChatGPT, Perplexity, Gemini, Claude, Copilot) — clear structure, direct answers, passages that can be lifted and cited on their own
2. **Human readers** — the audience in the config
3. **E-E-A-T** — visible Experience, Expertise, Authority and Trust

**Scope:** only the pillars in `niche.pillars` (each has a `covers` line saying what fits). Never write about anything in `niche.out_of_scope`; if a topic belongs there, say so and point to `niche.out_of_scope_goes_to` if it's set. Treat Google Search Central (https://developers.google.com/search/docs) as the source of truth for SEO. AEO is an extension of good SEO, not a set of tricks.

## How to work

- **Topic first.** Propose the topic (topic card below) and wait for approval before writing.
- **One topic at a time.** The blog anchors a series; other formats each cover a different detail.
- **Current news leads.** Build from sources published in the last few days. Older material can support, never lead. A news item older than 5 days loses a 3-filter point.
- **Data first.** Before proposing topics, read `analytics/reports/latest.md` and `analytics/opportunities.json`. A topic matching a query the site already gets impressions for beats a topic from scratch. If an analytics connector (OpenSEO, Rank Math via a WordPress MCP) is available and `integrations` says so, pull live numbers instead.
- **Site health first.** Glance at `seo-audit/reports/latest.md`: if it shows critical issues (blocked crawlers, broken pages, noindex on posts), mention them — they cap what any new post can achieve.
- **Site first.** Publish on the site first. If `channels.medium` is on, Medium gets it 2–3 days later via Import Story (canonical link), never copy-paste.

## Pick the tier

| Tier | Length | When | What it needs |
|---|---|---|---|
| **Deep post** (cornerstone) | 2,000–3,000 words | `cadence.deep_posts_per_week`; the cascade source | Full research, fan-out map, outline approval, full SEO/AEO pass, FAQ + Article + Person schema, original visual |
| **Decode post** (daily note) | 400–700 words | Other days | One news item, tool or data insight → what it means for the audience. Problem-led intro, TL;DR, 2–3 H2s, one takeaway, 2–3 FAQs, schema |

Ask which tier if it isn't clear. Default: news item → Decode; recurring reader question, a striking-distance query, or a big shift → Deep.

## The anchor rule

Every post needs **at least 2 of these 3 anchors**:
1. **A specific source** — dated, linked, with exact facts, numbers or quotes taken from it
2. **A specific work moment** — something the author saw in their work (`author.work_context`), anonymized
3. **A specific artifact** — a test they ran, a screenshot, a before/after, or a real number from the site's own Search Console or GA4

**The generic test:** could anyone in this niche have written it without reading anything this week or doing the author's job? If yes, rewrite it around an anchor or drop it. Never invent a number, not even as an illustration. If an example is hypothetical, label it as illustrative and use no fake statistics.

## Step 0 — Topic card (wait for approval)

```
TOPIC CARD
Idea: [one line]
Tier: Deep / Decode
News peg: [headline · publisher · date · link]
3-filter: In the pillars and the audience cares? [Y/N + why] · Angle? [Y/N + the angle] · One sharp line? [the line]
Score: [x/3]  (3/3 = write now · 2/3 = park · 1/3 = drop)
Pillar: [one of niche.pillars]
Your data: [matching Search Console query — impressions, position, page — or GA4 / AI-referral signal; "none yet"]
Target question people search: [...]
Primary keyword: [...]
Anchors available: [source ✓ · work moment ? · artifact ?]
Cascade value: [what LinkedIn posts / carousel / Reel this spawns]
```

When no topic is named, offer 2–3 cards: at least one from the news (newest digest in `scanner/sources/digests/` or today's `content/topic-lists/`) and, when the analytics report has one, one from the site's own data.

## Step 1 — Research (before any outline)

0. **The site's own data.** In `analytics/opportunities.json` find every related query and page: impressions, position, CTR, ranking page, question queries, AI-assistant referrals. Decide **new post or update an existing page**. If a page already ranks 8–20 for the target query, updating it usually beats a new URL — say so.
1. **Read the primary sources** with web fetch. If a story came from a roundup, find the original. If a page can't be opened, confirm through a second source or say plainly it couldn't be verified.
2. **A source card for each source:** published date · who says so (vendor / independent tester / journalist / survey firm) · what it says (2–3 sentences) · exact numbers · one quote · link. Keep vendor claims and independent findings apart.
3. **What already ranks.** Search the target question; read the top 3–5 results: what they cover, miss, and which format wins.
4. **What AI answers say.** Where possible run the question in an AI answer engine. Record the main points, the sources cited and what's missing — the cited pages are the competition, the gaps are the opening.
5. **Fan-out map.** List 5–8 sub-questions a searcher or AI would ask (site question queries first, then People Also Ask, related searches, the AI answers). Each maps to an H2, H3 or FAQ.
6. **Internal links.** Fetch the site's sitemap (`/sitemap.xml`, or `site:` search). Prefer linking from pages that already get impressions or AI referrals. List links out and the reverse links to add.
7. **Ask for the work moment** if the author hasn't given one; otherwise leave `[YOUR LINE]` markers. Never invent one.

For Decode posts, steps 0, 1, 2, 4 and 7 are required; 3, 5 and 6 can be quick.

## Step 2 — Outline (Deep posts: wait for approval)

```
BLOG OUTLINE
Title: [search-phrased question or claim, primary keyword, ≤60 characters; year only if time-sensitive]
Slug: /[lowercase-hyphenated, ≤60 chars, no stop words, no year]
Primary keyword · Secondary keywords (3–6) · Search intent · Target length
Your data: [queries + impressions + position + page · new post or update?]
What already ranks / what AI answers say, and the gap · Our edge: [the anchors no competitor has]
Fan-out map: [sub-question → H2 / H3 / FAQ]
Intro (~120–150 words): problem-led hook from the news
TL;DR box: 3–5 citable bullets
H2: [real reader question] — opening answer (1–2 standalone sentences) · covers · source(s) · anchor
Original visual · "What to do this week" · FAQ (count table below) · Internal links (2–5) · External links (3–5) · CTA
```

Don't write a Deep post until the outline is approved. For a Decode post, the approved topic card is enough.

## Step 3 — Write the post

**Structure**
- **Intro:** open with the news and why it matters to the reader. No definitions, no "In today's…". Primary keyword in the first 100 words. End with what the reader will get.
- **TL;DR box** right after the intro: 3–5 complete, citable bullets with the key numbers and dates.
- **Every H2 is a real question** from the fan-out map, and **opens with a direct answer** — 1–2 self-contained sentences, no "Direct answer:" label.
- **Tables** for comparisons, timelines, options, vendor-vs-independent numbers — real tables, never images.
- **"What to do this week"** before the FAQ: one action or one question for the reader.
- **Closing section** with a useful heading (never "Conclusion"): the takeaway and what to watch next.

**Write for retrieval (how AI search lifts passages)**
- Passages stand alone: no "as mentioned above", no pronouns that need earlier context.
- Name the entity in every section instead of "it" or "this tool".
- One question per H2, roughly 100–300 words before the next heading.
- Define a key term once, in the form "[Term] is a [category] that [does what]."
- Date changeable facts ("as of [Month Year]") and attribute in the sentence ("According to [publisher]'s [date] announcement…").
- Consistent terms; at least one specific, sourced, quotable sentence per H2.

**FAQ count by length**
| Post length | FAQs (on page and in schema) |
|---|---|
| under 500 words | 2–3 |
| 500–1,000 | 3–5 |
| 1,000–2,000 | 5–7 |
| 2,000+ | 7–10 |

FAQ schema contains **only** the questions and answers visible on the page, word for word. Each answer 2–4 standalone sentences.

**SEO:** primary keyword in title, slug, first 100 words, one H2, meta title and description; secondaries where natural. Meta title ≤60 characters; meta description 140–155. One H1. Descriptive alt text. OG image from the brand kit (`brand/og-1200x630.png` as default).

**E-E-A-T:** experience (work moments as lessons), expertise (plain definitions, mechanisms), authority (3–5 primary-source links), trust (every number linked and dated, vendor claims labelled, uncertainty stated), an original visual (Deep posts), author block and "Last updated".

**Links:** 2–5 internal (descriptive anchors) · 3–5 external to primary sources you've read.

**CTA:** mid-post `cta.mid`, end `cta.end`. Never pitch anything in `author.confidential`.

**Voice:** `voice.description`. Never use anything in `voice.banned_phrases`. Write to the depth the topic needs.

## Step 4 — Self-audit before handing over

Fix every ❌ first:

| Check | Pass? |
|---|---|
| In one of the pillars; nothing from out_of_scope | |
| Site data used; new-vs-update decision stated | |
| Built on recent news; dates shown | |
| 2 of 3 anchors present | |
| Every number linked to a dated source; none invented; vendor claims labelled | |
| Length fits the tier; intro problem-led; TL;DR present | |
| Every H2 a real question with a standalone opening answer; fan-out covered | |
| Entity named in every section; changeable facts dated and attributed | |
| Real tables; original visual (Deep) | |
| FAQ count fits; schema = on-page FAQs only | |
| Keyword placement; meta lengths; 2–5 internal + 3–5 external links | |
| Author block + last-updated; no banned phrases; nothing confidential | |
| People-first, non-commodity, helpful (Search Central) | |

Then a short verdict: strongest part, weakest part, and the one change that would most improve it.

## Output format

```
# [Title]

Slug: /[slug]
Meta title: [≤60]
Meta description: [140–155]
Primary keyword: [...]
Secondary keywords: [a, b, c]
Tier: Deep / Decode
Category: [pillar]
Tags: [a, b, c]
Last updated: [YYYY-MM-DD]
Featured image: [path or brief]
Author: [author.name] — [author.role_line]

---
[Intro]
> TL;DR …
## [H2 question] …
## What to do this week …
## Frequently asked questions …
## [Closing heading] …
[CTA]
**About the author** — [author.bio] · [brand.handles]
---
Schema (JSON-LD, ready to paste): BlogPosting (headline, description, image, datePublished, dateModified, mainEntityOfPage,
  author → Person with sameAs from brand.handles, publisher) · FAQPage (on-page FAQs only) · BreadcrumbList
Images: [featured image brief + alt text for every image]
Internal links to add to older posts · Source cards · Cascade hooks (3 quotable lines · carousel framework · Reel hook · LinkedIn angles)
```

## Step 5 — Publish checklist (hand over with the post)

- [ ] Add to the site; slug, category, tags, featured image, alt text, meta title + description
- [ ] Add schema; validate with Google's Rich Results Test or validator.schema.org
- [ ] View the live page source: body, tables and FAQ are in the HTML (not only loaded by scripts)
- [ ] Submit the URL in Google Search Console **and** Bing Webmaster Tools (Bing feeds Copilot and ChatGPT search); IndexNow if the site has it
- [ ] Add reverse internal links; add the post to llms.txt if the site keeps one
- [ ] Share on LinkedIn (link in the first comment) on publish day; add to the newsletter
- [ ] Medium Import Story 2–3 days later (if `channels.medium`)
- [ ] Note the target query; check it in the analytics report after 7 and 28 days
- [ ] Refresh date: 30 days for news-led posts, 90 days for Deep posts

**Static sites** (`publishing.platform` = `static` — Next.js, Astro, Hugo, Jekyll, Eleventy): save the post as `content/blog/<date>-<slug>.md` in exactly the output format above, then run `python3 tools/export_post.py content/blog/<file>.md` — it writes the post with front matter (title, description, slug, dates, author, tags, category, image, FAQ) into the site repo set in `publishing.static_site`. The JSON-LD goes in the site's template or the `schema` front-matter field. Commit to the site repo only with an explicit go-ahead.

**With connectors** (only those marked true in `integrations`, and never publish without an explicit go-ahead): WordPress (WordPress.com MCP or a WordPress MCP adapter) — create the post as a **draft**, then run the SEO plugin's checks if available; Google Drive — save the draft for review; Canva — in-post visuals from the brand kit.

After approval, offer the `blog-cascade` skill for the distribution set.

## Optimize mode

Given an existing post (pasted or a URL): fetch it, pull its queries from the analytics data, run the Step 4 audit as a table, list the top 3 AEO, SEO and E-E-A-T gaps, then rewrite the weakest parts (title, meta, intro, H2s, FAQ, links) showing before → after.

## Refresh mode

When a post hits its refresh date, appears in the analytics **Refresh** or **CTR fixes** lists, or the news has moved:
1. Re-check every source and number; replace outdated facts with dated new ones.
2. Add H2s/FAQs for queries it gets impressions for but doesn't answer; for a CTR fix, rewrite title + meta around the top query.
3. Re-run the AI-answer check: is the post cited? What do cited pages have that it lacks?
4. Update "Last updated", `dateModified` and any "as of" lines. Show a change log. Keep the URL unchanged.
