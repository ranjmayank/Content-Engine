#!/usr/bin/env python3
"""Set up Content Engine for your niche — answers a few questions, writes every file that depends on them.

  python3 setup/init.py                       # interactive (about 5 minutes)
  python3 setup/init.py --preset b2b-saas     # start from a preset, still asks the personal questions
  python3 setup/init.py --answers my.json     # no questions: use a filled-in answers file
                                              # (same shape as engine.config.example.json)
  python3 setup/init.py --list-presets
  python3 setup/init.py --migrate             # after an update: add new settings with defaults, keep yours

Writes:
  engine.config.json                 brand, author, niche, pillars, voice, cadence, channels (every skill reads this)
  scanner/sources/territories.json   pillar keywords the scanner and analytics use to rank stories and queries
  scanner/sources/sources.json       the news sources (from the preset, plus any sites you add)
  CLAUDE.md                          working rules Claude follows in this repo
  style.md                           look and voice for visuals and reels
  .github/workflows/*.yml            schedules converted to UTC from your local times
Re-run any time; it shows your current answers as the defaults.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PRESETS = os.path.join(HERE, "presets")
CONFIG = os.path.join(ROOT, "engine.config.json")
EXAMPLE = os.path.join(ROOT, "engine.config.example.json")
SRC_DIR = os.path.join(ROOT, "scanner", "sources")
CONFIG_VERSION = 2

BANNED = ["In today's fast-paced world", "delve", "leverage", "navigate the landscape", "game-changer", "unlock",
          "unleash", "revolutionize", "seamless", "it's important to note", "In conclusion", "let's dive in"]


def presets():
    out = {}
    for f in sorted(os.listdir(PRESETS)):
        if f.endswith(".json") and not f.endswith(".sources.json"):
            out[f[:-5]] = json.load(open(os.path.join(PRESETS, f)))
    return out


def ask(q, default="", required=False):
    d = f" [{default}]" if default else ""
    while True:
        v = input(f"{q}{d}: ").strip()
        if v:
            return v
        if default or not required:
            return default
        print("  (needed)")


def ask_list(q, default):
    v = ask(q + " (comma-separated)", ", ".join(default))
    return [x.strip() for x in v.split(",") if x.strip()]


def yes(q, default=True):
    v = ask(q + (" (Y/n)" if default else " (y/N)"), "").lower()
    return default if not v else v.startswith("y")


def slug_keywords(name):
    words = re.findall(r"[a-z0-9&+.-]+", name.lower())
    return [name.lower()] + [w for w in words if len(w) > 3]


def interview(cur, preset_name=None):
    P = presets()
    print("\n=== Content Engine setup ===\nPress Enter to keep the value in [brackets].\n")
    b, a, n = cur.get("brand", {}), cur.get("author", {}), cur.get("niche", {})
    cad, ch = cur.get("cadence", {}), cur.get("channels", {})

    print("— Your brand and site —")
    brand = {
        "name": ask("Brand name (what people call your content brand)", b.get("name", ""), True),
        "site": ask("Website URL (where blog posts live)", b.get("site", "https://"), True).rstrip("/"),
        "tagline": ask("One-line tagline", b.get("tagline", "")),
    }
    brand["site_name"] = re.sub(r"^https?://(www\.)?", "", brand["site"]).split("/")[0]
    print("\n— You (the author) —")
    author = {
        "name": ask("Your name (author byline)", a.get("name", ""), True),
        "role_line": ask("One line on what you do (for the author block)", a.get("role_line", "")),
        "work_context": ask("What your day job lets you see (anonymised — used for 'from my work' moments)", a.get("work_context", "")),
        "confidential": ask_list("Anything to never name (employer, clients…) and how to refer to it instead",
                                 a.get("confidential", [])),
    }
    author["bio"] = ask("Short author bio (2 sentences)", a.get("bio", f"{author['name']} {author['role_line']}".strip()))

    print("\n— Your niche —")
    names = list(P)
    for i, k in enumerate(names, 1):
        print(f"  {i}. {k:22} {P[k]['label']}")
    pick = preset_name or n.get("preset") or "blank"
    v = ask("Pick a preset (number or name)", pick)
    pick = names[int(v) - 1] if v.isdigit() and 0 < int(v) <= len(names) else v
    if pick not in P:
        print(f"  unknown preset '{pick}', using blank")
        pick = "blank"
    pr = P[pick]
    niche = {"preset": pick,
             "summary": ask("What your content is about, in one sentence", n.get("summary") or pr["summary"], True),
             "audience": ask("Who it's for", n.get("audience") or pr["audience"], True),
             "region": ask("Main region/country of your audience (blank = global)", n.get("region", "")),
             "language": ask("Language to write in", n.get("language", "English")),
             }
    pillars = n.get("pillars") if n.get("preset") == pick else pr["pillars"]
    terr = dict(pr["territories"])
    print("\nPillars (3–6 topics you'll cover):")
    for p in pillars:
        print(f"  • {p['name']} — {p['covers']}")
    if not pillars or not yes("Keep these pillars?"):
        pillars, kws = [], {}
        print("Enter pillars one by one (blank name to finish).")
        while True:
            nm = ask(f"  Pillar {len(pillars) + 1} name", "")
            if not nm:
                if len(pillars) >= 2:
                    break
                print("  add at least 2")
                continue
            cv = ask("    What it covers", "")
            kw = ask_list("    Keywords that mark a story as this pillar", slug_keywords(nm))
            pillars.append({"name": nm, "covers": cv})
            kws[nm] = [k.lower() for k in kw]
        terr = {"top_label": "stories in your pillars", "order": [p["name"] for p in pillars], "keywords": kws,
                "topic_terms": ask_list("Words that mark a story as being in your world at all", []),
                "boost_terms": ask_list("Words that make a story extra interesting (+1 score), e.g. ai", [])}
    niche["pillars"] = pillars
    niche["out_of_scope"] = ask_list("Topics you never cover", n.get("out_of_scope") or pr["out_of_scope"])
    niche["out_of_scope_goes_to"] = ask("Where out-of-scope ideas go instead (another site, or blank)", n.get("out_of_scope_goes_to", ""))

    print("\n— Channels and handles —")
    channels = {}
    for k, label, dflt in [("blog", "Blog on your site", True), ("linkedin", "LinkedIn", True), ("instagram", "Instagram", True),
                           ("facebook_mirror", "Facebook (mirrors Instagram)", False), ("youtube_shorts", "YouTube Shorts", False),
                           ("x", "X / Twitter", False), ("medium", "Medium (re-import of blog posts)", False),
                           ("newsletter", "Weekly newsletter", True)]:
        channels[k] = yes(f"Use {label}?", ch.get(k, dflt))
    handles = dict(b.get("handles", {}))
    for k in ("linkedin", "instagram", "x", "youtube", "newsletter", "medium"):
        if channels.get(k) or (k == "youtube" and channels.get("youtube_shorts")) or k == "linkedin":
            handles[k] = ask(f"  {k} URL or handle", handles.get(k, ""))
    brand["handles"] = handles

    print("\n— Cadence —")
    t = cad.get("times", {})
    cadence = {
        "timezone": ask("Your timezone (IANA name, e.g. Asia/Kolkata, Europe/London, America/New_York)", cad.get("timezone", "UTC")),
        "deep_posts_per_week": int(ask("Deep posts (2,000+ words) per week", str(cad.get("deep_posts_per_week", 1)))),
        "decode_posts_per_week": int(ask("Short decode posts (400–700 words) per week", str(cad.get("decode_posts_per_week", 3)))),
        "linkedin_per_week": int(ask("LinkedIn posts per week", str(cad.get("linkedin_per_week", 5)))),
        "instagram_per_day": int(ask("Instagram posts per day", str(cad.get("instagram_per_day", 1)))),
        "times": {
            "analytics": ask("Time for the daily analytics pull (HH:MM local)", t.get("analytics", "07:45")),
            "scan": ask("Time for the daily news scan", t.get("scan", "08:00")),
            "topic_list": ask("Time for the Claude topic-list task (set it in Claude's scheduled tasks)", t.get("topic_list", "10:15")),
            "email": ask("Time for the topic email", t.get("email", "11:00")),
            "seo_audit": ask("Weekly SEO audit (Day HH:MM)", t.get("seo_audit", "Mon 07:00")),
        }}
    print("\n— Voice and look —")
    v = cur.get("voice", {})
    voice = {"description": ask("Your voice in a few words", v.get("description", "Practical, clear and direct, proof-led; a practitioner explaining to a smart peer")),
             "banned_phrases": ask_list("Phrases to never use", v.get("banned_phrases", BANNED))}
    c = cur.get("colors", {})
    colors = {"ink": ask("Main dark colour (hex)", c.get("ink", "#16161E")),
              "accent": ask("Accent colour (hex)", c.get("accent", "#F5A623")),
              "paper": ask("Light background (hex)", c.get("paper", "#FAF7F2"))}
    cta = cur.get("cta", {})
    cta = {"mid": ask("Mid-post call to action", cta.get("mid", "Read a related post on the site, or join the newsletter")),
           "end": ask("End-of-post call to action", cta.get("end", "Subscribe to the newsletter"))}
    cfg = {**cur, "brand": brand, "author": author, "niche": niche, "channels": channels, "cadence": cadence,
           "voice": voice, "colors": colors, "cta": cta, "hashtags": cur.get("hashtags") or pr.get("hashtags", {}),
           "seo_audit": cur.get("seo_audit", {"max_pages": 200, "delay": 0.5, "exclude": ["/tag/", "/author/", "?replytocom", "/page/"],
                                               "pagespeed": False, "check_external": False, "render_js": False}),
           "integrations": cur.get("integrations", {})}
    print("\n— Publishing —")
    pub = cur.get("publishing", {})
    plat = ask("Where is the blog? (wordpress / static / ghost / webflow / other)", pub.get("platform", "wordpress")).lower()
    cfg["publishing"] = {"platform": plat, "static_site": pub.get("static_site", {})}
    if plat == "static":
        ssd = cfg["publishing"]["static_site"]
        ssd["repo_path"] = ask("  Path to the site's repo on this computer", ssd.get("repo_path", "../my-site"))
        ssd["content_dir"] = ask("  Folder for posts in it (Astro src/content/blog · Next content/posts · Hugo content/posts · Jekyll _posts)",
                                 ssd.get("content_dir", "content/blog"))
        ssd["front_matter"] = ask("  Front matter: yaml or toml", ssd.get("front_matter", "yaml"))
        ssd["filename"] = ask("  File name pattern", ssd.get("filename", "{slug}.md"))
        ssd["url_pattern"] = ask("  Public URL path of a post", ssd.get("url_pattern", "/blog/{slug}/"))
    cfg["config_version"] = CONFIG_VERSION

    print("\n— News sources —")
    src = load_sources()
    if pr.get("sources_file"):
        preset_src = json.load(open(os.path.join(PRESETS, pr["sources_file"])))
        if not src and yes(f"Start with the preset's {len(preset_src)} sources?"):
            src = preset_src
            for region, names in pr.get("regional", {}).items():
                if not yes(f"  Keep the {len(names)} {region}-specific sources?", region.lower() in niche.get("region", "").lower()):
                    src = [x for x in src if x["name"] not in names]
    print(f"You have {len(src)} sources. Add sites you read (blogs, news sites, newsletters) — the feed is found for you.")
    extra = []
    while True:
        u = ask("  Site URL (blank to finish)", "")
        if not u:
            break
        cat = ask("    Category (usually one of your pillars)", pillars[0]["name"] if pillars else "General")
        extra.append((u, cat, ask("    Why it's useful (optional)", "")))
    return cfg, terr, src, extra


def load_sources():
    p = os.path.join(SRC_DIR, "sources.json")
    return json.load(open(p)) if os.path.exists(p) else []


def render_claude_md(cfg):
    n, a, b = cfg["niche"], cfg["author"], cfg["brand"]
    pillars = " · ".join(p["name"] for p in n["pillars"])
    oos = "; ".join(n.get("out_of_scope", [])) or "nothing listed"
    goes = f" Those ideas go to {n['out_of_scope_goes_to']}." if n.get("out_of_scope_goes_to") else ""
    conf = "".join(f"\n- Confidential: {c}" for c in a.get("confidential", []))
    return f"""# {b['name']} content engine — working rules

