#!/usr/bin/env python3
"""
Turn the latest Search Console + GA4 pull into decisions for your site.

Reads the newest analytics/data/YYYY-MM-DD/ folder (written by fetch.py) and writes:
  analytics/reports/YYYY-MM-DD.md   the readable report
  analytics/reports/latest.md       same, always the newest
  analytics/opportunities.json      machine-readable list the daily topic list and skills use

What it looks for (each list is ranked, with the reason in plain words):
  1. Scorecard           clicks, impressions, CTR, position, sessions, AI referrals, key events — vs the previous 28 days
  2. Striking distance   queries ranking 8–20 with real impressions: one good update can push them to page 1
  3. CTR fixes           pages on page 1 whose CTR is far below what their position usually earns: rewrite title + meta
  4. Refresh             pages that lost clicks: update facts, add sections, re-date
  5. New post ideas      queries you get impressions for but rank past 20 for (no page really answers them),
                         plus fast-rising queries — grouped by pillar
  6. Question queries    how/what/why/should… searches: FAQ and H2 material, what AI answers get asked
  7. Cannibalisation     queries where two of your pages split the impressions
  8. AI referrals        visits from ChatGPT, Perplexity, Gemini, Copilot, Claude — by source and landing page
  9. Channel mix         sessions by channel, and which landing pages bring key events

Usage:
  python3 analytics/analyze.py                 # newest data folder
  python3 analytics/analyze.py --data DIR      # a specific folder
  python3 analytics/analyze.py --tracker       # also add this week's row to tracker/weekly-tracker.csv
"""
import argparse, csv, datetime as dt, glob, json, os, re, sys
from collections import defaultdict
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TERRITORIES = os.path.join(ROOT, "scanner", "sources", "territories.json")
CONFIG = os.path.join(ROOT, "engine.config.json")
TRACKER = os.path.join(ROOT, "tracker", "weekly-tracker.csv")

# Tunable thresholds (small site defaults — raise them as traffic grows)
MIN_IMPR_STRIKING = 20     # impressions in 28 days for a striking-distance query
MIN_IMPR_CTR = 50          # impressions for a CTR-fix page
MIN_IMPR_GAP = 15          # impressions for a "no page answers this" query
MIN_CLICKS_REFRESH = 5     # previous-period clicks before a drop counts
# Rough organic CTR by position (industry averages; use only to spot outliers, not as targets)
EXPECTED_CTR = {1: .28, 2: .15, 3: .10, 4: .07, 5: .05, 6: .04, 7: .03, 8: .025, 9: .02, 10: .018}
AI_SOURCES = [("ChatGPT", r"chatgpt\.com|chat\.openai\.com|openai"), ("Perplexity", r"perplexity"),
              ("Gemini", r"gemini\.google|bard\.google"), ("Copilot", r"copilot|bing\.com/chat|edgeservices"),
              ("Claude", r"claude\.ai|anthropic"), ("Meta AI", r"meta\.ai"), ("Grok", r"grok|x\.ai"),
              ("DeepSeek", r"deepseek"), ("You.com", r"(^|\.)you\.com"), ("Phind", r"phind")]
QUESTION = re.compile(r"^(how|what|why|when|where|which|who|is|are|can|does|do|should|will|vs\b)|\bvs\b|\?$", re.I)


