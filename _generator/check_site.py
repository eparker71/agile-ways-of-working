#!/usr/bin/env python3
"""Check the built site for problems. Exits non-zero if anything fails, so it can gate CI.

Checks:
  - every relative link and #anchor in every HTML page points to something that exists
  - redirect pages point to a page that exists
  - every page has a title, a meta description and link-preview metadata
  - every SVG and every part of every Word file is well-formed XML
  - every page in sitemap.xml exists
  - every board has an up-to-date A3 PDF in pdf/
  - text on one page of each kind meets WCAG AA contrast (needs Chrome)
  - the two cheat sheets have no overflowing panels and print to the expected number of pages
    (needs Google Chrome or Chromium; skipped with a warning if neither is found)

Run:  python3 _generator/check_site.py
"""
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
from brand import PUBLISH_AT  # noqa: E402
errors, warnings = [], []


def fail(msg):
    errors.append(msg)


def pages():
    return paths.pages()


def rel(p):
    return p.relative_to(OUT).as_posix()


def files(pattern):
    """Site files matching pattern, at the root and in each folder."""
    return [p for d in ("", *paths.FOLDERS) for p in sorted((OUT / d).glob(pattern))]


def check_links():
    ids = {}
    for p in pages():
        s = p.read_text(encoding="utf-8")
        ids[p.resolve()] = set(re.findall(r'\bid="([^"]+)"', s))
    for p in pages():
        s = p.read_text(encoding="utf-8")
        for href in re.findall(r'\b(?:href|src)="([^"]+)"', s):
            if href.startswith(("http:", "https:", "mailto:", "javascript:", "data:", "//")) or href in ("#",) or "'+" in href:
                continue
            target, _, anchor = href.partition("#")
            dest = (p.parent / target).resolve() if target else p.resolve()
            if not dest.exists():
                fail(f"{rel(p)}: broken link to {href}")
            elif not dest.is_relative_to(OUT):
                fail(f"{rel(p)}: link points outside the site: {href}")
            elif anchor and dest.suffix == ".html" and anchor not in ids.get(dest, set()) \
                    and not anchor.startswith(("role=", "letter-")) and dest != OUT / "index.html":
                fail(f"{rel(p)}: link to missing anchor {href}")
        # a bare file name that belongs in another folder means a page was written without paths.write_page
        for href in re.findall(r'\b(?:href|src)="([a-z0-9][^"/#?]*\.(?:html|svg|docx))', s):
            want = paths.folder(href)
            here = paths.folder(p.name)
            if want != here and p.parent == OUT / here:
                fail(f"{rel(p)}: {href} belongs in {want or 'the root'}/ (write the page with paths.write_page)")
        m = re.search(r'http-equiv="refresh" content="0; url=([^"]+)"', s)
        if m and not (p.parent / m.group(1)).exists():
            fail(f"{rel(p)}: redirects to missing {m.group(1)}")


def check_placement():
    """Every file is in the folder paths.folder() says it belongs in."""
    for p in files("*.html") + files("*.svg") + files("*.docx"):
        if p.name in ("404.html", "favicon.svg"):
            continue
        want = paths.folder(p.name)
        if p.parent != (OUT / want if want else OUT):
            fail(f"{rel(p)} should be in {want or 'the root'}/")


def check_metadata():
    for p in pages():
        s = p.read_text(encoding="utf-8")
        if 'http-equiv="refresh"' in s or p.name == "404.html":
            continue
        if not re.search(r"<title>[^<]+</title>", s):
            fail(f"{rel(p)}: no <title>")
        if 'name="description"' not in s:
            fail(f"{rel(p)}: no meta description (run build_meta.py)")
        if 'property="og:image"' not in s:
            fail(f"{rel(p)}: no link-preview metadata (run build_meta.py)")
        if '<html lang="en"' not in s:
            fail(f"{rel(p)}: <html> has no lang attribute")


def check_xml():
    for f in files("*.svg"):
        try:
            xml.dom.minidom.parse(str(f))
        except Exception as e:  # noqa: BLE001
            fail(f"{rel(f)}: invalid SVG ({e})")
    for f in files("*.docx"):
        try:
            with zipfile.ZipFile(f) as z:
                for n in z.namelist():
                    xml.dom.minidom.parseString(z.read(n))
        except Exception as e:  # noqa: BLE001
            fail(f"{rel(f)}: invalid Word file ({e})")


