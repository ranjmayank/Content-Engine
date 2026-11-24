#!/usr/bin/env python3
"""
SEO + AI-search site audit — free, no API keys, standard library only.

Crawls your site the way a search engine does (respecting robots.txt), checks every page for
technical, on-page and AI-search problems, and writes a ranked fix list.

Usage:
  python3 seo-audit/audit.py                         # audits brand.site from engine.config.json
  python3 seo-audit/audit.py --site https://example.com --max-pages 300
  python3 seo-audit/audit.py --psi                   # + Google PageSpeed (Core Web Vitals) for the top pages
                                                     #   (works without a key at low volume; set PSI_API_KEY for more)
Options:
  --max-pages N    stop after N pages (default from config seo_audit.max_pages, else 200)
  --delay S        seconds between requests (default 0.5 — be polite to your own server)
  --exclude PATH   skip URLs containing PATH (repeatable), e.g. --exclude /tag/ --exclude ?replytocom
  --out DIR        where reports go (default seo-audit/reports)

Writes:
  seo-audit/reports/YYYY-MM-DD.md   readable report: score, what changed since last run, issues by priority
  seo-audit/reports/latest.md       same, always the newest
  seo-audit/reports/latest.json     machine-readable (the seo-audit Claude skill reads this)
  seo-audit/reports/pages.csv       one row per crawled URL
  seo-audit/reports/issues.csv      one row per issue × URL

Issue set and thresholds adapted from OpenSEO (MIT) — see seo-audit/issues.py.
"""
import argparse
import csv
import datetime as dt
import gzip
import hashlib
import html as htmllib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from issues import CRAWLERS, ISSUES, SEVERITY_WEIGHT, THRESHOLDS  # noqa: E402

UA_TOKEN = "ContentEngine-Audit"
UA = f"Mozilla/5.0 (compatible; {UA_TOKEN}/1.0; +https://github.com/ranjmayank/Content-Engine)"
TIMEOUT = 20
SKIP_EXT = re.compile(r"\.(jpe?g|png|gif|webp|avif|svg|ico|pdf|zip|gz|mp4|mp3|webm|mov|css|js|json|xml|txt|woff2?|ttf|eot|docx?|xlsx?|pptx?)(\?|$)", re.I)


# ---------------------------------------------------------------- HTTP

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


_opener = urllib.request.build_opener(_NoRedirect)


