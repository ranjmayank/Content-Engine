#!/usr/bin/env bash
# Rebuild examples/ from the fixture sites and fictional demo data (no network). Usage: bash tests/build_examples.sh
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"; trap 'kill $S1 $S2 2>/dev/null || true; rm -rf "$WORK"' EXIT
cp -r "$REPO" "$WORK/repo"; cd "$WORK/repo"
rm -f engine.config.json scanner/sources/*.json
export NO_PROXY=127.0.0.1 no_proxy=127.0.0.1
python3 - <<'PY'
import json; c=json.load(open("engine.config.example.json")); c["use_preset_sources"]=False; json.dump(c,open("/tmp/ex-answers.json","w"))
PY
python3 setup/init.py --answers /tmp/ex-answers.json >/dev/null
NOW="$(python3 -c 'import email.utils;print(email.utils.formatdate())')"; TODAY="$(date +%F)"
sed "s|__RFCDATE__|$NOW|g" tests/fixture-news/feed.template.xml > tests/fixture-news/feed.xml
for f in tests/fixture-news/*.html; do sed -i "s|__DATE__|$TODAY|" "$f"; done
(cd tests/fixture-news && exec python3 -m http.server 8766 --bind 127.0.0.1 >/dev/null 2>&1) & S1=$!
(cd tests/fixture-site && exec python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1) & S2=$!
sleep 1
OUT="$REPO/examples"; mkdir -p "$OUT/screenshots"
# digest
echo '[{"name":"Demo SaaS News","category":"Sales & GTM","why":"Fictional news site for the examples","site":"http://127.0.0.1:8766/","type":"rss","url":"http://127.0.0.1:8766/feed.xml"}]' > scanner/sources/sources.json
(cd scanner && python3 fuel_scanner.py --config sources --init --no-notion --title "Sources — example.com (demo)" >/dev/null)
sed 's|http://127.0.0.1:8766|https://news.example.com|g; s|\.html)|)|g' scanner/sources/digests/digest-*.md > "$OUT/digest.md"
sed 's|http://127.0.0.1:8766|https://news.example.com|g' scanner/sources/SOURCES.md > "$OUT/SOURCES.md"
# audit
python3 seo-audit/audit.py --site http://127.0.0.1:8765/ --delay 0 --external --out "$WORK/audit" >/dev/null
sed 's|http://127.0.0.1:8765|http://demo-site.example|g; s|127.0.0.1:8765|demo-site.example|g; s|http://localhost:8765|http://old-source.example|g' "$WORK/audit/latest.md" > "$OUT/seo-audit.md"
# analytics
python3 tests/make_demo_analytics.py "$WORK/data/$TODAY" >/dev/null
python3 analytics/analyze.py --data "$WORK/data/$TODAY" >/dev/null
cp analytics/reports/latest.md "$OUT/analytics-report.md"
# topic list
cp tests/sample-topic-list.json content/topic-lists/2026-01-15.json
python3 tools/render_topics.py content/topic-lists/2026-01-15.json >/dev/null
cp content/topic-lists/2026-01-15.md "$OUT/topic-list.md"
cp content/topic-lists/2026-01-15.email.html "$OUT/topic-list-email.html"
cp content/topic-lists/latest.html "$OUT/topic-list.html"
# screenshots (needs Chrome/Chromium; skipped if missing)
CHROME="$(command -v google-chrome || command -v chromium || command -v chromium-browser || true)"
if [ -n "$CHROME" ]; then
  "$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=1200,1500 --screenshot="$OUT/screenshots/topic-list.png" "file://$OUT/topic-list.html" >/dev/null 2>&1 || true
  "$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=760,1400 --screenshot="$OUT/screenshots/topic-email.png" "file://$OUT/topic-list-email.html" >/dev/null 2>&1 || true
  for md in seo-audit analytics-report digest; do
    python3 - "$OUT/$md.md" "$WORK/$md.html" <<'PY'
import sys, html, re
src=open(sys.argv[1]).read(); out=[]
inlist=False; intable=False
for line in src.splitlines():
    if line.startswith("|"):
        cells=[c.strip() for c in line.strip("|").split("|")]
        if set("".join(cells)) <= set("-: "): continue
        if not intable: out.append("<table>"); intable=True; tag="th"
        else: tag="td"
        out.append("<tr>"+"".join(f"<{tag}>{html.escape(c)}</{tag}>" for c in cells)+"</tr>"); continue
    if intable: out.append("</table>"); intable=False
    e=html.escape(line); e=re.sub(r"\*\*(.+?)\*\*",r"<b>\1</b>",e); e=re.sub(r"\[(.+?)\]\((.+?)\)",r"<a>\1</a>",e)
    if line.startswith("### "): out.append(f"<h3>{e[4:]}</h3>")
    elif line.startswith("## "): out.append(f"<h2>{e[3:]}</h2>")
    elif line.startswith("# "): out.append(f"<h1>{e[2:]}</h1>")
    elif line.startswith("- "): out.append(f"<li>{e[2:]}</li>")
    elif line.startswith("> "): out.append(f"<blockquote>{e[5:]}</blockquote>")
    elif line.strip(): out.append(f"<p>{e}</p>")
css="body{font:15px/1.5 system-ui,sans-serif;max-width:1000px;margin:24px auto;color:#16161E;background:#FAF7F2;padding:0 20px}h1{font-size:26px}h2{font-size:19px;margin-top:22px;border-top:1px solid #E3E1DA;padding-top:14px}h3{font-size:16px}table{border-collapse:collapse;margin:8px 0;font-size:13px}td,th{border:1px solid #E3E1DA;padding:4px 8px;text-align:left;background:#fff}th{background:#F1EEE6}li{margin:2px 0}blockquote{background:#FBEFD9;margin:8px 0;padding:8px 12px;border-left:3px solid #F5A623}"
open(sys.argv[2],"w").write(f"<meta charset=utf-8><style>{css}</style>"+"\n".join(out))
PY
    "$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=1100,1600 --screenshot="$OUT/screenshots/$md.png" "file://$WORK/$md.html" >/dev/null 2>&1 || true
  done
fi
echo "examples rebuilt → $OUT"
