#!/usr/bin/env python3
"""Make print-ready A3 PDFs of every board and poster, in pdf/.

Needs Google Chrome or Chromium. Not part of build_all.py: PDFs carry creation timestamps, so they can't be rebuilt
byte-for-byte in CI. Instead pdf/manifest.json records a fingerprint of each board's SVG; this script only remakes
PDFs whose board has changed, and check_site.py fails if any PDF is missing or out of date.

Run after build_all.py, then run build_all.py again (board pages and guides link to a PDF once it exists):
    python3 _generator/build_all.py && python3 _generator/build_pdfs.py && python3 _generator/build_all.py
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_site import find_chrome  # noqa: E402

OUT = Path(__file__).resolve().parent.parent
PDF = OUT / "pdf"
MANIFEST = PDF / "manifest.json"


def boards():
    """Every board or poster: an SVG with a matching HTML page."""
    return [p.stem for p in sorted(OUT.glob("*.svg")) if (OUT / f"{p.stem}.html").exists()]


def fingerprint(stem):
    return hashlib.sha256((OUT / f"{stem}.svg").read_bytes()).hexdigest()[:16]


def load_manifest():
    return json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}


def build(force=False):
    chrome = find_chrome()
    if not chrome:
        sys.exit("build_pdfs.py needs Google Chrome or Chromium")
    PDF.mkdir(exist_ok=True)
    manifest, made = load_manifest(), 0
    wanted = boards()
    for stem in wanted:
        fp = fingerprint(stem)
        target = PDF / f"{stem}.pdf"
        if not force and manifest.get(stem) == fp and target.exists():
            continue
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        "--virtual-time-budget=20000", f"--print-to-pdf={target}", f"file://{OUT / (stem + '.html')}"],
                       capture_output=True, timeout=180)
        data = target.read_bytes() if target.exists() else b""
        pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
        if pages != 1 or b"Geist" not in data:
            sys.exit(f"{stem}: PDF has {pages} pages or is missing its fonts; not recording it")
        manifest[stem] = fp
        made += 1
        print("made", target.relative_to(OUT))
    for stale in set(manifest) - set(wanted):        # boards that no longer exist
        manifest.pop(stale)
        (PDF / f"{stale}.pdf").unlink(missing_ok=True)
    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), indent=1) + "\n")
    print(f"{made} PDF(s) made, {len(wanted) - made} already up to date")


if __name__ == "__main__":
    build(force="--force" in sys.argv)
