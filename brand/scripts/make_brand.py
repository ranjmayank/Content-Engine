#!/usr/bin/env python3
"""Generate a starter brand kit from engine.config.json.

Writes to brand/:
  avatar-1000.png          square profile picture (initials on ink, accent bar)
  wordmark-light.png       brand name, ink on paper
  wordmark-dark.png        brand name, paper on ink
  og-1200x630.png          default Open Graph / link-preview image
  cover-1584x396.png       LinkedIn banner
  cover-1640x624.png       Facebook cover
  quote-card-1080x1350.png a quote-card template (replace the text in Canva or re-run with --quote)

Usage:  pip install Pillow  &&  python3 brand/scripts/make_brand.py [--quote "One sharp line"]
Colours and names come from engine.config.json (brand.name, brand.site_name, brand.tagline, colors.*).
Fonts: Outfit and Geist Mono (SIL Open Font License, in brand/scripts/fonts/).
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(BRAND_DIR)
FONTS = os.path.join(HERE, "fonts")


def cfg():
    try:
        return json.load(open(os.path.join(ROOT, "engine.config.json")))
    except FileNotFoundError:
        return {}


C = cfg()
B = C.get("brand", {})
NAME = B.get("name") or "Your Brand"
SITE = B.get("site_name") or "example.com"
TAG = B.get("tagline") or ""
COL = {"ink": "#16161E", "accent": "#F5A623", "paper": "#FAF7F2", **C.get("colors", {})}
INK, ACC, PAPER = COL["ink"], COL["accent"], COL["paper"]


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def bold(s):
    return font("Outfit-Bold.ttf", s)


def regular(s):
    return font("Outfit-Regular.ttf", s)


def mono(s):
    return font("GeistMono-Regular.ttf", s)


def initials(name):
    parts = [p for p in name.replace("-", " ").split() if p[:1].isalnum()]
    return ("".join(p[0] for p in parts[:2]) or name[:2]).upper()


def fit(draw, text, maker, max_w, start):
    size = start
    while size > 10:
        f = maker(size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return maker(10)


def wrap(draw, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def avatar():
    s = 1000
    im = Image.new("RGB", (s, s), INK)
    d = ImageDraw.Draw(im)
    f = bold(420)
    t = initials(NAME)
    w = d.textlength(t, font=f)
    d.text(((s - w) / 2, 250), t, font=f, fill=PAPER)
    d.rectangle([s * 0.3, 760, s * 0.7, 790], fill=ACC)
    im.save(os.path.join(BRAND_DIR, "avatar-1000.png"))


def wordmark(bg, fg, fname):
    w, h = 1600, 400
    im = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(im)
    f = fit(d, NAME, bold, w - 200, 180)
    tw = d.textlength(NAME, font=f)
    d.text(((w - tw) / 2, 90), NAME, font=f, fill=fg)
    d.rectangle([(w - tw) / 2, 300, (w - tw) / 2 + 120, 312], fill=ACC)
    im.save(os.path.join(BRAND_DIR, fname))


def banner(w, h, fname):
    im = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(im)
    pad = int(w * 0.06)
    f = fit(d, NAME, bold, w * 0.6, int(h * 0.28))
    d.text((pad, h * 0.22), NAME, font=f, fill=PAPER)
    if TAG:
        ft = fit(d, TAG, regular, w * 0.7, int(h * 0.11))
        d.text((pad, h * 0.22 + f.size * 1.2), TAG, font=ft, fill=ACC)
    fm = mono(max(14, int(h * 0.06)))
    d.text((pad, h * 0.8), SITE, font=fm, fill=PAPER)
    d.rectangle([w - pad - int(w * 0.12), h * 0.2, w - pad, h * 0.2 + 10], fill=ACC)
    im.save(os.path.join(BRAND_DIR, fname))


def quote_card(text):
    w, h = 1080, 1350
    im = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(im)
    pad = 110
    d.rectangle([pad, 180, pad + 120, 196], fill=ACC)
    f = bold(84)
    y = 280
    for line in wrap(d, text, f, w - 2 * pad):
        d.text((pad, y), line, font=f, fill=INK)
        y += 104
    d.text((pad, h - 200), NAME, font=bold(40), fill=INK)
    d.text((pad, h - 145), SITE, font=mono(30), fill=INK)
    im.save(os.path.join(BRAND_DIR, "quote-card-1080x1350.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quote", default="One sharp line from your post goes here.")
    a = ap.parse_args()
    avatar()
    wordmark(PAPER, INK, "wordmark-light.png")
    wordmark(INK, PAPER, "wordmark-dark.png")
    banner(1200, 630, "og-1200x630.png")
    banner(1584, 396, "cover-1584x396.png")
    banner(1640, 624, "cover-1640x624.png")
    quote_card(a.quote)
    print("Brand kit written to brand/ for", NAME)


if __name__ == "__main__":
    main()
