#!/usr/bin/env python3
"""Build today's topic list with the Claude API — the no-Claude-app alternative to the scheduled task.

Reads engine.config.json, the newest scanner digest and analytics/opportunities.json, asks Claude for the
ranked list in the format of content/topic-lists/README.md, validates it, saves
content/topic-lists/<today>.json and renders the markdown, email and page.

  ANTHROPIC_API_KEY=sk-ant-... python3 tools/build_topic_list.py
Options (environment): CLAUDE_MODEL (default claude-sonnet-5-5) · TOPIC_WEB_SEARCH=0 to turn off web search ·
  TOPIC_WEB_SEARCH_TOOL (the API's web search tool type, default web_search_20250305)

Cost: one request with a digest of ~10–40k tokens plus a few searches — usually a few cents a day.
Every fact must come from the digest or a page Claude actually opened; facts it can't source are dropped.
"""
import glob
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_config as EC  # noqa: E402

ROOT = EC.ROOT
LISTS = os.path.join(ROOT, "content", "topic-lists")
API = "https://api.anthropic.com/v1/messages"


def read(path, limit=None):
    try:
        t = open(path).read()
    except FileNotFoundError:
        return ""
    return t[:limit] if limit else t


def recent_titles(n=3):
    out = []
    for f in sorted(glob.glob(os.path.join(LISTS, "20*.json")))[-n:]:
        try:
            out += [t["title"] for t in json.load(open(f)).get("topics", [])]
        except Exception:
            pass
    return out


def opportunities_summary():
    try:
        o = json.load(open(os.path.join(ROOT, "analytics", "opportunities.json")))
    except Exception:
        return "No analytics data yet."
    keep = {k: o.get(k) for k in ("window", "scorecard", "striking_distance", "ctr_fixes", "refresh",
                                   "new_post_ideas", "question_queries", "ai_referrals", "bing")}
    return json.dumps(keep, default=str)[:15000]


def prompt(today):
    cfg = EC.CFG
    n = cfg.get("niche", {})
    pillars = [p["name"] for p in n.get("pillars", [])]
    digests = sorted(glob.glob(os.path.join(ROOT, "scanner", "sources", "digests", "digest-*.md")))
    digest = read(digests[-1], 60000) if digests else "No digest yet."
    return f"""You build the daily topic list for {EC.SITE_NAME} ({cfg.get('brand', {}).get('name', '')}).
Today is {today}. Audience: {n.get('audience', '')}. Language for titles and text: {n.get('language', 'English')}.
Pillars (use these exact names as "category"): {json.dumps(pillars)}. Never cover: {json.dumps(n.get('out_of_scope', []))}.

Make 8–12 news topics from the digest below, plus 2–4 topics with category "From your data" built from the analytics
opportunities (best striking-distance query, biggest gap or rising query, a refresh or CTR fix). Add a "data" line to any
news topic that matches a site query. Skip stories already covered recently unless there's a new development:
{json.dumps(recent_titles())}

Rules: every fact must come from the digest's source cards or a page you opened with web search, with its date and source
in the text. Never invent numbers. "refs" must only contain URLs that appear in the digest or that you opened. If you
can't source a fact, leave it out. Label vendor claims as vendor claims.

Reply with ONLY a JSON object, no prose, exactly this shape:
{{"date": "{today}", "window": "Stories published …", "scanned": "what you read and what was missing",
 "topics": [{{"id": "t1", "category": "<pillar or From your data>", "priority": "Top pick|Strong|Good",
   "format": "Decode post|Deep post|LinkedIn|Reel|Refresh", "title": "…", "why": "…", "data": "optional",
   "facts": ["…"], "angle": "…", "refs": [["Publisher — headline", "https://…"]], "fanout": ["5–7 search questions"]}}]}}

=== ANALYTICS OPPORTUNITIES (JSON) ===
{opportunities_summary()}

=== NEWEST SCANNER DIGEST ===
{digest}
"""


def call(body, key):
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST", headers={
        "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)


def ask(text, key):
    body = {"model": os.environ.get("CLAUDE_MODEL") or "claude-sonnet-5-5", "max_tokens": 16000,
            "messages": [{"role": "user", "content": text}]}
    if os.environ.get("TOPIC_WEB_SEARCH", "1") != "0":
        body["tools"] = [{"type": os.environ.get("TOPIC_WEB_SEARCH_TOOL") or "web_search_20250305",
                          "name": "web_search", "max_uses": 8}]
    try:
        r = call(body, key)
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:400]
        if body.get("tools") and e.code == 400:
            print("Web search tool not accepted; retrying without it:", detail)
            body.pop("tools")
            r = call(body, key)
        else:
            sys.exit(f"Claude API {e.code}: {detail}")
    return "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")


def parse(text, today):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        sys.exit("No JSON in Claude's reply:\n" + text[:800])
    d = json.loads(m.group(0))
    d["date"] = today
    pillars = set(EC.pillars()) | {"From your data"}
    keep = []
    for i, t in enumerate(d.get("topics", []), 1):
        refs = [r for r in t.get("refs", []) if isinstance(r, list) and len(r) == 2 and str(r[1]).startswith("http")]
        if not refs or not t.get("title"):
            continue
        t["refs"] = refs
        t["id"] = t.get("id") or f"t{i}"
        if t.get("category") not in pillars:
            t["category"] = (EC.pillars() or ["From your data"])[0]
        t.setdefault("facts", []); t.setdefault("fanout", []); t.setdefault("angle", ""); t.setdefault("why", "")
        t.setdefault("priority", "Good"); t.setdefault("format", "Decode post")
        keep.append(t)
    d["topics"] = keep
    d.setdefault("window", ""); d.setdefault("scanned", "")
    return d


def main():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("Set ANTHROPIC_API_KEY (GitHub secret) to build the topic list with the Claude API.")
    today = EC.today().isoformat()
    d = parse(ask(prompt(today), key), today)
    if not d["topics"]:
        sys.exit("Claude returned no sourced topics; nothing saved (the email will send the scanner's top picks).")
    os.makedirs(LISTS, exist_ok=True)
    path = os.path.join(LISTS, f"{today}.json")
    json.dump(d, open(path, "w"), indent=1, ensure_ascii=False)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "render_topics.py"), path], check=True)
    print(f"{len(d['topics'])} topics → {path}")


if __name__ == "__main__":
    main()