Read `engine.config.json` at the start of any content task: it holds the brand, author, pillars, audience, voice and cadence.

- Scope: {len(n['pillars'])} pillars only — {pillars}. Never: {oos}.{goes}
- Audience: {n['audience']}{(' — mostly in ' + n['region']) if n.get('region') else ''}. Write in {n.get('language') or 'English'}.
- Propose the topic first and wait for approval before writing; one topic at a time, covered across formats.
- Build from current, dated sources: the newest digest in `scanner/sources/digests/`, and check `analytics/opportunities.json` / `analytics/reports/latest.md` before proposing topics — the site's own Search Console and GA4 data come first.
- Check `seo-audit/reports/latest.md` before publishing advice: fix critical site issues before writing more content.
- Never invent numbers. Every figure needs a dated source; site numbers need their date window.
- Write as {a['name']}: {cfg['voice']['description']}. Never use: {', '.join(cfg['voice']['banned_phrases'])}.{conf}
- Skills live in `.claude/skills/`; docs in `docs/`. Don't publish, schedule or send anything without an explicit go-ahead.
"""


def render_style(cfg):
    c = cfg["colors"]
    return f"""# Style — {cfg['brand']['name']}

Read by the reel, carousel and quote-card skills. Edit freely.

## Look
- Ink `{c['ink']}` (text, dark backgrounds) · Accent `{c['accent']}` (one highlight per frame) · Paper `{c['paper']}` (light backgrounds)
- Headlines: Outfit Bold · Accents and captions: Geist Mono (both in `brand/scripts/fonts/`, SIL OFL)
- Vertical video 1080×1920 · carousels 1080×1350 · link previews 1200×630

