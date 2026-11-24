#!/usr/bin/env python3
"""
Fuel Scanner — daily news discovery for your niche.
Pillars (territories) come from scanner/sources/territories.json; brand details from engine.config.json.
Scans each source's sitemap.xml or RSS/Atom feed, diffs against previously
seen URLs, and writes a daily digest of NEW posts + appends to a CSV inbox.

Usage:
  python3 fuel_scanner.py --config sources --init   # first run: record everything, report the last 2 days
  python3 fuel_scanner.py                 # daily run: report only what's new
  python3 fuel_scanner.py --backfill 3    # also re-report items dated in the last 3 days
Files (all live in the --config folder, default scanner/sources/):
  sources.json     — your source list (add a line any day)
  seen_urls.json   — state (auto-managed)
  digests/         — one markdown digest per day
  fuel_inbox.csv   — running inbox, one row per link, tagged by territory
  notion_pushed.json — links already sent to Notion (auto-managed)

Each new item gets a source card (the article's summary, numbers, a quote) and
territory tags. The digest leads with "Top picks"; only those go to Notion.
"""
import json, csv, gzip, io, os, re, sys, argparse, email.utils
import datetime as dt
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_CONFIG = os.path.join(HERE, "sources")
SOURCES = os.path.join(HERE, "sources.json")
STATE = os.path.join(HERE, "seen_urls.json")
DIGESTS = os.path.join(HERE, "digests")
INBOX = os.path.join(HERE, "fuel_inbox.csv")
PUSHED = os.path.join(HERE, "notion_pushed.json")   # links already sent to Notion

def _site_url():
    try:
        with open(os.path.join(ROOT, "engine.config.json")) as f:
            return json.load(f).get("brand", {}).get("site", "") or "https://github.com/ranjmayank/Content-Engine"
    except Exception:
        return "https://github.com/ranjmayank/Content-Engine"

UA = {"User-Agent": f"Mozilla/5.0 (compatible; ContentEngineFuelScanner/1.0; +{_site_url()})"}
MAX_NEW_PER_SOURCE = 12          # cap per source per day (anti-flood)
SITEMAP_RECENT_DAYS = 7          # sitemap URLs older than this (by lastmod) are ignored
TIMEOUT = 20

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = r.read()
    if url.endswith(".gz") or data[:2] == b"\x1f\x8b":
        data = gzip.GzipFile(fileobj=io.BytesIO(data)).read()
    return data

_BAD_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_BARE_AMP = re.compile(rb"&(?!(?:[a-zA-Z][a-zA-Z0-9]{1,31}|#[0-9]{1,7}|#x[0-9a-fA-F]{1,6});)")

def xml_root(data):
    """Parse XML; if the feed is slightly broken (control characters, bare &), clean it and retry."""
    try:
        return ET.fromstring(data)
    except ET.ParseError:
        text = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else data
        text = _BAD_XML.sub("", text).lstrip("\ufeff \r\n\t")
        cleaned = _BARE_AMP.sub(b"&amp;", text.encode("utf-8"))
        return ET.fromstring(cleaned)

def strip_ns(tag):
    return tag.split("}")[-1].lower()

def parse_feed(data):
    """RSS 2.0 or Atom → [(title, url, date)]"""
    root = xml_root(data)
    items = []
    for el in root.iter():
        if strip_ns(el.tag) in ("item", "entry"):
            title, link, date = "", "", ""
            for c in el:
                t = strip_ns(c.tag)
                if t == "title":
                    title = (c.text or "").strip()
                elif t == "link":
                    link = (c.get("href") or c.text or "").strip()
                elif t in ("pubdate", "published", "updated", "date"):
                    date = (c.text or "").strip()[:25]
            if link:
                items.append((title or slug_title(link), link, date))
    return items

