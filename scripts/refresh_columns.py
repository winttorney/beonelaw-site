"""Rewrite only the auto-managed column lists in site/*.html from data/posts.json.

Everything outside the <!--AUTO:...--> ... <!--/AUTO--> markers is hand-edited
content and is never touched. Area order and classification rules live in
data/areas.json (keep its order the same as the site's menus).

Blocks:
  index.html         <!--AUTO:latest-->       newest 6 columns
  <area>.html        <!--AUTO:area-->         up to 8 columns of that area + "전체 보기 (N)" link
  cases.html         <!--AUTO:cases-->        tab buttons + one panel per tab
  sitemap.xml        regenerated from the list of site pages
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
TISTORY = "https://beone1.tistory.com"
BASE = "https://beonelaw.com"

AREAS = json.load(open(os.path.join(ROOT, "data", "areas.json"), encoding="utf-8"))
POSTS = [p for p in json.load(open(os.path.join(ROOT, "data", "posts.json"), encoding="utf-8"))
         if "사이트 맵" not in p["title"] and "사이트맵" not in p["title"]]
POSTS.sort(key=lambda p: -p["id"])


def classify(p):
    text = p["title"] + " " + " ".join(p.get("tags", []))
    return [a["slug"] for a in AREAS if p.get("category") in a["cats"] or any(k in text for k in a["kw"])]


for p in POSTS:
    p["areas"] = classify(p)


def plist(posts):
    return '<ul class="posts">' + "".join(
        f'<li><a href="{TISTORY}/{p["id"]}" target="_blank" rel="noopener">{html.escape(p["title"])}</a></li>'
        for p in posts) + "</ul>"


def replace_block(text, name, new, path):
    pat = re.compile(r"(<!--AUTO:%s-->).*?(<!--/AUTO-->)" % re.escape(name), re.S)
    if len(pat.findall(text)) != 1:
        raise SystemExit(f"{path}: expected exactly one AUTO:{name} block")
    return pat.sub(lambda m: m.group(1) + new + m.group(2), text)


def update(fname, name, new):
    path = os.path.join(SITE, fname)
    text = open(path, encoding="utf-8").read()
    out = replace_block(text, name, new, fname)
    if out != text:
        open(path, "w", encoding="utf-8").write(out)
        print("updated", fname)


# home: newest 6
update("index.html", "latest", plist(POSTS[:6]))

# area pages: area-specific columns first, then shared ones; newest first within each
for a in AREAS:
    rel = sorted([p for p in POSTS if a["slug"] in p["areas"]], key=lambda p: (len(p["areas"]), -p["id"]))
    if rel:
        block = (plist(rel[:8]) + f'<p class="note"><a href="cases.html#{a["slug"]}" style="color:var(--link)">'
                 f'{a["name"]} 칼럼 전체 보기 ({len(rel)}) →</a></p>')
    else:
        block = '<p class="note">이 분야 칼럼이 곧 업데이트됩니다.</p>'
    update(f'{a["slug"]}.html', "area", block)

# cases: tabs and panels share one order (they are paired by position)
tabs = [("all", "전체", POSTS)] + [(a["slug"], a["name"], [p for p in POSTS if a["slug"] in p["areas"]]) for a in AREAS]
tab_html = '<div class="tabs">' + "".join(
    f'<button class="tab{" on" if i == 0 else ""}" type="button" data-key="{k}">{n} ({len(v)})</button>'
    for i, (k, n, v) in enumerate(tabs)) + "</div>\n  "
panels = "".join(f'<div class="panel{" on" if i == 0 else ""}">{plist(v)}</div>' for i, (k, n, v) in enumerate(tabs))
update("cases.html", "cases", tab_html + panels)

# stylesheet version stamp, so browsers fetch a changed style.css right away
import hashlib
ver = hashlib.sha256(open(os.path.join(SITE, "style.css"), "rb").read()).hexdigest()[:8]
for f in sorted(os.listdir(SITE)):
    if f.endswith(".html"):
        path = os.path.join(SITE, f)
        text = open(path, encoding="utf-8").read()
        out = re.sub(r'href="style\.css(\?v=[0-9a-f]+)?"', f'href="style.css?v={ver}"', text)
        if out != text:
            open(path, "w", encoding="utf-8").write(out)
            print("stamped", f)

# sitemap
pages = sorted(f for f in os.listdir(SITE) if f.endswith(".html"))
urls = [BASE + "/"] + [f"{BASE}/{f[:-5]}" for f in pages if f != "index.html"]
sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(SITE, "sitemap.xml"), "w").write(sm)
print("columns:", len(POSTS))
