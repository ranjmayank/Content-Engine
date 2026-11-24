# Daily rhythm

A rhythm that fits around a full-time job. Times are your local clock (`cadence.times` in `engine.config.json`); the defaults are below.

| When | What happens | Who |
|---|---|---|
| 07:45 | Search Console + GA4 pull → `analytics/reports/latest.md` | GitHub |
| 08:00 | News scan → `scanner/sources/digests/digest-<date>.md` | GitHub |
| 10:15 | Topic list → `content/topic-lists/<date>.{json,md,email.html}` | Claude scheduled task |
| 11:00 | Topic list emailed to you | GitHub |
| Monday 07:00 | SEO & AI-search audit → `seo-audit/reports/latest.md` | GitHub |

## The daily block (45–90 minutes, batch it)

1. **5 min — read the email.** Pick one topic. A "From your data" topic beats a news topic of the same strength.
2. **20–40 min — the post.** `blog-post` (Decode on most days, Deep on `deep_posts_per_week` days). Add your one line from work where it says `[YOUR LINE]`.
3. **10 min — the derivatives.** `news-fast-lane` or `blog-cascade`: Reel script, quote card, captions, LinkedIn post.
4. **10 min — publish and schedule.** Site first; LinkedIn in the morning with the link in the first comment; Instagram/Shorts via your scheduler.
5. **10 min — engage.** Reply to comments; comment on 5 posts from people in your niche.

## Weekly

- **Sunday (or your planning day):** `weekly-plan` — score the week's fuel, plan every slot, pick one adjustment.
- **Monday:** the audit's "Fix these first" and the analytics report's top 3 actions (a striking-distance update, a CTR fix, a refresh) before writing anything new.
- **Friday:** newsletter from the week's posts.

## When a day breaks

- No time: post the Reel and quote card from yesterday's post; skip the blog.
- No good news: write a "From your data" post or refresh a striking-distance page.
- Two weeks behind: drop to `deep_posts_per_week` only, and the weekly audit/analytics actions. Consistency beats volume.
