#!/usr/bin/env python3
"""Find the RSS/Atom feed (or sitemap) for a website and add it to scanner/sources/sources.json.

Usage:
  python3 setup/discover_feed.py https://example.com/blog                # print what it finds
  python3 setup/discover_feed.py https://example.com --add --category "SEO" --why "Weekly SEO news"
  python3 setup/discover_feed.py --file my-sites.txt --add               # one URL per line (optional: url | category | why)

How it looks: <link rel="alternate" type="application/rss+xml"> on the page, then common feed paths
(/feed, /rss, /rss.xml, /atom.xml, /feed.xml, /index.xml, /blog/feed), then the sitemap.
If nothing works it adds the site as "manual" so it still appears in SOURCES.md as a site to check by hand.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = os.path.join(ROOT, "scanner", "sources", "sources.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ContentEngineFeedFinder/1.0; +https://github.com/ranjmayank/Content-Engine)"}
PATHS = ["/feed", "/feed/", "/rss", "/rss.xml", "/atom.xml", "/feed.xml", "/index.xml", "/blog/feed", "/blog/rss.xml", "/news/rss"]


def fetch(url, n=1_500_000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.geturl(), r.headers.get("Content-Type", ""), r.read(n)


def kind(data):
    """'rss' for RSS/Atom with items, 'sitemap' for a sitemap, else None."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return None
    tag = root.tag.split("}")[-1].lower()
    if tag in ("rss", "feed", "rdf"):
        return "rss"
    if tag in ("urlset", "sitemapindex"):
        return "sitemap"
    return None


def discover(site):
    if not site.startswith("http"):
        site = "https://" + site
    tried = []
    try:
        final, ctype, body = fetch(site)
        html = body.decode("utf-8", "replace")
        if kind(body) == "rss":
            return {"type": "rss", "url": final, "site": site}
        for m in re.finditer(r"<link[^>]+>", html, re.I):
            tag = m.group(0)
            if re.search(r"application/(rss|atom)\+xml", tag, re.I):
                href = re.search(r'href=["\']([^"\']+)', tag, re.I)
                if href:
                    tried.append(urllib.parse.urljoin(final, href.group(1)))
        name = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        title = re.sub(r"\s+", " ", name.group(1)).strip()[:80] if name else ""
    except Exception as e:
        final, title = site, ""
        print(f"  couldn't open {site}: {type(e).__name__}", file=sys.stderr)
    base = urllib.parse.urlunsplit(urllib.parse.urlsplit(final)[:2] + ("", "", ""))
    path = urllib.parse.urlsplit(final).path.rstrip("/")
    tried += [final.rstrip("/") + p for p in PATHS if path] + [base + p for p in PATHS]
    for u in dict.fromkeys(tried):
        try:
            _, _, data = fetch(u)
            if kind(data) == "rss":
                return {"type": "rss", "url": u, "site": site, "title": title}
        except Exception:
            continue
    for u in (base + "/sitemap.xml", base + "/sitemap_index.xml", base + "/wp-sitemap.xml"):
        try:
            _, _, data = fetch(u)
            if kind(data) == "sitemap":
                out = {"type": "sitemap", "url": u, "site": site, "title": title}
                if path:
                    out["include"] = path + "/"
                return out
        except Exception:
            continue
    return {"type": "manual", "url": site, "site": site, "title": title}


def add(entries):
    os.makedirs(os.path.dirname(SOURCES), exist_ok=True)
    cur = json.load(open(SOURCES)) if os.path.exists(SOURCES) else []
    have = {s["url"] for s in cur}
    n = 0
    for e in entries:
        if e["url"] in have:
            print(f"  already listed: {e['url']}")
            continue
        cur.append(e)
        have.add(e["url"])
        n += 1
    json.dump(cur, open(SOURCES, "w"), indent=2, ensure_ascii=False)
    print(f"Added {n} source(s) → scanner/sources/sources.json ({len(cur)} in total)")


def entry(site, category, why):
    f = discover(site)
    name = f.pop("title", "") or urllib.parse.urlsplit(f["site"]).netloc.replace("www.", "")
    e = {"name": name, "category": category or "General", "why": why or "", **f}
    label = {"rss": "feed", "sitemap": "sitemap", "manual": "no feed found — added as check-by-hand"}[e["type"]]
    print(f"  {site} → {label}: {e['url']}")
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--file", help="text file, one URL per line: url | category | why")
    ap.add_argument("--category", default="")
    ap.add_argument("--why", default="")
    ap.add_argument("--add", action="store_true", help="write to scanner/sources/sources.json")
    a = ap.parse_args()
    rows = [(u, a.category, a.why) for u in a.urls]
    if a.file:
        for line in open(a.file):
            line = line.strip()
            if line and not line.startswith("#"):
                parts = [p.strip() for p in line.split("|")] + ["", ""]
                rows.append((parts[0], parts[1] or a.category, parts[2] or a.why))
    if not rows:
        ap.error("give at least one URL or --file")
    found = [entry(*r) for r in rows]
    if a.add:
        add(found)
    else:
        print(json.dumps(found, indent=2))


if __name__ == "__main__":
    main()
