#!/usr/bin/env python3
"""Add site-wide metadata to every page, and write sitemap.xml, robots.txt and 404.html.

Run this LAST, after the other generators. For each HTML page (generated or hand-written) it inserts, between
<!-- meta --> markers in <head>: a meta description, Open Graph and Twitter card tags for link previews, a
canonical URL, and the favicon. It's idempotent: re-running replaces the block. Redirect pages are skipped.

The description is taken from the page itself (a board's SVG <desc>, a guide's subtitle, or the first paragraph
in the header), so it never needs maintaining by hand.

og-image.png is made from _generator/og-card.html with headless Chrome (see CLAUDE.md); it rarely changes.

Run:  python3 _generator/build_meta.py
"""
import re
import sys
from html import escape, unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import SITE  # noqa: E402

OUT = Path(__file__).resolve().parent.parent
BASE = f"https://{SITE}/"
SITE_NAME = "Agile Ways of Working Toolkit"


def is_redirect(s):
    return 'http-equiv="refresh"' in s


def text_of(fragment):
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def describe(s):
    for pat in (r'<desc id="mg-desc">(.*?)</desc>',                      # boards: the SVG description
                r'<header class="masthead">.*?<p>(.*?)</p>',             # guides: the subtitle
                r"<header>.*?<p>(.*?)</p>",                               # index, role page, glossary, catalogues
                r'<header class="head">.*?<p>(.*?)</p>'):                 # cheat sheets
        m = re.search(pat, s, re.S)
        if m:
            d = text_of(m.group(1))
            if d:
                return d if len(d) <= 200 else d[:197].rsplit(" ", 1)[0] + "…"
    return "Free, printable agile boards, facilitator guides and playbooks for teams, facilitators and leaders."


def meta_block(name, title, desc):
    url = BASE if name == "index.html" else BASE + name
    full = title if title == SITE_NAME else f"{title} · {SITE_NAME}"
    e = lambda v: escape(v, quote=True)
    return "\n".join([
        "<!-- meta -->",
        f'<meta name="description" content="{e(desc)}">',
        f'<link rel="canonical" href="{url}">',
        '<link rel="icon" href="favicon.svg" type="image/svg+xml">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:title" content="{e(full)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{BASE}og-image.png">',
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        "<!-- /meta -->",
    ])


def build():
    pages = []
    for p in sorted(OUT.glob("*.html")):
        if p.name == "404.html":
            continue
        s = p.read_text(encoding="utf-8")
        if is_redirect(s):
            continue
        s = re.sub(r"<!-- meta -->.*?<!-- /meta -->\n", "", s, flags=re.S)
        title = text_of(re.search(r"<title>(.*?)</title>", s, re.S).group(1))
        block = meta_block(p.name, title, describe(s))
        s = re.sub(r"(<title>.*?</title>\n)", lambda m: m.group(1) + block + "\n", s, count=1, flags=re.S)
        p.write_text(s, encoding="utf-8")
        pages.append(p.name)

    urls = "\n".join(f"  <url><loc>{BASE if n == 'index.html' else BASE + n}</loc></url>" for n in pages)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8")

    # 404 page: absolute links, because GitHub Pages serves it from any missing path
    (OUT / "404.html").write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found · {SITE_NAME}</title>
<link rel="icon" href="{BASE}favicon.svg" type="image/svg+xml">
<style>
html,body{{margin:0;background:#0C1A2E;color:#fff;font-family:Geist,Inter,system-ui,sans-serif;}}
body{{min-height:100vh;display:flex;align-items:center;justify-content:center;border-top:6px solid #eb6c36;box-sizing:border-box;padding:24px;}}
main{{max-width:560px;}}
h1{{font:400 46px/1.1 'Instrument Serif',Georgia,serif;margin:0 0 12px;}}
p{{color:#94A3B8;line-height:1.6;margin:0 0 20px;}}
a{{display:inline-block;margin:0 8px 8px 0;color:#fff;background:rgba(255,255,255,.08);border-radius:6px;padding:8px 12px;text-decoration:none;font-size:14px;}}
a:hover{{background:#eb6c36;}}
a.primary{{background:#eb6c36;}}
</style>
</head>
<body><main>
<h1>That page isn't here</h1>
<p>It may have moved or been renamed. Every tool is listed on the home page, where you can search by name or filter by role.</p>
<a class="primary" href="{BASE}">All tools</a><a href="{BASE}start-here-by-role.html">Tools by role</a><a href="{BASE}scenarios.html">Scenario Playbook</a><a href="{BASE}glossary.html">Glossary</a>
</main></body>
</html>
""", encoding="utf-8")
    print(f"added metadata to {len(pages)} pages; wrote sitemap.xml, robots.txt, 404.html")


if __name__ == "__main__":
    build()
