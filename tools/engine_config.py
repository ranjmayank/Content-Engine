"""Shared loader for engine.config.json and the pillar list.

Every script reads brand, site, timezone and colours from here, so changing your niche
means editing engine.config.json (or re-running setup/init.py) — never the code.
"""
import datetime as dt
import json
import os
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "engine.config.json")
TERRITORIES_PATH = os.path.join(ROOT, "scanner", "sources", "territories.json")


def load():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


CFG = load()
BRAND = CFG.get("brand", {})
SITE = BRAND.get("site", "")
SITE_NAME = BRAND.get("site_name") or urlparse(SITE).netloc or "Your site"
BRAND_NAME = BRAND.get("name") or SITE_NAME
COLORS = {"ink": "#16161E", "accent": "#F5A623", "paper": "#FAF7F2", **CFG.get("colors", {})}
REPO = CFG.get("repo", "")


def pillars():
    """Pillar names in order, from scanner/sources/territories.json (falls back to the config)."""
    try:
        with open(TERRITORIES_PATH) as f:
            t = json.load(f)
        return t.get("order") or list(t.get("keywords", {}))
    except FileNotFoundError:
        return [p["name"] for p in CFG.get("niche", {}).get("pillars", [])]


def tz():
    """The owner's timezone as a tzinfo (IANA name in cadence.timezone; UTC if unknown)."""
    name = CFG.get("cadence", {}).get("timezone", "UTC")
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name)
    except Exception:
        return dt.timezone.utc


def today():
    return dt.datetime.now(tz()).date()
