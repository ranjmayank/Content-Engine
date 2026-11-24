#!/usr/bin/env python3
"""Render a daily topic list (content/topic-lists/YYYY-MM-DD.json) into:
   - YYYY-MM-DD.md          (readable in GitHub)
   - YYYY-MM-DD.email.html  (inline-styled, for the 11 AM email)
   - latest.html            (a self-contained page you can publish or open locally)
Usage: python3 tools/render_topics.py content/topic-lists/2026-11-20.json
"""
import json, sys, os, html, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_config as EC
from urllib.parse import quote_plus

src = sys.argv[1]
d = json.load(open(src))
base = os.path.splitext(src)[0]
outdir = os.path.dirname(src)
E = html.escape
gq = lambda q: "https://www.google.com/search?q=" + quote_plus(q)
day = datetime.date.fromisoformat(d["date"]).strftime("%A %-d %B %Y")
CATS = EC.pillars() + ["From your data"]
SITE = EC.SITE_NAME
NC = 6   # colour slots; categories beyond six reuse them
ORDER = {"Top pick": 0, "Strong": 1, "Good": 2}
topics = sorted(d["topics"], key=lambda t: ORDER.get(t["priority"], 3))

# ---------- markdown
md = [f"# {SITE} — topic list, {day}", "", f"{d['scanned']} · {d['window']}", ""]
for i, t in enumerate(topics, 1):
    md += [f"## {i}. {t['title']}", f"**{t['category']}** · {t['priority']} · Suggested format: {t['format']}", "",
           f"**Why now:** {t['why']}", ""] + ([f"**Your data:** {t['data']}", ""] if t.get("data") else []) + ["**Key facts**"] + [f"- {f}" for f in t["facts"]] + [
           "", f"**Angle:** {t['angle']}", "", "**References**"] + [f"- [{n}]({u})" for n, u in t["refs"]] + [
           "", "**Fan-out queries** (what people and AI search engines ask)"] + [f"- [{q}]({gq(q)})" for q in t["fanout"]] + [""]
open(base + ".md", "w").write("\n".join(md))

# ---------- email (inline styles only)
INK, AMB, PAP, MUT = EC.COLORS["ink"], "#B86E00", "#FFFFFF", "#5C5C6B"
ACC, PAPER = EC.COLORS["accent"], EC.COLORS["paper"]
e = [f'<div style="font-family:Arial,Helvetica,sans-serif;color:{INK};max-width:680px;margin:0 auto;line-height:1.5">',
     f'<div style="background:{INK};color:{PAPER};padding:20px 24px;border-radius:6px 6px 0 0"><div style="font-size:12px;letter-spacing:1px;color:{ACC}">{E(SITE.upper())} · DAILY TOPICS</div>'
     f'<div style="font-size:22px;font-weight:bold;margin-top:4px">{E(day)}</div><div style="font-size:13px;color:#C9C6BF;margin-top:4px">{E(d["scanned"])} · {E(d["window"])}</div></div>',
     f'<div style="padding:8px 24px 24px;border:1px solid #E4E2DC;border-top:0">']
e.append('<p style="font-size:14px;margin:16px 0 4px"><b>Today\'s list</b></p><ol style="font-size:14px;padding-left:20px;margin:0 0 8px">' +
         "".join(f'<li><a href="#{t["id"]}" style="color:{INK}">{E(t["title"])}</a> <span style="color:{MUT}">— {E(t["priority"])}</span></li>' for t in topics) + "</ol>")
for i, t in enumerate(topics, 1):
    e.append(f'<hr style="border:0;border-top:1px solid #E4E2DC;margin:20px 0"><a name="{t["id"]}"></a>'
             f'<div style="font-size:12px;color:{AMB};font-weight:bold;letter-spacing:.5px">{E(t["category"].upper())} · {E(t["priority"].upper())}</div>'
             f'<div style="font-size:18px;font-weight:bold;margin:4px 0 6px">{i}. {E(t["title"])}</div>'
             f'<div style="font-size:13px;color:{MUT}">Suggested format: {E(t["format"])}</div>'
             f'<p style="font-size:14px"><b>Why now:</b> {E(t["why"])}</p>'
             + (f'<p style="font-size:14px;background:#FBEFD9;padding:8px 10px;border-radius:4px"><b>Your data:</b> {E(t["data"])}</p>' if t.get("data") else "") +
             '<p style="font-size:14px;margin-bottom:4px"><b>Key facts</b></p><ul style="font-size:14px;margin-top:0">' + "".join(f"<li>{E(f)}</li>" for f in t["facts"]) + "</ul>"
             f'<p style="font-size:14px"><b>Angle:</b> {E(t["angle"])}</p>'
             '<p style="font-size:14px;margin-bottom:4px"><b>References</b></p><ul style="font-size:14px;margin-top:0">' +
             "".join(f'<li><a href="{E(u)}" style="color:#1A5FB4">{E(n)}</a></li>' for n, u in t["refs"]) + "</ul>"
             '<p style="font-size:14px;margin-bottom:4px"><b>Fan-out queries</b></p><p style="font-size:13px;margin-top:0">' +
             " · ".join(f'<a href="{gq(q)}" style="color:#1A5FB4">{E(q)}</a>' for q in t["fanout"]) + "</p>")