def get(url, max_bytes=3_000_000):
    """One request, no redirect following. Returns dict(status, headers, body, ms, error)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    t0 = time.time()
    try:
        r = _opener.open(req, timeout=TIMEOUT)
        status, headers, body = r.status, r.headers, r.read(max_bytes)
    except urllib.error.HTTPError as e:
        status, headers = e.code, e.headers
        try:
            body = e.read(max_bytes)
        except Exception:
            body = b""
    except Exception as e:
        return {"status": 0, "headers": {}, "body": b"", "ms": int((time.time() - t0) * 1000), "error": f"{type(e).__name__}: {e}"[:160]}
    ms = int((time.time() - t0) * 1000)
    if body[:2] == b"\x1f\x8b":
        try:
            body = gzip.GzipFile(fileobj=io.BytesIO(body)).read()
        except Exception:
            pass
    return {"status": status, "headers": headers, "body": body, "ms": ms, "error": ""}


def follow(url, max_hops=10):
    """Follow redirects by hand. Returns (final_response, chain[list of (url, status)], loop?)."""
    chain, seen, cur = [], set(), url
    for _ in range(max_hops):
        r = get(cur)
        chain.append((cur, r["status"]))
        if r["status"] in (301, 302, 303, 307, 308) and r["headers"].get("Location"):
            nxt = urllib.parse.urljoin(cur, r["headers"]["Location"])
            if nxt in seen or nxt == cur:
                return r, chain, True
            seen.add(cur)
            cur = nxt
            continue
        return r, chain, False
    return r, chain, True


def norm(url):
    """Normalise for de-duplication: drop fragments, default ports, trailing ? ."""
    p = urllib.parse.urlsplit(url)
    netloc = p.netloc.lower().replace(":80", "") if p.scheme == "http" else p.netloc.lower().replace(":443", "")
    path = p.path or "/"
    return urllib.parse.urlunsplit((p.scheme.lower(), netloc, path, p.query, ""))


def host_of(url):
    return urllib.parse.urlsplit(url).netloc.lower()


def bare(host):
    return host[4:] if host.startswith("www.") else host


# ---------------------------------------------------------------- HTML

class PageParser(HTMLParser):
    SKIP_TEXT = {"script", "style", "noscript", "svg", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self._in_title = "", False
        self.meta, self.links, self.canonicals = {}, [], []
        self.headings, self.images, self.jsonld = [], [], []
        self.hreflang, self.resources = [], []
        self.lang = None
        self.text, self._skip, self._in_jsonld, self._buf = [], 0, False, []
        self.app_container = False
        self._h = None

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang") or None
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or a.get("http-equiv") or "").lower()
            if key:
                self.meta.setdefault(key, a.get("content", "").strip())
        elif tag == "link":
            rel = a.get("rel", "").lower().split()
            if "canonical" in rel:
                self.canonicals.append(a.get("href", ""))
            if "alternate" in rel and a.get("hreflang"):
                self.hreflang.append((a["hreflang"], a.get("href", "")))
            if "stylesheet" in rel and a.get("href"):
                self.resources.append(a["href"])
        elif tag == "a" and a.get("href"):
            self.links.append((a["href"], a.get("rel", "").lower()))
        elif tag == "img":
            self.images.append(a.get("alt"))
            if a.get("src"):
                self.resources.append(a["src"])
        elif tag in ("script", "iframe") and a.get("src"):
            self.resources.append(a["src"])
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))
        elif tag == "div" and (a.get("id") in ("root", "app", "__next", "__nuxt", "svelte") or "data-reactroot" in a):
            self.app_container = True
        if tag == "script" and "ld+json" in a.get("type", "").lower():
            self._in_jsonld, self._buf = True, []
        if tag in self.SKIP_TEXT:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._buf))
            self._in_jsonld = False
        if tag in self.SKIP_TEXT and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_jsonld:
            self._buf.append(data)
        elif not self._skip:
            self.text.append(data)


def schema_types(blocks):
    """(types found, parse_errors, article objects)."""
    types, errors, articles = set(), 0, []

    def walk(o):
        if isinstance(o, dict):
            t = o.get("@type")
            for x in (t if isinstance(t, list) else [t]):
                if isinstance(x, str):
                    types.add(x)
                    if x in ("Article", "BlogPosting", "NewsArticle", "TechArticle"):
                        articles.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for b in blocks:
        try:
            walk(json.loads(b.strip()))
        except Exception:
            errors += 1
    return types, errors, articles


# ---------------------------------------------------------------- site-level

def read_robots(base):
    r = get(urllib.parse.urljoin(base, "/robots.txt"), max_bytes=500_000)
    if r["status"] != 200 or not r["body"]:
        return None, "", []
    text = r["body"].decode("utf-8", "replace")
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(text.splitlines())
    sitemaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", text)
    return rp, text, sitemaps


def sitemap_urls(url, depth=0, limit=5000):
    """All <loc> URLs in a sitemap or sitemap index (follows children, one level)."""
    r, _, _ = follow(url)
    if r["status"] != 200 or not r["body"]:
        return None
    try:
        root = ET.fromstring(r["body"])
    except ET.ParseError:
        return []
    tag = root.tag.split("}")[-1].lower()
    locs = [el.text.strip() for el in root.iter() if el.tag.split("}")[-1].lower() == "loc" and el.text]
    if tag == "sitemapindex" and depth == 0:
        out = []
        for child in locs[:50]:
            out += sitemap_urls(child, 1, limit) or []
            if len(out) >= limit:
                break
        return out[:limit]
    return locs[:limit]


def crawler_access(rp, base):
    """{bot: allowed?} for the home page and a typical deep path."""
    if rp is None:
        return {}
    out = {}
    for group in CRAWLERS.values():
        for bot in group:
            out[bot] = rp.can_fetch(bot, base) and rp.can_fetch(bot, urllib.parse.urljoin(base, "/blog/example-post/"))
    return out


def pagespeed(url, key=None):
    q = {"url": url, "strategy": "mobile", "category": "performance"}
    if key:
        q["key"] = key
    api = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?" + urllib.parse.urlencode(q)
    try:
        with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": UA}), timeout=90) as r:
            d = json.load(r)
    except Exception as e:
        return {"url": url, "error": f"{type(e).__name__}"}
    lh = d.get("lighthouseResult", {})
    au = lh.get("audits", {})
    field = d.get("loadingExperience", {}).get("metrics", {})

    def num(k):
        return au.get(k, {}).get("displayValue", "")

    return {"url": url, "score": round((lh.get("categories", {}).get("performance", {}).get("score") or 0) * 100),
            "lcp": num("largest-contentful-paint"), "cls": num("cumulative-layout-shift"), "tbt": num("total-blocking-time"),
            "field_lcp_ms": field.get("LARGEST_CONTENTFUL_PAINT_MS", {}).get("percentile"),
            "field_inp_ms": field.get("INTERACTION_TO_NEXT_PAINT", {}).get("percentile"),
            "field_cls": field.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", {}).get("percentile")}


# ---------------------------------------------------------------- the audit

def audit(start, max_pages=200, delay=0.5, exclude=(), use_psi=False, log=print):
    found = defaultdict(set)          # issue -> set(urls)   ("(site)" for site-wide issues)
    details = defaultdict(dict)        # issue -> url -> detail text
    pages = {}                         # url -> row
    site = {"start": start, "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}

    def flag(issue, url="(site)", detail=""):
        found[issue].add(url)
        if detail:
            details[issue][url] = detail[:200]

    # 1) start URL and host
    r, chain, loop = follow(start)
    if r["status"] == 0 or r["status"] >= 400 and r["status"] not in (403, 429):
        flag("site-unreachable", start, r["error"] or f"HTTP {r['status']}")
        return finish(site, pages, found, details, [])
    home = chain[-1][0]
    base = urllib.parse.urlunsplit(urllib.parse.urlsplit(home)[:2] + ("/", "", ""))
    host = host_of(home)
    site.update({"home": home, "host": host})
    if not home.startswith("https://"):
        flag("no-https")
    else:
        hr, hchain, _ = follow("http://" + host + "/")
        if not hchain[-1][0].startswith("https://"):
            flag("http-not-redirected", "http://" + host + "/")
    alt = ("www." + host) if not host.startswith("www.") else host[4:]
    ar, achain, _ = follow(urllib.parse.urlsplit(home).scheme + "://" + alt + "/")
    if ar["status"] == 200 and host_of(achain[-1][0]) == alt:
        flag("host-not-consolidated", alt)

    # 2) robots.txt, crawler access, llms.txt, sitemap, soft-404
    rp, robots_text, sm_listed = read_robots(base)
    site["robots_txt"] = bool(rp)
    if rp is None:
        flag("no-robots-txt")
    access = crawler_access(rp, base)
    site["crawler_access"] = access
    blocked = {k: [b for b in v if access.get(b) is False] for k, v in CRAWLERS.items()}
    if blocked["search"]:
        flag("search-engine-blocked", detail=", ".join(blocked["search"]))
    if blocked["ai_search"]:
        flag("ai-search-blocked", detail=", ".join(blocked["ai_search"]))
    if blocked["ai_training"]:
        flag("ai-training-blocked", detail=", ".join(blocked["ai_training"]))
    lr = get(urllib.parse.urljoin(base, "/llms.txt"), max_bytes=200_000)
    site["llms_txt"] = lr["status"] == 200 and b"<html" not in lr["body"][:500].lower()
    if not site["llms_txt"]:
        flag("no-llms-txt")
    sm_candidates = sm_listed or [urllib.parse.urljoin(base, p) for p in ("/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml")]
    in_sitemap = []
    for sm in sm_candidates:
        urls = sitemap_urls(sm)
        if urls:
            site.setdefault("sitemaps", []).append(sm)
            in_sitemap += urls
    in_sitemap = [norm(u) for u in dict.fromkeys(in_sitemap) if bare(host_of(u)) == bare(host)]
    site["sitemap_urls"] = len(in_sitemap)
    if not in_sitemap:
        flag("no-sitemap")
    junk = urllib.parse.urljoin(base, f"/this-page-should-not-exist-{int(time.time())}/")
    jr, _, _ = follow(junk)
    if jr["status"] == 200:
        flag("soft-404", junk)

    # 3) crawl: home first, then links, then sitemap URLs nothing linked to
    queue = deque([(norm(home), 0)])
    queued = {norm(home)}
    inlinks = defaultdict(set)
    link_targets = defaultdict(set)    # target -> pages linking to it
    titles, descs, bodies = defaultdict(list), defaultdict(list), defaultdict(list)

    def allowed(u):
        if bare(host_of(u)) != bare(host) or SKIP_EXT.search(urllib.parse.urlsplit(u).path):
            return False
        if any(x in u for x in exclude):
            return False
        return rp is None or rp.can_fetch(UA_TOKEN, u)

    def enqueue_sitemap():
        for u in in_sitemap:
            if u not in queued and allowed(u):
                queued.add(u)
                queue.append((u, 99))

    sitemap_added = False
    while len(pages) < max_pages:
        if not queue:
            if sitemap_added:
                break
            enqueue_sitemap()      # sitemap URLs nothing linked to (orphans) are checked last
            sitemap_added = True
            continue
        url, depth = queue.popleft()
        time.sleep(delay)
        r, chain, loop = follow(url)
        final = norm(chain[-1][0])
        row = {"url": url, "status": chain[0][1], "final_url": final if final != url else "", "final_status": r["status"],
               "hops": len(chain) - 1, "ms": r["ms"], "depth": depth if depth != 99 else "", "title": "", "words": 0,
               "h1": 0, "indexable": False, "in_sitemap": url in in_sitemap, "schema": ""}
        pages[url] = row
        if loop:
            flag("redirect-loop", url)
        elif len(chain) > 2:
            flag("redirect-chain", url, " → ".join(c[0] for c in chain))
        st = r["status"]
        if st in (401, 403) or (st == 503 and b"challenge" in r["body"][:5000].lower()):
            flag("blocked-page", url, f"HTTP {st}")
            continue
        if st == 429:
            flag("rate-limited-page", url)
            continue
        if st >= 500 or st == 0:
            flag("server-error", url, r["error"] or f"HTTP {st}")
            continue
        if st >= 400:
            flag("client-error", url, f"HTTP {st}")
            continue
        ctype = (r["headers"].get("Content-Type") or "") if r["headers"] else ""
        if "html" not in ctype.lower():
            continue
        if final != url and bare(host_of(final)) != bare(host):
            continue
        if r["ms"] > THRESHOLDS["slow_ms"]:
            flag("slow-response", url, f"{r['ms']} ms")
        if len(r["body"]) > THRESHOLDS["html_max_kb"] * 1024:
            flag("html-too-large", url, f"{len(r['body']) // 1024} KB")

        page = r["body"].decode("utf-8", "replace")
        p = PageParser()
        try:
            p.feed(page)
        except Exception:
            pass
        text = re.sub(r"\s+", " ", " ".join(p.text)).strip()
        words = len(text.split())
        title = htmllib.unescape(p.title).strip()
        desc = p.meta.get("description", "")
        robots = (p.meta.get("robots", "") + " " + (r["headers"].get("X-Robots-Tag") or "")).lower()
        noindex = "noindex" in robots
        canon = [urllib.parse.urljoin(final, c) for c in p.canonicals if c]
        canonical_other = bool(canon) and norm(canon[0]) != final
        types, jerr, articles = schema_types(p.jsonld)
        h1 = p.headings.count(1)
        row.update({"title": title[:120], "words": words, "h1": h1, "schema": " ".join(sorted(types)),
                    "indexable": not noindex and not canonical_other, "canonical": canon[0] if canon else "",
                    "noindex": noindex})

        if noindex:
            flag("noindex", final)
        if len(set(canon)) > 1:
            flag("canonical-conflict", final, "several canonical tags")
        elif canonical_other:
            flag("canonicalized", final, canon[0])
        if not title:
            flag("missing-title", final)
        else:
            if len(title) > THRESHOLDS["title_max"]:
                flag("title-too-long", final, f"{len(title)} chars")
            elif len(title) < THRESHOLDS["title_min"]:
                flag("title-too-short", final, title)
            if row["indexable"]:
                titles[title.lower()].append(final)
        if not desc:
            flag("missing-description", final)
        else:
            if len(desc) > THRESHOLDS["desc_max"]:
                flag("description-too-long", final, f"{len(desc)} chars")
            elif len(desc) < THRESHOLDS["desc_min"]:
                flag("description-too-short", final, f"{len(desc)} chars")
            if row["indexable"]:
                descs[desc.lower()].append(final)
        if h1 == 0:
            flag("missing-h1", final)
        elif h1 > 1:
            flag("multiple-h1", final, f"{h1} H1s")
        prev = 0
        for lvl in p.headings:
            if prev and lvl > prev + 1:
                flag("heading-skip", final, f"H{prev} → H{lvl}")
                break
            prev = lvl
        if p.app_container and words < 80 and not p.headings:
            flag("javascript-rendering-suspected", final)
        elif words < THRESHOLDS["thin_words"] and row["indexable"]:
            flag("thin-content", final, f"{words} words")
        if words >= THRESHOLDS["thin_words"] and row["indexable"]:
            bodies[hashlib.md5(text.lower().encode()).hexdigest()].append(final)
        missing_alt = sum(1 for a in p.images if a is None)
        if missing_alt:
            flag("images-missing-alt", final, f"{missing_alt} image(s)")
        if not p.lang:
            flag("missing-lang", final)
        if "viewport" not in p.meta:
            flag("missing-viewport", final)
        if not (p.meta.get("og:title") and p.meta.get("og:image")):
            flag("missing-og", final)
        if final.startswith("https://") and any(x.startswith("http://") for x in p.resources):
            flag("mixed-content", final, next(x for x in p.resources if x.startswith("http://")))
        if jerr:
            flag("invalid-structured-data", final, f"{jerr} block(s)")
        if not types and row["indexable"]:
            flag("no-structured-data", final)
        for art in articles[:1]:
            if not (art.get("datePublished") or art.get("dateModified")):
                flag("article-missing-dates", final)
            if not art.get("author"):
                flag("article-missing-author", final)

        # links
        out_internal = 0
        for href, rel in p.links:
            if href.startswith(("mailto:", "tel:", "javascript:", "#")):
                continue
            tgt = norm(urllib.parse.urljoin(final, href))
            if not tgt.startswith("http") or bare(host_of(tgt)) != bare(host):
                continue
            if tgt != final:
                out_internal += 1
                inlinks[tgt].add(final)
                link_targets[tgt].add(final)
            if tgt not in queued and allowed(tgt) and depth != 99:
                queued.add(tgt)
                queue.append((tgt, depth + 1))
        row["internal_links_out"] = out_internal
        if out_internal == 0 and row["indexable"]:
            flag("no-outgoing-links", final)
        if depth != 99 and depth >= THRESHOLDS["deep_depth"]:
            flag("deep-page", final, f"depth {depth}")

        if len(pages) % 25 == 0:
            log(f"  … {len(pages)} pages")

    site["pages_crawled"] = len(pages)
    site["stopped_at_limit"] = len(pages) >= max_pages and bool(queue)

    # 4) cross-page checks
    for t, urls in titles.items():
        if len(urls) > 1:
            for u in urls:
                flag("duplicate-title", u, f"shared by {len(urls)} pages")
    for d_, urls in descs.items():
        if len(urls) > 1:
            for u in urls:
                flag("duplicate-description", u, f"shared by {len(urls)} pages")
    for h, urls in bodies.items():
        if len(urls) > 1:
            for u in urls:
                flag("duplicate-content", u, "same text as " + ", ".join(x for x in urls if x != u)[:150])
    for tgt, srcs in link_targets.items():
        row = pages.get(tgt)
        if not row:
            continue
        if row["status"] >= 400 or row["status"] == 0:
            for s in list(srcs)[:20]:
                flag("broken-internal-link", s, f"→ {tgt} ({row['status']})")
        elif row["hops"]:
            flag("internal-redirect-link", tgt, f"linked from {len(srcs)} page(s)")
    for u in in_sitemap:
        row = pages.get(u)
        if not row:
            continue
        if row["status"] != 200 or row.get("noindex") or (row.get("canonical") and norm(row["canonical"]) != u):
            flag("sitemap-non-indexable", u, f"HTTP {row['status']}" + (" · noindex" if row.get("noindex") else "")
                 + (" · canonical elsewhere" if row.get("canonical") and norm(row["canonical"]) != u else ""))
        elif u not in inlinks and u != norm(home):
            flag("orphan-page", u)
    for u, row in pages.items():
        can = row.get("canonical")
        if can and norm(can) != u and norm(can) in pages and pages[norm(can)]["status"] != 200:
            flag("canonical-conflict", u, f"canonical → {can} ({pages[norm(can)]['status']})")

    psi = []
    if use_psi:
        key = os.environ.get("PSI_API_KEY")
        ranked = sorted((u for u, r in pages.items() if r.get("indexable")), key=lambda u: -len(inlinks.get(u, ())))[:5]
        for u in ranked:
            log(f"  PageSpeed {u}")
            psi.append(pagespeed(u, key))
    return finish(site, pages, found, details, psi)


def finish(site, pages, found, details, psi):
    n = max(1, len(pages))
    issues, score = [], 100.0
    if "site-unreachable" in found:
        score = 0.0
    for key, urls in found.items():
        sev, title, why, fix = ISSUES[key]
        sitewide = urls == {"(site)"} or key in ("no-https", "http-not-redirected", "host-not-consolidated", "soft-404")
        share = 1.0 if sitewide else min(1.0, len(urls) / n)
        penalty = SEVERITY_WEIGHT[sev] * (0.5 + 0.5 * share)
        score -= penalty
        issues.append({"id": key, "severity": sev, "title": title, "count": len(urls), "sitewide": sitewide,
                       "why": why, "fix": fix, "penalty": round(penalty, 1),
                       "urls": sorted(urls)[:200], "details": details.get(key, {})})
    order = {"critical": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda i: (order[i["severity"]], -i["penalty"], -i["count"]))
    return {"site": site, "score": max(0, round(score)), "issues": issues, "pages": list(pages.values()), "pagespeed": psi}


# ---------------------------------------------------------------- reports

def grade(s):
    return "A" if s >= 90 else "B" if s >= 75 else "C" if s >= 60 else "D" if s >= 40 else "F"


def write_reports(res, out, site_name):
    os.makedirs(out, exist_ok=True)
    today = dt.date.today().isoformat()
    prev_path = os.path.join(out, "latest.json")
    prev = None
    if os.path.exists(prev_path):
        try:
            prev = json.load(open(prev_path))
        except Exception:
            prev = None
    s = res["site"]
    L = [f"# {site_name} — SEO & AI-search audit, {today}", "",
         f"**Score: {res['score']}/100 ({grade(res['score'])})** · {s.get('pages_crawled', 0)} pages crawled"
         + (" (stopped at the page limit — raise --max-pages for a full crawl)" if s.get("stopped_at_limit") else "")
         + f" · {s.get('sitemap_urls', 0)} URLs in the sitemap", ""]
    if prev:
        before = {i["id"]: i["count"] for i in prev.get("issues", [])}
        now = {i["id"]: i["count"] for i in res["issues"]}
        new = [ISSUES[k][1] for k in now if k not in before]
        fixed = [ISSUES[k][1] for k in before if k not in now and k in ISSUES]
        L += [f"**Since the last audit ({prev['site'].get('checked_at', '')[:10]}):** score {prev.get('score')} → {res['score']}"
              + (f" · new: {', '.join(new)}" if new else "") + (f" · fixed: {', '.join(fixed)}" if fixed else ""), ""]
    acc = s.get("crawler_access") or {}
    if acc:
        def row(group):
            return " · ".join(f"{b} {'✅' if acc.get(b) else '⛔'}" for b in CRAWLERS[group])
        L += ["## Who can read your site", "",
              f"- **Search engines:** {row('search')}",
              f"- **AI search & answers** (what gets you cited): {row('ai_search')}",
              f"- **AI training** (optional to allow): {row('ai_training')}",
              f"- **llms.txt:** {'✅ found' if s.get('llms_txt') else '— not found (optional)'} · "
              f"**Sitemap:** {', '.join(s.get('sitemaps', [])) or '— not found'}", ""]
    crit = [i for i in res["issues"] if i["severity"] == "critical"]
    warn = [i for i in res["issues"] if i["severity"] == "warning"]
    info = [i for i in res["issues"] if i["severity"] == "info"]
    top = (crit + warn)[:5]
    L += ["## Fix these first", ""]
    if not top:
        L += ["Nothing critical or urgent. 🎉 See the notes below for polish.", ""]
    for k, i in enumerate(top, 1):
        where = "site-wide" if i["sitewide"] else f"{i['count']} page(s)"
        L += [f"{k}. **{i['title']}** ({i['severity']}, {where}) — {i['fix']}"]
    L.append("")
    for label, group in (("Critical", crit), ("Warnings", warn), ("Notes", info)):
        if not group:
            continue
        L += [f"## {label}", ""]
        for i in group:
            L += [f"### {i['title']} — {('site-wide' if i['sitewide'] else str(i['count']) + ' page(s)')}", "",
                  f"**Why it matters:** {i['why']}", "", f"**How to fix:** {i['fix']}", ""]
            shown = [u for u in i["urls"] if u != "(site)"][:10]
            for u in shown:
                d = i["details"].get(u, "")
                L.append(f"- {u}" + (f" — {d}" if d else ""))
            if i["details"].get("(site)"):
                L.append(f"- {i['details']['(site)']}")
            if i["count"] > len(shown) and shown:
                L.append(f"- … and {i['count'] - len(shown)} more (see issues.csv)")
            L.append("")
    if res.get("pagespeed"):
        L += ["## Speed (Google PageSpeed, mobile)", "", "| Page | Score | LCP | CLS | TBT | Real-user LCP / INP |", "|---|---|---|---|---|---|"]
        for p in res["pagespeed"]:
            if p.get("error"):
                L.append(f"| {p['url']} | — | — | — | — | {p['error']} |")
            else:
                L.append(f"| {p['url']} | {p['score']} | {p['lcp']} | {p['cls']} | {p['tbt']} | "
                         f"{p.get('field_lcp_ms') or '—'} ms / {p.get('field_inp_ms') or '—'} ms |")
        L.append("")
    L += ["---", "_Built by seo-audit/audit.py (Content Engine). Issue set and thresholds adapted from OpenSEO (MIT). "
          "This is a crawl of the HTML your server returns; it doesn't run JavaScript. For backlinks, rankings and AI-visibility "
          "tracking, use the OpenSEO skill (`.claude/skills/openseo-audit`)._"]
    md = "\n".join(L)
    for p in (os.path.join(out, f"{today}.md"), os.path.join(out, "latest.md")):
        open(p, "w").write(md)
    json.dump(res, open(prev_path, "w"), indent=1, default=str)
    cols = ["url", "status", "final_url", "final_status", "hops", "ms", "depth", "in_sitemap", "indexable", "title", "words", "h1",
            "internal_links_out", "canonical", "schema"]
    with open(os.path.join(out, "pages.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(res["pages"])
    with open(os.path.join(out, "issues.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["severity", "issue", "url", "detail", "how_to_fix"])
        for i in res["issues"]:
            for u in i["urls"]:
                w.writerow([i["severity"], i["title"], u, i["details"].get(u, ""), i["fix"]])
    return md


def main():
    try:
        cfg = json.load(open(os.path.join(ROOT, "engine.config.json")))
    except Exception:
        cfg = {}
    sa = cfg.get("seo_audit", {})
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--site", default=os.environ.get("AUDIT_SITE") or cfg.get("brand", {}).get("site"))
    ap.add_argument("--max-pages", type=int, default=int(os.environ.get("AUDIT_MAX_PAGES") or sa.get("max_pages", 200)))
    ap.add_argument("--delay", type=float, default=float(sa.get("delay", 0.5)))
    ap.add_argument("--exclude", action="append", default=list(sa.get("exclude", [])))
    ap.add_argument("--psi", action="store_true", default=bool(sa.get("pagespeed", False)))
    ap.add_argument("--out", default=os.path.join(HERE, "reports"))
    a = ap.parse_args()
    if not a.site:
        sys.exit("No site to audit. Pass --site https://your-site.com or set brand.site in engine.config.json.")
    site = a.site if a.site.startswith("http") else "https://" + a.site
    print(f"Auditing {site} (up to {a.max_pages} pages)…")
    res = audit(site, a.max_pages, a.delay, a.exclude, a.psi)
    name = cfg.get("brand", {}).get("site_name") or host_of(site)
    write_reports(res, a.out, name)
    c = sum(1 for i in res["issues"] if i["severity"] == "critical")
    print(f"Score {res['score']}/100 · {len(res['pages'])} pages · {len(res['issues'])} issue types ({c} critical) → {a.out}/latest.md")


if __name__ == "__main__":
    main()
