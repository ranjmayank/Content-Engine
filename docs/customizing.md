# Customising for your niche

Everything niche-specific lives in four files. The code and skills read them; you never need to edit Python or skill files to change niche.

| File | Controls | Edit by |
|---|---|---|
| `engine.config.json` | Brand, author, pillars (names + what they cover), audience, region, out-of-scope, channels, handles, cadence and times, voice, banned phrases, CTAs, colours, hashtags, audit settings, integrations | `python3 setup/init.py` (re-run any time) or by hand |
| `scanner/sources/territories.json` | The keywords that tag a story or a search query with a pillar | By hand |
| `scanner/sources/sources.json` | The news sources | `setup/discover_feed.py` or by hand |
| `style.md` | Look and voice for visuals and reels, plus standing notes | By hand (the reel skill also updates it from your feedback) |

After changing `cadence.timezone` or `cadence.times`, run `python3 setup/schedule.py` to rewrite the workflow schedules.

## Pillars and keywords (territories.json)

```json
{
  "top_label": "stories in your pillars",
  "order": ["Pillar A", "Pillar B"],
  "keywords": {
    "Pillar A": ["keyword", "two words", "prefix"],
    "Pillar B": ["..."]
  },
  "topic_terms": ["words that mark a story as in your world at all"],
  "boost_terms": ["ai"]
}
```

- A keyword matches at the start of a word, so `"personaliz"` matches *personalize*, *personalization*. Add a trailing space (`"ads "`) to stop a short word matching inside longer ones.
- **Score** = number of pillars hit + 1 if any pillar is hit + 1 if a `boost_terms` word appears. Score ≥ 2 = a top pick (and goes to Notion). A story touching neither a pillar nor a `topic_terms` word is capped at 1.
- `boost_terms` defaults to AI words if you leave it out; set `[]` for a niche where AI isn't special.
- The analytics report maps search queries to pillars with the same keywords — "Unmapped" queries usually mean a keyword is missing.
- Tune it from the digest: if good stories land under "Everything else", add their words; if junk reaches "Top picks", make keywords more specific.

## Sources (sources.json)

```json
{"name": "Site Name", "category": "Pillar A", "why": "What it's for",
 "site": "https://site.com/", "type": "rss", "url": "https://site.com/feed/"}
```

| Field | Options |
|---|---|
| `type` | `rss` (RSS or Atom) · `sitemap` (for sites without a feed) · `auto` (just the site URL — the scanner finds the feed on its first run and saves it) · `manual` (listed in SOURCES.md to check by hand) |
| `include` | For sitemaps: only URLs containing this path, e.g. `"/blog/"` |
| `topic_only` | `true` for a general news site — keep only stories that hit a pillar or topic term |
| `ai_only` | `true` — keep only stories about AI |

Aim for 30–80 sources: a few primary sources (official blogs of the companies that shape your niche), the main trade publications, 5–10 independent experts, and communities to check by hand. Cut any source that produces no top pick in 30 days.

## Language and region

`niche.language` sets the language the skills write in (titles, posts, captions); the scanner and audit work for any language, but add pillar keywords in that language to `territories.json` so stories and queries are tagged. `niche.region` steers examples and regional sources: presets with region-specific sources (`"regional"` in the preset) ask whether to keep them.

## Adding a niche preset

Copy `setup/presets/blank.json` to `setup/presets/<name>.json`, fill in `label`, `summary`, `audience`, `pillars`, `out_of_scope`, `territories` and `hashtags`. Add `<name>.sources.json` (sites can be `"type": "auto"`), set `"sources_file"`, and list region-specific sources under `"regional": {"Country": [names]}`. Run the scanner for a week, check SOURCES.md, and send a pull request — tested source lists are the most useful contribution.

## Skills

The skills in `.claude/skills/` read `engine.config.json`, so they work for any niche as they are. To change how a skill writes (structure, lengths, checks), edit its `SKILL.md` — it's plain instructions. Put personal corrections you keep repeating in `style.md` → "Standing notes" or in `CLAUDE.md`, so every skill picks them up.

## Several brands from one repo

Keep one repo per brand (simplest), or add a second sources folder (`scanner/<brand2>/` with its own sources.json and territories.json) and a second `scan` call in the scan workflow (`python3 fuel_scanner.py --config <brand2> --title "..."`). The analytics and audit jobs are per site.