def parse_sitemap(data, depth=0, max_children=3):
    """urlset → [(title-from-slug, url, lastmod)]; sitemapindex → recurse (depth 1)."""
    root = xml_root(data)
    kind = strip_ns(root.tag)
    out = []
    if kind == "sitemapindex" and depth == 0:
        children = []
        for sm in root.iter():
            if strip_ns(sm.tag) == "sitemap":
                loc = next((c.text.strip() for c in sm if strip_ns(c.tag) == "loc" and c.text), None)
                lastmod = next((c.text.strip() for c in sm if strip_ns(c.tag) == "lastmod" and c.text), "")
                if loc:
                    children.append((loc, lastmod))
        # newest child sitemaps first; scan at most 3
        children.sort(key=lambda x: x[1], reverse=True)
        for loc, _ in children[:max_children]:
            try:
                out += parse_sitemap(fetch(loc), depth=1)
            except Exception:
                pass
        return out
    for u in root.iter():
        if strip_ns(u.tag) == "url":
            loc, lastmod = "", ""
            for c in u:
                t = strip_ns(c.tag)
                if t == "loc":
                    loc = (c.text or "").strip()
                elif t == "lastmod":
                    lastmod = (c.text or "").strip()
            if loc:
                out.append((slug_title(loc), loc, lastmod))
    return out

def slug_title(url):
    slug = url.rstrip("/").split("/")[-1]
    slug = re.sub(r"\.(html?|php|aspx?)$", "", slug)
    slug = re.sub(r"[-_]+", " ", slug).strip()
    return slug.title() if slug else url

def parse_date(s):
    """ISO (2026-11-11...) or RSS/RFC 822 (Wed, 11 Nov 2026 ...) → date, else None."""
    if not s:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return dt.date(int(m[1]), int(m[2]), int(m[3]))
    t = email.utils.parsedate(s)
    if t:
        return dt.date(t[0], t[1], t[2])
    return None

def recent_enough(date_str):
    """Undated items pass (the URL diff still applies); dated ones must be recent.
    Applies to feeds too, so a feed that stopped updating can't flood the digest."""
    d = parse_date(date_str)
    if d is None:
        return True
    return (dt.date.today() - d).days <= SITEMAP_RECENT_DAYS

# ---------------------------------------------------------------- source cards
# A headline isn't enough to write from. For each new item the scanner opens
# the page and pulls the facts a post needs: what it says, the numbers, a quote.

from html.parser import HTMLParser
import html as htmllib

MAX_CARDS_PER_RUN = 90           # page reads per run (keeps the job fast and polite)
MAX_PAGE_BYTES = 2_000_000

class _ArticleParser(HTMLParser):
    """Collects meta tags and visible paragraph text; skips scripts, nav, footers."""
    SKIP = {"script", "style", "noscript", "nav", "footer", "header", "aside", "form", "svg"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.paras, self.title = {}, [], ""
        self._skip, self._in_p, self._in_title, self._buf = 0, False, False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self._skip += 1
        elif tag == "meta":
            key = (a.get("property") or a.get("name") or "").lower()
            if key and a.get("content"):
                self.meta.setdefault(key, a["content"].strip())
        elif tag == "title":
            self._in_title = True
        elif tag == "p" and not self._skip:
            self._in_p, self._buf = True, []

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._in_title = False
        elif tag == "p" and self._in_p:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if len(text) > 60:
                self.paras.append(text)
            self._in_p = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_p and not self._skip:
            self._buf.append(data)

_NUMBER = re.compile(r"(\d[\d,.]*\s?(%|percent|x\b|×)|[$€£₹]\s?\d|\b\d[\d,.]*\s?(million|billion|trillion|bn|m)\b"
                     r"|\b\d{1,3}(,\d{3})+\b|\b\d+\s+(of|out of|in)\s+\d+\b|\b(19|20)\d{2}\b.*\b\d+%)", re.I)
_QUOTE = re.compile(r"[“\"]([^”\"]{40,240})[”\"]")

def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", text) if s.strip()]

def build_card(url):
    """Fetch one article and return its source card. Never raises."""
    card = {"title": "", "summary": "", "published": "", "numbers": [], "quote": "", "ok": False}
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=15) as r:
            if "html" not in (r.headers.get("Content-Type") or "html"):
                return card
            raw = r.read(MAX_PAGE_BYTES)
        page = raw.decode("utf-8", errors="replace")
        p = _ArticleParser()
        p.feed(page)
    except Exception as e:
        card["error"] = type(e).__name__
        return card

    m = p.meta
    card["title"] = htmllib.unescape(m.get("og:title") or p.title or "").strip()[:200]
    card["summary"] = htmllib.unescape(m.get("og:description") or m.get("description")
                                       or m.get("twitter:description") or "").strip()[:400]
    card["published"] = (m.get("article:published_time") or m.get("og:updated_time")
                         or m.get("date") or m.get("parsely-pub-date") or "")[:10]

    body = " ".join(p.paras)
    seen_s = set()
    for s in _sentences(body):
        if 40 <= len(s) <= 280 and _NUMBER.search(s) and s not in seen_s:
            card["numbers"].append(s)
            seen_s.add(s)
        if len(card["numbers"]) == 3:
            break
    q = _QUOTE.search(body)
    if q:
        card["quote"] = q.group(1).strip()
    if not card["summary"] and p.paras:
        card["summary"] = p.paras[0][:400]
    card["ok"] = bool(card["summary"] or card["numbers"])
    return card