def check_sitemap():
    sm = OUT / "sitemap.xml"
    if not sm.exists():
        fail("sitemap.xml is missing (run build_meta.py)")
        return
    base = f"https://{PUBLISH_AT}/"
    for loc in re.findall(r"<loc>([^<]*)</loc>", sm.read_text()):
        name = loc[len(base):] if loc.startswith(base) else None
        if name is None or (name and not (OUT / name).exists()):
            fail(f"sitemap.xml lists missing page {loc}")


def check_pdfs():
    """Every board has an up-to-date A3 PDF (see build_pdfs.py)."""
    import hashlib
    import json
    man = OUT / "pdf" / "manifest.json"
    if not man.exists():
        fail("pdf/manifest.json is missing (run build_pdfs.py)")
        return
    manifest = json.loads(man.read_text())
    for svg in files("*.svg"):
        if not svg.with_suffix(".html").exists():
            continue
        fp = hashlib.sha256(svg.read_bytes()).hexdigest()[:16]
        if manifest.get(svg.stem) != fp or not (OUT / "pdf" / f"{svg.stem}.pdf").exists():
            fail(f"pdf/{svg.stem}.pdf is missing or out of date (run build_pdfs.py, then build_all.py)")
    from build_pdfs import DOCUMENTS, doc_fingerprint  # imported here: build_pdfs imports this module
    for stem in DOCUMENTS:
        if manifest.get(stem) != doc_fingerprint(stem) or not (OUT / "pdf" / f"{stem}.pdf").exists():
            fail(f"pdf/{stem}.pdf is missing or out of date (run build_pdfs.py, then build_all.py)")


def find_chrome():
    for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        path = shutil.which(c) or (c if os.path.exists(c) else None)
        if path:
            return path
    return None


OVERFLOW_JS = """<script>
// Measure only once the web fonts have loaded: the fallback font is wider and causes false overflows.
function measure(){var r=[];document.querySelectorAll('.panel,.pb,.sheet,.body').forEach(function(e){
if(e.scrollHeight>e.clientHeight+1||e.scrollWidth>e.clientWidth+1){var h=e.querySelector('h2');r.push((h?h.textContent:e.className)+' by '+(e.scrollHeight-e.clientHeight)+'px');}});
var o=document.createElement('pre');o.id='overflow-result';o.textContent='FONTS='+(document.fonts.check('12px Geist')?'ok':'missing')+';OVERFLOW='+r.join(' | ');document.body.appendChild(o);}
var done=false;function go(){if(!done){done=true;setTimeout(measure,300);}}
document.fonts.ready.then(go);setTimeout(go,15000);
</script></body>"""


def check_cheat_sheets():
    chrome = find_chrome()
    if not chrome:
        warnings.append("Chrome not found: skipped the cheat sheet overflow and page-count checks")
        return
    base = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--virtual-time-budget=20000"]
    for name, pages_expected in (("scrum-master-agile-coach-cheat-sheet.html", 2), ("jira-cheat-sheet.html", 1), ("azure-devops-cheat-sheet.html", 1)):
        src = (OUT / name).read_text(encoding="utf-8")
        with tempfile.NamedTemporaryFile("w", suffix=".html", dir=OUT, delete=False, encoding="utf-8") as t:
            t.write(src.replace("</body>", OVERFLOW_JS, 1))
            tmp = t.name
        try:
            dom = subprocess.run(base + ["--window-size=1660,1200", "--dump-dom", f"file://{tmp}"],
                                 capture_output=True, text=True, timeout=120).stdout
            m = re.search(r'<pre id="overflow-result">FONTS=(\w+);OVERFLOW=([^<]*)</pre>', dom)
            if m is None:
                warnings.append(f"{name}: couldn't measure overflow")
            elif m.group(1) != "ok":
                warnings.append(f"{name}: web fonts didn't load, so overflow wasn't checked")
            elif m.group(2).strip():
                fail(f"{name}: panels overflow: {m.group(2).strip()}")
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


