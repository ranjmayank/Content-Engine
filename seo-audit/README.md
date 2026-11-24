# SEO & AI-search audit

`audit.py` crawls your site like a search engine (respecting robots.txt), checks every page, and writes a ranked fix list. Standard library only — no keys, no install.

```bash
python3 seo-audit/audit.py                                  # brand.site from engine.config.json
python3 seo-audit/audit.py --site https://example.com --max-pages 500 --exclude /tag/
PSI_API_KEY=... python3 seo-audit/audit.py --psi            # + Core Web Vitals for the 5 most-linked pages
python3 seo-audit/audit.py --external                       # + check outbound links for 404s
pip install playwright && python3 -m playwright install chromium
python3 seo-audit/audit.py --render                         # render JavaScript before checking (SPA sites)
```

The **Weekly SEO audit** workflow runs it every week (`cadence.times.seo_audit`) and commits the reports. Ask Claude to "audit my site" and the `seo-audit` skill turns the report into 1–3 fixes worth the effort (and adds backlinks, rankings and AI visibility if OpenSEO is connected).

## Output (`reports/`)

| File | |
|---|---|
| `latest.md` (+ dated copy) | Score, what changed since last run, who can read your site, fix-first list, every issue with why and how to fix |
| `latest.json` | Everything, machine-readable (the skill reads this) |
| `pages.csv` | One row per URL: status, redirects, response time, depth, indexable, title, words, H1s, links, canonical, schema |
| `issues.csv` | One row per issue × URL, with the fix |

## What it checks

| Area | Checks |
|---|---|
| Access | Site reachable · HTTPS · HTTP→HTTPS redirect · www/non-www consolidated · robots.txt · **search, AI-search and AI-training crawlers allowed or blocked** (Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, PerplexityBot, Claude-SearchBot, GPTBot, ClaudeBot, Google-Extended, CCBot…) · llms.txt · soft 404s · bot blocking / rate limits |
| Crawl | 4xx and 5xx · broken internal links · redirect chains and loops · internal links to redirects · slow responses (>1.5 s) · very large HTML · JavaScript-only pages |
| Indexability | noindex (meta and header) · canonicalised pages · conflicting canonicals · sitemap found · sitemap URLs that aren't indexable · orphan pages · deep pages (5+ clicks) · pages with no outgoing links |
| On-page | Missing / duplicate / long / short titles and meta descriptions · missing or multiple H1 · skipped heading levels · thin content (<150 words) · duplicate content · images without alt · missing lang · missing viewport · missing Open Graph · mixed content |
| Links | Empty links · generic anchor text ("click here") · broken outbound links (`--external`) |
| Images | Heavy images (>300 KB) · broken images · images without width/height (layout shift) |
| International | Invalid hreflang codes · hreflang to broken/noindex pages · missing return links · missing self-reference |
| Sitemaps | Stale lastmod (>180 days) · files over 50,000 URLs / 50 MB |
| Structured data | No JSON-LD · invalid JSON-LD · Article schema without dates or author · FAQ schema that doesn't match the visible page |
| Speed (optional) | PageSpeed score, LCP, CLS, TBT, real-user LCP/INP |

Every check's severity, explanation and fix is in `issues.py`; thresholds are at the top. The issue set and thresholds are adapted from [OpenSEO](https://github.com/every-app/open-seo) (MIT).

**Score:** starts at 100; each issue type takes off up to 8 (critical), 3 (warning) or 1 (info), scaled by how many pages it affects. 90+ A · 75+ B · 60+ C · 40+ D.

**Limits:** by default it reads the HTML your server sends (as many AI crawlers do); use `--render` to check JavaScript-rendered content too. It doesn't know your backlinks or rankings; connect OpenSEO or use the analytics layer for those.