def card_lines(card, indent="  "):
    """Markdown lines for the digest."""
    if not card or not card.get("ok"):
        why = f" ({card.get('error')})" if card and card.get("error") else ""
        return [f"{indent}- _Couldn't read the page{why}. Open the link before writing from it._"]
    out = []
    if card["published"]:
        out.append(f"{indent}- **Published:** {card['published']}")
    if card["summary"]:
        out.append(f"{indent}- **What it says:** {card['summary']}")
    for n in card["numbers"]:
        out.append(f"{indent}- **Number:** {n}")
    if card["quote"]:
        out.append(f"{indent}- **Quote:** “{card['quote']}”")
    return out

def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

# ---------------------------------------------------------------- relevance
# Every item gets territory tags from its title and source card, so the digest
# leads with what fits the brand and Notion only receives items worth reading.

# Territories (the brand's pillars) come from territories.json in the sources folder,
# so the same scanner serves any niche. See scanner/sources/territories.json.
TERRITORY_KEYWORDS = {}
TERRITORY_ORDER = []
TOPIC_TERMS = []       # words that mark a story as in the brand's world at all (the gate)
TOP_LABEL = "Top picks"
AI_TERMS = ["ai", "a.i.", "llm", "gpt", "claude", "gemini", "openai", "anthropic", "copilot", "agent",
            "machine learning", "model", "models", "chatbot", "genai", "generative", "agentic",
            "chatgpt", "perplexity", "ai mode", "ai overview"]
BOOST_TERMS = AI_TERMS    # a story mentioning one of these gets +1 (set "boost_terms" in territories.json; [] to turn off)
MIN_SCORE_FOR_NOTION = 2

def load_territories(base):
    global TERRITORY_KEYWORDS, TERRITORY_ORDER, TOPIC_TERMS, TOP_LABEL, BOOST_TERMS
    cfg = load_json(os.path.join(base, "territories.json"), {})
    TERRITORY_KEYWORDS = cfg.get("keywords", {})
    TERRITORY_ORDER = cfg.get("order") or list(TERRITORY_KEYWORDS)
    TOPIC_TERMS = cfg.get("topic_terms", [])
    TOP_LABEL = cfg.get("top_label", TOP_LABEL)
    BOOST_TERMS = [k.lower() for k in cfg.get("boost_terms", AI_TERMS)]

def _has(text, kws):
    return any(re.search(r"(?<![a-z0-9])" + re.escape(k), text) for k in kws)

