"""Where each file lives, and how pages link to each other.

The site is in four places: boards, posters and canvases in boards/, facilitator guides (.html and .docx) in guides/,
worked examples in examples/, and everything else (home page, reference pages, cheat sheets) at the root. folder()
decides from the file name alone, so generators keep linking by bare file name ("retro-kit-board.html") and
write_page() turns each bare link into the right relative path for the page it's on. Links that already contain a
folder ("pdf/x.pdf", "boards/x.html") are treated as paths from the site root; links starting "../" are left alone.

Hand-written pages are fixed the same way, so it's safe to run fix_links() over them again: it only rewrites bare
names and root paths, and those come out the same each time.
"""
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
FOLDERS = ("boards", "guides", "examples")


def folder(name):
    """The folder a file belongs in ("" for the site root), from its name."""
    stem = name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    if stem.startswith("worked-example-"):
        return "examples"
    if stem.startswith("facilitator-guide-"):
        return "guides"
    if "-board" in stem or stem.endswith(("-poster", "-canvas")):
        return "boards"
    return ""


def site_path(name):
    """A file's path from the site root, e.g. "boards/retro-kit-board.html"."""
    f = folder(name)
    return f"{f}/{name}" if f else name


def path(name):
    """A file's location on disk."""
    return OUT / site_path(name)


def href(from_name, to):
    """The link from page from_name to `to` (a bare file name or a path from the site root, with any #anchor)."""
    m = re.match(r"([^#?]*)(.*)", to)
    base, rest = m.group(1), m.group(2)
    if not base:
        return to
    target = base if "/" in base else site_path(base)
    here = folder(from_name)
    if not here:
        return target + rest
    if target.startswith(here + "/"):
        return target[len(here) + 1:] + rest
    return "../" + target + rest


SKIP = ("#", "http:", "https:", "mailto:", "javascript:", "data:", "tel:", "//", "../")


def fix_links(html, name):
    """Rewrite every bare or root-relative href and src in a page so it works from that page's folder."""
    def one(m):
        v = m.group(2)
        if not v or v.startswith(SKIP) or "'" in v or "{" in v:
            return m.group(0)
        return f'{m.group(1)}="{href(name, v)}"'
    return re.sub(r'\b(href|src)="([^"]*)"', one, html)


def write_page(name, text):
    """Write a generated file into its folder, fixing the links in HTML pages."""
    p = path(name)
    p.parent.mkdir(exist_ok=True)
    if name.endswith(".html"):
        text = fix_links(text, name)
    p.write_text(text, encoding="utf-8")
    return p


def read_index():
    """index.html with the folders taken out of its links, so generators can match cards by bare file name."""
    return strip_folders((OUT / "index.html").read_text(encoding="utf-8"))


def strip_folders(html):
    return re.sub(r'\b(href|src)="(?:' + "|".join(FOLDERS) + r')/', r'\1="', html)


def pages():
    """Every HTML page on the site, root first, as paths."""
    return [p for d in ("", *FOLDERS) for p in sorted((OUT / d).glob("*.html"))]
