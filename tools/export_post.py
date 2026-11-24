#!/usr/bin/env python3
"""Export a finished post (the blog-post skill's output format) to a static site as Markdown with front matter.

  python3 tools/export_post.py content/blog/2026-01-15-usage-based-pricing.md            # uses publishing.static_site
  python3 tools/export_post.py post.md --site ../my-site --dir src/content/blog --fm toml
  python3 tools/export_post.py post.md --stdout                                         # print instead of writing

Settings (engine.config.json → publishing.static_site):
  repo_path   path to your site's repo on disk (e.g. ../my-astro-site)
  content_dir where posts live in it (Astro: src/content/blog · Next.js/MDX: content/posts · Hugo: content/posts ·
              Jekyll: _posts · Eleventy: posts)
  front_matter  yaml (all of the above) or toml (Hugo)
  filename    pattern with {date} and {slug}, e.g. "{date}-{slug}.md" (Jekyll needs the date) or "{slug}.md"
  format      markdown or mdx
  url_pattern the post's public path, e.g. "/blog/{slug}/" (used for the canonical URL)

Front matter written: title, description, slug, date, updated, author, category, tags, image, canonical, faq
(question/answer pairs from the FAQ section), schema (the JSON-LD block, if present). Rename keys in your
site's content schema if it expects different names.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_config as EC  # noqa: E402

FIELDS = {"slug": "slug", "meta title": "meta_title", "meta description": "description", "primary keyword": "keyword",
          "secondary keywords": "keywords", "tier": "tier", "category": "category", "tags": "tags",
          "last updated": "updated", "date": "date", "published": "date", "featured image": "image", "author": "author"}


def parse(text):
    meta, lines = {}, text.splitlines()
    title, i = "", 0
    while i < len(lines) and not lines[i].startswith("# "):
        i += 1
    if i < len(lines):
        title = lines[i][2:].strip()
        i += 1
    while i < len(lines) and lines[i].strip() != "---":
        m = re.match(r"\s*([A-Za-z ]+?)\s*:\s*(.+)$", lines[i])
        if m and m.group(1).lower() in FIELDS:
            meta[FIELDS[m.group(1).lower()]] = m.group(2).strip()
        i += 1
    rest = "\n".join(lines[i + 1:])
    # the body ends where the hand-over notes start ("---" then "Schema", "Images", "Source cards"…)
    parts = re.split(r"\n---\s*\n(?=\s*(?:\*\*)?(?:Schema|Images|Internal links|Source cards|Cascade))", rest, maxsplit=1)
    body = parts[0].strip()
    notes = parts[1] if len(parts) > 1 else ""
    schema = None
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", notes, re.S)
    if m:
        try:
            schema = json.loads(m.group(1))
        except json.JSONDecodeError:
            schema = None
    faq = []
    fm = re.search(r"^##\s+(?:Frequently asked questions|FAQs?)\s*$(.*?)(?=^##\s|\Z)", body, re.S | re.M | re.I)
    if fm:
        for q, a in re.findall(r"\*\*(.+?)\*\*\s*\n+(.+?)(?=\n\s*\*\*|\Z)", fm.group(1), re.S):
            faq.append({"question": q.strip(), "answer": " ".join(a.split())})
    return title, meta, body, faq, schema


def listify(v):
    return [x.strip() for x in re.split(r"[,·]", v) if x.strip()] if isinstance(v, str) else (v or [])


def yaml_val(v, indent=0):
    pad = " " * indent
    if isinstance(v, list):
        if not v:
            return " []"
        out = ""
        for x in v:
            if isinstance(x, dict):
                items = list(x.items())
                out += f"\n{pad}- {items[0][0]}: {json.dumps(items[0][1], ensure_ascii=False)}"
                for k, vv in items[1:]:
                    out += f"\n{pad}  {k}: {json.dumps(vv, ensure_ascii=False)}"
            else:
                out += f"\n{pad}- {json.dumps(x, ensure_ascii=False)}"
        return out
    if isinstance(v, dict):
        return " " + json.dumps(v, ensure_ascii=False)
    return " " + json.dumps(v, ensure_ascii=False)


def front_matter(d, kind):
    if kind == "toml":
        out = ["+++"]
        for k, v in d.items():
            if k == "faq":
                continue
            if isinstance(v, dict):          # TOML has no JSON objects: store JSON-LD as a string
                v = json.dumps(v, ensure_ascii=False)
            out.append(f"{k} = {json.dumps(v, ensure_ascii=False)}")
        for f in d.get("faq", []):
            out += ["", "[[faq]]", f"question = {json.dumps(f['question'], ensure_ascii=False)}",
                    f"answer = {json.dumps(f['answer'], ensure_ascii=False)}"]
        return "\n".join(out + ["+++", ""])
    return "---\n" + "\n".join(f"{k}:{yaml_val(v)}" for k, v in d.items()) + "\n---\n"


def main():
    ss = EC.CFG.get("publishing", {}).get("static_site", {})
    ap = argparse.ArgumentParser()
    ap.add_argument("post")
    ap.add_argument("--site", default=ss.get("repo_path", ""))
    ap.add_argument("--dir", default=ss.get("content_dir", "content/blog"))
    ap.add_argument("--fm", default=ss.get("front_matter", "yaml"), choices=["yaml", "toml"])
    ap.add_argument("--filename", default=ss.get("filename", "{slug}.md"))
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args()

    title, meta, body, faq, schema = parse(open(a.post).read())
    if not title:
        sys.exit("No '# Title' line found — is this the blog-post skill's output format?")
    slug = meta.get("slug", "").strip("/ ") or re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    date = meta.get("date") or meta.get("updated") or EC.today().isoformat()
    author = re.split(r"\s+[—-]\s+", meta.get("author", ""))[0] or EC.CFG.get("author", {}).get("name", "")
    site = EC.SITE.rstrip("/")
    d = {"title": meta.get("meta_title") and title or title, "description": meta.get("description", ""), "slug": slug,
         "date": date, "updated": meta.get("updated", date), "author": author, "category": meta.get("category", ""),
         "tags": listify(meta.get("tags", "")), "image": meta.get("image", ""),
         "canonical": site + ss.get("url_pattern", "/{slug}/").format(slug=slug, date=date[:10]) if site else ""}
    if meta.get("meta_title") and meta["meta_title"] != title:
        d["seo_title"] = meta["meta_title"]
    if faq:
        d["faq"] = faq
    if schema:
        d["schema"] = schema
    d = {k: v for k, v in d.items() if v not in ("", [], None)}
    # drop the H1 (the site template renders the title) and the meta lines
    out = front_matter(d, a.fm) + "\n" + body.strip() + "\n"
    if a.stdout or not a.site:
        if not a.site and not a.stdout:
            print("(no publishing.static_site.repo_path set — printing instead)\n", file=sys.stderr)
        print(out)
        return
    name = a.filename.format(date=date[:10], slug=slug)
    dest = os.path.join(os.path.expanduser(a.site), a.dir, name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w").write(out)
    print("wrote", dest)


if __name__ == "__main__":
    main()
