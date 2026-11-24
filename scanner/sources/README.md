# Sources

The scanner's settings for your niche (written by `setup/init.py`):

| File | What it is |
|---|---|
| `sources.json` | The source list — add with `python3 setup/discover_feed.py <url> --add` or by hand (format in docs/customizing.md) |
| `territories.json` | Your pillars and the keywords that tag stories with them |
| `SOURCES.md` | Rewritten every run: each source, why it's there, and whether it worked |
| `digests/` | One digest a day: top picks first, each with a source card (summary, numbers, quote) |
| `fuel_inbox.csv` | Every item ever found, one row per link |
| `seen_urls.json`, `notion_pushed.json` | State (auto-managed) |

**Re-report the last few days once:** create a file here called `BACKFILL` containing a number of days (e.g. `3`) and push. The next run reports those days again and deletes the file.

**Three kinds of source:** feeds/sitemaps (scanned automatically) · general news sites with `topic_only` or `ai_only` (only matching stories kept) · `manual` (dashboards and paid sites, listed in SOURCES.md for you to open).
