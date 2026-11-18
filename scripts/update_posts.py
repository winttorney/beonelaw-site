"""Fetch the Tistory RSS feed and merge new posts into posts.json.

Runs on a daily schedule after deployment (GitHub Actions). New posts keep the
Tistory category and tags from the feed; the site generator classifies them
into practice areas (see classify.py). Existing entries are never removed, so
posts older than the feed window stay listed.
"""
import json
import re
import urllib.request
import xml.etree.ElementTree as ET

FEED = "https://beone1.tistory.com/rss"
STORE = "data/posts.json"


def fetch_feed():
    req = urllib.request.Request(FEED, headers={"User-Agent": "beonelaw-site-builder"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    out = []
    for item in root.iter("item"):
        link = item.findtext("link") or ""
        m = re.search(r"/(\d+)(?:$|\?)", link)
        if not m:
            continue
        cats = [c.text or "" for c in item.findall("category")]
        # Tistory puts the blog category first ("비원 법률사무소/형사 사건"), then tags.
        category = cats[0].split("/")[-1].strip() if cats else ""
        tags = [c.strip() for c in cats[1:] if c.strip()]
        out.append({"id": int(m.group(1)), "title": (item.findtext("title") or "").strip(),
                    "category": category, "tags": tags})
    return out


def main():
    try:
        store = json.load(open(STORE, encoding="utf-8"))
    except FileNotFoundError:
        store = []
    by_id = {p["id"]: p for p in store}
    added = 0
    for p in parse(fetch_feed()):
        if p["id"] in by_id:
            by_id[p["id"]].update(title=p["title"], category=p["category"] or by_id[p["id"]]["category"],
                                  tags=p["tags"] or by_id[p["id"]].get("tags", []))
        else:
            by_id[p["id"]] = p
            added += 1
    posts = sorted(by_id.values(), key=lambda x: -x["id"])
    json.dump(posts, open(STORE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"posts: {len(posts)} (new: {added})")


if __name__ == "__main__":
    main()
