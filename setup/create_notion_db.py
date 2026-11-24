#!/usr/bin/env python3
"""Create the Content Fuel Database in Notion, with the columns the scanner writes to.

1. notion.so/profile/integrations → New integration (internal) → copy the secret.
2. Open (or create) the Notion page that should hold the database → ••• → Connections → add your integration.
3. Copy the page ID (the 32 characters at the end of the page URL).
4. NOTION_TOKEN=secret_xxx python3 setup/create_notion_db.py <page-id>
5. Put the printed database ID in the GitHub secret NOTION_DATABASE_ID, and the token in NOTION_TOKEN.

Columns: Idea (title) · Source (news/work/data/bank) · Territory (your pillars) · Link · Angle · Status (Raw → Scored → Scheduled → Published / Archived) · Score
"""
import json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLORS = ["blue", "green", "purple", "red", "pink", "orange", "yellow", "brown", "gray"]


def main():
    token = os.environ.get("NOTION_TOKEN")
    if not token or len(sys.argv) < 2:
        sys.exit(__doc__)
    page = sys.argv[1].split("-")[-1].split("?")[0]
    try:
        cfg = json.load(open(os.path.join(ROOT, "engine.config.json")))
    except FileNotFoundError:
        cfg = {}
    pillars = [p["name"] for p in cfg.get("niche", {}).get("pillars", [])] + ["News"]
    name = (cfg.get("brand", {}).get("name") or "Content") + " — Fuel Database"
    body = {
        "parent": {"type": "page_id", "page_id": page},
        "title": [{"type": "text", "text": {"content": name}}],
        "properties": {
            "Idea": {"title": {}},
            "Source": {"select": {"options": [{"name": n, "color": c} for n, c in
                                              zip(["news", "work", "data", "bank"], COLORS)]}},
            "Territory": {"select": {"options": [{"name": n[:100], "color": COLORS[i % len(COLORS)]} for i, n in enumerate(pillars)]}},
            "Link": {"url": {}},
            "Angle": {"rich_text": {}},
            "Status": {"select": {"options": [{"name": n, "color": c} for n, c in
                                              zip(["Raw", "Scored", "Scheduled", "Published", "Archived"], ["gray", "yellow", "blue", "green", "brown"])]}},
            "Score": {"number": {}},
        },
    }
    req = urllib.request.Request("https://api.notion.com/v1/databases", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Notion said {e.code}: {e.read().decode()[:300]}\n(Is the integration connected to that page?)")
    print("Created:", d.get("url"))
    print("NOTION_DATABASE_ID =", d["id"].replace("-", ""))


if __name__ == "__main__":
    main()
