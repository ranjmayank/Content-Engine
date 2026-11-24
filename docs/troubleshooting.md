# Troubleshooting

## Workflows

| Symptom | Fix |
|---|---|
| Jobs say "Not set up yet" | Run `python3 setup/init.py`, then commit and push `engine.config.json`. |
| Not sure what's set up or what to do next | **Actions → 2 · Check my setup → Run workflow**, then open the run's **Summary**. |
| **1 · Set up my engine** fails at "Write your settings" | Usually a typo: check the website address (e.g. `mysite.com`) and pick a niche from the list. Run the form again — it's safe to repeat. |
| **1 · Set up my engine** isn't in the Actions list | You're in the original repo, not your copy — open your own repo (your username in the address). Or Actions isn't enabled yet: click the green "I understand my workflows…" button. |
| The first scan/audit didn't start after setup | Start them by hand: **Actions → Daily fuel scan → Run workflow**, then **Weekly SEO audit**. |
| `git push` fails in a job (403) | Your organisation restricts workflow permissions. Settings → Actions → General → Workflow permissions → **Read and write** (or ask an org admin). |
| "Service account key creation is disabled" (Google Cloud) | A company Google Workspace policy. Create the project with a personal Google account, or ask your admin. |
| Scheduled jobs don't run | Enable Actions (Actions tab). GitHub pauses schedules in public repos with no activity for 60 days — push any commit or run a workflow by hand to wake them. |
| Jobs run at the wrong time | `python3 setup/schedule.py` after changing `cadence`. GitHub can start scheduled jobs late at busy times. In daylight-saving zones the time shifts an hour in summer. |
| Analytics job is skipped | `GOOGLE_SERVICE_ACCOUNT_JSON` isn't set. |
| Email job is skipped | `SMTP_HOST` secret or `MAIL_TO` variable isn't set. |

## Scanner (SOURCES.md)

| Status | Meaning | Fix |
|---|---|---|
| 🔴 HTTPError 403 | The site blocks bots | Use its sitemap instead, or set `"type": "manual"` |
| 🔴 HTTPError 404 | Feed moved | `python3 setup/discover_feed.py <site>` to find the new one |
| 🔴 ParseError | The feed isn't valid XML | The scanner already repairs small errors; try the sitemap |
| 🟡 reachable, nothing found | Wrong feed, or `include` filter too strict | Open the URL; adjust `include` |
| 🟢 working, no matching stories | Nothing in your pillars right now | Fine; cut it if this lasts 30 days |

Good stories landing under "Everything else"? Add their words to `territories.json`. Junk in "Top picks"? Make keywords more specific (see [customizing.md](customizing.md)).

## Analytics

- **403 from Search Console:** the service account isn't a user on that property, or `GSC_SITE_URL` doesn't exactly match (`sc-domain:example.com` vs `https://example.com/`).
- **403 from GA4:** add the service account as Viewer on the *property* (not just the account), and check `GA4_PROPERTY_ID` is the numeric property ID.
- **Empty lists:** new or small sites have little data; lower the thresholds at the top of `analytics/analyze.py`.
- **Sessions look doubled:** your analytics tag loads twice (common when two plugins both add GA4/GTM). Fix the site before trusting GA4 numbers.

## SEO audit

- **Lots of `blocked-page` (403/503):** your firewall or bot protection is blocking the crawler. Allow the user agent `ContentEngine-Audit`, or run the audit locally. If real search/AI bots are also blocked, that's a bigger problem than the audit.
- **`javascript-rendering-suspected`:** your content is rendered in the browser. The audit (like many AI crawlers) sees an empty page. Use server-side rendering, or use OpenSEO with JavaScript rendering for the audit.
- **Crawl stopped at the page limit:** raise `seo_audit.max_pages` or the `AUDIT_MAX_PAGES` variable. Exclude tag/author/pagination URLs with `seo_audit.exclude`.
- **Score feels harsh/lenient:** each issue type takes at most a fixed amount (critical 8, warning 3, info 1, scaled by the share of pages affected). Change `SEVERITY_WEIGHT` or `THRESHOLDS` in `seo-audit/issues.py`.

## Claude

- **Skills don't appear:** in Claude Code they load from `.claude/skills/` in the opened folder; in claude.ai upload the skill folder under Customize → Skills or attach the repo.
- **Claude says the config is missing:** run setup, or say "set up the engine".
- **Topic list wasn't built:** the scheduled task needs push access to the repo. The email falls back to the scanner's top picks.