## Voice
- {cfg['voice']['description']}
- Never: {', '.join(cfg['voice']['banned_phrases'])}

## Motion limits
- One idea per card, max 8 words on screen · captions word-timed · no more than one accent element moving at a time

## CTA
- Mid: {cfg['cta']['mid']}
- End: {cfg['cta']['end']}

## Standing notes
- (add anything you keep correcting here, so every skill picks it up)
"""


def write_all(cfg, terr, src, extra):
    os.makedirs(SRC_DIR, exist_ok=True)
    json.dump(cfg, open(CONFIG, "w"), indent=2, ensure_ascii=False)
    json.dump(terr, open(os.path.join(SRC_DIR, "territories.json"), "w"), indent=2, ensure_ascii=False)
    json.dump(src, open(os.path.join(SRC_DIR, "sources.json"), "w"), indent=2, ensure_ascii=False)
    open(os.path.join(ROOT, "CLAUDE.md"), "w").write(render_claude_md(cfg))
    open(os.path.join(ROOT, "style.md"), "w").write(render_style(cfg))
    print("\nWrote engine.config.json, scanner/sources/territories.json, sources.json, CLAUDE.md, style.md")
    if extra:
        print("Finding feeds for the sites you added…")
        sys.path.insert(0, HERE)
        import discover_feed
        discover_feed.add([discover_feed.entry(*e) for e in extra])
    subprocess.run([sys.executable, os.path.join(HERE, "schedule.py")])


def from_answers(path):
    cfg = json.load(open(path))
    cfg.pop("_readme", None)
    P = presets()
    pr = P.get(cfg.get("niche", {}).get("preset", "blank"), P["blank"])
    terr = cfg.pop("territories", None) or dict(pr["territories"])
    if not cfg["niche"].get("pillars"):
        cfg["niche"]["pillars"] = pr["pillars"]
    if not terr.get("keywords"):
        terr = {"top_label": "stories in your pillars", "order": [p["name"] for p in cfg["niche"]["pillars"]],
                "keywords": {p["name"]: p.get("keywords") or slug_keywords(p["name"]) for p in cfg["niche"]["pillars"]},
                "topic_terms": [], "boost_terms": []}
    for p in cfg["niche"]["pillars"]:
        p.pop("keywords", None)
    cfg.setdefault("hashtags", pr.get("hashtags", {}))
    cfg.setdefault("voice", {}).setdefault("banned_phrases", BANNED)
    src = load_sources()
    drop = cfg.pop("drop_regional", [])
    if not src and pr.get("sources_file") and cfg.pop("use_preset_sources", True):
        src = json.load(open(os.path.join(PRESETS, pr["sources_file"])))
        for region in drop:
            names = pr.get("regional", {}).get(region, [])
            src = [x for x in src if x["name"] not in names]
    cfg.pop("use_preset_sources", None)
    cfg["config_version"] = CONFIG_VERSION
    extra = [(s["url"], s.get("category", ""), s.get("why", "")) for s in cfg.pop("add_sources", [])]
    return cfg, terr, src, extra


def merge_defaults(cur, dflt):
    """Add keys that exist in the example config but not in yours (recursively). Never changes your values."""
    added = []
    for k, v in dflt.items():
        if k.startswith("_"):
            continue
        if k not in cur:
            cur[k] = v
            added.append(k)
        elif isinstance(v, dict) and isinstance(cur[k], dict):
            added += [f"{k}.{x}" for x in merge_defaults(cur[k], v)]
    return added


def migrate():
    if not os.path.exists(CONFIG):
        sys.exit("No engine.config.json yet — run python3 setup/init.py first.")
    cur = json.load(open(CONFIG))
    dflt = json.load(open(EXAMPLE))
    # personal fields stay yours: don't copy the example's people, handles, prompts or competitors
    for k in ("brand", "author"):
        dflt.pop(k, None)
    dflt.get("niche", {}).pop("pillars", None)
    dflt.pop("ai_visibility", None)
    dflt.setdefault("ai_visibility", {"prompts": [], "competitors": []})
    added = merge_defaults(cur, dflt)
    cur["config_version"] = CONFIG_VERSION
    json.dump(cur, open(CONFIG, "w"), indent=2, ensure_ascii=False)
    print("Added settings:", ", ".join(added) if added else "none (already up to date)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--migrate", action="store_true")
    ap.add_argument("--preset")
    ap.add_argument("--answers")
    ap.add_argument("--list-presets", action="store_true")
    a = ap.parse_args()
    if a.migrate:
        migrate()
        return
    if a.list_presets:
        for k, v in presets().items():
            print(f"{k:22} {v['label']} — {len(v['pillars'])} pillars" + (f", {len(json.load(open(os.path.join(PRESETS, v['sources_file']))))} sources" if v.get("sources_file") else ""))
        return
    if a.answers:
        write_all(*from_answers(a.answers))
        return
    cur = json.load(open(CONFIG)) if os.path.exists(CONFIG) else json.load(open(EXAMPLE))
    if not os.path.exists(CONFIG):
        for k in ("brand", "author"):
            cur[k] = {kk: ("" if isinstance(vv, str) else vv) for kk, vv in cur[k].items()}
        cur["brand"]["handles"] = {}
        cur["author"]["confidential"] = []
        cur["niche"] = {}
        cur["hashtags"] = {}
        cur["cadence"]["timezone"] = "UTC"
        cur["ai_visibility"] = {"prompts": [], "competitors": []}
    cur.pop("_readme", None)
    try:
        write_all(*interview(cur, a.preset))
    except (KeyboardInterrupt, EOFError):
        print("\nStopped — nothing written.")
        return
    print("\nNext: python3 brand/scripts/make_brand.py  (brand kit) · then follow docs/SETUP.md from step 3.")


if __name__ == "__main__":
    main()
