# Launch checklist — profiles, site and the first 30 days

Do this once, in the first week. About 2–3 hours in total. Every profile should say the same thing in the same words: who you help, with what, and where to read more (your site).

## 1. Your positioning line (write it first)

> I help **[audience]** **[get outcome]** with **[your pillars / method]** — every week at **[site]**.

Use it, lightly adapted, everywhere below. Ask Claude: "Using engine.config.json, write my positioning line, LinkedIn headline, About section, Instagram bio and author block."

## 2. Website (30 min)

- [ ] Home page headline readable in 3 seconds: the positioning line
- [ ] About page with your photo, the work you do (anonymized where needed) and links (`brand.handles`) — this is your E-E-A-T page
- [ ] Author block under every post (the `author.bio` from the config) with a link to About
- [ ] Newsletter sign-up on posts and the home page; mark it as a GA4 key event
- [ ] Search Console and Bing Webmaster Tools verified; sitemap submitted to both
- [ ] robots.txt allows Googlebot, Bingbot and AI-search bots (OAI-SearchBot, ChatGPT-User, PerplexityBot, Claude-SearchBot) — check `seo-audit/reports/latest.md`
- [ ] Default Open Graph image (`brand/og-1200x630.png`); Article + Person + Organization schema
- [ ] Optional: `/llms.txt` with a summary and your best pages

## 3. LinkedIn (30 min)

- [ ] Headline: positioning line (under 220 characters), not just a job title
- [ ] About: 3 short paragraphs — the problem you write about, what readers get, the link
- [ ] Featured: your best post, the newsletter, the site
- [ ] Banner: `brand/cover-1584x396.png`
- [ ] Creator mode / follow button on if available; website link set to your site

## 4. Instagram (20 min) — if `channels.instagram`

- [ ] Profile photo: `brand/avatar-1000.png`; name field includes your main keyword ("Name | Topic")
- [ ] Bio: the positioning line in 150 characters + link to the site (or a link page that leads with the newsletter)
- [ ] 3 pinned posts: a "start here" carousel, your best Reel, an about-me Reel
- [ ] Professional account (for insights); connect Facebook if mirroring

## 5. Newsletter (15 min)

- [ ] Welcome email: who you are, what they'll get, how often, one best post
- [ ] Sender name = your name (people open emails from people)
- [ ] Web archive on the site if your platform allows

## 6. Medium (15 min) — if `channels.medium`

- [ ] Bio (160 characters) with the site link
- [ ] Import posts with **Import Story** so the canonical points to your site — never copy-paste

## 7. The daily 30 minutes that drive month-one growth

Content alone grows slowly at the start; conversation grows it faster.
- 10 comments a day on posts from people in your niche (specific, adds something, never "Great post!")
- Reply to every comment on your posts within the first hour
- 2–3 DMs a week to people you learn from — no pitch

## 8. First 30 days — what to measure

| Week | Watch | Decide |
|---|---|---|
| 1 | Does the scanner give you 3/3 topics daily? Is the audit score improving? | Cut 🔴 sources; fix critical audit items |
| 2 | Which pillar gets the most saves/comments on LinkedIn | Weight next week toward it |
| 3 | First Search Console impressions for new posts | Note target queries; check at day 7 and 28 |
| 4 | Newsletter sign-ups per post; AI referrals | Point CTAs at converting pages; run `ai-visibility` |

Log the numbers in `tracker/weekly-tracker.csv`; the `weekly-plan` skill reads it.

## 9. The part no system can do for you

Your judgement, your experience and your opinions. The engine finds the news and the data; the reason anyone follows you is the line only you could write. Add it every time the draft says `[YOUR LINE]`.
