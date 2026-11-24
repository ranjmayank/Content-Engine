---
name: search-analytics
description: Read the site's Google Search Console and GA4 data and turn it into decisions — what to write next, which pages to refresh, which titles to rewrite, which queries are one update from page 1, and whether AI assistants are sending traffic. Use when the user asks about traffic, rankings, Search Console, GA4, analytics, "how is the site doing", "what should I update", or types /analytics.
---

# Search & analytics review

**First, read `engine.config.json`** (site, pillars, `integrations`).

You turn the site's own numbers into a short list of actions. A number is only useful if it ends in a decision: write, update, rewrite, merge, or leave alone.

## Where the data comes from

1. **The repo (default).** The "Daily search & analytics pull" GitHub workflow runs `analytics/fetch.py` (Search Console queries, pages, query × page, daily totals; GA4 landing page × source × medium × channel) for the last 28 days with data and the 28 before, then `analytics/analyze.py` writes `analytics/reports/latest.md` and `analytics/opportunities.json`. On Mondays it adds a row to `tracker/weekly-tracker.csv`. Read `opportunities.json` first; open the CSVs in the newest `analytics/data/YYYY-MM-DD/` only for a detail the report lacks.
2. **Live, through a connector** — only if `integrations` says it's connected:
   - **OpenSEO** (`get_search_console_performance`, `get_google_analytics_organic_landing_pages`, `get_google_analytics_traffic_acquisition`, `get_search_opportunities`, `get_ai_visibility_results`…) — needs a project for this site with Google connected in the OpenSEO dashboard.
   - **WordPress MCP with an SEO plugin** (e.g. Rank Math's `get-top-keywords`, `get-seo-scores`, AI-visibility abilities) — fresher, last 30 days.
3. If nothing is available, say so plainly and ask for a Search Console export (Queries + Pages) or a GA4 landing-page report. Never estimate.

Search Console lags 2–3 days. With under ~50 clicks a page, say "too early to call" rather than reading a trend.

## What to look at, in this order

| # | List (opportunities.json) | Meaning | Action |
|---|---|---|---|
| 1 | `scorecard` | Clicks, impressions, CTR, position, sessions, organic, AI referrals, key events vs previous 28 days | One sentence on direction and likely reason |
| 2 | `striking_distance` | Queries at positions 8–20 with real impressions | Update the ranking page: answer the query in an H2/FAQ using its words, add 2 internal links — usually the fastest win |
| 3 | `ctr_fixes` | Page-1 pages with under half the usual CTR | Rewrite title + meta around the top query; specific promise |
| 4 | `refresh` | Pages that lost 30%+ of clicks | `blog-post` Refresh mode; first check whether an algorithm update or a new AI Overview explains it |
| 5 | `new_post_ideas.gaps` / `.rising` | Shown for but ranking past 20 / new demand | A decode or deep post, by pillar |
| 6 | `question_queries` | How/what/why searches | H2s and FAQs, word for word |
| 7 | `cannibalisation` | Two pages splitting one query | Pick the owner; re-angle or merge the other |
| 8 | `ai_referrals` | Visits from ChatGPT, Perplexity, Gemini, Copilot, Claude… | Proof AEO works; keep cited pages fresh, link to them |
| 9 | `channels`, `key_event_pages` | Where sessions come from; which pages convert | Point CTAs and internal links at converting pages |

Queries are mapped to pillars from `scanner/sources/territories.json`; "Unmapped" means off-pillar — usually leave it (or add keywords to territories.json if it's a real pillar the keywords miss).

## Site health

Read `seo-audit/reports/latest.md` (the weekly audit) and add a "Site health" block with only the critical and warning items that affect the pages in this report. AI crawler access matters: search and answer bots (Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, PerplexityBot, Claude-SearchBot) must stay allowed; blocking training-only bots is a choice, not an error. Never change site settings — offer drafts; the owner applies them.

## Output

```
SITE CHECK — [date range]
Direction: [one sentence with the 2–3 numbers that matter]
This week's 5 actions (ranked by expected impact ÷ effort):
1. [Update / Rewrite / Write / Merge] — [page or query] — [the exact change] — why: [the number]
Post ideas from your data: [query · impressions, position · pillar · decode/deep · one-line angle]
AI assistants: [sessions by source, landing pages, change]
Site health: [only failing checks, each with the fix]
Too early to call: [anything with too little data]
```

## Rules

- Never invent or round up a number. Quote the window with every figure.
- Correlation isn't cause: "during the core update rollout", not "because of".
- Update before you create.
- Real site numbers are an **artifact** anchor for posts — offer one "From my data" LinkedIn post when a number is genuinely interesting.
