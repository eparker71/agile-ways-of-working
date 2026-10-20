#!/usr/bin/env python3
"""Check the built site for problems. Exits non-zero if anything fails, so it can gate CI.

Checks:
  - every relative link and #anchor in every HTML page points to something that exists
  - redirect pages point to a page that exists
  - every page has a title, a meta description and link-preview metadata
  - every SVG and every part of every Word file is well-formed XML
  - every page in sitemap.xml exists
  - the two cheat sheets have no overflowing panels and print to the expected number of pages
    (needs Google Chrome or Chromium; skipped with a warning if neither is found)

Run:  python3 _generator/check_site.py
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.dom.minidom
import zipfile
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
errors, warnings = [], []


def fail(msg):
    errors.append(msg)


def pages():
    return sorted(p for p in OUT.glob("*.html"))


def check_links():
    ids = {}
    for p in pages():
        s = p.read_text(encoding="utf-8")
        ids[p.name] = set(re.findall(r'\bid="([^"]+)"', s))
    for p in pages():
        s = p.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', s):
            if href.startswith(("http:", "https:", "mailto:", "javascript:")) or href in ("#",) or "'+" in href:
                continue
            target, _, anchor = href.partition("#")
            target = target or p.name
            if not (OUT / target).exists():
                fail(f"{p.name}: broken link to {href}")
            elif anchor and target.endswith(".html") and anchor not in ids.get(target, set()) \
                    and not anchor.startswith(("role=", "letter-")) and target != "index.html":
                fail(f"{p.name}: link to missing anchor {href}")
        m = re.search(r'http-equiv="refresh" content="0; url=([^"]+)"', s)
        if m and not (OUT / m.group(1)).exists():
            fail(f"{p.name}: redirects to missing {m.group(1)}")


def check_metadata():
    for p in pages():
        s = p.read_text(encoding="utf-8")
        if 'http-equiv="refresh"' in s or p.name == "404.html":
            continue
        if not re.search(r"<title>[^<]+</title>", s):
            fail(f"{p.name}: no <title>")
        if 'name="description"' not in s:
            fail(f"{p.name}: no meta description (run build_meta.py)")
        if 'property="og:image"' not in s:
            fail(f"{p.name}: no link-preview metadata (run build_meta.py)")
        if '<html lang="en"' not in s:
            fail(f"{p.name}: <html> has no lang attribute")


def check_xml():
    for f in sorted(glob.glob(str(OUT / "*.svg"))):
        try:
            xml.dom.minidom.parse(f)
        except Exception as e:  # noqa: BLE001
            fail(f"{os.path.basename(f)}: invalid SVG ({e})")
    for f in sorted(glob.glob(str(OUT / "*.docx"))):
        try:
            with zipfile.ZipFile(f) as z:
                for n in z.namelist():
                    xml.dom.minidom.parseString(z.read(n))
        except Exception as e:  # noqa: BLE001
            fail(f"{os.path.basename(f)}: invalid Word file ({e})")


def check_sitemap():
    sm = OUT / "sitemap.xml"
    if not sm.exists():
        fail("sitemap.xml is missing (run build_meta.py)")
        return
    for loc in re.findall(r"<loc>https://[^/<]+(?:/[^/<]+)?/([^/<]*)</loc>", sm.read_text()):
        if loc and not (OUT / loc).exists():
            fail(f"sitemap.xml lists missing page {loc}")


def find_chrome():
    for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        path = shutil.which(c) or (c if os.path.exists(c) else None)
        if path:
            return path
    return None


OVERFLOW_JS = """<script>setTimeout(function(){var r=[];document.querySelectorAll('.panel,.pb,.sheet,.body').forEach(function(e){
if(e.scrollHeight>e.clientHeight+1||e.scrollWidth>e.clientWidth+1){var h=e.querySelector('h2');r.push((h?h.textContent:e.className)+' by '+(e.scrollHeight-e.clientHeight)+'px');}});
var o=document.createElement('pre');o.id='overflow-result';o.textContent='OVERFLOW='+r.join(' | ');document.body.appendChild(o);},500)</script></body>"""


def check_cheat_sheets():
    chrome = find_chrome()
    if not chrome:
        warnings.append("Chrome not found: skipped the cheat sheet overflow and page-count checks")
        return
    base = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--virtual-time-budget=6000"]
    for name, pages_expected in (("scrum-master-agile-coach-cheat-sheet.html", 2), ("jira-cheat-sheet.html", 1)):
        src = (OUT / name).read_text(encoding="utf-8")
        with tempfile.NamedTemporaryFile("w", suffix=".html", dir=OUT, delete=False, encoding="utf-8") as t:
            t.write(src.replace("</body>", OVERFLOW_JS, 1))
            tmp = t.name
        try:
            dom = subprocess.run(base + ["--window-size=1660,1200", "--dump-dom", f"file://{tmp}"],
                                 capture_output=True, text=True, timeout=120).stdout
            m = re.search(r'<pre id="overflow-result">OVERFLOW=([^<]*)</pre>', dom)
            if m is None:
                warnings.append(f"{name}: couldn't measure overflow")
            elif m.group(1).strip():
                fail(f"{name}: panels overflow: {m.group(1).strip()}")
            pdf = tmp + ".pdf"
            subprocess.run(base + ["--no-pdf-header-footer", f"--print-to-pdf={pdf}", f"file://{OUT / name}"],
                           capture_output=True, timeout=120)
            if os.path.exists(pdf):
                n = len(re.findall(rb"/Type\s*/Page[^s]", open(pdf, "rb").read()))
                if n != pages_expected:
                    fail(f"{name}: prints to {n} pages, expected {pages_expected}")
                os.remove(pdf)
            else:
                warnings.append(f"{name}: couldn't print to PDF")
        finally:
            os.remove(tmp)


if __name__ == "__main__":
    check_links()
    check_metadata()
    check_xml()
    check_sitemap()
    check_cheat_sheets()
    for w in warnings:
        print("warning:", w)
    if errors:
        print(f"{len(errors)} problem(s) found:")
        for e in errors:
            print("  ✗", e)
        sys.exit(1)
    print(f"all checks passed ({len(pages())} pages)")