e.append(f'<p style="font-size:12px;color:{MUT};margin-top:24px">Facts come from the linked sources; open each before publishing. Built by Content Engine from your sources and your Search Console + GA4 data.</p></div></div>')
open(base + ".email.html", "w").write("".join(e))

# ---------- page (artifact)
cards = []
for i, t in enumerate(topics, 1):
    cat_f = CATS.index(t["category"]) if t["category"] in CATS else 0
    cat_i = cat_f % NC
    cards.append(f'''<article class="topic" id="{t["id"]}" data-cat="{cat_f}">
<header class="th"><span class="cat c{cat_i}">{E(t["category"])}</span><span class="pri p{ORDER.get(t["priority"],3)}">{E(t["priority"])}</span><span class="fmt">{E(t["format"])}</span></header>
<h2><span class="n">{i:02d}</span>{E(t["title"])}</h2>
<p class="why">{E(t["why"])}</p>{f'<p class="data"><b>Your data</b> {E(t["data"])}</p>' if t.get("data") else ""}
<div class="cols">
<section><h3>Key facts</h3><ul class="facts">{"".join(f"<li>{E(f)}</li>" for f in t["facts"])}</ul>
<p class="angle"><b>Angle</b> {E(t["angle"])}</p></section>
<section><h3>References <span class="cnt">{len(t["refs"])}</span></h3><ol class="refs">{"".join(f'<li><a href="{E(u)}" target="_blank" rel="noopener">{E(n)}</a><span class="host">{E(u.split("/")[2].replace("www.",""))}</span></li>' for n,u in t["refs"])}</ol>
<h3>Fan-out queries</h3><div class="fan">{"".join(f'<a href="{gq(q)}" target="_blank" rel="noopener">{E(q)}</a>' for q in t["fanout"])}</div></section>
</div></article>''')
counts = [sum(1 for t in topics if t["category"] == c) for c in CATS]
filters = '<button class="f on" data-f="all" id="f-all">All <b>' + str(len(topics)) + '</b></button>' + "".join(
    f'<button class="f" data-f="{i}" id="f-{i}"><i class="dot c{i % NC}"></i>{E(c)} <b>{counts[i]}</b></button>' for i, c in enumerate(CATS) if counts[i])
