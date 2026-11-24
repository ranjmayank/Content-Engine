---
name: topic-list
description: Build today's ranked topic list from the scanner digest and the site's Search Console/GA4 opportunities — 8–12 news topics plus 2–4 "From your data" topics — saved as content/topic-lists/<date>.json and rendered to markdown, an email and a page. Use when the user asks for today's topics or topic list, or when the daily scheduled topic-list task runs.
---

# Daily topic list

**First, read `engine.config.json`** (pillars, audience, out_of_scope, `cadence.timezone`) and `content/topic-lists/README.md` (the JSON format).

## Steps

1. **Update the repo.** `git pull` (in a scheduled run: clone the repo with push access first). Read the most recent `content/topic-lists/YYYY-MM-DD.json` as the format example.
2. **Inputs.** (a) The newest digest in `scanner/sources/digests/` plus `scanner/sources/fuel_inbox.csv` rows since the previous list — skip stories used in the last 3 lists unless there's a new development. (b) `analytics/opportunities.json` and `analytics/reports/latest.md`. If data is missing, say so in `scanned` and continue with news only.
3. **Scope.** Pillars only (`niche.pillars`); never `niche.out_of_scope`.
4. **Analyse.** 8–12 news topics — read the primary sources (web search, then web fetch) — plus 2–4 **"From your data"** topics (best striking-distance query, biggest gap or rising query, a refresh or CTR fix). Add a `data` line to any news topic that matches a site query.
   Per topic: `id`, `category` (a pillar name exactly, or "From your data"), `priority` (Top pick / Strong / Good), `format` (Decode / Deep / LinkedIn / Reel…), `title`, `why`, `data` (optional), `facts` (2–4, dated and sourced — never invent), `angle`, `refs` (only real URLs you opened, as [name, url] pairs), `fanout` (5–7 queries; prefer real question queries from the data). Top level: `date`, `window`, `scanned`, `topics`.
5. **Save and render.** Write `content/topic-lists/<today>.json`, run `python3 tools/render_topics.py content/topic-lists/<today>.json`, commit "Topic list <today> [skip ci]", `git pull --rebase`, push.
6. **Optional page.** If the user wants a shareable page, publish `content/topic-lists/latest.html` as an artifact (re-publish the same one each day; its URL can go in the `TOPIC_PAGE_URL` repo variable so the email links to it).
7. **Summary.** Top 3 topics, the best "From your data" action, the page link, and anything that failed.

The "Daily topic email" workflow sends `<today>.email.html` at `cadence.times.email`; if no list was built, it sends the scanner's top picks instead.

## Scheduling it

Create a Claude scheduled task at `cadence.times.topic_list` (after the scan, before the email) with this prompt:

```
Build today's topic list for the content engine in GitHub repo <owner>/<repo>: attach the repo with push access,
clone it, and follow .claude/skills/topic-list/SKILL.md exactly. It must be pushed before <email time> <timezone>.
```
