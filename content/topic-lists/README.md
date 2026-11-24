# Daily topic lists

1. The analytics job pulls Search Console + GA4 → `analytics/opportunities.json`.
2. The scanner collects new stories → `scanner/sources/digests/`.
3. A scheduled Claude task (the `topic-list` skill) groups the news into ranked topics in your pillars, adds 2–4 **"From your data"** topics, and saves `YYYY-MM-DD.json`; `tools/render_topics.py` makes `.md`, `.email.html` and `latest.html`.
4. The email job sends that day's `.email.html` (or the scanner's top picks if step 3 didn't run).

## JSON format

```json
{
  "date": "2026-01-15",
  "window": "Stories published 13–15 Jan 2026",
  "scanned": "42 new items from 31 sources; analytics through 12 Jan",
  "topics": [
    {
      "id": "t1",
      "category": "<a pillar name exactly, or From your data>",
      "priority": "Top pick",
      "format": "Decode post + Reel",
      "title": "The question this topic answers",
      "why": "Why it matters to the audience now",
      "data": "Optional: matching query — 340 impressions, position 11 (28 days to 12 Jan)",
      "facts": ["Dated, sourced fact (Publisher, 14 Jan)", "Another"],
      "angle": "The take only you can write",
      "refs": [["Publisher — headline", "https://…"]],
      "fanout": ["question people search", "another"]
    }
  ]
}
```
`priority`: Top pick · Strong · Good. Only real URLs you opened go in `refs`.