def relevance(title, card):
    """(score, [tags]). Score = distinct territories hit, +1 if it hits any territory, +1 if it hits a boost term.
    So a story in one pillar scores 2 (a top pick), and a story in a pillar that also hits a boost term scores 3.
    A story that never touches the brand's world (TOPIC_TERMS or a territory) is capped at 1."""
    text = " " + " ".join([title or "", (card or {}).get("summary", ""), " ".join((card or {}).get("numbers", []))]).lower() + " "
    tags = [t for t, kws in TERRITORY_KEYWORDS.items() if _has(text, kws)]
    is_ai = any(re.search(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])", text) for k in BOOST_TERMS)
    in_world = bool(tags) or (_has(text, TOPIC_TERMS) if TOPIC_TERMS else is_ai)
    score = len(tags) + (1 if tags else 0) + (1 if is_ai else 0)
    if not in_world:
        score = min(score, 1)   # off-topic pages never reach the top picks
    tags.sort(key=lambda t: TERRITORY_ORDER.index(t) if t in TERRITORY_ORDER else 99)
    return score, tags

def is_topic_text(text):
    """For general sites marked "topic_only": keep stories that touch a territory or a topic term."""
    t = " " + (text or "").lower() + " "
    return _has(t, TOPIC_TERMS) or any(_has(t, kws) for kws in TERRITORY_KEYWORDS.values())

SOURCE_REPORT = os.path.join(HERE, "SOURCES.md")

def write_source_report(sources, health, today_s, title="Sources"):
    """SOURCES.md: every source grouped by category, what it's for, and how it did on the last run."""
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    scanned = [x for x in sources if x.get("type") != "manual"]
    ok = sum(1 for x in scanned if health.get(x["name"], {}).get("ok") and not health[x["name"]].get("warn"))
    manual = len(sources) - len(scanned)
    lines = [
        f"# {title}",
        "",
        "Every source, grouped by category: what it's for and how it did on the last run.",
        "This file is rewritten automatically after each run. To add or remove a source, edit `sources.json` in this folder.",
        "",
        f"**Last run:** {now} · **Scanned automatically:** {ok} of {len(scanned)} working"
        + (f" · **Check manually:** {manual}" if manual else ""),
        "",
    ]
    cats = []
    for x in sources:
        c = x.get("category", "Other")
        if c not in cats:
            cats.append(c)
    n = 0
    for c in cats:
        lines += [f"## {c}", "",
                  "| # | Source | Why it's here | Status | Articles listed | Newest article | New this run |",
                  "|---|---|---|---|---|---|---|"]
        for x in [y for y in sources if y.get("category", "Other") == c]:
            n += 1
            h = health.get(x["name"], {})
            if x.get("type") == "manual":
                status = "📌 check manually (no feed)"
            elif not h:
                status = "⚪ not run"
            elif not h.get("ok"):
                status = f"🔴 {h['error']}"
            elif h.get("warn"):
                status = f"🟡 {h['warn']}"
            elif h.get("quiet"):
                status = "🟢 working (no matching stories in the feed right now)"
            else:
                status = "🟢 working"
            if x.get("ai_only") and x.get("type") != "manual":
                status += " · AI stories only"
            if x.get("topic_only") and x.get("type") != "manual":
                status += " · on-topic stories only"
            site = x.get("site") or x["url"]
            lines.append(f"| {n} | [{x['name']}]({site}) | {x.get('why', '')} | {status} | "
                         f"{h.get('listed', '')} | {h.get('latest', '')} | {h.get('new', '')} |")
        lines.append("")
    lines += ["**Status key:** 🟢 working · 🟡 reachable but no articles found (check the address or filter) · "
              "🔴 failed (blocked, moved, or wrong address) · 📌 no feed, so open it yourself (dashboards, paid sites) · "
              "\"AI stories only\" = a general news site where only AI-related stories are kept", ""]
    with open(SOURCE_REPORT, "w") as f:
        f.write("\n".join(lines))

AI_EXTRA = ["llm", "chatgpt", "deepfake", "prompt injection", "agentic", "ai agent", "ai-powered", "ai-driven",
            "ai-generated", "large language", "machine learning", "machine-learning", "jailbreak", "genai",
            "generative ai", "copilot", "gemini", "claude", "openai", "anthropic", "mcp server", "model context protocol"]
AI_STRICT = ["ai", "llm", "llms", "gpt", "genai"]   # whole words only; not "agent" or "model" (too many false hits)

