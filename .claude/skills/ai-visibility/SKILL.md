---
name: ai-visibility
description: Check whether AI assistants and AI search (ChatGPT, Perplexity, Gemini, Google AI Overviews, Copilot, Claude) mention or cite the site for the questions that matter in its niche, log the results over time, and say what to change. Use when the user asks "does ChatGPT mention us", "AI visibility", "are we cited in AI answers", "GEO/AEO check", or wants a monthly AI-visibility report.
---

# AI visibility check

**First, read `engine.config.json`** (and write in `niche.language`, default English): brand, site, pillars, `ai_visibility` (prompts and competitors, if set), `integrations`.

You find out whether answer engines cite the site for the questions its audience asks, track it over time in `tracker/ai-visibility.csv`, and turn the gaps into content and site fixes. Be honest about method: you can only report what you actually observed, with the date.

## Step 1 — The prompt set (10–30 prompts)

Use `ai_visibility.prompts` if it exists. Otherwise build it with the user and offer to save it to the config:
- 2–3 per pillar, phrased the way the audience asks an assistant ("what's the best way to…", "X vs Y for…", "how do I…")
- question queries from `analytics/opportunities.json` (`question_queries`, striking distance) — real demand first
- 2–3 brand prompts ("what is [brand]", "[author] [niche]")
- competitors to watch: `ai_visibility.competitors`, or the sites the answers keep citing

## Step 2 — Collect answers (use every route available, say which you used)

1. **OpenSEO** (if `integrations.openseo` and its tools are loaded): `save_ai_visibility_tracker` with the prompts → `run_ai_visibility_check` → `get_ai_visibility_results` / `get_ai_visibility_sources`. Confirm before anything that spends credits.
2. **WordPress SEO plugin with AI-visibility abilities** (e.g. Rank Math), if connected and a brand is set up.
3. **Your own web search:** run each prompt as an assistant would (search, read the top sources). Record which domains you'd cite and whether the site is among them. Label this "Claude's web-search view" — it's a proxy, not what ChatGPT shows.
4. **Manual spot-check by the user:** give them the 5 most important prompts to paste into ChatGPT (search on), Perplexity, Gemini and Google (AI Overview/AI Mode), and a one-line way to report back ("prompt — engine — cited? which URL?").

Also read `analytics/reports/latest.md` section 8: real sessions from ChatGPT, Perplexity, Gemini, Copilot and Claude, and their landing pages — the hard evidence.

## Step 3 — Log it

Append one row per prompt × engine to `tracker/ai-visibility.csv`:
`date, prompt, engine, brand_mentioned (y/n), site_cited (y/n), cited_url, competitors_cited, notes`. Engine = `openseo:<engine>`, `claude-web-search`, `manual:<engine>`. Never fill a row you didn't observe.

## Step 4 — Diagnose and act

- **Crawler access first:** read `seo-audit/reports/latest.md` → "Who can read your site". If OAI-SearchBot, PerplexityBot, Claude-SearchBot or Bingbot are blocked, that's the fix — nothing else matters until it's done.
- **Cited competitors:** open the pages that win. What do they have — a direct answer in the first lines, a table, original data, a clear date, an author, FAQ structure? List the gaps against the site's page for that prompt.
- **No page answers it:** a new post (hand to `blog-post`, with the prompt as the target question and the fan-out map).
- **A page exists but isn't cited:** `blog-post` Refresh mode — answer-first H2, standalone passages, dated facts, schema, internal links from pages that already get AI referrals.
- **Bing matters:** Copilot and ChatGPT search lean on Bing's index. Check the page is indexed in Bing Webmaster Tools; submit via IndexNow.

## Output

```
AI VISIBILITY — [date] — [n] prompts × [engines]
Cited in: [x of n prompts] (by engine) · mentioned but not cited: [y] · change since last check: [...]
AI referrals (GA4, 28 days): [sessions by assistant, top landing pages]
Top 3 moves: [prompt → page → the exact change → why (who's cited instead)]
Prompts where nobody in your niche is cited well: [openings]
Method note: [which routes were used; what's a proxy]
```

Suggest re-running monthly (a Claude scheduled task with this skill works well).
