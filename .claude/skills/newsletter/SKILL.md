---
name: newsletter
description: Write the weekly newsletter from the week's posts and data — subject lines, preview text, a personal letter-style issue with sections and links, and the send checklist. Use when the user asks for the newsletter, weekly letter, email issue, or "turn this week's posts into a newsletter".
---

# Weekly newsletter

**First, read `engine.config.json`** (and write in `niche.language`, default English) (brand, author, voice, pillars, `brand.handles.newsletter`, `channels.newsletter`, `integrations`).

The newsletter is a letter from the author, not a digest of links. Readers subscribed for the author's judgement: what mattered this week, what to do about it, and one thing they wouldn't find elsewhere.

## Step 1 — Gather the week

- Posts published this week (`content/blog/`, `content/decode/`, or links from the user) — titles, the one idea in each, the URL
- The week's best news item (newest digests in `scanner/sources/digests/`)
- One real number from the site's data (`analytics/reports/latest.md`, with its window) or the audit — an "artifact" readers can't get elsewhere
- One work moment from the author (ask for a line, or leave `[YOUR LINE]`)

## Step 2 — Write the issue (350–600 words)

1. **Subject line** — 3 options, under 50 characters, the sharpest specific claim (no "Weekly update #12"). **Preview text** — the line that makes them open, under 90 characters.
2. **Opening (60–100 words)** — personal, in the moment: "This week I…". The week's one big idea.
3. **The change of the week** — the most important development in the pillars, what it means, one thing to do. Link the primary source.
4. **From the blog** — each post in 1–2 sentences with the one idea worth stealing, linked (with `?utm_source=newsletter&utm_medium=email&utm_campaign=<date>`).
5. **From my data** — the real number and the lesson (never invented; give the date window).
6. **One thing to try** — a concrete action for this week.
7. **Sign-off** — one line, the author's name, and a reply prompt ("Reply and tell me…" — replies improve deliverability).

Voice: `voice.description`. Never: `voice.banned_phrases`. Respect `author.confidential`.

## Step 3 — Send checklist

- [ ] Subject + preview text set; send a test to yourself (mobile and desktop)
- [ ] Every link works and carries UTM tags; the main CTA is above the fold
- [ ] Plain-text version reads cleanly
- [ ] Send time: the audience's weekday morning in `cadence.timezone` unless their data says otherwise
- [ ] After 48 hours: open rate, click rate, replies → note them in `tracker/weekly-tracker.csv`
- [ ] Publish the issue on the site as a web version if the platform supports it (more indexable content)

If a newsletter platform connector is available and marked in `integrations` (beehiiv, WordPress/Jetpack newsletters, etc.), offer to create the issue as a **draft** there. Never send or schedule without an explicit go-ahead.
