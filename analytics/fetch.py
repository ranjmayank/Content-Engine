#!/usr/bin/env python3
"""
Pull your site's numbers from Google Search Console, Google Analytics 4 and Bing Webmaster Tools.

Writes one folder per run: analytics/data/YYYY-MM-DD/
  gsc_query_page_cur.csv / _prev.csv   query × page, last 28 days vs the 28 before
  gsc_page_cur.csv / _prev.csv         page totals
  gsc_query_cur.csv / _prev.csv        query totals
  gsc_daily.csv                        site totals per day, last 90 days
  ga4_landing_cur.csv / _prev.csv      landing page × source × medium × channel
  ga4_daily.csv                        sessions per day by channel, last 90 days
  bing_query_cur.csv / _prev.csv       Bing queries (clicks, impressions, avg position)
  bing_page_cur.csv / _prev.csv        Bing pages
  meta.json                            the date windows used

Search Console data lags 2–3 days, so windows end 3 days ago.

Settings (GitHub secrets / variables, or environment variables locally):
  GOOGLE_SERVICE_ACCOUNT_JSON  the service account key (the whole JSON text), or
  GOOGLE_APPLICATION_CREDENTIALS  a path to that file
  GSC_SITE_URL     e.g. sc-domain:example.com  or  https://example.com/
  GA4_PROPERTY_ID  the numeric property ID, e.g. 123456789
  BING_API_KEY     Bing Webmaster Tools API key (Settings → API access); BING_SITE_URL e.g. https://example.com/
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


# ---------------------------------------------------------------- Bing Webmaster Tools

def bing_call(method, site, key):
    import urllib.request
    url = (f"https://ssl.bing.com/webmaster/api.svc/json/{method}?"
           + urllib.parse.urlencode({"siteUrl": site, "apikey": key}))
    with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=60) as r:
        return json.load(r).get("d") or []


def bing_date(v):
    """Bing returns dates as "/Date(1700000000000-0800)/"."""
    import re
    m = re.search(r"Date\((-?\d+)", str(v))
    return dt.datetime.fromtimestamp(int(m.group(1)) / 1000, dt.timezone.utc).date() if m else None


def bing_window(rows, start, end, key_field):
    agg = {}
    for r in rows:
        d = bing_date(r.get("Date"))
        if not d or not (start <= d <= end):
            continue
        k = r.get(key_field) or ""
        a = agg.setdefault(k, {"clicks": 0, "impressions": 0, "pos_x_impr": 0.0})
        imp = r.get("Impressions") or 0
        a["clicks"] += r.get("Clicks") or 0
        a["impressions"] += imp
        a["pos_x_impr"] += (r.get("AvgImpressionPosition") or 0) * imp
    return [[k, v["clicks"], v["impressions"], round(v["clicks"] / v["impressions"], 5) if v["impressions"] else 0,
             round(v["pos_x_impr"] / v["impressions"], 2) if v["impressions"] else 0]
            for k, v in sorted(agg.items(), key=lambda x: -x[1]["impressions"])]


def pull_bing(site, key, out, cur, prev):
    m = ["clicks", "impressions", "ctr", "position"]
    q, pg = bing_call("GetQueryStats", site, key), bing_call("GetPageStats", site, key)
    for tag, (a, b) in (("cur", cur), ("prev", prev)):
        write_csv(f"{out}/bing_query_{tag}.csv", ["query"] + m, bing_window(q, a, b, "Query"))
        write_csv(f"{out}/bing_page_{tag}.csv", ["page"] + m, bing_window(pg, a, b, "Query"))


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
    bing_key, bing_site = os.environ.get("BING_API_KEY"), os.environ.get("BING_SITE_URL")
    if s is None and not bing_key:
        print("No Google credentials (GOOGLE_SERVICE_ACCOUNT_JSON) and no BING_API_KEY. Skipping — see analytics/README.md.")
        return 0
    out = os.path.join(HERE, "data", today.isoformat())
    os.makedirs(out, exist_ok=True)
    meta = {"pulled": today.isoformat(), "current": [d.isoformat() for d in cur],
            "previous": [d.isoformat() for d in prev], "daily": [d.isoformat() for d in daily], "sources": []}

    site, prop, failed = os.environ.get("GSC_SITE_URL"), os.environ.get("GA4_PROPERTY_ID"), []
    if site and s is not None:
        try:
            pull_gsc(s, site, out, cur, prev, daily)
            meta["sources"].append("gsc")
            print("Search Console: pulled", site)
        except Exception as e:
            failed.append(f"Search Console: {e}")
    else:
        print("GSC_SITE_URL not set; skipped Search Console.")
    if prop and s is not None:
        try:
            pull_ga4(s, prop, out, cur, prev, daily)
            meta["sources"].append("ga4")
            print("GA4: pulled property", prop)
        except Exception as e:
            failed.append(f"GA4: {e}")
    else:
        print("GA4_PROPERTY_ID not set; skipped GA4.")
    if bing_key and bing_site:
        try:
            pull_bing(bing_site, bing_key, out, cur, prev)
            meta["sources"].append("bing")
            print("Bing: pulled", bing_site)
        except Exception as e:
            failed.append(f"Bing: {e}")
    elif bing_key:
        print("BING_SITE_URL not set; skipped Bing.")
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
