# example.com — SEO & AI-search audit, 2026-11-24

**Score: 38/100 (F)** · 5 pages crawled · 4 URLs in the sitemap

## Who can read your site

- **Search engines:** Googlebot ✅ · Bingbot ✅
- **AI search & answers** (what gets you cited): OAI-SearchBot ✅ · ChatGPT-User ✅ · PerplexityBot ⛔ · Perplexity-User ✅ · Claude-SearchBot ✅ · Claude-User ✅ · DuckAssistBot ✅ · Applebot ✅
- **AI training** (optional to allow): GPTBot ⛔ · ClaudeBot ✅ · Google-Extended ✅ · CCBot ✅ · Applebot-Extended ✅ · Meta-ExternalAgent ✅ · Bytespider ✅
- **llms.txt:** — not found (optional) · **Sitemap:** http://demo-site.example/sitemap.xml

## Fix these first

1. **Site is not on HTTPS** (critical, site-wide) — Install an SSL certificate (free with Let's Encrypt or your host) and 301 all HTTP URLs to HTTPS.
2. **AI search crawlers are blocked** (critical, site-wide) — Allow the search/answer bots in robots.txt. You can keep blocking training-only bots (GPTBot, ClaudeBot, CCBot, Google-Extended) if you prefer.
3. **Broken internal link** (critical, 1 page(s)) — Update or remove the link on each linking page listed (see pages.csv), or redirect the dead URL.
4. **Thin content** (warning, 3 page(s)) — Expand the page with a direct answer, specifics and examples — or noindex/merge it if it has no search purpose.
5. **Missing meta description** (warning, 3 page(s)) — Write a specific 140–155 character description that answers why someone should click.

## Critical

### Site is not on HTTPS — site-wide

**Why it matters:** The site is served over plain HTTP.

**How to fix:** Install an SSL certificate (free with Let's Encrypt or your host) and 301 all HTTP URLs to HTTPS.


### AI search crawlers are blocked — site-wide

**Why it matters:** robots.txt blocks crawlers that power AI answers and AI search (for example OAI-SearchBot, PerplexityBot, Claude-SearchBot). The site can't be cited by those assistants.

**How to fix:** Allow the search/answer bots in robots.txt. You can keep blocking training-only bots (GPTBot, ClaudeBot, CCBot, Google-Extended) if you prefer.

- PerplexityBot

### Broken internal link — 1 page(s)

**Why it matters:** Your own pages link to a URL that returns an error. Visitors hit a dead end and crawlers waste budget.

**How to fix:** Update or remove the link on each linking page listed (see pages.csv), or redirect the dead URL.

- http://demo-site.example/ — → http://demo-site.example/missing.html (404)

## Warnings

### Thin content — 3 page(s)

**Why it matters:** Fewer than 150 words of readable text. Thin pages rarely rank and are rarely cited by AI answers.

**How to fix:** Expand the page with a direct answer, specifics and examples — or noindex/merge it if it has no search purpose.

- http://demo-site.example/ — 149 words
- http://demo-site.example/blog/orphan.html — 9 words
- http://demo-site.example/blog/post-a.html — 7 words

### Missing meta description — 3 page(s)

**Why it matters:** No meta description, so search engines pick a random snippet.

**How to fix:** Write a specific 140–155 character description that answers why someone should click.

- http://demo-site.example/blog/orphan.html
- http://demo-site.example/blog/post-a.html
- http://demo-site.example/blog/post-b.html

### No mobile viewport — 3 page(s)

**Why it matters:** No viewport meta tag, so the page may not render properly on phones (Google indexes the mobile version).

**How to fix:** Add <meta name="viewport" content="width=device-width, initial-scale=1"> in the theme head.

- http://demo-site.example/blog/orphan.html
- http://demo-site.example/blog/post-a.html
- http://demo-site.example/blog/post-b.html

### Images missing alt text — 1 page(s)

**Why it matters:** Images without alt text are invisible to screen readers and image search.

**How to fix:** Describe each meaningful image in a short alt text; use alt="" for decorative images.

- http://demo-site.example/ — 1 image(s)

### Links with no text — 1 page(s)

**Why it matters:** Links with no text, alt text or aria-label. Screen readers announce them as just 'link' and search engines get no context.

**How to fix:** Add descriptive text, or alt text on the linked image, or an aria-label for icon links.

- http://demo-site.example/ — 1 link(s): demo-site.example/blog/post-b.html

### Multiple H1 headings — 1 page(s)

**Why it matters:** The page has more than one H1, which blurs what it's about.

**How to fix:** Keep one H1; turn the others into H2s.

- http://demo-site.example/blog/post-a.html — 2 H1s

### Structured data doesn't parse — 1 page(s)

**Why it matters:** A JSON-LD block on the page is not valid JSON, so search engines ignore it.

**How to fix:** Validate it at validator.schema.org or Google's Rich Results Test and fix the syntax.

- http://demo-site.example/blog/post-a.html — 1 block(s)

### FAQ schema doesn't match the page — 1 page(s)

**Why it matters:** FAQPage schema includes questions that aren't visible on the page. Google's guidelines require marked-up content to be visible.

**How to fix:** Make the schema list exactly the questions and answers shown on the page, word for word.

- http://demo-site.example/blog/post-a.html — 1 of 1 questions not on the page: Is this question on the page?

### Invalid hreflang code — 1 page(s)

**Why it matters:** An hreflang value isn't a valid language(-region) code such as en, en-GB, hi-IN or x-default.

**How to fix:** Use ISO 639-1 language codes with optional ISO 3166-1 region codes (en-GB, not en-UK).

- http://demo-site.example/blog/post-a.html — en-UK

### Missing H1 heading — 1 page(s)

**Why it matters:** The page has no H1, the main on-page heading.

**How to fix:** Add one H1 that states what the page is about (usually the post title).

- http://demo-site.example/blog/post-b.html

### Page returns an error (4xx) — 1 page(s)

**Why it matters:** The URL returns a 4xx error (usually 404).

**How to fix:** If the page moved, 301-redirect it to the new URL. If it's gone, remove links to it and drop it from the sitemap.

- http://demo-site.example/missing.html — HTTP 404

### Sitemap lists URLs that can't be indexed — 1 page(s)

**Why it matters:** The sitemap includes URLs that redirect, error, are noindex or are canonicalized elsewhere. Sitemaps should list only pages you want indexed.

**How to fix:** Remove those URLs from the sitemap (in WordPress: your SEO plugin's sitemap settings).

- http://demo-site.example/blog/post-b.html — HTTP 200 · noindex · canonical elsewhere

### Orphan page — 1 page(s)

**Why it matters:** The page is in the sitemap but no crawled page links to it. Search engines treat unlinked pages as unimportant.

**How to fix:** Link to it from 2–3 related pages with descriptive anchor text.

- http://demo-site.example/blog/orphan.html

### hreflang without a return link — 1 page(s)

**Why it matters:** Page A lists page B as an alternate, but B doesn't list A. Search engines ignore one-way hreflang.

**How to fix:** Make every language version list all the others (and itself).

- http://demo-site.example/blog/post-a.html — hi → http://demo-site.example/blog/orphan.html doesn't link back

### Broken image — 1 page(s)

**Why it matters:** An image on the page returns an error.

**How to fix:** Re-upload the image or remove it from the page.

- http://demo-site.example/ — http://demo-site.example/x.png (404)

### Heavy images — 1 page(s)

**Why it matters:** Images over 300 KB slow the page, especially on phones.

**How to fix:** Resize to the display size and serve WebP or AVIF (an image-optimisation plugin or CDN does both).

- http://demo-site.example/ — heavy.jpg 390 KB

### Broken outbound link — 1 page(s)

**Why it matters:** A link to another site returns 404, 410, a server error, or the domain no longer exists. Dead citations hurt trust.

**How to fix:** Replace it with the source's new URL, an archived copy, or another source.

- http://demo-site.example/ — → http://old-source.example/gone-external.html (404)

## Notes

### AI training crawlers are blocked — site-wide

**Why it matters:** robots.txt blocks training-only crawlers. This is a business choice, not an error: it doesn't stop AI search citations.

**How to fix:** Keep it if you don't want your content used for model training.

- GPTBot

### No llms.txt — site-wide

**Why it matters:** There's no /llms.txt, the proposed file that gives AI tools a curated map of your best pages. It's optional and unofficial, but cheap to add.

**How to fix:** Create /llms.txt with a one-paragraph summary and links to your key pages (Rank Math and Yoast can generate it).


### Sitemap looks stale — site-wide

**Why it matters:** The newest lastmod in your sitemap is over 180 days old — either nothing was updated or the sitemap isn't regenerating.

**How to fix:** Check the sitemap regenerates when you publish (SEO plugin or build step), and that lastmod reflects real edits.

- newest lastmod 2024-01-01

### Missing Open Graph tags — 3 page(s)

**Why it matters:** No og:title or og:image, so links shared on LinkedIn, WhatsApp, X and Slack show a poor preview.

**How to fix:** Set og:title, og:description and og:image (your SEO plugin does this; use brand/og-1200x630.png as the default).

- http://demo-site.example/blog/orphan.html
- http://demo-site.example/blog/post-a.html
- http://demo-site.example/blog/post-b.html

### Images without width and height — 1 page(s)

**Why it matters:** Images with no width/height attributes make the page jump as they load (layout shift, a Core Web Vitals metric).

**How to fix:** Add width and height attributes (most CMSs do this automatically for images inserted through the editor).

- http://demo-site.example/ — 2 image(s)

### Generic link text — 1 page(s)

**Why it matters:** Links say 'click here', 'read more' or 'learn more'. Descriptive anchors tell readers and search engines what's behind the link.

**How to fix:** Rewrite the anchor to name the destination ("our pricing guide", "Google's March update notes").

- http://demo-site.example/ — 1 link(s)

### Heading levels skip — 1 page(s)

**Why it matters:** Headings jump a level (for example H2 straight to H4), which confuses screen readers and outline-based extraction.

**How to fix:** Use headings in order: H1 → H2 → H3.

- http://demo-site.example/blog/post-a.html — H1 → H4

### No language declared — 1 page(s)

**Why it matters:** The <html> tag has no lang attribute.

**How to fix:** Add lang="en" (or your language) to the <html> tag in the theme.

- http://demo-site.example/blog/post-a.html

### Article schema without dates — 1 page(s)

**Why it matters:** Article schema is present but has no datePublished or dateModified. Freshness is a strong signal for news and AI answers.

**How to fix:** Add datePublished and dateModified to the Article/BlogPosting schema (and show 'Last updated' on the page).

- http://demo-site.example/blog/post-a.html

### Article schema without an author — 1 page(s)

**Why it matters:** Article schema is present but names no author, which weakens E-E-A-T signals.

**How to fix:** Add author → Person (name, url, sameAs links) to the Article schema and show an author block on the page.

- http://demo-site.example/blog/post-a.html

### Page is noindex — 1 page(s)

**Why it matters:** A robots meta tag or X-Robots-Tag header tells search engines not to index the page.

**How to fix:** Fine for thank-you, login or tag pages. If the page should rank, remove the noindex.

- http://demo-site.example/blog/post-b.html

### Canonicalized to another URL — 1 page(s)

**Why it matters:** The page says another URL is the main version, so this one won't rank itself.

**How to fix:** Fine for duplicates and parameter URLs. If this page should rank, make the canonical self-referencing.

- http://demo-site.example/blog/post-b.html — http://demo-site.example/blog/post-a.html

### No structured data — 1 page(s)

**Why it matters:** The page has no JSON-LD schema. Schema helps search and AI systems understand what the page is and who wrote it.

**How to fix:** Add Article/BlogPosting (posts), Organization or Person (home/about), Product, FAQPage or BreadcrumbList as fits the page.

- http://demo-site.example/blog/orphan.html

---
_Built by seo-audit/audit.py (Content Engine). Issue set and thresholds adapted from OpenSEO (MIT). This checks the HTML your server returns (what most AI crawlers see); add --render to check JavaScript-rendered content. For backlinks, rankings and AI-visibility tracking, connect OpenSEO and use the `seo-audit` skill._