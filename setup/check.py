#!/usr/bin/env python3
"""Check my setup — what's working, what's missing, and the one thing to do next.

Runs in GitHub (Actions → "2 · Check my setup" — it can see which secrets are set, never their values)
or on your computer: python3 setup/check.py  (there it can only check files, not GitHub secrets).
"""
import datetime as dt
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_GH = os.environ.get("GITHUB_ACTIONS") == "true"
GUIDE = "docs/START-HERE.md"


def has(name):
    return bool((os.environ.get(name) or "").strip())


def newest(pattern):
    files = sorted(glob.glob(os.path.join(ROOT, pattern)))
    return files[-1] if files else None


def age_days(path):
    if not path:
        return None
    return (dt.datetime.now().timestamp() - os.path.getmtime(path)) / 86400


def date_in_name(path):
    import re
    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path or ""))
    return m.group(1) if m else ""


def main():
    rows = []  # (part, item, status, detail, fix)

    def add(part, item, ok, detail="", fix=""):
        rows.append((part, item, ok, detail, fix))

    # ---- Part 1: the basics
    cfg_path = os.path.join(ROOT, "engine.config.json")
    cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else None
    if not cfg:
        add(1, "Settings", "no", "engine.config.json doesn't exist yet",
            f"Actions → \"1 · Set up my engine\" → Run workflow ({GUIDE}, Part 1)")
    else:
        b = cfg.get("brand", {})
        add(1, "Settings", "yes", f"{b.get('name')} · {b.get('site')} · niche {cfg.get('niche', {}).get('preset')} · {cfg.get('cadence', {}).get('timezone')}")
        src = os.path.join(ROOT, "scanner", "sources", "sources.json")
        n = len(json.load(open(src))) if os.path.exists(src) else 0
        add(1, "News sources", "yes" if n >= 5 else "warn", f"{n} sources",
            "" if n >= 5 else "Add the sites you read: re-run \"1 · Set up my engine\" with the 'websites you read' box filled in")
        d = newest("scanner/sources/digests/digest-*.md")
        if not d:
            add(1, "News digest", "no", "no digest yet", "Actions → \"Daily fuel scan\" → Run workflow (takes 2–10 min)")
        else:
            dd = date_in_name(d)
            stale = dd and (dt.date.today() - dt.date.fromisoformat(dd)).days > 2
            add(1, "News digest", "warn" if stale else "yes", f"latest {dd}",
                "Scans have stopped — check the Actions tab for a failed \"Daily fuel scan\"" if stale else "")
        health = os.path.join(ROOT, "scanner", "sources", "SOURCES.md")
        if os.path.exists(health):
            t = open(health).read()
            red = t.count("🔴")
            add(1, "Source health", "warn" if red else "yes", f"{red} source(s) failing" if red else "all sources reachable",
                "Open scanner/sources/SOURCES.md — remove or fix the 🔴 ones (docs/troubleshooting.md)" if red else "")
        a = os.path.join(ROOT, "seo-audit", "reports", "latest.json")
        if os.path.exists(a):
            try:
                r = json.load(open(a))
                crit = sum(1 for i in r.get("issues", []) if i["severity"] == "critical")
                add(1, "SEO audit", "yes", f"score {r.get('score')}/100, {crit} critical issue(s), {r['site'].get('checked_at', '')[:10]}")
            except Exception:
                add(1, "SEO audit", "warn", "report unreadable", "Re-run \"Weekly SEO audit\"")
        else:
            add(1, "SEO audit", "no", "no audit yet", "Actions → \"Weekly SEO audit\" → Run workflow")
        add(1, "Brand kit", "yes" if os.path.exists(os.path.join(ROOT, "brand", "avatar-1000.png")) else "warn",
            "brand/ images", "" if os.path.exists(os.path.join(ROOT, "brand", "avatar-1000.png")) else "Re-run \"1 · Set up my engine\"")

    # ---- Part 2: your data and email (only checkable in GitHub)
    if IN_GH:
        g = has("GOOGLE_SERVICE_ACCOUNT_JSON")
        add(2, "Google key", "yes" if g else "no", "GOOGLE_SERVICE_ACCOUNT_JSON", "" if g else f"{GUIDE} → Part 2, step A")
        add(2, "Search Console site", "yes" if has("GSC_SITE_URL") else ("no" if g else "skip"), "GSC_SITE_URL",
            "" if has("GSC_SITE_URL") else f"{GUIDE} → Part 2, step A6")
        add(2, "GA4 property", "yes" if has("GA4_PROPERTY_ID") else ("warn" if g else "skip"), "GA4_PROPERTY_ID",
            "" if has("GA4_PROPERTY_ID") else f"{GUIDE} → Part 2, step A6 (optional)")
        bing = has("BING_API_KEY") and has("BING_SITE_URL")
        add(2, "Bing Webmaster Tools", "yes" if bing else "skip", "BING_API_KEY + BING_SITE_URL",
            "" if bing else f"{GUIDE} → Part 2, step B (optional, recommended)")
        keys = ("SMTP_HOST", "SMTP_USER", "SMTP_PASS", "MAIL_TO")
        missing = [k for k in keys if not has(k)]
        st = "yes" if not missing else ("skip" if len(missing) == len(keys) else "warn")
        add(2, "Daily email", st, "SMTP_HOST, SMTP_USER, SMTP_PASS, MAIL_TO" if st != "warn" else "partly set — missing " + ", ".join(missing),
            "" if st == "yes" else f"{GUIDE} → Part 2, step C" + (" (optional)" if st == "skip" else ""))
        claude = has("ANTHROPIC_API_KEY")
        tl = newest("content/topic-lists/2*.json")
        add(3, "Daily topic list", "yes" if (claude or tl) else "skip",
            ("Claude API key set" if claude else "") + (f" · latest list {date_in_name(tl)}" if tl else ""),
            "" if (claude or tl) else f"{GUIDE} → Part 3 (optional)")
        add(3, "Notion", "yes" if has("NOTION_TOKEN") and has("NOTION_DATABASE_ID") else "skip", "NOTION_TOKEN + NOTION_DATABASE_ID",
            "" if has("NOTION_TOKEN") else "docs/integrations.md → Notion (optional)")
        add(3, "PageSpeed", "yes" if has("PSI_API_KEY") else "skip", "PSI_API_KEY", "" if has("PSI_API_KEY") else "docs/integrations.md (optional)")
    rep = newest("analytics/reports/2*.md") or (os.path.join(ROOT, "analytics", "reports", "latest.md")
                                                if os.path.exists(os.path.join(ROOT, "analytics", "reports", "latest.md")) else None)
    if rep:
        add(2, "Analytics report", "yes", "analytics/reports/latest.md")
    elif IN_GH and has("GOOGLE_SERVICE_ACCOUNT_JSON"):
        add(2, "Analytics report", "warn", "key is set but no report yet", "Actions → \"Daily search & analytics pull\" → Run workflow")

    icon = {"yes": "✅", "warn": "⚠️", "no": "❌", "skip": "⬜"}
    parts = {1: "Part 1 — the basics (needed)", 2: "Part 2 — your Google data and email (recommended)", 3: "Part 3 — extras (optional)"}
    out = ["# Setup check", ""]
    if not IN_GH:
        out += ["_Running on your computer: GitHub secrets can't be checked here. Run \"2 · Check my setup\" in the Actions tab for the full check._", ""]
    for p in (1, 2, 3):
        pr = [r for r in rows if r[0] == p]
        if not pr:
            continue
        out += [f"## {parts[p]}", "", "| | Item | Details | To do |", "|---|---|---|---|"]
        out += [f"| {icon[s]} | {i} | {d} | {f} |" for _, i, s, d, f in pr]
        out.append("")
    todo = [r for r in rows if r[2] in ("no", "warn")]
    nxt = todo[0] if todo else next((r for r in rows if r[2] == "skip"), None)
    out += ["## Do this next", "", (f"**{nxt[1]}:** {nxt[4]}" if nxt else "🎉 Everything is set up. Ask Claude to **plan your week**."), "",
            "✅ working · ⚠️ needs a look · ❌ missing (needed) · ⬜ not set up (optional)"]
    if cfg:
        try:
            import io, contextlib
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import schedule
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                schedule.show(markdown=True)
            out += ["", "## When your jobs run", "", buf.getvalue().strip()]
        except Exception:
            pass
    text = "\n".join(out)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        open(os.environ["GITHUB_STEP_SUMMARY"], "a").write(text + "\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
