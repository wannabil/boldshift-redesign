#!/usr/bin/env python3
"""SEO/technical checks against a running server. Usage: python3 tests/check.py [base_url]"""
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:4823").rstrip("/")
PAGES = ["/", "/individuals", "/corporate-training", "/about", "/free-tools", "/contact"]
fails = []


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.ld, self._ld, self.title, self._t = [], [], False, "", False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, a))
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld = True
            self.ld.append("")
        if tag == "title":
            self._t = True

    def handle_endtag(self, tag):
        self._ld = self._t = False if tag in ("script", "title") else self._ld

    def handle_data(self, d):
        if self._ld:
            self.ld[-1] += d
        if self._t:
            self.title += d


def check(cond, msg):
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond:
        fails.append(msg)


internal = set()
for path in PAGES:
    st, hd, body = get(path)
    print(path)
    check(st == 200, f"{path} 200 (got {st})")
    p = P()
    p.feed(body)
    meta = {a.get("name") or a.get("property"): a.get("content") for t, a in p.tags if t == "meta"}
    links = {a.get("rel"): a.get("href") for t, a in p.tags if t == "link"}
    check(10 <= len(p.title) <= 65, f"title length {len(p.title)}: {p.title}")
    d = meta.get("description") or ""
    check(70 <= len(d) <= 165, f"description length {len(d)}")
    check(bool(links.get("canonical")), f"canonical {links.get('canonical')}")
    check(sum(1 for t, _ in p.tags if t == "h1") == 1, "exactly one h1")
    for k in ("og:title", "og:description", "og:image", "og:url", "twitter:card"):
        check(bool(meta.get(k)), f"{k} present")
    check(any(t == "html" and a.get("lang") for t, a in p.tags), "html lang set")
    ok_ld = True
    types = []
    for raw in p.ld:
        try:
            data = json.loads(raw)
            types += [g.get("@type") for g in data.get("@graph", [data])]
        except Exception as ex:  # noqa
            ok_ld = False
    check(ok_ld and p.ld, f"JSON-LD parses: {types}")
    imgs = [a for t, a in p.tags if t == "img"]
    check(all("alt" in a and a.get("width") and a.get("height") for a in imgs), f"{len(imgs)} imgs have alt+width+height")
    for t, a in p.tags:
        h = a.get("href") or a.get("src") or ""
        if (t in ("a", "link", "script", "img")) and h.startswith("/") and not h.startswith("//"):
            internal.add(h.split("#")[0].split("?")[0] or "/")

print("internal links/assets")
for h in sorted(internal):
    st, _, _ = get(h)
    check(st == 200, f"{h} -> {st}")

for f in ("/robots.txt", "/sitemap.xml", "/llms.txt", "/site.webmanifest", "/favicon.ico"):
    st, hd, body = get(f)
    check(st == 200, f"{f} -> {st}")
st, _, sm = get("/sitemap.xml")
check(len(re.findall("<loc>", sm)) == len(PAGES), "sitemap lists every page")
st, _, _ = get("/definitely-missing")
check(st == 404, f"unknown URL returns 404 (got {st})")

print("\nFAILED: %d" % len(fails) if fails else "\nALL CHECKS PASSED")
sys.exit(1 if fails else 0)
