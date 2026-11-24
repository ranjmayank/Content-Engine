#!/usr/bin/env python3
"""Write a fictional, clearly-labelled demo data folder (Search Console + GA4 + Bing) for a made-up SaaS blog.
Used by the tests and to build examples/analytics-report.md. None of these numbers are real.
Usage: python3 tests/make_demo_analytics.py OUT_DIR"""
import csv, json, os, random, sys, datetime as dt

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
rnd = random.Random(7)
S = "https://example.com"
pages = ["/", "/blog/usage-based-pricing/", "/blog/plg-onboarding-checklist/", "/blog/reduce-saas-churn/",
         "/blog/saas-pricing-page-examples/", "/blog/nrr-benchmarks/", "/blog/cold-email-b2b/", "/newsletter/"]
queries = [  # query, page, impressions now, position now, impressions before, position before, clicks before
    ("usage based pricing", 1, 820, 11.4, 700, 12.0, 6), ("usage-based pricing examples", 1, 410, 9.2, 300, 10.5, 3),
    ("how to reduce saas churn", 3, 960, 6.1, 900, 5.8, 40), ("saas churn rate benchmark", 3, 300, 14.0, 120, 18.0, 1),
    ("plg onboarding checklist", 2, 520, 3.2, 480, 3.1, 30), ("what is product led growth", 2, 1500, 24.5, 1300, 27.0, 2),
    ("saas pricing page examples", 4, 640, 4.4, 600, 4.2, 25), ("net revenue retention benchmark", 5, 380, 8.7, 50, 30.0, 0),
    ("nrr vs grr", 5, 140, 13.2, 0, 0, 0), ("cold email templates b2b", 6, 1100, 31.0, 1000, 29.0, 1),
    ("should i raise saas prices", 1, 90, 16.0, 40, 19.0, 0), ("pricing page", 4, 200, 9.5, 220, 9.0, 3),
    ("pricing page", 1, 180, 11.0, 150, 12.0, 1), ("customer success playbook", 3, 70, 22.0, 60, 25.0, 0)]

def ctr_for(pos):
    return {1: .28, 2: .15, 3: .1, 4: .07, 5: .05, 6: .04}.get(round(pos), .02 if pos < 11 else .006)

def w(name, header, rows):
    with open(os.path.join(out, name), "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(header); cw.writerows(rows)

m = ["clicks", "impressions", "ctr", "position"]
cur_qp, prev_qp = [], []
for q, pi, i, p, ib, pb, cb in queries:
    c = round(i * ctr_for(p) * (0.4 if q == "saas pricing page examples" else 1))
    cur_qp.append([q, S + pages[pi], c, i, round(c / i, 4), p])
    if ib:
        prev_qp.append([q, S + pages[pi], cb, ib, round(cb / ib, 4), pb])
for tag, rows in (("cur", cur_qp), ("prev", prev_qp)):
    w(f"gsc_query_page_{tag}.csv", ["query", "page"] + m, rows)
    agg = {}
    for r in rows:
        for key, idx in (("q", 0), ("p", 1)):
            a = agg.setdefault((key, r[idx]), [0, 0, 0.0])
            a[0] += r[2]; a[1] += r[3]; a[2] += r[5] * r[3]
    w(f"gsc_query_{tag}.csv", ["query"] + m, [[k[1], v[0], v[1], round(v[0] / v[1], 4), round(v[2] / v[1], 2)] for k, v in agg.items() if k[0] == "q"])
    w(f"gsc_page_{tag}.csv", ["page"] + m, [[k[1], v[0], v[1], round(v[0] / v[1], 4), round(v[2] / v[1], 2)] for k, v in agg.items() if k[0] == "p"])
end = dt.date.today() - dt.timedelta(days=3)
w("gsc_daily.csv", ["date"] + m, [[(end - dt.timedelta(days=i)).isoformat(), rnd.randint(4, 12), rnd.randint(200, 320), 0.03, 12.0] for i in range(90)])
ga = []
for tag, mult in (("cur", 1.0), ("prev", 0.8)):
    rows = []
    for pg in pages:
        for src, med, ch, base in (("google", "organic", "Organic Search", 40), ("bing", "organic", "Organic Search", 6),
                                   ("chatgpt.com", "referral", "Referral", 4), ("perplexity.ai", "referral", "Referral", 2),
                                   ("linkedin.com", "referral", "Organic Social", 10), ("(direct)", "(none)", "Direct", 12)):
            sess = max(0, int(base * mult * rnd.uniform(0.3, 1.4)) - (3 if "chatgpt" in src and tag == "prev" else 0))
            rows.append([pg, src, med, ch, sess, int(sess * .6), 74.2, 1 if pg in ("/newsletter/", "/blog/reduce-saas-churn/") and sess > 5 else 0, int(sess * .7)])
    w(f"ga4_landing_{tag}.csv", ["landingPage", "sessionSource", "sessionMedium", "sessionDefaultChannelGroup",
                                 "sessions", "engagedSessions", "averageSessionDuration", "keyEvents", "newUsers"], rows)
w("ga4_daily.csv", ["date", "sessionDefaultChannelGroup", "sessions", "keyEvents"],
  [[(end - dt.timedelta(days=i)).strftime("%Y%m%d"), "Organic Search", rnd.randint(20, 40), 1] for i in range(90)])
w("bing_query_cur.csv", ["query"] + m, [["usage based pricing", 4, 120, 0.033, 7.9], ["saas pricing calculator", 2, 85, 0.024, 12.3],
                                       ["how to reduce saas churn", 3, 140, 0.021, 5.5]])
w("bing_query_prev.csv", ["query"] + m, [["usage based pricing", 2, 90, 0.022, 9.1]])
w("bing_page_cur.csv", ["page"] + m, [[S + pages[1], 6, 205, 0.029, 9.4], [S + pages[3], 3, 140, 0.021, 5.5]])
w("bing_page_prev.csv", ["page"] + m, [[S + pages[1], 2, 90, 0.022, 9.1]])
cur = (end - dt.timedelta(days=27), end); prev = (cur[0] - dt.timedelta(days=28), cur[0] - dt.timedelta(days=1))
json.dump({"pulled": dt.date.today().isoformat(), "current": [d.isoformat() for d in cur], "previous": [d.isoformat() for d in prev],
           "sources": ["gsc", "ga4", "bing"], "errors": [], "demo": "Fictional demo data — not a real site"}, open(os.path.join(out, "meta.json"), "w"))
print("demo data →", out)
