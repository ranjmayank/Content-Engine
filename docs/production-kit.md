# Production kit

Templates for turning one post into visuals and video quickly and consistently. Colours, fonts and voice come from `engine.config.json` and `style.md`; the starter assets come from `python3 brand/scripts/make_brand.py`.

## 1. The weekly flow

1. **Write once:** the post (`blog-post`) — the most complete, best-sourced version.
2. **Derive:** `blog-cascade` (deep posts) or `news-fast-lane` (news) writes every other asset.
3. **Produce in batches:** carousels and quote cards in one sitting, Reels in another. Batching cuts the time per asset by more than half.
4. **Review:** `content-feedback` on anything going out under your name.
5. **Publish site-first,** then social, then Medium and the newsletter.

## 2. Brand kit — fill these in once

| Item | Where it lives | Notes |
|---|---|---|
| Colours | `engine.config.json` → `colors` | Ink (text, dark backgrounds), one accent (one highlight per frame), paper (light backgrounds) |
| Fonts | `brand/scripts/fonts/` | Outfit for headlines, Geist Mono for captions and accents (SIL OFL). Swap for yours if you have them |
| Logo / avatar | `brand/avatar-1000.png`, wordmarks | Replace with your own design when you have one |
| Link preview | `brand/og-1200x630.png` | Default Open Graph image for posts without their own |
| Covers | `brand/cover-1584x396.png` (LinkedIn), `cover-1640x624.png` (Facebook) | |
| Voice | `engine.config.json` → `voice` | Plus `style.md` → "Standing notes" for corrections you keep repeating |
| Video voice | `style.md` | Pick one TTS voice and never change it — voice consistency is brand |

## 3. Carousel template (LinkedIn PDF + Instagram, 1080×1350)

```
Slide 1 — HOOK: 6–10 words, big type, accent on one key word. No brand name.
Slide 2 — THE PROBLEM: one stat (sourced) or one vivid scenario.
Slide 3 — WHY IT'S WORSE THAN YOU THINK: the hidden cost.
Slide 4 — THE SHIFT: the one-line reframe — your point of view.
Slide 5 — THE FRAMEWORK: 3–4 numbered steps, verbs first, ≤8 words each.
Slide 6 — PROOF: a concrete before/after or a real observation.
Slide 7 — THIS WEEK: one action.
Slide 8 — CTA: "Full playbook → [your site]" + avatar + handle.
```
Rules: ≤20 words a slide (slide 1 ≤10) · a source footer on any slide with a number ("Source: [who], [month year]") · no emojis, no "swipe for more" · one accent per slide.

**Design:** build one master in Canva (or Figma) from the brand kit, then duplicate for each carousel. With the Canva connector, Claude can fill the template for you. Export PNGs for Instagram and a PDF for LinkedIn.

## 4. Quote card (1080×1350)

One sentence under 20 words; 2–4 words in the accent colour. Quick version: `python3 brand/scripts/make_brand.py --quote "Your line"` → `brand/quote-card-1080x1350.png`.

## 5. Faceless Reel / Short (30–45 s)

```
0–2s   HOOK: the sharpest claim (on screen + voiceover). No intro.
2–8s   AGITATE: why it costs the viewer something real
8–30s  THE MEAT: 3 points, one text card each (≤8 words a card)
30–40s PAYOFF: the one-line takeaway
40–45s CTA: "Comment KEYWORD and I'll send the full breakdown" or "link in bio"
```
**Chain:** script (`reel` or `news-fast-lane`) → voice (one TTS voice, or the free local Kokoro voice) → a CapCut-style template with auto-captions in your fonts and colours, **or** the `reel` skill's Remotion pipeline for motion graphics in code → export 1080×1920. Same file works for Instagram Reels, YouTube Shorts and TikTok.

Keep text out of the top 220 px, bottom 420 px and right 140 px (platform UI covers them).

## 6. Selfie video (LinkedIn, 30–45 s, 10 minutes)

```
Beat 1 (0–5s)   The claim — start mid-thought.
Beat 2 (5–20s)  Why — one reason, one example from your work (anonymized).
Beat 3 (20–35s) The reframe, or the one question to ask.
Beat 4 (35–45s) "I wrote the full breakdown — link in the comments."
```
Phone front camera, natural light, 2–3 takes, auto-captions. Imperfect reads human next to polished AI content.

## 7. Featured images

Decide one rule for the site and keep it (put it in `CLAUDE.md`): e.g. text-free illustrations if your theme overlays the title, or a branded title card from the OG template. Always write descriptive alt text. Don't use photos of real people you don't have rights to.

## 8. Minimum tool stack

| Job | Free / cheap option | Upgrade |
|---|---|---|
| Writing | Claude + these skills | — |
| Design | Canva free + brand kit | Canva Pro (brand kit, bulk create) |
| Voice | Kokoro (local, free) | ElevenLabs |
| Video | CapCut | Remotion (code, via the `reel` skill) |
| Scheduling | Native schedulers (LinkedIn, Meta Business Suite) | A scheduler with a Claude connector |
| SEO data | This engine (Search Console, GA4, Bing, audit) | OpenSEO for backlinks, rankings, AI visibility |