def is_ai_text(text):
    """Stricter than relevance(): used to keep only AI stories from general security/news feeds."""
    t = " " + (text or "").lower() + " "
    if any(k in t for k in AI_EXTRA):
        return True
    return any(re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", t) for k in AI_STRICT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true",
                    help="first run: record everything as seen, but still report items from the last 2 days")
    ap.add_argument("--backfill", type=int, default=0, metavar="DAYS",
                    help="also report items dated within DAYS even if already seen")
    ap.add_argument("--config", default=DEFAULT_CONFIG, metavar="DIR",
                    help="folder holding sources.json; state, digests and SOURCES.md are written there too")
    ap.add_argument("--title", default="Sources", help="heading for SOURCES.md")
    ap.add_argument("--no-notion", action="store_true", help="don't send top picks to Notion")
    args = ap.parse_args()

    global SOURCES, STATE, DIGESTS, INBOX, PUSHED, SOURCE_REPORT
    base = os.path.abspath(args.config)
    SOURCES = os.path.join(base, "sources.json")
    STATE = os.path.join(base, "seen_urls.json")
    DIGESTS = os.path.join(base, "digests")
    INBOX = os.path.join(base, "fuel_inbox.csv")
    PUSHED = os.path.join(base, "notion_pushed.json")
    SOURCE_REPORT = os.path.join(base, "SOURCES.md")

    load_territories(base)
    sources = load_json(SOURCES, [])
    if not sources:
        sys.exit(f"No sources found. Create {SOURCES} first.")
    seen = load_json(STATE, {})
    today = dt.date.today()
    today_s = today.isoformat()
    report_days = 2 if args.init else args.backfill
    new_by_source, errors = {}, []

    def within(date_str, days):
        d = parse_date(date_str)
        return d is not None and (today - d).days <= days

    health = {}   # per-source result for SOURCES.md
    for s in sources:
        name, typ, url = s["name"], s["type"], s["url"]
        if typ == "manual":
            continue              # dashboards and paid sites: listed in SOURCES.md, not fetched
        try:
            data = fetch(url)
            # A filtered sitemap may keep its articles in a later child sitemap, so read more of them.
            items = parse_feed(data) if typ == "rss" else parse_sitemap(data, max_children=12 if s.get("include") else 3)
        except Exception as e:
            errors.append(f"{name}: {type(e).__name__} {e}")
            health[name] = {"ok": False, "error": f"{type(e).__name__}: {str(e)[:80]}".replace("|", "/")}
            continue
        # Optional filter: only keep links containing this text (e.g. "/news/"),
        # for sitemaps that list every page on a site, not just articles.
        inc = s.get("include")
        if inc:
            pats = inc if isinstance(inc, list) else [inc]
            items = [it for it in items if any(pt in it[1] for pt in pats)]
        # General news sites: keep only AI-related stories (judged from the title or link slug).
        before_ai = len(items)
        if s.get("ai_only"):
            items = [it for it in items if is_ai_text(it[0] + " " + it[1].replace("-", " "))]
        if s.get("topic_only"):
            items = [it for it in items if is_topic_text(it[0] + " " + it[1].replace("-", " "))]
        dated = [parse_date(d) for _, _, d in items if parse_date(d)]
        health[name] = {"ok": True, "listed": len(items),
                        "latest": max(dated).isoformat() if dated else "", "new": 0}
        if not items and before_ai:
            health[name]["quiet"] = True    # feed works; just no AI stories in it right now
        elif not items:
            health[name]["warn"] = "feed returned no articles"
        fresh = []
        for title, link, date in items:
            already = link in seen
            if already and not (report_days and within(date, report_days)):
                continue
            if not recent_enough(date):
                seen[link] = today_s  # old item; remember it, never report it
                continue
            seen.setdefault(link, today_s)
            if args.init and not within(date, report_days):
                continue              # first run: only the last 2 days are news
            fresh.append((title, link, date))
        if fresh:
            new_by_source[name] = fresh[:MAX_NEW_PER_SOURCE]
            health[name]["new"] = len(new_by_source[name])

    with open(STATE, "w") as f:
        json.dump(seen, f)
    write_source_report(sources, health, today_s, args.title)

    if args.init:
        print(f"Initialized: {len(seen)} URLs recorded across {len(sources)} sources; "
              f"reporting {sum(len(v) for v in new_by_source.values())} items from the last {report_days} days.")
        if errors:
            print("Source errors (fix these URLs):\n  " + "\n  ".join(errors))

    # Source cards: read each new article once, up to the per-run cap.
    cards, budget = {}, MAX_CARDS_PER_RUN
    if os.environ.get("FUEL_SKIP_CARDS") != "1":
        for name, items in new_by_source.items():
            for title, link, _ in items:
                if budget <= 0:
                    break
                cards[link] = build_card(link)
                budget -= 1
        types = {s["name"]: s["type"] for s in sources}
        for name, items in new_by_source.items():
            if types.get(name) != "sitemap":
                continue
            fixed = []
            for t, l, d in items:
                c = cards.get(l) or {}
                better = c.get("title") if c.get("ok") and len(c.get("title", "")) > 10 else ""
                fixed.append((better or t, l, d))
            new_by_source[name] = fixed

    # Relevance for every item
    rel = {}
    for name, items in new_by_source.items():
        for t, l, d in items:
            rel[l] = relevance(t, cards.get(l))

    os.makedirs(DIGESTS, exist_ok=True)
    digest_path = os.path.join(DIGESTS, f"digest-{today_s}.md")
    total = sum(len(v) for v in new_by_source.values())
    exists = os.path.exists(digest_path)
    h2 = "###" if exists else "##"
    if exists:
        stamp = dt.datetime.now().strftime("%H:%M")
        label = "Backfill" if args.backfill else "Later run"
        lines = ["", "---", f"## {label} {stamp} — {total} items", ""]
    else:
        lines = [f"# Fuel digest — {today_s}", f"_{total} new items across {len(new_by_source)} sources_", ""]

    cat_of = {x["name"]: x.get("category", "") for x in sources}

    def item_lines(title, link, date, source):
        score, tags = rel.get(link, (0, []))
        source = f"{source} · {cat_of.get(source, '')}" if cat_of.get(source) else source
        tag_s = f"  `{' · '.join(tags)}`" if tags else ""
        out = [f"- [{title}]({link}) — {source}{'  ·  ' + date if date else ''}{tag_s}"]
        if link in cards:
            out.extend(card_lines(cards[link]))
        return out

    flat = [(t, l, d, n) for n, items in new_by_source.items() for t, l, d in items]
    top = sorted([x for x in flat if rel[x[1]][0] >= MIN_SCORE_FOR_NOTION],
                 key=lambda x: -rel[x[1]][0])
    rest = [x for x in flat if rel[x[1]][0] < MIN_SCORE_FOR_NOTION]
    if top:
        lines.append(f"{h2} Top picks ({len(top)}) — {TOP_LABEL}")
        for t, l, d, n in top:
            lines.extend(item_lines(t, l, d, n))
        lines.append("")
    if rest:
        lines.append(f"{h2} Everything else ({len(rest)})")
        for t, l, d, n in rest:
            score, tags = rel[l]
            lines.append(f"- [{t}]({l}) — {n}")
        lines.append("")
    if errors:
        lines += [f"{h2} Scanner errors", *[f"- {e}" for e in errors], ""]
    if not (exists and total == 0 and not errors):
        with open(digest_path, "a" if exists else "w") as f:
            f.write("\n".join(lines))

    new_file = not os.path.exists(INBOX)
    logged = set()
    if not new_file:
        with open(INBOX, newline="") as f:
            logged = {row[3] for row in csv.reader(f) if len(row) > 3}
    with open(INBOX, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["date", "source", "title", "url", "territory", "angle", "score", "status"])
        for t, l, d, n in flat:
            if l in logged:
                continue          # a backfill re-reports items; log each link once
            score, tags = rel[l]
            w.writerow([today_s, n, t, l, " · ".join(tags), "", score, "raw"])
            logged.add(l)

    # Notion only gets the top picks, so the database stays worth reading.
    to_notion = {}
    for t, l, d, n in top:
        to_notion.setdefault(n, []).append((t, l, d))
    pushed, push_errors = (None, []) if args.no_notion else notion_push(to_notion, cards, rel)
    print(f"{total} items → {digest_path} ({len(top)} top picks)")
    if pushed is not None:
        print(f"Notion: {pushed} top picks added to the Fuel Database")
    if push_errors:
        print("Notion errors:\n  " + "\n  ".join(push_errors[:5]))
    if errors:
        print("Source errors:\n  " + "\n  ".join(errors))

