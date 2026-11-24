---
name: reel
description: Turn a blog post link into a finished vertical reel — story format, Hook → Lock-in → Body → Rehook → CTA script, a "Comment KEYWORD" call to action with the DM to send, then voice, word-timed captions and motion graphics in code (Remotion) or a production sheet. Use when the user types /reel, shares a blog link for a reel, or asks for a reel, short or animated explainer.
---

# Make a reel from a blog post

**First, read `engine.config.json`** (and write in `niche.language`, default English) — `brand`, `author`, `niche.pillars`, `niche.audience`, `voice`, `hashtags`, `channels`, and `author.confidential`. Wherever this skill says *the author*, *the site* or *the pillars*, use those values. If the file is missing, run the `engine-setup` skill first.

**In:** a link to one of the author's blog posts (the site or Medium), plus any notes.
**Out:** an approved script, the comment-to-DM CTA kit, and — if the video setup exists in this folder — a finished video at `reels/<short-name>/<short-name>.mp4`.

Read `style.md` first, every time (colours, font, voice, motion limits, standing notes). If it doesn't exist, use the brand defaults at the bottom of this file and say so.

the author approves **three** things, in order: the **angle**, the **script**, and the **storyboard**. Never skip one.

**Model check.** Reels come out best on the strongest available model at high effort. If you're not sure that's what's running, say how to switch and ask whether to switch first.

## Rules that always apply

- **Built from the blog and its sources.** Every fact in the reel comes from the blog post or a source it links, with the date. Never invent a number, result or quote — not even as an example.
- **One reel, one detail.** A blog post can feed several reels; each covers a different detail (the news, the surprising number, the risk, the how-to, the regional angle).
- **Their voice:** strategic but practical, plain words, confident, no hype. Not influencer-style — no "game-changer", "mind-blowing", "you won't believe", "let that sink in".
- **Confidentiality:** respect everything in `author.confidential`.
- **Who it's for:** `niche.audience`. Explain any technical term in 3–4 words or drop it.

## Step 1 — Read the blog and write the reel brief

Fetch the link and read the whole post (and open the sources it cites for the numbers you plan to use). If the page can't be opened, ask them to paste the text.

Write a short **reel brief**:

