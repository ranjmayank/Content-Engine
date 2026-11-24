---
name: engine-setup
description: Set up or re-configure this Content Engine for the user's niche — interview them about brand, site, pillars, audience, voice, channels and cadence, write engine.config.json and the source list with setup/init.py, then walk them through every access and secret the automations need. Use when engine.config.json is missing, or the user says "set up", "configure", "change my niche", "add sources", or asks what access the engine needs.
---

# Engine setup

You set the engine up for the user's niche in a conversation, so they never have to edit JSON. Ask in small groups (2–4 questions at a time), offer sensible defaults, and keep going.

## Step 1 — Interview

Check whether `engine.config.json` exists; if it does, show the current values and ask only what they want to change.

1. **Brand and site:** brand name, website URL (where posts live), one-line tagline. The site's platform (WordPress, Webflow, Ghost, Shopify, custom…) — note it for later steps.
2. **Author:** name, one line on what they do, a 2-sentence bio, what their day job lets them see (used for "from my work" anchors, anonymized), and anything never to name (employer, clients) with how to refer to it instead.
3. **Niche:** show the presets (`python3 setup/init.py --list-presets`): ai-marketing, ai-business-security, b2b-saas, ecommerce, personal-finance, health-fitness, travel, local-business, developer-tools, blank. Pick one, then review the pillars together (3–6 pillars, each with a "covers" line). For a custom pillar, propose 10–20 keywords that would appear in a headline about it, and confirm them. Ask for audience, region, and what's out of scope.
4. **Channels:** blog, LinkedIn, Instagram, Facebook mirror, YouTube Shorts, X, Medium, newsletter — and the handles/URLs.
5. **Cadence:** timezone (IANA name), posts per week per channel, and the times for the analytics pull, news scan, topic list, email and weekly audit.
6. **Voice and look:** voice in a few words, phrases to ban (start from the default list), colours (hex), CTAs.
7. **Sources:** keep the preset's sources (if any)? Then ask for the 5–20 sites they actually read in this niche; you'll find the feeds.

## Step 2 — Write the files

Write the answers to a temporary JSON in the shape of `engine.config.example.json` (add `"use_preset_sources": true/false` and `"add_sources": [{"url": "...", "category": "<pillar>", "why": "..."}]`; for custom pillars put `"keywords": [...]` on each pillar), then run:

```bash
python3 setup/init.py --answers /tmp/answers.json
python3 brand/scripts/make_brand.py        # starter brand kit (needs Pillow)
```

This writes `engine.config.json`, `scanner/sources/territories.json`, `scanner/sources/sources.json`, `CLAUDE.md`, `style.md` and converts the workflow schedules to UTC. If this environment can't reach the web, `discover_feed.py` adds unreachable sites as "manual" — tell the user the first GitHub run will show which feeds work in `scanner/sources/SOURCES.md`, and they can re-run `python3 setup/discover_feed.py <url> --add` locally.

Show what was written in a short summary and ask them to commit and push (or do it for them if they've asked you to and you have push access).

## Step 3 — Access checklist (ask for each; never ask them to paste a secret into chat)

Walk through `docs/ACCESS.md` in order and record each answer. For anything that needs a secret, tell them exactly where to paste it (GitHub → Settings → Secrets and variables → Actions) — secrets never go in chat, in a file, or in a commit.

| # | What | Needed for | Required? |
|---|---|---|---|
| 1 | GitHub repo (their fork/copy) with Actions enabled | everything automated | yes |
| 2 | Google Search Console + GA4 via a service account (`GOOGLE_SERVICE_ACCOUNT_JSON`, `GSC_SITE_URL`, `GA4_PROPERTY_ID`) | analytics report | recommended |
| 3 | SMTP email (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `MAIL_TO`) | daily topic email | optional |
| 4 | Notion integration (`NOTION_TOKEN`, `NOTION_DATABASE_ID`) — `python3 setup/create_notion_db.py` makes the database | Fuel Database | optional |
| 5 | PageSpeed API key (`PSI_API_KEY`) | Core Web Vitals in the audit | optional |
| 6 | Claude connectors: OpenSEO, WordPress, Canva, Notion, Google Drive, a social scheduler | live data, drafts, visuals, scheduling | optional |
| 7 | A Claude scheduled task for the topic list (prompt in the `topic-list` skill) | daily topic list | optional |

After each connector they add, set it to `true` under `integrations` in `engine.config.json`.

## Step 4 — First run

1. Actions → "Daily fuel scan" → Run workflow. Then open `scanner/sources/SOURCES.md` together and fix or remove any 🔴 source.
2. Actions → "Weekly SEO audit" → Run workflow → read the result with the `seo-audit` skill.
3. If Google is set up: Actions → "Daily search & analytics pull" → Run workflow → `search-analytics` skill.
4. Offer the `weekly-plan` skill to plan their first week.