def _txt(s):
    return [{"type": "text", "text": {"content": s[:1900]}}]

def card_blocks(source, link, card):
    """The source card as Notion blocks, so it sits in the page body."""
    blocks = [{"object": "block", "type": "heading_3", "heading_3": {"rich_text": _txt("Source card")}}]
    if not card or not card.get("ok"):
        blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": _txt(
            "Couldn't read the page. Open the link and add the key facts before writing from it.")}})
    else:
        meta = f"{source}" + (f" · published {card['published']}" if card["published"] else "")
        blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": _txt(meta)}})
        if card["summary"]:
            blocks.append({"object": "block", "type": "paragraph",
                           "paragraph": {"rich_text": _txt("What it says: " + card["summary"])}})
        for n in card["numbers"]:
            blocks.append({"object": "block", "type": "bulleted_list_item",
                           "bulleted_list_item": {"rich_text": _txt(n)}})
        if card["quote"]:
            blocks.append({"object": "block", "type": "quote", "quote": {"rich_text": _txt(card["quote"])}})
    blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [
        {"type": "text", "text": {"content": link[:1900], "link": {"url": link}}}]}})
    return blocks

def notion_payload(database_id, source, title, link, card=None, tags=None):
    """One Fuel Database row. Property names match the Notion schema exactly."""
    idea = f"{title}"[:1900]
    summary = (card or {}).get("summary") or ""
    return {
        "parent": {"database_id": database_id},
        "properties": {
            "Idea": {"title": [{"text": {"content": idea}}]},
            "Source": {"select": {"name": "news"}},
            "Territory": {"select": {"name": (tags or ["News"])[0]}},
            "Link": {"url": link},
            "Angle": {"rich_text": [{"text": {"content": f"via {source}" + (f" — {summary[:300]}" if summary else "")}}]},
            # Status is a Select (what setup/create_notion_db.py makes). If your database uses
            # Notion's built-in Status type instead, set NOTION_STATUS_TYPE=status.
            "Status": {(os.environ.get("NOTION_STATUS_TYPE") or "select"): {"name": "Raw"}},
        },
        "children": card_blocks(source, link, card),
    }

