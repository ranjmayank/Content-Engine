# Changelog

Notable changes. Your settings (`engine.config.json`, `scanner/sources/`) are never touched by an update — see [docs/UPDATING.md](docs/UPDATING.md).

## 1.1.1 — 2026-11-24
- **Audit, from the first live-site run:** no longer crawls share/nofollow/action links (`?share=`, `?replytocom=`…); redirect chains that leave the site aren't flagged; a page reached through a redirect is checked once (fixes false duplicate title/content); LinkedIn's 999 and other non-HTTP codes aren't reported as broken links; empty-link findings show which links; PageSpeed errors explain the missing key.

## 1.1.0 — 2026-11-24
- **Audit:** hreflang, broken outbound links (`--external`), heavy/unsized images, sitemap freshness and size, weak anchor text, FAQ schema that doesn't match the page, optional JavaScript rendering (`--render`).
- **Analytics:** Bing Webmaster Tools (queries and pages; Bing feeds Copilot and ChatGPT search).
- **Topic list without Claude scheduling:** optional GitHub Action using the Claude API (`ANTHROPIC_API_KEY`).
- **New skills:** `content-feedback` (pre-publish review), `newsletter`, `x-thread`, `ai-visibility`.
- **Publishing:** static-site export (Markdown + front matter for Next.js, Astro, Hugo, Jekyll, Eleventy).
- **Setup:** content language, regional sources made optional, `"type": "auto"` sources (feed found on the first run) and starter source lists for every preset.
- **Docs:** production kit, launch checklist, updating guide, Windows notes; examples with screenshots.
- **Repo:** tests on every push and pull request, issue and PR templates, security policy, code of conduct.

## 1.0.0 — 2026-11-24
- First public release: news scanner, Search Console + GA4 analytics, weekly SEO & AI-search audit, topic list and email, 11 Claude skills, setup wizard with 10 presets, brand kit.