| Field | What to write |
|---|---|
| Promise | The one thing a viewer will know or be able to do after watching |
| Pain | The viewer's problem this solves, in their words |
| Non-obvious insights | 2–4 points from the post that would surprise the audience — these become body blocks. Each with its source and date |
| Contrarian take | The common belief this post goes against, if any |
| Proof assets | Screenshots, numbers, charts, before/after they can show (strongest when it's their own) |
| Magic-box term | A named method, framework or term from the post the viewer would want to learn  |
| DM deliverable | What the viewer gets by commenting: the blog link, plus a checklist / template / framework if the post has one |
| Keyword | One word for the CTA (rules in Step 4) |

## Step 2 — Propose angles and pick the format (wait for approval)

Offer **2–3 reel angles** from the brief. Each = one detail + one story format + the hook line. Mark one as recommended. Wait for their pick.

### The 10 story formats — and when to use each for their content

All are told first-person. The first four fit blog-to-reel best.

| # | Format | Use it when the blog… | Beats | What makes it work |
|---|---|---|---|---|
| 1 | **Personal learning / epiphany** | teaches a lesson they learned or a result they got | Hook with the result or bold claim → brief backstory (old belief) → the insight → the 3-step breakdown → CTA | Visible proof (screenshot) up front, and a non-obvious method — or viewers write it off as luck |
| 2 | **Lesson from others** | decodes news about a company or person (a named company or person) | Hook naming who and the lesson → their situation, vivid → the lesson (a direct quote or specific moment) → how it applies to the viewer → CTA | He's the curator, not the hero. Name the company/person, use the exact quote or number |
| 3 | **Hero's journey (problem → solution)** | is a how-to that solves a common problem | Hook → them + the problem → failed attempts (what everyone tries) → the different solution → why it worked + result → CTA | The viewer has to feel the pain they felt; then they want the solution |
| 4 | **Before and after** | shows a transformation (a workflow, a page, a metric, AI visibility) | Hook teasing the change → the before (relatable) → a short build → the reveal on a beat → time/effort it took → CTA | The bigger and more visual the gap, the better. 15–30 seconds; it doesn't need explaining |
| 5 | **Challenge** | is an experiment they ran ("I tested X for 7 days") | Hook with challenge + stakes → rules and starting point → the journey with setbacks → result or cliffhanger | A big enough goal and real complications |
| 6 | **Win** | announces a result (a milestone, a launch, a ranking) | The win immediately → proof → what it means → nod to the effort → CTA | Undeniable, visual proof; short and raw |
| 7 | **Goal / dream journey** | is about building in public (e.g. growing the account) | The goal and why → when they started → progress so far → what's next → "follow to see if I pull this off" | Ambitious enough that people wonder if he'll make it; honest about doubts |
| 8 | **About me (origin story)** | — use for one pinned profile reel | Normal life → the trigger event → the realisation → what they did → their mission now | Builds trust, not expertise. Pin it |
| 9 | **Day in the life** | shows how they actually works (the author's real working day) | Who + context → a complication → how they solved it → wrap | Something unexpected about how they works |
| 10 | **Personal update** | shares a change in their work or brand | Tease → context → the update → why | Community-building, not authority |

## Step 3 — Write the script (wait for approval)

### Structure

| Beat | Sentences | Job |
|---|---|---|
| **Hook** | 1–2 | Make the viewer opt in to this topic |
| **Lock-in** | 2–4 | Convince them the rest is worth watching |
| **Body block 1** | 3–5 | A non-obvious point, then 2–4 lines of facts, examples or reasons that support it |
| **Rehook** | 1 | Reset attention and open the next loop |
| **Body block 2** | 3–5 | A second non-obvious point (at least one body block is contrarian) |
| **Rehook 2 + Body block 3** | optional | Only if the blog has a third genuinely strong point |
| **Closing** | 0 | Skip it — every reel ends on the CTA instead |
| **CTA** | 1 | Comment KEYWORD for the DM (Step 4) |

Fit the format's beats from Step 2 into this structure (for example, in "Lesson from others", the hook names the company, the lock-in teases the lesson, the body blocks are the situation and the lesson, the CTA offers the breakdown).

**Length — as short as the idea allows:**
- **Short** (news, one point): Hook + Lock-in + 1 body block + CTA — 70–110 words, 25–40 seconds
- **Standard** (default): 2 body blocks + 1 rehook — 120–170 words, 45–65 seconds
- **Long** (only with three strong points): 3 body blocks + 2 rehooks — up to ~210 words, about 80 seconds

### The hook — the four S's

1. **Subject:** the topic is clear in the first sentence.
2. **Stakes:** a reason this viewer feels they must keep watching.
3. **Simple:** very simple words.
4. **Superclear:** a short, punchy sentence that's easy to follow.

Write the hook as three layers that land together in the first 1–2 seconds:
- **Spoken hook:** the first line of the script.
- **Text hook:** on screen from frame one, 8 words or fewer, readable in under a second.
- **Visual hook:** what's moving in frame one — the real headline, a big number counting up, a screenshot being stamped, a split screen. Never a logo or a title card.

Give **two alternative hooks** (spoken + text + visual) so they can test them.

### The lock-in — pick one or two tactics

The viewer should leave this beat thinking "I have to keep listening."
- **Tease proof:** the result that came from what's about to be explained (the real result, sourced).
- **Tease the transformation:** the before → after the viewer will get.
- **Clarifying contrast:** why this is different from the common advice ("Everyone says publish more. The data says the opposite.").
- **Magic box:** name the method or term they'll want to know (name the method from the post).
- **Handle the objection:** dismiss the reason they'd scroll away ("You don't need a developer for this").
- **Double down:** make the hook's claim stronger.

### Body blocks

Each one opens with a frame the viewer doesn't expect, then 2–4 sentences that prove it (the sourced number, the example, the reason). Two body blocks = two "huh, I didn't know that" moments — that's what earns the follow.

### Rehooks

Attention resets around every 20–25 seconds. One sentence between body blocks that creates contrast with what came before and opens a new question:
- "That's the part everyone knows. The part nobody talks about is worse."
- "But the number that should worry you is the second one."
- "So that's the problem. Here's what's actually working."

Make it flow from the previous line — a forced rehook sounds corny.

### Writing principles

- Cut every word that doesn't carry meaning.
- Each sentence connects to the one before, or clearly starts a new thought — no jumps.
- Tease the value as early as possible.
- Simple words, complete sentences a person would say out loud.
- One idea per sentence — in the video, each sentence becomes one picture.
- Specific, true, sourced numbers. End on the CTA, not a summary.

Show the script with the beats labelled, the word count and the estimated length. Wait for approval; change it when they ask.

## Step 4 — The CTA and the DM kit

Every reel ends with one spoken sentence asking viewers to comment a keyword, and the author sends them the blog and the extra material by DM. The CTA is the measure of whether the reel worked.

### Choosing the keyword

- One word, uppercase in text, tied to the topic: AUDIT, CHECKLIST, TEMPLATE, PLAN, GUIDE.
- Easy to spell on a phone; no numbers or symbols.
- Not a word people would comment anyway (avoid YES, AI, WOW, NICE) — otherwise the count means nothing.
- A different keyword for each reel, so each reel's results can be counted separately.

### Wording

Say what they get, then the keyword:
- "Comment AUDIT and I'll send you the full checklist."
- "Want the step-by-step? Comment AGENT and I'll DM it to you."
- "I wrote the whole breakdown, with every source. Comment AUDIT and it's yours."

Never promise something the DM doesn't deliver.

### Where the CTA appears

1. **Spoken:** the last sentence of the script.
2. **On screen:** the keyword big in the accent colour for the final 3–4 seconds, inside the safe area.
3. **Caption:** repeated in the first two lines of the caption and again at the end.
4. **Pinned comment:** "Comment KEYWORD below and I'll DM you [the deliverable]."

### The DM message (write it for the author)

```
Hey [name], thanks for commenting! Here's [the deliverable]:
[blog link with ?utm_source=instagram&utm_medium=dm&utm_campaign=<reel-short-name>]

[One line on what to look at first — the most useful section or step]

Quick question: [one easy question about their situation, to start a conversation]
```

Keep it short, friendly and useful. No hard pitch.

### Delivering the DMs

- **Automatic:** set up a keyword → DM automation. Options: a comment automation in a connected scheduler (if `integrations` lists one — ask before creating it), ManyChat, or Instagram's own tools if available on their account. Check that the automation tool currently supports Instagram comment-to-DM before recommending it.
- **Manual:** reply to each comment ("Sent! Check your DMs") and send the message. Fine at the start; switch to automatic once a reel gets more than ~30 comments.
- Instagram only allows replying privately to recent comments, so send DMs within a day or two.

### Tracking

Note for each reel: keyword, comments with the keyword, DMs sent, clicks on the UTM link (from site analytics). Comments ÷ views is the reel's conversion rate.

## Step 5 — Produce the video

### If the video setup isn't in this folder yet (script-only mode)

Hand over a production sheet instead of a render:

| Time | Scene (one per sentence) | On-screen text (≤8 words) | Voiceover | Motion / visual | Sound |
|---|---|---|---|---|---|

Plus: the cover frame (readable at thumbnail size), B-roll or screenshot list (with where each comes from), and a note that the full pipeline can be set up with Remotion when they want it.

### If the setup exists (Remotion in this folder)

1. **Voice.** Use the voice in `style.md` and save the audio and the start and end time of every word.
   - **Free local voice (Kokoro):** speak the script a sentence at a time with natural pauses, into one audio file; get the word times from that audio with Remotion's Whisper tooling. The script is the truth — keep its words and spelling and take only the times from Whisper.
   - **ElevenLabs:** one request for the whole script using the "with timestamps" endpoint and the key in `.env`; work out each word's start and end from the character times.
   - **No voice:** time the words at a natural reading speed.
2. **Plan.** Write `plan.md`: one scene per sentence, with its words, its start and end, its story beat (hook, lock-in, body, rehook, CTA), and what's on screen. Check it against "Make it look good" before drawing anything.
3. **Storyboard.** Draw each scene as one still at its fullest moment, all on one sheet, numbered, with the words under each. Show it and wait for approval; redraw the scenes they want changed.
4. **Build.** Animate each approved scene in Remotion, following Remotion's agent skills. Every movement is calculated from the current frame (no CSS animations or transitions — they flicker in renders). Each change on screen lands on the word it belongs to. Rehooks get a visible change (a cut, a new layout) to reset attention.
5. **Captions.** Each word appears as it's spoken, and the spoken word is highlighted. In English, 2–5 words a line; in other languages, break lines the way that language reads best.
6. **Sound.** A few small effects on the moments that land (the reveal, the number, the keyword), made in code. The voice is always the loudest thing.
7. **Render** to MP4, 1080 × 1920, 30 frames a second.
8. **Check your own work — measure first, then look:**
   - **Dead spots:** take a frame every half second and compare each with the one before. A stretch where almost nothing changes for longer than `style.md` allows is a dead spot.
   - **Too busy:** more things moving at once than `style.md` allows, or most of the picture changing without a scene change.
   - **Reading:** put those frames on one sheet with their times and look for text that's blurred, cut off, too small for a phone, or inside the areas Instagram covers.
   - **Sound:** every line plays to the end — compare the audio length with the last word's time.
   - **Hook:** the first frame shows the text hook and something is moving.
   - **CTA:** the keyword is on screen, readable, for the last 3–4 seconds.
   - Fix what fails and render again, three rounds at most. Say what was measured, what failed and what changed.

### Make it look good

- Show the idea as a drawing: a diagram, a chart, an object, a small machine at work. Few words on screen.
- One focus at a time. Change what's already there (grow it, fill it, break it) before replacing it.
- The picture changes with every sentence, always with motion. Nothing sits still while the voice moves on.
- Moves are short and land with weight: things arrive fast and settle. No slow fades, spinning or drifting.
- Numbers count up. Lines draw themselves. When the words are about an app or a website, draw its screen and make it move.
- One font, the `style.md` colours, the accent only on what matters. No gradients, glows, emoji or stock icons.
- Keep everything that must be read out of the top 220 px, the bottom 420 px and the right 140 px (Instagram covers them).
- Everything reads on a phone. If a frame could belong to any video, make it belong to this one.

## Step 6 — Caption and hand over

**Caption:**
- First line (about 125 characters show before "more"): the hook + "Comment KEYWORD for [deliverable]".
- 2–3 short lines of context in plain words.
- "Sources: [who], [date]."
- CTA again.
- 3–5 hashtags, specific first.

**Hand over:**
- The video file path (or the production sheet), the caption, the pinned comment, the DM message, the keyword, and the automation to set up.
- One thing you'd improve next time.

## Self-check before showing the script

| Check | Pass? |
|---|---|
| Built from the blog; every fact sourced and dated; nothing invented | |
| Format fits the content (table in Step 2) | |
| Hook passes all four S's; text, spoken and visual hooks land in 1–2 seconds | |
| Lock-in uses at least one tactic and makes the viewer want the rest | |
| At least two non-obvious body blocks (one contrarian), unless it's a Short | |
| Rehook between body blocks flows naturally | |
| One idea per sentence; no jumps in logic; simple words | |
| Length fits the type (Short / Standard / Long) | |
| CTA: one sentence, topic keyword, says what they get; DM kit ready | |
| No confidential employer details | |

## When they give feedback

- A specific change ("make the hook bigger") — change only that and render again.
- A feeling ("calmer", "more going on", "bigger text") — change the reel, then update the numbers and rules in `style.md` so the next reel starts from their taste. Tell them what changed.
- Anything about scripts or storytelling — add it to "Standing notes" in `style.md` and apply it on every reel from then on.

## Brand defaults (when `style.md` is missing)

- Colours from `engine.config.json` → `colors` (ink background, paper text, accent) · Font: Outfit
- Motion limits: nothing still for more than 1 second; no more than 2 things moving at once
- Voice: not chosen yet — ask, and offer the free local voice to start
