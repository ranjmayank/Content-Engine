#!/usr/bin/env python3
"""
Pull your site's numbers from Google Search Console and Google Analytics 4.

Writes one folder per run: analytics/data/YYYY-MM-DD/
  gsc_query_page_cur.csv / _prev.csv   query × page, last 28 days vs the 28 before
  gsc_page_cur.csv / _prev.csv         page totals
  gsc_query_cur.csv / _prev.csv        query totals
  gsc_daily.csv                        site totals per day, last 90 days
  ga4_landing_cur.csv / _prev.csv      landing page × source × medium × channel
  ga4_daily.csv                        sessions per day by channel, last 90 days
  meta.json                            the date windows used

Search Console data lags 2–3 days, so windows end 3 days ago.

Settings (GitHub secrets / variables, or environment variables locally):
  GOOGLE_SERVICE_ACCOUNT_JSON  the service account key (the whole JSON text), or
  GOOGLE_APPLICATION_CREDENTIALS  a path to that file
  GSC_SITE_URL     e.g. sc-domain:example.com  or  https://example.com/
  GA4_PROPERTY_ID  the numeric property ID, e.g. 412345678
Either source can be missing: the script pulls what it can and says what it skipped.

Usage: python3 analytics/fetch.py [--days 28]
"""
import argparse, csv, datetime as dt, json, os, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly",
          "https://www.googleapis.com/auth/analytics.readonly"]


def session():
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        sys.exit("Install the Google auth library first: pip install google-auth requests")
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if raw:
        creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=SCOPES)
    elif path and os.path.exists(path):
        creds = service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    else:
        return None
    return AuthorizedSession(creds)


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


# ---------------------------------------------------------------- Search Console

def gsc_query(s, site, start, end, dims, limit=25000):
    url = ("https://searchconsole.googleapis.com/webmasters/v3/sites/"
           + urllib.parse.quote(site, safe="") + "/searchAnalytics/query")
    rows, start_row = [], 0
    while True:
        body = {"startDate": start.isoformat(), "endDate": end.isoformat(), "dimensions": dims,
                "rowLimit": limit, "startRow": start_row, "type": "web"}
        r = s.post(url, json=body, timeout=60)
        if r.status_code != 200:
            raise RuntimeError(f"Search Console {r.status_code}: {r.text[:300]}")
        batch = r.json().get("rows", [])
        rows += batch
        if len(batch) < limit:
            return rows
        start_row += limit


def gsc_rows(rows):
    return [r["keys"] + [r["clicks"], r["impressions"], round(r["ctr"], 5), round(r["position"], 2)] for r in rows]


def pull_gsc(s, site, out, cur, prev, daily):
    m = ["clicks", "impressions", "ctr", "position"]
    for tag, (a, b) in (("cur", cur), ("prev", prev)):
        write_csv(f"{out}/gsc_query_page_{tag}.csv", ["query", "page"] + m,
                  gsc_rows(gsc_query(s, site, a, b, ["query", "page"])))
        write_csv(f"{out}/gsc_page_{tag}.csv", ["page"] + m, gsc_rows(gsc_query(s, site, a, b, ["page"])))
        write_csv(f"{out}/gsc_query_{tag}.csv", ["query"] + m, gsc_rows(gsc_query(s, site, a, b, ["query"])))
    write_csv(f"{out}/gsc_daily.csv", ["date"] + m, gsc_rows(gsc_query(s, site, *daily, ["date"])))


# ---------------------------------------------------------------- GA4

def ga4_report(s, prop, start, end, dims, metrics, limit=100000):
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{prop}:runReport"
    body = {"dateRanges": [{"startDate": start.isoformat(), "endDate": end.isoformat()}],
            "dimensions": [{"name": d} for d in dims], "metrics": [{"name": m} for m in metrics],
            "limit": limit}
    r = s.post(url, json=body, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"GA4 {r.status_code}: {r.text[:300]}")
    out = []
    for row in r.json().get("rows", []):
        out.append([d["value"] for d in row["dimensionValues"]] + [m["value"] for m in row["metricValues"]])
    return out


GA4_DIMS = ["landingPage", "sessionSource", "sessionMedium", "sessionDefaultChannelGroup"]
GA4_METRICS = ["sessions", "engagedSessions", "averageSessionDuration", "keyEvents", "newUsers"]


def pull_ga4(s, prop, out, cur, prev, daily):
    for tag, (a, b) in (("cur", cur), ("prev", prev)):
        write_csv(f"{out}/ga4_landing_{tag}.csv", GA4_DIMS + GA4_METRICS,
                  ga4_report(s, prop, a, b, GA4_DIMS, GA4_METRICS))
    write_csv(f"{out}/ga4_daily.csv", ["date", "sessionDefaultChannelGroup", "sessions", "keyEvents"],
              ga4_report(s, prop, *daily, ["date", "sessionDefaultChannelGroup"], ["sessions", "keyEvents"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28, help="window length (default 28)")
    args = ap.parse_args()

    today = dt.date.today()
    end = today - dt.timedelta(days=3)                 # Search Console lag
    cur = (end - dt.timedelta(days=args.days - 1), end)
    prev = (cur[0] - dt.timedelta(days=args.days), cur[0] - dt.timedelta(days=1))
    daily = (end - dt.timedelta(days=89), end)

    s = session()
    if s is None:
        print("No Google credentials set (GOOGLE_SERVICE_ACCOUNT_JSON). Skipping the pull — see analytics/README.md.")
        return 0
    out = os.path.join(HERE, "data", today.isoformat())
    os.makedirs(out, exist_ok=True)
    meta = {"pulled": today.isoformat(), "current": [d.isoformat() for d in cur],
            "previous": [d.isoformat() for d in prev], "daily": [d.isoformat() for d in daily], "sources": []}

    site, prop, failed = os.environ.get("GSC_SITE_URL"), os.environ.get("GA4_PROPERTY_ID"), []
    if site:
        try:
            pull_gsc(s, site, out, cur, prev, daily)
            meta["sources"].append("gsc")
            print("Search Console: pulled", site)
        except Exception as e:
            failed.append(f"Search Console: {e}")
    else:
        print("GSC_SITE_URL not set; skipped Search Console.")
    if prop:
        try:
            pull_ga4(s, prop, out, cur, prev, daily)
            meta["sources"].append("ga4")
            print("GA4: pulled property", prop)
        except Exception as e:
            failed.append(f"GA4: {e}")
    else:
        print("GA4_PROPERTY_ID not set; skipped GA4.")
    meta["errors"] = failed
    json.dump(meta, open(os.path.join(out, "meta.json"), "w"), indent=2)
    for f in failed:
        print("ERROR", f)
    # keep the last 14 pulls; older ones are summarised in the reports and the tracker
    import glob, shutil
    for old in sorted(glob.glob(os.path.join(HERE, "data", "20*")))[:-14]:
        shutil.rmtree(old, ignore_errors=True)
    return 1 if failed and not meta["sources"] else 0


if __name__ == "__main__":
    sys.exit(main())
