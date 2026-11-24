#!/usr/bin/env bash
# End-to-end smoke test: setup → scanner → audit → topic render, all against a local fixture site.
# Usage: bash tests/run.sh      (needs python3; no network)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"; PORT=8765
trap 'kill $SRV 2>/dev/null || true; rm -rf "$WORK"' EXIT
cp -r "$REPO" "$WORK/repo"; cd "$WORK/repo"
rm -f engine.config.json scanner/sources/sources.json scanner/sources/territories.json
export NO_PROXY=127.0.0.1 no_proxy=127.0.0.1
ok() { echo "  ✓ $1"; }

echo "0. quick setup (the browser form's path) and setup check"
SETUP_BRAND="Fit Daily" SETUP_SITE="fitdaily.example" SETUP_NAME="Sam Lee" SETUP_NICHE="health-fitness — Health & fitness" \
  SETUP_TIMEZONE="London" python3 setup/quick.py >/dev/null
python3 - <<'PY'
import json
c = json.load(open("engine.config.json"))
assert c["brand"]["site"] == "https://fitdaily.example" and c["niche"]["preset"] == "health-fitness"
assert c["cadence"]["timezone"] == "Europe/London" and c["_setup"]["mode"] == "quick"
assert len(json.load(open("scanner/sources/sources.json"))) >= 5
PY
ok "quick setup writes settings from the form fields"
GITHUB_ACTIONS=true python3 setup/check.py | grep -q "Do this next" && ok "setup check runs"
rm -f engine.config.json scanner/sources/sources.json scanner/sources/territories.json

echo "1. setup (answers file)"
python3 - <<'PY'
import json; c=json.load(open("engine.config.example.json")); c["use_preset_sources"]=False; json.dump(c,open("/tmp/ce-answers.json","w"))
PY
python3 setup/init.py --answers /tmp/ce-answers.json >/dev/null
test -f engine.config.json && test -f scanner/sources/territories.json && grep -q "Pricing & packaging" CLAUDE.md && ok "config, territories, CLAUDE.md written"

echo "2. fixture site"
cd tests/fixture-site
NOW="$(python3 -c 'import email.utils;print(email.utils.formatdate())')"
cat > feed.xml <<XML
<?xml version="1.0"?><rss version="2.0"><channel><title>T</title>
<item><title>Usage-based pricing study: SaaS firms raised prices</title><link>http://127.0.0.1:$PORT/index.html</link><pubDate>$NOW</pubDate></item>
<item><title>Onboarding and activation tips for product-led growth</title><link>http://127.0.0.1:$PORT/blog/post-a.html</link><pubDate>$NOW</pubDate></item>
<item><title>Celebrity gossip</title><link>http://127.0.0.1:$PORT/blog/orphan.html</link><pubDate>$NOW</pubDate></item>
</channel></rss>
XML
python3 -m http.server $PORT --bind 127.0.0.1 >/dev/null 2>&1 & SRV=$!
cd "$WORK/repo"; sleep 1

echo "3. scanner"
echo "[{\"name\":\"Fixture\",\"category\":\"Pricing & packaging\",\"why\":\"test\",\"site\":\"http://127.0.0.1:$PORT/\",\"type\":\"rss\",\"url\":\"http://127.0.0.1:$PORT/feed.xml\"}]" > scanner/sources/sources.json
(cd scanner && python3 fuel_scanner.py --config sources --init --no-notion >/dev/null)
D=$(ls scanner/sources/digests/digest-*.md | tail -1)
grep -q "Top picks (2)" "$D" && grep -q "Celebrity gossip" "$D" && ok "digest ranks pillar stories as top picks"
grep -q "🟢" scanner/sources/SOURCES.md && ok "SOURCES.md health report"

echo "4. SEO audit"
python3 seo-audit/audit.py --site "http://127.0.0.1:$PORT/" --delay 0 --external --out "$WORK/audit" >/dev/null
python3 - "$WORK/audit/latest.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1])); ids={i["id"] for i in r["issues"]}
want={"no-https","ai-search-blocked","ai-training-blocked","broken-internal-link","client-error","multiple-h1","missing-h1",
      "invalid-structured-data","heading-skip","noindex","canonicalized","sitemap-non-indexable","orphan-page","no-llms-txt",
      "images-missing-alt","missing-description","thin-content","article-missing-dates","article-missing-author",
      "faq-schema-mismatch","hreflang-invalid","hreflang-no-return","images-missing-dimensions","heavy-images",
      "generic-anchor-text","empty-anchor","broken-external-link","sitemap-stale"}
miss=want-ids
assert not miss, f"missing issues: {miss}"
assert r["site"]["crawler_access"]["GPTBot"] is False and r["site"]["crawler_access"]["Googlebot"] is True
assert 0 < r["score"] < 100
print(f"  ✓ {len(want)} expected issues found, score {r['score']}")
PY

echo "5. topic list render"
cp tests/sample-topic-list.json content/topic-lists/2026-01-15.json
python3 tools/render_topics.py content/topic-lists/2026-01-15.json >/dev/null
grep -q "Growth Notes\|example.com" content/topic-lists/2026-01-15.md && test -f content/topic-lists/latest.html && ok "markdown, email and page rendered"

echo "6. static-site export"
cat > "$WORK/post.md" <<'MD'
# Test post

Slug: /test-post
Meta description: Test.
Tags: a, b
Last updated: 2026-01-15
Author: Alex Doe — test

---
Body.

## Frequently asked questions
**Question one?**
Answer one.
MD
python3 tools/export_post.py "$WORK/post.md" --site "$WORK/site" --dir content/blog --filename "{date}-{slug}.md" >/dev/null
grep -q 'question: "Question one?"' "$WORK/site/content/blog/2026-01-15-test-post.md" && ok "front matter with FAQ written"

echo "7. demo analytics"
python3 tests/make_demo_analytics.py "$WORK/data/2026-01-15" >/dev/null
python3 analytics/analyze.py --data "$WORK/data/2026-01-15" >/dev/null
grep -q "Bing-only demand" analytics/reports/latest.md && grep -q "Striking distance" analytics/reports/latest.md && ok "report with Search Console, GA4 and Bing sections"

echo "8. schedules"
python3 setup/schedule.py --dry-run | grep -q "cron" && ok "cron conversion"
echo "All tests passed."
