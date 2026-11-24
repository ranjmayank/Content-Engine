#!/usr/bin/env python3
"""Quick setup — 6 questions, sensible defaults for everything else.

Used three ways:
  1. In the browser (no installs): GitHub → Actions → "1 · Set up my engine" → Run workflow → fill the form.
  2. On your computer:  python3 setup/quick.py          (asks the 6 questions)
  3. From a script:     python3 setup/quick.py --brand "My Brand" --site https://my.site --name "Sam Lee" \
                          --niche b2b-saas --timezone India [--about "..."] [--language English] [--sites "a.com, b.com"]

Everything it doesn't ask is filled from engine.config.example.json with your details swapped in.
Change anything later by re-running setup/init.py (the full questions) or by asking Claude to "change my settings".
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import init  # noqa: E402

# Friendly names → IANA timezones (anything already like "Area/City" is used as is)
TZ = {
    "india": "Asia/Kolkata", "ist": "Asia/Kolkata", "delhi": "Asia/Kolkata", "new delhi": "Asia/Kolkata", "noida": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata", "bangalore": "Asia/Kolkata", "bengaluru": "Asia/Kolkata", "kolkata": "Asia/Kolkata",
    "chennai": "Asia/Kolkata", "hyderabad": "Asia/Kolkata", "pune": "Asia/Kolkata",
    "uk": "Europe/London", "united kingdom": "Europe/London", "england": "Europe/London", "london": "Europe/London",
    "ireland": "Europe/Dublin", "dublin": "Europe/Dublin", "germany": "Europe/Berlin", "berlin": "Europe/Berlin",
    "france": "Europe/Paris", "paris": "Europe/Paris", "spain": "Europe/Madrid", "madrid": "Europe/Madrid",
    "italy": "Europe/Rome", "netherlands": "Europe/Amsterdam", "amsterdam": "Europe/Amsterdam",
    "us east": "America/New_York", "est": "America/New_York", "new york": "America/New_York", "boston": "America/New_York",
    "miami": "America/New_York", "toronto": "America/Toronto", "us central": "America/Chicago", "cst": "America/Chicago",
    "chicago": "America/Chicago", "texas": "America/Chicago", "austin": "America/Chicago", "dallas": "America/Chicago",
    "us mountain": "America/Denver", "denver": "America/Denver", "us west": "America/Los_Angeles", "pst": "America/Los_Angeles",
    "california": "America/Los_Angeles", "san francisco": "America/Los_Angeles", "los angeles": "America/Los_Angeles",
    "seattle": "America/Los_Angeles", "vancouver": "America/Vancouver", "usa": "America/New_York", "us": "America/New_York",
    "canada": "America/Toronto", "mexico": "America/Mexico_City", "brazil": "America/Sao_Paulo", "sao paulo": "America/Sao_Paulo",
    "uae": "Asia/Dubai", "dubai": "Asia/Dubai", "saudi arabia": "Asia/Riyadh", "pakistan": "Asia/Karachi",
    "bangladesh": "Asia/Dhaka", "nepal": "Asia/Kathmandu", "sri lanka": "Asia/Colombo", "singapore": "Asia/Singapore",
    "malaysia": "Asia/Kuala_Lumpur", "indonesia": "Asia/Jakarta", "philippines": "Asia/Manila", "vietnam": "Asia/Ho_Chi_Minh",
    "thailand": "Asia/Bangkok", "china": "Asia/Shanghai", "hong kong": "Asia/Hong_Kong", "japan": "Asia/Tokyo",
    "tokyo": "Asia/Tokyo", "korea": "Asia/Seoul", "australia": "Australia/Sydney", "sydney": "Australia/Sydney",
    "melbourne": "Australia/Melbourne", "new zealand": "Pacific/Auckland", "nigeria": "Africa/Lagos", "lagos": "Africa/Lagos",
    "kenya": "Africa/Nairobi", "south africa": "Africa/Johannesburg", "egypt": "Africa/Cairo", "utc": "UTC", "gmt": "UTC",
}


def timezone(text):
    """Turn 'India', 'London', 'pst' or 'Asia/Kolkata' into a valid IANA name (UTC if unknown)."""
    from zoneinfo import ZoneInfo
    t = (text or "").strip()
    name = TZ.get(t.lower(), t)
    try:
        ZoneInfo(name)
        return name, True
    except Exception:
        return "UTC", False


def site_url(text):
    u = (text or "").strip().rstrip("/")
    if u and not u.startswith(("http://", "https://")):
        u = "https://" + u
    return u


def build(brand, site, name, niche, tz, about="", language="English", sites=""):
    P = init.presets()
    niche = (niche or "blank").strip().lower().split(" ")[0]
    if niche not in P:
        print(f"Unknown niche '{niche}' — using 'blank'. Options: {', '.join(P)}")
        niche = "blank"
    pr = P[niche]
    if not pr["pillars"]:
        sys.exit("The 'blank' niche needs your own pillars — use the full setup instead: python3 setup/init.py "
                 "(or ask Claude: \"set up the engine\").")
    tzname, ok = timezone(tz)
    if not ok:
        print(f"Couldn't recognise the timezone '{tz}' — using UTC. Fix it later in engine.config.json → cadence.timezone.")
    ex = json.load(open(init.EXAMPLE))
    site = site_url(site)
    host = re.sub(r"^https?://(www\.)?", "", site).split("/")[0]
    first = (name or "").split(" ")[0]
    cfg = {
        **ex,
        "brand": {"name": brand.strip(), "site": site, "site_name": host, "tagline": pr["label"],
                  "handles": {"linkedin": "", "instagram": "", "x": "", "youtube": "", "newsletter": "", "medium": ""}},
        "author": {"name": name.strip(), "role_line": about.strip(),
                   "bio": f"{name.strip()} {about.strip()}".strip() + (f" and writes at {host}." if about else f" writes at {host}."),
                   "work_context": about.strip(), "confidential": []},
        "niche": {"preset": niche, "summary": pr["summary"], "audience": pr["audience"], "region": "",
                  "language": (language or "English").strip(), "pillars": pr["pillars"],
                  "out_of_scope": pr["out_of_scope"], "out_of_scope_goes_to": ""},
        "cadence": {**ex["cadence"], "timezone": tzname},
        "hashtags": pr.get("hashtags", {}),
        "ai_visibility": {"prompts": [], "competitors": []},
        "use_preset_sources": True,
        "add_sources": [{"url": s.strip(), "category": pr["pillars"][0]["name"], "why": "Added at setup"}
                        for s in re.split(r"[,\n ]+", sites or "") if "." in s],
    }
    cfg.pop("_readme", None)
    cfg["_setup"] = {"mode": "quick", "date": dt.date.today().isoformat(),
                     "note": f"Quick setup for {first or 'you'}. Re-run setup/init.py or ask Claude to fill in handles, voice, bio and channels."}
    return cfg


def ask(q, default=""):
    v = input(f"{q}{f' [{default}]' if default else ''}: ").strip()
    return v or default


def main():
    ap = argparse.ArgumentParser(description="Quick setup — 6 questions")
    for k in ("brand", "site", "name", "niche", "timezone", "about", "language", "sites"):
        ap.add_argument("--" + k, default=os.environ.get("SETUP_" + k.upper(), ""))
    a = ap.parse_args()
    if not (a.brand and a.site and a.name):
        P = init.presets()
        print("\n=== Quick setup — 6 questions (Enter = default) ===\n")
        a.brand = a.brand or ask("1. Your brand or blog name (e.g. Growth Notes)")
        a.site = a.site or ask("2. Your website address (e.g. mysite.com)")
        a.name = a.name or ask("3. Your name (shown as the author)")
        print("\n4. Your niche:")
        keys = [k for k in P if k != "blank"]
        for i, k in enumerate(keys, 1):
            print(f"   {i}. {P[k]['label']}")
        v = ask("   Pick a number", "1")
        a.niche = keys[int(v) - 1] if v.isdigit() and 0 < int(v) <= len(keys) else v
        a.timezone = a.timezone or ask("5. Where are you? (country or city, e.g. India, London, New York)", "UTC")
        a.about = a.about or ask("6. One line about what you do (optional, e.g. 'runs marketing at a SaaS company')")
        if not (a.brand and a.site and a.name):
            sys.exit("Brand, website and name are needed. Nothing was written.")
    cfg = build(a.brand, a.site, a.name, a.niche, a.timezone, a.about, a.language or "English", a.sites)
    # switching niche: start from the new niche's sources (sites you added by hand are kept)
    src_path = os.path.join(init.SRC_DIR, "sources.json")
    if os.path.exists(init.CONFIG) and os.path.exists(src_path):
        old = json.load(open(init.CONFIG)).get("niche", {}).get("preset")
        if old and old != cfg["niche"]["preset"]:
            P = init.presets()
            old_names = set()
            if P.get(old, {}).get("sources_file"):
                old_names = {x["name"] for x in json.load(open(os.path.join(init.PRESETS, P[old]["sources_file"])))}
            mine = [x for x in json.load(open(src_path)) if x["name"] not in old_names]
            json.dump([], open(src_path, "w"))
            cfg["add_sources"] += [{"url": x.get("site") or x["url"], "category": x.get("category", ""), "why": x.get("why", "")} for x in mine]
            os.remove(src_path)
    tmp = os.path.join(ROOT, ".quick-answers.json")
    json.dump(cfg, open(tmp, "w"), ensure_ascii=False)
    try:
        init.write_all(*init.from_answers(tmp))
    finally:
        os.remove(tmp)
    c = json.load(open(init.CONFIG))
    print(f"\n✅ Set up '{c['brand']['name']}' for {c['brand']['site']} — niche: {c['niche']['preset']}, "
          f"timezone: {c['cadence']['timezone']}, {len(json.load(open(os.path.join(init.SRC_DIR, 'sources.json'))))} news sources.")


if __name__ == "__main__":
    main()
