#!/usr/bin/env python3
"""Set the GitHub Actions schedules from your local times in engine.config.json.

GitHub cron runs in UTC. This converts cadence.times (your local clock, in cadence.timezone)
to UTC and rewrites the `- cron:` line tagged `# engine:<job>` in each workflow.

  cadence.times.analytics  "07:45"      daily Search Console + GA4 pull
  cadence.times.scan       "08:00"      daily news scan
  cadence.times.topic_list "10:15"      daily topic list (Claude API workflow, or your Claude scheduled task)
  cadence.times.email      "11:00"      daily topic email (leave time after the topic-list task)
  cadence.times.seo_audit  "Mon 07:00"  weekly SEO audit

Usage: python3 setup/schedule.py            (prints the result; --dry-run to only print)
GitHub may start scheduled jobs a few minutes late at busy times; that's normal.
"""
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF = os.path.join(ROOT, ".github", "workflows")
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DEFAULTS = {"analytics": "07:45", "scan": "08:00", "topic_list": "10:15", "email": "11:00", "seo_audit": "Mon 07:00"}


def to_cron(spec, tzname):
    from zoneinfo import ZoneInfo
    m = re.fullmatch(r"\s*(?:(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+)?(\d{1,2}):(\d{2})\s*", spec)
    if not m:
        raise ValueError(f"can't read time '{spec}' (use 'HH:MM' or 'Mon HH:MM')")
    day, h, mi = m.group(1), int(m.group(2)), int(m.group(3))
    # A reference week (2026-01-05 is a Monday); outside DST, so set DST-sensitive zones in winter time
    ref = dt.date(2026, 1, 5) + dt.timedelta(days=DAYS.index(day) if day else 0)
    local = dt.datetime(ref.year, ref.month, ref.day, h, mi, tzinfo=ZoneInfo(tzname))
    u = local.astimezone(dt.timezone.utc)
    if day:
        cron_dow = (u.weekday() + 1) % 7      # cron: 0 = Sunday
        return f"{u.minute} {u.hour} * * {cron_dow}"
    return f"{u.minute} {u.hour} * * *"


def main():
    cfg = json.load(open(os.path.join(ROOT, "engine.config.json")))
    cad = cfg.get("cadence", {})
    tzname = cad.get("timezone", "UTC")
    times = {**DEFAULTS, **cad.get("times", {})}
    dry = "--dry-run" in sys.argv
    for f in sorted(os.listdir(WF)):
        path = os.path.join(WF, f)
        s = open(path).read()
        changed = s
        for job, spec in times.items():
            cron = to_cron(spec, tzname)
            changed = re.sub(rf'- cron: "[^"]*"(\s+# engine:{job}\b)', f'- cron: "{cron}"\\1', changed)
        if changed != s:
            for job, spec in times.items():
                if f"# engine:{job}" in s:
                    print(f"{f}: {job} {spec} {tzname} → cron '{to_cron(spec, tzname)}' (UTC)")
            if not dry:
                open(path, "w").write(changed)
        else:
            for job, spec in times.items():
                if f"# engine:{job}" in s:
                    print(f"{f}: {job} already at {spec} {tzname}")
    if "America/" in tzname or "Europe/" in tzname or "Australia/" in tzname:
        print("Note: your timezone has daylight saving; GitHub cron is fixed UTC, so jobs shift by an hour in summer.")


if __name__ == "__main__":
    main()
