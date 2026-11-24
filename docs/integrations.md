# Optional integrations

Every integration is optional. After you connect one, set it to `true` under `integrations` in `engine.config.json` so the skills know to use it. Skills never publish, schedule or change anything through an integration without your explicit go-ahead.

## OpenSEO — backlinks, rankings, AI visibility, deeper audits

[OpenSEO](https://openseo.so) is an open-source (MIT), pay-as-you-go alternative to Semrush/Ahrefs, with an MCP server for AI agents. The built-in audit (`seo-audit/audit.py`) is free and covers technical and on-page SEO; OpenSEO adds what a crawler alone can't see:

| Need | OpenSEO tool |
|---|---|
| JavaScript-rendered crawl, Lighthouse | `run_site_audit`, `get_audit_issues`, `get_audit_lighthouse` |
| Backlinks and authority | `get_backlinks_overview`, `get_backlinks_profile`, `get_domain_overview` |
| What you rank for / competitors | `get_ranked_keywords`, `find_serp_competitors`, `get_serp_results` |
| Search Console + GA4, any date range | `get_search_console_performance`, `get_google_analytics_*` |
| AI visibility (ChatGPT, Perplexity, Gemini mentions and citations) | `save_ai_visibility_tracker`, `run_ai_visibility_check`, `get_ai_visibility_results` |
| Keyword research | `research_keywords`, `get_keyword_metrics` |

**Connect:**
- claude.ai: **Customize → Connectors** → add OpenSEO from the directory (or the OpenSEO plugin on paid plans). Claude Code: follow openseo.so/docs/claude-code-plugin.
- Create a project for your site (free) and connect Google in the OpenSEO dashboard for Search Console/GA4 data.
- Self-hosting: clone github.com/every-app/open-seo and follow its docs; bring your own DataForSEO key.
- Site audits are included on every plan (up to 50 pages free at the time of writing); backlink, ranking and keyword lookups spend credits. The `seo-audit` skill always says before it runs anything paid.

## Notion — the Fuel Database

1. notion.so/profile/integrations → **New integration** → copy the secret.
2. Open the page that will hold the database → **••• → Connections** → add the integration.
3. `NOTION_TOKEN=secret_xxx python3 setup/create_notion_db.py <page-id>` → prints the database ID.
4. GitHub secrets `NOTION_TOKEN` and `NOTION_DATABASE_ID`.

The scanner sends only **top picks** (score ≥ 2), with the source card in the page body. Columns: Idea · Source · Territory (your pillars) · Link · Angle · Status · Score. Using an existing database with Notion's built-in Status column? Set the variable `NOTION_STATUS_TYPE` to `status`. In Claude, the Notion connector lets `weekly-plan` read Raw items and write scores back.

## WordPress — drafts and SEO-plugin checks

- **WordPress.com / Jetpack-connected sites:** the WordPress.com connector can create drafts, edit posts and upload media.
- **Self-hosted with the WordPress MCP Adapter** (and Rank Math, Yoast or similar exposing abilities): live Search Console keywords, on-page analysis of drafts, schema, link reports, 404 logs, robots.txt and llms.txt.

The `blog-post` skill creates **drafts only**. Watch for two plugins both writing schema or llms.txt — the audit flags invalid schema; check one post in Google's Rich Results Test.

## Canva

The Canva connector can build carousels and quote cards from your brand kit. Upload the files from `brand/` to a Canva brand kit first so designs match.

## Social scheduling

Any scheduler with a Claude connector (for example PostZen, Buffer-style tools) lets `news-fast-lane`, `blog-cascade` and `weekly-plan` queue posts. LinkedIn posts do best published natively with the link in the first comment. Facebook can mirror Instagram from Meta Business Suite.

## Google Drive

Save drafts for review in a Drive folder. Note the folder in `integrations` (e.g. `"google_drive_folder": "Content/Drafts"`) and the skills will use it.

## PageSpeed Insights

Google Cloud → enable **PageSpeed Insights API** → create an API key → secret `PSI_API_KEY`. The weekly audit then adds mobile performance and real-user Core Web Vitals for your five most-linked pages. Without a key it works at low volume locally: `python3 seo-audit/audit.py --psi`.

## Video (reels)

The `reel` skill writes scripts and production sheets with no setup. For finished videos it uses [Remotion](https://www.remotion.dev) in a `reels/` folder, with a free local voice (Kokoro) or ElevenLabs (`ELEVENLABS_API_KEY` in a local `.env`, never committed).
