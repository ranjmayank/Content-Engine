---
name: weekly-plan
description: Weekly planning session — score the week's fuel items with the 3-filter and build the full content week (deep posts, decode posts, LinkedIn and Instagram) from engine.config.json's cadence. Use when the user says /sunday, /plan, "plan my week", "weekly plan", or pastes a fuel dump.
---

# Weekly content plan

**First, read `engine.config.json`** (and write in `niche.language`, default English): `niche.pillars`, `niche.audience`, `channels`, `cadence` (posts per week, timezone), `integrations`. Read `docs/daily-cadence.md` and `docs/content-fuel-system.md` if they aren't in context.

**Surfaces and roles** (only those switched on in `channels`)
- **The site** — the canonical home; every blog post publishes here first.
- **LinkedIn** — the positioning surface, anchored in the author's work.
- **Instagram / Shorts** — the distribution surface; the niche's changes decoded for the audience.
- **Facebook** — mirrors Instagram automatically (`facebook_mirror`); never plan separate content.
- **Medium** — echo of the blog via Import Story, 2–3 days later.
- **Newsletter** — one personal letter a week, built from the week's posts.

**Weekly targets:** `cadence.deep_posts_per_week` deep posts · `cadence.decode_posts_per_week` decode posts · `cadence.linkedin_per_week` LinkedIn posts · `cadence.instagram_per_day` Instagram posts a day.

## The anchor rule

Every piece needs **2 of 3**: a dated, linked source fact · an anonymized work moment (`author.work_context`) · an artifact (a test, screenshot, or a real number from the site's analytics). Never invent a number.

## Step 1 — Intake

1. **This week's fuel** — the digests in `scanner/sources/digests/`, the last few `content/topic-lists/`, the Notion Fuel Database (if `integrations.notion`, Status = Raw or Scored), or pasted text. Each item needs its source card.
2. **This week's data** — `analytics/reports/latest.md` and `opportunities.json`: striking distance, CTR fixes, refreshes, gaps, questions, AI referrals.
3. **Site health** — `seo-audit/reports/latest.md`: any critical item goes in the week's housekeeping.
4. **Work notes** — 2–3 anonymized moments from the author's week. Ask if there are none.
5. **Last week's numbers** — best and worst post, profile visits, follower change (or `tracker/weekly-tracker.csv`).

No fuel? Search the web for this week's news in each pillar, read the primary sources, build source cards. Never plan a week from evergreen ideas alone.

## Step 2 — Score every item

| Question | Pass means |
|---|---|
| In the pillars, and does the audience care? | It changes something the audience does. Out-of-scope items score 0. Items matching a site query get the point automatically. |
| Is there an angle? | From the author's work or lens — not a summary anyone could write |
| One sharp line? | If the hook can't be written, the idea isn't ready |
| 2 anchors? | Without them an item can't score 3/3 |

3/3 → schedule · 2/3 → park, note what's missing · 1/3 → archive. News older than 5 days drops a level. Write scores back to Notion if connected (ask first).

## Step 3 — Build the week

- **Deep posts** — the strongest 3/3 items with depth: working title (the search question), the proof from the author's work, the assets it spawns (LinkedIn ×2, carousel, Reel, newsletter section, Medium).
- **Decode posts** — one per remaining slot: news → what it means, 400–700 words. At least one a week from the site's own data. Each also becomes that day's Reel.
- **LinkedIn** — rotate through the pillars (one pillar per day), plus one POV/question post and one "From my data" post with a real number from the site. Weight toward last week's winning pillar but don't drop a pillar two weeks running. For every post: the hook (<15 words, never starting with "I" or the brand) and its anchors; mark missing work moments `[YOUR LINE]`.
- **Instagram** — per day: news Reel (from the decode post), carousel or quote card, a light post — up to `cadence.instagram_per_day`.

## Step 3b — Put the week where it gets done (ask before writing anywhere)

Notion tasks (if connected) · scheduler queue (if connected) · Google Drive drafts (if connected).

## Step 4 — One adjustment

From last week's numbers, name exactly **one** thing to stop, change or double down on, with the number that justifies it.

## Output

1. Scored fuel table (item · score · reason · anchors)
2. The week, day by day: blog · LinkedIn hook · anchors · Instagram slots
3. Housekeeping: top 3 from the analytics report and any critical audit item, each with the page and the change
4. The one adjustment
5. Offer to write Monday's decode post and LinkedIn post in full.
