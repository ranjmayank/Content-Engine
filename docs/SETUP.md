# Setup from the terminal (advanced)

> **Not comfortable with a terminal? Use [START-HERE.md](START-HERE.md)** — the same setup in your browser, with a form.
>
> In a hurry? `python3 setup/quick.py` asks 6 questions and fills the rest with defaults. `python3 setup/check.py` shows what's set up.

Each step works on its own: stop after step 4 and you already have a daily news digest and a weekly SEO audit. Steps 5–9 add your search data, email, Claude and integrations.

| Step | What you get | Time | Cost |
|---|---|---|---|
| 1. Copy the repo | Your own engine | 2 min | Free |
| 2. Run the setup | Everything tuned to your niche | 5–10 min | Free |
| 3. Brand kit | Avatar, covers, OG image, quote card | 2 min | Free |
| 4. Turn on GitHub Actions | Daily scan + weekly audit | 3 min | Free (public repos; private repos get 2,000 Actions minutes/month on GitHub Free — this engine uses roughly 150–300) |
| 5. Search Console + GA4 + Bing | Daily analytics report | 20 min | Free |
| 6. Email | Topic list in your inbox | 5 min | Free with Gmail |
| 7. Claude | Skills + daily topic list | 10 min | A Claude plan, or Claude API credits for the topic-list workflow |
| 8. Optional integrations | Notion, OpenSEO, WordPress, Canva, scheduler | varies | Their own pricing |
| 9. First week | A planned week of content | 20 min | — |

**You need:** a GitHub account, Python 3.10+ on your computer (for setup; the automations run on GitHub), and a website with a blog. Everything you'll be asked for is listed in [ACCESS.md](ACCESS.md).

> **On Windows:** install Python from python.org (tick "Add python.exe to PATH") and Git for Windows. Use `py` instead of `python3` in every command (e.g. `py setup\init.py`), or run everything in **Git Bash**, where the commands work exactly as written — including `bash tests/run.sh`. WSL works too. The GitHub Actions jobs run on Linux, so nothing else changes.

**See what you'll get first:** [`examples/`](../examples/) has a sample digest, audit, analytics report and topic list.

---

## 1. Copy the repo

- On GitHub, click **Use this template → Create a new repository** (or **Fork**).
- **Public or private?** Private if you'll keep Search Console / GA4 numbers in it (the analytics job commits them). Public is fine for the scanner and audit alone.
- Clone it: `git clone https://github.com/<you>/<repo> && cd <repo>`

## 2. Run the setup

```bash
python3 setup/init.py --list-presets   # see the niches
python3 setup/init.py                  # answer the questions (Enter keeps the default)
```

Or open the repo in Claude Code / a Claude project and say **"set up the engine"** — the `engine-setup` skill asks the same questions in conversation and runs the script for you.

