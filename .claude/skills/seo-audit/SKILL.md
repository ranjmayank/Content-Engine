---
name: seo-audit
description: Audit the site for SEO and AI-search problems and turn the findings into a short, prioritised fix plan — using the free built-in crawler (seo-audit/audit.py) and, when connected, OpenSEO for backlinks, rankings, Lighthouse and AI visibility. Use when the user asks for an SEO audit, site audit, technical SEO check, "why isn't my site ranking", "can ChatGPT find my site", or types /audit.
---

# SEO & AI-search audit

**First, read `engine.config.json`** (`brand.site`, `seo_audit`, `integrations.openseo`).

You find what's stopping the site from ranking and being cited, and say what to fix first in plain words — for someone who may never have done SEO. Every recommendation names the page(s), the exact change, and why it's worth the effort.

## Step 1 — Get the crawl

1. **Use the latest report** if `seo-audit/reports/latest.json` is less than 7 days old (the "Weekly SEO audit" workflow writes it).
2. **Otherwise run it** (needs network access to the site):
   ```bash
   python3 seo-audit/audit.py                    # brand.site, up to seo_audit.max_pages
   python3 seo-audit/audit.py --max-pages 500 --psi   # bigger crawl + PageSpeed for the top 5 pages
   ```
   If this environment can't reach the site, tell the user to run the workflow: GitHub → Actions → "Weekly SEO audit" → Run workflow, then pull and re-read `seo-audit/reports/latest.json`.
3. Read `latest.json`: `score`, `site` (crawler access, llms.txt, sitemaps, pages crawled, `stopped_at_limit`), `issues` (severity, count, urls, details, fix), `pagespeed`.

What the crawler checks: status codes, redirects and loops, broken internal links, slow responses, JavaScript-only pages, noindex, canonicals, sitemap hygiene, orphan and deep pages, titles, meta descriptions, H1s and heading order, thin and duplicate content, image alt text, lang, viewport, Open Graph, mixed content, JSON-LD validity and Article dates/author, HTTPS and host consolidation, robots.txt, soft 404s, llms.txt, and which search / AI-search / AI-training crawlers robots.txt lets in. It reads the HTML the server returns; it doesn't run JavaScript.

## Step 2 — Go deeper with OpenSEO (only if connected)

If `integrations.openseo` is true and OpenSEO tools are loaded (`whoami` and `list_projects` are free reads — run them first; never claim it's connected until they succeed):
- No project for this site? Offer to `create_project` (free). Don't run paid research without saying it uses credits.
- `run_site_audit` → `get_audit_status` → `get_audit_issues` / `get_audit_pages` (and `get_audit_lighthouse` if the user wants performance depth). Compare with the local crawl; OpenSEO can render JavaScript.
- `get_backlinks_overview`, `get_domain_overview`, `get_ranked_keywords` — authority and which pages rank.
- `get_search_opportunities` / `get_search_console_performance` if Google is connected there.
- `get_ai_visibility_results` if an AI-visibility tracker exists — is the brand mentioned or cited by ChatGPT, Perplexity, Gemini?
- For the full OpenSEO workflow, its own `seo-audit` skill (github.com/every-app/open-seo, `.agents/skills/seo-audit`) can be installed alongside this one.

Not connected? Mention once that OpenSEO (open source, pay-as-you-go; docs/integrations.md) adds backlinks, rankings and AI-visibility tracking, then continue with the local crawl.

## Step 3 — Diagnose before prescribing

- **Broken site first.** If `site-unreachable`, `search-engine-blocked`, `blocked-page` or `no-https` appear, investigate why (expired certificate, firewall, staging robots.txt left live) before anything else.
- **Partial crawl?** If `stopped_at_limit`, say the numbers are a sample and suggest a bigger `--max-pages`.
- **Weigh effort against benefit.** A site-wide template fix (missing viewport, no Open Graph, no schema) is one change that fixes hundreds of pages — rank it high. Twenty "title too long" notes on old tag pages are low value.
- **Cross-check with search data.** If `analytics/opportunities.json` exists, prioritise issues on pages that already get impressions or sit in striking distance. A noindex on a page with impressions is urgent; on a thank-you page it's correct.
- **AI search.** Blocked AI-search crawlers mean the site can't be cited by those assistants — critical if AEO is a goal. Blocked training crawlers are a business choice: explain, don't "fix".
- Separate confirmed findings from hypotheses.

## Step 4 — The report

```
SEO AUDIT — [site] — [date] — score [n]/100 ([grade])
Verdict: [one sentence: the state of the site and the single biggest problem]

What to do (1–3 moves, ranked by benefit ÷ effort):
1. [Move] — pages: [list or "site-wide"] — Do this: [numbered steps, CMS-specific if you know the CMS] — Why: [the evidence, with counts] — Effort: [minutes/hours]

Who can read your site: [search / AI search / AI training crawlers, llms.txt, sitemap]
What else we checked: [table: issue · pages · decision (fix later / fine as is / not worth it) · one-line reason]
Speed: [PageSpeed table if run]
Since last audit: [score change, new and fixed issues]
```

Explain every technical term in plain words the first time. If the user wants a shareable page, offer to publish the report as an artifact or doc.

## Rules

- Never change the site, robots.txt or plugin settings yourself. Give exact steps; the owner applies them. With a WordPress connector, offer to create drafts or show the change — apply only with an explicit go-ahead.
- Never invent counts — every number comes from `latest.json`, OpenSEO or Search Console, with its date.
- Re-run the audit after fixes and report what changed.
