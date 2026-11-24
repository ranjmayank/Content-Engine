# Every access, key and permission — what it's for and whether you need it

Nothing here is needed to start. With **zero** secrets you get the daily news digest, the weekly SEO & AI-search audit, the brand kit and every Claude skill. Add the rest when you want what they unlock.

**Where secrets go:** GitHub → your repo → **Settings → Secrets and variables → Actions**. *Secrets* are hidden after saving; *Variables* are visible. Never paste a secret into a chat, a file in the repo, a commit message or an issue.

| # | Access | Unlocks | Required? | Where you get it | Goes in |
|---|---|---|---|---|---|
| 1 | **GitHub repo + Actions** with *Read and write* workflow permissions | All automation (jobs commit reports back) | **Yes** | Settings → Actions → General | — |
| 2 | **Your website, readable by bots** (no WAF block for `ContentEngine-Audit`) | SEO audit | Yes for the audit | Your host / Cloudflare | — |
| 3 | `GOOGLE_SERVICE_ACCOUNT_JSON` | Search Console + GA4 pulls | Recommended | Google Cloud → service account key (SETUP step 5) | Secret |
| 4 | `GSC_SITE_URL` | Which Search Console property | With #3 | Search Console property name | Variable |
| 5 | `GA4_PROPERTY_ID` | Which GA4 property | With #3 | GA4 Admin → Property details | Variable |
| 6 | Service account added to **Search Console (Restricted)** and **GA4 (Viewer)** | Read-only data access | With #3 | Search Console users, GA4 property access | — |
| 7 | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` (+ `MAIL_FROM`) | Daily topic email | Optional | Gmail app password, or any SMTP provider | Secrets |
| 8 | `MAIL_TO`, `TOPIC_PAGE_URL` | Email recipient, link to the topic page | Optional | — | Variables |
| 9 | `NOTION_TOKEN`, `NOTION_DATABASE_ID` | Top picks into a Notion Fuel Database | Optional | notion.so/profile/integrations + `setup/create_notion_db.py` | Secrets |
| 10 | `NOTION_STATUS_TYPE` = `status` | Only if your Notion database uses the built-in Status type | Optional | — | Variable |
| 10b | `BING_API_KEY` + `BING_SITE_URL` | Bing Webmaster Tools data (Bing feeds Copilot and ChatGPT search) | Recommended | bing.com/webmasters → Settings → API access | Secret + Variable |
| 10c | `ANTHROPIC_API_KEY` (+ `CLAUDE_MODEL`, `TOPIC_WEB_SEARCH`) | Daily topic list built by the Claude API workflow | Optional | console.anthropic.com → API keys | Secret (+ Variables) |
| 11 | `PSI_API_KEY` | Core Web Vitals in the weekly audit | Optional | Google Cloud → enable PageSpeed Insights API → API key | Secret |
| 12 | `AUDIT_MAX_PAGES` | Bigger/smaller weekly crawl (default 200) | Optional | — | Variable |
| 13 | **Claude** (claude.ai plan or Claude Code) | The skills; the daily topic-list task | For writing | claude.ai | — |
| 14 | Claude **GitHub connection** with push access to your repo | Scheduled topic list, Claude committing drafts | For the topic list | claude.ai → Settings → Connectors / Claude Code login | — |
| 15 | Claude connectors (OpenSEO, WordPress, Notion, Canva, Google Drive, a scheduler) | Live data, drafts, visuals, scheduling | Optional | claude.ai → Settings → Connectors | `integrations` in engine.config.json |

## What each piece can and can't do

- The **service account** gets read-only access you grant per property. Remove it from Search Console / GA4 to revoke.
- The **Bing API key** reads your Webmaster Tools data; regenerate it in Bing to revoke.
- The **Claude API key** is billed to your Anthropic account; set a monthly spend limit in the console.
- **GitHub Actions** writes only to your repo, using the built-in `GITHUB_TOKEN`.
- **Claude skills** never publish, schedule, send or change site settings without your explicit go-ahead. Connectors are used only when you've marked them in `integrations`.
- The **scanner** and **audit** fetch public pages only. The audit respects your robots.txt for its own user agent and waits `seo_audit.delay` seconds between requests.

## If a secret leaks

Revoke it first (delete the service-account key in Google Cloud, regenerate the app password, revoke the Notion integration), then add the new one in GitHub. Deleting a commit does not make a leaked key safe.