def read(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def path_of(url):
    p = urlparse(url).path if url.startswith("http") else url
    return p or "/"


def pct(a, b):
    if not b:
        return "new" if a else "—"
    return f"{(a - b) / b * 100:+.0f}%"


def load_pillars():
    try:
        cfg = json.load(open(TERRITORIES))
        return cfg.get("order", []), cfg.get("keywords", {})
    except Exception:
        return [], {}


ORDER, KW = load_pillars()


def site_name():
    try:
        b = json.load(open(CONFIG)).get("brand", {})
        return b.get("site_name") or urlparse(b.get("site", "")).netloc or "Your site"
    except Exception:
        return "Your site"


def pillar(text):
    t = " " + text.lower() + " "
    for p in ORDER:
        if any(re.search(r"(?<![a-z0-9])" + re.escape(k.strip()), t) for k in KW.get(p, [])):
            return p
    return "Unmapped"


def ai_source(src):
    for name, rx in AI_SOURCES:
        if re.search(rx, src or "", re.I):
            return name
    return None


def agg_gsc(rows, key):
    out = {}
    for r in rows:
        out[r[key]] = {"clicks": num(r["clicks"]), "impressions": num(r["impressions"]),
                       "ctr": num(r["ctr"]), "position": num(r["position"])}
    return out


def totals_gsc(rows):
    c = sum(num(r["clicks"]) for r in rows)
    i = sum(num(r["impressions"]) for r in rows)
    pos = sum(num(r["position"]) * num(r["impressions"]) for r in rows) / i if i else 0
    return {"clicks": c, "impressions": i, "ctr": c / i if i else 0, "position": pos}


def ga4_totals(rows):
    t = defaultdict(float)
    for r in rows:
        s = num(r["sessions"])
        t["sessions"] += s
        t["engaged"] += num(r["engagedSessions"])
        t["key_events"] += num(r["keyEvents"])
        t["new_users"] += num(r["newUsers"])
        if r["sessionDefaultChannelGroup"] == "Organic Search":
            t["organic"] += s
        if ai_source(r["sessionSource"]):
            t["ai"] += s
    return t


def analyze(d):
    meta = json.load(open(os.path.join(d, "meta.json"))) if os.path.exists(os.path.join(d, "meta.json")) else {}
    qp_cur, qp_prev = read(f"{d}/gsc_query_page_cur.csv"), read(f"{d}/gsc_query_page_prev.csv")
    p_cur, p_prev = agg_gsc(read(f"{d}/gsc_page_cur.csv"), "page"), agg_gsc(read(f"{d}/gsc_page_prev.csv"), "page")
    q_cur, q_prev = agg_gsc(read(f"{d}/gsc_query_cur.csv"), "query"), agg_gsc(read(f"{d}/gsc_query_prev.csv"), "query")
    g_cur, g_prev = read(f"{d}/ga4_landing_cur.csv"), read(f"{d}/ga4_landing_prev.csv")
    has_gsc, has_ga4 = bool(p_cur or q_cur), bool(g_cur)

    o = {"date": meta.get("pulled", os.path.basename(d)), "window": meta.get("current"),
         "previous_window": meta.get("previous"), "sources": meta.get("sources", []), "errors": meta.get("errors", []),
         **({"demo": meta["demo"]} if meta.get("demo") else {})}

    # 1. Scorecard
    sc = {}
    if has_gsc:
        a, b = totals_gsc(read(f"{d}/gsc_page_cur.csv")), totals_gsc(read(f"{d}/gsc_page_prev.csv"))
        sc["gsc"] = {"cur": a, "prev": b}
    if has_ga4:
        sc["ga4"] = {"cur": dict(ga4_totals(g_cur)), "prev": dict(ga4_totals(g_prev))}
    b_cur, b_prev = read(f"{d}/bing_query_cur.csv"), read(f"{d}/bing_query_prev.csv")
    if b_cur or read(f"{d}/bing_page_cur.csv"):
        sc["bing"] = {"cur": totals_gsc(read(f"{d}/bing_page_cur.csv") or b_cur),
                      "prev": totals_gsc(read(f"{d}/bing_page_prev.csv") or b_prev)}
        bq = agg_gsc(b_cur, "query")
        o["bing"] = {
            "top_queries": [{"query": k, "clicks": int(v["clicks"]), "impressions": int(v["impressions"]),
                             "position": round(v["position"], 1), "pillar": pillar(k)}
                            for k, v in sorted(bq.items(), key=lambda x: -x[1]["impressions"])[:15]],
            # demand Bing (and so Copilot / ChatGPT search) sees that Google doesn't show you for
            "bing_only": [{"query": k, "impressions": int(v["impressions"]), "position": round(v["position"], 1), "pillar": pillar(k)}
                          for k, v in sorted(bq.items(), key=lambda x: -x[1]["impressions"])
                          if k not in q_cur and v["impressions"] >= MIN_IMPR_GAP][:15]}
    o["scorecard"] = sc

    # best page per query (by impressions) and pages per query
    by_q = defaultdict(list)
    for r in qp_cur:
        by_q[r["query"]].append(r)

    # 2. Striking distance
    sd = []
    for q, v in q_cur.items():
        if 8 <= v["position"] <= 20 and v["impressions"] >= MIN_IMPR_STRIKING:
            best = max(by_q.get(q, [{"page": ""}]), key=lambda r: num(r.get("impressions")))
            sd.append({"query": q, "page": path_of(best["page"]), "impressions": int(v["impressions"]),
                       "clicks": int(v["clicks"]), "position": round(v["position"], 1), "pillar": pillar(q),
                       "action": "Add a section or FAQ that answers this query directly, use the phrase in an H2, "
                                 "and link to the page from 2 related posts."})
    o["striking_distance"] = sorted(sd, key=lambda x: -x["impressions"])[:25]

    # 3. CTR fixes
    cf = []
    for p, v in p_cur.items():
        pos = round(v["position"])
        if 1 <= pos <= 10 and v["impressions"] >= MIN_IMPR_CTR:
            exp = EXPECTED_CTR[pos]
            if v["ctr"] < exp * 0.5:
                top_q = sorted([r for r in qp_cur if r["page"] == p], key=lambda r: -num(r["impressions"]))[:3]
                cf.append({"page": path_of(p), "impressions": int(v["impressions"]), "ctr": round(v["ctr"] * 100, 2),
                           "position": round(v["position"], 1), "expected_ctr": round(exp * 100, 1),
                           "top_queries": [r["query"] for r in top_q],
                           "action": "Rewrite the title and meta description around the top query; make the promise specific."})
    o["ctr_fixes"] = sorted(cf, key=lambda x: -x["impressions"])[:15]

    # 4. Refresh (lost clicks)
    rf = []
    for p, b in p_prev.items():
        a = p_cur.get(p, {"clicks": 0, "impressions": 0, "position": 0})
        if b["clicks"] >= MIN_CLICKS_REFRESH and a["clicks"] < b["clicks"] * 0.7:
            rf.append({"page": path_of(p), "clicks_now": int(a["clicks"]), "clicks_before": int(b["clicks"]),
                       "change": pct(a["clicks"], b["clicks"]),
                       "position_now": round(a["position"], 1), "position_before": round(b["position"], 1),
                       "action": "Refresh: re-check every fact and date, add what newer results cover, update 'Last updated'."})
    o["refresh"] = sorted(rf, key=lambda x: x["clicks_now"] - x["clicks_before"])[:15]

    # 5. New post ideas: gaps + rising queries
    gaps = []
    for q, v in q_cur.items():
        if v["position"] > 20 and v["impressions"] >= MIN_IMPR_GAP:
            gaps.append({"query": q, "impressions": int(v["impressions"]), "position": round(v["position"], 1),
                         "pillar": pillar(q), "why": "Google already shows you for this, but no page answers it well."})
    rising = []
    for q, v in q_cur.items():
        b = q_prev.get(q)
        if v["impressions"] >= MIN_IMPR_GAP and (b is None or v["impressions"] >= 2 * max(b["impressions"], 1)):
            rising.append({"query": q, "impressions": int(v["impressions"]),
                           "impressions_before": int(b["impressions"]) if b else 0,
                           "position": round(v["position"], 1), "pillar": pillar(q),
                           "why": "Demand for this is new or doubled in 28 days."})
    o["new_post_ideas"] = {"gaps": sorted(gaps, key=lambda x: -x["impressions"])[:20],
                           "rising": sorted(rising, key=lambda x: -x["impressions"])[:20]}

    # 6. Question queries
    qq = [{"query": q, "impressions": int(v["impressions"]), "position": round(v["position"], 1), "pillar": pillar(q)}
          for q, v in q_cur.items() if QUESTION.search(q.strip())]
    o["question_queries"] = sorted(qq, key=lambda x: -x["impressions"])[:25]

    # 7. Cannibalisation
    cn = []
    for q, rows in by_q.items():
        tot = sum(num(r["impressions"]) for r in rows)
        big = [r for r in rows if tot and num(r["impressions"]) / tot >= 0.2]
        if len(big) >= 2 and tot >= MIN_IMPR_STRIKING:
            cn.append({"query": q, "impressions": int(tot),
                       "pages": [{"page": path_of(r["page"]), "share": round(num(r["impressions"]) / tot * 100),
                                  "position": round(num(r["position"]), 1)} for r in sorted(big, key=lambda r: -num(r["impressions"]))],
                       "action": "Pick one page to own this query; merge or re-angle the other and link it to the owner."})
    o["cannibalisation"] = sorted(cn, key=lambda x: -x["impressions"])[:10]

    # 8. AI referrals + 9. channel mix
    if has_ga4:
        src_cur, src_prev, page_ai, chan, page_ke = defaultdict(float), defaultdict(float), defaultdict(lambda: defaultdict(float)), defaultdict(float), defaultdict(float)
        for r in g_cur:
            s = num(r["sessions"])
            chan[r["sessionDefaultChannelGroup"]] += s
            page_ke[r["landingPage"]] += num(r["keyEvents"])
            n = ai_source(r["sessionSource"])
            if n:
                src_cur[n] += s
                page_ai[r["landingPage"]][n] += s
        for r in g_prev:
            n = ai_source(r["sessionSource"])
            if n:
                src_prev[n] += num(r["sessions"])
        o["ai_referrals"] = {
            "by_source": [{"source": k, "sessions": int(v), "before": int(src_prev.get(k, 0)), "change": pct(v, src_prev.get(k, 0))}
                          for k, v in sorted(src_cur.items(), key=lambda x: -x[1])],
            "by_page": [{"page": p, "sessions": int(sum(v.values())), "sources": {k: int(x) for k, x in v.items()}}
                        for p, v in sorted(page_ai.items(), key=lambda x: -sum(x[1].values()))][:15]}
        o["channels"] = [{"channel": k, "sessions": int(v)} for k, v in sorted(chan.items(), key=lambda x: -x[1])]
        o["key_event_pages"] = [{"page": p, "key_events": int(v)} for p, v in sorted(page_ke.items(), key=lambda x: -x[1]) if v][:10]
    return o


def fmt_n(x):
    return f"{int(x):,}"


def report(o):
    L = [f"# {site_name()} — search & analytics report, {o['date']}", ""]
    if o.get("window"):
        L += [f"Window: **{o['window'][0]} → {o['window'][1]}** (last 28 days with data) vs "
              f"{o['previous_window'][0]} → {o['previous_window'][1]}. Search Console data lags 2–3 days.", ""]
    if o.get("demo"):
        L += [f"> 🧪 **{o['demo']}.**", ""]
    for e in o.get("errors", []):
        first = " ".join(e.split())
        m = re.search(r'"message":\s*"([^"]+)', e)
        L.append(f"> ⚠️ {e.split(':')[0]}: {(m.group(1) if m else first)[:220]}")
    if o.get("errors"):
        L.append("")
    sc = o.get("scorecard", {})
    L += ["## 1. Scorecard", "", "| Metric | Now | Before | Change |", "|---|---|---|---|"]
    if "gsc" in sc:
        a, b = sc["gsc"]["cur"], sc["gsc"]["prev"]
        L += [f"| Search clicks | {fmt_n(a['clicks'])} | {fmt_n(b['clicks'])} | {pct(a['clicks'], b['clicks'])} |",
              f"| Search impressions | {fmt_n(a['impressions'])} | {fmt_n(b['impressions'])} | {pct(a['impressions'], b['impressions'])} |",
              f"| CTR | {a['ctr']*100:.2f}% | {b['ctr']*100:.2f}% | {(a['ctr']-b['ctr'])*100:+.2f} pts |",
              f"| Avg position | {a['position']:.1f} | {b['position']:.1f} | {a['position']-b['position']:+.1f} (lower is better) |"]
    if "ga4" in sc:
        a, b = sc["ga4"]["cur"], sc["ga4"]["prev"]
        for k, lab in (("sessions", "Sessions"), ("organic", "Organic search sessions"), ("ai", "AI assistant referrals"),
                       ("engaged", "Engaged sessions"), ("key_events", "Key events (sign-ups etc.)"), ("new_users", "New users")):
            L.append(f"| {lab} | {fmt_n(a.get(k, 0))} | {fmt_n(b.get(k, 0))} | {pct(a.get(k, 0), b.get(k, 0))} |")
    if "bing" in sc:
        a, b = sc["bing"]["cur"], sc["bing"]["prev"]
        L += [f"| Bing clicks | {fmt_n(a['clicks'])} | {fmt_n(b['clicks'])} | {pct(a['clicks'], b['clicks'])} |",
              f"| Bing impressions | {fmt_n(a['impressions'])} | {fmt_n(b['impressions'])} | {pct(a['impressions'], b['impressions'])} |"]
    if not sc:
        L.append("| — | no data yet | | |")
    L.append("")

    def table(title, intro, rows, cols, empty="Nothing here this period."):
        L.extend([f"## {title}", "", intro, ""])
        if not rows:
            L.extend([f"_{empty}_", ""])
            return
        L.append("| " + " | ".join(c[0] for c in cols) + " |")
        L.append("|" + "---|" * len(cols))
        for r in rows:
            L.append("| " + " | ".join(str(c[1](r)).replace("|", "/") for c in cols) + " |")
        L.append("")

    table("2. Striking distance — one update from page 1",
          "Queries at positions 8–20 with real impressions. Add a section or FAQ that answers the query, use it in an H2, add 2 internal links.",
          o["striking_distance"], [("Query", lambda r: r["query"]), ("Page", lambda r: r["page"]), ("Impr.", lambda r: r["impressions"]),
                                   ("Pos.", lambda r: r["position"]), ("Pillar", lambda r: r["pillar"])])
    table("3. CTR fixes — ranking but not clicked",
          "Page-1 pages getting under half the clicks their position usually earns. Rewrite title + meta around the top query.",
          o["ctr_fixes"], [("Page", lambda r: r["page"]), ("Impr.", lambda r: r["impressions"]), ("CTR", lambda r: f"{r['ctr']}%"),
                           ("Typical at pos.", lambda r: f"{r['expected_ctr']}% @ {r['position']}"), ("Top queries", lambda r: ", ".join(r["top_queries"]))])
    table("4. Refresh — pages losing clicks", "Lost 30%+ of clicks vs the previous 28 days. Re-check facts, add what newer results cover, re-date.",
          o["refresh"], [("Page", lambda r: r["page"]), ("Clicks", lambda r: f"{r['clicks_before']} → {r['clicks_now']}"),
                         ("Change", lambda r: r["change"]), ("Position", lambda r: f"{r['position_before']} → {r['position_now']}")])
    table("5a. New post ideas — Google shows you, nothing answers it",
          "Queries with impressions where your best page ranks past 20. Each is a decode or deep post waiting to be written.",
          o["new_post_ideas"]["gaps"], [("Query", lambda r: r["query"]), ("Impr.", lambda r: r["impressions"]),
                                        ("Pos.", lambda r: r["position"]), ("Pillar", lambda r: r["pillar"])])
    table("5b. Rising queries", "New or doubled demand in the last 28 days.",
          o["new_post_ideas"]["rising"], [("Query", lambda r: r["query"]), ("Impr.", lambda r: f"{r['impressions_before']} → {r['impressions']}"),
                                          ("Pos.", lambda r: r["position"]), ("Pillar", lambda r: r["pillar"])])
    table("6. Question queries — FAQ and AEO material",
          "What people (and AI answer engines' fan-out) ask. Use them as H2s and FAQs, word for word.",
          o["question_queries"], [("Question", lambda r: r["query"]), ("Impr.", lambda r: r["impressions"]),
                                  ("Pos.", lambda r: r["position"]), ("Pillar", lambda r: r["pillar"])])
    table("7. Cannibalisation", "Two of your pages split the same query. Pick one owner, re-angle or merge the other.",
          o["cannibalisation"], [("Query", lambda r: r["query"]), ("Impr.", lambda r: r["impressions"]),
                                 ("Pages (share, pos.)", lambda r: "; ".join(f"{p['page']} ({p['share']}%, {p['position']})" for p in r["pages"]))])
    if "ai_referrals" in o:
        table("8. AI assistant referrals", "Visits from ChatGPT, Perplexity, Gemini, Copilot and Claude — proof your AEO work lands.",
              o["ai_referrals"]["by_source"], [("Source", lambda r: r["source"]), ("Sessions", lambda r: r["sessions"]),
                                               ("Before", lambda r: r["before"]), ("Change", lambda r: r["change"])],
              empty="No AI-assistant visits recorded yet.")
        table("8b. Pages AI assistants send people to", "These pages are being cited. Keep them fresh; build related posts that link to them.",
              o["ai_referrals"]["by_page"], [("Page", lambda r: r["page"]), ("Sessions", lambda r: r["sessions"]),
                                             ("From", lambda r: ", ".join(f"{k} {v}" for k, v in r["sources"].items()))])
        table("9. Channels", "Where sessions came from.", o["channels"],
              [("Channel", lambda r: r["channel"]), ("Sessions", lambda r: r["sessions"])])
        table("9b. Pages that convert", "Landing pages with the most key events (newsletter sign-ups etc.). Point internal links and CTAs here.",
              o["key_event_pages"], [("Page", lambda r: r["page"]), ("Key events", lambda r: r["key_events"])])
    if o.get("bing"):
        table("10. Bing — top queries", "Bing's index also feeds Microsoft Copilot and ChatGPT search.",
              o["bing"]["top_queries"], [("Query", lambda r: r["query"]), ("Clicks", lambda r: r["clicks"]),
                                         ("Impr.", lambda r: r["impressions"]), ("Pos.", lambda r: r["position"]), ("Pillar", lambda r: r["pillar"])])
        table("10b. Bing-only demand", "Queries Bing shows you for that Google doesn't (yet). Often early signal for new topics.",
              o["bing"]["bing_only"], [("Query", lambda r: r["query"]), ("Impr.", lambda r: r["impressions"]),
                                       ("Pos.", lambda r: r["position"]), ("Pillar", lambda r: r["pillar"])])
    L += ["---", "_Built by analytics/analyze.py from Search Console, GA4 and Bing Webmaster Tools. CTR benchmarks are rough industry averages, "
          "used only to spot outliers. Thresholds are at the top of the script._"]
    return "\n".join(L)


def update_tracker(o):
    sc = o.get("scorecard", {})
    g, a = sc.get("gsc", {}).get("cur", {}), sc.get("ga4", {}).get("cur", {})
    rows = read(TRACKER)
    header = list(rows[0].keys()) if rows else []
    with open(TRACKER, newline="") as f:
        header = next(csv.reader(f))
    week = dt.date.fromisoformat(o["date"])
    week = (week - dt.timedelta(days=week.weekday())).isoformat()
    if any(r.get("week_start") == week for r in rows):
        return False
    row = {k: "" for k in header}
    row.update({"week_start": week, "site_sessions": int(a.get("sessions", 0)) if a else "",
                "gsc_clicks_28d": int(g.get("clicks", 0)) if g else "", "gsc_impressions_28d": int(g.get("impressions", 0)) if g else "",
                "gsc_avg_position": round(g.get("position", 0), 1) if g else "",
                "organic_sessions_28d": int(a.get("organic", 0)) if a else "", "ai_referrals_28d": int(a.get("ai", 0)) if a else "",
                "key_events_28d": int(a.get("key_events", 0)) if a else "",
                "notes": "auto: 28-day totals from analytics/reports"})
    with open(TRACKER, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=header).writerow({k: row.get(k, "") for k in header})
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", help="data folder (default: newest in analytics/data/)")
    ap.add_argument("--tracker", action="store_true", help="add this week's row to tracker/weekly-tracker.csv")
    args = ap.parse_args()
    d = args.data
    if not d:
        dirs = sorted(glob.glob(os.path.join(HERE, "data", "20*")))
        if not dirs:
            print("No data yet — run analytics/fetch.py first (needs the Google credentials).")
            return 0
        d = dirs[-1]
    o = analyze(d)
    os.makedirs(os.path.join(HERE, "reports"), exist_ok=True)
    md = report(o)
    for p in (os.path.join(HERE, "reports", f"{o['date']}.md"), os.path.join(HERE, "reports", "latest.md")):
        open(p, "w").write(md)
    json.dump(o, open(os.path.join(HERE, "opportunities.json"), "w"), indent=1)
    print(f"Report → analytics/reports/{o['date']}.md · "
          f"{len(o['striking_distance'])} striking-distance, {len(o['ctr_fixes'])} CTR fixes, "
          f"{len(o['refresh'])} refresh, {len(o['new_post_ideas']['gaps'])} gaps, {len(o['question_queries'])} questions")
    if args.tracker and update_tracker(o):
        print("Tracker: added this week's row")
    return 0


if __name__ == "__main__":
    sys.exit(main())