def notion_push(new_by_source, cards=None, rel=None):
    """Optional: push new items to Notion when NOTION_TOKEN + NOTION_DATABASE_ID are set.
    Returns (count_pushed or None if disabled, [errors])."""
    token = os.environ.get("NOTION_TOKEN")
    db = os.environ.get("NOTION_DATABASE_ID")
    if not token or not db:
        return None, []
    pushed, errs = 0, []
    done = set(load_json(PUSHED, []))
    for source, items in new_by_source.items():
        for title, link, _ in items:
            if link in done:
                continue          # never create a second page for the same link
            tags = ((rel or {}).get(link) or (0, []))[1]
            body = json.dumps(notion_payload(db, source, title, link, (cards or {}).get(link), tags)).encode()
            req = urllib.request.Request(
                os.environ.get("NOTION_API_URL", "https://api.notion.com/v1/pages"), data=body, method="POST",
                headers={"Authorization": f"Bearer {token}",
                         "Notion-Version": "2022-06-28",
                         "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT):
                    pushed += 1
                    done.add(link)
            except Exception as e:
                detail = e.read().decode()[:200] if hasattr(e, "read") else str(e)
                errs.append(f"{title[:50]}: {detail}")
    with open(PUSHED, "w") as f:
        json.dump(sorted(done), f)
    return pushed, errs

if __name__ == "__main__":
    main()
