# Search & analytics layer — Search Console + GA4

Every morning (at `cadence.times.analytics`) the "Daily search & analytics pull" workflow:
1. `fetch.py` pulls your site's **Google Search Console** (queries, pages, query × page, daily totals) and **GA4** (landing page × source × medium × channel, daily sessions) for the last 28 days with data and the 28 days before. Files land in `data/YYYY-MM-DD/` (the last 14 pulls are kept).
2. `analyze.py` writes `reports/latest.md` (plus a dated copy) and `opportunities.json`. On Mondays it adds a row to `tracker/weekly-tracker.csv`.
3. The topic-list task and the skills (`blog-post`, `search-analytics`, `weekly-plan`) read `opportunities.json`.

## What the report gives you

| # | Section | The decision it drives |
|---|---|---|
| 1 | Scorecard | Clicks, impressions, CTR, position, sessions, organic, AI-assistant referrals, key events — vs the previous 28 days |
| 2 | Striking distance | Queries at positions 8–20 → add a section/FAQ + internal links to push them to page 1 |
| 3 | CTR fixes | Page-1 pages with under half the usual CTR → rewrite title + meta |
| 4 | Refresh | Pages that lost 30%+ of clicks → update facts, re-date |
| 5 | New post ideas | Queries Google shows you for but no page answers (position > 20), and rising queries → new posts, by pillar |
| 6 | Question queries | How/what/why searches → H2s and FAQs, word for word |
| 7 | Cannibalisation | Two pages splitting one query → pick an owner |
| 8 | AI assistant referrals | Sessions from ChatGPT, Perplexity, Gemini, Copilot, Claude — by source and landing page |
| 9 | Channels + converting pages | Where sessions come from; which pages produce key events (newsletter sign-ups) |

Thresholds (minimum impressions etc.) are at the top of `analyze.py` and are set for a small site — raise them as traffic grows.

## One-time setup (about 15 minutes)

1. **Google Cloud project.** console.cloud.google.com → create (or pick) a project → *APIs & Services → Library* → enable **Google Search Console API** and **Google Analytics Data API**.
2. **Service account.** *IAM & Admin → Service accounts → Create*. No roles needed. Open it → *Keys → Add key → JSON* → download the file. Copy the service account's email (…@….iam.gserviceaccount.com).
3. **Give it read access.**
   - Search Console → your property → *Settings → Users and permissions → Add user* → the service account email, permission **Restricted** (read-only is enough).
   - GA4 → *Admin → Property access management → +* → the service account email, role **Viewer**. Note the **Property ID** (Admin → Property details, a number like 123456789).
4. **Add to GitHub** (repo *Settings → Secrets and variables → Actions*):
   - Secret `GOOGLE_SERVICE_ACCOUNT_JSON` = the whole contents of the JSON key file.
   - Variable `GSC_SITE_URL` = `sc-domain:example.com` for a domain property, or `https://example.com/` for a URL-prefix property (it must match the property exactly).
   - Variable `GA4_PROPERTY_ID` = the number from step 3.
5. **Run it once:** Actions → "Daily search & analytics pull" → Run workflow. Check `analytics/reports/latest.md`.
6. **Recommended in GA4:** mark the newsletter sign-up as a **key event**, so section 9 shows which pages convert.

Never commit the JSON key; `.gitignore` blocks the usual file names.

## Running it by hand

```bash
pip install google-auth requests
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json   # or GOOGLE_SERVICE_ACCOUNT_JSON='{…}'
export GSC_SITE_URL=sc-domain:example.com GA4_PROPERTY_ID=123456789
python3 analytics/fetch.py && python3 analytics/analyze.py
```

## In a Claude session

The `search-analytics` skill reads `opportunities.json`. If OpenSEO or a WordPress SEO plugin is connected (see docs/integrations.md), it can pull fresher numbers live; the repo report stays the default.