CONTRAST_PAGES = ["index.html", "boards/sprint-planning-board.html", "guides/facilitator-guide-sprint-planning.html",
                  "guides/facilitator-guide-marginal-gains.html", "examples/worked-example-adr-board.html", "scrum-master-agile-coach-cheat-sheet.html", "jira-cheat-sheet.html", "azure-devops-cheat-sheet.html",
                  "glossary.html", "start-here-by-role.html", "scenarios.html", "anti-patterns.html", "workshop-recipes.html",
                  "print-pack.html", "about.html", "make-it-yours.html", "404.html"]

CONTRAST_JS = r"""<!doctype html><html><head><meta charset="utf-8"></head><body><iframe id="f" style="width:1300px;height:900px;border:0"></iframe><script>
var B=%s,pages=%s,i=0,res=[];
function lum(c){var a=c.map(function(v){v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*a[0]+.7152*a[1]+.0722*a[2];}
function parse(s){var m=s.match(/[\d.]+/g);return m?m.map(Number):[0,0,0,0];}
function bgOf(el,w){while(el){var c=parse(w.getComputedStyle(el).backgroundColor);if(c.length<4||c[3]>0.9)return c.slice(0,3);
 if(w.getComputedStyle(el).backgroundImage!=='none'&&el.tagName!=='BODY')return null;el=el.parentElement;}return [255,255,255];}
var f=document.getElementById('f');
function next(){if(i>=pages.length){var o=document.createElement('pre');o.id='contrast-result';o.textContent=JSON.stringify(res);document.body.appendChild(o);return;}
f.onload=function(){setTimeout(function(){var d=f.contentDocument,w=f.contentWindow,seen={};
d.querySelectorAll('body *:not(svg):not(svg *)').forEach(function(el){
 var t=[].filter.call(el.childNodes,function(n){return n.nodeType===3&&n.textContent.trim()}).map(function(n){return n.textContent.trim()}).join(' ');
 if(!t||el.closest('[aria-hidden="true"]'))return;var cs=w.getComputedStyle(el);if(cs.display==='none'||cs.visibility==='hidden'||!el.getBoundingClientRect().width)return;
 var fg=parse(cs.color),bg=bgOf(el,w);if(!bg)return;var a=(fg.length>3?fg[3]:1)*parseFloat(cs.opacity);
 var f3=fg.slice(0,3).map(function(v,k){return v*a+bg[k]*(1-a)});var L1=lum(f3),L2=lum(bg),cr=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
 var size=parseFloat(cs.fontSize),large=size>=24||(size>=18.66&&parseInt(cs.fontWeight)>=700);
 if(cr<(large?3:4.5)){var k=cs.color+'/'+bg;if(!seen[k]){seen[k]=1;res.push(pages[i]+': “'+t.slice(0,30)+'” '+cr.toFixed(2)+':1');}}});
 i++;next();},800)};f.src=B+pages[i];}
next();</script></body></html>"""


def check_contrast():
    """WCAG AA text contrast (4.5:1, or 3:1 for large text) on one page of each kind. Board SVGs aren't covered."""
    chrome = find_chrome()
    if not chrome:
        warnings.append("Chrome not found: skipped the contrast check")
        return
    import json
    with tempfile.TemporaryDirectory() as tmp:
        harness = Path(tmp) / "contrast.html"
        harness.write_text(CONTRAST_JS % (json.dumps(f"file://{OUT}/"), json.dumps(CONTRAST_PAGES)), encoding="utf-8")
        dom = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--allow-file-access-from-files",
                              "--window-size=1400,1000", "--virtual-time-budget=120000", "--dump-dom", f"file://{harness}"],
                             capture_output=True, text=True, timeout=300).stdout
    m = re.search(r'<pre id="contrast-result">(.*?)</pre>', dom, re.S)
    if not m:
        warnings.append("couldn't run the contrast check")
        return
    from html import unescape
    for problem in json.loads(unescape(m.group(1))):
        fail(f"low contrast: {problem}")


if __name__ == "__main__":
    check_links()
    check_placement()
    check_metadata()
    check_xml()
    check_sitemap()
    check_pdfs()
    check_cheat_sheets()
    check_contrast()
    for w in warnings:
        print("warning:", w)
    if errors:
        print(f"{len(errors)} problem(s) found:")
        for e in errors:
            print("  ✗", e)
        sys.exit(1)
    print(f"all checks passed ({len(pages())} pages)")