page = f'''<title>{E(SITE)} Topics</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Inter:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap">
<style>
/* Layout: one reading column of topic cards, filter chips on top, each card splits facts | sources+queries on wide screens */
:root{{--bg:#F6F5F1;--surface:#FFFFFF;--fg:#16161E;--muted:#5D5C66;--line:#E3E1DA;--accent:#B26A00;--accent-bg:#FBEFD9;
--c0:#2F6FD6;--c1:#1E8A6B;--c2:#7A4FD1;--c3:#C2412D;--c4:#B0457F;--c5:#8A6A00;--link:#1F5FBF;
--display:"Outfit",system-ui,sans-serif;--body:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;--mono:"Geist Mono",ui-monospace,Menlo,monospace}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#121218;--surface:#1B1B23;--fg:#F1EFEA;--muted:#A3A1AB;--line:#2C2C37;--accent:#F5A623;--accent-bg:#2E2414;--c0:#7FA8F0;--c1:#5CC9A7;--c2:#B497F0;--c3:#F08A76;--c4:#EE8CC2;--c5:#E3C25A;--link:#8DB4F5;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#121218;--surface:#1B1B23;--fg:#F1EFEA;--muted:#A3A1AB;--line:#2C2C37;--accent:#F5A623;--accent-bg:#2E2414;--c0:#7FA8F0;--c1:#5CC9A7;--c2:#B497F0;--c3:#F08A76;--c4:#EE8CC2;--c5:#E3C25A;--link:#8DB4F5;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.55}}
.wrap{{max-width:1040px;margin:0 auto;padding-block:28px 56px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
.eyebrow{{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}}
h1{{font-family:var(--display);font-size:clamp(28px,4.4vw,42px);line-height:1.1;margin:6px 0 8px;text-wrap:balance}}
.meta{{color:var(--muted);margin:0 0 20px;font-size:14px}}
.filters{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:22px}}
.f{{font:500 13px var(--body);color:var(--fg);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:6px 12px;cursor:pointer;display:inline-flex;align-items:center;gap:6px}}
.f b{{font-family:var(--mono);font-weight:500;color:var(--muted)}}
.f.on{{border-color:var(--fg);box-shadow:inset 0 0 0 1px var(--fg)}}
.f:focus-visible,a:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.dot{{width:8px;height:8px;border-radius:50%;display:inline-block}}
.dot.c0,.cat.c0{{--c:var(--c0)}}.dot.c1,.cat.c1{{--c:var(--c1)}}.dot.c2,.cat.c2{{--c:var(--c2)}}.dot.c3,.cat.c3{{--c:var(--c3)}}.dot.c4,.cat.c4{{--c:var(--c4)}}.dot.c5,.cat.c5{{--c:var(--c5)}}
.dot{{background:var(--c)}}
.list{{display:flex;flex-direction:column;gap:16px}}
.topic{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:20px 22px}}
.th{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:12px}}
.cat{{color:var(--c);font-weight:600;letter-spacing:.02em}}
.pri{{font-family:var(--mono);font-size:11px;padding:2px 8px;border-radius:4px;border:1px solid var(--line);color:var(--muted)}}
.pri.p0{{background:var(--accent-bg);color:var(--accent);border-color:transparent;font-weight:500}}
.fmt{{color:var(--muted);margin-left:auto}}
h2{{font-family:var(--display);font-weight:600;font-size:21px;line-height:1.25;margin:10px 0 8px;text-wrap:balance;display:flex;gap:12px}}
h2 .n{{font-family:var(--mono);font-size:13px;font-weight:400;color:var(--muted);padding-top:5px}}
.why{{margin:0 0 14px;max-width:72ch}}
.data{{margin:-6px 0 14px;font-size:14px;border-left:3px solid var(--accent);padding:4px 10px}} .data b{{color:var(--accent);margin-right:6px}}
.cols{{display:grid;grid-template-columns:1.1fr 1fr;gap:24px;border-top:1px solid var(--line);padding-top:14px}}
.cols>section{{min-width:0}}
h3{{font:600 12px var(--body);text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin:0 0 8px;display:flex;gap:6px;align-items:center}}
h3:not(:first-child){{margin-top:16px}}
.cnt{{font-family:var(--mono);font-weight:400}}
.facts{{margin:0;padding-left:18px;display:flex;flex-direction:column;gap:6px;font-size:14px}}
.angle{{margin:14px 0 0;font-size:14px;background:var(--accent-bg);padding:10px 12px;border-radius:6px}}
.angle b{{color:var(--accent);margin-right:6px}}
.refs{{margin:0;padding-left:20px;font-size:14px;display:flex;flex-direction:column;gap:6px}}
.refs a{{color:var(--link);text-decoration:none}} .refs a:hover{{text-decoration:underline}}
.host{{display:block;font-family:var(--mono);font-size:11px;color:var(--muted)}}
.fan{{display:flex;flex-wrap:wrap;gap:6px}}
.fan a{{font-size:13px;color:var(--fg);text-decoration:none;border:1px dashed var(--line);border-radius:6px;padding:4px 8px}}
.fan a:hover{{border-color:var(--link);color:var(--link)}}
.foot{{color:var(--muted);font-size:13px;margin-top:28px;max-width:72ch}}
@media (max-width:720px){{.cols{{grid-template-columns:1fr}}.fmt{{margin-left:0;width:100%}}.topic{{padding:16px}}}}
</style>
<div class="wrap">
<div class="eyebrow">{E(SITE)} · daily topic list</div>
<h1>{E(day)}</h1>
<p class="meta">{E(d["scanned"])} · {E(d["window"])} · {len(topics)} topics, ranked. Fan-out queries open a Google search.</p>
<nav class="filters" aria-label="Filter by topic">{filters}</nav>
<div class="list">{"".join(cards)}</div>
<p class="foot">Every fact is taken from the linked source; items marked "open the article" were not readable from here, so check them before publishing. Vendor numbers are labelled as vendor claims. "Your data" lines come from Search Console and GA4 (analytics/reports/latest.md).</p>
</div>
<script>
(function(){{var bs=document.querySelectorAll('.f'),cs=document.querySelectorAll('.topic');
bs.forEach(function(b){{b.addEventListener('click',function(){{bs.forEach(function(x){{x.classList.toggle('on',x===b)}});var f=b.dataset.f;
cs.forEach(function(c){{c.hidden=!(f==='all'||c.dataset.cat===f)}})}})}})}})();
</script>'''
open(os.path.join(outdir, "latest.html"), "w").write(page)
print("wrote", base + ".md", base + ".email.html", os.path.join(outdir, "latest.html"))