You'll be asked about:
- **Brand and site** — name, URL, tagline
- **You** — name, a line on what you do, a short bio, what your job lets you see (the skills use this for "from my work" moments, anonymized), and anything never to name (employer, clients)
- **Niche** — a preset, then your pillars (3–6 topics). For custom pillars you give keywords that would appear in a headline about each
- **Channels and handles** — blog, LinkedIn, Instagram, Facebook, Shorts, X, Medium, newsletter
- **Cadence** — timezone (IANA name like `Asia/Kolkata` or `Europe/London`), posts per week, and when each daily job runs (converted to GitHub's UTC cron for you)
- **Voice and look** — voice in a few words, banned phrases, colours, calls to action
- **Sources** — keep the preset's tested list (AI-marketing and AI-security presets) and/or add the sites you read

It writes `engine.config.json`, `scanner/sources/{sources,territories}.json`, `CLAUDE.md`, `style.md`, and updates the workflow schedules. Re-run it whenever you want to change something.

**Add sources later:**
```bash
python3 setup/discover_feed.py https://site.com/blog --add --category "Your pillar" --why "What it's for"
python3 setup/discover_feed.py --file my-sites.txt --add     # one per line: url | category | why
```
It looks for an RSS/Atom feed, then common feed paths, then the sitemap. Sites with neither are listed as "check manually".

## 3. Brand kit

```bash
pip install Pillow
python3 brand/scripts/make_brand.py
```
Writes `brand/avatar-1000.png`, wordmarks, `og-1200x630.png`, LinkedIn and Facebook covers and a quote-card template from your colours. Replace them with your own designs any time.

Commit and push:
```bash
git add -A && git commit -m "Set up for my niche" && git push
```

## 4. Turn on GitHub Actions

1. Repo → **Actions** → "I understand my workflows, go ahead and enable them".
2. Nothing else to switch on: each workflow asks for the permission it needs. (If an organisation policy blocks it and jobs fail to push, see [troubleshooting.md](troubleshooting.md).)
3. Actions → **Daily fuel scan** → **Run workflow**. The first run records everything it sees and reports the last 2 days.
4. Open `scanner/sources/SOURCES.md`: 🟢 working · 🟡 reachable but nothing found · 🔴 failed. Fix or remove 🔴 sources (see [troubleshooting.md](troubleshooting.md)).
5. Actions → **Weekly SEO audit** → **Run workflow** → read `seo-audit/reports/latest.md`.

From now on the scan runs daily and the audit weekly. To re-report the last few days once, create `scanner/sources/BACKFILL` containing a number (e.g. `3`) and push.

> If your site blocks bots (Cloudflare "Bot Fight Mode", a WAF), the audit may get 403s. Allow the user agent `ContentEngine-Audit` or run the audit from your own computer: `python3 seo-audit/audit.py`.

## 5. Search Console + GA4 (the analytics layer)

1. **Google Cloud project:** console.cloud.google.com → create a project → *APIs & Services → Library* → enable **Google Search Console API** and **Google Analytics Data API**.
2. **Service account:** *IAM & Admin → Service accounts → Create* (no roles needed) → open it → *Keys → Add key → JSON* → download. Copy its email (…@….iam.gserviceaccount.com).
3. **Give it read access:**
   - Search Console → your property → *Settings → Users and permissions → Add user* → the service account email → **Restricted**.
   - GA4 → *Admin → Property access management → +* → the email → **Viewer**. Note the **Property ID** (Admin → Property details; a number).
4. **GitHub** → Settings → *Secrets and variables → Actions*:
   - Secret `GOOGLE_SERVICE_ACCOUNT_JSON` = the whole JSON file contents
   - Variable `GSC_SITE_URL` = `sc-domain:example.com` (domain property) or `https://example.com/` (URL-prefix property) — exactly as Search Console shows it
   - Variable `GA4_PROPERTY_ID` = the number
5. Actions → **Daily search & analytics pull** → Run workflow → read `analytics/reports/latest.md`.
6. In GA4, mark your newsletter sign-up (or lead form) as a **key event** so the report shows which pages convert.

**Bing Webmaster Tools (recommended — Bing's index feeds Microsoft Copilot and ChatGPT search):**
1. bing.com/webmasters → add and verify your site (you can import it from Search Console in one click).
2. Settings (⚙️) → **API access** → **API key** → generate → copy.
3. GitHub: secret `BING_API_KEY`, variable `BING_SITE_URL` = your site exactly as listed in Bing (e.g. `https://example.com/`).
The next pull adds Bing clicks and impressions to the scorecard, Bing's top queries, and **Bing-only demand** — queries Bing shows you for that Google doesn't yet.

Either source can be left out; the job pulls what it can. **Never commit the JSON key** — `.gitignore` blocks the usual names.

## 6. Email the topic list (optional)

Gmail: turn on 2-step verification → myaccount.google.com/apppasswords → create an app password. Then in GitHub *Secrets and variables → Actions*:

| Name | Type | Value (Gmail) |
|---|---|---|
| `SMTP_HOST` | secret | `smtp.gmail.com` |
| `SMTP_PORT` | secret | `587` |
| `SMTP_USER` | secret | your Gmail address |
| `SMTP_PASS` | secret | the app password |
| `MAIL_FROM` | secret (optional) | sender address |
| `MAIL_TO` | variable | where to send it (comma-separate several) |
| `TOPIC_PAGE_URL` | variable (optional) | a published page of the topic list |

Run **Daily topic email** once to test. If the Claude topic-list task hasn't run that day, the email contains the scanner's top picks instead.

## 7. Claude

- **Claude Code:** open the repo folder; `CLAUDE.md` and `.claude/skills/` load automatically.
- **claude.ai:** connect GitHub and attach this repo to a project or session, or upload individual skill folders under **Customize → Skills**.
- **Daily topic list — pick one:**
  - **Claude scheduled task:** create one at your `cadence.times.topic_list` with the prompt in `.claude/skills/topic-list/SKILL.md` (it needs push access to your repo).
  - **Claude API workflow (no app needed):** add the secret `ANTHROPIC_API_KEY` (console.anthropic.com → API keys). The **Daily topic list (Claude API)** workflow then builds the list at the same time each day; it usually costs a few cents a day. Optional variables: `CLAUDE_MODEL`, `TOPIC_WEB_SEARCH=0` to turn off web search.
  Either way the list lands in `content/topic-lists/<date>.json` before the email goes out.

Try: "plan my week", "what should I write today?", "audit my site", "how is the site doing?", "are we cited in AI answers?", "review this draft".

## 8. Optional integrations

See [integrations.md](integrations.md): static-site publishing (Next.js, Astro, Hugo, Jekyll, Eleventy), Notion (Fuel Database), OpenSEO (backlinks, rankings, AI visibility, JS-rendered audits), WordPress (drafts and SEO-plugin checks), Canva (brand-kit visuals), Google Drive (drafts), a social scheduler, PageSpeed. After connecting one, set it to `true` under `integrations` in `engine.config.json` so the skills use it.

## 9. Your first week

1. Read the latest digest and `seo-audit/reports/latest.md`; fix anything critical first (blocked crawlers, broken pages, noindex on posts).
2. Ask Claude to **plan your week** (`weekly-plan`).
3. Write the first post with **blog-post**, then **blog-cascade** for the distribution set.
4. Each Monday, look at the analytics report's top actions and the audit's "Fix these first".

See [daily-cadence.md](daily-cadence.md) for a daily rhythm that fits around a job.
