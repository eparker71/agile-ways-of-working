#!/usr/bin/env python3
"""Generate the printable A3 facilitation boards (SVG + HTML) for my_agile_tools.

Every board shares the visual language of the Marginal Gains Workshop Board:
navy header band, orange accent, Instrument Serif / Geist / Geist Mono, the
eight colour-coded area pairs, dotted sticky-note zones and footer prompts.

Run:  python3 _generator/build_boards.py      (writes into the parent folder)
"""
import math
import re
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
W, H = 1680, 1190

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import ACCENT, NAVY, SANS, SERIF, MONO, FONT_URL, CREDIT  # noqa: E402  (edit brand.py to rebrand)
INK = "#1E293B"
MUTED = "#566578"
RULE = "#E2E8F0"
WRITE = "#CBD5E1"  # write-on lines: visible on white and on tinted panels
YELLOW = "#FDE047"
GREEN = "#4ADE80"
BLUE_ST = "#93C5FD"
PINK_ST = "#F9A8D4"

# (dark, light) pairs used by the eight Marginal Gains areas
BLUE = ("#1E3A8A", "#DBEAFE")
EMERALD = ("#065F46", "#D1FAE5")
PURPLE = ("#581C87", "#EDE9FE")
ORANGE = ("#9A3412", "#FFEDD5")
RED = ("#991B1B", "#FEE2E2")
AMBER = ("#92400E", "#FEF3C7")
FOREST = ("#14532D", "#DCFCE7")
SKY = ("#0C4A6E", "#E0F2FE")

AREAS = [("Strategy", BLUE), ("Outcomes", EMERALD), ("Product", PURPLE), ("Teams", ORANGE),
         ("Dependencies", RED), ("Engineering", AMBER), ("Delivery", FOREST), ("Learning", SKY)]

FOOT_TAG = "Systems-Thinking · Continuous Improvement · Team-Led Change"


# ---------------------------------------------------------------- primitives

def T(x, y, s, size=11, fill=INK, font=SANS, weight=None, anchor=None,
      italic=False, ls=None, op=None):
    a = [f'x="{x:g}" y="{y:g}"']
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    a.append(f'font-family="{font}" font-size="{size}"')
    if weight:
        a.append(f'font-weight="{weight}"')
    if italic:
        a.append('font-style="italic"')
    a.append(f'fill="{fill}"')
    if op is not None:
        a.append(f'fill-opacity="{op}"')
    if ls:
        a.append(f'letter-spacing="{ls}"')
    return f'<text {" ".join(a)}>{escape(s, quote=False)}</text>'


def R(x, y, w, h, fill, rx=0, extra=""):
    r = f' rx="{rx}"' if rx else ""
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"{r} fill="{fill}"{extra}/>'


def L(x1, y1, x2, y2, stroke=RULE, sw=1.5, extra=""):
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="{sw}"{extra}/>'


def top_round(x, y, w, h, r, fill):
    return (f'<path d="M{x},{y + h} V{y + r} A{r},{r} 0 0 1 {x + r},{y} H{x + w - r} '
            f'A{r},{r} 0 0 1 {x + w},{y + r} V{y + h} Z" fill="{fill}"/>')


def text_w(s, size):
    """Rough width estimate for Geist at a given size."""
    return len(s) * size * 0.52


def sticky(x, y, size, fill):
    return (R(x, y, size, size, fill, 3, ' filter="url(#fsm)"') +
            f'<polygon points="{x + size - 7},{y} {x + size},{y + 7} {x + size},{y}" fill="#000" fill-opacity=".15"/>')


def checkbox(x, y, label, color=INK, size=11):
    return (R(x, y - 10, 12, 12, "white", 2, f' stroke="{color}" stroke-opacity=".6" stroke-width="1.2"') +
            T(x + 20, y, label, size, color))


def field(x, y, label, x_end, color=MUTED, size=11):
    """Label followed by a write-on line to x_end."""
    start = x + text_w(label, size) + 10
    return T(x, y, label, size, color) + L(start, y + 4, x_end, y + 4, WRITE)


def lines(x, y, x_end, n, gap=26, stroke=WRITE):
    return "".join(L(x, y + i * gap, x_end, y + i * gap, stroke) for i in range(n))


# ---------------------------------------------------------------- components

def defs():
    return """
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#F8FAFC"/>
      <stop offset="100%" stop-color="#EFF6FF"/>
    </linearGradient>
    <filter id="fc" x="-4%" y="-4%" width="110%" height="112%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000" flood-opacity=".10"/>
    </filter>
    <filter id="fsm" x="-6%" y="-6%" width="114%" height="116%">
      <feDropShadow dx="0" dy="1" stdDeviation="2" flood-color="#000" flood-opacity=".08"/>
    </filter>
    <pattern id="dots" patternUnits="userSpaceOnUse" width="20" height="20">
      <circle cx="10" cy="10" r="1.2" fill="#000" fill-opacity=".055"/>
    </pattern>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#E0F2FE"/>
      <stop offset="100%" stop-color="#F0F9FF"/>
    </linearGradient>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#7DD3FC"/>
      <stop offset="100%" stop-color="#BAE6FD"/>
    </linearGradient>"""


def header(title, subtitle, tagline, right=""):
    return "".join([
        R(0, 0, W, H, "url(#bg)"),
        R(0, 0, W, 4, ACCENT),
        R(0, 4, W, 134, NAVY),
        T(24, 70, title, 42, "white", SERIF, weight=400),
        T(24, 100, subtitle, 13, "#94A3B8"),
        T(24, 120, tagline, 9, "#8291A6", MONO, ls=".06em"),
        right,
    ])


def legend(items, x=1356):
    """items: list of (kind, color, label); kind is 'sticky' or 'dot'."""
    out = [T(x, 48 if len(items) != 3 else 44, "LEGEND", 8, "#8291A6", MONO, ls=".14em")]
    if len(items) == 4:
        x0 = x
        pos = [(x0, 59), (x0 + 150, 59), (x0, 89), (x0 + 150, 89)]
    else:
        pos = [(x, y) for y in ([59, 89] if len(items) < 3 else [52, 80, 108])]
    for (kind, color, label), (x, y) in zip(items, pos):
        if kind == "sticky":
            out.append(sticky(x, y, 22, color))
        else:
            out.append(f'<circle cx="{x + 11}" cy="{y + 11}" r="9" fill="{color}"/>')
        out.append(T(x + 28, y + 15, label, 11, "#CBD5E1"))
    return "".join(out)


def header_fields(labels, x=1356, x_end=1656):
    out = []
    for i, label in enumerate(labels):
        y = 66 + i * 30
        out.append(T(x, y, label.upper(), 8, "#8291A6", MONO, ls=".14em"))
        out.append(L(x + 96, y + 3, x_end, y + 3, "#334155", 1.2))
    return "".join(out)


def panel(x, y, w, h, num, title, color, note=None):
    dark, light = color
    out = [
        R(x, y, w, h, light, 10, f' stroke="{dark}" stroke-opacity=".18" stroke-width="1.5" filter="url(#fc)"'),
        top_round(x, y, w, 52, 10, dark),
    ]
    tx = x + 21
    if num is not None:
        out.append(f'<circle cx="{x + 21}" cy="{y + 26}" r="12" fill="white" fill-opacity=".18"/>')
        out.append(T(x + 21, y + 31, str(num), 11, "white", weight=600, anchor="middle"))
        tx = x + 44
    out.append(T(tx, y + 32, title, 14, "white", weight=600))
    if note:
        out.append(T(x + w - 16, y + 31, note, 8.5, "white", MONO, anchor="end", ls=".10em", op=".88"))
    return "".join(out)


def bullets(x, y, items, dark, step=18):
    out = []
    for i, s in enumerate(items):
        cy = y + i * step
        out.append(f'<circle cx="{x}" cy="{cy}" r="2.5" fill="{dark}" fill-opacity=".55"/>')
        out.append(T(x + 10, cy + 4, s, 10.5, dark))
    return "".join(out)


def sticky_zone(x, y, w, h, dark, hint="Add your sticky notes here", chips=(YELLOW, GREEN)):
    cx, cy = x + w / 2, y + h / 2
    out = [R(x, y, w, h, "url(#dots)", 6),
           T(cx, cy - 6, hint, 10, dark, italic=True, anchor="middle", op=".22")]
    n = len(chips)
    for i, c in enumerate(chips):
        out.append(R(cx - (n * 32 - 14) / 2 + i * 32, cy + 8, 18, 18, c, 2, ' fill-opacity=".35"'))
    return "".join(out)


def dashed(x1, x2, y, dark):
    return L(x1, y, x2, y, dark, 1, ' stroke-opacity=".20" stroke-dasharray="5,4"')


def strip(y, label, x=24, w=1632):
    return (R(x, y, w, 32, INK, 6) + R(x, y, 6, 32, ACCENT, 3) +
            T(x + w / 2, y + 21, label, 11, "white", weight=600, anchor="middle", ls=".12em"))


def strip_blank(y, label, hint="sprint, month, quarter…", x=24, w=1632):
    """Dark strip with a label and a write-in line, e.g. 'ACTIONS FOR OUR NEXT ______'."""
    lw = len(label) * 11 * 0.68 + 16
    total = lw + 220
    sx = x + (w - total) / 2
    return "".join([R(x, y, w, 32, INK, 6), R(x, y, 6, 32, ACCENT, 3),
                    T(sx, y + 21, label, 11, "white", weight=600, ls=".12em"),
                    L(sx + lw, y + 24, sx + lw + 200, y + 24, "#94A3B8", 1.2),
                    T(sx + lw + 100, y + 17, hint, 8.5, "#94A3B8", italic=True, anchor="middle", op=".88")])


def card(x, y, w, h, title, accent, fields_):
    out = [R(x, y, w, h, "white", 8, f' stroke="{RULE}" stroke-width="1.5" filter="url(#fsm)"'),
           R(x, y, 5, h, accent, 3),
           T(x + 22, y + 34, title, 13, INK, weight=600)]
    for i, label in enumerate(fields_):
        out.append(field(x + 22, y + 72 + i * 36, label, x + w - 22))
    out.append(L(x + 22, y + 72 + len(fields_) * 36 - 2, x + w - 22, y + 72 + len(fields_) * 36 - 2))
    return "".join(out)


def three_cards(y, prefix, fields_):
    accents = [ACCENT, EMERALD[0], BLUE[0]]
    return "".join(card(24 + i * 548, y, 534, 154, f"{prefix} #{i + 1}", accents[i], fields_)
                   for i in range(3))


def footer(left, right, tag=FOOT_TAG):
    return "".join([
        L(24, 1070, 1656, 1070, RULE, 1),
        T(24, 1106, f"“{left}”", 15, INK, SERIF, italic=True),
        L(832, 1078, 832, 1128, RULE, 1),
        T(848, 1106, f"“{right}”", 15, INK, SERIF, italic=True),
        T(1656, 1138, tag, 8, "#5B6B82", MONO, anchor="end", ls=".08em"),
        T(24, 1138, CREDIT, 8, "#5B6B82", MONO, ls=".06em"),
    ])


# ---------------------------------------------------------------- output

def guide_for(slug):
    """Facilitator guide that documents a board slug."""
    m = re.match(r"retro-board-(.+?)(?:-(?:sprint|quarter))?$", slug)
    if m:
        return f"facilitator-guide-retro-{m.group(1)}.html"
    return f"facilitator-guide-{slug.removesuffix('-board').removesuffix('-poster')}.html"


GUIDE_LINK_CSS = (f"a.guide{{position:fixed;right:16px;bottom:16px;font:500 12px 'Geist',system-ui,sans-serif;color:#fff;"
                  f"background:{NAVY};border-left:4px solid {ACCENT};padding:9px 14px;border-radius:6px;text-decoration:none;"
                  f"box-shadow:0 6px 20px rgba(0,0,0,.25);}}\na.guide:hover{{background:#C2410C;}}\na.guide.pdf{{bottom:60px;}}")


PHONE_CSS = ("p.phone{display:none;}"
             "@media (max-width:700px){body{flex-direction:column;align-items:stretch;padding:12px 12px 72px;min-height:0;}"
             "p.phone{display:block;margin:14px 2px 0;font:14px/1.5 'Geist',system-ui,sans-serif;color:#0C1A2E;}"
             "p.phone b{display:block;font-weight:600;margin-bottom:2px;}p.phone a{color:#9A3412;}}"
             "@media print{p.phone{display:none !important;}}")


def phone_note(svg_href, guide_href):
    """Shown on phones only: the board is A3, so say how to read it."""
    return (f'<p class="phone"><b>This is an A3 board, made for printing or a big screen.</b>'
            f'Pinch to zoom, turn your phone sideways, or <a href="{svg_href}">open the SVG</a> to zoom in. '
            f'The <a href="{guide_href}">facilitator guide</a> is easy to read on a phone.</p>')


def pdf_link(slug):
    """Download button for the board's A3 PDF, once build_pdfs.py has made it."""
    return f'<a class="guide pdf" href="pdf/{slug}.pdf" download title="A3 landscape. On 11×17 (Tabloid) paper, print with Fit to page.">A3 PDF ↓</a>\n' if (OUT / "pdf" / f"{slug}.pdf").exists() else ""


def write_board(slug, title, desc, body):
    svg_open = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
                f'role="img" aria-labelledby="mg-title mg-desc">\n'
                f'  <title id="mg-title">{escape(title)}</title>\n'
                f'  <desc id="mg-desc">{escape(desc)}</desc>\n')
    font_import = f"<style>@import url('{FONT_URL.replace('&', '&amp;')}');</style>"
    svg_file = ('<?xml version="1.0" encoding="UTF-8"?>\n' + svg_open +
                f'  <defs>{font_import}{defs()}\n  </defs>\n{body}\n</svg>\n')
    svg_inline = svg_open + f'  <defs>{defs()}\n  </defs>\n{body}\n</svg>'
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<link rel="stylesheet" href="{FONT_URL.replace('&', '&amp;')}">
<style>
html,body{{margin:0;padding:0;background:#B0BEC5;}}
body{{display:flex;justify-content:center;align-items:flex-start;padding:24px;box-sizing:border-box;min-height:100vh;}}
svg{{display:block;max-width:100%;height:auto;box-shadow:0 12px 40px rgba(0,0,0,.22);}}
{GUIDE_LINK_CSS}
{PHONE_CSS}
@media print{{@page{{size:A3 landscape;margin:0;}}html,body{{background:none;}}body{{padding:0;}}svg{{box-shadow:none;width:100%;max-height:296mm;}}html,body{{height:297mm;overflow:hidden;}}a.guide{{display:none;}}}}
</style>
</head>
<body>
<a class="guide" href="{guide_for(slug)}">Facilitator guide →</a>
{pdf_link(slug)}{svg_inline}
{phone_note(f"{slug}.svg", guide_for(slug))}
</body>
</html>
"""
    (OUT / f"{slug}.svg").write_text(svg_file, encoding="utf-8")
    (OUT / f"{slug}.html").write_text(page, encoding="utf-8")
    print("wrote", slug)


REDIRECTS = {f"{old}-{h}": old for old in ["retro-board-start-stop-continue", "retro-board-4ls", "retro-board-mad-sad-glad",
                                          "retro-board-sailboat", "marginal-gains-workshop-board"] for h in ("sprint", "quarter")}


def write_redirects():
    """Old -sprint / -quarter pages now point to the single board, so existing links keep working."""
    for old, new in REDIRECTS.items():
        (OUT / f"{old}.html").write_text(
            f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="UTF-8"><title>Moved</title>'
            f'<meta http-equiv="refresh" content="0; url={new}.html"><link rel="canonical" href="{new}.html"></head>'
            f'<body><p>This board has moved to <a href="{new}.html">{new}.html</a>.</p></body></html>\n', encoding="utf-8")
        old_svg = OUT / f"{old}.svg"
        if old_svg.exists():
            old_svg.unlink()
    print("wrote", len(REDIRECTS), "redirects")


RETRO_LEGEND = [("sticky", YELLOW, "Yellow Sticky = What Happened"),
                ("sticky", GREEN, "Green Sticky = Idea / Action"),
                ("dot", ACCENT, "Dot = Vote (3 per person)")]
RETRO_TAG = "Retrospective Kit · Team Reflection · Continuous Improvement"


# ---------------------------------------------------------------- retro: column formats

def retro_columns(slug, title, subtitle, cols, foot_left, foot_right):
    n = len(cols)
    gap = 14
    cw = (1632 - gap * (n - 1)) / n
    body = [header(title, subtitle, "Retrospective Kit · Agile Team · Reflect, Learn, Adapt",
                   legend(RETRO_LEGEND))]
    for i, (name, color, question, prompts) in enumerate(cols):
        x = 24 + i * (cw + gap)
        dark = color[0]
        body.append(panel(x, 148, cw, 704, i + 1, name, color))
        body.append(T(x + 18, 236, question, 22, dark, SERIF, italic=True))
        body.append(bullets(x + 22, 264, prompts, dark))
        zy = 264 + len(prompts) * 18 + 14
        body.append(dashed(x + 10, x + cw - 10, zy, dark))
        body.append(sticky_zone(x + 10, zy + 6, cw - 20, 852 - 12 - zy - 6, dark, chips=(YELLOW, GREEN)))
    body.append(strip_blank(866, "ACTIONS WE'LL TAKE INTO OUR NEXT"))
    body.append(three_cards(906, "Action", ["Owner:", "Done when:"]))
    body.append(footer(foot_left, foot_right, RETRO_TAG))
    desc = (f"A3 landscape retrospective board: {', '.join(c[0] for c in cols)}. "
            "Sticky-note zones per column and three action slots for the next sprint, month or quarter.")
    write_board(slug, title, desc, "\n".join(body))


def build_retros():
    retro_columns(
        "retro-board-start-stop-continue", "Start · Stop · Continue",
        "Looking back at recent work, what should we change about how we work together?",
        [("Start", EMERALD, "What should we start doing?",
          ["New practices worth trying", "Experiments we keep putting off", "Things other teams do well"]),
         ("Stop", RED, "What should we stop doing?",
          ["Waste and low-value work", "Habits that slow us down", "Meetings or steps nobody would miss"]),
         ("Continue", BLUE, "What should we keep doing?",
          ["What's working well", "Practices worth protecting", "Wins worth amplifying"])],
        "If we could only change one thing, what would it be?",
        "What's the smallest step we can take on it tomorrow?")

    retro_columns(
        "retro-board-4ls", "The 4 Ls Retrospective",
        "Reflect on recent work through four lenses: what we liked, learned, lacked and longed for.",
        [("Liked", FOREST, "What did we enjoy?",
          ["Moments of good collaboration", "Things that went better than expected"]),
         ("Learned", BLUE, "What did we discover?",
          ["New skills, tools or insights", "Surprises about users or the system"]),
         ("Lacked", ORANGE, "What was missing?",
          ["Information, people or time", "Clarity, focus or support"]),
         ("Longed For", PURPLE, "What do we wish we had?",
          ["Things that would make work easier", "Changes we'd love to see"])],
        "What did we learn that we don't want to forget?",
        "Which ‘lacked’ or ‘longed for’ could we fix by 1% next time?")

    retro_columns(
        "retro-board-mad-sad-glad", "Mad · Sad · Glad",
        "How has work felt lately? Surface the emotions behind it, then decide what to act on.",
        [("Mad", RED, "What frustrated us?",
          ["Blockers and recurring problems", "Things outside our control", "Moments we felt stuck"]),
         ("Sad", SKY, "What disappointed us?",
          ["Things that didn't go to plan", "Missed opportunities", "Unmet expectations"]),
         ("Glad", EMERALD, "What made us happy?",
          ["Wins and achievements", "People who helped us", "Moments we were proud of"])],
        "What's behind the strongest feelings on this board?",
        "What would turn one ‘mad’ into a ‘glad’ next time?")


# ---------------------------------------------------------------- retro: sailboat

def build_sailboat():
    x0, y0, w, h = 24, 148, 1632, 704
    water = 540
    b = [header("Sailboat Retrospective",
                "Where are we heading, what's driving us forward, what's holding us back, and what risks lie ahead?",
                "Retrospective Kit · Agile Team · Reflect, Learn, Adapt", legend(RETRO_LEGEND)),
         '<clipPath id="sea-clip"><rect x="24" y="148" width="1632" height="704" rx="10"/></clipPath>',
         R(x0, y0, w, h, "url(#sky)", 10, f' stroke="{SKY[0]}" stroke-opacity=".18" stroke-width="1.5" filter="url(#fc)"'),
         f'<g clip-path="url(#sea-clip)">',
         R(x0, water, w, y0 + h - water, "url(#sea)"),
         # waves on the waterline
         '<path d="' + "".join(f"M{x},{water} q20,-10 40,0 " for x in range(24, 1656, 80)) +
         f'" fill="none" stroke="white" stroke-opacity=".7" stroke-width="2"/>',
         '</g>',
         # sun
         '<circle cx="700" cy="222" r="34" fill="#FDE68A"/><circle cx="700" cy="222" r="24" fill="#FCD34D"/>']

    # island + palm (top right, sitting on the waterline)
    b.append(f'<path d="M1300,{water} Q1440,{water - 70} 1580,{water} Z" fill="#FDE68A" stroke="#D97706" stroke-opacity=".3"/>')
    b.append(f'<path d="M1452,{water - 34} Q1458,{water - 90} 1440,{water - 140}" fill="none" stroke="#92400E" stroke-width="7" stroke-linecap="round"/>')
    for d in ["q40,-30 80,8", "q-40,-30 -80,6", "q30,-48 66,-46", "q-26,-50 -64,-40"]:
        b.append(f'<path d="M1440,{water - 140} {d}" fill="none" stroke="#15803D" stroke-width="8" stroke-linecap="round"/>')
    # flag
    b.append(f'<line x1="1500" y1="{water - 30}" x2="1500" y2="{water - 96}" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<path d="M1500,{water - 96} l34,10 l-34,10 Z" fill="{ACCENT}"/>')

    # boat
    bx = 840
    b.append(f'<line x1="{bx}" y1="300" x2="{bx}" y2="{water - 18}" stroke="{INK}" stroke-width="4"/>')
    b.append(f'<path d="M{bx + 6},306 L{bx + 6},{water - 30} L{bx + 130},{water - 30} Z" fill="white" stroke="{INK}" stroke-opacity=".5" stroke-width="2"/>')
    b.append(f'<path d="M{bx - 6},330 L{bx - 6},{water - 30} L{bx - 100},{water - 30} Z" fill="white" stroke="{INK}" stroke-opacity=".5" stroke-width="2"/>')
    b.append(f'<path d="M{bx}, 300 l26,8 l-26,8 Z" fill="{ACCENT}"/>')
    b.append(f'<path d="M{bx - 150},{water - 20} L{bx + 170},{water - 20} L{bx + 120},{water + 26} L{bx - 110},{water + 26} Z" fill="{NAVY}"/>')
    b.append(R(bx - 140, water - 20, 300, 6, ACCENT))

    # wind lines blowing toward the sails
    for i, (y, ln) in enumerate([(330, 170), (372, 190), (414, 160)]):
        sx = 540 + i * 18
        b.append(f'<path d="M{sx},{y} h{ln - 40} q30,0 30,-16" fill="none" stroke="{SKY[0]}" stroke-opacity=".45" stroke-width="3" stroke-linecap="round"/>')

    # anchor hanging below the stern
    ax, ay = bx - 70, 760
    b.append(L(bx - 70, water + 26, ax, ay - 28, INK, 2, ' stroke-dasharray="6,5" stroke-opacity=".6"'))
    b.append(f'<g fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round" stroke-opacity=".8">'
             f'<circle cx="{ax}" cy="{ay - 20}" r="8"/><line x1="{ax}" y1="{ay - 12}" x2="{ax}" y2="{ay + 40}"/>'
             f'<line x1="{ax - 18}" y1="{ay}" x2="{ax + 18}" y2="{ay}"/>'
             f'<path d="M{ax - 32},{ay + 18} Q{ax - 26},{ay + 44} {ax},{ay + 44} Q{ax + 26},{ay + 44} {ax + 32},{ay + 18}"/></g>')

    # rocks ahead of the boat
    for px, ph, pw in [(1112, 46, 54), (1162, 30, 40), (1210, 54, 48)]:
        b.append(f'<path d="M{px - pw / 2},{water + 14} L{px - 8},{water - ph} L{px + 10},{water - ph + 10} '
                 f'L{px + pw / 2},{water + 14} Z" fill="#475569"/>')

    def zone(x, y, w_, h_, num, label, q, prompts, dark):
        out = [R(x, y, w_, h_, "white", 10, f' fill-opacity=".55" stroke="{dark}" stroke-opacity=".25" stroke-dasharray="6,5" stroke-width="1.5"'),
               f'<circle cx="{x + 22}" cy="{y + 24}" r="12" fill="{dark}"/>',
               T(x + 22, y + 29, str(num), 11, "white", weight=600, anchor="middle"),
               T(x + 42, y + 30, label, 14, dark, weight=600, ls=".08em"),
               T(x + 42 + len(label) * 14 * 0.74 + 12, y + 30, q, 18, dark, SERIF, italic=True),
               bullets(x + 24, y + 56, prompts, dark, 17)]
        zy = y + 56 + len(prompts) * 17
        out.append(sticky_zone(x + 10, zy, w_ - 20, y + h_ - 10 - zy, dark))
        return "".join(out)

    b.append(zone(44, 168, 470, 352, 1, "WIND", "What pushes us forward?",
                  ["Strengths, support and momentum", "What's helping us go faster?"], FOREST[0]))
    b.append(zone(1100, 168, 536, 170, 2, "ISLAND", "Where are we heading?",
                  ["Our goal for the next sprint, month or quarter"], EMERALD[0]))
    b.append(zone(44, 572, 600, 264, 3, "ANCHORS", "What's holding us back?",
                  ["Impediments, waste, slow handoffs"], RED[0]))
    b.append(zone(1000, 572, 636, 264, 4, "ROCKS", "What risks lie ahead?",
                  ["Dependencies, unknowns, deadlines"], AMBER[0]))

    b.append(strip_blank(866, "ACTIONS WE'LL TAKE INTO OUR NEXT"))
    b.append(three_cards(906, "Action", ["Owner:", "Done when:"]))
    b.append(footer("Which anchor, if cut, would let us sail fastest?",
                    "What can we do next time to steer clear of the rocks?", RETRO_TAG))
    write_board("retro-board-sailboat", "Sailboat Retrospective",
                "A3 landscape sailboat retrospective: Island (goal), Wind (what helps), Anchors (what slows us) "
                "and Rocks (risks), with sticky-note zones and three action slots.", "\n".join(b))


# ---------------------------------------------------------------- team health check

HEALTH = [
    ("Delivering Value", "We deliver great stuff and customers are delighted.",
     "We deliver poor work and feel uneasy shipping it."),
    ("Easy to Release", "Releasing is simple, safe, painless and automated.",
     "Releasing is risky, manual, painful and slow."),
    ("Fun", "We love coming to work and have fun together.",
     "Work feels like a grind."),
    ("Health of Codebase", "Clean, readable code with great test coverage.",
     "Technical debt is out of control."),
    ("Learning", "We're learning interesting things all the time.",
     "We never have time to learn anything."),
    ("Mission", "We know why we're here and we're excited about it.",
     "No clear purpose, big picture or focus."),
    ("Pawns or Players", "We control our destiny: we decide what and how.",
     "We're pawns with no influence on what we do."),
    ("Speed", "We get things done quickly. No waiting, no delays.",
     "We keep getting stuck, blocked or interrupted."),
    ("Suitable Process", "Our way of working fits us perfectly.",
     "Our way of working gets in our way."),
    ("Support", "We get great help and support when we ask.",
     "We get stuck because we can't get the help we need."),
    ("Teamwork", "We're a gelled team with awesome collaboration.",
     "We're individuals who don't really know each other."),
]


def build_health_check():
    g, a, r = FOREST, AMBER, RED
    cols = [  # (x, w)
        (24, 470),    # dimension
        (504, 228),   # healthy
        (742, 228),   # some issues
        (980, 228),   # unhealthy
        (1218, 176),  # trend
        (1404, 252),  # notes
    ]
    b = [header("Team Health Check",
                "How healthy is our team right now, and which way is it trending? Vote, discuss, then pick 1–2 areas to improve.",
                "Inspired by the Spotify Squad Health Check · Team & Facilitator Tool · Systems-Thinking Approach",
                legend([("dot", "#22C55E", "Green = Healthy, nothing to fix"),
                        ("dot", "#F59E0B", "Amber = Some issues to discuss"),
                        ("dot", "#EF4444", "Red = Unhealthy, needs attention")]))]

    # column header band
    b.append(R(24, 148, 1632, 36, INK, 6))
    b.append(R(24, 148, 6, 36, ACCENT, 3))
    heads = ["DIMENSION", "HEALTHY", "SOME ISSUES", "UNHEALTHY", "TREND", "NOTES & ACTIONS"]
    dots = [None, "#22C55E", "#F59E0B", "#EF4444", None, None]
    for (x, w), label, d in zip(cols, heads, dots):
        if d:
            tw = text_w(label, 10) * 1.25
            b.append(f'<circle cx="{x + w / 2 - tw / 2 - 10}" cy="166" r="5" fill="{d}"/>')
            b.append(T(x + w / 2 + 4, 170, label, 10, "white", weight=600, anchor="middle", ls=".12em"))
        else:
            b.append(T(x + (20 if label == "DIMENSION" else w / 2), 170, label, 10, "white",
                       weight=600, anchor=None if label == "DIMENSION" else "middle", ls=".12em"))

    rh, gap, y = 72, 6, 192
    for i, (name, good, bad) in enumerate(HEALTH):
        ry = y + i * (rh + gap)
        b.append(R(24, ry, 1632, rh, "white", 8, f' stroke="{RULE}" stroke-width="1.5" filter="url(#fsm)"'))
        b.append(f'<circle cx="46" cy="{ry + 22}" r="11" fill="{NAVY}"/>')
        b.append(T(46, ry + 26, str(i + 1), 10, "white", weight=600, anchor="middle"))
        b.append(T(66, ry + 27, name, 14, INK, weight=600))
        b.append(f'<circle cx="70" cy="{ry + 44}" r="3.5" fill="#22C55E"/>')
        b.append(T(80, ry + 48, good, 10.5, g[0]))
        b.append(f'<circle cx="70" cy="{ry + 60}" r="3.5" fill="#EF4444"/>')
        b.append(T(80, ry + 64, bad, 10.5, r[0]))
        for (cx, cw), (dark, light) in zip(cols[1:4], (g, a, r)):
            b.append(R(cx, ry + 8, cw, rh - 16, light, 6))
            b.append(R(cx, ry + 8, cw, rh - 16, "url(#dots)", 6))
        tx, tw = cols[4]
        for j, (glyph, col) in enumerate([("↑", g[0]), ("→", a[0]), ("↓", r[0])]):
            cx = tx + tw / 2 + (j - 1) * 46
            b.append(f'<circle cx="{cx}" cy="{ry + rh / 2}" r="15" fill="white" stroke="{col}" stroke-opacity=".45" stroke-width="1.5"/>')
            b.append(T(cx, ry + rh / 2 + 5, glyph, 14, col, weight=600, anchor="middle"))
        nx, nw = cols[5]
        b.append(lines(nx + 6, ry + 30, nx + nw - 14, 2, 22))

    b.append("".join([
        L(24, 1070, 1656, 1070, RULE, 1),
        field(24, 1106, "Team:", 330, INK, 13),
        field(350, 1106, "Date:", 560, INK, 13),
        field(580, 1106, "Facilitator:", 810, INK, 13),
        L(832, 1078, 832, 1128, RULE, 1),
        T(848, 1106, "“Which 1–2 areas would make the biggest difference if they got 1% better?”", 15, INK, SERIF, italic=True),
        T(1656, 1138, "Vote with coloured dots · Repeat each quarter to see trends · Feed red/amber areas into the 1% Experiment Canvas",
          8, "#CBD5E1", MONO, anchor="end", ls=".08em"),
    ]))
    write_board("team-health-check-board", "Team Health Check",
                "A3 landscape team health check: eleven dimensions, each with healthy and unhealthy descriptions, "
                "green/amber/red dot-vote cells, a trend indicator and space for notes and actions.", "\n".join(b))


# ---------------------------------------------------------------- experiment canvas

def build_experiment_canvas():
    b = [header("1% Experiment Canvas",
                "Turn one small improvement idea into a testable experiment with a clear owner, measure and review date.",
                "Companion to the Marginal Gains Workshop · Hypothesis-Driven Improvement · Build, Measure, Learn",
                header_fields(["Experiment #", "Team"]))]

    # 1 friction
    x, y, w = 24, 148, 397
    b.append(panel(x, y, w, 320, 1, "Where's the Friction?", RED, "FROM THE BOARD"))
    b.append(T(x + 18, y + 78, "Board area (tick one):", 11, RED[0], weight=600))
    for i, (name, (dark, light)) in enumerate(AREAS):
        cx = x + 22 + (i // 4) * 186
        cy = y + 104 + (i % 4) * 22
        b.append(R(cx, cy - 10, 12, 12, "white", 2, f' stroke="{dark}" stroke-width="1.4"'))
        b.append(R(cx + 20, cy - 8, 8, 8, dark, 2))
        b.append(T(cx + 34, cy, name, 11, dark))
    b.append(T(x + 18, y + 208, "The pain point we observed:", 11, RED[0], weight=600))
    b.append(lines(x + 18, y + 236, x + w - 18, 3, 26))

    # 2 hypothesis
    x, w = 435, 808
    b.append(panel(x, y, w, 320, 2, "Hypothesis", PURPLE, "IF · FOR · THEN · WE'LL KNOW"))
    rows = [("If we…", "the change we will make"),
            ("for…", "who or which part of the system"),
            ("then we expect…", "the outcome or improvement"),
            ("We'll know we're right when we see…", "the signal or evidence")]
    for i, (lead, hint) in enumerate(rows):
        ly = y + 86 + i * 56
        b.append(T(x + 18, ly, lead, 20, PURPLE[0], SERIF, italic=True))
        b.append(T(x + 18 + text_w(lead, 20) * 0.82 + 12, ly, f"({hint})", 9, PURPLE[0], MONO, op=".88", ls=".04em"))
        b.append(L(x + 18, ly + 26, x + w - 18, ly + 26, PURPLE[0], 1, ' stroke-opacity=".25"'))
    b.append(T(x + w - 18, y + 306, "TIP: keep it small enough to start tomorrow", 8.5, PURPLE[0], MONO, anchor="end", op=".88", ls=".1em"))

    # 3 change
    x, w = 1257, 397
    b.append(panel(x, y, w, 320, 3, "The 1% Change", EMERALD))
    b.append(T(x + 18, y + 78, "What exactly will we do differently?", 11, EMERALD[0], weight=600))
    b.append(lines(x + 18, y + 106, x + w - 18, 3, 26))
    b.append(T(x + 18, y + 208, "Smallest version we could try first:", 11, EMERALD[0], weight=600))
    b.append(lines(x + 18, y + 236, x + w - 18, 3, 26))

    # 4 measure
    x, y, w = 24, 482, 808
    b.append(panel(x, y, w, 320, 4, "Measure", BLUE, "BASELINE → TARGET"))
    bw = (w - 36 - 24) / 3
    for i, (lab, hint) in enumerate([("Baseline", "where we are today"), ("Target", "what 1% better looks like"),
                                     ("How & where measured", "source, frequency")]):
        bx = x + 18 + i * (bw + 12)
        b.append(R(bx, y + 66, bw, 118, "white", 6, f' stroke="{BLUE[0]}" stroke-opacity=".2"'))
        b.append(T(bx + 14, y + 88, lab.upper(), 9, BLUE[0], MONO, weight=600, ls=".1em"))
        b.append(T(bx + 14, y + 104, hint, 10, BLUE[0], italic=True, op=".88"))
    b.append(field(x + 18, y + 226, "Leading indicator (early signal):", x + w - 18, BLUE[0]))
    b.append(field(x + 18, y + 266, "Guardrail (what must not get worse):", x + w - 18, BLUE[0]))
    b.append(L(x + 18, y + 300, x + w - 18, y + 300))

    # 5 plan
    x, w = 846, 397
    b.append(panel(x, y, w, 320, 5, "Plan & Timebox", ORANGE))
    for i, lab in enumerate(["Owner:", "Supporters:", "Start date:", "Mid-point check-in:", "Review date:"]):
        b.append(field(x + 18, y + 84 + i * 36, lab, x + w - 18, ORANGE[0]))
    b.append(T(x + 18, y + 278, "Timebox:", 11, ORANGE[0], weight=600))
    for i, lab in enumerate(["1 iteration", "2 iterations", "1 quarter"]):
        b.append(checkbox(x + 92 + i * 96, y + 278, lab, ORANGE[0], 10.5))

    # 6 risks
    x, w = 1257, 397
    b.append(panel(x, y, w, 320, 6, "Risks & Assumptions", AMBER))
    b.append(bullets(x + 22, y + 74, ["What must be true for this to work?", "What could go wrong, and how will we spot it?",
                                     "Who else needs to know or agree?"], AMBER[0]))
    b.append(dashed(x + 10, x + w - 10, y + 128, AMBER[0]))
    b.append(sticky_zone(x + 10, y + 134, w - 20, 174, AMBER[0], chips=(YELLOW,)))

    # 7 result & decision
    b.append(strip(816, "7 · RESULT & DECISION: COMPLETE AT THE REVIEW"))
    cy, ch = 856, 204
    b.append(R(24, cy, 534, ch, "white", 8, f' stroke="{RULE}" stroke-width="1.5" filter="url(#fsm)"'))
    b.append(R(24, cy, 5, ch, ACCENT, 3))
    b.append(T(46, cy + 34, "What happened?", 13, INK, weight=600))
    b.append(field(46, cy + 72, "Result vs. target:", 536))
    b.append(lines(46, cy + 108, 536, 3, 30))

    b.append(R(572, cy, 534, ch, "white", 8, f' stroke="{RULE}" stroke-width="1.5" filter="url(#fsm)"'))
    b.append(R(572, cy, 5, ch, EMERALD[0], 3))
    b.append(T(594, cy + 34, "Decision (tick one)", 13, INK, weight=600))
    opts = [("Persevere", "It worked. Make it standard.", FOREST),
            ("Pivot", "Promising. Adjust and re-run.", AMBER),
            ("Stop", "No gain. Stop and share why.", RED)]
    ow = (534 - 44 - 20) / 3
    for i, (lab, d, (dark, light)) in enumerate(opts):
        ox = 594 + i * (ow + 10)
        b.append(R(ox, cy + 52, ow, 130, light, 6, f' stroke="{dark}" stroke-opacity=".25"'))
        b.append(R(ox + 14, cy + 68, 18, 18, "white", 3, f' stroke="{dark}" stroke-width="1.5"'))
        b.append(T(ox + 40, cy + 83, lab, 14, dark, weight=600))
        b.append(T(ox + 14, cy + 112, d.split(". ")[0] + ".", 10.5, dark))
        b.append(T(ox + 14, cy + 128, d.split(". ")[1], 10.5, dark))

    b.append(R(1120, cy, 534, ch, "white", 8, f' stroke="{RULE}" stroke-width="1.5" filter="url(#fsm)"'))
    b.append(R(1120, cy, 5, ch, BLUE[0], 3))
    b.append(T(1142, cy + 34, "What did we learn?", 13, INK, weight=600))
    b.append(lines(1142, cy + 72, 1632, 3, 30))
    b.append(field(1142, cy + 172, "Share the learning with:", 1632))

    b.append(footer("What's the smallest change that could prove us right or wrong?",
                    "If this works, who else would benefit from knowing?"))
    write_board("experiment-canvas", "1% Experiment Canvas",
                "A3 landscape experiment canvas: friction source, hypothesis, the 1% change, baseline/target measures, "
                "owner and timebox, risks, and a result/decision section (persevere, pivot, stop).", "\n".join(b))


# ---------------------------------------------------------------- lean coffee

def build_lean_coffee():
    b = [header("Lean Coffee",
                "A structured, agenda-less meeting: the group sets the topics, votes on them, and talks about what matters most.",
                "Facilitation Toolkit · Participant-Driven Meetings · Timeboxed Conversations",
                legend([("sticky", YELLOW, "Yellow Sticky = Discussion Topic"),
                        ("sticky", GREEN, "Green Sticky = Takeaway / Action"),
                        ("dot", ACCENT, "Dot = Vote (3 per person)")]))]
    top, ph = 148, 640

    # 1 to discuss / 3 discussed: wide sticky columns
    for x, num, name, color, q, prompts in [
        (24, 1, "To Discuss", BLUE, "What do we want to talk about?",
         ["One topic per sticky, pitched in a sentence", "Dot-vote, then sort by votes (most at the top)"]),
        (1056, 3, "Discussed", EMERALD, "What have we covered?",
         ["Move the topic here when the group moves on", "Add a green sticky with the key takeaway"]),
    ]:
        dark = color[0]
        b.append(panel(x, top, 600, ph, num, name, color))
        b.append(T(x + 18, top + 88, q, 22, dark, SERIF, italic=True))
        b.append(bullets(x + 22, top + 116, prompts, dark))
        zy = top + 116 + len(prompts) * 18 + 14
        b.append(dashed(x + 10, x + 590, zy, dark))
        b.append(sticky_zone(x + 10, zy + 6, 580, top + ph - 12 - zy - 6, dark,
                             chips=(YELLOW,) if num == 1 else (YELLOW, GREEN)))

    # 2 discussing: current topic, timebox and the keep-going vote
    x, w = 638, 404
    dark = ORANGE[0]
    b.append(panel(x, top, w, ph, 2, "Discussing", ORANGE, "NOW"))
    b.append(T(x + 18, top + 88, "What are we discussing now?", 22, dark, SERIF, italic=True))
    b.append(T(x + 18, top + 120, "CURRENT TOPIC", 9, dark, MONO, weight=600, ls=".12em"))
    sq = 170
    sx = x + (w - sq) / 2
    b.append(R(sx, top + 132, sq, sq, "white", 6, f' fill-opacity=".6" stroke="{dark}" stroke-opacity=".35" stroke-dasharray="6,5" stroke-width="1.5"'))
    b.append(T(x + w / 2, top + 212, "Place the top-voted", 10, dark, italic=True, anchor="middle", op=".45"))
    b.append(T(x + w / 2, top + 226, "topic here", 10, dark, italic=True, anchor="middle", op=".45"))

    b.append(T(x + 18, top + 336, "TIMEBOX (TICK EACH ROUND)", 9, dark, MONO, weight=600, ls=".12em"))
    for i, lab in enumerate(["8 min", "+ 4 min", "+ 2 min"]):
        b.append(checkbox(x + 22 + i * 120, top + 362, lab, dark, 11))

    b.append(T(x + 18, top + 400, "WHEN THE TIMER ENDS, VOTE", 9, dark, MONO, weight=600, ls=".12em"))
    for i, (glyph, lab, col) in enumerate([("↑", "Keep going", FOREST[0]), ("→", "Wrap up", AMBER[0]),
                                            ("↓", "Move on", RED[0])]):
        cx = x + w / 2 + (i - 1) * 120
        b.append(f'<circle cx="{cx}" cy="{top + 438}" r="20" fill="white" stroke="{col}" stroke-opacity=".5" stroke-width="1.5"/>')
        b.append(T(cx, top + 445, glyph, 18, col, weight=600, anchor="middle"))
        b.append(T(cx, top + 476, lab, 11, col, weight=600, anchor="middle"))
    b.append(T(x + w / 2, top + 496, "Majority ↑ extends the timer · otherwise pull the next topic", 9.5, dark,
               italic=True, anchor="middle", op=".88"))

    b.append(dashed(x + 10, x + w - 10, top + 514, dark))
    b.append(T(x + 18, top + 540, "Key takeaway:", 11, dark, weight=600))
    b.append(lines(x + 18, top + 568, x + w - 18, 3, 24))

    # how it works
    steps = [("Brainstorm topics", "5 min · one topic per sticky"),
             ("Pitch & dot-vote", "One sentence each · 3 dots per person"),
             ("Discuss the top topic", "Start the 8-minute timer"),
             ("Keep going or move on?", "Vote ↑ → ↓ when time is up"),
             ("Capture takeaways", "Green sticky, then move to Discussed")]
    sw = (1632 - 4 * 10) / 5
    for i, (t, d) in enumerate(steps):
        sx = 24 + i * (sw + 10)
        b.append(R(sx, 800, sw, 52, "white", 8, f' stroke="{RULE}" stroke-width="1.5" filter="url(#fsm)"'))
        b.append(f'<circle cx="{sx + 24}" cy="826" r="11" fill="{NAVY}"/>')
        b.append(T(sx + 24, 830, str(i + 1), 10, "white", weight=600, anchor="middle"))
        b.append(T(sx + 44, 821, t, 12, INK, weight=600))
        b.append(T(sx + 44, 838, d, 10, MUTED))

    b.append(strip(866, "TAKEAWAYS & ACTIONS"))
    b.append(three_cards(906, "Action", ["Owner:", "Done when:"]))
    b.append(footer("What's the most valuable thing we could talk about right now?",
                    "Has this conversation run its course, or is there more value to unlock?",
                    "Lean Coffee · Participant-Driven Meetings · Facilitation Toolkit"))
    write_board("lean-coffee-board", "Lean Coffee",
                "A3 landscape Lean Coffee board: To Discuss, Discussing (current topic, timebox and keep-going vote) "
                "and Discussed columns, a five-step how-it-works row, and three action slots.", "\n".join(b))


# ---------------------------------------------------------------- break down work: helpers

SLATE = ("#334155", "#F1F5F9")


def para(x, y, text_lines, size=11, fill=INK, step=None, **kw):
    step = step or round(size * 1.4)
    return "".join(T(x, y + i * step, ln, size, fill, **kw) for i, ln in enumerate(text_lines))


def slot(x, y, w, h, fill, dark, hint):
    """Dashed placeholder sized for one sticky note."""
    return (R(x, y, w, h, fill, 6, f' fill-opacity=".35" stroke="{dark}" stroke-opacity=".35" stroke-dasharray="6,5" stroke-width="1.5"') +
            T(x + w / 2, y + h / 2 + 4, hint, 10, dark, italic=True, anchor="middle", op=".88"))


BREAKDOWN_TAG = "Break Down Work · Vertical Slicing · Deliver Value Early"


# ---------------------------------------------------------------- epic breakdown canvas

def build_epic_breakdown():
    b = [header("Epic Breakdown Canvas",
                "Turn a big idea into an MVP, a handful of valuable features, and the first stories a team can start.",
                "Break Down Work · Epic Hypothesis · Minimum Viable Product · Feature Slicing",
                header_fields(["Epic", "Owner"]))]

    # 1 hypothesis
    x, y, w = 24, 148, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, 320, 1, "Epic Hypothesis", PURPLE, "WHY ARE WE DOING THIS?"))
    for i, lead in enumerate(["For…", "who…", "the…", "is a…", "that…", "unlike…", "our solution…"]):
        ly = y + 90 + i * 34
        b.append(T(x + 18, ly, lead, 19, d, SERIF, italic=True))
        b.append(L(x + 150, ly + 3, x + w - 18, ly + 3, d, 1, ' stroke-opacity=".25"'))
    hints = ["(the customers or users)", "(have this need or problem)", "(epic name)", "(what it is: product, service, capability)",
             "(provides this value)", "(the current solution or competitor)", "(does this better)"]
    for i, h in enumerate(hints):
        b.append(T(x + w - 18, y + 90 + i * 34 - 6, h, 8.5, d, MONO, anchor="end", op=".88", ls=".04em"))

    # 2 outcomes
    x, w = 846, 397
    b.append(panel(x, y, w, 320, 2, "Outcomes & Measures", EMERALD))
    b.append(T(x + 18, y + 80, "Business outcomes: how we'll know it worked", 11, EMERALD[0], weight=600))
    b.append(lines(x + 18, y + 108, x + w - 18, 3, 26))
    b.append(T(x + 18, y + 204, "Leading indicators: early signals", 11, EMERALD[0], weight=600))
    b.append(lines(x + 18, y + 232, x + w - 18, 3, 26))

    # 3 mvp
    x = 1257
    b.append(panel(x, y, w, 320, 3, "Minimum Viable Product", BLUE, "TEST IT SMALL"))
    b.append(T(x + 18, y + 80, "Smallest thing that tests the hypothesis:", 11, BLUE[0], weight=600))
    b.append(lines(x + 18, y + 108, x + w - 18, 4, 26))
    b.append(field(x + 18, y + 240, "Persevere if…", x + w - 18, BLUE[0]))
    b.append(field(x + 18, y + 280, "Pivot or stop if…", x + w - 18, BLUE[0]))

    # 4 features
    x, y, w = 24, 482, 1632
    d = ORANGE[0]
    b.append(panel(x, y, w, 280, 4, "Features", ORANGE, "SPLIT THE EPIC INTO 3–8 FEATURES THAT EACH DELIVER VALUE"))
    cw = (w - 36 - 4 * 12) / 5
    for i in range(5):
        cx, cy = x + 18 + i * (cw + 12), y + 66
        b.append(R(cx, cy, cw, 200, "white", 6, f' stroke="{d}" stroke-opacity=".2"'))
        b.append(T(cx + 14, cy + 22, f"FEATURE {i + 1}", 9, d, MONO, weight=600, ls=".12em"))
        b.append(field(cx + 14, cy + 52, "Name:", cx + cw - 14, d))
        b.append(field(cx + 14, cy + 86, "Benefit:", cx + cw - 14, d))
        b.append(L(cx + 14, cy + 114, cx + cw - 14, cy + 114))
        b.append(T(cx + 14, cy + 148, "Size:", 11, d))
        for j, sz in enumerate(["S", "M", "L", "XL"]):
            b.append(checkbox(cx + 56 + j * 50, cy + 148, sz, d, 10.5))
        b.append(checkbox(cx + 14, cy + 182, "Part of the MVP", d, 10.5))

    # 5 first stories, 6 out of scope, 7 risks
    y = 776
    x, w = 24, 808
    d = FOREST[0]
    b.append(panel(x, y, w, 284, 5, "First Stories", FOREST, "FROM THE MVP FEATURES"))
    b.append(bullets(x + 22, y + 74, ["Slice vertically: each story is usable end-to-end",
                                      "Too big for an iteration? Use the Story Splitting poster"], d))
    b.append(dashed(x + 10, x + w - 10, y + 104, d))
    b.append(sticky_zone(x + 10, y + 110, w - 20, 162, d, chips=(YELLOW,)))

    x, w = 846, 397
    d = AMBER[0]
    b.append(panel(x, y, w, 284, 6, "Out of Scope & NFRs", AMBER))
    b.append(T(x + 18, y + 80, "We are explicitly not doing:", 11, d, weight=600))
    b.append(lines(x + 18, y + 108, x + w - 18, 3, 26))
    b.append(T(x + 18, y + 202, "Non-functional needs (security, scale…):", 11, d, weight=600))
    b.append(lines(x + 18, y + 230, x + w - 18, 2, 26))

    x = 1257
    d = RED[0]
    b.append(panel(x, y, w, 284, 7, "Dependencies & Risks", RED))
    b.append(bullets(x + 22, y + 74, ["Other teams, systems or suppliers we need", "What could stop or delay this?"], d))
    b.append(dashed(x + 10, x + w - 10, y + 104, d))
    b.append(sticky_zone(x + 10, y + 110, w - 20, 162, d, chips=(YELLOW,)))

    b.append(footer("What's the smallest thing we could build to learn whether this epic is worth it?",
                    "Which feature, if it were the only one, would still deliver value?", BREAKDOWN_TAG))
    write_board("epic-breakdown-canvas", "Epic Breakdown Canvas",
                "A3 landscape canvas: epic hypothesis, outcomes, MVP, five feature cards with size and MVP flags, "
                "first stories, out-of-scope items and NFRs, and dependencies and risks.", "\n".join(b))


# ---------------------------------------------------------------- story map

def build_story_map():
    b = [header("User Story Map",
                "Map the user's journey, then slice it into releases that each deliver a complete, usable path.",
                "Break Down Work · Inspired by Jeff Patton's Story Mapping · Walking Skeleton · Release Slices",
                legend([("sticky", BLUE_ST, "Blue Sticky = Activity (backbone)"),
                        ("sticky", YELLOW, "Yellow Sticky = User Task"),
                        ("sticky", GREEN, "Green Sticky = Story / Detail")]))]

    # context bar
    b.append(R(24, 148, 1632, 48, "white", 8, f' stroke="{RULE}" stroke-width="1.5" filter="url(#fsm)"'))
    b.append(field(44, 178, "Persona / user:", 520, INK, 12))
    b.append(field(546, 178, "Their goal:", 1100, INK, 12))
    b.append(field(1126, 178, "Product / epic:", 1636, INK, 12))

    def lane(y, h, num, title, desc, color, chip, note):
        dark, light = color
        return "".join([
            R(24, y, 230, h, dark, 10),
            f'<circle cx="46" cy="{y + 24}" r="12" fill="white" fill-opacity=".18"/>',
            T(46, y + 29, str(num), 11, "white", weight=600, anchor="middle"),
            T(68, y + 30, title, 14, "white", weight=600),
            para(24 + 20, y + 54, desc, 10.5, "white", 15, op=".88"),
            R(264, y, 1392, h, light, 10, f' stroke="{dark}" stroke-opacity=".18" stroke-width="1.5"'),
            R(264, y, 1392, h, "url(#dots)", 10),
            T(1640, y + 20, note, 8.5, dark, MONO, anchor="end", op=".88", ls=".1em"),
            "".join(R(300 + i * 150, y + 28, 110, h - 46, chip, 3, ' fill-opacity=".22"') for i in range(4)),
            T(300 + 4 * 150 + 20, y + h / 2 + 4, "…one sticky per step, left to right", 10, dark, italic=True, op=".4"),
        ])

    b.append(lane(208, 98, 1, "Activities", ["The backbone: the big things", "users do, in order"], BLUE, BLUE_ST,
                  "USER JOURNEY → LEFT TO RIGHT, IN THE ORDER USERS DO THINGS"))
    b.append(lane(316, 98, 2, "User Tasks", ["The walking skeleton: steps", "within each activity"], AMBER, YELLOW,
                  "UNDER EACH ACTIVITY"))

    b.append(strip(426, "RELEASE SLICES: STORIES GO BELOW EACH TASK, MOST IMPORTANT AT THE TOP. EACH SLICE IS A COMPLETE PATH"))

    def band(y, h, name, sub, color):
        dark, light = color
        return "".join([
            R(24, y, 230, h, light, 10, f' stroke="{dark}" stroke-opacity=".3" stroke-width="1.5"'),
            R(24, y, 6, h, dark, 3),
            T(44, y + 30, name, 15, dark, weight=600),
            para(44, y + 52, sub, 10.5, dark, 15, op=".88"),
            field(44, y + h - 52, "Outcome:", 238, dark, 11),
            field(44, y + h - 20, "Target:", 238, dark, 11),
            R(264, y, 1392, h, light, 10, f' fill-opacity=".55" stroke="{dark}" stroke-opacity=".25" stroke-dasharray="6,5" stroke-width="1.5"'),
            R(264, y, 1392, h, "url(#dots)", 10),
            T(960, y + h / 2 + 4, "Stories for this slice, under the task they belong to", 10, dark, italic=True,
              anchor="middle", op=".3"),
        ])

    b.append(band(468, 220, "Release 1 · MVP", ["The thinnest slice that lets", "a user reach their goal", "end-to-end"], EMERALD))
    b.append(band(698, 190, "Release 2", ["Makes the journey better:", "more options, fewer errors"], BLUE))
    b.append(band(898, 162, "Later", ["Nice to have.", "Revisit after learning", "from earlier releases"], SLATE))

    b.append(footer("What's the smallest slice that lets a user reach their goal end-to-end?",
                    "What will we learn from releasing this slice?", BREAKDOWN_TAG))
    write_board("story-map-board", "User Story Map",
                "A3 landscape story map: persona and goal, an activities backbone, user tasks (walking skeleton), "
                "and three release slices (MVP, Release 2, Later) for stories.", "\n".join(b))


# ---------------------------------------------------------------- story splitting poster

PATTERNS = [
    ("Workflow Steps", "PATHS", ["Split along the steps users take.", "Build the thinnest end-to-end path", "first, then add the extra steps."],
     "Basket → pay → confirmation", "Gift wrap, delivery notes"),
    ("Business Rules", "RULES", ["Start with the simplest rule set,", "then add each rule variation as", "its own story."],
     "Standard delivery, no discounts", "Discount codes, delivery limits"),
    ("Happy / Unhappy Paths", "PATHS", ["Deliver the success path first,", "then handle errors and edge cases", "in follow-up stories."],
     "Card payment succeeds", "Declined card, timeout, retry"),
    ("Data Variations", "DATA", ["Support one type of data first,", "then widen to more types, formats", "or sources."],
     "UK addresses", "International addresses"),
    ("Interfaces", "INTERFACES", ["Start with one channel, device or", "input method, then add the others."],
     "Web checkout, card only", "Mobile app, Apple Pay, PayPal"),
    ("Simple → Complex", "SIMPLIFY", ["Ask “what's the simplest version", "that could work?”, then defer the", "complicated parts."],
     "Flat shipping fee", "Price by weight and zone"),
    ("Operations (CRUD)", "OPERATIONS", ["Split “manage X” into create, read,", "update and delete. Ship the ones", "users need first."],
     "Save and view a card", "Edit and delete saved cards"),
    ("Defer Performance", "QUALITY", ["Make it work, then make it fast or", "scale. Agree the minimum bar in", "the Definition of Done."],
     "100 orders an hour", "Black Friday peak load"),
    ("Spike First", "SPIKE", ["Too unknown to split? Timebox", "research first. The output is", "knowledge, not code."],
     "1-day spike: choose a provider", "Split the build using 1–8"),
]
PATTERN_COLORS = [BLUE, PURPLE, FOREST, SKY, ORANGE, EMERALD, AMBER, RED, SLATE]


def build_story_splitting():
    right = "".join([
        T(1356, 50, "RUNNING EXAMPLE", 8, "#8291A6", MONO, ls=".14em"),
        para(1356, 74, ["“As a shopper, I want to check out", "my basket so that I receive", "my order.”"], 15, "#CBD5E1", 19, font=SERIF, italic=True),
    ])
    b = [header("Story Splitting",
                "When a story is too big to finish in an iteration, split it into thin, vertical slices that each deliver value.",
                "Break Down Work · INVEST · SPIDR · Story Splitting Patterns · Vertical Slicing", right)]

    # INVEST row
    invest = [("I", "Independent", ["Can it be built and", "released on its own?"]),
              ("N", "Negotiable", ["Is it a conversation,", "not a contract?"]),
              ("V", "Valuable", ["Does a user or customer", "get value from it?"]),
              ("E", "Estimable", ["Do we understand it", "well enough to size it?"]),
              ("S", "Small", ["Can we finish it in a", "few days, well within an iteration?"]),
              ("T", "Testable", ["Do we know how to", "prove it's done?"])]
    iw = (1632 - 5 * 12) / 6
    for i, (letter, word, q) in enumerate(invest):
        x = 24 + i * (iw + 12)
        b.append(R(x, 148, iw, 112, "white", 8, f' stroke="{RULE}" stroke-width="1.5" filter="url(#fsm)"'))
        b.append(R(x, 148, iw, 4, ACCENT, 2))
        b.append(T(x + 30, 214, letter, 50, ACCENT, SERIF, anchor="middle"))
        b.append(T(x + 62, 182, word, 14, INK, weight=600))
        b.append(para(x + 62, 204, q, 11, MUTED, 16))
    b.append(T(24, 278, "BEFORE YOU SPLIT: DOES THE STORY PASS INVEST? IF “SMALL” FAILS, SPLIT IT. IF “VALUABLE” FAILS, RETHINK IT.",
               9, MUTED, MONO, ls=".1em"))

    b.append(strip(290, "SPLITTING PATTERNS: TRY THEM IN ROUGHLY THIS ORDER"))
    pw = (1632 - 4 * 12) / 5
    for i, ((name, tag, how, first, later), (dark, light)) in enumerate(zip(PATTERNS, PATTERN_COLORS)):
        x = 24 + (i % 5) * (pw + 12)
        y = 332 + (i // 5) * 208
        b.append(R(x, y, pw, 196, "white", 8, f' stroke="{RULE}" stroke-width="1.5" filter="url(#fsm)"'))
        b.append(R(x, y, 5, 196, dark, 3))
        b.append(f'<circle cx="{x + 28}" cy="{y + 26}" r="12" fill="{dark}"/>')
        b.append(T(x + 28, y + 30, str(i + 1), 11, "white", weight=600, anchor="middle"))
        b.append(T(x + 48, y + 31, name, 14, INK, weight=600))
        tw = len(tag) * 8.5 * 0.68 + 14
        b.append(R(x + pw - 14 - tw, y + 16, tw, 18, light, 9))
        b.append(T(x + pw - 14 - tw / 2, y + 28, tag, 8.5, dark, MONO, weight=600, anchor="middle", ls=".08em"))
        b.append(para(x + 20, y + 62, how, 11, INK, 16))
        b.append(R(x + 14, y + 118, pw - 28, 64, light, 6, ' fill-opacity=".6"'))
        b.append(T(x + 24, y + 138, "FIRST", 8.5, FOREST[0], MONO, weight=600, ls=".1em"))
        b.append(T(x + 72, y + 138, first, 11, INK))
        b.append(T(x + 24, y + 166, "LATER", 8.5, MUTED, MONO, weight=600, ls=".1em"))
        b.append(T(x + 72, y + 166, later, 11, MUTED))
    # 10th card: still too big
    x, y = 24 + 4 * (pw + 12), 540
    b.append(R(x, y, pw, 196, NAVY, 8))
    b.append(R(x, y, 5, 196, ACCENT, 3))
    b.append(T(x + 20, y + 31, "Still too big?", 14, "white", weight=600))
    b.append(bullets(x + 24, y + 58, ["Combine patterns: workflow first,", "then rules within one step"], "#CBD5E1"))
    b.append(bullets(x + 24, y + 104, ["Find the 80/20: which slice gives", "the most value for the least effort?"], "#CBD5E1"))
    b.append(bullets(x + 24, y + 150, ["Ask what could be dropped", "entirely, not just deferred"], "#CBD5E1"))

    # slice vertically diagram
    x, y, w = 24, 752, 808
    d = BLUE[0]
    b.append(panel(x, y, w, 308, None, "Slice Vertically, Not Horizontally", BLUE))
    layers = ["UI / screens", "Logic / API", "Data / storage"]
    # horizontal: wrong
    b.append(T(x + 24, y + 84, "✗  HORIZONTAL", 10, RED[0], MONO, weight=600, ls=".1em"))
    for j, lab in enumerate(layers):
        ly = y + 98 + j * 52
        b.append(R(x + 24, ly, 340, 42, "white", 5, f' stroke="{RED[0]}" stroke-opacity=".35"'))
        b.append(T(x + 38, ly + 26, lab, 11, INK))
        b.append(T(x + 350, ly + 26, f"Story {j + 1}", 10, RED[0], MONO, anchor="end"))
    b.append(T(x + 24, y + 278, "Nothing is usable until every layer is finished.", 11, RED[0], italic=True))
    # vertical: right
    vx = x + 420
    b.append(T(vx, y + 84, "✓  VERTICAL", 10, FOREST[0], MONO, weight=600, ls=".1em"))
    for j, lab in enumerate(layers):
        ly = y + 98 + j * 52
        b.append(R(vx, ly, 364, 42, "white", 5, f' stroke="{d}" stroke-opacity=".2"'))
        b.append(T(vx + 12, ly + 26, lab, 11, MUTED, op=".88"))
    for k in range(4):
        sx = vx + 124 + k * 60
        b.append(R(sx, y + 92, 44, 166, ACCENT, 5, ' fill-opacity=".8"'))
        b.append(T(sx + 22, y + 270, f"Slice {k + 1}", 9, ACCENT, MONO, weight=600, anchor="middle"))
    b.append(T(vx, y + 292, "Each slice is usable and testable on its own.", 11, FOREST[0], italic=True))

    # checks
    x, w = 846, 810
    d = EMERALD[0]
    b.append(panel(x, y, w, 308, None, "Is It a Good Split?", EMERALD))
    b.append(T(x + 22, y + 84, "AFTER SPLITTING, CHECK EACH SLICE", 9, d, MONO, weight=600, ls=".1em"))
    b.append(bullets(x + 26, y + 106, ["Delivers value or learning by itself", "Fits comfortably in an iteration: aim for several per iteration",
                                       "Has clear acceptance criteria", "The team can estimate it", "Still passes INVEST"], d, 22))
    b.append(T(x + 420, y + 84, "CHOOSE THE SPLIT THAT…", 9, d, MONO, weight=600, ls=".1em"))
    b.append(bullets(x + 424, y + 106, ["Lets you deprioritise or drop a slice", "Makes slices of roughly equal size",
                                        "Gets user feedback soonest", "Tackles the biggest risk first",
                                        "Exposes low-value work you can skip"], d, 22))
    b.append(T(x + w / 2, y + 260, "If no slice can be dropped, try a different pattern.", 16, d, SERIF, italic=True, anchor="middle"))

    b.append(footer("What's the thinnest slice that still delivers value to a user?",
                    "If we could only ship half of this, which half?",
                    "INVEST (Bill Wake) · SPIDR (Mike Cohn) · Splitting Patterns (Richard Lawrence)"))
    write_board("story-splitting-poster", "Story Splitting",
                "A3 landscape reference poster: the INVEST check, nine story splitting patterns with a running checkout "
                "example, vertical vs. horizontal slicing, and checks for a good split.", "\n".join(b))


# ---------------------------------------------------------------- example mapping

def build_example_mapping():
    b = [header("Example Mapping",
                "Explore one story through its rules, concrete examples and open questions, and find out if it's ready.",
                "Break Down Work · Inspired by Matt Wynne's Example Mapping · Refinement · 25-Minute Timebox",
                legend([("sticky", YELLOW, "Yellow = Story"), ("sticky", BLUE_ST, "Blue = Rule"),
                        ("sticky", GREEN, "Green = Example"), ("sticky", PINK_ST, "Pink = Question")]))]

    # story bar
    b.append(R(24, 148, 1632, 104, "white", 10, f' stroke="{RULE}" stroke-width="1.5" filter="url(#fc)"'))
    b.append(slot(40, 160, 300, 80, YELLOW, AMBER[0], "Story card"))
    b.append(field(362, 192, "As a…", 760, INK, 12))
    b.append(field(782, 192, "I want…", 1220, INK, 12))
    b.append(field(1242, 192, "so that…", 1636, INK, 12))
    b.append(T(362, 230, "TIMEBOX 25 MIN · ONE BLUE CARD PER RULE · GREEN EXAMPLES UNDER EACH RULE · PINK FOR ANYTHING UNKNOWN",
               9, MUTED, MONO, ls=".1em"))

    cw = (1278 - 36) / 4
    for i in range(4):
        x = 24 + i * (cw + 12)
        d = BLUE[0]
        b.append(panel(x, 266, cw, 586, i + 1, f"Rule {i + 1}", BLUE, "ACCEPTANCE CRITERION"))
        b.append(slot(x + 14, 332, cw - 28, 84, BLUE_ST, d, "Blue card: the rule"))
        b.append(T(x + 16, 444, "EXAMPLES", 9, FOREST[0], MONO, weight=600, ls=".12em"))
        b.append(T(x + cw - 16, 444, "given · when · then", 9, FOREST[0], MONO, anchor="end", op=".88"))
        b.append(sticky_zone(x + 10, 454, cw - 20, 386, d, "Green cards: concrete examples", chips=(GREEN,)))

    x, w = 1314, 342
    d = "#9D174D"
    b.append(panel(x, 266, w, 586, None, "Questions", (d, "#FCE7F3"), "UNKNOWNS"))
    b.append(bullets(x + 22, 340, ["Anything nobody here can answer", "Write who will find out", "Don't let one question stall the session"], d))
    b.append(dashed(x + 10, x + w - 10, 390, d))
    b.append(sticky_zone(x + 10, 396, w - 20, 444, d, "Pink cards: open questions", chips=(PINK_ST,)))

    b.append(strip(866, "OUTCOME: THUMB-VOTE AT THE END OF THE TIMEBOX"))
    b.append(R(24, 906, 534, 154, "white", 8, f' stroke="{RULE}" stroke-width="1.5" filter="url(#fsm)"'))
    b.append(R(24, 906, 5, 154, ACCENT, 3))
    b.append(T(46, 940, "Decision", 13, INK, weight=600))
    for j, (lab, note) in enumerate([("Ready to plan", "few questions, rules are clear"),
                                     ("Needs splitting", "too many rules: split by rule"),
                                     ("Needs answers first", "too many questions: find out")]):
        b.append(checkbox(46, 974 + j * 30, lab, INK, 12))
        b.append(T(220, 974 + j * 30, note, 11, MUTED, italic=True))
    b.append(card(572, 906, 534, 154, "Split into…", EMERALD[0], ["Story A:", "Story B:"]))
    b.append(card(1120, 906, 534, 154, "Open questions", "#9D174D", ["Owner:", "Answer by:"]))

    b.append(footer("Lots of pink? We're not ready yet.", "Lots of blue? The story is too big, so split it by rule.",
                    BREAKDOWN_TAG))
    write_board("example-mapping-board", "Example Mapping",
                "A3 landscape example mapping board: story card and statement, four rule columns with example zones, "
                "a questions column, and an outcome strip for the ready / split / needs-answers decision.", "\n".join(b))


# ---------------------------------------------------------------- lifecycle helpers

def check_lines(x, y, x_end, n, color, gap=30):
    """Empty checkbox followed by a write-on line, n times."""
    out = []
    for i in range(n):
        cy = y + i * gap
        out.append(R(x, cy - 10, 12, 12, "white", 2, f' stroke="{color}" stroke-opacity=".6" stroke-width="1.2"'))
        out.append(L(x + 22, cy + 3, x_end, cy + 3, WRITE))
    return "".join(out)


def table(x, y, cols, n, color, row_h=32):
    """Write-on table. cols: list of (label, width); header labels sit at y."""
    dark = color
    w = sum(cw for _, cw in cols)
    out = []
    cx = x
    for label, cw in cols:
        out.append(T(cx + 6, y, label.upper(), 8.5, dark, MONO, weight=600, ls=".1em"))
        cx += cw
    out.append(L(x, y + 10, x + w, y + 10, dark, 1.2, ' stroke-opacity=".35"'))
    for i in range(1, n + 1):
        out.append(L(x, y + 10 + i * row_h, x + w, y + 10 + i * row_h, WRITE))
    cx = x
    for _, cw in cols[:-1]:
        cx += cw
        out.append(L(cx, y - 12, cx, y + 10 + n * row_h, dark, 1, ' stroke-opacity=".15"'))
    return "".join(out)


def label(x, y, s, color, size=11):
    return T(x, y, s, size, color, weight=600)


LIFECYCLE_TAG = "Agile Lifecycle · Plan · Build · Review · Improve"


# ---------------------------------------------------------------- team charter

def build_team_charter():
    b = [header("Team Charter",
                "Agree why the team exists, how it works together, and what Ready and Done mean, before the work starts.",
                "Team Formation · Working Agreements · Definition of Ready & Done · Review It as the Team Changes",
                header_fields(["Team", "Date"]))]

    # row 1
    y, h = 148, 300
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Purpose", PURPLE, "WHY DOES THIS TEAM EXIST?"))
    for i, lead in enumerate(["We exist to…", "for…", "We succeed when…"]):
        ly = y + 96 + i * 66
        b.append(T(x + 18, ly, lead, 19, d, SERIF, italic=True))
        b.append(L(x + 190, ly + 3, x + w - 18, ly + 3, d, 1, ' stroke-opacity=".25"'))
        b.append(L(x + 18, ly + 33, x + w - 18, ly + 33, d, 1, ' stroke-opacity=".25"'))

    x, w = 846, 397
    d = BLUE[0]
    b.append(panel(x, y, w, h, 2, "Members & Roles", BLUE))
    b.append(table(x + 16, y + 84, [("Name", 120), ("Role", 110), ("What I bring", w - 32 - 230)], 6, d))

    x = 1257
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 3, "Our Values", EMERALD, "WHAT MATTERS TO US"))
    b.append(bullets(x + 22, y + 74, ["3–5 values, each with an example of it in action"], d))
    b.append(dashed(x + 10, x + w - 10, y + 92, d))
    b.append(sticky_zone(x + 10, y + 98, w - 20, h - 110, d, chips=(YELLOW,)))

    # row 2
    y, h = 462, 300
    x, w = 24, 808
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 4, "Working Agreements", ORANGE, "WE AGREE TO…"))
    b.append(bullets(x + 22, y + 74, ["Communication, core hours, meetings, feedback, how we handle interruptions"], d))
    b.append(dashed(x + 10, x + w - 10, y + 92, d))
    b.append(sticky_zone(x + 10, y + 98, w - 20, h - 110, d, "One agreement per sticky, written as “We…”", chips=(YELLOW,)))

    x, w = 846, 397
    d = SKY[0]
    b.append(panel(x, y, w, h, 5, "How We Decide", SKY))
    for i, m in enumerate(["Consent: no one objects", "Consensus: everyone agrees", "Majority vote",
                           "Consult, then one person decides", "Delegated to an owner"]):
        b.append(checkbox(x + 18, y + 86 + i * 28, m, d, 11))
    b.append(T(x + 18, y + 236, "Default method, and who decides what:", 11, d, weight=600))
    b.append(lines(x + 18, y + 264, x + w - 18, 1))

    x = 1257
    d = SLATE[0]
    b.append(panel(x, y, w, h, 6, "Ways of Working", SLATE, "CADENCE & TOOLS"))
    for i, f in enumerate(["Iteration length:", "Planning:", "Daily sync:", "Review:", "Retro:", "Board / tools:", "Channels:"]):
        b.append(field(x + 18, y + 86 + i * 30, f, x + w - 18, d))

    # row 3
    y, h, w = 776, 284, 534
    for i, (num, title, color, note, hint) in enumerate([
            (7, "Definition of Ready", AMBER, "BEFORE WE START AN ITEM", "e.g. value is clear, it's small enough, examples agreed"),
            (8, "Definition of Done", FOREST, "BEFORE WE CALL IT DONE", "e.g. tested, reviewed, documented, releasable")]):
        x = 24 + i * 548
        d = color[0]
        b.append(panel(x, y, w, h, num, title, color, note))
        b.append(T(x + 18, y + 78, hint, 10.5, d, italic=True, op=".88"))
        b.append(check_lines(x + 18, y + 110, x + w - 18, 6, d))

    x = 1120
    d = RED[0]
    b.append(panel(x, y, 536, h, 9, "Conflict & Review", RED))
    b.append(T(x + 18, y + 82, "When we disagree, we…", 11, d, weight=600))
    b.append(lines(x + 18, y + 110, x + 536 - 18, 2))
    b.append(T(x + 18, y + 170, "We review this charter:", 11, d, weight=600))
    for j, lab in enumerate(["Every quarter", "When someone joins", "When it stops working"]):
        b.append(checkbox(x + 18 + j * 168, y + 200, lab, d, 10.5))
    b.append(field(x + 18, y + 244, "Signed by the team:", x + 536 - 18, d))

    b.append(footer("What would make this the best team any of us has worked on?",
                    "Which of these agreements will we find hardest to keep?",
                    "Team Formation · Working Agreements · Continuous Improvement"))
    write_board("team-charter-board", "Team Charter",
                "A3 landscape team charter: purpose, members and roles, values, working agreements, decision methods, "
                "ways of working, Definition of Ready, Definition of Done, and conflict and review.", "\n".join(b))


# ---------------------------------------------------------------- product vision board

def build_product_vision():
    b = [header("Product Vision Board",
                "Describe the change the product will bring, who it's for, what they need, and how we'll know it's working.",
                "Envision · Inspired by Roman Pichler's Product Vision Board · Outcomes Over Output",
                header_fields(["Product", "Owner"]))]

    x, y, w, h = 24, 148, 1632, 176
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Vision", PURPLE, "THE POSITIVE CHANGE THE PRODUCT WILL BRING · NOT WHAT IT IS"))
    b.append(T(x + 18, y + 98, "Our vision is…", 22, d, SERIF, italic=True))
    b.append(L(x + 190, y + 101, x + w - 18, y + 101, d, 1, ' stroke-opacity=".25"'))
    b.append(L(x + 18, y + 142, x + w - 18, y + 142, d, 1, ' stroke-opacity=".25"'))

    y, h = 338, 470
    cw = (1632 - 3 * 14) / 4
    cols = [(2, "Target Group", BLUE, "WHO?", ["Which users and customers?", "Who is the most important group?", "Who is it not for?"]),
            (3, "Needs", EMERALD, "WHY?", ["What problem does it solve?", "What benefit does it bring?", "How do they solve it today?"]),
            (4, "Product", ORANGE, "WHAT?", ["The 3–5 things that make it stand out", "Is it feasible?", "How is it different?"]),
            (5, "Business Goals", AMBER, "WHY US?", ["How does it help the organisation?", "Revenue, cost, reach, reputation?", "Which goal matters most?"])]
    for i, (num, title, color, note, prompts) in enumerate(cols):
        x = 24 + i * (cw + 14)
        d = color[0]
        b.append(panel(x, y, cw, h, num, title, color, note))
        b.append(bullets(x + 22, y + 74, prompts, d))
        b.append(dashed(x + 10, x + cw - 10, y + 128, d))
        b.append(sticky_zone(x + 10, y + 134, cw - 20, h - 146, d, chips=(YELLOW,)))

    y, h = 822, 238
    x, w = 24, 808
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "Measures of Success", FOREST, "HOW WE'LL KNOW IT'S WORKING"))
    b.append(table(x + 18, y + 84, [("Outcome", 300), ("Measure", 230), ("Baseline", 118), ("Target", w - 36 - 648)], 4, d))

    x = 846
    d = RED[0]
    b.append(panel(x, y, w, h, 7, "Riskiest Assumptions", RED, "TEST THESE FIRST"))
    b.append(bullets(x + 22, y + 74, ["What must be true for this vision to work?",
                                      "Test the riskiest with the 1% Experiment Canvas or an MVP"], d))
    b.append(dashed(x + 10, x + w - 10, y + 110, d))
    b.append(sticky_zone(x + 10, y + 116, w - 20, h - 128, d, chips=(YELLOW, PINK_ST)))

    b.append(footer("What will be different for our users when this succeeds?",
                    "Who is this not for?", "Envision · Product Strategy · Outcomes Over Output"))
    write_board("product-vision-board", "Product Vision Board",
                "A3 landscape product vision board: vision statement, target group, needs, product, business goals, "
                "measures of success, and riskiest assumptions to test.", "\n".join(b))


# ---------------------------------------------------------------- prioritisation board

def build_prioritisation():
    b = [header("Prioritisation Board",
                "Compare value and effort, put a number on the cost of delay, agree what's in, and lay out Now, Next and Later.",
                "Plan · Value vs. Effort · Cost of Delay (CD3 / WSJF) · MoSCoW · Now / Next / Later Roadmap",
                header_fields(["Product / scope", "Date"]))]

    # 1 value vs effort
    x, y, w, h = 24, 148, 808, 600
    b.append(panel(x, y, w, h, 1, "Value vs. Effort", BLUE, "PLACE EACH ITEM ON THE GRID"))
    gx0, gy0, gx1, gy1 = x + 54, y + 70, x + w - 18, y + h - 52
    mx, my = (gx0 + gx1) / 2, (gy0 + gy1) / 2
    quads = [(gx0, gy0, "Quick Wins", "High value · low effort · do these first", EMERALD),
             (mx, gy0, "Big Bets", "High value · high effort · slice them first", BLUE),
             (gx0, my, "Fill-ins", "Low value · low effort · if there's spare time", AMBER),
             (mx, my, "Money Pits", "Low value · high effort · avoid or drop", RED)]
    for qx, qy, name, sub, (dk, lt) in quads:
        b.append(R(qx + 2, qy + 2, mx - gx0 - 4, my - gy0 - 4, lt, 6))
        b.append(R(qx + 2, qy + 2, mx - gx0 - 4, my - gy0 - 4, "url(#dots)", 6))
        b.append(T(qx + 16, qy + 28, name, 15, dk, weight=600))
        b.append(T(qx + 16, qy + 46, sub, 10, dk, op=".88"))
    b.append(L(gx0, gy1, gx1, gy1, INK, 1.5))
    b.append(L(gx0, gy0, gx0, gy1, INK, 1.5))
    b.append(T(gx0, gy1 + 22, "LOW EFFORT", 9, MUTED, MONO, ls=".12em"))
    b.append(T(gx1, gy1 + 22, "HIGH EFFORT", 9, MUTED, MONO, anchor="end", ls=".12em"))
    b.append(T(mx, gy1 + 22, "EFFORT →", 9, INK, MONO, weight=600, anchor="middle", ls=".12em"))
    vy = (gy0 + gy1) / 2
    b.append(f'<text transform="translate({gx0 - 22:g},{vy:g}) rotate(-90)" text-anchor="middle" font-family="{MONO}" '
             f'font-size="9" font-weight="600" fill="{INK}" letter-spacing=".12em">VALUE →</text>')

    # 2 cost of delay
    x, y, w, h = 846, 148, 810, 290
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Cost of Delay · WSJF", PURPLE, "CD3 · CALLED WSJF IN SAFe · HIGHEST SCORE FIRST"))
    b.append(T(x + 18, y + 76, "Score one column at a time across all items: 1, 2, 3, 5, 8, 13 (smallest item = 1). CoD = value + time + risk.",
               10.5, d, italic=True, op=".88"))
    b.append(table(x + 18, y + 108, [("Item", 196), ("Value", 66), ("Time", 66), ("Risk / opp.", 92),
                                     ("CoD", 60), ("Job size", 80), ("CoD / size", 92), ("Rank", w - 36 - 652)], 5, d, 32))

    # 3 moscow
    x, y, w, h = 846, 452, 810, 296
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 3, "MoSCoW", ORANGE, "FOR A FIXED DATE OR SCOPE"))
    mw = (w - 20 - 3 * 10) / 4
    for i, (name, sub, col) in enumerate([("Must", "Fails without it", RED), ("Should", "Important, not vital", ORANGE),
                                          ("Could", "Nice if there's time", AMBER), ("Won't (this time)", "Agreed out", SLATE)]):
        cx = x + 10 + i * (mw + 10)
        b.append(T(cx + 6, y + 78, name, 13, col[0], weight=600))
        b.append(T(cx + 6, y + 94, sub, 9.5, col[0], op=".88"))
        b.append(sticky_zone(cx, y + 104, mw, h - 116, col[0], "Stickies", chips=(YELLOW,)))

    # 4 roadmap
    x, y, w, h = 24, 762, 1632, 298
    b.append(panel(x, y, w, h, 4, "Now · Next · Later", FOREST, "A ROADMAP OF OUTCOMES, NOT DATES"))
    rw = (w - 20 - 2 * 12) / 3
    for i, (name, sub, col) in enumerate([("Now", "Committed and in progress", EMERALD),
                                          ("Next", "Planned and being shaped", BLUE),
                                          ("Later", "Ideas and options, not committed", SLATE)]):
        cx = x + 10 + i * (rw + 12)
        d = col[0]
        b.append(R(cx, y + 64, rw, h - 76, col[1], 6, f' stroke="{d}" stroke-opacity=".2"'))
        b.append(T(cx + 14, y + 90, name.upper(), 12, d, MONO, weight=600, ls=".14em"))
        b.append(T(cx + rw - 14, y + 90, sub, 10, d, anchor="end", op=".88"))
        b.append(sticky_zone(cx + 8, y + 102, rw - 16, h - 166, d, chips=(YELLOW,)))
        b.append(field(cx + 14, y + h - 28, "Outcome:", cx + rw - 14, d))

    b.append(footer("What does it cost us, each week, to not have this yet?",
                    "If we could only do one thing this quarter, what would it be?", "Plan · Prioritise · Deliver Value Early"))
    write_board("prioritisation-board", "Prioritisation Board",
                "A3 landscape prioritisation board: value vs. effort grid, cost of delay table (CD3 / WSJF), MoSCoW columns, "
                "and a Now / Next / Later roadmap.", "\n".join(b))


# ---------------------------------------------------------------- sprint planning

def build_sprint_planning():
    b = [header("Sprint Planning",
                "Agree why this sprint matters, what can be done, and how the team will start, in one visible plan.",
                "Build in Iterations · Sprint Goal · Capacity · Forecast, Not Commitment to Every Item",
                header_fields(["Team", "Sprint dates"]))]

    y, h = 148, 268
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Sprint Goal", PURPLE, "WHY IS THIS SPRINT VALUABLE?"))
    b.append(T(x + 18, y + 96, "By the end of this sprint…", 19, d, SERIF, italic=True))
    b.append(L(x + 250, y + 99, x + w - 18, y + 99, d, 1, ' stroke-opacity=".25"'))
    b.append(L(x + 18, y + 135, x + w - 18, y + 135, d, 1, ' stroke-opacity=".25"'))
    b.append(field(x + 18, y + 182, "We'll know we've achieved it when…", x + w - 18, d))
    b.append(field(x + 18, y + 222, "It supports this product goal:", x + w - 18, d))

    x, w = 846, 397
    d = BLUE[0]
    b.append(panel(x, y, w, h, 2, "Capacity", BLUE, "BE REALISTIC"))
    for i, f in enumerate(["Working days:", "People available:", "Holidays & absences:", "Other commitments:",
                           "Recent throughput (last 3):", "Capacity this sprint:"]):
        b.append(field(x + 18, y + 86 + i * 30, f, x + w - 18, d))

    x = 1257
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 3, "Inputs Checked", EMERALD))
    for i, m in enumerate(["Product goal & roadmap reviewed", "Top of the backlog is ready", "Last review's feedback included",
                           "Retro actions planned in", "Dependencies known", "Definition of Done visible"]):
        b.append(checkbox(x + 18, y + 86 + i * 30, m, d, 11))

    y, h = 430, 420
    x, w = 24, 1219
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 4, "Selected Items", ORANGE, "IN PRIORITY ORDER · STOP WHEN CAPACITY IS REACHED"))
    hw = (w - 30) / 2
    for i, (name, sub) in enumerate([("Needed for the Sprint Goal", "If we only finish these, the sprint still succeeds"),
                                     ("Also planned", "Valuable, but they can move if the goal is at risk")]):
        cx = x + 10 + i * (hw + 10)
        b.append(T(cx + 6, y + 78, name, 13, d, weight=600))
        b.append(T(cx + 6, y + 96, sub, 10, d, op=".88"))
        b.append(sticky_zone(cx, y + 106, hw, h - 118, d, chips=(YELLOW,)))

    x, w = 1257, 397
    d = RED[0]
    b.append(panel(x, y, w, h, 5, "Risks & Dependencies", RED))
    b.append(bullets(x + 22, y + 74, ["What could stop us reaching the goal?", "Who outside the team do we need, and when?"], d))
    b.append(dashed(x + 10, x + w - 10, y + 110, d))
    b.append(sticky_zone(x + 10, y + 116, w - 20, h - 128, d, chips=(YELLOW, PINK_ST)))

    y, h = 864, 196
    x, w = 24, 808
    d = SKY[0]
    b.append(panel(x, y, w, h, 6, "How We'll Start", SKY, "THE FIRST DAYS"))
    b.append(field(x + 18, y + 86, "Day 1, we start with:", x + w - 18, d))
    b.append(field(x + 18, y + 120, "Pairing / swarming on:", x + w - 18, d))
    b.append(field(x + 18, y + 154, "First thing to finish:", x + w - 18, d))

    x = 846
    d = FOREST[0]
    b.append(panel(x, y, w, h, 7, "Confidence Vote", FOREST, "FIST OF FIVE"))
    for i, lab in enumerate(["No confidence", "Serious concerns", "Some concerns", "Confident", "Very confident"]):
        cx = x + 70 + i * 108
        b.append(f'<circle cx="{cx}" cy="{y + 92}" r="17" fill="white" stroke="{d}" stroke-opacity=".5" stroke-width="1.5"/>')
        b.append(T(cx, y + 98, str(i + 1), 14, d, weight=600, anchor="middle"))
        b.append(T(cx, y + 128, lab, 9.5, d, anchor="middle", op=".88"))
    b.append(field(x + 18, y + 168, "Any 1s or 2s? Concerns raised:", x + w - 18, d))

    b.append(footer("If we only achieve one thing this sprint, what should it be?",
                    "What would stop us from reaching the goal?", LIFECYCLE_TAG))
    write_board("sprint-planning-board", "Sprint Planning",
                "A3 landscape sprint planning board: sprint goal, capacity, inputs checklist, selected items split by "
                "goal and also-planned, risks and dependencies, first-day plan, and a fist-of-five confidence vote.", "\n".join(b))


# ---------------------------------------------------------------- sprint review

def build_sprint_review():
    b = [header("Sprint Review",
                "Show what's done, hear from stakeholders, and decide together what the backlog should look like next.",
                "Review & Release · Inspect the Increment · Stakeholder Feedback · Adapt the Backlog",
                legend([("sticky", YELLOW, "Yellow = Item"), ("sticky", GREEN, "Green = Positive"),
                        ("sticky", PINK_ST, "Pink = Concern"), ("sticky", BLUE_ST, "Blue = Idea")]))]

    y, h = 148, 236
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Sprint Goal & Result", PURPLE))
    b.append(field(x + 18, y + 86, "Team & sprint:", x + w - 18, d))
    b.append(field(x + 18, y + 122, "Sprint Goal:", x + w - 18, d))
    b.append(T(x + 18, y + 162, "Did we achieve it?", 11, d, weight=600))
    for j, lab in enumerate(["Yes", "Partly", "No"]):
        b.append(checkbox(x + 160 + j * 90, y + 162, lab, d, 11))
    b.append(field(x + 18, y + 204, "What we learned about the goal:", x + w - 18, d))

    x = 846
    d = BLUE[0]
    b.append(panel(x, y, 810, h, 2, "Key Measures", BLUE, "DID THE NUMBERS MOVE?"))
    b.append(table(x + 18, y + 84, [("Measure", 300), ("Before", 140), ("Now", 140), ("Target", 810 - 36 - 580)], 4, d))

    y, h = 398, 400
    cols = [(3, "What We Built", EMERALD, "DONE ITEMS ONLY", ["Only work that meets the Definition of Done", "Show working product, not slides"], (YELLOW,)),
            (4, "Stakeholder Feedback", ORANGE, "LISTEN FIRST", ["What did you like? What worries you?", "What would you change or add?"], (GREEN, PINK_ST, BLUE_ST)),
            (5, "What's Changed Around Us", SKY, "CONTEXT", ["Users, market, competitors", "Budget, timeline, priorities"], (YELLOW,))]
    for i, (num, title, color, note, prompts, chips) in enumerate(cols):
        x = 24 + i * 548
        w = 534 if i < 2 else 536
        d = color[0]
        b.append(panel(x, y, w, h, num, title, color, note))
        b.append(bullets(x + 22, y + 74, prompts, d))
        b.append(dashed(x + 10, x + w - 10, y + 110, d))
        b.append(sticky_zone(x + 10, y + 116, w - 20, h - 128, d, chips=chips))

    y, h = 812, 248
    x, w = 24, 1082
    d = AMBER[0]
    b.append(panel(x, y, w, h, 6, "Backlog Changes", AMBER, "WHAT THE REVIEW CHANGES"))
    bw = (w - 20 - 2 * 10) / 3
    for i, (name, sub) in enumerate([("Add", "New items from feedback"), ("Change", "Re-order, re-shape or re-size"),
                                     ("Remove", "No longer worth doing")]):
        cx = x + 10 + i * (bw + 10)
        b.append(T(cx + 6, y + 78, name, 13, d, weight=600))
        b.append(T(cx + 6, y + 94, sub, 9.5, d, op=".88"))
        b.append(sticky_zone(cx, y + 104, bw, h - 116, d, "Stickies", chips=(YELLOW,)))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 7, "What's Next", FOREST))
    for i, f in enumerate(["Likely next Sprint Goal:", "Release / forecast update:", "Decisions needed from stakeholders:",
                           "Who follows up:"]):
        b.append(field(x + 18, y + 90 + i * 38, f, x + w - 18, d))

    b.append(footer("Based on what we've seen, what should we do next?",
                    "What surprised you today?", LIFECYCLE_TAG))
    write_board("sprint-review-board", "Sprint Review",
                "A3 landscape sprint review board: sprint goal and result, key measures, what was built, stakeholder "
                "feedback, changes in context, backlog changes (add, change, remove), and next steps.", "\n".join(b))


# ---------------------------------------------------------------- project & program helpers

PROJECT_TAG = "Run a Project · Stakeholders · Forecasts · Risks"
PROGRAM_TAG = "Coordinate Teams · Shared Outcomes · Manage Dependencies"


def rot_label(x, y, s, fill=INK):
    return (f'<text transform="translate({x:g},{y:g}) rotate(-90)" text-anchor="middle" font-family="{MONO}" '
            f'font-size="9" font-weight="600" fill="{fill}" letter-spacing=".12em">{escape(s)}</text>')


def quad_grid(gx0, gy0, gx1, gy1, quads, x_lo, x_hi, x_name, y_name):
    """2×2 grid. quads: (name, sub, color) for top-left, top-right, bottom-left, bottom-right."""
    mx, my = (gx0 + gx1) / 2, (gy0 + gy1) / 2
    out = []
    for (qx, qy), (name, sub, (dk, lt)) in zip([(gx0, gy0), (mx, gy0), (gx0, my), (mx, my)], quads):
        out.append(R(qx + 2, qy + 2, mx - gx0 - 4, my - gy0 - 4, lt, 6))
        out.append(R(qx + 2, qy + 2, mx - gx0 - 4, my - gy0 - 4, "url(#dots)", 6))
        out.append(T(qx + 16, qy + 28, name, 15, dk, weight=600))
        out.append(T(qx + 16, qy + 46, sub, 10, dk, op=".88"))
    out += [L(gx0, gy1, gx1, gy1, INK, 1.5), L(gx0, gy0, gx0, gy1, INK, 1.5),
            T(gx0, gy1 + 22, x_lo, 9, MUTED, MONO, ls=".12em"),
            T(gx1, gy1 + 22, x_hi, 9, MUTED, MONO, anchor="end", ls=".12em"),
            T(mx, gy1 + 22, x_name, 9, INK, MONO, weight=600, anchor="middle", ls=".12em"),
            rot_label(gx0 - 22, my, y_name)]
    return "".join(out)


def slider(x, y, w, name, color, lo="FLEX", hi="FIXED"):
    out = [T(x, y + 4, name, 12, color, weight=600),
           T(x + 120, y + 4, lo, 8.5, color, MONO, op=".88", ls=".1em"),
           T(x + w, y + 4, hi, 8.5, color, MONO, anchor="end", op=".88", ls=".1em")]
    tx0, tx1 = x + 162, x + w - 50
    out.append(L(tx0, y, tx1, y, color, 2, ' stroke-opacity=".25"'))
    for i in range(5):
        cx = tx0 + i * (tx1 - tx0) / 4
        out.append(f'<circle cx="{cx:g}" cy="{y}" r="8" fill="white" stroke="{color}" stroke-opacity=".5" stroke-width="1.5"/>')
    return "".join(out)


def kanban_cols(x, y, w, h, names, color, gap=10, chips=(YELLOW,)):
    """Labelled sticky columns inside a panel body. names: (title, sub)."""
    cw = (w - (len(names) - 1) * gap) / len(names)
    out = []
    for i, (name, sub) in enumerate(names):
        cx = x + i * (cw + gap)
        out.append(T(cx + 6, y + 14, name, 13, color, weight=600))
        out.append(T(cx + 6, y + 30, sub, 9.5, color, op=".88"))
        out.append(sticky_zone(cx, y + 40, cw, h - 40, color, "Stickies", chips=chips))
    return "".join(out)


# ---------------------------------------------------------------- project kickoff

def build_project_kickoff():
    b = [header("Project Kickoff",
                "Agree why the project exists, what's in and out, what can flex, and who's involved, before the first iteration.",
                "Run a Project · Inception · Scope In & Out · Trade-off Sliders · First Milestones",
                header_fields(["Project", "Sponsor"]))]

    y, h = 148, 260
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Why Are We Here?", PURPLE, "THE PROBLEM AND THE OUTCOME"))
    for i, lead in enumerate(["We're doing this because…", "Success looks like…"]):
        ly = y + 96 + i * 80
        b.append(T(x + 18, ly, lead, 19, d, SERIF, italic=True))
        b.append(L(x + 270, ly + 3, x + w - 18, ly + 3, d, 1, ' stroke-opacity=".25"'))
        b.append(L(x + 18, ly + 38, x + w - 18, ly + 38, d, 1, ' stroke-opacity=".25"'))

    x, w = 846, 810
    b.append(panel(x, y, w, h, 2, "Scope", BLUE, "SAYING WHAT'S OUT MATTERS AS MUCH AS WHAT'S IN"))
    hw = (w - 46) / 2
    for i, (name, col) in enumerate([("In scope", EMERALD), ("Out of scope", RED)]):
        cx = x + 18 + i * (hw + 10)
        b.append(T(cx, y + 80, name, 13, col[0], weight=600))
        b.append(lines(cx, y + 110, cx + hw, 5, 28))

    y, h = 422, 300
    x, w = 24, 808
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 3, "Trade-off Sliders", ORANGE, "ONLY ONE CAN BE FULLY FIXED"))
    b.append(T(x + 18, y + 78, "Mark one dot per row. If everything is fixed, nothing can give when plans change.",
               10.5, d, italic=True, op=".88"))
    for i, name in enumerate(["Scope", "Time", "Budget", "Quality", "Team size"]):
        b.append(slider(x + 18, y + 116 + i * 38, w - 36, name, d))

    x, w = 846, 397
    d = SLATE[0]
    b.append(panel(x, y, w, h, 4, "Constraints & Givens", SLATE))
    b.append(bullets(x + 22, y + 74, ["Fixed dates, regulations, budgets", "Technology and platform choices"], d))
    b.append(lines(x + 18, y + 136, x + w - 18, 6, 28))

    x = 1257
    d = SKY[0]
    b.append(panel(x, y, w, h, 5, "People & Roles", SKY))
    for i, f in enumerate(["Sponsor:", "Product owner:", "Delivery lead:", "Team(s):", "Key experts:", "Decision forum:"]):
        b.append(field(x + 18, y + 88 + i * 34, f, x + w - 18, d))

    y, h = 736, 324
    x, w = 24, 534
    d = RED[0]
    b.append(panel(x, y, w, h, 6, "What Keeps Us Up at Night", RED, "TOP RISKS"))
    b.append(bullets(x + 22, y + 74, ["What could stop or derail this?", "Move the big ones to the RAID Log"], d))
    b.append(dashed(x + 10, x + w - 10, y + 110, d))
    b.append(sticky_zone(x + 10, y + 116, w - 20, h - 128, d, chips=(YELLOW, PINK_ST)))

    x = 572
    d = FOREST[0]
    b.append(panel(x, y, w, h, 7, "First Milestones", FOREST, "OUTCOMES, NOT TASKS"))
    b.append(table(x + 18, y + 84, [("Milestone", 170), ("Outcome", 210), ("Target", w - 36 - 380)], 6, d, 34))

    x, w = 1120, 536
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 8, "Next Steps", EMERALD))
    for i, m in enumerate(["Team Charter for each team", "Product Vision Board", "Stakeholder Map",
                           "Prioritised backlog and first slice", "Release Forecast", "RAID Log set up"]):
        b.append(checkbox(x + 18, y + 86 + i * 30, m, d, 11))
    b.append(field(x + 18, y + 284, "Next review of this board:", x + w - 18, d))

    b.append(footer("What problem are we solving, and for whom?",
                    "If we had to cut half the scope, what would we keep?", PROJECT_TAG))
    write_board("project-kickoff-board", "Project Kickoff",
                "A3 landscape project kickoff board: why we're here, scope in and out, trade-off sliders, constraints, "
                "people and roles, top risks, first milestones, and next steps.", "\n".join(b))


# ---------------------------------------------------------------- stakeholder map

def build_stakeholder_map():
    b = [header("Stakeholder Map",
                "See who affects or is affected by the work, how much they care, and how you'll keep each of them involved.",
                "Run a Project · Influence vs. Interest · Engagement · Communication Plan",
                legend([("sticky", YELLOW, "Yellow Sticky = Stakeholder"), ("sticky", PINK_ST, "Pink Sticky = Concern / Blocker")]))]

    x, y, w, h = 24, 148, 900, 620
    b.append(panel(x, y, w, h, 1, "Influence vs. Interest", BLUE, "ONE STICKY PER PERSON OR GROUP"))
    b.append(quad_grid(x + 54, y + 70, x + w - 18, y + h - 52,
                       [("Keep Satisfied", "High influence · low interest · consult on what matters to them", AMBER),
                        ("Manage Closely", "High influence · high interest · involve in key decisions", RED),
                        ("Monitor", "Low influence · low interest · light-touch updates", SLATE),
                        ("Keep Informed", "Low influence · high interest · regular updates, invite feedback", EMERALD)],
                       "LOW INTEREST", "HIGH INTEREST", "INTEREST →", "INFLUENCE →"))

    x, w = 938, 718
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Stakeholder Register", PURPLE, "WHAT THEY WANT AND HOW WE ENGAGE"))
    b.append(table(x + 18, y + 84, [("Stakeholder", 150), ("Wants / worries", 230), ("How & how often", 190),
                                    ("Owner", w - 36 - 570)], 14, d, 36))

    y, h = 782, 278
    x, w = 24, 1082
    d = SKY[0]
    b.append(panel(x, y, w, h, 3, "Communication Plan", SKY, "RIGHT MESSAGE · RIGHT PEOPLE · RIGHT RHYTHM"))
    b.append(table(x + 18, y + 84, [("Audience", 210), ("What they need", 300), ("Format", 190), ("Frequency", 170),
                                    ("Owner", w - 36 - 870)], 5, d, 34))

    x, w = 1120, 536
    d = RED[0]
    b.append(panel(x, y, w, h, 4, "Watch-outs", RED))
    b.append(bullets(x + 22, y + 74, ["Who could block this, and why?", "Who is missing from the map?"], d))
    b.append(dashed(x + 10, x + w - 10, y + 110, d))
    b.append(sticky_zone(x + 10, y + 116, w - 20, h - 128, d, chips=(PINK_ST,)))

    b.append(footer("Who will be affected by this, and have we asked them?",
                    "Who could stop this, and what do they need from us?", PROJECT_TAG))
    write_board("stakeholder-map-board", "Stakeholder Map",
                "A3 landscape stakeholder map: influence vs. interest grid, stakeholder register, communication plan, "
                "and watch-outs.", "\n".join(b))


# ---------------------------------------------------------------- release forecast

def build_release_forecast():
    b = [header("Release Forecast & Burn-up",
                "Answer “when will it be done?” with a range, based on how fast the team actually finishes work.",
                "Run a Project · Burn-up Chart · Throughput Forecasting · Ranges, Not Single Dates",
                header_fields(["Release / scope", "Forecast date"]))]

    x, y, w, h = 24, 148, 1082, 600
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Burn-up Chart", BLUE, "PLOT AFTER EVERY ITERATION"))
    cx0, cy0, cx1, cy1 = x + 80, y + 76, x + w - 24, y + h - 72
    b.append(R(cx0, cy0, cx1 - cx0, cy1 - cy0, "white", 4, f' stroke="{RULE}"'))
    n = 12
    for i in range(1, n):
        gx = cx0 + i * (cx1 - cx0) / n
        b.append(L(gx, cy0, gx, cy1, RULE, 1))
    for j in range(1, 8):
        gy = cy0 + j * (cy1 - cy0) / 8
        b.append(L(cx0, gy, cx1, gy, RULE, 1))
        b.append(L(cx0 - 40, gy, cx0 - 8, gy, WRITE, 1))
    for i in range(n):
        b.append(T(cx0 + (i + 0.5) * (cx1 - cx0) / n, cy1 + 18, str(i + 1), 10, MUTED, MONO, anchor="middle"))
    b.append(L(cx0, cy1, cx1, cy1, INK, 1.5))
    b.append(L(cx0, cy0, cx0, cy1, INK, 1.5))
    b.append(T((cx0 + cx1) / 2, cy1 + 36, "ITERATION →", 9, INK, MONO, weight=600, anchor="middle", ls=".12em"))
    b.append(rot_label(x + 22, (cy0 + cy1) / 2, "WORK DONE (ITEMS) →"))
    ly = y + h - 18
    for i, (lab, col, dash) in enumerate([("Total scope", PURPLE[0], ' stroke-dasharray="7,4"'), ("Done", EMERALD[0], ""),
                                          ("Forecast range (fast / slow)", AMBER[0], ' stroke-dasharray="2,4"')]):
        lx = cx0 + i * 240
        b.append(L(lx, ly - 4, lx + 34, ly - 4, col, 2.5, dash))
        b.append(T(lx + 42, ly, lab, 10.5, INK))

    x, w = 1120, 536
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 2, "Throughput Data", EMERALD, "ITEMS FINISHED PER ITERATION"))
    b.append(table(x + 18, y + 84, [("Iteration", 110), ("Done", 110), ("Added", 110), ("Total scope", w - 36 - 330)], 10, d, 34))
    for i, f in enumerate(["Average per iteration:", "Slowest 3, average:", "Fastest 3, average:"]):
        b.append(field(x + 18, y + 470 + i * 36, f, x + w - 18, d))

    y, h = 762, 298
    x, w = 24, 808
    d = AMBER[0]
    b.append(panel(x, y, w, h, 3, "The Forecast", AMBER, "REMAINING / RATE = ITERATIONS LEFT"))
    b.append(field(x + 18, y + 88, "Remaining items (incl. expected growth):", x + 420, d))
    b.append(table(x + 18, y + 136, [("Scenario", 160), ("Rate / iteration", 180), ("Iterations left", 180),
                                     ("Date", w - 36 - 520)], 3, d, 36))
    for i, s in enumerate(["Slow", "Likely", "Fast"]):
        b.append(T(x + 24, y + 136 + 36 * (i + 1) - 2, s, 11, d, weight=600))

    x, w = 846, 810
    d = RED[0]
    b.append(panel(x, y, w, h, 4, "What Would Change It", RED, "UPDATE THE FORECAST WHEN THESE MOVE"))
    b.append(bullets(x + 22, y + 74, ["Scope growth · team changes · dependencies · item size changing",
                                      "Share the range and the assumptions, not just the likely date"], d))
    b.append(dashed(x + 10, x + w - 10, y + 110, d))
    b.append(sticky_zone(x + 10, y + 116, w - 20, h - 172, d, chips=(YELLOW, PINK_ST)))
    b.append(field(x + 18, y + h - 22, "Next forecast update:", x + w - 18, d))

    b.append(footer("When will it be done? Here's the range, and here's what it depends on.",
                    "What would have to be true for the fast forecast to happen?", PROJECT_TAG))
    write_board("release-forecast-board", "Release Forecast & Burn-up",
                "A3 landscape release forecast board: burn-up chart grid, throughput data table, slow / likely / fast "
                "forecast, and the factors that would change it.", "\n".join(b))


# ---------------------------------------------------------------- RAID log

def build_raid_log():
    b = [header("RAID Log",
                "Keep the project's risks, assumptions, issues and dependencies visible, owned and reviewed.",
                "Run a Project · Risks · Assumptions · Issues · Dependencies · Review Every Iteration",
                header_fields(["Project", "Last reviewed"]))]
    w, h = 808, 449
    blocks = [
        (24, 148, "R", "Risks", RED, "MIGHT HAPPEN · RESPONSE: AVOID · REDUCE · TRANSFER · ACCEPT",
         [("Risk", 250), ("Likelihood", 92), ("Impact", 80), ("Response", 216), ("Owner", w - 36 - 638)]),
        (846, 148, "A", "Assumptions", AMBER, "BELIEVED TRUE · NOT YET PROVEN",
         [("Assumption", 300), ("How we'll test it", 250), ("By when", 88), ("Owner", w - 36 - 638)]),
        (24, 611, "I", "Issues", ORANGE, "HAPPENING NOW",
         [("Issue", 250), ("Impact", 150), ("Action", 196), ("Owner", 80), ("Due", w - 36 - 676)]),
        (846, 611, "D", "Dependencies", BLUE, "WE NEED FROM OTHERS · OTHERS NEED FROM US",
         [("Dependency", 240), ("From → to", 150), ("Needed by", 100), ("Status", 100), ("Owner", w - 36 - 590)]),
    ]
    for x, y, letter, title, color, note, cols in blocks:
        b.append(panel(x, y, w, h, letter, title, color, note))
        b.append(table(x + 18, y + 84, cols, 10, color[0], 34))

    b.append(footer("What's the risk we're not talking about?",
                    "Which assumption, if wrong, would hurt us most?", PROJECT_TAG))
    write_board("raid-log-board", "RAID Log",
                "A3 landscape RAID log: tables for risks, assumptions, issues and dependencies, each with an owner.",
                "\n".join(b))


# ---------------------------------------------------------------- cross-team planning

def build_cross_team_planning():
    b = [header("Cross-Team Planning",
                "Plan a period of work across several teams: shared objectives, each team's plan, milestones and risks.",
                "Coordinate Teams · Big-Room Planning (SAFe: PI Planning) · Shared Objectives · Team Plans",
                header_fields(["Group", "Planning period"]))]

    y, h = 148, 236
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Shared Objectives", PURPLE, "WHAT WE'LL ACHIEVE TOGETHER"))
    b.append(table(x + 18, y + 84, [("Objective", 420), ("Value (1–10)", 120), ("Teams", w - 36 - 540)], 4, d, 34))

    x, w = 846, 810
    d = SLATE[0]
    b.append(panel(x, y, w, h, 2, "Context & Constraints", SLATE))
    for i, f in enumerate(["Product vision / goal:", "Fixed dates & events:", "Capacity changes (holidays, hiring):",
                           "Platform or architecture changes:"]):
        b.append(field(x + 18, y + 90 + i * 36, f, x + w - 18, d))

    # 3 team plans grid
    x, y, w, h = 24, 398, 1632, 500
    d = BLUE[0]
    b.append(panel(x, y, w, h, 3, "Team Plans", BLUE, "ONE ROW PER TEAM · STICKIES IN THE ITERATION THEY'LL BE DONE"))
    gx0, gy0 = x + 14, y + 64
    label_w, risk_w = 170, 230
    it_w = (w - 28 - label_w - risk_w) / 5
    heads = [f"ITERATION {i + 1}" for i in range(5)]
    for i, hd in enumerate(heads):
        cx = gx0 + label_w + i * it_w
        b.append(T(cx + 10, gy0 + 14, hd, 9, d, MONO, weight=600, ls=".12em"))
        b.append(L(cx + 10, gy0 + 30, cx + it_w - 10, gy0 + 30, WRITE, 1))
    b.append(T(gx0 + label_w + 5 * it_w + 10, gy0 + 14, "RISKS & NEEDS", 9, RED[0], MONO, weight=600, ls=".12em"))
    rows = ["Milestones"] + [f"Team {i}" for i in range(1, 6)]
    rh = (h - 64 - 44 - 12) / 6
    for r, name in enumerate(rows):
        ry = gy0 + 44 + r * rh
        is_ms = r == 0
        b.append(R(gx0, ry, label_w - 8, rh - 6, "white" if not is_ms else AMBER[1], 6,
                   f' stroke="{d}" stroke-opacity=".15"'))
        b.append(T(gx0 + 12, ry + 22, name, 12, AMBER[0] if is_ms else d, weight=600))
        if not is_ms:
            b.append(L(gx0 + 12, ry + rh - 18, gx0 + label_w - 20, ry + rh - 18, WRITE, 1))
        for i in range(5):
            cx = gx0 + label_w + i * it_w
            if is_ms:
                mx = cx + it_w / 2
                b.append(f'<path d="M{mx:g},{ry + 8:g} l9,9 -9,9 -9,-9 z" fill="none" stroke="{AMBER[0]}" stroke-opacity=".5" stroke-width="1.5"/>')
            else:
                b.append(R(cx + 4, ry, it_w - 8, rh - 6, "url(#dots)", 4,))
                b.append(R(cx + 4, ry, it_w - 8, rh - 6, "white", 4, f' fill-opacity=".45" stroke="{d}" stroke-opacity=".12"'))
        rx = gx0 + label_w + 5 * it_w
        b.append(R(rx + 4, ry, risk_w - 4, rh - 6, RED[1], 4, f' stroke="{RED[0]}" stroke-opacity=".15"'))

    y, h = 912, 148
    x, w = 24, 534
    d = FOREST[0]
    b.append(panel(x, y, w, h, 4, "Confidence Vote", FOREST, "FIST OF FIVE"))
    for i in range(5):
        cx = x + 60 + i * 100
        b.append(f'<circle cx="{cx}" cy="{y + 94}" r="16" fill="white" stroke="{d}" stroke-opacity=".5" stroke-width="1.5"/>')
        b.append(T(cx, y + 100, str(i + 1), 13, d, weight=600, anchor="middle"))
    b.append(T(x + 18, y + 134, "Anyone at 1–2? Explore, adjust the plan, re-vote.", 10, d, italic=True, op=".88"))

    x = 572
    d = RED[0]
    b.append(panel(x, y, w, h, 5, "Risks to the Plan", RED))
    b.append(lines(x + 18, y + 86, x + w - 18, 3, 24))

    x, w = 1120, 536
    d = SKY[0]
    b.append(panel(x, y, w, h, 6, "Capacity Split", SKY, "AGREE IT UP FRONT"))
    for i, f in enumerate(["Features %:", "Tech debt & enablers %:", "Unplanned buffer %:"]):
        b.append(field(x + 18, y + 84 + i * 26, f, x + w - 18, d))

    b.append(footer("What will we achieve together that no team could achieve alone?",
                    "Which dependency, if it slips, takes the plan with it?", PROGRAM_TAG))
    write_board("cross-team-planning-board", "Cross-Team Planning",
                "A3 landscape cross-team planning board: shared objectives, context and constraints, a team-by-iteration "
                "plan with milestones and risks, a confidence vote, risks to the plan, and the capacity split.", "\n".join(b))


# ---------------------------------------------------------------- dependency map

def build_dependency_map():
    b = [header("Dependency Map",
                "Make cross-team dependencies visible: who needs what from whom, by when, and which ones are at risk.",
                "Coordinate Teams · Dependency Board · Red String · Reduce, Don't Just Manage",
                legend([("sticky", YELLOW, "Yellow = Work item"), ("sticky", BLUE_ST, "Blue = Dependency"),
                        ("sticky", PINK_ST, "Pink = At risk"), ("dot", RED[0], "Red string = link")]))]

    x, y, w, h = 24, 148, 1632, 600
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Dependency Board", BLUE, "PLACE THE ITEM WHERE IT'S NEEDED · LINK IT TO WHO PROVIDES IT"))
    gx0, gy0 = x + 14, y + 64
    label_w = 170
    cols = [f"ITERATION {i + 1}" for i in range(5)] + ["LATER"]
    it_w = (w - 28 - label_w) / len(cols)
    for i, hd in enumerate(cols):
        cx = gx0 + label_w + i * it_w
        b.append(T(cx + 10, gy0 + 14, hd, 9, d, MONO, weight=600, ls=".12em"))
    rows = [f"Team {i}" for i in range(1, 7)]
    rh = (h - 64 - 28 - 12) / len(rows)
    for r, name in enumerate(rows):
        ry = gy0 + 28 + r * rh
        b.append(R(gx0, ry, label_w - 8, rh - 6, "white", 6, f' stroke="{d}" stroke-opacity=".15"'))
        b.append(T(gx0 + 12, ry + 22, name, 12, d, weight=600))
        b.append(L(gx0 + 12, ry + rh - 18, gx0 + label_w - 20, ry + rh - 18, WRITE, 1))
        for i in range(len(cols)):
            cx = gx0 + label_w + i * it_w
            b.append(R(cx + 4, ry, it_w - 8, rh - 6, "url(#dots)", 4))
            b.append(R(cx + 4, ry, it_w - 8, rh - 6, "white", 4, f' fill-opacity=".45" stroke="{d}" stroke-opacity=".12"'))

    y, h = 762, 298
    x, w = 24, 1082
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Dependency Register", PURPLE, "ONE ROW PER DEPENDENCY"))
    b.append(table(x + 18, y + 84, [("#", 40), ("Needed by", 150), ("Provided by", 150), ("What", 330), ("By when", 120),
                                    ("Status", 130), ("Owner", w - 36 - 920)], 5, d, 34))
    b.append(T(x + 18, y + h - 16, "Status: agreed · at risk · blocked · done", 9, d, MONO, op=".88", ls=".08em"))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 3, "Reduce Dependencies", FOREST, "BEST DEPENDENCY = NO DEPENDENCY"))
    for i, m in enumerate(["Could the team do it themselves (skills, access)?", "Could we re-order the work so it's needed later?",
                           "Could a stub, mock or contract unblock us?", "Does it keep happening? Change team boundaries"]):
        b.append(checkbox(x + 18, y + 86 + i * 30, m, d, 11))
    b.append(field(x + 18, y + 230, "Top dependency to remove:", x + w - 18, d))
    b.append(field(x + 18, y + 264, "Owner:", x + w - 18, d))

    b.append(footer("Who are we waiting on, and do they know?",
                    "Which dependency could we remove instead of managing?", PROGRAM_TAG))
    write_board("dependency-map-board", "Dependency Map",
                "A3 landscape dependency map: a team-by-iteration dependency board, a dependency register, and ways to "
                "reduce dependencies.", "\n".join(b))


# ---------------------------------------------------------------- OKRs

def build_okr():
    b = [header("Objectives & Key Results",
                "Agree a few ambitious outcomes, how you'll measure them, and the bets teams will make to move them.",
                "Coordinate Teams · OKRs · Outcomes Over Output · Confidence Check-ins",
                header_fields(["Group / team", "Period"]))]

    x, y, w, h = 24, 148, 1632, 120
    d = SLATE[0]
    b.append(panel(x, y, w, h, None, "Focus for This Period", SLATE, "WHY THESE OBJECTIVES, AND WHY NOW?"))
    b.append(L(x + 18, y + 92, x + w - 18, y + 92, WRITE))

    y, h, w = 282, 600, 534
    for i, color in enumerate([PURPLE, BLUE, EMERALD]):
        x = 24 + i * 548
        w_ = w if i < 2 else 536
        d = color[0]
        b.append(panel(x, y, w_, h, i + 1, f"Objective {i + 1}", color, "QUALITATIVE · INSPIRING"))
        b.append(T(x + 18, y + 94, "We will…", 19, d, SERIF, italic=True))
        b.append(L(x + 110, y + 97, x + w_ - 18, y + 97, d, 1, ' stroke-opacity=".25"'))
        b.append(L(x + 18, y + 132, x + w_ - 18, y + 132, d, 1, ' stroke-opacity=".25"'))
        b.append(T(x + 18, y + 172, "KEY RESULTS · MEASURABLE OUTCOMES", 9, d, MONO, weight=600, ls=".12em"))
        b.append(table(x + 18, y + 200, [("Key result", 230), ("Start", 70), ("Target", 70), ("Conf.", w_ - 36 - 370)], 3, d, 34))
        b.append(field(x + 18, y + 342, "Teams contributing:", x + w_ - 18, d))
        b.append(T(x + 18, y + 382, "Initiatives: the bets we'll make", 11, d, weight=600))
        b.append(sticky_zone(x + 10, y + 392, w_ - 20, h - 404, d, chips=(YELLOW,)))

    y, h = 896, 164
    x, w = 24, 808
    d = AMBER[0]
    b.append(panel(x, y, w, h, 4, "Check-in Rhythm", AMBER, "CONFIDENCE 1–10 · SCORE 0–1.0 AT THE END"))
    for i, f in enumerate(["Weekly confidence check:", "Mid-period review:", "End-of-period scoring:"]):
        b.append(field(x + 18, y + 84 + i * 28, f, x + w - 18, d))

    x, w = 846, 810
    d = RED[0]
    b.append(panel(x, y, w, h, 5, "Not Doing This Period", RED, "FOCUS MEANS SAYING NO"))
    b.append(lines(x + 18, y + 90, x + w - 18, 3, 26))

    b.append(footer("If we achieved only one of these, which would matter most?",
                    "How will we know, without asking anyone, that we've succeeded?", PROGRAM_TAG))
    write_board("okr-board", "Objectives & Key Results",
                "A3 landscape OKR board: focus statement, three objectives each with key results, confidence and "
                "initiatives, a check-in rhythm, and a not-doing list.", "\n".join(b))


# ---------------------------------------------------------------- cross-team sync

def build_cross_team_sync():
    b = [header("Cross-Team Sync",
                "A short, regular check across teams: progress toward shared objectives, dependencies, and what's blocking whom.",
                "Coordinate Teams · Scrum of Scrums · Cross-Team Impediments · 15–30 Minutes",
                header_fields(["Group", "Date"]))]

    x, y, w, h = 24, 148, 1632, 460
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Team Updates", BLUE, "ONE PERSON PER TEAM · ABOUT 2 MINUTES EACH"))
    b.append(table(x + 18, y + 84, [("Team", 150), ("Progress toward shared objectives", 380), ("Next up", 280),
                                    ("Blocked by / needs", 300), ("Dependencies at risk", 300),
                                    ("Conf. 1–5", w - 36 - 1410)], 6, d, 58))

    x, y, w, h = 24, 622, 1082, 438
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 2, "Cross-Team Impediments", ORANGE, "PROBLEMS NO SINGLE TEAM CAN SOLVE"))
    b.append(kanban_cols(x + 10, y + 64, w - 20, h - 76,
                         [("New", "Raised today"), ("Being worked", "Has an owner and a next step"),
                          ("Resolved", "Say what fixed it")], d))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 3, "Decisions & Actions", FOREST))
    b.append(table(x + 18, y + 84, [("Decision / action", 290), ("Owner", 110), ("Due", w - 36 - 400)], 9, d, 34))

    b.append(footer("What's blocking another team that we could help with today?",
                    "Are we still on track for the shared objectives?", PROGRAM_TAG))
    write_board("cross-team-sync-board", "Cross-Team Sync",
                "A3 landscape cross-team sync board: team updates table, cross-team impediments (new, being worked, "
                "resolved), and decisions and actions.", "\n".join(b))


# ---------------------------------------------------------------- flow pack

FLOW_TAG = "Manage Flow · Stop Starting, Start Finishing"


def step_cards(x, y, w, h, steps, color, gap=10):
    """Numbered horizontal cards: steps = (title, [lines])."""
    dark = color[0]
    cw = (w - (len(steps) - 1) * gap) / len(steps)
    out = []
    for i, (title, body) in enumerate(steps):
        cx = x + i * (cw + gap)
        out.append(R(cx, y, cw, h, "white", 6, f' stroke="{dark}" stroke-opacity=".2"'))
        out.append(f'<circle cx="{cx + 22:g}" cy="{y + 24}" r="11" fill="{dark}"/>')
        out.append(T(cx + 22, y + 28, str(i + 1), 10.5, "white", weight=600, anchor="middle"))
        out.append(T(cx + 40, y + 29, title, 12, dark, weight=600))
        out.append(para(cx + 14, y + 56, body, 10.5, dark, 15))
        out.append(T(cx + 14, y + h - 74, "Our note:", 9.5, dark, op=".88"))
        out.append(lines(cx + 14, y + h - 46, cx + cw - 14, 2, 24))
        if i < len(steps) - 1:
            out.append(T(cx + cw + gap / 2, y + h / 2 + 4, "›", 14, dark, anchor="middle", op=".5"))
    return "".join(out)


def rule_line(x, y, before, after, x_end, color, size=11):
    """Checkbox, text, a short blank, then more text: 'blocked for more than ___ hours'."""
    out = [R(x, y - 10, 12, 12, "white", 2, f' stroke="{color}" stroke-opacity=".6" stroke-width="1.2"'),
           T(x + 20, y, before, size, color)]
    bx = x + 20 + text_w(before, size) + 6
    out.append(L(bx, y + 3, bx + 50, y + 3, color, 1, ' stroke-opacity=".4"'))
    if after:
        out.append(T(bx + 56, y, after, size, color))
    return "".join(out)


# ---------------------------------------------------------------- buffering & swarming

def build_buffering_swarming():
    b = [header("Buffering & Swarming",
                "Protect capacity for the unexpected, and agree when the team stops starting and gathers to finish.",
                "Manage Flow · Capacity Buffer · Swarm Triggers · Stop Starting, Start Finishing",
                header_fields(["Team", "Date"]))]

    y, h = 148, 300
    x, w = 24, 808
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Unplanned Work History", BLUE, "HOW MUCH SURPRISE WORK DO WE REALLY GET?"))
    b.append(table(x + 18, y + 84, [("Iteration", 120), ("Planned capacity", 170), ("Unplanned work", 170), ("% unplanned", 120),
                                    ("Notes", w - 36 - 580)], 5, d, 34))
    b.append(field(x + 18, y + 278, "Average % unplanned over the last 5:", x + 420, d))

    x, w = 846, 397
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 2, "Size the Buffer", EMERALD))
    for i, f in enumerate(["Buffer this iteration (%):", "In days or items:"]):
        b.append(field(x + 18, y + 88 + i * 32, f, x + w - 18, d))
    b.append(T(x + 18, y + 172, "The buffer is for:", 11, d, weight=600))
    for i, m in enumerate(["Support, incidents & bugs", "Urgent requests", "Swarming & helping others", "Improvement work, if unused"]):
        b.append(checkbox(x + 18, y + 200 + i * 26, m, d, 11))

    x = 1257
    d = SLATE[0]
    b.append(panel(x, y, w, h, 3, "Buffer Rules", SLATE))
    for i, f in enumerate(["What counts as unplanned?", "Who decides to use it?", "If it runs out, we…", "If it's unused, we…"]):
        b.append(T(x + 18, y + 84 + i * 54, f, 11, d, weight=600))
        b.append(L(x + 18, y + 106 + i * 54, x + w - 18, y + 106 + i * 54, WRITE))

    y, h = 462, 300
    x, w = 24, 808
    d = RED[0]
    b.append(panel(x, y, w, h, 4, "Swarm Triggers", RED, "WHEN WE STOP STARTING AND SWARM"))
    rules = [("An item is blocked for more than", "hours"), ("An item is older than", "days (our 85% SLE)"),
             ("An item the goal depends on is at risk with", "days left"), ("A production incident at severity", "or higher"),
             ("A column is at its WIP limit", "")]
    for i, (a, c) in enumerate(rules):
        b.append(rule_line(x + 18, y + 90 + i * 34, a, c, x + w - 18, d))
    b.append(field(x + 18, y + 268, "Our own trigger:", x + w - 18, d))

    x, w = 846, 810
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 5, "How We Swarm", ORANGE, "AGREE IT BEFORE YOU NEED IT"))
    b.append(step_cards(x + 14, y + 66, w - 28, h - 80, [
        ("Stop", ["Don't start anything", "new. Say “swarm”", "at the board."]),
        ("Gather", ["Whoever can help joins.", "Not everyone needs", "to, just enough."]),
        ("Plan", ["What's the next step", "to finish it? Who", "does which part?"]),
        ("Work it", ["Pair or mob. Test", "while building.", "Clear the blocker."]),
        ("Reflect", ["Done? Log it below.", "Why did it need a", "swarm at all?"])], ORANGE))

    y, h = 776, 284
    x, w = 24, 1082
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 6, "Swarm Log", PURPLE, "LEARN FROM EVERY SWARM"))
    b.append(table(x + 18, y + 84, [("Date", 90), ("Item", 220), ("Trigger", 170), ("Who swarmed", 170), ("Time to done", 120),
                                    ("What we learned", w - 36 - 770)], 5, d, 34))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 7, "Iteration Check", FOREST, "AT THE RETRO"))
    for i, f in enumerate(["Buffer used last iteration (%):", "Number of swarms:"]):
        b.append(field(x + 18, y + 88 + i * 34, f, x + w - 18, d))
    b.append(T(x + 18, y + 170, "Did swarming finish things faster?", 11, d, weight=600))
    for j, lab in enumerate(["Yes", "Partly", "No"]):
        b.append(checkbox(x + 18 + j * 90, y + 198, lab, d, 11))
    b.append(field(x + 18, y + 244, "Next iteration's buffer (%):", x + w - 18, d))

    b.append(footer("What would we stop starting so we could finish this?",
                    "How much of our plan is really for surprises?", FLOW_TAG))
    write_board("buffering-swarming-board", "Buffering & Swarming",
                "A3 landscape board: unplanned work history, buffer sizing and rules, swarm triggers, a five-step swarm "
                "routine, a swarm log, and an iteration check.", "\n".join(b))


# ---------------------------------------------------------------- kanban board design

def build_kanban_design():
    b = [header("Kanban Board Design",
                "Design a board that shows how work really flows: columns, WIP limits, exit policies and classes of service.",
                "Manage Flow · Visualise the Workflow · Limit WIP · Make Policies Explicit",
                header_fields(["Team", "Date"]))]

    x, y, w, h = 24, 148, 1632, 380
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Workflow Columns", BLUE, "LEFT TO RIGHT · ONE COLUMN PER REAL STATE OR QUEUE"))
    n = 7
    cw = (w - 28 - (n - 1) * 10) / n
    hints = ["e.g. Options", "e.g. Ready", "e.g. Building", "e.g. Waiting for review", "e.g. Testing", "e.g. Ready to release", "Done"]
    for i in range(n):
        cx = x + 14 + i * (cw + 10)
        b.append(R(cx, y + 64, cw, h - 78, "white", 6, f' stroke="{d}" stroke-opacity=".2"'))
        b.append(T(cx + 12, y + 86, f"COLUMN {i + 1}", 9, d, MONO, weight=600, ls=".12em"))
        b.append(T(cx + cw - 12, y + 86, hints[i], 9, d, italic=True, anchor="end", op=".88"))
        b.append(field(cx + 12, y + 120, "Name:", cx + cw - 12, d))
        b.append(field(cx + 12, y + 154, "WIP limit:", cx + cw - 12, d))
        b.append(T(cx + 12, y + 190, "Done when (exit policy):", 10.5, d, weight=600))
        b.append(lines(cx + 12, y + 218, cx + cw - 12, 3, 26))
        b.append(checkbox(cx + 12, y + 316, "Active", d, 10.5))
        b.append(checkbox(cx + 88, y + 316, "Queue", d, 10.5))

    y, h = 542, 300
    x, w = 24, 1082
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Classes of Service", PURPLE, "HOW WE TREAT DIFFERENT KINDS OF WORK"))
    cols = [("Class", 150), ("When to use it", 300), ("Our policy", 440), ("Limit", w - 36 - 890)]
    b.append(table(x + 18, y + 84, cols, 4, d, 46))
    for i, (cls, hint) in enumerate([("Expedite", "Urgent, high cost of delay now"), ("Fixed date", "Value drops after a date"),
                                     ("Standard", "Most work, in priority order"), ("Intangible", "Improvement, tech debt")]):
        ry = y + 84 + 10 + i * 46 + 28
        b.append(T(x + 24, ry, cls, 12, d, weight=600))
        b.append(T(x + 24 + 150, ry, hint, 10.5, d, italic=True, op=".88"))

    x, w = 1120, 536
    d = SLATE[0]
    b.append(panel(x, y, w, h, 3, "Board Policies", SLATE, "WRITE THEM ON THE BOARD"))
    for i, f in enumerate(["We pull work when:", "Blocked items are marked by:", "Replenishment: when & who:",
                           "We walk the board at:", "Definition of Done lives at:", "Policies reviewed every:"]):
        b.append(field(x + 18, y + 88 + i * 34, f, x + w - 18, d))

    y, h = 856, 204
    x, w = 24, 808
    d = SKY[0]
    b.append(panel(x, y, w, h, 4, "Cards & Swimlanes", SKY))
    b.append(T(x + 18, y + 82, "Each card shows:", 11, d, weight=600))
    for j, lab in enumerate(["Title", "Owner", "Age (days)", "Blocked flag", "Class of service", "Due date"]):
        b.append(checkbox(x + 18 + (j % 3) * 200, y + 110 + (j // 3) * 28, lab, d, 11))
    b.append(field(x + 18, y + 184, "Swimlanes (if any):", x + w - 18, d))

    x, w = 846, 810
    d = FOREST[0]
    b.append(panel(x, y, w, h, 5, "Flow Metrics to Watch", FOREST, "LEARN, DON'T JUDGE"))
    for j, (lab, note) in enumerate([("WIP", "items in progress"), ("Throughput", "items done per week"),
                                     ("Cycle time", "start to done, in days"), ("Work item age", "how long open items have run"),
                                     ("Blocked time", "days items spend blocked"), ("Flow efficiency", "active time / total time")]):
        cx = x + 18 + (j % 2) * 390
        cy = y + 86 + (j // 2) * 32
        b.append(checkbox(cx, cy, lab, d, 11))
        b.append(T(cx + 130, cy, note, 10.5, d, italic=True, op=".88"))

    b.append(footer("Where does work wait, and is that visible on our board?",
                    "What would happen if we lowered this WIP limit by one?", FLOW_TAG))
    write_board("kanban-board-design", "Kanban Board Design",
                "A3 landscape board: seven workflow columns each with name, WIP limit, exit policy and active/queue type, "
                "classes of service, board policies, card and swimlane design, and flow metrics.", "\n".join(b))


# ---------------------------------------------------------------- ageing WIP & SLE

def build_ageing_wip():
    b = [header("Ageing WIP & Service Level Expectation",
                "See how old each open item is compared with how long work usually takes, and act before it's late.",
                "Manage Flow · Work Item Age · Cycle Time Percentiles · Service Level Expectation",
                header_fields(["Team", "Date"]))]

    x, y, w, h = 24, 148, 1082, 600
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Ageing WIP Chart", BLUE, "ONE DOT PER OPEN ITEM, IN ITS CURRENT COLUMN"))
    cx0, cy0, cx1, cy1 = x + 80, y + 76, x + w - 24, y + h - 80
    b.append(R(cx0, cy0, cx1 - cx0, cy1 - cy0, "white", 4, f' stroke="{RULE}"'))
    ncol = 5
    for i in range(1, ncol):
        gx = cx0 + i * (cx1 - cx0) / ncol
        b.append(L(gx, cy0, gx, cy1, RULE, 1))
    for j in range(1, 10):
        gy = cy0 + j * (cy1 - cy0) / 10
        b.append(L(cx0, gy, cx1, gy, RULE, 1, ' stroke-dasharray="2,4"'))
        b.append(L(cx0 - 36, gy, cx0 - 8, gy, WRITE, 1))
    for i in range(ncol):
        mx = cx0 + (i + 0.5) * (cx1 - cx0) / ncol
        colw = (cx1 - cx0) / ncol
        b.append(L(mx - colw / 2 + 14, cy1 + 24, mx + colw / 2 - 14, cy1 + 24, WRITE, 1))
    b.append(T(cx0, cy1 + 44, "COLUMN NAMES ↑ · IN-PROGRESS COLUMNS ONLY, LEFT TO RIGHT", 9, MUTED, MONO, ls=".1em"))
    b.append(L(cx0, cy1, cx1, cy1, INK, 1.5))
    b.append(L(cx0, cy0, cx0, cy1, INK, 1.5))
    b.append(rot_label(x + 22, (cy0 + cy1) / 2, "AGE IN DAYS →"))
    for i, (lab, col) in enumerate([("50th percentile", EMERALD[0]), ("70th", AMBER[0]), ("85th = SLE", RED[0])]):
        lx = cx0 + i * 200
        b.append(L(lx, y + h - 22, lx + 34, y + h - 22, col, 2.5, ' stroke-dasharray="8,4"'))
        b.append(T(lx + 42, y + h - 18, lab, 10.5, INK))
    b.append(T(cx1, y + h - 18, "Draw each percentile as a line across the chart", 10, MUTED, italic=True, anchor="end"))

    x, w = 1120, 536
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 2, "Cycle Time Data", EMERALD, "RECENTLY FINISHED ITEMS"))
    b.append(table(x + 18, y + 84, [("Item", 200), ("Started", 90), ("Finished", 90), ("Days", w - 36 - 380)], 11, d, 34))
    for i, f in enumerate(["50th percentile (days):", "70th percentile (days):", "85th percentile (days):"]):
        b.append(field(x + 18, y + 500 + i * 30, f, x + w - 18, d))

    y, h = 762, 298
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 3, "Our Service Level Expectation", PURPLE, "A FORECAST FOR ONE ITEM, NOT A TARGET"))
    b.append(T(x + 18, y + 104, "85% of our items finish within", 22, d, SERIF, italic=True))
    b.append(L(x + 262, y + 107, x + 342, y + 107, d, 1.2, ' stroke-opacity=".4"'))
    b.append(T(x + 352, y + 104, "days.", 22, d, SERIF, italic=True))
    for i, f in enumerate(["Based on how many items, from when to when:", "The clock starts when:", "The clock stops when:"]):
        b.append(field(x + 18, y + 160 + i * 38, f, x + w - 18, d))

    x, w = 846, 810
    d = RED[0]
    b.append(panel(x, y, w, h, 4, "Act on Ageing Items", RED, "LOOK AT THE OLDEST ITEMS FIRST, EVERY DAY"))
    for i, (lab, act, col) in enumerate([("Past the 50th", "Mention it at the daily sync", EMERALD[0]),
                                         ("Past the 70th", "Ask what's needed to finish it", AMBER[0]),
                                         ("Past the 85th", "Swarm it (see Buffering & Swarming)", RED[0])]):
        cy = y + 88 + i * 30
        b.append(R(x + 18, cy - 10, 12, 12, col, 2))
        b.append(T(x + 40, cy, lab, 11, col, weight=600))
        b.append(T(x + 160, cy, act, 11, d))
    b.append(T(x + 18, y + 184, "Items to act on today:", 11, d, weight=600))
    b.append(sticky_zone(x + 10, y + 194, w - 20, h - 206, d, "Sticky per item", chips=(PINK_ST,)))

    b.append(footer("Which item is oldest, and what would it take to finish it today?",
                    "How long does work usually take here, really?", FLOW_TAG))
    write_board("ageing-wip-board", "Ageing WIP & Service Level Expectation",
                "A3 landscape board: ageing WIP chart by column, cycle time data with percentiles, the team's service "
                "level expectation, and actions for ageing items.", "\n".join(b))


# ---------------------------------------------------------------- blocker clustering

def build_blocker_clustering():
    b = [header("Blocker Clustering",
                "Log every blocker, cluster them by cause, and fix the cluster that costs the most days.",
                "Manage Flow · Inspired by Klaus Leopold & Troy Magennis · Blocked Time · Root Causes",
                legend([("sticky", PINK_ST, "Pink Sticky = One blocker"), ("sticky", YELLOW, "Yellow Sticky = Cluster name")]))]

    y, h = 148, 420
    x, w = 24, 1082
    d = RED[0]
    b.append(panel(x, y, w, h, 1, "Blocker Log", RED, "ONE ROW PER BLOCKER · CAUSE, NOT PERSON"))
    b.append(table(x + 18, y + 84, [("Date", 90), ("Item", 220), ("Blocked by (what)", 340), ("Inside / outside team", 170),
                                    ("Days blocked", w - 36 - 820)], 9, d, 34))

    x, w = 1120, 536
    d = SLATE[0]
    b.append(panel(x, y, w, h, 2, "Blocker Stickies", SLATE, "KEEP THEM AFTER THEY'RE CLEARED"))
    b.append(bullets(x + 22, y + 74, ["A pink sticky on the card the moment it's blocked",
                                      "Write the cause and the start date",
                                      "When it's cleared, add the days and move it here"], SLATE[0]))
    b.append(dashed(x + 10, x + w - 10, y + 128, d))
    b.append(sticky_zone(x + 10, y + 134, w - 20, h - 146, d, "Cleared blocker stickies", chips=(PINK_ST,)))

    x, y, w, h = 24, 582, 1632, 300
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 3, "Clusters", ORANGE, "GROUP SIMILAR CAUSES · NAME EACH CLUSTER"))
    n = 5
    cw = (w - 28 - (n - 1) * 10) / n
    for i in range(n):
        cx = x + 14 + i * (cw + 10)
        b.append(R(cx, y + 64, cw, h - 78, "white", 6, f' fill-opacity=".5" stroke="{d}" stroke-opacity=".2"'))
        b.append(field(cx + 12, y + 92, "Cluster:", cx + cw - 12, d))
        b.append(sticky_zone(cx + 6, y + 104, cw - 12, h - 160, d, "Pink stickies", chips=(PINK_ST,)))
        b.append(field(cx + 12, y + h - 30, "Count:", cx + cw / 2 - 6, d))
        b.append(field(cx + cw / 2 + 4, y + h - 30, "Days:", cx + cw - 12, d))

    y, h = 896, 164
    x, w = 24, 1082
    d = FOREST[0]
    b.append(panel(x, y, w, h, 4, "Fix the Biggest Cluster", FOREST, "BY TOTAL DAYS BLOCKED, NOT COUNT"))
    hw = (w - 54) / 2
    for i, f in enumerate(["Biggest cluster:", "Root cause:"]):
        b.append(field(x + 18, y + 90 + i * 36, f, x + 18 + hw, d))
    for i, f in enumerate(["Experiment to fix it:", "Owner & review date:"]):
        b.append(field(x + 36 + hw, y + 90 + i * 36, f, x + w - 18, d))

    x, w = 1120, 536
    d = BLUE[0]
    b.append(panel(x, y, w, h, 5, "Trend", BLUE, "IS IT WORKING?"))
    b.append(table(x + 18, y + 82, [("Period", 160), ("Blockers", 140), ("Days blocked", w - 36 - 300)], 2, d, 30))

    b.append(footer("What keeps blocking us, and what does it cost?",
                    "Which cluster, if we fixed it, would give us the most days back?", FLOW_TAG))
    write_board("blocker-clustering-board", "Blocker Clustering",
                "A3 landscape board: blocker log, cleared blocker stickies, five cause clusters with counts and days, "
                "an action for the biggest cluster, and a trend table.", "\n".join(b))


# ---------------------------------------------------------------- skills matrix

def build_skills_matrix():
    key = "".join([
        T(1356, 48, "LEVELS", 8, "#8291A6", MONO, ls=".14em"),
        *[T(1356 + (i % 2) * 160, 72 + (i // 2) * 28, f"{n} = {lab}", 11, "#CBD5E1")
          for i, (n, lab) in enumerate([(0, "No experience"), (1, "Learning"), (2, "Can do it alone"), (3, "Can teach it")])],
    ])
    b = [header("Skills Matrix",
                "See who can do what, where you rely on one person, and who will learn what, so the team can swarm.",
                "Manage Flow · Team Capability · T-Shaped Skills · Reduce Single Points of Failure",
                key)]

    x, y, w, h = 24, 148, 1632, 640
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Skills Matrix", BLUE, "SCORE 0–3 IN EACH CELL · SELF-ASSESSED, THEN DISCUSSED"))
    gx0, gy0 = x + 14, y + 64
    name_w, want_w, nskill = 170, 210, 10
    sk_w = (w - 28 - name_w - want_w) / nskill
    head_h = 62
    b.append(T(gx0 + 8, gy0 + 40, "TEAM MEMBER", 9, d, MONO, weight=600, ls=".12em"))
    for i in range(nskill):
        cx = gx0 + name_w + i * sk_w
        b.append(R(cx + 3, gy0, sk_w - 6, head_h - 6, "white", 4, f' stroke="{d}" stroke-opacity=".2"'))
        b.append(T(cx + 10, gy0 + 16, f"SKILL {i + 1}", 8.5, d, MONO, op=".88", ls=".1em"))
        b.append(L(cx + 10, gy0 + 42, cx + sk_w - 10, gy0 + 42, WRITE, 1))
    wx = gx0 + name_w + nskill * sk_w
    b.append(T(wx + 10, gy0 + 40, "WANTS TO LEARN", 9, EMERALD[0], MONO, weight=600, ls=".12em"))
    nrow = 8
    rh = (h - 64 - head_h - 14) / nrow
    for r in range(nrow):
        ry = gy0 + head_h + r * rh
        b.append(R(gx0, ry, name_w - 6, rh - 6, "white", 4, f' stroke="{d}" stroke-opacity=".15"'))
        b.append(L(gx0 + 10, ry + rh - 20, gx0 + name_w - 16, ry + rh - 20, WRITE, 1))
        for i in range(nskill):
            cx = gx0 + name_w + i * sk_w
            b.append(R(cx + 3, ry, sk_w - 6, rh - 6, "white", 4, f' fill-opacity=".55" stroke="{d}" stroke-opacity=".12"'))
        b.append(R(wx + 3, ry, want_w - 3, rh - 6, EMERALD[1], 4, f' stroke="{EMERALD[0]}" stroke-opacity=".15"'))

    y, h = 802, 258
    x, w = 24, 534
    d = RED[0]
    b.append(panel(x, y, w, h, 2, "Single Points of Failure", RED, "THE BUS-FACTOR CHECK"))
    b.append(T(x + 18, y + 82, "Skills where only one person is at 2 or 3:", 11, d, weight=600))
    b.append(lines(x + 18, y + 110, x + w - 18, 2, 26))
    b.append(T(x + 18, y + 172, "Skills where nobody is at 3 (no one to teach):", 11, d, weight=600))
    b.append(lines(x + 18, y + 200, x + w - 18, 2, 26))

    x = 572
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 3, "Learning Plan", EMERALD, "PAIR TO SPREAD SKILLS"))
    b.append(table(x + 18, y + 84, [("Who", 120), ("Learns", 150), ("From", 120), ("By when", w - 36 - 390)], 4, d, 34))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 4, "Ready to Swarm?", FOREST))
    for i, m in enumerate(["Every key skill has 2+ people at level 2", "Pairing time is planned each iteration",
                           "Experts have time set aside to teach", "New joiners have a learning buddy"]):
        b.append(checkbox(x + 18, y + 88 + i * 30, m, d, 11))
    b.append(field(x + 18, y + 228, "Next review of the matrix:", x + w - 18, d))

    b.append(footer("If one person was away for a month, what would stop?",
                    "What would you like to learn, and who could teach you?", FLOW_TAG))
    write_board("skills-matrix-board", "Skills Matrix",
                "A3 landscape skills matrix: team members by ten skills scored 0 to 3, wants-to-learn column, "
                "single points of failure, a learning plan, and a swarm-readiness checklist.", "\n".join(b))


# ---------------------------------------------------------------- impediments board

def build_impediments():
    b = [header("Impediments Board",
                "Make what's holding the team back visible, give each impediment an owner, and escalate it on time.",
                "Manage Flow · Team Impediments · Escalation Ladder · Show the Cost",
                legend([("sticky", PINK_ST, "Pink Sticky = Impediment"), ("sticky", GREEN, "Green Sticky = Resolution")]))]

    x, y, w, h = 24, 148, 1632, 560
    d = RED[0]
    b.append(panel(x, y, w, h, 1, "Impediments", RED, "EACH STICKY: WHAT · WHAT IT COSTS US · OWNER · DATE RAISED"))
    b.append(kanban_cols(x + 14, y + 66, w - 28, h - 80,
                         [("New", "Raised, not yet picked up"), ("Being worked", "Owner and next step agreed"),
                          ("Escalated", "Needs help from outside the team"), ("Resolved", "Add a green sticky: what fixed it")], d, 12,
                         chips=(PINK_ST,)))

    y, h = 722, 338
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Escalation Ladder", PURPLE, "MOVE UP IF NOT RESOLVED IN TIME"))
    rungs = [("1 · TEAM", "The team tries first", "Escalate after", "days"),
             ("2 · SCRUM MASTER / COACH", "Removes or chases it", "Escalate after", "days"),
             ("3 · MANAGEMENT", "Decides or funds the fix", "Escalate after", "days"),
             ("4 · LEADERSHIP", "Changes policy or structure", "Decision by", "")]
    rh, gap = 58, 8
    for k, (lev, role, after, unit) in enumerate(rungs):
        ry = y + h - 18 - (k + 1) * rh - k * gap
        rx = x + 18 + k * 48
        rw = w - 36 - k * 48
        b.append(R(rx, ry, rw, rh, "white", 6, f' stroke="{d}" stroke-opacity=".25"'))
        b.append(R(rx, ry, 5, rh, d, 3, f' fill-opacity="{.4 + k * .2:.1f}"'))
        b.append(T(rx + 18, ry + 22, lev, 9, d, MONO, weight=600, ls=".12em"))
        b.append(T(rx + 18, ry + 42, role, 10.5, d, op=".88"))
        b.append(field(rx + 250, ry + 34, "Who:", rx + rw - 230, d))
        b.append(T(rx + rw - 210, ry + 34, after, 10.5, d))
        b.append(L(rx + rw - 120, ry + 37, rx + rw - 60, ry + 37, WRITE, 1))
        if unit:
            b.append(T(rx + rw - 52, ry + 34, unit, 10.5, d))

    x, w = 846, 810
    d = FOREST[0]
    b.append(panel(x, y, w, h, 3, "Resolved Log", FOREST, "SHOW THE VALUE OF REMOVING IMPEDIMENTS"))
    b.append(table(x + 18, y + 84, [("Impediment", 230), ("What it cost us", 190), ("Resolved by", 150), ("Days open", 90),
                                    ("Lesson", w - 36 - 660)], 6, d, 36))

    b.append(footer("What's slowing us down that we've stopped noticing?",
                    "Who could remove this, and do they know it's costing us?", FLOW_TAG))
    write_board("impediments-board", "Impediments Board",
                "A3 landscape impediments board: new, being worked, escalated and resolved columns, a four-step "
                "escalation ladder with time limits, and a resolved log.", "\n".join(b))


# ---------------------------------------------------------------- pairing & mobbing

def build_pairing_mobbing():
    b = [header("Pairing & Mobbing",
                "Choose a style, rotate partners, agree how sessions run, and use pairing to spread skills across the team.",
                "Manage Flow · Pair Programming · Mob / Ensemble Programming · Pair Stair · Spread Skills",
                header_fields(["Team", "Date"]))]

    x, y, w, h = 24, 148, 1632, 300
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Styles", BLUE, "PICK ONE PER SESSION · WORKS FOR CODE, TESTS, ANALYSIS AND DESIGN"))
    styles = [("Driver / Navigator", PURPLE, ["One types (driver), one thinks ahead", "and reviews (navigator). Swap", "roles every 15–30 minutes."]),
              ("Ping-Pong", EMERALD, ["A writes a failing test, B makes", "it pass and writes the next test.", "Great with test-driven development."]),
              ("Strong-Style", ORANGE, ["“For an idea to go from your head", "into the computer, it must go", "through someone else's hands.”"]),
              ("Mob / Ensemble", SKY, ["The whole group, one keyboard.", "The driver rotates every few", "minutes. Ideal for swarming."])]
    cw = (w - 28 - 3 * 12) / 4
    for i, (name, col, body) in enumerate(styles):
        cx = x + 14 + i * (cw + 12)
        cd = col[0]
        b.append(R(cx, y + 64, cw, h - 78, "white", 6, f' stroke="{cd}" stroke-opacity=".25"'))
        b.append(R(cx, y + 64, cw, 5, cd, 3))
        b.append(T(cx + 16, y + 96, name, 14, cd, weight=600))
        b.append(para(cx + 16, y + 122, body, 10.5, cd, 16))
        b.append(field(cx + 16, y + 200, "Use it for:", cx + cw - 16, cd))
        b.append(field(cx + 16, y + 234, "Swap every:", cx + cw - 16, cd))

    y, h = 462, 400
    x, w = 24, 700
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Pair Stair", PURPLE, "TALLY EACH PAIRING · SPREAD IT OUT"))
    n = 8
    name_w = 130
    cell_w = (w - 28 - name_w) / n
    cell_h = (h - 64 - 40 - 26) / n
    gx0, gy0 = x + 14, y + 64
    for i in range(n):
        b.append(T(gx0 + name_w + i * cell_w + cell_w / 2, gy0 + 16, f"P{i + 1}", 9, d, MONO, weight=600, anchor="middle"))
    for r in range(n):
        ry = gy0 + 28 + r * cell_h
        b.append(T(gx0, ry + cell_h / 2 + 4, f"P{r + 1}", 9, d, MONO, weight=600))
        b.append(L(gx0 + 24, ry + cell_h / 2 + 6, gx0 + name_w - 10, ry + cell_h / 2 + 6, WRITE, 1))
        for c in range(n):
            cx = gx0 + name_w + c * cell_w
            if c < r:
                b.append(R(cx + 2, ry + 2, cell_w - 4, cell_h - 4, "white", 4, f' stroke="{d}" stroke-opacity=".15"'))
            elif c == r:
                b.append(R(cx + 2, ry + 2, cell_w - 4, cell_h - 4, d, 4, ' fill-opacity=".12"'))
    b.append(T(gx0, y + h - 16, "Write names on the left. Add a tally where two people pair. Empty cells = pairs to try.",
               10, d, italic=True, op=".88"))

    x, w = 738, 460
    d = SLATE[0]
    b.append(panel(x, y, w, h, 3, "Session Agreements", SLATE))
    for i, f in enumerate(["We pair or mob by default on:", "We work solo on:", "Swap roles every (min):", "Take a break every (min):",
                           "Rotate partners every:", "Setup & tools:"]):
        b.append(field(x + 18, y + 88 + i * 36, f, x + w - 18, d))
    for i, m in enumerate(["Anyone can call a break or a swap", "Navigators ask questions, not orders"]):
        b.append(checkbox(x + 18, y + 318 + i * 30, m, d, 11))

    x, w = 1212, 444
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 4, "Skills to Spread", EMERALD, "FROM THE SKILLS MATRIX"))
    b.append(table(x + 18, y + 84, [("Skill", 130), ("Learner", 95), ("Teacher", 95), ("Pair / mob", w - 36 - 320)], 8, d, 36))

    y, h = 876, 184
    x, w = 24, 808
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 5, "This Week's Pairs", ORANGE))
    b.append(table(x + 18, y + 82, [("Work item", 330), ("Who", 260), ("Style", w - 36 - 590)], 2, d, 34))

    x, w = 846, 810
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "Quick Retro", FOREST, "AFTER A SESSION OR AT THE END OF THE WEEK"))
    tw = (w - 36 - 2 * 16) / 3
    for i, q in enumerate(["What worked?", "What was hard?", "Next time we'll…"]):
        cx = x + 18 + i * (tw + 16)
        b.append(T(cx, y + 82, q, 11, d, weight=600))
        b.append(lines(cx, y + 110, cx + tw, 3, 24))

    b.append(footer("Who haven't we paired with yet, and what could we learn from each other?",
                    "What would finish faster if two of us worked on it?", FLOW_TAG))
    write_board("pairing-mobbing-board", "Pairing & Mobbing",
                "A3 landscape board: four pairing and mobbing styles, a pair stair, session agreements, skills to spread, "
                "this week's pairs, and a quick retro.", "\n".join(b))


# ---------------------------------------------------------------- pre-mortem

def build_pre_mortem():
    b = [header("Pre-mortem",
                "Imagine the work has already failed, explain why, then act now to prevent the most likely causes.",
                "Run a Project · Inspired by Gary Klein's Pre-mortem · Prospective Hindsight · Risks Before They Happen",
                legend([("sticky", PINK_ST, "Pink Sticky = Why it failed"), ("dot", ACCENT, "Dot = Vote (3 per person)")]))]

    x, y, w, h = 24, 148, 1632, 170
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "The Scenario", PURPLE, "READ IT ALOUD · SPEAK AS IF IT HAS ALREADY HAPPENED"))
    b.append(T(x + 18, y + 100, "It's", 22, d, SERIF, italic=True))
    b.append(L(x + 60, y + 103, x + 240, y + 103, d, 1.2, ' stroke-opacity=".4"'))
    b.append(T(x + 250, y + 100, "and this has failed badly. What went wrong?", 22, d, SERIF, italic=True))
    b.append(field(x + 18, y + 146, "Project, plan or release:", x + 800, d))
    b.append(field(x + 830, y + 146, "Failure looks like:", x + w - 18, d))

    y, h = 332, 410
    x, w = 24, 1082
    d = RED[0]
    b.append(panel(x, y, w, h, 2, "Why It Failed", RED, "SILENT WRITING FIRST · ONE REASON PER STICKY"))
    b.append(bullets(x + 22, y + 74, ["Everyone writes alone for 5 minutes, in the past tense: “We lost our key supplier”",
                                      "Think wide: people, tech, customers, money, dependencies, decisions"], d))
    b.append(dashed(x + 10, x + w - 10, y + 110, d))
    b.append(sticky_zone(x + 10, y + 116, w - 20, h - 128, d, "Pink stickies, clustered by theme", chips=(PINK_ST,)))

    x, w = 1120, 536
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 3, "Top Risks", ORANGE, "AFTER DOT VOTING"))
    b.append(table(x + 18, y + 84, [("#", 34), ("Reason", 240), ("Likely", 70), ("Impact", 70), ("Votes", w - 36 - 414)], 8, d, 36))

    y, h = 756, 304
    x, w = 24, 1082
    d = FOREST[0]
    b.append(panel(x, y, w, h, 4, "Prevent or Detect", FOREST, "FOR EACH TOP RISK"))
    b.append(table(x + 18, y + 84, [("Top risk", 250), ("We'll prevent it by…", 330), ("Early warning sign", 280),
                                    ("Owner", w - 36 - 860)], 5, d, 36))

    x, w = 1120, 536
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 5, "Next Steps", EMERALD))
    for i, m in enumerate(["Top risks added to the RAID Log", "Prevention actions added to the backlog",
                           "Warning signs visible on the team board", "Plan or scope changed where needed",
                           "Re-run before the next big milestone"]):
        b.append(checkbox(x + 18, y + 88 + i * 30, m, d, 11))
    b.append(field(x + 18, y + 260, "Review these risks on:", x + w - 18, d))

    b.append(footer("It's six months from now and this has failed. What happened?",
                    "Which of these are we quietly hoping won't happen?", PROJECT_TAG))
    write_board("pre-mortem-board", "Pre-mortem",
                "A3 landscape pre-mortem board: the failure scenario, reasons it failed, top risks after dot voting, "
                "prevention and early warning signs, and next steps.", "\n".join(b))


# ---------------------------------------------------------------- root cause

def build_root_cause():
    b = [header("Root Cause Analysis",
                "Dig beneath a recurring problem with a fishbone and 5 Whys, check the cause, and test a fix.",
                "Improve · Fishbone (Ishikawa) Diagram · 5 Whys · Fix the System, Not the Person",
                header_fields(["Team", "Date"]))]

    x, y, w, h = 24, 148, 1632, 130
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "The Problem", SLATE, "FACTS, NOT BLAME"))
    b.append(field(x + 18, y + 82, "What happened:", x + 800, d))
    b.append(field(x + 830, y + 82, "When, where, how often:", x + w - 18, d))
    b.append(field(x + 18, y + 110, "Impact:", x + w - 18, d))

    # 2 fishbone
    x, y, w, h = 24, 292, 1082, 470
    d = BLUE[0]
    b.append(panel(x, y, w, h, 2, "Fishbone", BLUE, "STICKIES ON THE BONE THEY BELONG TO"))
    top, bot = y + 64, y + h - 14
    spine = (top + bot) / 2
    hx0 = x + w - 200
    b.append(R(x + 10, top, w - 20, bot - top, "url(#dots)", 6))
    b.append(L(x + 40, spine, hx0, spine, d, 3))
    b.append(f'<path d="M{hx0 - 14:g},{spine - 8:g} L{hx0:g},{spine:g} L{hx0 - 14:g},{spine + 8:g}" fill="none" stroke="{d}" stroke-width="3"/>')
    b.append(R(hx0 + 6, spine - 60, 176, 120, "white", 8, f' stroke="{d}" stroke-opacity=".5" stroke-width="1.5"'))
    b.append(T(hx0 + 22, spine - 34, "PROBLEM", 9, d, MONO, weight=600, ls=".12em"))
    b.append(lines(hx0 + 22, spine - 4, hx0 + 166, 3, 24))
    cats_top = ["People & Skills", "Process", "Tools & Tech"]
    cats_bot = ["Environment", "Information", "Requirements"]
    for i in range(3):
        bx = x + 270 + i * 230
        for cats, end_y, sign in ((cats_top, top + 50, -1), (cats_bot, bot - 50, 1)):
            b.append(L(bx, spine, bx - 130, end_y, d, 2, ' stroke-opacity=".6"'))
            ly = end_y - 26 if sign < 0 else end_y + 8
            b.append(R(bx - 230, ly, 200, 26, d, 5))
            b.append(T(bx - 130, ly + 17, cats[i], 11, "white", weight=600, anchor="middle"))

    # 3 five whys
    x, w = 1120, 536
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 3, "5 Whys", PURPLE, "ASK WHY UNTIL YOU REACH A CAUSE YOU CAN FIX"))
    for i in range(5):
        ry = y + 84 + i * 66
        b.append(T(x + 18, ry, f"Why {i + 1}?", 12, d, weight=600))
        b.append(L(x + 90, ry + 3, x + w - 18, ry + 3, WRITE))
        b.append(L(x + 18, ry + 30, x + w - 18, ry + 30, WRITE))
        if i < 4:
            b.append(T(x + 30, ry + 52, "↓", 12, d, op=".5"))
    b.append(R(x + 14, y + h - 66, w - 28, 52, PURPLE[1], 6, f' stroke="{d}" stroke-opacity=".4" stroke-width="1.5"'))
    b.append(field(x + 28, y + h - 34, "Root cause:", x + w - 28, d, 12))

    y, h = 776, 284
    x, w = 24, 534
    d = AMBER[0]
    b.append(panel(x, y, w, h, 4, "Check the Cause", AMBER, "BEFORE YOU FIX IT"))
    for i, m in enumerate(["If we fixed this, would the problem stop?", "Do we have evidence, not just opinion?",
                           "Is it about the system, not a person?", "Is it within our control or influence?",
                           "Would it explain other problems too?"]):
        b.append(checkbox(x + 18, y + 88 + i * 32, m, d, 11))
    b.append(T(x + 18, y + 256, "Any “no”? Ask why again, or test another branch.", 10.5, d, italic=True, op=".88"))

    x = 572
    d = FOREST[0]
    b.append(panel(x, y, w, h, 5, "Countermeasures", FOREST, "SMALL, TESTABLE FIXES"))
    b.append(table(x + 18, y + 84, [("Action", 280), ("Owner", 100), ("By when", w - 36 - 380)], 5, d, 36))

    x, w = 1120, 536
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 6, "Did It Work?", EMERALD))
    for i, f in enumerate(["We'll measure:", "Baseline:", "Check on:", "Result:"]):
        b.append(field(x + 18, y + 90 + i * 40, f, x + w - 18, d))
    for j, lab in enumerate(["Fixed", "Better", "No change"]):
        b.append(checkbox(x + 18 + j * 120, y + 256, lab, d, 11))

    b.append(footer("Why does this keep happening, and what in our system lets it?",
                    "If we fixed the cause, what else would get better?", FOOT_TAG))
    write_board("root-cause-board", "Root Cause Analysis",
                "A3 landscape root cause board: problem statement, a six-bone fishbone diagram, 5 Whys, a cause check, "
                "countermeasures, and a check that the fix worked.", "\n".join(b))


# ---------------------------------------------------------------- value metrics (EBM)

LEAD_TAG = "Lead the Organisation · Outcomes Over Output · Evidence, Not Opinion"


def build_value_metrics():
    b = [header("Value Metrics",
                "Measure the value you deliver and your ability to deliver more, then pick experiments to improve it.",
                "Lead the Organisation · Inspired by Evidence-Based Management (Scrum.org) · Four Key Value Areas",
                header_fields(["Product / org", "Date"]))]

    x, y, w, h = 24, 148, 1632, 150
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "Goals", SLATE, "BIG AND FAR · NEXT MILESTONE · NOW"))
    gw = (w - 36 - 2 * 16) / 3
    for i, (name, hint) in enumerate([("Strategic goal", "The big, long-term ambition"),
                                      ("Intermediate goal", "The next milestone toward it"),
                                      ("Immediate tactical goal", "What we're working on now")]):
        cx = x + 18 + i * (gw + 16)
        b.append(T(cx, y + 80, name, 12, d, weight=600))
        b.append(T(cx + gw, y + 80, hint, 10, d, italic=True, anchor="end", op=".88"))
        b.append(lines(cx, y + 110, cx + gw, 2, 26))

    y, h = 312, 560
    kvas = [(2, "Current Value", EMERALD, "VALUE DELIVERED TODAY",
             "How much value do customers get now?", ["Customer satisfaction", "Usage / adoption", "Revenue per customer", "Employee satisfaction"]),
            (3, "Unrealised Value", PURPLE, "VALUE STILL ON THE TABLE",
             "How much more value could we deliver?", ["Market share gap", "Unmet customer needs", "Demand we can't serve", "Competitor gaps"]),
            (4, "Time to Market", BLUE, "HOW FAST WE LEARN & DELIVER",
             "How quickly can we deliver and learn?", ["Lead / cycle time", "Release frequency", "Time to first feedback", "Time to fix"]),
            (5, "Ability to Innovate", ORANGE, "WHAT SLOWS NEW VALUE",
             "What stops us delivering new value?", ["% time on new features", "Technical debt", "Defect trends", "Time lost to blockers"])]
    cw = (1632 - 3 * 14) / 4
    for i, (num, title, color, note, q, examples) in enumerate(kvas):
        x = 24 + i * (cw + 14)
        d = color[0]
        b.append(panel(x, y, cw, h, num, title, color, note))
        b.append(T(x + 18, y + 84, q, 16, d, SERIF, italic=True))
        b.append(T(x + 18, y + 116, "EXAMPLE MEASURES", 8.5, d, MONO, weight=600, ls=".12em"))
        for j, ex in enumerate(examples):
            b.append(checkbox(x + 18 + (j % 2) * 186, y + 142 + (j // 2) * 26, ex, d, 10.5))
        b.append(table(x + 18, y + 220, [("Our measure", 150), ("Now", 62), ("Target", 62), ("Trend", cw - 36 - 274)], 4, d, 38))
        b.append(T(x + 18, y + 412, "What the numbers tell us:", 11, d, weight=600))
        b.append(lines(x + 18, y + 440, x + cw - 18, 4, 26))

    y, h = 886, 174
    x, w = 24, 1082
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "Experiments to Improve", FOREST, "ONE PER KEY VALUE AREA AT MOST"))
    b.append(table(x + 18, y + 82, [("Area", 160), ("Experiment", 430), ("Measure we expect to move", 300), ("Owner", w - 36 - 890)], 2, d, 34))

    x, w = 1120, 536
    d = AMBER[0]
    b.append(panel(x, y, w, h, 7, "Review Rhythm", AMBER))
    for i, f in enumerate(["Measures updated every:", "Reviewed with leaders at:", "Next review:"]):
        b.append(field(x + 18, y + 84 + i * 30, f, x + w - 18, d))

    b.append(footer("How do we know we're delivering value, not just output?",
                    "What's stopping us from delivering more value, sooner?", LEAD_TAG))
    write_board("value-metrics-board", "Value Metrics",
                "A3 landscape value metrics board: strategic, intermediate and tactical goals, the four key value areas "
                "with example measures, a measures table and insights, experiments, and a review rhythm.", "\n".join(b))


# ---------------------------------------------------------------- opportunity solution tree

def build_opportunity_tree():
    b = [header("Opportunity Solution Tree",
                "Connect a product outcome to customer opportunities, candidate solutions, and the assumptions to test first.",
                "Envision & Plan · Continuous Discovery · Inspired by Teresa Torres · Assumption Mapping",
                legend([("sticky", BLUE_ST, "Blue = Opportunity"), ("sticky", YELLOW, "Yellow = Solution"),
                        ("sticky", PINK_ST, "Pink = Assumption"), ("sticky", GREEN, "Green = Test")]))]

    x, y, w, h = 24, 148, 1082, 912
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "The Tree", PURPLE, "OUTCOME → OPPORTUNITIES → SOLUTIONS → TESTS"))
    cx = x + w / 2
    # outcome
    ow = 420
    b.append(R(cx - ow / 2, y + 70, ow, 92, EMERALD[1], 8, f' stroke="{EMERALD[0]}" stroke-opacity=".5" stroke-width="1.5"'))
    b.append(T(cx - ow / 2 + 16, y + 94, "OUTCOME · ONE MEASURABLE PRODUCT OUTCOME", 9, EMERALD[0], MONO, weight=600, ls=".1em"))
    b.append(lines(cx - ow / 2 + 16, y + 124, cx + ow / 2 - 16, 2, 24))
    # opportunities
    n = 3
    colw = (w - 40) / n
    oy = y + 210
    for i in range(n):
        ox = x + 20 + i * colw + colw / 2
        b.append(L(cx, y + 162, ox, oy, d, 1.5, ' stroke-opacity=".5"'))
        bw = colw - 30
        b.append(R(ox - bw / 2, oy, bw, 120, BLUE[1], 8, f' stroke="{BLUE[0]}" stroke-opacity=".4"'))
        b.append(T(ox - bw / 2 + 14, oy + 22, f"OPPORTUNITY {i + 1}", 9, BLUE[0], MONO, weight=600, ls=".1em"))
        b.append(T(ox - bw / 2 + 14, oy + 40, "A customer need, pain or desire", 9.5, BLUE[0], italic=True, op=".88"))
        b.append(lines(ox - bw / 2 + 14, oy + 68, ox + bw / 2 - 14, 2, 24))
        # solutions
        sy = oy + 170
        sw = (bw - 12) / 2
        for j in range(2):
            sx = ox - bw / 2 + j * (sw + 12)
            b.append(L(ox, oy + 120, sx + sw / 2, sy, d, 1.2, ' stroke-opacity=".4"'))
            b.append(R(sx, sy, sw, 380, AMBER[1], 6, f' stroke="{AMBER[0]}" stroke-opacity=".35"'))
            b.append(T(sx + 10, sy + 20, "SOLUTION", 8.5, AMBER[0], MONO, weight=600, ls=".1em"))
            b.append(lines(sx + 10, sy + 48, sx + sw - 10, 3, 24))
            b.append(T(sx + 10, sy + 136, "Riskiest assumption", 9.5, RED[0], weight=600))
            b.append(lines(sx + 10, sy + 162, sx + sw - 10, 2, 24))
            b.append(T(sx + 10, sy + 230, "Test", 9.5, FOREST[0], weight=600))
            b.append(lines(sx + 10, sy + 256, sx + sw - 10, 2, 24))
            b.append(T(sx + 10, sy + 324, "Result", 9.5, BLUE[0], weight=600))
            b.append(lines(sx + 10, sy + 350, sx + sw - 10, 1, 24))
    b.append(T(x + 20, y + h - 112, "Compare and contrast: explore at least two or three solutions per opportunity before choosing.",
               10.5, d, italic=True, op=".88"))
    b.append(sticky_zone(x + 10, y + h - 98, w - 20, 86, d, "Parked opportunities and ideas", chips=(BLUE_ST, YELLOW)))

    x, w = 1120, 536
    b.append(panel(x, y, w, 500, 2, "Assumption Map", RED, "TEST TOP-RIGHT FIRST"))
    b.append(quad_grid(x + 54, y + 70, x + w - 18, y + 500 - 52,
                       [("Watch", "Important · good evidence", SLATE), ("Test First", "Important · little evidence", RED),
                        ("Ignore for now", "Less important · evidence", SLATE), ("Park", "Less important · little evidence", AMBER)],
                       "HAVE EVIDENCE", "NO EVIDENCE", "EVIDENCE →", "IMPORTANCE →"))

    y2, h2 = y + 514, h - 514
    d = FOREST[0]
    b.append(panel(x, y2, w, h2, 3, "Assumption Tests", FOREST, "SMALL, FAST, CHEAP"))
    b.append(table(x + 18, y2 + 82, [("Assumption", 150), ("Test", 140), ("Success if…", 120), ("Result", w - 36 - 410)], 6, d, 40))
    b.append(T(x + 18, y2 + h2 - 14, "Types: desirable · viable · feasible · usable · ethical", 9, d, MONO, op=".88", ls=".06em"))

    b.append(footer("Which customer need, if we solved it, would move our outcome most?",
                    "What must be true for this solution to work, and how could we find out this week?", "Envision · Continuous Discovery · Outcomes Over Output"))
    write_board("opportunity-solution-tree-board", "Opportunity Solution Tree",
                "A3 landscape opportunity solution tree: outcome, three opportunities with two solutions each, riskiest "
                "assumptions and tests, an assumption map, and an assumption test table.", "\n".join(b))


# ---------------------------------------------------------------- team topology

def build_team_topology():
    b = [header("Team Topology Design",
                "Design teams around the flow of value: team types, how they interact, and how much each team can hold.",
                "Coordinate Teams · Inspired by Team Topologies (Skelton & Pais) · Cognitive Load · Interaction Modes",
                legend([("sticky", YELLOW, "Yellow Sticky = A team"), ("sticky", PINK_ST, "Pink Sticky = Pain point")]))]

    x, y, w, h = 24, 148, 1632, 290
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Team Types", BLUE, "MOST TEAMS SHOULD BE STREAM-ALIGNED"))
    types = [("Stream-aligned", EMERALD, ["Owns a flow of work end to end:", "a product, journey or customer", "segment. Delivers value directly."]),
             ("Platform", BLUE, ["Provides internal services that", "stream-aligned teams use self-", "service, reducing their load."]),
             ("Enabling", PURPLE, ["Helps other teams build new skills", "or adopt practices, for a while,", "then steps back."]),
             ("Complicated subsystem", ORANGE, ["Owns a part needing deep", "specialist knowledge, so others", "don't have to."])]
    cw = (w - 28 - 3 * 12) / 4
    for i, (name, col, body) in enumerate(types):
        cx = x + 14 + i * (cw + 12)
        cd = col[0]
        b.append(R(cx, y + 64, cw, h - 78, "white", 6, f' stroke="{cd}" stroke-opacity=".25"'))
        b.append(R(cx, y + 64, cw, 5, cd, 3))
        b.append(T(cx + 16, y + 94, name, 14, cd, weight=600))
        b.append(para(cx + 16, y + 120, body, 10.5, cd, 16))
        b.append(T(cx + 16, y + 186, "Our teams of this type:", 10.5, cd, weight=600))
        b.append(lines(cx + 16, y + 212, cx + cw - 16, 2, 26))

    y, h = 452, 420
    x, w = 24, 1082
    d = SLATE[0]
    b.append(panel(x, y, w, h, 2, "Team Map", SLATE, "PLACE TEAMS · DRAW HOW THEY INTERACT"))
    b.append(sticky_zone(x + 10, y + 64, w - 20, h - 116, d, "One yellow sticky per team, grouped by value stream", chips=(YELLOW, PINK_ST)))
    ly = y + h - 24
    for i, (lab, dash) in enumerate([("Collaboration · work closely, for a time", ""),
                                     ("X-as-a-Service · use with little contact", ' stroke-dasharray="8,5"'),
                                     ("Facilitating · help and coach", ' stroke-dasharray="2,4"')]):
        lx = x + 18 + i * 350
        b.append(L(lx, ly - 4, lx + 36, ly - 4, d, 2.5, dash))
        b.append(T(lx + 44, ly, lab, 10.5, d))

    x, w = 1120, 536
    d = RED[0]
    b.append(panel(x, y, w, h, 3, "Cognitive Load Check", RED, "CAN EACH TEAM HOLD WHAT IT OWNS?"))
    b.append(table(x + 18, y + 84, [("Team", 120), ("Domains & systems owned", 200), ("Load L/M/H", 90), ("Too much?", w - 36 - 410)], 7, d, 40))

    y, h = 886, 174
    x, w = 24, 1082
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 4, "Interaction Agreements", PURPLE, "EVERY COLLABORATION HAS AN END DATE"))
    b.append(table(x + 18, y + 82, [("Team A", 180), ("Team B", 180), ("Mode", 200), ("Purpose", 330), ("Review by", w - 36 - 890)], 2, d, 34))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 5, "Changes to Try", FOREST))
    b.append(lines(x + 18, y + 88, x + w - 18, 3, 26))

    b.append(footer("Which team is carrying more than it can hold?",
                    "If we redrew one team boundary, which dependency would disappear?", PROGRAM_TAG))
    write_board("team-topology-board", "Team Topology Design",
                "A3 landscape team topology board: four team types, a team map with interaction modes, a cognitive load "
                "check, interaction agreements, and changes to try.", "\n".join(b))


# ---------------------------------------------------------------- AI working agreement

def build_ai_agreement():
    b = [header("AI Working Agreement",
                "Agree how the team uses AI tools: where it helps, the guardrails, how output is reviewed, and how you'll know it's working.",
                "Form the Team · Responsible Use · Human Review · Measure the Impact · Review It Often",
                header_fields(["Team", "Date"]))]

    y, h = 148, 300
    x, w = 24, 808
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Where We Use AI", BLUE, "BE SPECIFIC: NAME THE TASKS"))
    cw3 = (w - 36 - 2 * 14) / 3
    for i, (name, col, hint) in enumerate([("Encouraged", EMERALD, "e.g. drafts, summaries, test ideas"),
                                           ("With care", AMBER, "e.g. code, analysis: always reviewed"),
                                           ("Not for", RED, "e.g. decisions about people")]):
        cx = x + 18 + i * (cw3 + 14)
        b.append(T(cx, y + 80, name, 13, col[0], weight=600))
        b.append(T(cx, y + 98, hint, 9.5, col[0], italic=True, op=".88"))
        b.append(lines(cx, y + 130, cx + cw3, 6, 26))

    x, w = 846, 810
    d = RED[0]
    b.append(panel(x, y, w, h, 2, "Guardrails", RED, "CHECK WITH YOUR ORGANISATION'S POLICY"))
    for i, m in enumerate(["Only approved tools for work data", "No confidential, customer or personal data in unapproved tools",
                           "A person reviews AI output before it's used or shipped", "We say when work is substantially AI-assisted",
                           "We check sources, facts and licences"]):
        b.append(checkbox(x + 18, y + 86 + i * 30, m, d, 11))
    b.append(field(x + 18, y + 248, "Approved tools:", x + w / 2 - 10, d))
    b.append(field(x + w / 2 + 10, y + 248, "Policy owner / contact:", x + w - 18, d))

    y, h = 462, 300
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 3, "Quality & Review", PURPLE, "SAME BAR, WHOEVER WROTE IT"))
    for i, m in enumerate(["AI-assisted code gets the same review and tests as any code",
                           "The person who uses AI owns the result", "Reviewers can ask how output was produced"]):
        b.append(checkbox(x + 18, y + 86 + i * 30, m, d, 11))
    b.append(T(x + 18, y + 190, "Additions to our Definition of Done:", 11, d, weight=600))
    b.append(lines(x + 18, y + 218, x + w - 18, 3, 26))

    x, w = 846, 397
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 4, "Skills & Sharing", EMERALD))
    for i, f in enumerate(["Shared prompts live at:", "We share what works at:", "Who can help others:", "Skills we'll keep sharp:"]):
        b.append(field(x + 18, y + 88 + i * 46, f, x + w - 18, d))

    x = 1257
    d = AMBER[0]
    b.append(panel(x, y, w, h, 5, "Risks We'll Watch", AMBER))
    b.append(bullets(x + 22, y + 74, ["Wrong or invented answers", "Security and data leaks", "Bias · over-reliance · lost skills"], d))
    b.append(dashed(x + 10, x + w - 10, y + 128, d))
    b.append(sticky_zone(x + 10, y + 134, w - 20, h - 146, d, chips=(PINK_ST,)))

    y, h = 776, 284
    x, w = 24, 1082
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "Measure the Impact", FOREST, "IS IT ACTUALLY HELPING?"))
    b.append(table(x + 18, y + 84, [("Measure", 300), ("Before", 140), ("After", 140), ("What we noticed", w - 36 - 580)], 4, d, 34))
    b.append(T(x + 18, y + h - 20, "Try: cycle time · defects found later · review time · rework · team confidence", 9, d, MONO, op=".88", ls=".06em"))

    x, w = 1120, 536
    d = SLATE[0]
    b.append(panel(x, y, w, h, 7, "Review This Agreement", SLATE, "AI CHANGES FAST"))
    for i, f in enumerate(["Review every:", "Last reviewed:", "Owner:"]):
        b.append(field(x + 18, y + 90 + i * 36, f, x + w - 18, d))
    b.append(checkbox(x + 18, y + 210, "Agreed by the whole team", d, 11))
    b.append(checkbox(x + 18, y + 240, "Checked against organisation policy", d, 11))

    b.append(footer("Where does AI genuinely help us, and where does it get in the way?",
                    "Would we be comfortable explaining how this was made?", "Form the Team · Working Agreements · Responsible Use"))
    write_board("ai-working-agreement-board", "AI Working Agreement",
                "A3 landscape AI working agreement: where the team uses AI, guardrails, quality and review, skills and "
                "sharing, risks, impact measures, and a review schedule.", "\n".join(b))


# ---------------------------------------------------------------- outcome status report

def build_status_report():
    b = [header("Outcome Status Report",
                "A one-page update built on outcomes, a forecast range, risks and the decisions needed, not traffic lights.",
                "Run a Project · Outcomes Over Output · Forecast Ranges · Decisions, Not Just Status",
                header_fields(["Project", "Report date"]))]

    x, y, w, h = 24, 148, 1632, 150
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Headline", PURPLE, "IF THEY READ ONLY THIS"))
    b.append(T(x + 18, y + 96, "In one sentence:", 18, d, SERIF, italic=True))
    b.append(L(x + 180, y + 99, x + 1100, y + 99, d, 1, ' stroke-opacity=".3"'))
    b.append(T(x + 1130, y + 82, "CONFIDENCE", 9, d, MONO, weight=600, ls=".12em"))
    for i in range(5):
        ccx = x + 1140 + i * 52
        b.append(f'<circle cx="{ccx}" cy="{y + 110}" r="15" fill="white" stroke="{d}" stroke-opacity=".5" stroke-width="1.5"/>')
        b.append(T(ccx, y + 115, str(i + 1), 12, d, weight=600, anchor="middle"))
    b.append(T(x + 1420, y + 82, "SINCE LAST TIME", 9, d, MONO, weight=600, ls=".12em"))
    for j, lab in enumerate(["↑", "→", "↓"]):
        b.append(checkbox(x + 1420 + j * 60, y + 116, lab, d, 13))
    b.append(field(x + 18, y + 134, "Because:", x + 1100, d))

    y, h = 312, 380
    x, w = 24, 1082
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 2, "Outcomes", EMERALD, "WHAT'S CHANGED FOR CUSTOMERS AND THE BUSINESS"))
    b.append(table(x + 18, y + 84, [("Outcome", 310), ("Measure", 220), ("Start", 100), ("Now", 100), ("Target", 100),
                                    ("Trend", w - 36 - 830)], 6, d, 44))

    x, w = 1120, 536
    d = AMBER[0]
    b.append(panel(x, y, w, h, 3, "Forecast", AMBER, "A RANGE, WITH ITS ASSUMPTIONS"))
    for i, f in enumerate(["Likely finish range:", "Work done / remaining:", "Scope change since last report:"]):
        b.append(field(x + 18, y + 90 + i * 40, f, x + w - 18, d))
    b.append(T(x + 18, y + 226, "Has the forecast moved?", 11, d, weight=600))
    for j, lab in enumerate(["No", "Earlier", "Later"]):
        b.append(checkbox(x + 200 + j * 90, y + 226, lab, d, 11))
    b.append(field(x + 18, y + 270, "Why:", x + w - 18, d))
    b.append(T(x + 18, y + 330, "See the Release Forecast board for the burn-up.", 10, d, italic=True, op=".88"))

    y, h = 706, 354
    x, w = 24, 534
    d = BLUE[0]
    b.append(panel(x, y, w, h, 4, "Delivered & Learned", BLUE, "SINCE THE LAST REPORT"))
    b.append(T(x + 18, y + 82, "Delivered (working, in use):", 11, d, weight=600))
    b.append(lines(x + 18, y + 110, x + w - 18, 4, 26))
    b.append(T(x + 18, y + 230, "Learned (what changed our thinking):", 11, d, weight=600))
    b.append(lines(x + 18, y + 258, x + w - 18, 3, 26))

    x = 572
    d = RED[0]
    b.append(panel(x, y, w, h, 5, "Top Risks & Issues", RED, "FROM THE RAID LOG"))
    b.append(table(x + 18, y + 84, [("Risk / issue", 210), ("Action", 180), ("Owner", w - 36 - 390)], 6, d, 40))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "Decisions Needed", FOREST, "WHAT WE NEED FROM YOU"))
    b.append(table(x + 18, y + 84, [("Decision", 230), ("From whom", 130), ("By when", w - 36 - 360)], 4, d, 44))
    b.append(field(x + 18, y + h - 26, "Next report:", x + w - 18, d))

    b.append(footer("What has changed for our customers since the last report?",
                    "What decision do we need, and from whom?", PROJECT_TAG))
    write_board("status-report-board", "Outcome Status Report",
                "A3 landscape one-page status report: headline with confidence and trend, outcomes table, forecast range, "
                "delivered and learned, top risks and issues, and decisions needed.", "\n".join(b))


# ---------------------------------------------------------------- ADKAR change readiness

ADKAR = [("Awareness", BLUE, "of why the change is needed",
          ["People ask “why are we doing this?”", "Rumours fill the silence"],
          ["Sponsor explains the why, early and often", "Share the cost of not changing"]),
         ("Desire", PURPLE, "to support and take part",
          ["People understand, but resist or stall", "“What's in it for me?” is unanswered"],
          ["Involve people in shaping the change", "Managers discuss concerns one-to-one"]),
         ("Knowledge", SKY, "of how to change",
          ["Willing, but unsure what to do", "Lots of “how do I…?” questions"],
          ["Training, guides and worked examples", "Show the new way on real work"]),
         ("Ability", EMERALD, "to do it in practice",
          ["Know how, but can't do it yet", "Old habits return under pressure"],
          ["Coaching, pairing and practice time", "Remove blockers: tools, time, access"]),
         ("Reinforcement", ORANGE, "to make it stick",
          ["Early wins, then people slide back", "The old way is still rewarded"],
          ["Recognise and celebrate adoption", "Measure use; fix what pulls people back"])]


def build_adkar():
    b = [header("ADKAR Change Readiness",
                "Find where people are in a change, spot the barrier point, and act on it before moving on.",
                "Lead the Organisation · Inspired by Prosci's ADKAR® Model (Jeff Hiatt) · The People Side of Change",
                header_fields(["Change", "Sponsor"]))]

    x, y, w, h = 24, 148, 1632, 150
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "Change on a Page", SLATE, "WHAT, WHY, WHO, WHEN"))
    hw = (w - 54) / 2
    for i, f in enumerate(["What's changing:", "Why now:"]):
        b.append(field(x + 18, y + 84 + i * 34, f, x + 18 + hw, d))
    for i, f in enumerate(["Who's affected:", "Key dates:"]):
        b.append(field(x + 36 + hw, y + 84 + i * 34, f, x + w - 18, d))

    x, y, w, h = 24, 312, 1632, 330
    d = INK
    b.append(panel(x, y, w, h, 2, "Readiness Grid", (SLATE[0], "#FFFFFF"), "SCORE 1–5 · THE FIRST LOW SCORE IS THE BARRIER POINT"))
    gx0, gy = x + 18, y + 72
    group_w, el_w = 250, 222
    bar_w = w - 36 - group_w - 5 * el_w
    b.append(T(gx0 + 6, gy + 22, "PERSON OR GROUP", 9, SLATE[0], MONO, weight=600, ls=".12em"))
    for i, (name, (dk, lt), _, _, _) in enumerate(ADKAR):
        cx = gx0 + group_w + i * el_w
        b.append(R(cx + 3, gy, el_w - 6, 32, dk, 5))
        b.append(T(cx + el_w / 2, gy + 21, f"{name[0]} · {name.upper()}", 10, "white", MONO, weight=600, anchor="middle", ls=".1em"))
    bx = gx0 + group_w + 5 * el_w
    b.append(R(bx + 3, gy, bar_w - 3, 32, RED[0], 5))
    b.append(T(bx + bar_w / 2 + 1, gy + 21, "BARRIER POINT", 10, "white", MONO, weight=600, anchor="middle", ls=".1em"))
    rows, rh = 5, 37
    for r in range(rows):
        ry = gy + 40 + r * rh
        b.append(R(gx0, ry, group_w - 6, rh - 6, SLATE[1], 4, f' stroke="{SLATE[0]}" stroke-opacity=".15"'))
        b.append(L(gx0 + 10, ry + rh - 14, gx0 + group_w - 18, ry + rh - 14, WRITE, 1))
        for i, (_, (dk, lt), _, _, _) in enumerate(ADKAR):
            cx = gx0 + group_w + i * el_w
            b.append(R(cx + 3, ry, el_w - 6, rh - 6, lt, 4, f' stroke="{dk}" stroke-opacity=".2"'))
            for k in range(5):
                b.append(T(cx + el_w / 2 - 60 + k * 30, ry + 22, str(k + 1), 10, dk, MONO, anchor="middle", op=".88"))
        b.append(R(bx + 3, ry, bar_w - 3, rh - 6, RED[1], 4, f' stroke="{RED[0]}" stroke-opacity=".2"'))
    b.append(T(gx0, y + h - 14, "Circle each score. Scores run 1 (not at all) to 5 (fully). The barrier point is the first element scored 3 or lower, "
               "working left to right. Fix it before working on later elements.", 10, SLATE[0], italic=True, op=".88"))

    y, h = 656, 240
    cw = (1632 - 4 * 12) / 5
    for i, (name, color, sub, missing, helps) in enumerate(ADKAR):
        x = 24 + i * (cw + 12)
        dk = color[0]
        b.append(panel(x, y, cw, h, name[0], name, color))
        b.append(T(x + cw - 16, y + 31, sub, 9, "white", italic=True, anchor="end", op=".88"))
        b.append(T(x + 16, y + 76, "MISSING IF…", 8.5, dk, MONO, weight=600, ls=".12em"))
        b.append(para(x + 16, y + 96, missing, 10.5, dk, 16, italic=True))
        b.append(T(x + 16, y + 140, "WHAT HELPS", 8.5, dk, MONO, weight=600, ls=".12em"))
        b.append(bullets(x + 22, y + 156, helps, dk, 18))
        b.append(field(x + 16, y + 214, "Our action:", x + cw - 16, dk))

    y, h = 910, 150
    x, w = 24, 1082
    d = RED[0]
    b.append(panel(x, y, w, h, 3, "Action Plan", RED, "ONE ACTION PER BARRIER POINT"))
    b.append(table(x + 18, y + 76, [("Who (person or group)", 220), ("Barrier point", 160), ("Action", 400), ("Owner", 140),
                                    ("By when", w - 36 - 920)], 2, d, 26))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 4, "Reinforce & Re-assess", FOREST))
    for i, f in enumerate(["We'll recognise success by:", "We'll measure adoption by:", "Re-assess on:"]):
        b.append(field(x + 18, y + 80 + i * 26, f, x + w - 18, d))

    b.append(footer("Where is each group in this change, really?",
                    "What's the first thing stopping them, and what would help most?",
                    "ADKAR® is a registered trademark of Prosci, Inc. · Lead the Organisation"))
    write_board("adkar-board", "ADKAR Change Readiness",
                "A3 landscape change readiness board based on the ADKAR model: change on a page, a readiness grid scoring "
                "awareness, desire, knowledge, ability and reinforcement with a barrier point, one panel per element with "
                "signs and helpful actions, an action plan, and reinforcement and re-assessment.", "\n".join(b))


# ---------------------------------------------------------------- portfolio kanban & investment mix

def build_portfolio_kanban():
    b = [header("Portfolio Kanban & Investment Mix",
                "Limit how many big initiatives run at once, decide with a lean business case, and keep investment balanced.",
                "Lead the Organisation · Lean Portfolio Management · Limit Portfolio WIP · Stop Starting, Start Finishing",
                header_fields(["Portfolio", "Date"]))]

    x, y, w, h = 24, 148, 1632, 470
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Portfolio Kanban", BLUE, "ONE STICKY PER INITIATIVE · PULL, DON'T PUSH"))
    cols = [("Funnel", "Every new idea lands here", False), ("Reviewing", "Worth a closer look?", True),
            ("Analysing", "Lean business case", True), ("Ready", "Approved, waiting for capacity", True),
            ("Implementing", "MVP first, then persevere or pivot", True), ("Done", "Outcome measured", False)]
    n = len(cols)
    cw = (w - 28 - (n - 1) * 10) / n
    for i, (name, sub, wip) in enumerate(cols):
        cx = x + 14 + i * (cw + 10)
        b.append(R(cx, y + 64, cw, h - 78, "white", 6, f' fill-opacity=".55" stroke="{d}" stroke-opacity=".2"'))
        b.append(T(cx + 12, y + 88, name, 13, d, weight=600))
        b.append(T(cx + 12, y + 106, sub, 9.5, d, op=".88"))
        if wip:
            b.append(field(cx + 12, y + 134, "WIP limit:", cx + cw - 12, d, 10.5))
        b.append(field(cx + 12, y + 164, "Exit when:", cx + cw - 12, d, 10.5))
        b.append(sticky_zone(cx + 6, y + 178, cw - 12, h - 198, d, "Initiatives", chips=(YELLOW,)))

    y, h = 632, 428
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Lean Business Case", PURPLE, "ONE PAGE PER INITIATIVE IN ANALYSING"))
    b.append(field(x + 18, y + 86, "Initiative:", x + w - 18, d))
    b.append(field(x + 18, y + 122, "Problem or opportunity:", x + w - 18, d))
    b.append(T(x + 18, y + 162, "Hypothesis", 11, d, weight=600))
    for i, lead in enumerate(["We believe…", "will result in…", "We'll know when…"]):
        b.append(field(x + 30, y + 190 + i * 30, lead, x + w - 18, d))
    b.append(field(x + 18, y + 298, "Smallest version (MVP):", x + w - 18, d))
    b.append(field(x + 18, y + 334, "Cost range:", x + w / 2 - 10, d))
    b.append(T(x + w / 2 + 10, y + 334, "Cost of delay:", 11, d))
    for j, lab in enumerate(["High", "Medium", "Low"]):
        b.append(checkbox(x + w / 2 + 110 + j * 80, y + 334, lab, d, 10.5))
    b.append(field(x + 18, y + 372, "Go / no-go criteria:", x + w - 18, d))
    b.append(T(x + 18, y + 408, "Decision:", 11, d, weight=600))
    for j, lab in enumerate(["Go to Ready", "Not now", "Stop"]):
        b.append(checkbox(x + 100 + j * 130, y + 408, lab, d, 10.5))

    x, w = 846, 397
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 3, "Investment Mix", EMERALD, "AGREE THE SPLIT UP FRONT"))
    b.append(table(x + 18, y + 84, [("Type of work", 190), ("Target %", 75), ("Actual %", w - 36 - 265)], 6, d, 40))
    for i, t in enumerate(["New bets", "Grow existing", "Run & maintain", "Tech debt & enablers", "Unplanned buffer", "Total = 100%"]):
        b.append(T(x + 24, y + 84 + 10 + (i + 1) * 40 - 14, t, 11, d, weight=600 if i == 5 else None))
    b.append(T(x + 18, y + h - 20, "Is the actual mix what we intended?", 10.5, d, italic=True, op=".88"))

    x = 1257
    d = AMBER[0]
    b.append(panel(x, y, w, h, 4, "Portfolio Review", AMBER))
    for i, f in enumerate(["Review cadence:", "Decision forum:"]):
        b.append(field(x + 18, y + 88 + i * 34, f, x + w - 18, d))
    for i, m in enumerate(["WIP limits respected", "Stop something to start something", "Funding checked against outcomes",
                           "Done items had their outcome measured", "Mix compared with the target"]):
        b.append(checkbox(x + 18, y + 176 + i * 30, m, d, 11))
    b.append(field(x + 18, y + 346, "Next review:", x + w - 18, d))

    b.append(footer("What would we stop to make room for this?",
                    "Which initiative, if it were the only one, would we finish first?", LEAD_TAG))
    write_board("portfolio-kanban-board", "Portfolio Kanban & Investment Mix",
                "A3 landscape portfolio board: a six-column portfolio Kanban with WIP limits and exit criteria, a lean "
                "business case, an investment mix table, and a portfolio review checklist.", "\n".join(b))


# ---------------------------------------------------------------- delivery metrics & tech debt

def build_delivery_metrics():
    b = [header("Delivery Metrics & Tech Debt",
                "Track how quickly and safely you deliver, keep technical debt visible, and plan time to pay it down.",
                "Manage Flow · Inspired by DORA's Four Key Metrics · Technical Debt Quadrant (Martin Fowler)",
                header_fields(["Team / system", "Date"]))]

    x, y, w, h = 24, 148, 1632, 330
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Four Key Delivery Metrics", BLUE, "TWO FOR SPEED · TWO FOR STABILITY · TRACK THE TREND"))
    keys = [("Deployment Frequency", EMERALD, "SPEED", ["How often we release", "to production."]),
            ("Lead Time for Changes", SKY, "SPEED", ["Time from code committed", "to running in production."]),
            ("Change Failure Rate", ORANGE, "STABILITY", ["% of releases that cause a", "failure needing a fix."]),
            ("Recovery Time", RED, "STABILITY", ["Time to restore service", "after a failed release."])]
    cw = (w - 28 - 3 * 12) / 4
    for i, (name, col, kind, body) in enumerate(keys):
        cx = x + 14 + i * (cw + 12)
        cd = col[0]
        b.append(R(cx, y + 64, cw, h - 78, "white", 6, f' stroke="{cd}" stroke-opacity=".25"'))
        b.append(R(cx, y + 64, cw, 5, cd, 3))
        b.append(T(cx + 16, y + 94, name, 14, cd, weight=600))
        b.append(T(cx + cw - 16, y + 94, kind, 8.5, cd, MONO, anchor="end", op=".88", ls=".12em"))
        b.append(para(cx + 16, y + 118, body, 10.5, cd, 16))
        for j, f in enumerate(["3 months ago:", "Now:", "Target:"]):
            b.append(field(cx + 16, y + 176 + j * 30, f, cx + cw - 16, cd))
        b.append(field(cx + 16, y + 266, "Measured from:", cx + cw - 16, cd))
        for j, lab in enumerate(["Better", "Same", "Worse"]):
            b.append(checkbox(cx + 16 + j * 90, y + 300, lab, cd, 10.5))

    y, h = 492, 400
    x, w = 24, 1082
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Tech Debt Register", PURPLE, "THE INTEREST IS WHAT IT COSTS TO LEAVE IT"))
    b.append(table(x + 18, y + 84, [("Debt", 230), ("Where", 140), ("Interest: cost of leaving it", 300), ("Effort S/M/L", 110),
                                    ("Type", 110), ("Owner", w - 36 - 890)], 8, d, 36))

    x, w = 1120, 536
    b.append(panel(x, y, w, h, 3, "Debt Quadrant", AMBER, "WHY THE DEBT EXISTS"))
    b.append(quad_grid(x + 54, y + 70, x + w - 18, y + h - 52,
                       [("Reckless · Deliberate", "“No time for design.”", RED), ("Prudent · Deliberate", "“Ship now, fix later, knowingly.”", EMERALD),
                        ("Reckless · Inadvertent", "“What's good design?”", ORANGE), ("Prudent · Inadvertent", "“Now we know how we should have built it.”", BLUE)],
                       "RECKLESS", "PRUDENT", "", "DELIBERATE ↑"))

    y, h = 906, 154
    x, w = 24, 808
    d = FOREST[0]
    b.append(panel(x, y, w, h, 4, "Time to Pay It Down", FOREST))
    for i, f in enumerate(["% of each iteration for debt & enablers:", "This iteration we'll pay down:"]):
        b.append(field(x + 18, y + 86 + i * 34, f, x + w - 18, d))

    x, w = 846, 810
    d = SLATE[0]
    b.append(panel(x, y, w, h, 5, "Review", SLATE, "LEARN, DON'T COMPARE TEAMS"))
    for i, f in enumerate(["Metrics reviewed every:", "What the trends tell us:"]):
        b.append(field(x + 18, y + 86 + i * 34, f, x + w - 18, d))

    b.append(footer("Are we getting faster without getting less stable?",
                    "Which debt is costing us most every week we leave it?", FLOW_TAG))
    write_board("delivery-metrics-board", "Delivery Metrics & Tech Debt",
                "A3 landscape board: four key delivery metrics (deployment frequency, lead time, change failure rate, "
                "recovery time), a tech debt register, a debt quadrant, time to pay down debt, and a review.", "\n".join(b))


# ---------------------------------------------------------------- delegation board

DELEGATION = [("Tell", "I decide and tell you"), ("Sell", "I decide and explain why"), ("Consult", "I ask you, then I decide"),
              ("Agree", "We decide together"), ("Advise", "I advise, you decide"), ("Inquire", "You decide, then tell me"),
              ("Delegate", "You decide; no need to tell me")]


def build_delegation():
    b = [header("Delegation Board",
                "Make decision rights explicit: for each area, agree how much the team decides, and move it up over time.",
                "Lead the Organisation · Inspired by Management 3.0 (Jurgen Appelo) · Seven Levels of Delegation",
                header_fields(["Team", "Leader"]))]

    x, y, w, h = 24, 148, 1632, 150
    d = PURPLE[0]
    b.append(panel(x, y, w, h, None, "Seven Levels of Delegation", PURPLE, "FROM LEADER DECIDES TO TEAM DECIDES"))
    n = len(DELEGATION)
    cw = (w - 28 - (n - 1) * 8) / n
    for i, (name, mean) in enumerate(DELEGATION):
        cx = x + 14 + i * (cw + 8)
        b.append(R(cx, y + 64, cw, 72, "white", 6, f' stroke="{d}" stroke-opacity="{.15 + i * .08:.2f}" stroke-width="1.5"'))
        b.append(f'<circle cx="{cx + 22:g}" cy="{y + 88}" r="11" fill="{d}" fill-opacity="{.35 + i * .1:.2f}"/>')
        b.append(T(cx + 22, y + 92, str(i + 1), 10.5, "white", weight=600, anchor="middle"))
        b.append(T(cx + 42, y + 93, name, 13, d, weight=600))
        b.append(T(cx + 14, y + 120, mean, 10.5, d, italic=True))

    x, y, w, h = 24, 312, 1632, 560
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Decision Areas", BLUE, "MARK TODAY'S LEVEL · ARROW TO WHERE WE'RE HEADING"))
    gx0, gy = x + 18, y + 70
    area_w, rev_w = 340, 170
    lv_w = (w - 36 - area_w - rev_w) / n
    b.append(T(gx0 + 6, gy + 20, "DECISION AREA", 9, d, MONO, weight=600, ls=".12em"))
    for i, (name, _) in enumerate(DELEGATION):
        cx = gx0 + area_w + i * lv_w
        b.append(R(cx + 3, gy, lv_w - 6, 30, PURPLE[0], 5, f' fill-opacity="{.35 + i * .1:.2f}"'))
        b.append(T(cx + lv_w / 2, gy + 20, f"{i + 1} · {name.upper()}", 9.5, "white", MONO, weight=600, anchor="middle", ls=".08em"))
    b.append(T(gx0 + area_w + n * lv_w + 10, gy + 20, "REVIEW BY", 9, d, MONO, weight=600, ls=".12em"))
    hints = ["e.g. Hiring into the team", "e.g. Tools and technology", "e.g. How we plan our work", "e.g. Working hours",
             "e.g. Spending up to a limit", "e.g. Architecture choices", "e.g. Who works on what", "e.g. Release timing", ""]
    rows = 9
    rh = (h - 70 - 38 - 12) / rows
    for r in range(rows):
        ry = gy + 38 + r * rh
        b.append(R(gx0, ry, area_w - 6, rh - 6, "white", 4, f' stroke="{d}" stroke-opacity=".15"'))
        b.append(T(gx0 + 12, ry + 18, hints[r], 9.5, d, italic=True, op=".45"))
        b.append(L(gx0 + 12, ry + rh - 16, gx0 + area_w - 20, ry + rh - 16, WRITE, 1))
        for i in range(n):
            cx = gx0 + area_w + i * lv_w
            b.append(R(cx + 3, ry, lv_w - 6, rh - 6, "white", 4, f' fill-opacity=".6" stroke="{d}" stroke-opacity=".12"'))
        rx = gx0 + area_w + n * lv_w
        b.append(R(rx + 3, ry, rev_w - 3, rh - 6, "white", 4, f' fill-opacity=".6" stroke="{d}" stroke-opacity=".12"'))

    y, h = 886, 174
    x, w = 24, 808
    d = RED[0]
    b.append(panel(x, y, w, h, 2, "Guardrails", RED, "LIMITS THAT ALWAYS APPLY"))
    b.append(T(x + 18, y + 80, "e.g. budget limits, legal and policy rules, security standards", 10.5, d, italic=True, op=".88"))
    b.append(lines(x + 18, y + 108, x + w - 18, 2, 26))

    x, w = 846, 810
    d = FOREST[0]
    b.append(panel(x, y, w, h, 3, "Next Steps", FOREST))
    for i, m in enumerate(["Agreed with the team, not just announced", "Posted where everyone can see it",
                           "One area moves up a level next", "Review the board every few months"]):
        b.append(checkbox(x + 18 + (i % 2) * 390, y + 90 + (i // 2) * 34, m, d, 11))

    b.append(footer("Which decisions could the team make without us?",
                    "What would we need to trust to move this up one level?", LEAD_TAG))
    write_board("delegation-board", "Delegation Board",
                "A3 landscape delegation board: the seven levels of delegation, a decision-area grid with a review "
                "column, guardrails, and next steps.", "\n".join(b))


# ---------------------------------------------------------------- coaching conversation (GROW)

def build_coaching_conversation():
    b = [header("Coaching Conversation",
                "A simple structure for one-to-one coaching: agree the goal, explore reality and options, and commit to action.",
                "Facilitate · GROW Model (Sir John Whitmore) · Ask More Than Tell · One-to-One Coaching",
                header_fields(["Coachee", "Date"]))]

    x, y, w, h = 24, 148, 1632, 120
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "Contract", SLATE, "AGREE THIS FIRST"))
    b.append(field(x + 18, y + 86, "What do you want from this conversation?", x + 1100, d))
    b.append(checkbox(x + 1130, y + 86, "Confidentiality agreed", d, 11))
    b.append(field(x + 1330, y + 86, "Time:", x + w - 18, d))

    y, h = 282, 560
    grow = [(2, "Goal", PURPLE, "WHAT DO YOU WANT?", ["What would you like to achieve?", "What would success look like?",
                                                     "Why does this matter to you now?", "How will you know you've got there?"]),
            (3, "Reality", BLUE, "WHERE ARE YOU NOW?", ["What's happening at the moment?", "What have you tried so far?",
                                                        "What's getting in the way?", "What's within your control?"]),
            (4, "Options", EMERALD, "WHAT COULD YOU DO?", ["What could you do?", "What else? And what else?",
                                                           "What would you advise a friend?", "What if there were no limits?"]),
            (5, "Will", ORANGE, "WHAT WILL YOU DO?", ["Which option will you take?", "What's the first step, and when?",
                                                      "What might stop you?", "How committed are you, 1–10?"])]
    cw = (1632 - 3 * 14) / 4
    for i, (num, name, color, note, qs) in enumerate(grow):
        x = 24 + i * (cw + 14)
        dk = color[0]
        b.append(panel(x, y, cw, h, num, name, color, note))
        b.append(T(x + 18, y + 80, "QUESTIONS TO TRY", 8.5, dk, MONO, weight=600, ls=".12em"))
        for j, q in enumerate(qs):
            b.append(T(x + 18, y + 106 + j * 24, q, 14, dk, SERIF, italic=True))
        b.append(T(x + 18, y + 220, "NOTES", 8.5, dk, MONO, weight=600, ls=".12em"))
        b.append(lines(x + 18, y + 252, x + cw - 18, 11, 26))

    y, h = 856, 204
    x, w = 24, 1082
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "Commitments", FOREST, "IN THE COACHEE'S WORDS"))
    b.append(table(x + 18, y + 82, [("Action", 520), ("By when", 160), ("Support needed", w - 36 - 680)], 3, d, 34))

    x, w = 1120, 536
    d = AMBER[0]
    b.append(panel(x, y, w, h, 7, "Coach's Reflection", AMBER, "AFTERWARDS"))
    for i, f in enumerate(["What I noticed:", "Did I ask more than tell?", "Follow up on:"]):
        b.append(field(x + 18, y + 86 + i * 36, f, x + w - 18, d))

    b.append(footer("What do you want to be different by the end of this conversation?",
                    "What's the smallest step you could take this week?", "Facilitate · Coaching · Ask, Don't Tell"))
    write_board("coaching-conversation-board", "Coaching Conversation",
                "A3 landscape GROW coaching canvas: contract, goal, reality, options and will panels with questions and "
                "notes, commitments, and the coach's reflection.", "\n".join(b))


# ---------------------------------------------------------------- psychological safety check

PSAFE = ["I can admit a mistake here without it being held against me.",
         "We raise problems and difficult topics openly.",
         "Different views and backgrounds are welcomed on this team.",
         "It's safe to try something new here, even if it might fail.",
         "I can ask anyone on the team for help.",
         "People on this team have my back.",
         "My ideas are listened to and used."]


def build_psych_safety():
    b = [header("Psychological Safety Check",
                "An anonymous check of how safe it feels to speak up, take risks and admit mistakes, and what to do about it.",
                "Diagnose · Inspired by Amy Edmondson's Research · Anonymous · Not a Validated Survey",
                legend([("dot", "#94A3B8", "Dot = One anonymous vote"), ("sticky", YELLOW, "Yellow Sticky = Observation")]))]

    x, y, w, h = 24, 148, 1082, 520
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "The Check", PURPLE, "ONE DOT PER STATEMENT · VOTE PRIVATELY"))
    st_w = 470
    scale = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]
    sc_w = (w - 36 - st_w) / 5
    gx0, gy = x + 18, y + 70
    for i, lab in enumerate(scale):
        cx = gx0 + st_w + i * sc_w
        b.append(T(cx + sc_w / 2, gy + 14, lab.upper(), 8.5, d, MONO, weight=600, anchor="middle", ls=".06em"))
    rh = (h - 70 - 26 - 14) / len(PSAFE)
    for r, stmt in enumerate(PSAFE):
        ry = gy + 26 + r * rh
        b.append(R(gx0, ry, st_w - 8, rh - 6, "white", 4, f' stroke="{d}" stroke-opacity=".15"'))
        b.append(T(gx0 + 12, ry + rh / 2 + 1, f"{r + 1}.", 11, d, weight=600))
        b.append(T(gx0 + 32, ry + rh / 2 + 1, stmt, 11, d))
        for i in range(5):
            cx = gx0 + st_w + i * sc_w
            shade = [RED[1], ORANGE[1], SLATE[1], EMERALD[1], FOREST[1]][i]
            b.append(R(cx + 3, ry, sc_w - 6, rh - 6, shade, 4, f' stroke="{d}" stroke-opacity=".12"'))
            b.append(R(cx + 3, ry, sc_w - 6, rh - 6, "url(#dots)", 4))

    x, w = 1120, 536
    d = SLATE[0]
    b.append(panel(x, y, w, h, 2, "Run It Safely", SLATE, "SAFETY FIRST, OR THE RESULTS LIE"))
    for i, m in enumerate(["Votes are anonymous (board turned away, or an online form)", "Leaders and managers step out while voting",
                           "Results stay with the team unless it chooses to share", "No one is asked to explain their vote",
                           "Talk about patterns, not individuals"]):
        b.append(checkbox(x + 18, y + 88 + i * 30, m, d, 10.5))
    b.append(T(x + 18, y + 270, "Results", 11, d, weight=600))
    b.append(table(x + 18, y + 296, [("Statement", 110), ("Mostly agree", 120), ("Mostly disagree", 130), ("Change", w - 36 - 360)], 4, d, 40))
    b.append(T(x + 18, y + h - 18, "Re-run every 2–3 months to see the trend.", 10, d, italic=True, op=".88"))

    y, h = 682, 378
    x, w = 24, 534
    d = BLUE[0]
    b.append(panel(x, y, w, h, 3, "What We Notice", BLUE, "PATTERNS, NOT PEOPLE"))
    b.append(bullets(x + 22, y + 74, ["Where are votes lowest? What might explain it?", "What would make it easier to speak up?"], d))
    b.append(dashed(x + 10, x + w - 10, y + 110, d))
    b.append(sticky_zone(x + 10, y + 116, w - 20, h - 128, d, chips=(YELLOW,)))

    x = 572
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 4, "What Leaders Can Do", EMERALD, "MODEL IT"))
    for i, m in enumerate(["Frame work as learning, not just doing", "Admit your own mistakes and doubts",
                           "Ask genuine questions, then listen", "Thank people for bad news and dissent",
                           "Respond to failure with curiosity, not blame", "Make it clear every voice is wanted",
                           "Follow up on what people raise"]):
        b.append(checkbox(x + 18, y + 88 + i * 32, m, d, 11))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 5, "Our Experiments", FOREST, "SMALL CHANGES · CHECK THEM"))
    b.append(table(x + 18, y + 84, [("Experiment", 260), ("Who", 100), ("Check on", w - 36 - 360)], 6, d, 40))

    b.append(footer("What would make it easier to say what you really think here?",
                    "When did someone last speak up, and what happened next?", "Diagnose · Team Health · Psychological Safety"))
    write_board("psych-safety-board", "Psychological Safety Check",
                "A3 landscape psychological safety check: seven statements with a five-point anonymous dot vote, "
                "guidance to run it safely, results, observations, leader behaviours, and experiments.", "\n".join(b))


# ---------------------------------------------------------------- cross-team retro

def build_cross_team_retro():
    b = [header("Cross-Team Retro",
                "Reflect across teams at the end of a period: what worked, what didn't, and one system problem to fix together.",
                "Coordinate Teams · Inspect & Adapt (SAFe) · Joint Retrospective · Fix the System",
                legend([("sticky", GREEN, "Green = Went well"), ("sticky", PINK_ST, "Pink = Problem"),
                        ("sticky", BLUE_ST, "Blue = Idea"), ("dot", ACCENT, "Dot = Vote")]))]

    x, y, w, h = 24, 148, 1632, 150
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "What We Set Out to Do", SLATE, "BRING THE SHARED OBJECTIVES AND THE DATA"))
    b.append(table(x + 18, y + 80, [("Shared objective", 560), ("Planned value", 160), ("Achieved", 160), ("What we learned", w - 36 - 880)], 2, d, 26))

    y, h = 312, 400
    for i, (num, name, col, note, chip, prompt) in enumerate([
            (2, "Went Well Across Teams", EMERALD, "KEEP DOING", GREEN, "Where did teams help each other?"),
            (3, "Cross-Team Problems", RED, "DOT-VOTE THE BIGGEST", PINK_ST, "Where did work wait between teams?"),
            (4, "Ideas", BLUE, "FOR ANY TEAM TO TRY", BLUE_ST, "What would make next period smoother?")]):
        x = 24 + i * 548
        w = 534 if i < 2 else 536
        d = col[0]
        b.append(panel(x, y, w, h, num, name, col, note))
        b.append(bullets(x + 22, y + 74, [prompt], d))
        b.append(dashed(x + 10, x + w - 10, y + 92, d))
        b.append(sticky_zone(x + 10, y + 98, w - 20, h - 110, d, chips=(chip,)))

    y, h = 726, 334
    x, w = 24, 1082
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 5, "Solve the Top Problem", PURPLE, "IN MIXED-TEAM GROUPS"))
    lw = 470
    b.append(field(x + 18, y + 86, "Top problem (most dots):", x + lw, d))
    for i in range(4):
        b.append(field(x + 18, y + 124 + i * 34, f"Why {i + 1}?", x + lw, d))
    b.append(field(x + 18, y + 270, "Root cause:", x + lw, d))
    b.append(table(x + lw + 30, y + 86, [("Improvement", 260), ("Teams involved", 150), ("Owner", w - 36 - lw - 12 - 410)], 5, d, 40))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "Follow Through", FOREST, "INTO THE NEXT PLANNING"))
    for i, m in enumerate(["Improvements added to the next cross-team plan", "Each improvement has an owner",
                           "Teams' own retros have the same themes?", "Progress checked at the cross-team sync"]):
        b.append(checkbox(x + 18, y + 88 + i * 30, m, d, 11))
    b.append(field(x + 18, y + 236, "We'll measure success by:", x + w - 18, d))
    b.append(field(x + 18, y + 276, "Next cross-team retro:", x + w - 18, d))

    b.append(footer("What got in the way between teams, not within them?",
                    "What one change would help every team next period?", PROGRAM_TAG))
    write_board("cross-team-retro-board", "Cross-Team Retro",
                "A3 landscape cross-team retrospective: shared objectives and results, went well, cross-team problems, "
                "ideas, problem solving for the top problem, and follow-through.", "\n".join(b))


# ---------------------------------------------------------------- backlog item anatomy poster

def example_card(x, y, w, h, good, title, body, why, size=11.5):
    dk, lt = (EMERALD if good else RED)
    out = [R(x, y, w, h, lt, 8, f' stroke="{dk}" stroke-opacity=".35" stroke-width="1.5"'),
           R(x, y, 5, h, dk, 3),
           T(x + 18, y + 24, ("✓ GOOD · " if good else "✗ WEAK · ") + title, 9.5, dk, MONO, weight=600, ls=".1em")]
    out.append(para(x + 18, y + 48, body, size, INK, round(size * 1.45)))
    out.append(para(x + 18, y + h - 14 - (len(why) - 1) * 15, why, 10.5, dk, 15, italic=True))
    return "".join(out)


def level_panel(y, h, num, name, color, note, definition, size_line, template, good, weak):
    dk, lt = color
    x, w = 24, 1632
    out = [panel(x, y, w, h, num, name, color, note)]
    ax, aw = x + 18, 430
    out.append(para(ax, y + 80, definition, 12, dk, 17, weight=600))
    ty = y + 80 + len(definition) * 17 + 4
    out.append(T(ax, ty, size_line, 8.5, dk, MONO, op=".88", ls=".1em"))
    out.append(T(ax, ty + 24, "TEMPLATE", 8.5, dk, MONO, weight=600, ls=".12em"))
    th = len(template) * 18 + 16
    out.append(R(ax, ty + 32, aw, th, "white", 6, f' stroke="{dk}" stroke-opacity=".2"'))
    out.append(para(ax + 14, ty + 53, template, 14, dk, 18, font=SERIF, italic=True))
    gx = x + 470
    cw = (w - 470 - 18 - 14) / 2
    out.append(example_card(gx, y + 64, cw, h - 78, True, *good))
    out.append(example_card(gx + cw + 14, y + 64, cw, h - 78, False, *weak))
    return "".join(out)


def build_backlog_anatomy():
    right = "".join([T(1356, 60, "HOW TO READ IT", 8, "#8291A6", MONO, ls=".14em"),
                     T(1356, 86, "✓ Good example, and why it works", 11, "#86EFAC"),
                     T(1356, 112, "✗ Weak example, and what's wrong", 11, "#FCA5A5")])
    b = [header("Backlog Item Anatomy",
                "What a good epic, feature and story look like, with one running example from big bet to thin slice.",
                "Break Down Work · Epics, Features & Stories · INVEST (Bill Wake) · Given / When / Then",
                right)]

    b.append(R(24, 148, 1632, 52, NAVY, 8))
    b.append(R(24, 148, 6, 52, ACCENT, 3))
    b.append(T(48, 180, "RUNNING EXAMPLE", 9, ACCENT, MONO, weight=600, ls=".14em"))
    b.append(T(190, 181, "An online grocery service wants more customers to come back and order again. Follow it down the levels.",
               14, "white", SERIF, italic=True))

    b.append(level_panel(214, 230, 1, "Epic", PURPLE, "THE BIG BET",
                         ["A big bet that should deliver a business", "outcome. Broken into features."],
                         "WEEKS TO MONTHS · OFTEN SEVERAL TEAMS",
                         ["We believe [doing this] for [these people]", "will achieve [this outcome]. We'll know", "we're right when [measure]."],
                         ("Reorder made easy", ["We believe making it quick to repeat a past order, for",
                                                "returning customers, will increase repeat orders. We'll know",
                                                "when weekly repeat orders rise from 22% to 30% in 3 months."],
                          ["Names the people, the outcome and a measure, so it can be proven wrong."]),
                         ("Reorder platform", ["“Build the new reorder platform.”"],
                          ["A solution, not an outcome. No measure, so nobody can", "tell if it worked, or when to stop."])))

    b.append(level_panel(458, 200, 2, "Feature", BLUE, "A USABLE CAPABILITY",
                         ["Something users can see and use that", "delivers part of the epic's value."],
                         "A FEW ITERATIONS · ONE OR TWO TEAMS",
                         ["[Capability] so that [benefit]."],
                         ("One-tap reorder", ["One-tap reorder of a past basket, so returning customers",
                                              "can repeat a weekly shop in under a minute."],
                          ["Usable on its own, with a clear benefit to a named user."]),
                         ("Reorder back end", ["“Reorder API and database changes.”"],
                          ["A technical layer. Nobody can use it alone, so it", "delivers no value until everything else is done."])))

    # story: custom, with acceptance criteria and two weak examples
    y, h = 672, 292
    x, w = 24, 1632
    dk, lt = EMERALD
    b.append(panel(x, y, w, h, 3, "Story", EMERALD, "A THIN VERTICAL SLICE"))
    ax, aw = x + 18, 430
    b.append(para(ax, y + 80, ["A thin, vertical slice of a feature that", "a user can use. Finishes in days."], 12, dk, 17, weight=600))
    b.append(T(ax, y + 122, "DAYS · WITHIN YOUR SLE · ONE TEAM", 8.5, dk, MONO, op=".88", ls=".1em"))
    b.append(T(ax, y + 150, "TEMPLATE", 8.5, dk, MONO, weight=600, ls=".12em"))
    b.append(R(ax, y + 160, aw, 76, "white", 6, f' stroke="{dk}" stroke-opacity=".2"'))
    b.append(para(ax + 14, y + 182, ["As a [type of user], I want [goal]", "so that [reason]."], 14, dk, 18, font=SERIF, italic=True))
    b.append(T(ax + 14, y + 226, "+ acceptance criteria: Given · When · Then", 10, dk, op=".88"))
    b.append(T(ax, y + 262, "INVEST", 9, dk, MONO, weight=600, ls=".12em"))
    b.append(T(ax + 60, y + 262, "Independent · Negotiable · Valuable · Estimable · Small · Testable", 9.5, dk))
    gx = x + 470
    gw = 600
    b.append(R(gx, y + 64, gw, h - 78, EMERALD[1], 8, f' stroke="{dk}" stroke-opacity=".35" stroke-width="1.5"'))
    b.append(R(gx, y + 64, 5, h - 78, dk, 3))
    b.append(T(gx + 18, y + 88, "✓ GOOD · SEE MY LAST ORDER", 9.5, dk, MONO, weight=600, ls=".1em"))
    b.append(para(gx + 18, y + 112, ["As a returning customer, I want to see my last order on",
                                     "the home page so that I can reorder it quickly."], 11.5, INK, 17))
    b.append(T(gx + 18, y + 160, "ACCEPTANCE CRITERIA", 8.5, dk, MONO, weight=600, ls=".12em"))
    b.append(para(gx + 18, y + 180, ["Given I've ordered before, when I open the app,",
                                     "then I see my last order with a Reorder button.",
                                     "Given an item is out of stock, when I reorder,",
                                     "then I'm offered a substitute."], 11, INK, 16))
    b.append(T(gx + 18, y + h - 22, "Valuable to a user, small, and testable from the criteria.", 10.5, dk, italic=True))
    wx = gx + gw + 14
    ww = (x + w - 18 - wx - 12) / 2
    b.append(example_card(wx, y + 64, ww, h - 78, False, "TECHNICAL TASK",
                          ["“As a developer, I want a reorder", "table so that the data is stored.”"],
                          ["No user value. It's a task", "inside a real story."], 11))
    b.append(example_card(wx + ww + 12, y + 64, ww, h - 78, False, "TOO BIG",
                          ["“As a customer, I want to reorder,", "edit my basket and schedule", "delivery.”"],
                          ["Three stories joined by “and”.", "Split it (see Story Splitting)."], 11))

    # also on the backlog
    y = 978
    others = [("Task", "A step the team takes to finish a story. Not tracked as value."),
              ("Spike", "Time-boxed research to answer a question. Its output is knowledge."),
              ("Bug", "Doesn't work as agreed. Fix fast, or order it like any other item."),
              ("Enabler", "Technical work that makes future value possible, such as paying down debt.")]
    cw = (1632 - 3 * 12) / 4
    for i, (name, body) in enumerate(others):
        cx = 24 + i * (cw + 12)
        b.append(R(cx, y, cw, 82, "white", 8, f' stroke="{RULE}" stroke-width="1.5"'))
        b.append(R(cx, y, 5, 82, SLATE[0], 3))
        b.append(T(cx + 18, y + 26, name.upper(), 9.5, SLATE[0], MONO, weight=600, ls=".12em"))
        b.append(para(cx + 18, y + 50, [body[:body.index('.') + 1]] + ([body[body.index('.') + 2:]] if body.index('.') + 2 < len(body) else []),
                      10.5, INK, 15))

    b.append(footer("Who is this for, and what will be better for them?",
                    "Could a user use this slice on its own?", BREAKDOWN_TAG))
    write_board("backlog-anatomy-poster", "Backlog Item Anatomy",
                "A3 landscape reference poster: definitions, templates, and good and weak examples of an epic, a feature "
                "and a story, using one running example, plus INVEST, acceptance criteria, and other backlog item types.",
                "\n".join(b))


# ---------------------------------------------------------------- value stream map

def wbox(x, y, w, h, label, dark, nlines=2, gap=24, fill="white"):
    """Labelled write-on box."""
    out = [R(x, y, w, h, fill, 6, f' stroke="{dark}" stroke-opacity=".3"'),
           T(x + 12, y + 20, label, 8.5, dark, MONO, weight=600, ls=".1em")]
    out.append(lines(x + 12, y + 46, x + w - 12, nlines, gap))
    return "".join(out)


def build_value_stream_map():
    b = [header("Value Stream Map",
                "Map every step from request to customer, see where work waits, and design a faster future state.",
                "Manage Flow · Inspired by Lean Value Stream Mapping (Rother & Shook) · Wait vs. Work Time · Flow Efficiency",
                header_fields(["Value stream", "Date"]))]

    x, y, w, h = 24, 148, 1632, 120
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "Scope", SLATE, "ONE STREAM, ONE TYPE OF WORK"))
    qw = (w - 36 - 3 * 16) / 4
    for i, f in enumerate(["Starts when:", "Ends when:", "Unit of work:", "Measured over:"]):
        cx = x + 18 + i * (qw + 16)
        b.append(field(cx, y + 92, f, cx + qw, d))

    x, y, w, h = 24, 282, 1632, 430
    d = BLUE[0]
    b.append(panel(x, y, w, h, 2, "Current State", BLUE, "PROCESS STEPS LEFT TO RIGHT · WAITS BETWEEN THEM"))
    n, gap = 6, 64
    cw = (w - 28 - (n - 1) * gap) / n
    by, bh = y + 74, 196
    for i in range(n):
        cx = x + 14 + i * (cw + gap)
        b.append(R(cx, by, cw, bh, "white", 6, f' stroke="{d}" stroke-opacity=".35" stroke-width="1.5"'))
        b.append(R(cx, by, cw, 30, d, 6))
        b.append(R(cx, by + 24, cw, 6, d))
        b.append(T(cx + 12, by + 20, f"STEP {i + 1}", 9, "white", MONO, weight=600, ls=".12em"))
        for j, f in enumerate(["Name:", "Who:", "Work time:", "% complete & accurate:", "People / WIP:"]):
            b.append(field(cx + 12, by + 58 + j * 30, f, cx + cw - 12, d, 10.5))
        if i < n - 1:
            tx = cx + cw + gap / 2
            b.append(f'<path d="M{tx - 16:g},{by + bh / 2 + 14:g} L{tx:g},{by + bh / 2 - 14:g} L{tx + 16:g},{by + bh / 2 + 14:g} Z" '
                     f'fill="{AMBER[1]}" stroke="{AMBER[0]}" stroke-width="1.5"/>')
            b.append(T(tx, by + bh / 2 + 10, "W", 10, AMBER[0], weight=600, anchor="middle"))
            b.append(T(tx, by + bh / 2 + 34, "wait", 9, AMBER[0], MONO, anchor="middle"))
            b.append(L(tx - 24, by + bh / 2 + 56, tx + 24, by + bh / 2 + 56, AMBER[0], 1, ' stroke-opacity=".5"'))
    # timeline ladder
    ly_hi, ly_lo = y + 312, y + 360
    b.append(T(x + 18, y + 300, "TIMELINE", 9, d, MONO, weight=600, ls=".12em"))
    pts = []
    for i in range(n):
        cx = x + 14 + i * (cw + gap)
        pts += [(cx, ly_lo), (cx + cw, ly_lo)]
        if i < n - 1:
            pts += [(cx + cw, ly_hi), (cx + cw + gap, ly_hi)]
    path = "M" + " L".join(f"{px:g},{py:g}" for px, py in pts)
    b.append(f'<path d="{path}" fill="none" stroke="{d}" stroke-width="2"/>')
    for i in range(n):
        cx = x + 14 + i * (cw + gap)
        b.append(T(cx + cw / 2, ly_lo + 22, "work", 9, d, MONO, anchor="middle", op=".88"))
        b.append(L(cx + 20, ly_lo + 44, cx + cw - 20, ly_lo + 44, WRITE, 1))
        if i < n - 1:
            b.append(T(cx + cw + gap / 2, ly_hi - 8, "wait", 9, AMBER[0], MONO, anchor="middle"))

    x, y, w, h = 24, 726, 1632, 150
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 3, "Totals", PURPLE, "FLOW EFFICIENCY = WORK TIME / LEAD TIME"))
    tw = (w - 36 - 4 * 16) / 5
    for i, (f, hint) in enumerate([("Lead time", "first step to last"), ("Work time", "sum of all steps"),
                                   ("Flow efficiency", "work / lead × 100"), ("Biggest wait", "where and how long"),
                                   ("Most rework", "lowest % C&A")]):
        cx = x + 18 + i * (tw + 16)
        b.append(T(cx, y + 80, f, 13, d, weight=600))
        b.append(T(cx, y + 98, hint, 9.5, d, italic=True, op=".88"))
        b.append(L(cx, y + 130, cx + tw, y + 130, WRITE))

    y, h = 890, 170
    x, w = 24, 1082
    d = FOREST[0]
    b.append(panel(x, y, w, h, 4, "Future State Ideas", FOREST, "REMOVE WAITS · REDUCE HAND-OFFS · BUILD QUALITY IN"))
    b.append(sticky_zone(x + 10, y + 64, w - 20, h - 76, d, chips=(GREEN, YELLOW)))

    x, w = 1120, 536
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 5, "Improvement Plan", EMERALD))
    b.append(table(x + 18, y + 80, [("Change", 260), ("Owner", 110), ("Check on", w - 36 - 370)], 2, d, 30))

    b.append(footer("Where does work wait, and why?", "What would it take to halve the lead time?", FLOW_TAG))
    write_board("value-stream-map-board", "Value Stream Map",
                "A3 landscape value stream map: scope, six process steps with wait triangles and a timeline ladder, totals "
                "including flow efficiency, future state ideas, and an improvement plan.", "\n".join(b))


# ---------------------------------------------------------------- blameless incident review

def build_incident_review():
    b = [header("Blameless Incident Review",
                "Learn from an incident without blame: what happened, why it made sense at the time, and how to make it less likely.",
                "Improve · Blameless Post-Incident Review · Learning from Incidents · Systems, Not People",
                header_fields(["Incident", "Review date"]))]

    y, h = 148, 170
    x, w = 24, 1082
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "Summary", SLATE, "FACTS ONLY"))
    hw = (w - 54) / 2
    for i, f in enumerate(["What happened:", "Impact (who, how long):"]):
        b.append(field(x + 18, y + 86 + i * 36, f, x + 18 + hw, d))
    for i, f in enumerate(["Detected by / how:", "Duration to recover:"]):
        b.append(field(x + 36 + hw, y + 86 + i * 36, f, x + w - 18, d))
    b.append(T(x + 18, y + 152, "Severity:", 11, d, weight=600))
    for j, lab in enumerate(["1 · critical", "2 · major", "3 · minor", "4 · near miss"]):
        b.append(checkbox(x + 100 + j * 140, y + 152, lab, d, 10.5))

    x, w = 1120, 536
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Ground Rules", PURPLE, "READ ALOUD AT THE START"))
    for i, m in enumerate(["We look at systems, not at who to blame", "People did what made sense with what they knew",
                           "Curiosity over judgement: ask “how”, not “who”", "What we learn is shared openly"]):
        b.append(checkbox(x + 18, y + 84 + i * 24, m, d, 10.5))

    x, y, w, h = 24, 332, 1632, 290
    d = BLUE[0]
    b.append(panel(x, y, w, h, 3, "Timeline", BLUE, "WHAT DID PEOPLE KNOW AT EACH POINT?"))
    b.append(table(x + 18, y + 84, [("Time", 120), ("What happened", 520), ("What we knew then", 420), ("What we did and why", w - 36 - 1060)], 5, d, 36))

    y, h = 636, 280
    x, w = 24, 1082
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 4, "Contributing Factors", ORANGE, "USUALLY SEVERAL · RARELY ONE ROOT CAUSE"))
    cats = ["Technology", "Process", "Knowledge", "Environment", "Communication"]
    cw = (w - 20 - 4 * 8) / 5
    for i, c in enumerate(cats):
        cx = x + 10 + i * (cw + 8)
        b.append(T(cx + 6, y + 80, c, 12, d, weight=600))
        b.append(sticky_zone(cx, y + 90, cw, h - 102, d, "Stickies", chips=(PINK_ST,)))

    x, w = 1120, 262
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 5, "What Helped", EMERALD))
    b.append(sticky_zone(x + 10, y + 64, w - 20, h - 76, d, "Stickies", chips=(GREEN,)))
    x = 1394
    d = AMBER[0]
    b.append(panel(x, y, w, h, 6, "Where We Got Lucky", AMBER))
    b.append(sticky_zone(x + 10, y + 64, w - 20, h - 76, d, "Stickies", chips=(YELLOW,)))

    x, y, w, h = 24, 930, 1632, 130
    d = FOREST[0]
    b.append(panel(x, y, w, h, 7, "Follow-up Actions", FOREST, "PREVENT · DETECT SOONER · RECOVER FASTER"))
    b.append(table(x + 18, y + 76, [("Action", 640), ("Type: prevent / detect / recover", 340), ("Owner", 260), ("Due", w - 36 - 1240)], 1, d, 34))

    b.append(footer("Why did it make sense to them at the time?",
                    "What would make the next incident less likely, or easier to recover from?", FOOT_TAG))
    write_board("incident-review-board", "Blameless Incident Review",
                "A3 landscape blameless incident review: summary and severity, ground rules, a timeline of what people knew, "
                "contributing factors, what helped, where we got lucky, and follow-up actions.", "\n".join(b))


# ---------------------------------------------------------------- RACI & decision log

def build_raci():
    b = [header("RACI & Decision Log",
                "Agree who does, owns, advises on and hears about each piece of work, and keep a record of key decisions.",
                "Run a Project · Responsibility Assignment (RACI) · Decision Log · One Accountable Person",
                header_fields(["Project", "Date"]))]

    x, y, w, h = 24, 148, 1632, 470
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "RACI Matrix", BLUE, "R RESPONSIBLE · A ACCOUNTABLE (ONE ONLY) · C CONSULTED · I INFORMED"))
    gx0, gy = x + 18, y + 70
    act_w, nrole = 380, 8
    rw = (w - 36 - act_w) / nrole
    b.append(T(gx0 + 6, gy + 32, "WORK, DELIVERABLE OR DECISION", 9, d, MONO, weight=600, ls=".1em"))
    for i in range(nrole):
        cx = gx0 + act_w + i * rw
        b.append(R(cx + 3, gy, rw - 6, 46, "white", 4, f' stroke="{d}" stroke-opacity=".25"'))
        b.append(T(cx + 10, gy + 16, f"ROLE {i + 1}", 8.5, d, MONO, op=".88", ls=".1em"))
        b.append(L(cx + 10, gy + 36, cx + rw - 10, gy + 36, WRITE, 1))
    rows = 8
    rh = (h - 70 - 54 - 12) / rows
    for r in range(rows):
        ry = gy + 54 + r * rh
        b.append(R(gx0, ry, act_w - 6, rh - 5, "white", 4, f' stroke="{d}" stroke-opacity=".15"'))
        b.append(L(gx0 + 10, ry + rh - 15, gx0 + act_w - 18, ry + rh - 15, WRITE, 1))
        for i in range(nrole):
            cx = gx0 + act_w + i * rw
            b.append(R(cx + 3, ry, rw - 6, rh - 5, "white", 4, f' fill-opacity=".55" stroke="{d}" stroke-opacity=".12"'))

    x, y, w, h = 24, 632, 1632, 110
    d = AMBER[0]
    b.append(panel(x, y, w, h, 2, "Check the Matrix", AMBER))
    for i, m in enumerate(["Exactly one A in every row", "Every row has at least one R", "Few Cs: each one slows a decision",
                           "No one is R for everything", "The people named have agreed"]):
        b.append(checkbox(x + 18 + i * 322, y + 84, m, d, 11))

    x, y, w, h = 24, 756, 1632, 304
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 3, "Decision Log", PURPLE, "WHAT WE DECIDED, WHY, AND WHEN TO REVISIT"))
    b.append(table(x + 18, y + 84, [("#", 40), ("Date", 100), ("Decision", 380), ("Options considered", 340), ("Why", 360),
                                    ("Decided by", 170), ("Revisit when", w - 36 - 1390)], 5, d, 38))

    b.append(footer("Who is accountable for this, just one person?",
                    "Why did we decide that, and what would make us revisit it?", PROJECT_TAG))
    write_board("raci-decision-log-board", "RACI & Decision Log",
                "A3 landscape RACI matrix for eight roles and eight work items, a matrix check, and a decision log.",
                "\n".join(b))


# ---------------------------------------------------------------- persona & journey map

def build_persona_journey():
    b = [header("Persona & Journey Map",
                "Describe a real type of user, then map their journey: what they do, think and feel, and where to help.",
                "Envision & Plan · Personas · Customer Journey Mapping · Jobs to Be Done",
                legend([("sticky", YELLOW, "Yellow = Step"), ("sticky", BLUE_ST, "Blue = Thought"),
                        ("sticky", PINK_ST, "Pink = Pain point"), ("sticky", GREEN, "Green = Opportunity")]))]

    y, h = 148, 330
    x, w = 24, 534
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Persona", PURPLE, "BASED ON EVIDENCE, NOT GUESSES"))
    b.append(R(x + 18, y + 70, 120, 120, PURPLE[1], 8, f' stroke="{d}" stroke-opacity=".3" stroke-dasharray="5,4"'))
    b.append(T(x + 78, y + 136, "sketch", 10, d, italic=True, anchor="middle", op=".5"))
    for i, f in enumerate(["Name:", "Role / context:", "Tech comfort:"]):
        b.append(field(x + 156, y + 94 + i * 34, f, x + w - 18, d))
    for i, f in enumerate(["Goals:", "Frustrations:", "In their words:", "Evidence from:"]):
        b.append(field(x + 18, y + 218 + i * 30, f, x + w - 18, d))

    x, w = 572, 1084
    d = BLUE[0]
    b.append(panel(x, y, w, h, 2, "The Journey We're Mapping", BLUE))
    b.append(field(x + 18, y + 90, "Scenario or goal:", x + w - 18, d))
    b.append(field(x + 18, y + 128, "Starts when:", x + w / 2 - 10, d))
    b.append(field(x + w / 2 + 10, y + 128, "Ends when:", x + w - 18, d))
    b.append(T(x + 18, y + 176, "JOB TO BE DONE", 9, d, MONO, weight=600, ls=".12em"))
    for i, lead in enumerate(["When…", "I want to…", "so I can…"]):
        ly = y + 210 + i * 36
        b.append(T(x + 18, ly, lead, 17, d, SERIF, italic=True))
        b.append(L(x + 130, ly + 3, x + w - 18, ly + 3, d, 1, ' stroke-opacity=".25"'))

    x, y, w, h = 24, 492, 1632, 568
    d = SLATE[0]
    b.append(panel(x, y, w, h, 3, "Journey Map", SLATE, "STAGES LEFT TO RIGHT · ONE ROW AT A TIME"))
    lab_w, ns = 170, 5
    sw = (w - 28 - lab_w) / ns
    gx0, gy = x + 14, y + 64
    for i in range(ns):
        cx = gx0 + lab_w + i * sw
        b.append(R(cx + 3, gy, sw - 6, 34, d, 5))
        b.append(T(cx + 14, gy + 22, f"STAGE {i + 1}", 9, "white", MONO, weight=600, ls=".12em"))
        b.append(L(cx + 96, gy + 25, cx + sw - 16, gy + 25, "#94A3B8", 1))
    rows = [("Doing", "Steps they take", YELLOW, AMBER, 92), ("Thinking", "Questions, doubts", BLUE_ST, BLUE, 78),
            ("Feeling", "Highs and lows", None, PURPLE, 88), ("Pain points", "What goes wrong", PINK_ST, RED, 88),
            ("Opportunities", "How we could help", GREEN, FOREST, 88)]
    ry = gy + 42
    for name, sub, chip, col, rh in rows:
        dk, lt = col
        b.append(R(gx0, ry, lab_w - 8, rh - 6, lt, 5))
        b.append(T(gx0 + 12, ry + 24, name, 12, dk, weight=600))
        b.append(T(gx0 + 12, ry + 42, sub, 9.5, dk, op=".88"))
        if chip is None:
            mid = ry + (rh - 6) / 2
            b.append(R(gx0 + lab_w, ry, ns * sw, rh - 6, "white", 5, f' fill-opacity=".6" stroke="{dk}" stroke-opacity=".15"'))
            b.append(L(gx0 + lab_w + 30, mid, gx0 + lab_w + ns * sw - 10, mid, dk, 1, ' stroke-opacity=".3" stroke-dasharray="4,4"'))
            b.append(T(gx0 + lab_w + 10, ry + 18, "+", 13, dk, weight=600))
            b.append(T(gx0 + lab_w + 10, ry + rh - 14, "−", 13, dk, weight=600))
            b.append(T(gx0 + lab_w + ns * sw - 14, mid - 6, "draw the emotion line across the stages", 9.5, dk, italic=True, anchor="end", op=".5"))
        else:
            for i in range(ns):
                cx = gx0 + lab_w + i * sw
                b.append(R(cx + 3, ry, sw - 6, rh - 6, lt, 5, f' fill-opacity=".5" stroke="{dk}" stroke-opacity=".15"'))
                b.append(R(cx + 3, ry, sw - 6, rh - 6, "url(#dots)", 5))
        ry += rh

    b.append(footer("What is this person really trying to get done?",
                    "Where in the journey do we lose them, and why?", "Envision · Understand Users · Outcomes Over Output"))
    write_board("persona-journey-board", "Persona & Journey Map",
                "A3 landscape persona and customer journey map: a persona, the scenario and job to be done, and a five-stage "
                "journey with doing, thinking, feeling, pain points and opportunities.", "\n".join(b))


# ---------------------------------------------------------------- impact map

def build_impact_map():
    b = [header("Impact Map",
                "Connect a business goal to the people who can help or hinder it, the behaviour changes you need, and what to build.",
                "Envision & Plan · Inspired by Gojko Adzic's Impact Mapping · Why → Who → How → What",
                header_fields(["Initiative", "Date"]))]

    x, y, w, h = 24, 148, 1632, 762
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "The Map", PURPLE, "READ LEFT TO RIGHT · EVERY DELIVERABLE TRACES BACK TO THE GOAL"))
    cols = [("WHY · GOAL", 20, 290, EMERALD), ("WHO · ACTORS", 380, 320, BLUE), ("HOW · IMPACTS", 770, 380, ORANGE),
            ("WHAT · DELIVERABLES", 1220, 392, AMBER)]
    hints = ["The measurable business goal", "People who can help or get in the way", "How their behaviour needs to change",
             "Features or activities that could cause it"]
    for (lab, cx, cw, col), hint in zip(cols, hints):
        b.append(T(x + cx, y + 82, lab, 9.5, col[0], MONO, weight=600, ls=".12em"))
        b.append(T(x + cx, y + 98, hint, 9.5, col[0], italic=True, op=".88"))
    top, bot = y + 116, y + h - 16
    n = 6
    rowh = (bot - top) / n
    bh = 88
    imp_y = [top + rowh * (k + 0.5) - bh / 2 for k in range(n)]
    act_y = [(imp_y[2 * a] + imp_y[2 * a + 1]) / 2 for a in range(3)]
    goal_y = (top + bot) / 2 - 70
    gx, gw = x + 20, 290
    ax, aw = x + 380, 320
    ix, iw = x + 770, 380
    dx, dw = x + 1220, 392
    for a in range(3):
        b.append(L(gx + gw, goal_y + 70, ax, act_y[a] + bh / 2, d, 1.5, ' stroke-opacity=".4"'))
        for k in (2 * a, 2 * a + 1):
            b.append(L(ax + aw, act_y[a] + bh / 2, ix, imp_y[k] + bh / 2, d, 1.5, ' stroke-opacity=".4"'))
    for k in range(n):
        b.append(L(ix + iw, imp_y[k] + bh / 2, dx, imp_y[k] + bh / 2, d, 1.5, ' stroke-opacity=".4"'))
    b.append(R(gx, goal_y, gw, 140, EMERALD[1], 8, f' stroke="{EMERALD[0]}" stroke-opacity=".5" stroke-width="1.5"'))
    b.append(T(gx + 14, goal_y + 22, "GOAL", 8.5, EMERALD[0], MONO, weight=600, ls=".1em"))
    b.append(lines(gx + 14, goal_y + 50, gx + gw - 14, 2, 24))
    b.append(field(gx + 14, goal_y + 118, "Measure:", gx + gw - 14, EMERALD[0], 10.5))
    for a in range(3):
        b.append(wbox(ax, act_y[a], aw, bh, f"ACTOR {a + 1}", BLUE[0], 2, 24, BLUE[1]))
    for k in range(n):
        b.append(wbox(ix, imp_y[k], iw, bh, f"IMPACT {k + 1}", ORANGE[0], 2, 24, ORANGE[1]))
        b.append(wbox(dx, imp_y[k], dw, bh, f"DELIVERABLE {k + 1}", AMBER[0], 2, 24, AMBER[1]))

    y, h = 924, 136
    x, w = 24, 808
    d = RED[0]
    b.append(panel(x, y, w, h, 2, "Riskiest Assumption", RED))
    b.append(field(x + 18, y + 84, "The impact we're least sure of:", x + w - 18, d))
    b.append(field(x + 18, y + 116, "How we'll test it:", x + w - 18, d))

    x, w = 846, 810
    d = FOREST[0]
    b.append(panel(x, y, w, h, 3, "First Step", FOREST))
    b.append(field(x + 18, y + 84, "Deliverable to try first:", x + w - 18, d))
    b.append(field(x + 18, y + 116, "We'll know the impact happened when:", x + w - 18, d))

    b.append(footer("Whose behaviour has to change for us to reach this goal?",
                    "If we built only one thing, which impact would it move?", "Envision · Outcomes Over Output · Impact Mapping"))
    write_board("impact-map-board", "Impact Map",
                "A3 landscape impact map: goal and measure, three actors, six impacts, six deliverables, the riskiest "
                "assumption, and a first step.", "\n".join(b))


# ---------------------------------------------------------------- estimation

def build_estimation():
    b = [header("Estimation",
                "Size work together quickly with planning poker, T-shirt sizes or affinity estimation, or decide not to estimate.",
                "Iterate · Planning Poker · T-Shirt Sizing · Affinity Estimation · Relative, Not Absolute",
                header_fields(["Team", "Date"]))]

    y, h = 148, 330
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Planning Poker", PURPLE, "FOR A HANDFUL OF ITEMS"))
    cards = ["1", "2", "3", "5", "8", "13", "20", "?", "☕"]
    cwid = (w - 36 - 8 * 8) / 9
    for i, c in enumerate(cards):
        cx = x + 18 + i * (cwid + 8)
        b.append(R(cx, y + 66, cwid, 70, "white", 6, f' stroke="{d}" stroke-opacity=".4" stroke-width="1.5"'))
        b.append(T(cx + cwid / 2, y + 110, c, 22, d, SERIF, anchor="middle"))
    steps = ["Read the item", "Pick a card privately", "Reveal together", "Highest and lowest explain", "Re-vote, two rounds at most"]
    for i, s in enumerate(steps):
        sx = x + 18 + i * 156
        b.append(f'<circle cx="{sx + 9:g}" cy="{y + 164}" r="9" fill="{d}"/>')
        b.append(T(sx + 9, y + 168, str(i + 1), 9.5, "white", weight=600, anchor="middle"))
        b.append(T(sx + 24, y + 168, s, 10, d))
    b.append(table(x + 18, y + 206, [("Item", 400), ("Round 1", 110), ("Round 2", 110), ("Estimate", w - 36 - 620)], 3, d, 30))

    x, w = 846, 810
    d = BLUE[0]
    b.append(panel(x, y, w, h, 2, "T-Shirt Sizing", BLUE, "FOR MANY ITEMS, ROUGHLY"))
    sizes = ["XS", "S", "M", "L", "XL"]
    sw = (w - 20 - 4 * 10) / 5
    for i, sz in enumerate(sizes):
        cx = x + 10 + i * (sw + 10)
        b.append(T(cx + sw / 2, y + 88, sz, 20, d, SERIF, anchor="middle"))
        b.append(sticky_zone(cx, y + 100, sw, h - 150, d, "Items", chips=(YELLOW,)))
    b.append(field(x + 18, y + h - 22, "Reference item that is an “M”:", x + w - 18, d))

    y, h = 492, 400
    x, w = 24, 1082
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 3, "Affinity Estimation", ORANGE, "FOR A WHOLE BACKLOG IN AN HOUR"))
    b.append(bullets(x + 22, y + 74, ["Silently place items left to right, smallest to largest. Anyone can move any item.",
                                      "Then discuss items that keep moving, and draw size boundaries."], d))
    zy = y + 114
    b.append(sticky_zone(x + 10, zy, w - 20, h - 168, d, "Items, smallest on the left", chips=(YELLOW,)))
    b.append(L(x + 30, y + h - 34, x + w - 30, y + h - 34, d, 2))
    b.append(f'<path d="M{x + w - 30:g},{y + h - 40:g} L{x + w - 18:g},{y + h - 34:g} L{x + w - 30:g},{y + h - 28:g}" fill="{d}"/>')
    for i, lab in enumerate(["1", "2", "3", "5", "8", "13"]):
        tx = x + 60 + i * (w - 120) / 5
        b.append(L(tx, y + h - 40, tx, y + h - 28, d, 1.5))
        b.append(T(tx, y + h - 14, lab, 11, d, weight=600, anchor="middle"))
    b.append(T(x + 30, y + h - 44, "SMALLER", 8.5, d, MONO, ls=".12em"))
    b.append(T(x + w - 34, y + h - 44, "LARGER", 8.5, d, MONO, anchor="end", ls=".12em"))

    x, w = 1120, 536
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 4, "Reference Items", EMERALD, "SHARED EXAMPLES KEEP SIZES CONSISTENT"))
    b.append(table(x + 18, y + 84, [("Size", 70), ("Item everyone remembers", 260), ("Why this size", w - 36 - 330)], 6, d, 44))

    y, h = 906, 154
    x, w = 24, 1082
    d = SLATE[0]
    b.append(panel(x, y, w, h, 5, "Or Don't Estimate", SLATE, "COUNTING ITEMS OFTEN FORECASTS JUST AS WELL"))
    b.append(bullets(x + 22, y + 78, ["If items are split small enough to finish within your SLE, count them instead of sizing them.",
                                      "Forecast from throughput with the Release Forecast board."], d))
    b.append(checkbox(x + 18, y + 136, "We'll try counting items instead of estimating for", d, 11))
    b.append(L(x + 350, y + 139, x + 420, y + 139, d, 1, ' stroke-opacity=".4"'))
    b.append(T(x + 428, y + 136, "iterations, then compare", 11, d))

    x, w = 1120, 536
    d = RED[0]
    b.append(panel(x, y, w, h, 6, "Ground Rules", RED))
    for i, m in enumerate(["Estimates belong to the people doing the work", "An estimate is a forecast, not a promise",
                           "Never compare points between teams"]):
        b.append(checkbox(x + 18, y + 82 + i * 26, m, d, 11))

    b.append(footer("Is this bigger or smaller than the last thing we finished?",
                    "Do we need a number, or do we just need to know it's small?", "Iterate · Relative Sizing · Forecast, Don't Promise"))
    write_board("estimation-board", "Estimation",
                "A3 landscape estimation board: planning poker cards and steps, T-shirt sizing columns, an affinity "
                "estimation wall, reference items, the option not to estimate, and ground rules.", "\n".join(b))


# ---------------------------------------------------------------- facilitation techniques poster

TECHNIQUES = [
    ("Check-in", SLATE, ["Start: help everyone arrive", "and speak once early."],
     ["Ask one light question", "Go round, a sentence each", "No discussion yet"], "Voices heard early speak up later."),
    ("Silent Writing", PURPLE, ["Before discussing, so ideas", "aren't shaped by the loudest."],
     ["Pose one clear question", "Everyone writes alone, 3–5 min", "One idea per sticky"], "Quiet people contribute as much as anyone."),
    ("Think · Pair · Share", BLUE, ["To deepen ideas before the", "whole group hears them."],
     ["Think alone for a minute", "Discuss in pairs", "Pairs share with the group"], "Pairs filter and strengthen ideas fast."),
    ("Round-Robin", SKY, ["When a few voices dominate,", "or you need every view."],
     ["Go round in order", "Each person speaks briefly", "“Pass” is always allowed"], "Equal airtime, without putting people on the spot."),
    ("Affinity Clustering", EMERALD, ["To make sense of many", "ideas quickly."],
     ["Put all stickies up", "Move similar ones together, silently", "Name each cluster"], "Silent moving avoids arguments about wording."),
    ("Dot Voting", ORANGE, ["To prioritise a list in", "minutes."],
     ["Give each person 3 dots", "Vote at the same time", "Count, then discuss the top items"], "Vote together, so no one follows the leader."),
    ("Fist of Five", FOREST, ["To check support for a", "proposal or plan."],
     ["Everyone shows 0–5 fingers", "Ask the lowest votes what's missing", "Adjust and re-vote"], "Low votes are information, not obstruction."),
    ("Agreement Scale", AMBER, ["To show how far people", "really support a decision."],
     ["Offer a 1–5 or 1–8 scale", "From “fully support” to “block”", "Discuss the spread"], "Shows lukewarm support that a yes/no vote hides."),
    ("Timeboxing", RED, ["For any activity that could", "run on forever."],
     ["Agree the time up front", "Show a visible timer", "At zero, decide: stop or extend"], "Ending on time builds trust in the process."),
    ("Parking Lot", SLATE, ["When a useful topic is off", "the current agenda."],
     ["Write it on the parking lot", "Move on", "Review it before closing"], "Respects the idea without derailing the session."),
    ("Fishbowl", PURPLE, ["For a big group to hear a", "small, focused conversation."],
     ["A few people talk in an inner circle", "Others listen around them", "Leave an empty chair to join"], "Lets a large group follow a real dialogue."),
    ("Check-out", BLUE, ["End: capture value and", "close the session well."],
     ["Each person says one takeaway", "Optional: rate the session 1–5", "Thank everyone"], "A score of 1–5 for time well spent tells you what to change."),
]


def build_facilitation_poster():
    b = [header("Facilitation Techniques",
                "Twelve simple techniques for better group conversations, plus tips for remote and hybrid sessions.",
                "Facilitate · Include Every Voice · Diverge, Then Converge · Remote & Hybrid",
                header_fields(["Session", "Facilitator"]))]
    cw = (1632 - 3 * 12) / 4
    ch = 252
    for i, (name, col, when, how, tip) in enumerate(TECHNIQUES):
        r, c = divmod(i, 4)
        x, y = 24 + c * (cw + 12), 148 + r * (ch + 12)
        dk, lt = col
        b.append(R(x, y, cw, ch, lt, 10, f' stroke="{dk}" stroke-opacity=".2" stroke-width="1.5" filter="url(#fc)"'))
        b.append(top_round(x, y, cw, 44, 10, dk))
        b.append(f'<circle cx="{x + 22}" cy="{y + 22}" r="11" fill="white" fill-opacity=".2"/>')
        b.append(T(x + 22, y + 26, str(i + 1), 10, "white", weight=600, anchor="middle"))
        b.append(T(x + 42, y + 28, name, 14, "white", weight=600))
        b.append(T(x + 18, y + 66, "WHEN", 8.5, dk, MONO, weight=600, ls=".12em"))
        b.append(para(x + 18, y + 84, when, 11, dk, 15))
        b.append(T(x + 18, y + 124, "HOW", 8.5, dk, MONO, weight=600, ls=".12em"))
        for j, s in enumerate(how):
            b.append(T(x + 18, y + 144 + j * 17, f"{j + 1}.", 10.5, dk, weight=600))
            b.append(T(x + 34, y + 144 + j * 17, s, 10.5, INK))
        b.append(L(x + 18, y + 206, x + cw - 18, y + 206, dk, 1, ' stroke-opacity=".2"'))
        b.append(T(x + 18, y + 228, tip, 10.5, dk, italic=True))

    y = 940
    b.append(R(24, y, 1632, 120, NAVY, 10))
    b.append(R(24, y, 6, 120, ACCENT, 3))
    b.append(T(48, y + 30, "REMOTE & HYBRID", 9.5, ACCENT, MONO, weight=600, ls=".14em"))
    tips = [("One shared board", "Everyone works in it, not just the facilitator."),
            ("Everyone on their own device", "In hybrid sessions, room and remote are equal."),
            ("Use chat for silent writing", "Then paste ideas onto the board."),
            ("Name the roles", "Facilitator, timekeeper, scribe, tech help."),
            ("Break every 50 minutes", "Screens tire people faster than rooms."),
            ("Cameras optional", "Ask for voices and participation, not faces.")]
    tw = (1632 - 48) / 3
    for i, (t, s) in enumerate(tips):
        r, c = divmod(i, 3)
        tx = 48 + c * tw
        ty = y + 60 + r * 34
        b.append(T(tx, ty, t, 12, "white", weight=600))
        b.append(T(tx + text_w(t, 12) + 14, ty, s, 11, "#94A3B8"))

    b.append(footer("Who hasn't spoken yet, and how could we make it easy for them?",
                    "Are we still exploring, or is it time to decide?", "Facilitate · Include Every Voice · Diverge, Then Converge"))
    write_board("facilitation-techniques-poster", "Facilitation Techniques",
                "A3 landscape reference poster: twelve facilitation techniques, each with when to use it, how to run it and a "
                "tip, plus remote and hybrid facilitation tips.", "\n".join(b))


# ---------------------------------------------------------------- architecture decision record

def build_adr():
    b = [header("Architecture Decision Record",
                "Record an important technical decision: its context, the options you considered, what you chose, and the trade-offs.",
                "Manage Flow · Inspired by Michael Nygard's ADR Format · Decisions Worth Remembering",
                header_fields(["ADR number", "Date"]))]

    x, y, w, h = 24, 148, 1632, 130
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "Title & Status", SLATE, "ONE DECISION PER RECORD"))
    b.append(field(x + 18, y + 88, "Title (short, e.g. “Use event queues for order updates”):", x + 1000, d))
    b.append(field(x + 1030, y + 88, "Deciders:", x + w - 18, d))
    b.append(T(x + 18, y + 118, "Status:", 11, d, weight=600))
    for j, lab in enumerate(["Proposed", "Accepted", "Rejected", "Deprecated", "Superseded by ADR #"]):
        b.append(checkbox(x + 90 + j * 150, y + 118, lab, d, 10.5))
    b.append(L(x + 90 + 4 * 150 + 160, y + 121, x + 90 + 4 * 150 + 220, y + 121, d, 1, ' stroke-opacity=".4"'))

    y, h = 292, 300
    x, w = 24, 808
    d = BLUE[0]
    b.append(panel(x, y, w, h, 2, "Context", BLUE, "WHAT FORCES ARE AT PLAY?"))
    b.append(T(x + 18, y + 80, "The problem, the constraints, and why a decision is needed now", 10.5, d, italic=True, op=".88"))
    b.append(lines(x + 18, y + 112, x + w - 18, 7, 26))

    x, w = 846, 810
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 3, "Decision Drivers", PURPLE, "WHAT MATTERS MOST"))
    b.append(T(x + 18, y + 80, "e.g. cost, performance, team skills, time to market, security, reversibility", 10.5, d, italic=True, op=".88"))
    b.append(check_lines(x + 18, y + 116, x + w - 18, 6, d, 28))

    x, y, w, h = 24, 606, 1632, 290
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 4, "Options Considered", ORANGE, "AT LEAST TWO, INCLUDING “DO NOTHING”"))
    b.append(table(x + 18, y + 84, [("Option", 300), ("Pros", 440), ("Cons", 440), ("Effort / cost", 220),
                                    ("Chosen?", w - 36 - 1400)], 4, d, 44))

    y, h = 910, 150
    x, w = 24, 808
    d = FOREST[0]
    b.append(panel(x, y, w, h, 5, "Decision", FOREST))
    b.append(T(x + 18, y + 86, "We will…", 18, d, SERIF, italic=True))
    b.append(L(x + 110, y + 89, x + w - 18, y + 89, d, 1, ' stroke-opacity=".25"'))
    b.append(L(x + 18, y + 124, x + w - 18, y + 124, d, 1, ' stroke-opacity=".25"'))

    x, w = 846, 810
    d = AMBER[0]
    b.append(panel(x, y, w, h, 6, "Consequences", AMBER, "WHAT BECOMES EASIER, AND HARDER"))
    hw = (w - 54) / 2
    for i, (lab, col) in enumerate([("Easier / good", EMERALD[0]), ("Harder / trade-offs", RED[0])]):
        cx = x + 18 + i * (hw + 18)
        b.append(T(cx, y + 80, lab, 11, col, weight=600))
        b.append(lines(cx, y + 106, cx + hw, 2, 26))

    b.append(footer("Will someone joining next year understand why we did this?",
                    "What would make us revisit this decision?", FLOW_TAG))
    write_board("adr-board", "Architecture Decision Record",
                "A3 landscape architecture decision record: title and status, context, decision drivers, options considered, "
                "the decision, and its consequences.", "\n".join(b))


# ---------------------------------------------------------------- team launch (sprint zero)

LAUNCH = [
    ("Why & What", PURPLE, [("Purpose and problem agreed", "Project Kickoff"), ("Product vision written", "Product Vision Board"),
                            ("Users understood", "Persona & Journey Map"), ("Outcomes and measures", "Impact Map · OKRs"),
                            ("Stakeholders mapped", "Stakeholder Map")]),
    ("The Team", BLUE, [("Charter and working agreements", "Team Charter"), ("Roles and accountability clear", "RACI & Decision Log"),
                        ("Skills and gaps known", "Skills Matrix"), ("AI use agreed", "AI Working Agreement"),
                        ("Decision rights agreed", "Delegation Board")]),
    ("The Backlog", EMERALD, [("Journey and first release slice", "User Story Map"), ("Epic shaped, with an MVP", "Epic Breakdown Canvas"),
                              ("Items right-sized", "Story Splitting · Backlog Item Anatomy"), ("Top items understood", "Example Mapping"),
                              ("First forecast range", "Release Forecast")]),
    ("Ways of Working", ORANGE, [("Board, workflow and WIP limits", "Kanban Board Design"), ("Definition of Done agreed", "Team Charter"),
                                 ("Cadence and events booked", "Sprint Planning · Review · Retro"), ("Risks named and owned", "Pre-mortem · RAID Log"),
                                 ("First retro booked", "Retrospective Kit")]),
]


def build_team_launch():
    b = [header("Team Launch",
                "Get a new team or initiative ready to deliver in one or two weeks, and deliver something real while you do it.",
                "Set Up the Team · Often Called Sprint Zero or Iteration 0 · Timeboxed · Thin First Slice",
                header_fields(["Team", "Launch dates"]))]

    y, h = 148, 140
    x, w = 24, 1082
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Launch Goal", PURPLE, "THE LAUNCH IS DONE WHEN…"))
    b.append(T(x + 18, y + 94, "We'll start delivering by", 20, d, SERIF, italic=True))
    b.append(L(x + 262, y + 97, x + 470, y + 97, d, 1.2, ' stroke-opacity=".4"'))
    b.append(T(x + 480, y + 94, "and by then we will have:", 20, d, SERIF, italic=True))
    b.append(L(x + 18, y + 126, x + w - 18, y + 126, d, 1, ' stroke-opacity=".25"'))

    x, w = 1120, 536
    d = SLATE[0]
    b.append(panel(x, y, w, h, 2, "Timebox", SLATE, "SHORT ON PURPOSE"))
    for j, lab in enumerate(["1 week", "2 weeks", "Other:"]):
        b.append(checkbox(x + 18 + j * 110, y + 84, lab, d, 11))
    b.append(L(x + 18 + 2 * 110 + 76, y + 87, x + w - 18, y + 87, WRITE))
    b.append(field(x + 18, y + 118, "Launch owner:", x + w / 2 - 10, d))
    b.append(field(x + w / 2 + 10, y + 118, "Daily check-in at:", x + w - 18, d))

    x, y, w, h = 24, 302, 1632, 470
    b.append(panel(x, y, w, h, 3, "Launch Checklist", BLUE, "TICK WHEN DONE · EACH ITEM LINKS TO A TOOL · DO JUST ENOUGH"))
    cw = (w - 28 - 3 * 12) / 4
    for i, (group, col, items) in enumerate(LAUNCH):
        cx = x + 14 + i * (cw + 12)
        dk, lt = col
        b.append(R(cx, y + 64, cw, h - 78, lt, 6, f' stroke="{dk}" stroke-opacity=".2"'))
        b.append(T(cx + 14, y + 90, group, 14, dk, weight=600))
        for j, (item, tool) in enumerate(items):
            iy = y + 128 + j * 66
            b.append(R(cx + 14, iy - 11, 13, 13, "white", 2, f' stroke="{dk}" stroke-opacity=".6" stroke-width="1.2"'))
            b.append(T(cx + 36, iy, item, 11.5, INK, weight=500))
            b.append(T(cx + 36, iy + 17, "→ " + tool, 9.5, dk, MONO, op=".88"))
            b.append(field(cx + 36, iy + 40, "Owner:", cx + cw - 14, dk, 10))

    y, h = 786, 274
    x, w = 24, 534
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 4, "Thin First Slice", EMERALD, "DELIVER SOMETHING REAL"))
    b.append(T(x + 18, y + 80, "However small, finish something a user could see or use.", 10.5, d, italic=True, op=".88"))
    for i, f in enumerate(["Slice:", "Who it's for:", "Done when:"]):
        b.append(field(x + 18, y + 116 + i * 36, f, x + w - 18, d))
    b.append(checkbox(x + 18, y + 240, "It runs end to end, from input to output (a walking skeleton)", d, 10.5))

    x = 572
    d = SKY[0]
    b.append(panel(x, y, w, h, 5, "Environment & Tools", SKY, "EVERYONE CAN WORK ON DAY ONE"))
    for i, m in enumerate(["Code repository and access for everyone", "Build and deploy pipeline to a test environment",
                           "Team board set up in the team's tool", "Shared channel, calendar and document space",
                           "Development setup works on every machine", "Test data and environments available"]):
        b.append(checkbox(x + 18, y + 86 + i * 30, m, d, 11))

    x, w = 1120, 536
    d = RED[0]
    b.append(panel(x, y, w, h, 6, "Ready to Start?", RED, "THE EXIT CHECK"))
    for i, m in enumerate(["Vision and first outcome agreed", "Top of the backlog ready for 1–2 iterations",
                           "Definition of Done agreed", "First slice planned or already done",
                           "Everyone can contribute from day one"]):
        b.append(checkbox(x + 18, y + 86 + i * 28, m, d, 11))
    b.append(R(x + 14, y + 222, w - 28, 40, RED[1], 6, f' stroke="{d}" stroke-opacity=".3"'))
    b.append(T(x + 26, y + 247, "Watch for: running past the timebox · designing everything up front · delivering nothing",
               9.5, d, italic=True))

    b.append(footer("What's the least we need to agree before we can start delivering?",
                    "What could we deliver this week, however small?", "Set Up the Team · Team Launch · Start Small, Start Now"))
    write_board("team-launch-board", "Team Launch",
                "A3 landscape team launch (Sprint Zero) board: launch goal and timebox, a 20-item launch checklist linking to "
                "toolkit tools, a thin first slice, environment and tools, and a ready-to-start exit check.", "\n".join(b))


# ---------------------------------------------------------------- daily sync

EVENTS_TAG = "Run Events · Inspect & Adapt · Short, Regular, Purposeful"


def build_daily_sync():
    b = [header("Daily Sync",
                "A short daily check on progress toward the goal: walk the board, raise blockers, and plan the day together.",
                "Run Events · Daily Scrum · Stand-up · Kanban Meeting · 15 Minutes",
                header_fields(["Team", "Time & place"]))]

    y, h = 148, 140
    x, w = 24, 1082
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Our Goal", PURPLE, "EVERY CONVERSATION POINTS HERE"))
    b.append(T(x + 18, y + 94, "We're working toward", 20, d, SERIF, italic=True))
    b.append(L(x + 228, y + 97, x + w - 200, y + 97, d, 1, ' stroke-opacity=".25"'))
    b.append(field(x + w - 186, y + 94, "Days left:", x + w - 18, d))
    b.append(T(x + 18, y + 126, "Sprint goal, iteration goal, or the outcome the team is focused on this week", 10.5, d, italic=True, op=".88"))

    x, w = 1120, 536
    d = SLATE[0]
    b.append(panel(x, y, w, h, 2, "Ground Rules", SLATE))
    for i, m in enumerate(["15 minutes, same time, same place", "For the team, not a status report",
                           "Details go to the parking lot"]):
        b.append(checkbox(x + 18, y + 80 + i * 24, m, d, 10.5))

    x, y, w, h = 24, 302, 1082, 420
    d = BLUE[0]
    b.append(panel(x, y, w, h, 3, "Walk the Board", BLUE, "RIGHT TO LEFT · FINISH BEFORE YOU START"))
    steps = ["What's nearly done, and what's needed to finish it?", "What's blocked or getting old? Who can help?",
             "What will we finish today?", "Only then: what should we start?"]
    for i, st in enumerate(steps):
        sx = x + 18 + (i % 2) * 520
        sy = y + 82 + (i // 2) * 26
        b.append(f'<circle cx="{sx + 9}" cy="{sy - 4}" r="9" fill="{d}"/>')
        b.append(T(sx + 9, sy, str(i + 1), 9.5, "white", weight=600, anchor="middle"))
        b.append(T(sx + 26, sy, st, 11, d))
    cols = ["Ready", "In progress", "Review / test", "Done"]
    cw = (w - 20 - 3 * 10) / 4
    zy = y + 150
    for i, c in enumerate(cols):
        cx = x + 10 + i * (cw + 10)
        b.append(T(cx + 6, zy - 8, c.upper(), 9, d, MONO, weight=600, ls=".12em"))
        b.append(sticky_zone(cx, zy, cw, h - 162, d, "Work items", chips=(YELLOW, PINK_ST)))
    ay = y + 130
    b.append(L(x + w - 40, ay, x + 40, ay, ACCENT, 2))
    b.append(f'<path d="M{x + 52},{ay - 6} L{x + 40},{ay} L{x + 52},{ay + 6}" fill="{ACCENT}"/>')
    b.append(T(x + w / 2, ay - 6, "WALK THIS WAY", 8.5, ACCENT, MONO, weight=600, anchor="middle", ls=".14em"))

    x, w = 1120, 536
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 4, "Questions to Ask", EMERALD, "ABOUT THE WORK, NOT THE PEOPLE"))
    b.append(T(x + 18, y + 82, "For each item on the board", 11, d, weight=600))
    for i, q in enumerate(["What's needed to finish this?", "Is anything blocking it?", "Who can help, today?",
                           "Is it older than our SLE?"]):
        b.append(T(x + 30, y + 108 + i * 24, q, 15, d, SERIF, italic=True))
    b.append(T(x + 18, y + 226, "The classic three questions", 11, d, weight=600))
    for i, q in enumerate(["What did I do yesterday toward the goal?", "What will I do today toward the goal?",
                           "Do I see anything in the way?"]):
        b.append(T(x + 30, y + 252 + i * 24, q, 15, d, SERIF, italic=True))
    b.append(para(x + 18, y + 346, ["Useful, but easily becomes a status report.", "The Scrum Guide no longer requires them."],
                  10, d, 14, italic=True, op=".88"))

    y, h = 736, 324
    x, w = 24, 534
    d = RED[0]
    b.append(panel(x, y, w, h, 5, "Blockers & Swarms", RED, "ACT TODAY"))
    b.append(table(x + 18, y + 84, [("Item", 160), ("Blocked by", 160), ("Swarm?", 70), ("Who", w - 36 - 390)], 5, d, 40))

    x = 572
    d = AMBER[0]
    b.append(panel(x, y, w, h, 6, "Parking Lot", AMBER, "AFTER THE SYNC"))
    b.append(bullets(x + 22, y + 74, ["Topics that need more than a minute", "Note who stays to discuss"], d))
    b.append(dashed(x + 10, x + w - 10, y + 110, d))
    b.append(sticky_zone(x + 10, y + 116, w - 20, h - 128, d, chips=(YELLOW,)))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 7, "Sync Health Check", FOREST, "ONCE A WEEK"))
    for i, m in enumerate(["Finished within 15 minutes", "Talked about the goal, not just activity",
                           "Oldest and blocked items discussed first", "Every blocker has an owner",
                           "We know what we'll finish today", "Everyone could take part"]):
        b.append(checkbox(x + 18, y + 86 + i * 30, m, d, 11))
    b.append(field(x + 18, y + 284, "If a check fails, we'll try:", x + w - 18, d))

    b.append(footer("What will we finish today?", "Who needs help, and who can give it?", EVENTS_TAG))
    write_board("daily-sync-board", "Daily Sync",
                "A3 landscape daily sync board: the goal, ground rules, a walk-the-board area read right to left, questions "
                "to ask, blockers and swarms, a parking lot, and a weekly sync health check.", "\n".join(b))


# ---------------------------------------------------------------- backlog refinement

def build_backlog_refinement():
    b = [header("Backlog Refinement",
                "Get the next few items ordered, understood, split, sized and ready, in one focused session.",
                "Run Events · Backlog Refinement · Order → Understand → Split → Example → Size → Ready",
                header_fields(["Team", "Date"]))]

    x, y, w, h = 24, 148, 1632, 124
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "Session Goal", SLATE, "REFINE JUST ENOUGH, JUST IN TIME"))
    tw = (w - 36 - 2 * 16) / 3
    for i, f in enumerate(["Items to refine:", "Ready for (iteration or date):", "Who's here:"]):
        cx = x + 18 + i * (tw + 16)
        b.append(field(cx, y + 92, f, cx + tw, d))

    x, y, w, h = 24, 286, 1632, 476
    b.append(panel(x, y, w, h, 2, "Refinement Flow", BLUE, "FOR EACH ITEM, IN ORDER · STOP WHEN IT'S READY"))
    b.append(step_cards(x + 14, y + 66, w - 28, h - 80, [
        ("Order", ["Is this still the most", "valuable next item?", "→ Prioritisation Board"]),
        ("Understand", ["Who is it for, and why?", "What does done look like?", "→ Backlog Item Anatomy"]),
        ("Split", ["Can we finish it in a few", "days? If not, slice it.", "→ Story Splitting"]),
        ("Examples", ["Rules, examples and", "open questions.", "→ Example Mapping"]),
        ("Size", ["Roughly how big, compared", "with things we've done?", "→ Estimation"]),
        ("Ready?", ["Check it against our", "Definition of Ready.", "→ panel 4, below"])], BLUE))

    y, h = 776, 284
    x, w = 24, 1082
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 3, "Items Refined", EMERALD))
    b.append(table(x + 18, y + 84, [("Item", 250), ("Split into", 220), ("Examples agreed", 140), ("Size", 80),
                                    ("Ready?", 80), ("Open questions & owner", w - 36 - 770)], 5, d, 36))

    x, w = 1120, 536
    d = AMBER[0]
    b.append(panel(x, y, w, h, 4, "Definition of Ready", AMBER, "A GUIDE, NOT A GATE"))
    for i, m in enumerate(["Who it's for and why is clear", "Small enough to finish in a few days",
                           "Examples or acceptance criteria agreed", "Dependencies known and handled",
                           "No open question that would stop work"]):
        b.append(checkbox(x + 18, y + 86 + i * 30, m, d, 11))
    b.append(field(x + 18, y + 248, "Next refinement:", x + w - 18, d))

    b.append(footer("Which items do we need ready for the next iteration?",
                    "What don't we know yet that would stop us starting?", EVENTS_TAG))
    write_board("backlog-refinement-board", "Backlog Refinement",
                "A3 landscape backlog refinement board: session goal, a six-step flow (order, understand, split, examples, "
                "size, ready) linked to the toolkit, an items-refined table, and a Definition of Ready check.", "\n".join(b))


# ---------------------------------------------------------------- kanban cadences

CADENCES = [
    ("Daily Kanban Meeting", BLUE, "Daily · 15 min", ["Walk the board, unblock work,", "decide what to finish today."]),
    ("Replenishment", PURPLE, "Weekly · 30–60 min", ["Choose which options to pull", "into the system next."]),
    ("Delivery Planning", EMERALD, "Per delivery · 30 min", ["Decide what's ready to hand", "over to customers, and when."]),
    ("Service Delivery Review", ORANGE, "Every 2 weeks · 45 min", ["Check flow and service levels", "against what customers expect."]),
    ("Operations Review", SKY, "Monthly · 60 min", ["Look across services for", "shared problems and capacity."]),
    ("Risk Review", RED, "Monthly · 30 min", ["Review blockers and risks", "that threaten delivery."]),
    ("Strategy Review", FOREST, "Quarterly · 1–2 h", ["Check direction, services and", "investment still fit the goals."]),
    ("Our Own Cadence", SLATE, "", ["Add a review your team needs.", ""]),
]


def build_kanban_cadences():
    b = [header("Kanban Cadences",
                "Set a rhythm of short, focused meetings that keep work flowing and services improving, with or without iterations.",
                "Manage Flow · Inspired by the Kanban Method (David J. Anderson) · Feedback Loops · Replenishment",
                header_fields(["Team / service", "Date"]))]

    x, y, w, h = 24, 148, 1632, 430
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Our Cadences", BLUE, "TYPICAL TIMINGS SHOWN · ADAPT TO YOUR CONTEXT · TICK THE ONES YOU'LL RUN"))
    cw = (w - 28 - 3 * 12) / 4
    ch = (h - 78 - 12) / 2
    for i, (name, col, when, purpose) in enumerate(CADENCES):
        r, c = divmod(i, 4)
        cx, cy = x + 14 + c * (cw + 12), y + 64 + r * (ch + 12)
        dk, lt = col
        b.append(R(cx, cy, cw, ch, "white", 6, f' stroke="{dk}" stroke-opacity=".3"'))
        b.append(R(cx, cy, 5, ch, dk, 3))
        b.append(R(cx + 18, cy + 14, 13, 13, "white", 2, f' stroke="{dk}" stroke-opacity=".6" stroke-width="1.2"'))
        b.append(T(cx + 40, cy + 26, name, 13, dk, weight=600))
        if when:
            b.append(T(cx + cw - 14, cy + 26, when, 9, dk, MONO, anchor="end", op=".88"))
        b.append(para(cx + 18, cy + 50, [p for p in purpose if p], 10.5, INK, 15))
        for j, f in enumerate(["When:", "Who:", "Inputs → outputs:"]):
            b.append(field(cx + 18, cy + 100 + j * 26, f, cx + cw - 14, dk, 10))

    y, h = 592, 468
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Replenishment", PURPLE, "WHAT DO WE PULL IN NEXT?"))
    for i, f in enumerate(["Space available (WIP limit minus items in progress):", "How we choose:"]):
        b.append(field(x + 18, y + 88 + i * 34, f, x + w - 18, d))
    hw = (w - 46) / 2
    b.append(T(x + 18, y + 168, "Options waiting", 12, d, weight=600))
    b.append(sticky_zone(x + 10, y + 178, hw, h - 190, d, "Candidate items", chips=(YELLOW,)))
    b.append(T(x + 28 + hw, y + 168, "Pulled in, and why", 12, d, weight=600))
    b.append(table(x + 28 + hw, y + 200, [("Item", 170), ("Why now", hw - 170)], 6, d, 40))

    x, w = 846, 810
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 3, "Service Delivery Review", ORANGE, "ARE WE MEETING EXPECTATIONS?"))
    b.append(table(x + 18, y + 84, [("Measure", 240), ("Expectation / SLE", 170), ("Actual", 120), ("Action", w - 36 - 530)], 6, d, 40))
    for i, m in enumerate(["Lead time (85th percentile)", "Throughput per week", "Items past their SLE", "Blocked time",
                           "Customer satisfaction", "Our own measure"]):
        b.append(T(x + 24, y + 84 + 10 + (i + 1) * 40 - 14, m, 11, d, weight=600 if i < 5 else None, italic=i == 5))
    b.append(field(x + 18, y + h - 40, "Top improvement to try:", x + w - 18, d))

    b.append(footer("Which conversation would most improve our flow if we had it regularly?",
                    "Are we meeting what our customers expect, and how do we know?", FLOW_TAG))
    write_board("kanban-cadences-board", "Kanban Cadences",
                "A3 landscape board: eight Kanban cadences with typical timings and fields for when, who, inputs and outputs, "
                "plus replenishment and service delivery review panels.", "\n".join(b))


# ---------------------------------------------------------------- events & cadences poster

EVENTS = [
    ("TEAM", BLUE, [
        ("Planning", "Sprint Planning (Scrum) · Replenishment (Kanban)", "Agree a goal and pull in the work that fits capacity",
         "Each iteration · ≤ 2 h per week of iteration", "Team, PO", "A goal and a plan", "Sprint Planning"),
        ("Daily sync", "Daily Scrum · Stand-up · Kanban meeting", "Inspect progress toward the goal and plan the next day",
         "Daily · 15 min", "The team", "Today's plan, blockers raised", "Daily Sync"),
        ("Refinement", "Backlog refinement · Grooming (older term)", "Get the next items understood, split and ready",
         "Weekly or ongoing · ~10% of capacity", "Team, PO, experts", "Ready items", "Backlog Refinement"),
        ("Review", "Sprint Review · Delivery planning (Kanban)", "Inspect what was built with stakeholders, adapt the backlog",
         "Each iteration · ≤ 1 h per week of iteration", "Team, PO, stakeholders", "Feedback, a changed backlog", "Sprint Review"),
        ("Retrospective", "Sprint Retrospective · Kaizen", "Inspect how we work and agree improvements",
         "Each iteration · ≤ 45 min per week", "The team", "One to three improvements", "Retrospective Kit"),
        ("Service review", "Service Delivery Review (Kanban)", "Check flow and service levels against expectations",
         "Every 2–4 weeks · 30–60 min", "Team, customer or PO", "Flow improvements", "Kanban Cadences")]),
    ("MULTI-TEAM", PURPLE, [
        ("Big-room planning", "PI Planning (SAFe) · Multi-team planning (LeSS)", "Align several teams on shared objectives and a plan",
         "Each quarter or period · 1–2 days", "All teams, leaders", "Objectives, team plans, risks", "Cross-Team Planning"),
        ("Cross-team sync", "Scrum of Scrums · ART Sync (SAFe)", "Track shared progress, dependencies and blockers",
         "1–2 × a week · 15–30 min", "One rep per team", "Owned blockers, decisions", "Cross-Team Sync"),
        ("Joint review", "System Demo (SAFe) · Sprint Review (LeSS)", "See the integrated product working across teams",
         "Each iteration or period · 1 h", "Teams, stakeholders", "Feedback on the whole product", "Sprint Review"),
        ("Cross-team retro", "Inspect & Adapt (SAFe) · Overall Retrospective (LeSS)", "Fix problems that sit between teams",
         "End of each period · 1.5–2 h", "Reps from every team, leaders", "One system improvement", "Cross-Team Retro")]),
    ("ORGANISATION", FOREST, [
        ("Portfolio review", "Lean portfolio review · MetaScrum (Scrum@Scale)", "Decide what to fund, start, stop and finish",
         "Monthly or quarterly · 1–2 h", "Leaders, product heads", "An updated portfolio", "Portfolio Kanban"),
        ("Outcome review", "OKR check-in · Strategy Review (Kanban)", "Check progress toward outcomes and adjust direction",
         "Monthly or quarterly · 1 h", "Leaders, POs", "Adjusted objectives", "OKRs · Value Metrics")]),
]


def _wrap(text, width, size):
    """Greedy word wrap using the same rough width estimate as text_w()."""
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(trial, size) > width and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def build_events_poster():
    b = [header("Events & Cadences",
                "Every recurring event in one place: what it's for, how often, who comes, what it produces, and the tool to use.",
                "Run Events · Scrum · Kanban · SAFe · LeSS · Scrum@Scale · One Toolbox",
                header_fields(["Team", "Date"]))]
    cols = [("Event", 150), ("Also called", 270), ("Purpose", 330), ("Cadence & timebox", 230), ("Who", 170),
            ("Output", 200), ("Tool in this kit", 1632 - 36 - 1350)]
    x0, y = 24, 148
    b.append(R(x0, y, 1632, 34, NAVY, 6))
    cx = x0 + 18
    for name, cw in cols:
        b.append(T(cx + 6, y + 22, name.upper(), 9, "white", MONO, weight=600, ls=".1em"))
        cx += cw
    y += 42
    rows_total = sum(len(r) for _, _, r in EVENTS)
    rh = (1060 - y - len(EVENTS) * 30) / rows_total
    for group, (dk, lt), rows in EVENTS:
        b.append(T(x0 + 4, y + 20, group, 10, dk, MONO, weight=600, ls=".14em"))
        b.append(L(x0 + 4 + len(group) * 9, y + 16, x0 + 1632, y + 16, dk, 1, ' stroke-opacity=".3"'))
        y += 30
        for k, row in enumerate(rows):
            b.append(R(x0, y, 1632, rh - 4, lt if k % 2 == 0 else "white", 6, f' stroke="{dk}" stroke-opacity=".15"'))
            b.append(R(x0, y, 5, rh - 4, dk, 3))
            cx = x0 + 18
            for j, ((_, cw), val) in enumerate(zip(cols, row)):
                if j == 0:
                    b.append(T(cx + 6, y + 24, val, 13, dk, weight=600))
                else:
                    lines_ = _wrap(val, cw - 16, 10.5)[:3]
                    b.append(para(cx + 6, y + 22, lines_, 10.5, dk if j == 6 else INK, 15,
                                  weight=600 if j == 6 else None))
                cx += cw
            y += rh

    b.append(footer("Does every event we hold have a clear purpose and output?",
                    "Which event could we shorten, merge or drop?", EVENTS_TAG))
    write_board("events-cadences-poster", "Events & Cadences",
                "A3 landscape reference poster: twelve team, multi-team and organisation events, each with other names "
                "used by Scrum, Kanban, SAFe, LeSS and Scrum@Scale, purpose, cadence, who, output and the toolkit tool.",
                "\n".join(b))


# ---------------------------------------------------------------- anti-pattern spotter

def build_antipattern_spotter():
    from build_antipatterns import ANTIPATTERNS, AREAS
    b = [header("Anti-Pattern Spotter",
                "Tick the anti-patterns you recognise, vote on the ones that hurt most, and pick a tool to tackle each.",
                "Reflect & Improve · Common Anti-Patterns · Spot · Vote · Act · See the Anti-Pattern Catalogue",
                legend([("dot", ACCENT, "Dot = Vote (3 per person)"), ("dot", "#CBD5E1", "Tick = We recognise this")]))]

    x, y, w, h = 24, 148, 1632, 96
    b.append(R(x, y, w, h, NAVY, 10))
    b.append(R(x, y, 6, h, ACCENT, 3))
    b.append(T(x + 24, y + 30, "HOW TO USE IT", 9.5, ACCENT, MONO, weight=600, ls=".14em"))
    steps = [("Spot", "Tick every symptom you recognise, alone and in silence."),
             ("Vote", "Three dots each on the ones that hurt most."),
             ("Act", "Take the top three into the table below.")]
    for i, (t, s) in enumerate(steps):
        sx = x + 24 + i * 540
        b.append(f'<circle cx="{sx + 11}" cy="{y + 62}" r="11" fill="{ACCENT}"/>')
        b.append(T(sx + 11, y + 66, str(i + 1), 10.5, "white", weight=600, anchor="middle"))
        b.append(T(sx + 30, y + 67, t, 14, "white", weight=600))
        b.append(T(sx + 30 + text_w(t, 14) + 14, y + 67, s, 11.5, "#CBD5E1"))

    colours = {"events": BLUE, "backlog": EMERALD, "flow": ORANGE, "teams": PURPLE, "scaling": SKY,
               "leadership": FOREST, "metrics": AMBER}
    cw = (1632 - 3 * 14) / 4
    ph = 270
    for i, (aid, name) in enumerate(AREAS + [("own", "Our Own")]):
        r, c = divmod(i, 4)
        px, py = 24 + c * (cw + 14), 258 + r * (ph + 14)
        col = colours.get(aid, SLATE)
        d = col[0]
        b.append(panel(px, py, cw, ph, None, name, col))
        items = [a[2] for a in ANTIPATTERNS if a[0] == aid][:4] if aid != "own" else []
        for j in range(4):
            iy = py + 84 + j * 46
            b.append(R(px + 18, iy - 11, 13, 13, "white", 2, f' stroke="{d}" stroke-opacity=".6" stroke-width="1.2"'))
            if items:
                b.append(T(px + 40, iy, items[j], 11.5, INK))
            else:
                b.append(L(px + 40, iy + 3, px + cw - 90, iy + 3, WRITE))
            for k in range(3):
                b.append(f'<circle cx="{px + cw - 66 + k * 22:g}" cy="{iy - 4}" r="7" fill="white" stroke="{d}" '
                         f'stroke-opacity=".35" stroke-dasharray="2,2"/>')
            b.append(L(px + 40, iy + 22, px + cw - 18, iy + 22, d, 1, ' stroke-opacity=".08"'))

    x, y, w, h = 24, 826, 1082, 234
    d = RED[0]
    b.append(panel(x, y, w, h, 1, "Our Top Three", RED, "WHY HERE? WHAT WILL WE TRY?"))
    b.append(table(x + 18, y + 82, [("Anti-pattern", 250), ("Why it's happening here", 330), ("Tool to try", 210),
                                    ("Owner", 120), ("Check on", w - 36 - 910)], 3, d, 42))

    x, w = 1120, 536
    d = FOREST[0]
    b.append(panel(x, y, w, h, 2, "Next Time", FOREST))
    for i, m in enumerate(["Re-run the spotter in 6–8 weeks", "Compare which ticks have gone",
                           "Look up each symptom in the catalogue"]):
        b.append(checkbox(x + 18, y + 86 + i * 30, m, d, 11))
    b.append(field(x + 18, y + 200, "Next session:", x + w - 18, d))

    b.append(footer("Which of these would we be embarrassed for a new joiner to see?",
                    "If we fixed only one, which would make the biggest difference?", FOOT_TAG))
    write_board("anti-pattern-spotter-board", "Anti-Pattern Spotter",
                "A3 landscape board: seven areas of common agile anti-patterns, four symptoms each with checkboxes and vote "
                "dots, a panel for your own, a top-three action table, and next steps.", "\n".join(b))


# ---------------------------------------------------------------- leading for psychological safety

def build_leading_safety():
    b = [header("Leading for Psychological Safety",
                "What leaders can do every day to make it safe to speak up, ask for help and admit mistakes, without lowering the bar.",
                "Lead the Organisation · Inspired by Amy Edmondson's Work · Set the Stage · Invite · Respond",
                header_fields(["Leader", "Date"]))]

    moves = [("1", "Set the Stage", PURPLE, "FRAME THE WORK",
              ["Say the work is uncertain and needs everyone's", "input. Be open that you don't have all the answers."],
              ["Explain why each person's view matters", "Name the risks and unknowns out loud", "Share a mistake of your own"],
              ["“This is new for all of us.”", "“I could be wrong about this.”"]),
             ("2", "Invite Participation", BLUE, "ASK, THEN LISTEN",
              ["Ask genuine questions and build ways for", "people to contribute, especially the quiet ones."],
              ["Ask open questions, then wait", "Use silent writing and round-robins", "Speak last in discussions"],
              ["“What are we missing?”", "“Who sees this differently?”"]),
             ("3", "Respond Productively", EMERALD, "WHAT YOU DO NEXT DECIDES IT",
              ["How you react to bad news, questions and", "failure tells people whether to speak again."],
              ["Thank people for raising problems", "Treat failure as learning: ask what happened", "Still address real misconduct, fairly"],
              ["“Thank you for telling me early.”", "“What can we learn from this?”"])]
    cw = (1632 - 2 * 14) / 3
    for i, (n, name, col, note, means, do, say) in enumerate(moves):
        x, y, h = 24 + i * (cw + 14), 148, 340
        d = col[0]
        b.append(panel(x, y, cw, h, n, name, col, note))
        b.append(para(x + 18, y + 82, means, 11.5, d, 17, weight=500))
        b.append(T(x + 18, y + 136, "DO", 8.5, d, MONO, weight=600, ls=".12em"))
        for j, s in enumerate(do):
            b.append(T(x + 18, y + 160 + j * 22, "✓", 11, d, weight=600))
            b.append(T(x + 36, y + 160 + j * 22, s, 11, INK))
        b.append(T(x + 18, y + 246, "SAY", 8.5, d, MONO, weight=600, ls=".12em"))
        for j, s in enumerate(say):
            b.append(T(x + 18, y + 274 + j * 28, s, 17, d, SERIF, italic=True))

    y, h = 502, 360
    x, w = 24, 808
    b.append(panel(x, y, w, h, 4, "Safety and Standards", SLATE, "SAFETY IS NOT THE SAME AS COMFORT"))
    b.append(quad_grid(x + 54, y + 70, x + w - 18, y + h - 52,
                       [("Comfort Zone", "Safe, but little is asked of people", AMBER),
                        ("Learning Zone", "Safe to speak up, and high standards: aim here", EMERALD),
                        ("Apathy Zone", "Not safe, and little expected", SLATE),
                        ("Anxiety Zone", "High pressure, but unsafe to speak up", RED)],
                       "LOW STANDARDS", "HIGH STANDARDS", "ACCOUNTABILITY →", "PSYCHOLOGICAL SAFETY →"))

    x, w = 846, 810
    d = SLATE[0]
    b.append(panel(x, y, w, h, 5, "Phrases to Use and Avoid", SLATE))
    use = ["“What would you do?”", "“Help me understand.”", "“What did we learn?”", "“I'd value your view on this.”",
           "“Thanks for flagging that.”", "“Let's look at the process, not the person.”"]
    avoid = ["“Who's responsible for this?”", "“That's not how we do it here.”", "“Why didn't you tell me sooner?”",
             "“Any questions? No? Good.”", "“Just make it work.”", "“I don't want problems, I want solutions.”"]
    hw = (w - 54) / 2
    for k, (title, items, col) in enumerate([("Try saying", use, EMERALD[0]), ("Avoid saying", avoid, RED[0])]):
        cx = x + 18 + k * (hw + 18)
        b.append(T(cx, y + 80, title.upper(), 9, col, MONO, weight=600, ls=".12em"))
        for j, s in enumerate(items):
            b.append(T(cx, y + 112 + j * 38, s, 15, col, SERIF, italic=True))

    y, h = 876, 184
    x, w = 24, 1082
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "Daily Habits", FOREST, "SMALL, REPEATED, VISIBLE"))
    habits = ["Open meetings by asking for risks and concerns", "Admit a mistake or a doubt each week",
              "Close decisions with a fist of five", "Thank the person who brings the hardest news",
              "Ask the quietest person first, sometimes", "Follow up on what people raised"]
    for j, m in enumerate(habits):
        b.append(checkbox(x + 18 + (j % 2) * 530, y + 86 + (j // 2) * 30, m, d, 11))

    x, w = 1120, 536
    d = RED[0]
    b.append(panel(x, y, w, h, 7, "Warning Signs", RED, "TIME TO ACT"))
    b.append(bullets(x + 22, y + 82, ["Meetings go quiet when you speak", "Bad news reaches you late, or second-hand",
                                      "Status is always green", "No one asks questions or disagrees"], d, 22))

    b.append(footer("When did someone last tell you something you didn't want to hear, and how did you react?",
                    "What would make it easier to say “I don't know” here?", LEAD_TAG))
    write_board("leading-psych-safety-poster", "Leading for Psychological Safety",
                "A3 landscape poster for leaders: three moves (set the stage, invite participation, respond productively) with "
                "things to do and say, a safety and standards grid, phrases to use and avoid, daily habits and warning signs.",
                "\n".join(b))


# ---------------------------------------------------------------- CI/CD and SDLC pack

ENG_TAG = "Engineering Practices · Continuous Delivery · Build Quality In"


def build_delivery_pipeline():
    b = [header("Delivery Pipeline Canvas",
                "Map how a change gets from a developer's commit to customers, find where it waits or fails, and pick the next fix.",
                "Engineering Practices · Continuous Integration & Delivery · Inspired by Continuous Delivery (Humble & Farley)",
                header_fields(["Team / system", "Date"]))]

    x, y, w, h = 24, 148, 1632, 400
    b.append(panel(x, y, w, h, 1, "Pipeline Stages", BLUE, "FROM COMMIT TO CUSTOMER · ADD OR RENAME STAGES TO MATCH YOURS"))
    stages = [("Commit & review", "Merge to main, peer review", PURPLE), ("Build", "Compile, package, version", BLUE),
              ("Automated tests", "Unit, integration, end-to-end", SKY), ("Quality & security", "Scans, checks, approvals", AMBER),
              ("Deploy to test", "Staging or pre-production", ORANGE), ("Release", "Production, to users", EMERALD),
              ("Monitor", "Is it working for users?", RED)]
    gap = 12
    cw = (w - 28 - gap * 6) / 7
    for i, (name, hint, col) in enumerate(stages):
        cx = x + 14 + i * (cw + gap)
        cd = col[0]
        b.append(R(cx, y + 64, cw, h - 78, "white", 6, f' stroke="{cd}" stroke-opacity=".25"'))
        b.append(R(cx, y + 64, cw, 5, cd, 3))
        b.append(T(cx + 14, y + 94, name, 13, cd, weight=600))
        b.append(T(cx + 14, y + 112, hint, 9.5, cd, op=".88"))
        for j, f in enumerate(["Time:", "Waits before:", "Fails:", "Manual steps:", "Gate:", "Tool:", "Owner:"]):
            b.append(field(cx + 14, y + 148 + j * 30, f, cx + cw - 12, cd, 10.5))
        if i < 6:
            b.append(T(cx + cw + gap / 2, y + 64 + (h - 78) / 2, "›", 16, INK, anchor="middle", op=".45"))

    y, h = 562, 290
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Totals & Signals", PURPLE, "THE WHOLE PIPELINE"))
    left = ["Commit to production, typical:", "Of that, time spent waiting:", "Pipeline runs per day:", "Runs that fail:"]
    right = ["Time to fix a broken build:", "Flaky or skipped steps:", "Deploys per week:", "Releases rolled back:"]
    for i, f in enumerate(left):
        b.append(field(x + 18, y + 90 + i * 40, f, x + w / 2 - 14, d))
    for i, f in enumerate(right):
        b.append(field(x + w / 2 + 6, y + 90 + i * 40, f, x + w - 18, d))
    b.append(T(x + 18, y + h - 22, "Fast feedback matters most: aim for a build and test run that finishes in minutes, not hours.",
               10, d, italic=True, op=".88"))

    x, w = 846, 810
    d = RED[0]
    b.append(panel(x, y, w, h, 3, "Bottlenecks & Pain", RED, "WHERE DOES WORK WAIT, FAIL OR NEED A PERSON?"))
    b.append(sticky_zone(x + 16, y + 66, w - 32, h - 82, d, chips=(YELLOW, PINK_ST)))

    y, h = 866, 194
    x, w = 24, 808
    d = FOREST[0]
    b.append(panel(x, y, w, h, 4, "Next Improvement", FOREST, "ONE CHANGE AT A TIME"))
    for i, f in enumerate(["The change we'll make:", "Expected effect (which number moves?):", "Owner:", "Check it on:"]):
        b.append(field(x + 18, y + 82 + i * 30, f, x + w - 18, d))

    x, w = 846, 810
    d = SKY[0]
    b.append(panel(x, y, w, h, 5, "Signs of a Healthy Pipeline", SKY, "TICK WHAT'S TRUE TODAY"))
    signs = ["Every change goes through the same pipeline", "Main is always releasable", "A broken build is fixed first",
             "Tests and config live in version control", "Deploying is one click, or none", "We can roll back in minutes"]
    for i, s in enumerate(signs):
        b.append(checkbox(x + 18 + (i % 2) * 392, y + 88 + (i // 2) * 34, s, d, 11))

    b.append(footer("Where does a change spend most of its time waiting?",
                    "What would it take to release any day we choose?", ENG_TAG))
    write_board("delivery-pipeline-board", "Delivery Pipeline Canvas",
                "A3 landscape board: seven pipeline stages from commit to monitoring, each with time, waits, failures, "
                "manual steps, gates, tools and owner; pipeline totals, bottlenecks, the next improvement, and signs of a healthy pipeline.",
                "\n".join(b))


def build_test_strategy():
    b = [header("Test Strategy",
                "Agree what you test at each level, how much is automated, where the quality gates sit, and what to test hardest.",
                "Engineering Practices · Build Quality In · Inspired by the Test Pyramid (Mike Cohn)",
                header_fields(["Team / product", "Date"]))]

    x, y, w, h = 24, 148, 808, 760
    b.append(panel(x, y, w, h, 1, "Test Pyramid", BLUE, "MANY FAST TESTS AT THE BOTTOM, FEW SLOW ONES AT THE TOP"))
    layers = [("Exploratory", "People testing what scripts can't", PURPLE),
              ("End-to-end / UI", "Whole journeys, through the interface", ORANGE),
              ("Integration / API", "Services and components together", SKY),
              ("Unit", "Small pieces of code, in isolation", EMERALD)]
    top, bot, cx = y + 84, y + h - 24, x + 196
    lh = (bot - top) / 4
    hw = lambda yy: 46 + 124 * (yy - top) / (bot - top)
    for i, (name, hint, col) in enumerate(layers):
        yt, yb = top + i * lh, top + (i + 1) * lh
        dk, lt = col
        pts = f"{cx - hw(yt):g},{yt + 3:g} {cx + hw(yt):g},{yt + 3:g} {cx + hw(yb):g},{yb - 3:g} {cx - hw(yb):g},{yb - 3:g}"
        b.append(f'<polygon points="{pts}" fill="{dk}" fill-opacity=".88"/>')
        b.append(T(cx, yt + lh / 2 + 4, name, 12 if i else 11, "white", weight=600, anchor="middle"))
        fx = x + 392
        b.append(T(fx, yt + 26, name.upper(), 9, dk, MONO, weight=600, ls=".12em"))
        b.append(T(fx, yt + 42, hint, 10, dk, op=".88"))
        for j, f in enumerate(["What we test:", "Automated:", "Runs when:", "Owner:"]):
            b.append(field(fx, yt + 68 + j * 28, f, x + w - 18, dk, 10.5))
        if i:
            b.append(dashed(fx, x + w - 18, yt, dk))

    x, w, h = 846, 810, 380
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Quality Gates", PURPLE, "WHAT MUST PASS, AND WHERE IN THE PIPELINE"))
    b.append(table(x + 18, y + 86, [("Where", 150), ("Check", 300), ("Blocks release?", 140), ("Owner", w - 36 - 590)], 8, d, 32))

    y2, h2 = y + h + 14, 760 - h - 14
    x, w = 846, 398
    d = AMBER[0]
    b.append(panel(x, y2, w, h2, 3, "Shift Left", AMBER, "FIND PROBLEMS EARLIER"))
    for i, s in enumerate(["Examples agreed before coding", "Testers join refinement", "Tests written with the code",
                           "Accessibility checked early", "Security checked early", "Performance tested early", "Test data on demand"]):
        b.append(checkbox(x + 18, y2 + 86 + i * 32, s, d, 11))

    x, w = 1258, 398
    d = RED[0]
    b.append(panel(x, y2, w, h2, 4, "Test Hardest", RED, "HIGHEST RISK"))
    b.append(sticky_zone(x + 16, y2 + 66, w - 32, h2 - 82, d, "Where would a bug hurt most?", chips=(YELLOW, PINK_ST)))

    y, h = 922, 138
    x, w = 24, 808
    d = FOREST[0]
    b.append(panel(x, y, w, h, 5, "Our Definition of Done Says", FOREST, "THE QUALITY BAR FOR EVERY ITEM"))
    b.append(lines(x + 18, y + 86, x + w - 18, 2, 30))

    x, w = 846, 810
    d = SLATE[0]
    b.append(panel(x, y, w, h, 6, "Test Debt", SLATE, "FLAKY, SLOW OR MISSING TESTS"))
    for i, f in enumerate(["Fix first:", "Time set aside each iteration:"]):
        b.append(field(x + 18, y + 84 + i * 32, f, x + w - 18, d))

    b.append(footer("How would we know, within minutes, that we'd broken something?",
                    "Which bug would hurt our users most, and are we testing for it?", ENG_TAG))
    write_board("test-strategy-board", "Test Strategy",
                "A3 landscape board: a four-level test pyramid with what is tested, automation, timing and owner at each level; "
                "quality gates; shift-left practices; the riskiest areas; the Definition of Done; and test debt.", "\n".join(b))


def build_release_readiness():
    b = [header("Release Readiness & Strategy",
                "Plan how a change reaches users, check it's ready, know how to undo it, and tell the people who need to know.",
                "Engineering Practices · Separate Deploy from Release · Go / No-Go",
                header_fields(["Release", "Target date"]))]

    y, h = 148, 300
    x, w = 24, 536
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "What's Releasing", PURPLE))
    for i, f in enumerate(["Release / version:", "Outcome for users:", "Main changes:", "Who's affected:",
                           "Deploy date:", "Switch-on date:"]):
        b.append(field(x + 18, y + 86 + i * 34, f, x + w - 18, d))

    x, w = 574, 1082
    d = BLUE[0]
    b.append(panel(x, y, w, h, 2, "Release Approach", BLUE, "TICK ONE OR COMBINE · DEPLOYING ISN'T THE SAME AS RELEASING"))
    opts = [("Big bang", ["Everyone gets it at once.", "Simple, but the riskiest."]),
            ("Feature flag", ["Deploy switched off, then turn it", "on when ready, for some or all."]),
            ("Canary", ["A small share of users first,", "then more if all is well."]),
            ("Blue-green", ["Switch traffic to a new copy;", "switch back if it goes wrong."]),
            ("Phased rollout", ["By region, customer group", "or channel, one at a time."]),
            ("Beta / early access", ["Volunteers try it first and", "give feedback."])]
    cw, ch = (w - 28 - 20) / 3, (h - 64 - 14 - 10) / 2
    for i, (name, body) in enumerate(opts):
        cx, cy = x + 14 + (i % 3) * (cw + 10), y + 64 + (i // 3) * (ch + 10)
        b.append(R(cx, cy, cw, ch, "white", 6, f' stroke="{d}" stroke-opacity=".2"'))
        b.append(checkbox(cx + 14, cy + 28, "", d))
        b.append(T(cx + 34, cy + 28, name, 13, d, weight=600))
        b.append(para(cx + 14, cy + 52, body, 10.5, d, 16))

    y, h = 462, 360
    x, w = 24, 808
    d = FOREST[0]
    b.append(panel(x, y, w, h, 3, "Go / No-Go Checklist", FOREST, "AGREE THE LIST BEFORE THE DAY"))
    checks = ["Definition of Done met for every item", "Pipeline green, no open critical defects",
              "Performance and security checks done", "Rollback tested, not just written down",
              "Monitoring and alerts ready", "Support and operations briefed",
              "Release notes and messages ready", "Data migration rehearsed (if any)",
              "Change approval recorded (if needed)", "Someone on hand after release"]
    for i, s in enumerate(checks):
        b.append(checkbox(x + 18 + (i % 2) * 392, y + 90 + (i // 2) * 36, s, d, 11))
    b.append(L(x + 18, y + 274, x + w - 18, y + 274, d, 1, ' stroke-opacity=".2"'))
    b.append(T(x + 18, y + 306, "Decision:", 11, d, weight=600))
    b.append(checkbox(x + 96, y + 306, "Go", d))
    b.append(checkbox(x + 156, y + 306, "No-go", d))
    b.append(field(x + 240, y + 306, "Decided by:", x + 520, d))
    b.append(field(x + 536, y + 306, "When:", x + w - 18, d))

    x, w = 846, 810
    d = RED[0]
    b.append(panel(x, y, w, h, 4, "Rollback & Recovery", RED, "PLAN TO UNDO IT BEFORE YOU DO IT"))
    for i, f in enumerate(["If it goes wrong, we'll see:", "We'll undo it by:", "Time to undo:", "Who decides to roll back:",
                           "What we can't undo (data, messages):", "Rollback last tested on:"]):
        b.append(field(x + 18, y + 90 + i * 42, f, x + w - 18, d))

    y, h = 836, 224
    x, w = 24, 1082
    d = SKY[0]
    b.append(panel(x, y, w, h, 5, "Who Needs to Know", SKY, "USERS, SUPPORT, SALES, OTHER TEAMS"))
    b.append(table(x + 18, y + 86, [("Audience", 210), ("What they need to know", 380), ("When", 140), ("How", 160),
                                    ("Owner", w - 36 - 890)], 4, d, 30))

    x, w = 1120, 536
    d = AMBER[0]
    b.append(panel(x, y, w, h, 6, "After Release", AMBER))
    for i, f in enumerate(["Check the outcome on:", "Remove the feature flag by:", "What we learned:"]):
        b.append(field(x + 18, y + 86 + i * 36, f, x + w - 18, d))
    b.append(L(x + 18, y + 194, x + w - 18, y + 194, WRITE))

    b.append(footer("If this goes wrong at the worst moment, what's our plan?",
                    "Could we release this a little at a time?", ENG_TAG))
    write_board("release-readiness-board", "Release Readiness & Strategy",
                "A3 landscape board: what's releasing, six release approaches (big bang, feature flag, canary, blue-green, "
                "phased, beta), a go/no-go checklist, rollback and recovery, who needs to know, and after-release checks.",
                "\n".join(b))


CD_PRACTICES = [
    ("BUILD & INTEGRATE", BLUE, [
        ("Version control for everything", "Code, tests, configuration and infrastructure are all versioned."),
        ("Small, short-lived branches", "Work merges to main at least daily (trunk-based development)."),
        ("Continuous integration", "Every merge builds and tests automatically, in minutes.")]),
    ("TEST", SKY, [
        ("Test automation we trust", "A green run means we're confident; flaky tests get fixed."),
        ("Test data on demand", "Anyone can get realistic test data without waiting."),
        ("Security built in", "Security checks run in the pipeline, not just before release.")]),
    ("DEPLOY & RELEASE", EMERALD, [
        ("Automated deployment", "Deploying to any environment is one click, or none."),
        ("Deploy separate from release", "Feature flags or similar let us switch features on later."),
        ("Small batches", "Changes reach production in small pieces, often.")]),
    ("RUN & LEARN", RED, [
        ("Monitoring & observability", "We know quickly when something's wrong for users."),
        ("Fast recovery", "We can roll back or fix forward in minutes, and practise it."),
        ("Learning from failure", "Incidents lead to blameless reviews and real changes.")]),
]


def build_cd_health_check():
    b = [header("Continuous Delivery Health Check",
                "Score twelve practices that make releasing safe and routine, find the biggest gaps, and pick experiments to close them.",
                "Engineering Practices · Inspired by DORA research, Accelerate (Forsgren, Humble & Kim) and Continuous Delivery (Humble & Farley)",
                header_fields(["Team", "Date"]))]

    x, y, w, h = 24, 148, 1082, 912
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "Practices", SLATE, "VOTE SILENTLY · 1 NOT YET · 3 SOMETIMES · 5 ALWAYS"))
    sx, nx = x + 590, x + 820
    b.append(T(sx + 70, y + 72, "SCORE", 8.5, d, MONO, weight=600, anchor="middle", ls=".12em"))
    # one text element (tspans) so the AI prompt reads it as a scale, not a numbered list
    b.append(f'<text x="{sx + 14:g}" y="{y + 90}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{d}" fill-opacity=".88">'
             + " ".join(f'<tspan x="{sx + 14 + k * 28:g}">{k + 1}</tspan>' for k in range(5)) + "</text>")
    b.append(T(nx, y + 80, "NOTES / EVIDENCE", 8.5, d, MONO, weight=600, ls=".12em"))
    cy = y + 92
    for group, (dk, lt), items in CD_PRACTICES:
        b.append(T(x + 18, cy + 18, group, 9, dk, MONO, weight=600, ls=".14em"))
        b.append(L(x + 30 + text_w(group, 9) * 1.25, cy + 14, x + w - 18, cy + 14, dk, 1, ' stroke-opacity=".25"'))
        cy += 26
        for name, desc in items:
            b.append(R(x + 14, cy, w - 28, 50, "white", 6, f' stroke="{dk}" stroke-opacity=".18"'))
            b.append(R(x + 14, cy, 4, 50, dk, 2))
            b.append(T(x + 30, cy + 21, name, 12.5, dk, weight=600))
            b.append(T(x + 30, cy + 39, desc, 10, INK, op=".88"))
            for k in range(5):
                b.append(f'<circle cx="{sx + 14 + k * 28:g}" cy="{cy + 25}" r="10" fill="white" stroke="{dk}" stroke-opacity=".45"/>')
            b.append(L(nx, cy + 22, x + w - 30, cy + 22, WRITE))
            b.append(L(nx, cy + 40, x + w - 30, cy + 40, WRITE))
            cy += 54
        cy += 4

    x, w = 1120, 536
    y, h = 148, 420
    d = RED[0]
    b.append(panel(x, y, w, h, 2, "Biggest Gaps", RED, "LOWEST SCORES · WIDEST SPREAD"))
    b.append(sticky_zone(x + 16, y + 66, w - 32, h - 82, d, chips=(YELLOW, PINK_ST)))

    y, h = 582, 290
    d = FOREST[0]
    b.append(panel(x, y, w, h, 3, "Experiments", FOREST, "ONE OR TWO, SMALL"))
    for i, f in enumerate(["Practice:", "We'll try:", "Owner / check on:", "Practice:", "We'll try:", "Owner / check on:"]):
        b.append(field(x + 18, y + 86 + i * 32 + (14 if i > 2 else 0), f, x + w - 18, d))
    b.append(dashed(x + 18, x + w - 18, y + 172, d))

    y, h = 886, 174
    d = BLUE[0]
    b.append(panel(x, y, w, h, 4, "Trend", BLUE, "REPEAT EVERY QUARTER"))
    for i, f in enumerate(["Last check (date and total):", "This check (total out of 60):", "Next check:"]):
        b.append(field(x + 18, y + 84 + i * 32, f, x + w - 18, d))

    b.append(footer("Which practice, if it improved, would make releasing least scary?",
                    "Where do our scores disagree most, and why?", ENG_TAG))
    write_board("cd-health-check-board", "Continuous Delivery Health Check",
                "A3 landscape board: twelve continuous delivery practices in four groups, each scored 1 to 5 with notes; "
                "biggest gaps, experiments, and a quarterly trend.", "\n".join(b))


SDLC_STAGES = [
    ("Idea", PURPLE, "A problem or opportunity is raised and weighed against other work.", "Is this worth exploring?",
     ["Product Vision Board", "Prioritisation Board", "Portfolio Kanban"], "Business case approved"),
    ("Discover", BLUE, "Understand users, the problem and the options before committing.", "What problem, for whom?",
     ["Persona & Journey Map", "Opportunity Solution Tree", "Impact Map"], "Requirements signed off"),
    ("Design", SKY, "Shape the solution into slices and stories, with examples and key technical decisions.",
     "What's the smallest valuable slice?", ["User Story Map", "Epic Breakdown Canvas", "Example Mapping", "Architecture Decision Record"],
     "Design approved"),
    ("Build", AMBER, "Write code and tests together, integrate continuously and keep work flowing.",
     "Is main always releasable?", ["Sprint Planning", "Pairing & Mobbing", "Kanban Board Design", "Delivery Pipeline Canvas"],
     "Code complete"),
    ("Test", ORANGE, "Automated checks on every change, plus exploratory testing for what automation can't see.",
     "How do we know it works?", ["Test Strategy", "Example Mapping", "Definition of Done (Team Charter)"], "Test sign-off (UAT)"),
    ("Release", EMERALD, "Deploy safely, then switch on for users at the right pace, with a way back.",
     "Can we release, and undo it, safely?", ["Release Readiness & Strategy", "Release Forecast & Burn-up"],
     "Go-live approval (change board)"),
    ("Operate", RED, "Monitor, support users and recover quickly when something goes wrong.", "Would we know if it broke?",
     ["Blameless Incident Review", "Delivery Metrics & Tech Debt", "Continuous Delivery Health Check"], "Handover to operations"),
    ("Learn", FOREST, "Measure the outcome, review what happened and feed the learning back in.",
     "Did it make the difference we hoped?", ["Sprint Review", "Value Metrics", "Retrospective Kit"], "Post-implementation review"),
]


def build_sdlc_poster():
    b = [header("SDLC at a Glance",
                "The software development lifecycle from idea to outcome: what happens at each stage, the question it answers, and the tools that help.",
                "Agile Lifecycle · From Idea to Outcome · One Toolbox",
                header_fields(["Team", "Date"]))]
    y, h, gap = 148, 500, 10
    cw = (1632 - 7 * gap) / 8
    for i, (name, (dk, lt), what, q, tools, gate) in enumerate(SDLC_STAGES):
        cx = 24 + i * (cw + gap)
        b.append(R(cx, y, cw, h, lt, 10, f' stroke="{dk}" stroke-opacity=".18" stroke-width="1.5" filter="url(#fc)"'))
        b.append(top_round(cx, y, cw, 52, 10, dk))
        b.append(f'<circle cx="{cx + 21:g}" cy="{y + 26}" r="12" fill="white" fill-opacity=".18"/>')
        b.append(T(cx + 21, y + 31, str(i + 1), 11, "white", weight=600, anchor="middle"))
        b.append(T(cx + 42, y + 32, name, 15, "white", weight=600))
        ty = y + 82
        b.append(T(cx + 14, ty, "WHAT HAPPENS", 8, dk, MONO, weight=600, ls=".12em"))
        wl = _wrap(what, cw - 28, 10.5)
        b.append(para(cx + 14, ty + 20, wl, 10.5, INK, 15))
        ty += 20 + len(wl) * 15 + 18
        b.append(T(cx + 14, ty, "KEY QUESTION", 8, dk, MONO, weight=600, ls=".12em"))
        ql = _wrap(f"“{q}”", cw - 28, 13)
        b.append(para(cx + 14, ty + 22, ql, 13, dk, 17, font=SERIF, italic=True))
        ty = y + 276
        b.append(T(cx + 14, ty, "TOOLS IN THIS KIT", 8, dk, MONO, weight=600, ls=".12em"))
        ty += 22
        for t in tools:
            tl = _wrap(t, cw - 40, 10.5)
            b.append(f'<circle cx="{cx + 18:g}" cy="{ty - 4}" r="2.5" fill="{dk}"/>')
            b.append(para(cx + 28, ty, tl, 10.5, dk, 14, weight=600))
            ty += len(tl) * 14 + 8
        b.append(L(cx + 14, y + h - 76, cx + cw - 14, y + h - 76, dk, 1, ' stroke-opacity=".25"'))
        b.append(T(cx + 14, y + h - 54, "TRADITIONAL GATE", 8, dk, MONO, weight=600, ls=".12em", op=".88"))
        b.append(para(cx + 14, y + h - 34, _wrap(gate, cw - 28, 10.5), 10.5, MUTED, 14))
        if i < 7:
            b.append(T(cx + cw + gap / 2, y + h / 2, "›", 14, INK, anchor="middle", op=".45"))

    b.append(T(840, y + h + 28, "↺  Learning feeds the next idea. In agile delivery the whole loop runs for every small slice, "
               "many times over, not once per project.", 12, INK, SERIF, italic=True, anchor="middle"))

    y, h = 696, 364
    x, w = 24, 1082
    d = SLATE[0]
    b.append(panel(x, y, w, h, None, "Traditional SDLC and Agile Delivery", SLATE, "SAME STAGES, DIFFERENT RHYTHM"))
    rows = [("Planning", "Detailed plan up front; change is controlled", "Plan a little, often; change is expected"),
            ("Requirements", "Complete and signed off before building", "Discovered and refined just in time, with examples"),
            ("Testing", "A phase near the end", "On every change, automated, from the start"),
            ("Release", "Rare, large and risky", "Frequent, small and routine"),
            ("Teams", "Hand-offs between specialist groups", "Cross-functional teams own the whole slice"),
            ("Feedback", "From users, after launch", "From users, every iteration"),
            ("Risk", "Found late, when change is costly", "Found early, while change is cheap"),
            ("Progress", "Phases and documents completed", "Working software and outcomes"),
            ("Governance", "Document gates between phases", "Evidence from working software, every iteration")]
    cols = [("", 170), ("Traditional (stage-gate)", 430), ("Agile delivery", 430)]
    cx = x + 18
    for name, cwid in cols:
        b.append(T(cx + 6, y + 82, name.upper(), 8.5, d, MONO, weight=600, ls=".1em"))
        cx += cwid
    for i, (a, t, ag) in enumerate(rows):
        ry = y + 108 + i * 28
        b.append(T(x + 24, ry, a, 11, d, weight=600))
        b.append(T(x + 194, ry, t, 11, MUTED))
        b.append(T(x + 624, ry, ag, 11, EMERALD[0], weight=500))
        b.append(L(x + 18, ry + 11, x + w - 18, ry + 11, RULE, 1))

    x, w = 1120, 536
    d = PURPLE[0]
    b.append(panel(x, y, w, h, None, "Keeping Governance, Losing the Delay", PURPLE))
    tips = [["Keep the questions each gate asks,", "and answer them with evidence every iteration."],
            ["Put compliance checks in the", "Definition of Done, not a final phase."],
            ["Let the pipeline produce audit evidence:", "tests run, approvals, who deployed what."],
            ["Review working software, not documents", "about software."],
            ["Match approval to risk: small, routine", "changes go straight through."],
            ["Invite risk, audit and security partners", "to reviews early, not just at the end."]]
    for i, t in enumerate(tips):
        ty = y + 86 + i * 44
        b.append(f'<circle cx="{x + 22}" cy="{ty - 4}" r="3" fill="{d}"/>')
        b.append(para(x + 34, ty, t, 11, d, 16))

    b.append(footer("Where in our lifecycle does work wait longest?",
                    "Which gate could we replace with evidence from working software?", "Agile Lifecycle · From Idea to Outcome · One Toolbox"))
    write_board("sdlc-poster", "SDLC at a Glance",
                "A3 landscape reference poster: eight software development lifecycle stages from idea to learn, each with what "
                "happens, its key question, the toolkit tools that help and the traditional gate; plus traditional vs. agile "
                "delivery and how to keep governance without the delay.", "\n".join(b))


# ---------------------------------------------------------------- right-size your structure

RIGHT_SIZE_ROWS = ["Planning", "Roles", "Events", "Tracking work", "Risks & dependencies", "Reporting", "Decisions & governance"]
RIGHT_SIZE = [
    ("One Team", EMERALD, "3–10 people · 1 team", "4 people: 6 links", [
        ("A short planning conversation each iteration, and a simple roadmap.", "Sprint Planning · Prioritisation Board"),
        ("A product owner or lead sets priorities; the team shares the rest.", "Team Charter"),
        ("Daily sync, planning, review and retro, kept short.", "Events & Cadences"),
        ("One visible board. Conversation fills the gaps.", "Kanban Board Design"),
        ("Raise them in the daily sync and planning; note the big ones.", "Pre-mortem"),
        ("Show working software at the review, plus a short note to the sponsor.", "Sprint Review"),
        ("Decide in the room. Write down only what people will ask about later.", "Team Charter (How We Decide)")]),
    ("Team of Teams", BLUE, "10–50 people · 2–5 teams", "40 people: 780 links", [
        ("Plan together each planning period, with shared objectives.", "Cross-Team Planning · OKRs"),
        ("Add a programme manager or RTE to coordinate, and one product lead across teams.", "RACI & Decision Log"),
        ("Add a weekly cross-team sync, a joint demo and a joint retro.", "Cross-Team Sync · Cross-Team Retro"),
        ("A shared view of features across teams; each team keeps its own board.", "Dependency Map"),
        ("A shared RAID log and dependency map, reviewed every week.", "RAID Log · Dependency Map"),
        ("A one-page outcome status report and a forecast range.", "Outcome Status Report · Release Forecast"),
        ("A decision log, a shared Definition of Done and clear decision rights.", "RACI & Decision Log · Delegation Board")]),
    ("Programme", PURPLE, "50+ people · many teams", "120 people: 7,140 links", [
        ("Outcomes set at the top; big-room planning for each group of teams.", "OKRs · Portfolio Kanban"),
        ("Programme and portfolio leads, an RTE per group of teams, architecture and product leads.", "Team Topology Design"),
        ("Add portfolio reviews, and inspect & adapt across the whole programme.", "Events & Cadences · Value Metrics"),
        ("A portfolio board of initiatives, with work in progress limited at the top.", "Portfolio Kanban & Investment Mix"),
        ("Managed across groups of teams, with an owner at each level.", "RAID Log · Value Stream Map"),
        ("Outcome and value measures for leaders, rolled up from the same data.", "Value Metrics · Outcome Status Report"),
        ("Light governance: evidence from working software, risk-based approval, delegated decisions.",
         "SDLC at a Glance · Delegation Board · ADKAR")]),
]


def build_right_size():
    b = [header("Right-Size Your Structure",
                "How much structure a project needs as it grows from one team to many: just enough to stay safe, no more.",
                "Run a Project · Inspired by Brooks's law (Fred Brooks), Scrum's small teams, SAFe's release trains and Team Topologies",
                header_fields(["Project", "Date"]))]

    y, h, gap = 148, 912, 14
    cw = (1182 - 2 * gap) / 3
    for i, (name, col, size, links, cells) in enumerate(RIGHT_SIZE):
        dk = col[0]
        x = 24 + i * (cw + gap)
        b.append(panel(x, y, cw, h, i + 1, name, col, "LEVEL " + str(i + 1)))
        b.append(T(x + 18, y + 80, size, 14, dk, weight=600))
        b.append(T(x + 18, y + 98, links, 10, dk, op=".88"))
        top = y + 116
        ch = (h - 116 - 10) / len(cells)
        for j, ((text, tools), row) in enumerate(zip(cells, RIGHT_SIZE_ROWS)):
            cy = top + j * ch
            b.append(R(x + 12, cy, cw - 24, ch - 8, "white", 6, f' stroke="{dk}" stroke-opacity=".15"'))
            b.append(T(x + 24, cy + 18, row.upper(), 8, dk, MONO, weight=600, ls=".12em"))
            tl = _wrap(text, cw - 52, 10.5)[:3]
            b.append(para(x + 24, cy + 36, tl, 10.5, INK, 15))
            ty = cy + 36 + len(tl) * 15 + 4
            b.append(para(x + 24, ty, _wrap(tools, cw - 52, 10), 10, dk, 14, weight=600))
        if i < 2:
            b.append(T(x + cw + gap / 2, y + 30, "›", 16, INK, anchor="middle", op=".45"))

    x, w = 1220, 436
    yy, hh = 148, 330
    d = AMBER[0]
    b.append(panel(x, yy, w, hh, 4, "Turn the Dial Up If…", AMBER, "SIZE ISN'T EVERYTHING"))
    factors = ["High risk, safety or regulation", "Many dependencies on others", "A fixed date or contract",
               "Many stakeholders or senior visibility", "People across sites or time zones", "New team, domain or technology",
               "Long duration (many months)"]
    for k, f in enumerate(factors):
        b.append(checkbox(x + 18, yy + 86 + k * 30, f, d, 11))
    b.append(para(x + 18, yy + hh - 32, ["Two or more ticked? Borrow the next level's", "practices for those areas only."], 10, d, 14,
                  italic=True))

    yy, hh = 492, 260
    d = SKY[0]
    b.append(panel(x, yy, w, hh, 5, "Coordination Grows Fast", SKY, "LINKS = N × (N − 1) / 2"))
    cx, cy, r = x + 104, yy + 152, 62
    pts = [(cx + r * math.cos(math.pi * (0.5 + 2 * k / 6)), cy - r * math.sin(math.pi * (0.5 + 2 * k / 6))) for k in range(6)]
    for a_ in range(6):
        for c_ in range(a_ + 1, 6):
            b.append(L(pts[a_][0], pts[a_][1], pts[c_][0], pts[c_][1], d, 1, ' stroke-opacity=".35"'))
    for px, py in pts:
        b.append(f'<circle cx="{px:g}" cy="{py:g}" r="9" fill="{d}"/>')
    b.append(T(cx, yy + hh - 16, "6 people: 15 links", 10, d, anchor="middle", op=".88"))
    for k, (n, l_) in enumerate([("4 people", "6 links"), ("12 people", "66 links"), ("40 people", "780 links"),
                                 ("120 people", "7,140 links")]):
        ty = yy + 96 + k * 36
        b.append(T(x + 210, ty, n, 11, INK))
        b.append(T(x + w - 18, ty, l_, 14, d, weight=600, anchor="end"))
        b.append(L(x + 210, ty + 10, x + w - 18, ty + 10, RULE, 1))

    yy, hh = 766, 294
    d = RED[0]
    b.append(panel(x, yy, w, hh, 6, "Signs It's the Wrong Size", RED))
    half = (w - 36) / 2
    for k, (title, items) in enumerate([("TOO LITTLE", ["Surprises arrive late", "Teams block each other", "The same questions, again",
                                                         "No one knows the plan"]),
                                        ("TOO MUCH", ["Meetings about meetings", "Reports no one reads", "Decisions wait for sign-off",
                                                      "Process for its own sake"])]):
        cx2 = x + 18 + k * (half + 0)
        b.append(T(cx2, yy + 84, title, 9, d, MONO, weight=600, ls=".14em"))
        b.append(bullets(cx2 + 4, yy + 110, items, d, 26))
    b.append(T(x + 18, yy + hh - 22, "Add structure when it solves a problem you have; remove it when it doesn't.", 10, d,
               italic=True, op=".88"))

    b.append(footer("What's the least structure that would keep this project safe?",
                    "Which part of our process could we drop without anyone missing it?", PROJECT_TAG))
    write_board("right-size-poster", "Right-Size Your Structure",
                "A3 landscape reference poster: three levels of project size (one team, team of teams, programme), with what "
                "planning, roles, events, tracking work, risks and dependencies, reporting and decisions need at each level and "
                "the tools to use; factors that call for more structure; how coordination grows; and signs of too little or too much.",
                "\n".join(b))


# ---------------------------------------------------------------- project close-out

def build_project_closeout():
    b = [header("Project Close-out",
                "Finish well: check what was achieved, hand over cleanly, capture what you learned, tie up loose ends and say thank you.",
                "Run a Project · Close · Benefits Realisation · Lessons Learned",
                header_fields(["Project", "Date"]))]

    y, h = 148, 300
    x, w = 24, 808
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Did We Achieve It?", PURPLE, "AGAINST THE ORIGINAL GOAL"))
    for i, f in enumerate(["Original goal:", "What we delivered:"]):
        b.append(field(x + 18, y + 84 + i * 32, f, x + w - 18, d))
    b.append(table(x + 18, y + 170, [("Measure", 250), ("Target", 130), ("Actual", 130), ("What it tells us", w - 36 - 510)], 3, d, 32))

    x, w = 846, 810
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 2, "Benefits Still to Come", EMERALD, "MOST VALUE ARRIVES AFTER THE PROJECT ENDS"))
    b.append(table(x + 18, y + 86, [("Benefit", 260), ("Expected by", 130), ("Measured how", 230), ("Owner", w - 36 - 620)], 5, d, 34))

    y, h = 462, 330
    x, w = 24, 536
    d = BLUE[0]
    b.append(panel(x, y, w, h, 3, "Handover", BLUE, "WHO OWNS IT NOW?"))
    for i, s in enumerate(["Support team trained and ready", "Documentation and runbooks handed over",
                           "Open defects and backlog given an owner", "Monitoring and alerts owned",
                           "Access, licences and accounts sorted", "Contracts and suppliers closed", "Budget closed and reported"]):
        b.append(checkbox(x + 18, y + 86 + i * 28, s, d, 11))
    b.append(field(x + 18, y + h - 26, "Handed to:", x + w - 18, d))

    x, w = 574, 1082
    d = AMBER[0]
    b.append(panel(x, y, w, h, 4, "What We Learned", AMBER, "FOR THE NEXT PROJECT, NOT FOR THE ARCHIVE"))
    sub = (w - 28 - 20) / 3
    for i, (name, hint) in enumerate([("Keep doing", "What worked that we'd repeat?"), ("Do differently", "What would we change?"),
                                      ("Surprises", "What did we not see coming?")]):
        sx = x + 14 + i * (sub + 10)
        b.append(T(sx + 4, y + 82, name.upper(), 9, d, MONO, weight=600, ls=".12em"))
        b.append(sticky_zone(sx, y + 94, sub, h - 108, d, hint, chips=(YELLOW, GREEN) if i < 2 else (BLUE_ST,)))

    y, h = 806, 254
    x, w = 24, 808
    d = RED[0]
    b.append(panel(x, y, w, h, 5, "Loose Ends", RED, "NOTHING LEFT WITHOUT AN OWNER"))
    b.append(table(x + 18, y + 86, [("Item", 420), ("Owner", 170), ("By when", w - 36 - 590)], 4, d, 34))

    x, w = 846, 810
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "Thanks & Celebrate", FOREST))
    for i, f in enumerate(["People and teams to thank:", "", "How we'll celebrate:", "Share the story and lessons with:"]):
        if f:
            b.append(field(x + 18, y + 86 + i * 36, f, x + w - 18, d))
        else:
            b.append(L(x + 18, y + 90 + i * 36, x + w - 18, y + 90 + i * 36, WRITE))

    b.append(footer("What would we tell the next team that runs a project like this?",
                    "Who will check the benefits arrived, and when?", PROJECT_TAG))
    write_board("project-closeout-board", "Project Close-out",
                "A3 landscape board: goal versus what was delivered, benefits still to come with owners, a handover "
                "checklist, lessons learned (keep doing, do differently, surprises), loose ends, and thanks.", "\n".join(b))


# ---------------------------------------------------------------- team onboarding

def build_team_onboarding():
    b = [header("Team Onboarding",
                "Help a new team member feel welcome, get set up and do useful work quickly, with a buddy and clear check-ins.",
                "Set Up the Team · Onboarding · First Week · 30 / 60 / 90 Days",
                header_fields(["New member", "Start date"]))]

    y, h = 148, 330
    x, w = 24, 536
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "Before Day One", PURPLE, "SO DAY ONE ISN'T ABOUT WAITING"))
    for i, s in enumerate(["Laptop, accounts and access ready", "Added to channels, calendars and boards", "Buddy chosen and briefed",
                           "Welcome message sent", "First-week plan shared", "A first small task picked", "Team told who's joining and when"]):
        b.append(checkbox(x + 18, y + 86 + i * 32, s, d, 11))

    x, w = 574, 1082
    b.append(panel(x, y, w, h, 2, "First Week", BLUE, "ONE STEP A DAY · A PLAN, NOT A FIREHOSE"))
    b.append(step_cards(x + 14, y + 66, w - 28, h - 80,
                        [("Meet & set up", ["Meet the team and your", "buddy; get set up."]),
                         ("Product & users", ["What we build, for whom,", "and why it matters."]),
                         ("Pair", ["Pair on a small item", "with a teammate."]),
                         ("Join in", ["Join the team's events;", "ask every question."]),
                         ("Finish & check in", ["Finish something small;", "first check-in."])], BLUE))

    y, h = 492, 300
    x, w = 24, 808
    d = SKY[0]
    b.append(panel(x, y, w, h, 3, "People to Meet", SKY, "INSIDE AND OUTSIDE THE TEAM"))
    b.append(table(x + 18, y + 86, [("Who", 200), ("Role", 170), ("Why talk to them", 320), ("Met", w - 36 - 690)], 6, d, 32))

    x, w = 846, 810
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 4, "How We Work Here", EMERALD, "WALK THROUGH EACH ONE TOGETHER"))
    for i, s in enumerate(["Team charter and working agreements", "Definition of Done", "Our board and workflow", "Events and when they happen",
                           "How we decide", "How to ask for help", "Where documentation lives", "How we release",
                           "Our tools and AI agreement", "Who our users are"]):
        b.append(checkbox(x + 18 + (i % 2) * 392, y + 88 + (i // 2) * 38, s, d, 11))

    y, h = 806, 254
    x, w = 24, 536
    d = AMBER[0]
    b.append(panel(x, y, w, h, 5, "Buddy", AMBER, "A FRIENDLY FIRST CONTACT"))
    for i, f in enumerate(["Buddy:", "We'll meet every:", "Ask me about:", "Until (date):"]):
        b.append(field(x + 18, y + 86 + i * 38, f, x + w - 18, d))

    x, w = 574, 1082
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "30 · 60 · 90 Days", FOREST, "CHECK IN, BOTH WAYS"))
    cw = (w - 28 - 20) / 3
    for i, (name, hint) in enumerate([("30 days", "Settled in, doing real work"), ("60 days", "Working independently"),
                                      ("90 days", "Fully part of the team")]):
        cx = x + 14 + i * (cw + 10)
        b.append(R(cx, y + 64, cw, h - 78, "white", 6, f' stroke="{d}" stroke-opacity=".2"'))
        b.append(T(cx + 14, y + 88, name.upper(), 9, d, MONO, weight=600, ls=".12em"))
        b.append(T(cx + 14, y + 106, hint, 10, d, op=".88"))
        for j, f in enumerate(["Goal:", "Check-in date:", "How it's going:"]):
            b.append(field(cx + 14, y + 140 + j * 30, f, cx + cw - 14, d, 10.5))
        b.append(L(cx + 14, y + 234, cx + cw - 14, y + 234, WRITE))

    b.append(footer("What do you wish someone had told you in your first week?",
                    "What could the newest person see that we've stopped noticing?", LIFECYCLE_TAG))
    write_board("team-onboarding-board", "Team Onboarding",
                "A3 landscape board: before day one checklist, a first-week plan, people to meet, how we work here, "
                "a buddy, and 30, 60 and 90-day check-ins.", "\n".join(b))


# ---------------------------------------------------------------- now / next / later roadmap

def build_roadmap():
    b = [header("Now · Next · Later Roadmap",
                "Show what you're working on, what's coming and what you're exploring, tied to goals, without promising dates you can't keep.",
                "Decide What to Build · Now / Next / Later (Janna Bastow, ProdPad) · Outcomes, Not Dates",
                header_fields(["Product", "Owner", "Updated"]))]

    y, h = 148, 540
    ct, cb = y + 64, y + h - 14
    lane = (cb - ct) / 3
    gx, gw = 24, 272
    d = EMERALD[0]
    b.append(panel(gx, y, gw, h, 1, "Goals", EMERALD, "WHY"))
    for i, g in enumerate("ABC"):
        ly = ct + i * lane
        b.append(T(gx + 18, ly + 22, f"GOAL {g}", 9, d, MONO, weight=600, ls=".12em"))
        b.append(lines(gx + 18, ly + 50, gx + gw - 18, 2, 26))
        b.append(field(gx + 18, ly + 118, "Measure:", gx + gw - 18, d, 10.5))
        if i:
            b.append(dashed(gx + 14, gx + gw - 14, ly, d))

    cw = (1632 - gw - 3 * 14) / 3
    cols = [(2, "Now", BLUE, "COMMITTED · HIGH CERTAINTY", "Being built for this goal", (YELLOW,)),
            (3, "Next", PURPLE, "SHAPED · MEDIUM CERTAINTY", "Shaped and ready to start", (YELLOW,)),
            (4, "Later", SKY, "EXPLORING · LOW CERTAINTY", "Problems worth exploring", (BLUE_ST,))]
    for i, (num, name, color, note, hint, chips) in enumerate(cols):
        x = gx + gw + 14 + i * (cw + 14)
        dk = color[0]
        b.append(panel(x, y, cw, h, num, name, color, note))
        for j in range(3):
            ly = ct + j * lane
            b.append(sticky_zone(x + 14, ly + 8, cw - 28, lane - 16, dk, hint, chips))
            if j:
                b.append(dashed(x + 14, x + cw - 14, ly, dk))

    b.append(strip(702, "CERTAINTY FALLS FROM LEFT TO RIGHT  ·  LATER HOLDS PROBLEMS, NOT PROMISES"))

    y, h = 748, 312
    x, w = 24, 536
    d = RED[0]
    b.append(panel(x, y, w, h, 5, "Not Doing", RED, "AND WHY · SAYING NO OUT LOUD"))
    b.append(table(x + 18, y + 86, [("Item", 230), ("Why not (for now)", w - 36 - 230)], 6, d, 32))

    x = 574
    d = AMBER[0]
    b.append(panel(x, y, w, h, 6, "Assumptions to Test", AMBER, "BEFORE IT MOVES LEFT"))
    b.append(table(x + 18, y + 86, [("We believe…", 260), ("We'll test it by", w - 36 - 260)], 6, d, 32))

    x = 1124
    w = 532
    d = SLATE[0]
    b.append(panel(x, y, w, h, 7, "Review & Share", SLATE, "A LIVING PLAN"))
    for i, f in enumerate(["We review this every:", "Next review:", "An item moves to Now when:", "", "Shared with:"]):
        if f:
            b.append(field(x + 18, y + 86 + i * 34, f, x + w - 18, d))
        else:
            b.append(L(x + 18, y + 90 + i * 34, x + w - 18, y + 90 + i * 34, WRITE))
    for i, s in enumerate(["Every item links to a goal", "No dates beyond Now"]):
        b.append(checkbox(x + 18 + i * 250, y + h - 30, s, d, 11))

    b.append(footer("Which goal does this serve, and how will we know it worked?",
                    "What would have to be true for this to move from Later to Next?",
                    "Decide What to Build · Roadmaps · Outcomes Over Output"))
    write_board("roadmap-board", "Now · Next · Later Roadmap",
                "A3 landscape roadmap board: three goals with measures, Now, Next and Later columns as horizons of "
                "certainty, what we're not doing and why, assumptions to test, and how the roadmap is reviewed and shared.",
                "\n".join(b))


# ---------------------------------------------------------------- personal user manual

MANUAL_PROMPTS = ["I do my best work when…", "The best way to reach me is…", "Give me feedback by…",
                  "What drains me, and what energises me", "Things people misread about me", "Ask me about… (I can help with)"]


def build_user_manual():
    b = [header("Personal User Manual",
                "A short guide to working with each person: how they like to work, communicate and get feedback. Four people per board.",
                "Set Up the Team · Working With Me · Popularised by Atlassian's Team Playbook",
                header_fields(["Team", "Date"]))]

    colors = [PURPLE, BLUE, EMERALD, ORANGE]
    hh = (1060 - 148 - 14) / 2
    for k, color in enumerate(colors):
        x, w = (24, 808) if k % 2 == 0 else (846, 810)
        y = 148 + (k // 2) * (hh + 14)
        d = color[0]
        b.append(panel(x, y, w, hh, k + 1, "Working With Me", color, "ONE PERSON PER BLOCK"))
        b.append(field(x + 18, y + 84, "Name:", x + 290, d))
        b.append(field(x + 306, y + 84, "Role:", x + 520, d))
        b.append(field(x + 536, y + 84, "Hours / time zone:", x + w - 18, d))
        cw = (w - 36 - 24) / 2
        for i, p in enumerate(MANUAL_PROMPTS):
            px = x + 18 + (i % 2) * (cw + 24)
            py = y + 126 + (i // 2) * 106
            b.append(label(px, py, p, d))
            b.append(lines(px, py + 28, px + cw, 3, 24))

    b.append(footer("What's one thing about working with you that would save your teammates time?",
                    "What will you do differently now you've read each other's?",
                    "Set Up the Team · Know Each Other · Work Better Together"))
    write_board("user-manual-board", "Personal User Manual",
                "A3 landscape board with four personal user manual blocks: name, role and hours, then how each person "
                "does their best work, likes to be reached and given feedback, what drains and energises them, what "
                "people misread, and what to ask them about.", "\n".join(b))


# ---------------------------------------------------------------- levels of conflict

CONFLICT_LEVELS = [
    ("Problem to Solve", EMERALD,
     ["Different views, shared goal. Information is", "shared openly; people focus on the problem."],
     ["“Let's work out what's", "going on here.”"],
     "Collaborate", ["Facilitate, then let the team solve it.", "Help them reach a decision together."]),
    ("Disagreement", AMBER,
     ["Self-protection creeps in. People keep their", "distance and talk in general terms."],
     ["“I hear you, but…”", "“Some people think…”"],
     "Support", ["Coach them to resolve it themselves;", "make sure each side is heard."]),
    ("Contest", ORANGE,
     ["Winning matters more than solving. Sides", "form, facts get distorted, it gets personal."],
     ["“You always…”", "“They never…”"],
     "Facilitate", ["Get back to facts and interests;", "run a structured conversation."]),
    ("Crusade", RED,
     ["Protecting one's own group. Positions harden", "into principles; the other side is the problem."],
     ["“They're just like that.”", "“It's the principle.”"],
     "Mediate", ["Bring in a neutral third party;", "talk with each group separately first."]),
    ("World War", ("#7F1D1D", "#FEE2E2"),
     ["Destroy the other side. Little talk, open", "hostility; real harm is possible."],
     ["Little is said;", "people avoid each other."],
     "Protect people", ["Separate the parties and escalate now:", "HR or leadership, not the team."]),
]


def build_conflict_levels():
    b = [header("Levels of Conflict",
                "Notice how far a conflict has gone, then choose a response that fits, from letting the team solve it to stepping in.",
                "Facilitate & Coach · Five Levels of Conflict (Speed B. Leas) · via Lyssa Adkins, Coaching Agile Teams",
                legend([("dot", EMERALD[0], "Level 1: healthy"), ("dot", "#B91C1C", "Level 5: get help")]))]

    y, h = 148, 560
    x, w = 24, 1082
    b.append(panel(x, y, w, h, 1, "What Level Are We At?", SLATE, "LISTEN TO THE LANGUAGE"))
    x2, w2 = 1120, 536
    b.append(panel(x2, y, w2, h, 2, "The Coach's Move", BLUE, "LEVELS 4–5: GET HELP"))
    x0 = x + 14
    for cx, s in [(x0 + 16, "LEVEL"), (x0 + 262, "WHAT YOU SEE"), (x0 + 636, "WHAT YOU HEAR"), (x0 + 950, "SEEN?")]:
        b.append(T(cx, y + 80, s, 8.5, SLATE[0], MONO, weight=600, ls=".1em"))
    b.append(T(x2 + 18, y + 80, "WHAT TO DO", 8.5, BLUE[0], MONO, weight=600, ls=".1em"))
    rh, gap = 84, 7
    for i, (name, color, see, hear, move, how) in enumerate(CONFLICT_LEVELS):
        dk = color[0]
        ry = y + 92 + i * (rh + gap)
        b.append(R(x0, ry, w - 28, rh, "white", 6, f' stroke="{dk}" stroke-opacity=".25"'))
        b.append(R(x0, ry, 5, rh, dk, 3))
        b.append(f'<circle cx="{x0 + 30}" cy="{ry + 28}" r="12" fill="{dk}"/>')
        b.append(T(x0 + 30, ry + 33, str(i + 1), 11, "white", weight=600, anchor="middle"))
        b.append(T(x0 + 50, ry + 33, name, 13, dk, weight=600))
        b.append(para(x0 + 262, ry + 33, see, 10.5, dk, 18))
        b.append(para(x0 + 636, ry + 33, hear, 13, dk, 20, font=SERIF, italic=True))
        b.append(checkbox(x0 + 950, ry + 33, "Seen", dk, 11))
        b.append(L(x0 + 950, ry + 62, x0 + w - 44, ry + 62, WRITE))
        b.append(R(x2 + 14, ry, w2 - 28, rh, "white", 6, f' stroke="{dk}" stroke-opacity=".25"'))
        b.append(R(x2 + 14, ry, 5, rh, dk, 3))
        b.append(T(x2 + 34, ry + 30, f"{i + 1} · {move}", 12, dk, weight=600))
        b.append(para(x2 + 34, ry + 52, how, 10.5, dk, 16))

    y, h = 722, 338
    x, w = 24, 536
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 3, "What's It About?", PURPLE, "FACTS, NOT BLAME"))
    for i, f in enumerate(["The issue (what happened):", "", "Who's involved:", "Going on since:",
                           "What each side needs:", "", ""]):
        if f:
            b.append(field(x + 18, y + 86 + i * 34, f, x + w - 18, d))
        else:
            b.append(L(x + 18, y + 90 + i * 34, x + w - 18, y + 90 + i * 34, WRITE))

    x = 574
    d = AMBER[0]
    b.append(panel(x, y, w, h, 4, "Before You Step In", AMBER, "ASK YOURSELF"))
    for i, s in enumerate(["Is this mine to act on, or the team's to solve?", "Am I neutral? If not, who is?",
                           "Have I heard each side on their own?", "Can the team use its own working agreements?",
                           "Would naming the level help the team see it?", "Is anyone at risk of harm?"]):
        b.append(checkbox(x + 18, y + 88 + i * 32, s, d, 11))
    b.append(T(x + 18, y + h - 40, "Harassment, discrimination or safety concerns:", 11, RED[0], weight=600))
    b.append(T(x + 18, y + h - 22, "don't mediate. Go to HR or your leadership straight away.", 11, RED[0]))

    x, w = 1124, 532
    d = FOREST[0]
    b.append(panel(x, y, w, h, 5, "Our Next Step", FOREST, "AND WHEN TO CHECK AGAIN"))
    for i, f in enumerate(["Level now:", "Move we'll try:", "", "With whom:", "By when:", "Check again on:", "Escalate if:"]):
        if f:
            b.append(field(x + 18, y + 86 + i * 34, f, x + w - 18, d))
        else:
            b.append(L(x + 18, y + 90 + i * 34, x + w - 18, y + 90 + i * 34, WRITE))

    b.append(footer("What words are people using, and what level do they point to?",
                    "Is this conflict about the work, or about each other?",
                    "Facilitate & Coach · Conflict · Healthy Disagreement, Early Help"))
    write_board("conflict-levels-board", "Levels of Conflict",
                "A3 landscape coach's board for diagnosing team conflict with Speed Leas's five levels: what you see and "
                "hear at each level, the coach's move for each, what the conflict is about, questions to ask before "
                "stepping in, and an agreed next step.", "\n".join(b))


# ---------------------------------------------------------------- feedback conversation

SBI = [("Situation", "When and where. Recent,", "specific and factual.", ["“In Tuesday's review…”"]),
       ("Behaviour", "What you saw or heard.", "No labels, no guesses.", ["“…you cut Priya off", "twice…”"]),
       ("Impact", "The effect on you, the", "team or the work.", ["“…and we didn't hear", "her view on the risk.”"]),
       ("Request", "What you'd like next,", "then ask for their view.", ["“Could you let people", "finish? How did it seem", "to you?”"])]


def build_feedback():
    b = [header("Feedback Conversation",
                "Prepare and hold one feedback conversation: describe what happened and its effect, listen, and agree what happens next.",
                "Facilitate & Coach · Situation–Behaviour–Impact (Center for Creative Leadership) · Feedback Both Ways",
                header_fields(["With", "Date"]))]

    x, y, w, h = 24, 148, 1632, 150
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "Check Yourself First", SLATE, "BEFORE YOU BOOK IT"))
    for i, s in enumerate(["My intent is to help, not to win", "It's recent and specific", "I'll say it in private",
                           "I'm ready to listen, too", "It's a good time for them"]):
        b.append(checkbox(x + 18 + i * 322, y + 86, s, d, 11))
    b.append(field(x + 18, y + 122, "What I want for them from this conversation:", x + w - 18, d))

    y, h = 312, 440
    x, w = 24, 1082
    d = BLUE[0]
    b.append(panel(x, y, w, h, 2, "Prepare It", BLUE, "SITUATION · BEHAVIOUR · IMPACT · REQUEST"))
    cw = (w - 28 - 30) / 4
    for i, (name, h1, h2, ex) in enumerate(SBI):
        cx = x + 14 + i * (cw + 10)
        b.append(R(cx, y + 64, cw, h - 78, "white", 6, f' stroke="{d}" stroke-opacity=".2"'))
        b.append(f'<circle cx="{cx + 22:g}" cy="{y + 88}" r="11" fill="{d}"/>')
        b.append(T(cx + 22, y + 92, "SBIR"[i], 10.5, "white", weight=600, anchor="middle"))
        b.append(T(cx + 40, y + 93, name, 12, d, weight=600))
        b.append(para(cx + 14, y + 122, [h1, h2], 10.5, d, 15))
        b.append(para(cx + 14, y + 168, ex, 12.5, d, 18, font=SERIF, italic=True))
        b.append(T(cx + 14, y + 236, "What I'll say:", 9.5, d, op=".88"))
        b.append(lines(cx + 14, y + 264, cx + cw - 14, 6, 26))

    x, w = 1120, 536
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 3, "Hear It Back", EMERALD, "IT'S A CONVERSATION"))
    b.append(T(x + 18, y + 80, "QUESTIONS TO ASK", 8.5, d, MONO, weight=600, ls=".12em"))
    for j, q in enumerate(["“How did it look from your side?”", "“What did I miss?”", "“What would help?”"]):
        b.append(T(x + 18, y + 106 + j * 24, q, 14, d, SERIF, italic=True))
    for i, f in enumerate(["Their view:", "", "", "What I learned:", "", "", "Feedback for me:", ""]):
        if f:
            b.append(field(x + 18, y + 200 + i * 28, f, x + w - 18, d))
        else:
            b.append(L(x + 18, y + 204 + i * 28, x + w - 18, y + 204 + i * 28, WRITE))

    y, h = 766, 294
    x, w = 24, 808
    d = FOREST[0]
    b.append(panel(x, y, w, h, 4, "Agree Next Steps", FOREST, "BOTH OF US"))
    b.append(table(x + 18, y + 86, [("Who", 150), ("Will do", 440), ("By when", w - 36 - 590)], 4, d, 34))
    b.append(field(x + 18, y + h - 30, "We'll check in on:", x + w - 18, d))

    x, w = 846, 810
    d = AMBER[0]
    b.append(panel(x, y, w, h, 5, "Praise Works the Same Way", AMBER, "SAY WHAT WENT WELL, SPECIFICALLY"))
    for i, f in enumerate(["Situation:", "Behaviour:", "Impact:"]):
        b.append(field(x + 18, y + 86 + i * 36, f, x + w - 18, d))
    b.append(T(x + 18, y + 210, "RECEIVING FEEDBACK", 8.5, d, MONO, weight=600, ls=".12em"))
    b.append(T(x + 18, y + 236, "Listen to the end · Ask to understand, not to defend · Say thank you", 11, d))
    b.append(T(x + 18, y + 258, "Then decide what you'll do with it, in your own time.", 11, d))

    b.append(footer("Did I describe what happened, or judge who they are?",
                    "What would I want to know if it were me?",
                    "Facilitate & Coach · Feedback · Kind, Clear, Specific"))
    write_board("feedback-conversation-board", "Feedback Conversation",
                "A3 landscape board for preparing and holding a feedback conversation: a self-check, situation, behaviour, "
                "impact and request with examples, questions to hear the other side, agreed next steps, and using the same "
                "shape for praise.", "\n".join(b))


# ---------------------------------------------------------------- motivation & recognition

MOTIVATORS = [("Curiosity", "Plenty to explore and learn"), ("Honour", "My work fits my values"),
              ("Acceptance", "People approve of me and what I do"), ("Mastery", "Work that stretches my skills"),
              ("Power", "I can influence what happens"), ("Freedom", "Independence in my own work"),
              ("Relatedness", "Good relationships at work"), ("Order", "Enough structure and stability"),
              ("Goal", "My work serves a purpose I care about"), ("Status", "My position is recognised")]


def build_motivation():
    b = [header("Motivation & Recognition",
                "Find out what motivates each person, test how a change will affect it, and thank people specifically and often.",
                "Lead the Organisation · Inspired by Management 3.0 (Jurgen Appelo) · Moving Motivators & Kudo Cards",
                header_fields(["Name", "Date"]))]

    x, y, w, h = 24, 148, 1632, 230
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 1, "The Ten Motivators", PURPLE, "WRITE EACH ON A CARD OR STICKY"))
    cw = (w - 28 - 4 * 10) / 5
    for i, (name, desc) in enumerate(MOTIVATORS):
        cx = x + 14 + (i % 5) * (cw + 10)
        cy = y + 64 + (i // 5) * 80
        b.append(R(cx, cy, cw, 70, "white", 6, f' stroke="{d}" stroke-opacity=".2"'))
        # one <text> per card so the whiteboard prompt keeps each name with its description
        b.append(f'<text x="{cx + 16:g}" y="{cy + 28}" font-family="{SANS}" fill="{d}">'
                 f'<tspan font-size="12.5" font-weight="600">{name}</tspan><tspan fill-opacity="0">: </tspan>'
                 f'<tspan x="{cx + 16:g}" dy="22" font-size="10.5">{escape(desc)}</tspan></text>')

    y, h = 392, 420
    d = BLUE[0]
    b.append(panel(x, y, w, h, 2, "Rank Them, Then Test a Change", BLUE, "LEFT TO RIGHT · THEN MOVE UP OR DOWN"))
    b.append(field(x + 18, y + 84, "The change we're testing:", x + w - 18, d))
    cw = (w - 28 - 9 * 10) / 10
    for i in range(10):
        cx = x + 14 + i * (cw + 10)
        b.append(R(cx, y + 108, cw, 86, "url(#dots)", 6))
        b.append(T(cx + cw / 2, y + 156, "↑", 16, d, anchor="middle", op=".35"))
        b.append(slot(cx, y + 202, cw, 70, BLUE[1], d, f"Card {i + 1}"))
        b.append(R(cx, y + 280, cw, 86, "url(#dots)", 6))
        b.append(T(cx + cw / 2, y + 328, "↓", 16, d, anchor="middle", op=".35"))
    b.append(T(x + 14, y + 130, "MORE MOTIVATED", 8.5, d, MONO, weight=600, ls=".1em"))
    b.append(T(x + 14, y + 358, "LESS MOTIVATED", 8.5, d, MONO, weight=600, ls=".1em"))
    b.append(L(x + 14, y + 388, x + w - 30, y + 388, d, 1.2, ' stroke-opacity=".5"'))
    b.append(T(x + w - 14, y + 393, "›", 16, d, anchor="end", op=".6"))
    b.append(T(x + 14, y + 408, "LEAST IMPORTANT TO ME", 8.5, d, MONO, weight=600, ls=".1em"))
    b.append(T(x + w - 14, y + 408, "MOST IMPORTANT TO ME", 8.5, d, MONO, weight=600, ls=".1em", anchor="end"))

    y, h = 826, 234
    x, w = 24, 536
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 3, "What I Learned", EMERALD, "SHARE WHAT YOU CHOOSE"))
    for i, f in enumerate(["What surprised me:", "What I need more of:", "What I'll ask for:", "What I can offer others:"]):
        b.append(field(x + 18, y + 86 + i * 36, f, x + w - 18, d))

    x, w = 574, 1082
    d = AMBER[0]
    b.append(panel(x, y, w, h, 4, "Kudo Cards", AMBER, "SPECIFIC · TIMELY · OFTEN"))
    kw = (w - 28 - 20) / 3
    for i in range(3):
        kx = x + 14 + i * (kw + 10)
        ky = y + 64
        b.append(R(kx, ky, kw, 156, "white", 6, f' stroke="{d}" stroke-opacity=".25"'))
        for j, s in enumerate(["Thank you", "Well done", "You helped me"]):
            b.append(checkbox(kx + 14 + j * 108, ky + 26, s, d, 10.5))
        b.append(field(kx + 14, ky + 60, "To:", kx + kw - 14, d))
        b.append(field(kx + 14, ky + 92, "For:", kx + kw - 14, d))
        b.append(L(kx + 14, ky + 120, kx + kw - 14, ky + 120, WRITE))
        b.append(field(kx + 14, ky + 144, "From:", kx + kw - 14, d))

    b.append(footer("Which motivator would this change put at risk, and for whom?",
                    "Who deserves a thank-you this week, and for what exactly?",
                    "Lead the Organisation · Intrinsic Motivation · Recognition"))
    write_board("motivation-board", "Motivation & Recognition",
                "A3 landscape board: the ten motivators, a row of ten cards to rank from least to most important and move "
                "up or down to test a change, what each person learned, and kudo cards for specific thanks.", "\n".join(b))


# ---------------------------------------------------------------- design sprint

SPRINT_DAYS = [("Map", "MONDAY", BLUE, ["Agree the long-term goal", "Map the customer journey",
                                         "Ask the experts; note “How might we…?”", "Pick a target on the map"], "Our target:"),
               ("Sketch", "TUESDAY", PURPLE, ["Lightning demos of existing ideas", "Sketch solutions alone, in four steps",
                                               "Recruit five customers for Friday"], "Sketches made:"),
               ("Decide", "WEDNESDAY", ORANGE, ["Silent gallery and heat-map dots", "Straw poll, then the Decider chooses",
                                                "Storyboard the prototype"], "Winning idea:"),
               ("Prototype", "THURSDAY", EMERALD, ["Build a realistic façade, not the product", "Split roles: makers, writer, stitcher",
                                                    "Trial run; write the interview script"], "Prototype is a:"),
               ("Test", "FRIDAY", FOREST, ["Five one-to-one customer interviews", "The team watches and takes notes",
                                            "Look for patterns across interviews"], "Patterns we saw:")]


def build_design_sprint():
    b = [header("Design Sprint",
                "Answer a big question in five days: map the problem, sketch ideas, decide, build a realistic prototype and test it with customers.",
                "Decide What to Build · Design Sprint (Jake Knapp, GV) · Map · Sketch · Decide · Prototype · Test",
                header_fields(["Sprint", "Dates", "Decider"]))]

    y, h = 148, 210
    x, w = 24, 808
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "Challenge & Goal", SLATE, "MONDAY MORNING"))
    for i, f in enumerate(["The challenge:", "Long-term goal (in two years…):", "Sprint questions (what could stop us?):", ""]):
        if f:
            b.append(field(x + 18, y + 86 + i * 34, f, x + w - 18, d))
        else:
            b.append(L(x + 18, y + 90 + i * 34, x + w - 18, y + 90 + i * 34, WRITE))

    x, w = 846, 810
    d = SKY[0]
    b.append(panel(x, y, w, h, 2, "The Sprint Team", SKY, "SEVEN OR FEWER"))
    for i, f in enumerate(["Decider:", "Facilitator:", "Customer expert:", "Tech expert:", "Design:", "Business / money:"]):
        b.append(field(x + 18 + (i % 2) * 392, y + 86 + (i // 2) * 40, f, x + 18 + (i % 2) * 392 + 368, d))

    y, h = 372, 480
    cw = (1632 - 4 * 14) / 5
    for i, (name, day, color, steps, out) in enumerate(SPRINT_DAYS):
        x = 24 + i * (cw + 14)
        dk = color[0]
        b.append(panel(x, y, cw, h, i + 3, name, color, day))
        b.append(bullets(x + 22, y + 84, steps, dk, 24))
        b.append(T(x + 18, y + 190, "WHAT WE PRODUCED", 8.5, dk, MONO, weight=600, ls=".12em"))
        b.append(sticky_zone(x + 14, y + 202, cw - 28, h - 270, dk, "Stickies, sketches, photos", (YELLOW,)))
        b.append(field(x + 18, y + h - 30, out, x + cw - 18, dk))

    y, h = 866, 194
    x, w = 24, 1082
    d = FOREST[0]
    b.append(panel(x, y, w, h, 8, "Friday's Results", FOREST, "✓ WORKED · ✗ DIDN'T · ? UNCLEAR"))
    rest = (w - 36 - 482) / 5
    b.append(table(x + 18, y + 80, [("Sprint question or target", 482)] + [(f"Customer {i + 1}", rest) for i in range(5)], 3, d, 30))

    x, w = 1120, 536
    d = RED[0]
    b.append(panel(x, y, w, h, 9, "What Next?", RED, "THE DECIDER CALLS IT"))
    for i, s in enumerate(["Build it", "Iterate and test again", "Change direction", "Stop here"]):
        b.append(checkbox(x + 18 + (i % 2) * 250, y + 86 + (i // 2) * 30, s, d, 11))
    b.append(field(x + 18, y + 158, "First step and owner:", x + w - 18, d))

    b.append(footer("What question, if answered on Friday, would make this week worth it?",
                    "What did customers do, not just say?",
                    "Decide What to Build · Design Sprint · Learn in Five Days"))
    write_board("design-sprint-board", "Design Sprint",
                "A3 landscape board for a five-day design sprint: challenge, long-term goal and sprint questions, the team, "
                "Monday to Friday panels (map, sketch, decide, prototype, test) with steps and outputs, a results grid "
                "for five customer interviews, and the decision on what happens next.", "\n".join(b))


# ---------------------------------------------------------------- product bet canvas

def build_product_bet():
    b = [header("Product Bet Canvas",
                "Treat a new product or feature as a bet: who has the problem, what you believe, the riskiest assumptions, and how you'll find out cheaply.",
                "Decide What to Build · Bets, Not Plans · Four Big Risks (Marty Cagan) · Test the Riskiest Assumption First",
                header_fields(["Idea", "Owner", "Date"]))]

    y, h = 148, 300
    x, w = 24, 536
    d = RED[0]
    b.append(panel(x, y, w, h, 1, "The Problem", RED, "WHOSE, AND HOW BAD?"))
    for i, f in enumerate(["Who has it:", "The problem, in their words:", "", "How they cope today:", "",
                           "How often, how painful (1–5):"]):
        if f:
            b.append(field(x + 18, y + 86 + i * 34, f, x + w - 18, d))
        else:
            b.append(L(x + 18, y + 90 + i * 34, x + w - 18, y + 90 + i * 34, WRITE))

    x, w = 574, 1082
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Our Bet", PURPLE, "ONE SENTENCE, FOUR PARTS"))
    for i, f in enumerate(["We believe that (who):", "will (do what):", "if we (offer what):", "because (what we know):",
                           "The smallest version we could try:", ""]):
        if f:
            b.append(field(x + 18, y + 86 + i * 34, f, x + w - 18, d, 12 if i < 4 else 11))
        else:
            b.append(L(x + 18, y + 90 + i * 34, x + w - 18, y + 90 + i * 34, WRITE))

    y, h = 462, 310
    x, w = 24, 536
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 3, "Why It's Worth It", EMERALD, "VALUE AND COST"))
    for i, f in enumerate(["Value to users:", "", "Value to us:", "", "Cost of doing nothing:", "Roughly what it'll take:"]):
        if f:
            b.append(field(x + 18, y + 86 + i * 36, f, x + w - 18, d))
        else:
            b.append(L(x + 18, y + 90 + i * 36, x + w - 18, y + 90 + i * 36, WRITE))

    x = 574
    d = AMBER[0]
    b.append(panel(x, y, w, h, 4, "Riskiest Assumptions", AMBER, "CONFIDENCE 1 (GUESS) – 5 (PROVEN)"))
    b.append(table(x + 18, y + 86, [("Risk", 120), ("We're assuming…", w - 36 - 210), ("Conf.", 90)], 4, d, 48))
    for i, (risk, q) in enumerate([("Value", "Will they want it?"), ("Usability", "Can they use it?"),
                                   ("Feasibility", "Can we build it?"), ("Viability", "Does it work for us?")]):
        ry = y + 96 + i * 48
        b.append(T(x + 24, ry + 22, risk, 11, d, weight=600))
        b.append(T(x + 24, ry + 38, q, 9.5, d, op=".88"))

    x, w = 1124, 532
    d = BLUE[0]
    b.append(panel(x, y, w, h, 5, "How We'll Test It", BLUE, "CHEAPEST FIRST"))
    b.append(table(x + 18, y + 86, [("Test", 190), ("Signal we need", w - 36 - 290), ("By when", 100)], 6, d, 34))

    y, h = 786, 274
    x, w = 24, 808
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "Measures of Success", FOREST, "HOW WE'LL KNOW IT PAID OFF"))
    b.append(table(x + 18, y + 86, [("Measure", 330), ("Now", 120), ("Target", 120), ("By when", w - 36 - 570)], 3, d, 34))
    b.append(field(x + 18, y + h - 30, "We'll stop or change course if:", x + w - 18, d))

    x, w = 846, 810
    d = SLATE[0]
    b.append(panel(x, y, w, h, 7, "Decision", SLATE, "GO, TEST, PARK OR NO"))
    for i, s in enumerate(["Go: build the smallest version", "Test first: run the tests above",
                           "Park it: revisit later", "No: not worth it, and here's why"]):
        b.append(checkbox(x + 18 + (i % 2) * 392, y + 88 + (i // 2) * 32, s, d, 11))
    for i, f in enumerate(["Why:", "Decided by:", "Revisit on:"]):
        b.append(field(x + 18, y + 164 + i * 34, f, x + w - 18, d))

    b.append(footer("What would have to be true for this to be a good bet?",
                    "What's the cheapest way to find out we're wrong?",
                    "Decide What to Build · Bets, Not Plans · Learn Before You Build"))
    write_board("product-bet-canvas", "Product Bet Canvas",
                "A3 landscape canvas for a product or feature bet: the problem and who has it, the bet as one sentence, "
                "why it's worth it, the riskiest value, usability, feasibility and viability assumptions, how to test "
                "them, measures of success, and a go, test, park or no decision.", "\n".join(b))


# ---------------------------------------------------------------- ai in delivery

def build_ai_delivery():
    b = [header("AI in Delivery",
                "Decide where AI and AI agents fit in how you deliver, the guardrails for each, who's accountable, and whether it's helping.",
                "Lead the Organisation · AI Governance · Assist · Approve · Act · People Stay Accountable",
                header_fields(["Scope", "Owner", "Review date"]))]

    y, h = 148, 330
    x, w = 24, 1082
    d = BLUE[0]
    b.append(panel(x, y, w, h, 1, "Where AI Fits", BLUE, "TICK ONE AUTONOMY LEVEL PER STAGE"))
    cols = [("Stage", 190), ("Where we use it", 360), ("Assists", 100), ("Acts, we approve", 130), ("Acts alone", 100)]
    cols.append(("Human check", w - 36 - sum(c for _, c in cols)))
    b.append(table(x + 18, y + 86, cols, 6, d, 34))
    for i, s in enumerate(["Discover & research", "Plan & refine", "Build", "Test", "Release & deploy", "Operate & support"]):
        b.append(T(x + 24, y + 118 + i * 34, s, 11, d, weight=600))
        for cx in (x + 18 + 550 + 44, x + 18 + 650 + 59, x + 18 + 780 + 44):
            b.append(R(cx, y + 108 + i * 34, 12, 12, "white", 2, f' stroke="{d}" stroke-opacity=".6" stroke-width="1.2"'))

    x, w = 1120, 536
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 2, "Autonomy Levels", PURPLE, "MOVE UP ONLY WITH EVIDENCE"))
    for i, (name, line1, line2) in enumerate([("1 · Assists", "AI suggests; a person decides and does the work.", "Lowest risk. Start here."),
                                              ("2 · Acts, we approve", "AI does the work; a person reviews it", "before it counts."),
                                              ("3 · Acts alone", "AI acts within set limits; people check", "afterwards and can stop it.")]):
        cy = y + 66 + i * 84
        b.append(R(x + 14, cy, w - 28, 74, "white", 6, f' stroke="{d}" stroke-opacity=".2"'))
        b.append(T(x + 30, cy + 26, name, 12, d, weight=600))
        b.append(para(x + 30, cy + 46, [line1, line2], 10.5, d, 16))

    y, h = 492, 300
    x, w = 24, 536
    d = RED[0]
    b.append(panel(x, y, w, h, 3, "Guardrails", RED, "AGREED BEFORE WE SCALE"))
    for i, s in enumerate(["No confidential or personal data in unapproved tools", "AI output is reviewed like any other change",
                           "Agents get the least access they need", "Generated code passes the same tests and scans",
                           "AI use is visible in commits and tickets", "Licences and ownership of outputs checked",
                           "A person can stop or roll back any agent"]):
        b.append(checkbox(x + 18, y + 86 + i * 30, s, d, 11))

    x = 574
    d = AMBER[0]
    b.append(panel(x, y, w, h, 4, "Risks to Watch", AMBER, "LIKELIHOOD × IMPACT, 1–3"))
    b.append(table(x + 18, y + 86, [("Risk", 210), ("L × I", 70), ("What we'll do", w - 36 - 280)], 5, d, 36))

    x, w = 1124, 532
    d = SLATE[0]
    b.append(panel(x, y, w, h, 5, "Who's Accountable", SLATE, "PEOPLE, NOT TOOLS"))
    for i, f in enumerate(["Owns the AI policy:", "Approves new tools:", "Approves agent access:", "Reviews AI incidents:",
                           "Trains and supports people:", "Questions go to:"]):
        b.append(field(x + 18, y + 86 + i * 34, f, x + w - 18, d))

    y, h = 806, 254
    x, w = 24, 808
    d = EMERALD[0]
    b.append(panel(x, y, w, h, 6, "Is It Helping?", EMERALD, "OUTCOMES, NOT USAGE"))
    b.append(table(x + 18, y + 86, [("Measure", 310), ("Before", 140), ("Now", 140), ("Target", w - 36 - 590)], 4, d, 34))
    for i, s in enumerate(["Lead time for changes", "Change failure rate", "Rework and escaped defects", "Team experience (survey)"]):
        b.append(T(x + 24, y + 118 + i * 34, s, 11, d))

    x, w = 846, 810
    d = FOREST[0]
    b.append(panel(x, y, w, h, 7, "Experiments & Review", FOREST, "SMALL, VISIBLE, REVERSIBLE"))
    b.append(table(x + 18, y + 86, [("Next experiment", 420), ("Owner", 160), ("Review on", w - 36 - 580)], 3, d, 34))
    b.append(field(x + 18, y + h - 30, "We review this whole board every:", x + w - 18, d))

    b.append(footer("Where would we notice first if AI made our work worse?",
                    "Who's accountable when an agent gets it wrong?",
                    "Lead the Organisation · AI Governance · People Stay Accountable"))
    write_board("ai-delivery-board", "AI in Delivery",
                "A3 landscape board for governing AI across delivery: where AI is used at each stage and at what autonomy "
                "level, the three autonomy levels, guardrails, risks, who is accountable, outcome measures, and experiments "
                "with a review rhythm.", "\n".join(b))


# ---------------------------------------------------------------- event storming

ORANGE_ST, LILAC_ST, PALE_ST, ROSE_ST = "#FDBA74", "#C4B5FD", "#FEF08A", "#FB7185"
STORM_KEY = [("Domain event", ORANGE_ST, "Something that happened,", "in the past tense"),
             ("Command", BLUE_ST, "A request or decision", "that causes an event"),
             ("Actor", YELLOW, "The person or role", "who issues a command"),
             ("Policy", LILAC_ST, "“Whenever this happens,", "we do that”"),
             ("System", PALE_ST, "What accepts a command", "and records the event"),
             ("External system", PINK_ST, "Something outside", "we depend on"),
             ("Read model", GREEN, "Information someone", "needs to decide"),
             ("Hotspot", ROSE_ST, "A question, risk, gap", "or disagreement")]


def build_event_storming():
    b = [header("Event Storming",
                "Map a business domain as a timeline of events with everyone who knows it, to find shared understanding, gaps and boundaries.",
                "Engineering Practices · Event Storming (Alberto Brandolini) · Big Picture · Process · Design",
                header_fields(["Domain", "Date"]))]

    x, y, w, h = 24, 148, 1632, 170
    d = SLATE[0]
    b.append(panel(x, y, w, h, 1, "Sticky Key", SLATE, "ONE COLOUR PER KIND OF STICKY"))
    kw = (w - 28) / 8
    for i, (name, color, l1, l2) in enumerate(STORM_KEY):
        kx = x + 14 + i * kw
        b.append(sticky(kx + 4, y + 70, 30, color))
        # one <text> per key entry so the whiteboard prompt keeps each name with its meaning
        b.append(f'<text x="{kx + 44:g}" y="{y + 90}" font-family="{SANS}" fill="{d}">'
                 f'<tspan font-size="11.5" font-weight="600">{escape(name)}</tspan><tspan fill-opacity="0">: </tspan>'
                 f'<tspan x="{kx + 4:g}" dy="36" font-size="10">{escape(l1)} </tspan>'
                 f'<tspan x="{kx + 4:g}" dy="15" font-size="10">{escape(l2)}</tspan></text>')

    y, h = 332, 520
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 2, "The Timeline", ORANGE, "EVENTS FIRST · THEN ORDER · THEN THE REST"))
    pw = (w - 28) / 4
    for i in range(4):
        px = x + 14 + i * pw
        b.append(field(px + 8, y + 84, "Phase:", px + pw - 20, d, 10.5))
        if i:
            b.append(L(px, y + 70, px, y + h - 52, d, 1, ' stroke-opacity=".25" stroke-dasharray="6,5"'))
    b.append(R(x + 14, y + 100, w - 28, h - 160, "url(#dots)", 6))
    b.append(L(x + 14, y + h - 34, x + w - 34, y + h - 34, d, 1.2, ' stroke-opacity=".5"'))
    b.append(T(x + w - 14, y + h - 29, "›", 16, d, anchor="end", op=".6"))
    b.append(T(x + 14, y + h - 16, "TIME", 8.5, d, MONO, weight=600, ls=".12em"))
    b.append(T(x + w / 2, y + h - 16, "Orange events left to right in time, other colours around them · Dashed lines mark "
               "pivotal events, where the story changes phase", 9.5, d,
               italic=True, anchor="middle", op=".88"))

    y, h = 866, 194
    x, w = 24, 536
    d = RED[0]
    b.append(panel(x, y, w, h, 3, "Hotspots", RED, "TO RESOLVE, NOT IGNORE"))
    b.append(table(x + 18, y + 80, [("Question or problem", 330), ("Owner", w - 36 - 330)], 3, d, 30))

    x = 574
    d = PURPLE[0]
    b.append(panel(x, y, w, h, 4, "Boundaries We Found", PURPLE, "CANDIDATE CONTEXTS"))
    b.append(table(x + 18, y + 80, [("Area", 170), ("Key events", 210), ("Team", w - 36 - 380)], 3, d, 30))

    x, w = 1124, 532
    d = FOREST[0]
    b.append(panel(x, y, w, h, 5, "Next Steps", FOREST, "ZOOM IN WHERE IT MATTERS"))
    for i, f in enumerate(["Zoom into (process or design):", "Who to invite next:", "Next session:"]):
        b.append(field(x + 18, y + 86 + i * 36, f, x + w - 18, d))

    b.append(footer("What happens in this domain, in the order it really happens?",
                    "Where do people disagree about what happens next?",
                    "Engineering Practices · Event Storming · Shared Understanding"))
    write_board("event-storming-board", "Event Storming",
                "A3 landscape Event Storming board: a key to the eight sticky colours, a large timeline split into phases "
                "by pivotal events, hotspots with owners, candidate boundaries, and next steps.", "\n".join(b))


# ---------------------------------------------------------------- cynefin sense-making

CYNEFIN = [("Complex", PURPLE, "PROBE · SENSE · RESPOND", ["Cause and effect only make sense afterwards.",
                                                         "Run safe-to-fail experiments; amplify what works."],
            "Practice: emergent", "Things we can only learn by trying"),
           ("Complicated", BLUE, "SENSE · ANALYSE · RESPOND", ["Cause and effect can be found with analysis or",
                                                             "expertise. Ask the experts and weigh options."],
            "Practice: good practice (more than one right answer)", "Things experts can work out"),
           ("Chaotic", RED, "ACT · SENSE · RESPOND", ["No visible cause and effect. Act first to",
                                                     "stabilise, then move the situation to complex."],
            "Practice: novel", "Crises needing action now"),
           ("Clear", EMERALD, "SENSE · CATEGORISE · RESPOND", ["Cause and effect are obvious to everyone.",
                                                              "Follow the agreed practice, but watch for complacency."],
            "Practice: best practice · beware the cliff into chaos", "Things with a known right answer")]


def build_cynefin():
    b = [header("Cynefin® Sense-Making",
                "Sort situations by how predictable they are, then choose an approach that fits: analyse, experiment, act or follow the rule.",
                "Lead the Organisation · Inspired by the Cynefin® Framework (Dave Snowden) · Sense-Making · Choose Your Approach",
                header_fields(["Topic", "Date"]))]

    qw, qh = (1082 - 14) / 2, (1060 - 148 - 14) / 2
    for i, (name, color, approach, desc, practice, hint) in enumerate(CYNEFIN):
        x = 24 + (i % 2) * (qw + 14)
        y = 148 + (i // 2) * (qh + 14)
        d = color[0]
        b.append(panel(x, y, qw, qh, i + 1, name, color, approach))
        b.append(para(x + 18, y + 82, desc, 11, d, 18))
        b.append(T(x + 18, y + 128, practice, 10, d, MONO, ls=".04em"))
        b.append(sticky_zone(x + 14, y + 144, qw - 28, qh - 158, d, hint, (YELLOW,)))

    x, w = 1120, 536
    y, h = 148, 330
    d = SLATE[0]
    b.append(panel(x, y, w, h, 5, "Confused? Split It Up", SLATE, "THE CENTRE"))
    b.append(para(x + 18, y + 84, ["When you can't tell which domain you're in, you're",
                                   "in confusion. People fall back on the approach they",
                                   "like best. Break the situation into parts and place",
                                   "each part in a domain."], 11, d, 18))
    for i in range(4):
        b.append(field(x + 18, y + 186 + i * 34, f"Part {i + 1}:", x + w - 18, d))

    y, h = 492, 568
    d = FOREST[0]
    b.append(panel(x, y, w, h, 6, "Our Approach", FOREST, "FOR THE SITUATION WE CHOSE"))
    for i, f in enumerate(["Situation:", "", "Main domain:", "So we will:", "", "Safe-to-fail experiments:", "", "",
                           "Signs it's working:", "Signs to stop:", "Amplify or dampen by:", "", "Revisit on:"]):
        if f:
            b.append(field(x + 18, y + 86 + i * 36, f, x + w - 18, d))
        else:
            b.append(L(x + 18, y + 90 + i * 36, x + w - 18, y + 90 + i * 36, WRITE))

    b.append(footer("Are we treating a complex problem as if it were only complicated?",
                    "What's the smallest safe-to-fail experiment we could run?",
                    "Cynefin® is a registered trademark of Cognitive Edge Pte Ltd · Lead the Organisation"))
    write_board("cynefin-board", "Cynefin® Sense-Making",
                "A3 landscape sense-making board inspired by the Cynefin framework: complex, complicated, chaotic and clear "
                "domains with the approach for each and space to place situations, a confused centre, and the chosen "
                "approach with safe-to-fail experiments and signals.", "\n".join(b))


# ---------------------------------------------------------------- worked examples
# Filled-in copies of real boards for a fictional team (the "Basket team" at an online grocery service, the same
# running example as the Backlog Item Anatomy poster). Each example reads the generated blank board and adds a layer
# of handwriting and sticky notes on top, so it always matches the current board.

HAND = "'Caveat','Segoe Print','Bradley Hand',cursive"
HAND_URL = "https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&display=swap"
PEN = "#1D4ED8"


def hand(x, y, text, size=19, fill=PEN, anchor=None):
    return T(x, y, text, size, fill, HAND, weight=500, anchor=anchor)


def after(x, label, size=11):
    """x position for handwriting written after a field() label."""
    return x + text_w(label, size) + 16


def tick(bx, by, col=PEN):
    """Tick inside a checkbox drawn by checkbox(bx, by, ...)."""
    return f'<path d="M{bx + 2:g},{by - 5:g} l3.5,4.5 l7,-10" fill="none" stroke="{col}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'


def note(x, y, text, color=YELLOW, w=150, h=80, rot=0, size=17):
    words, lines_, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if len(trial) * size * 0.42 > w - 16 and cur:
            lines_.append(cur)
            cur = wd
        else:
            cur = trial
    lines_.append(cur)
    cy = y + h / 2 - (len(lines_) - 1) * size * 0.55 + size * 0.35
    body = "".join(T(x + w / 2, cy + i * size * 1.1, ln, size, INK, HAND, weight=500, anchor="middle") for i, ln in enumerate(lines_))
    return (f'<g transform="rotate({rot} {x + w / 2:g} {y + h / 2:g})">'
            + R(x, y, w, h, color, 3, ' filter="url(#fsm)"') + body + "</g>")


def dots(x, y, n, col=ACCENT):
    return "".join(f'<circle cx="{x + i * 14:g}" cy="{y}" r="5.5" fill="{col}"/>' for i in range(n))


def write_example(base, title, layer, header=None, strip=()):
    stamp = (f'<g transform="rotate(-3 1150 66)"><rect x="1010" y="48" width="280" height="36" rx="5" fill="none" '
             f'stroke="{ACCENT}" stroke-width="2"/>' + T(1150, 71, "WORKED EXAMPLE · FICTIONAL TEAM", 10.5, ACCENT, MONO,
                                                          weight=600, anchor="middle", ls=".12em") + "</g>")
    head = "".join(hand(1462, 64 + i * 30, v, 20, "#FDE68A") for i, v in enumerate(header or []))
    group = f'<g class="worked-example">{stamp}{head}{layer}</g>\n'
    imp = f"<style>@import url('{HAND_URL.replace('&', '&amp;')}');</style>"
    svg = (OUT / f"{base}.svg").read_text(encoding="utf-8")
    svg = svg.replace("<defs>", "<defs>" + imp, 1).replace("</svg>", group + "</svg>")
    svg = re.sub(r'<title id="mg-title">(.*?)</title>', lambda m: f'<title id="mg-title">Example: {m.group(1)}</title>', svg, count=1)
    svg = re.sub(r'<desc id="mg-desc">', '<desc id="mg-desc">Worked example for a fictional team. ', svg, count=1)
    page = (OUT / f"{base}.html").read_text(encoding="utf-8")
    page = re.sub(r"<!-- meta -->.*?<!-- /meta -->\n", "", page, flags=re.S)
    page = page.replace("</svg>", group + "</svg>", 1)
    page = page.replace('<link rel="stylesheet"', f'<link rel="stylesheet" href="{HAND_URL.replace("&", "&amp;")}">\n<link rel="stylesheet"', 1)
    page = re.sub(r"<title>(.*?)</title>", lambda m: f"<title>Example: {title}</title>", page, count=1)
    page = re.sub(r'<title id="mg-title">(.*?)</title>', lambda m: f'<title id="mg-title">Example: {m.group(1)}</title>', page, count=1)
    page = re.sub(r'<desc id="mg-desc">', '<desc id="mg-desc">Worked example for a fictional team. ', page, count=1)
    page = page.replace('<a class="guide"', f'<a class="guide" style="right:auto;left:16px" href="{base}.html">← Blank board</a>\n<a class="guide"', 1)
    # hide the blank board's placeholders: sticky-zone hints, sample chips and the write-in hint
    def clean(t):
        t = re.sub(r'<text[^>]*fill-opacity="\.22"[^>]*>[^<]*</text>', "", t)
        t = re.sub(r'<rect x="[^"]*" y="[^"]*" width="18" height="18" rx="2" fill="#[0-9A-Fa-f]{6}" fill-opacity="\.35"/>', "", t)
        t = re.sub(r'<text[^>]*font-style="italic"[^>]*fill-opacity="\.(?:3|4|45|5)"[^>]*>[^<]*</text>', "", t)
        t = re.sub(r'<rect [^>]*rx="3" fill="#[0-9A-Fa-f]{6}" fill-opacity="\.22"/>', "", t)
        t = re.sub(r'<text[^>]*>sprint, month, quarter…</text>', "", t)
        for label in strip:  # extra placeholder labels this example covers or empties
            t = re.sub(rf'<text[^>]*>{re.escape(label)}</text>', "", t)
        return t
    svg, page = clean(svg), clean(page)
    slug = f"worked-example-{base}"
    page = page.replace(f'<a href="{base}.svg">open the SVG</a>', f'<a href="{slug}.svg">open the SVG</a>')
    page = page.replace(pdf_link(base), pdf_link(slug))
    (OUT / f"{slug}.svg").write_text(svg, encoding="utf-8")
    (OUT / f"{slug}.html").write_text(page, encoding="utf-8")
    print("wrote", slug)


def example_team_charter():
    L_ = []
    L_ += [hand(220, 242, "help returning customers repeat their weekly shop"), hand(66, 275, "in under a minute, so they keep choosing us."),
           hand(220, 308, "busy households who order groceries every week."),
           hand(220, 374, "weekly repeat orders rise from 22% to 30%"), hand(66, 407, "and customers say reordering is “easy”.")]
    rows = [("Priya", "Product owner", "Customer research"), ("Sam", "Developer", "Payments, APIs"),
            ("Jo", "Developer", "Front end, accessibility"), ("Alex", "Tester", "Test automation"),
            ("Mei", "Designer", "Journeys, prototypes"), ("Tom", "Scrum Master", "Facilitation")]
    for i, (a, b_, c) in enumerate(rows):
        y = 266 + i * 32
        L_ += [hand(868, y, a, 17), hand(988, y, b_, 17), hand(1098, y, c, 17)]
    L_ += [note(1290, 262, "Customer first", YELLOW, 150, 70, -3), note(1460, 262, "Finish before starting", YELLOW, 150, 70, 2),
           note(1375, 350, "Speak up early", YELLOW, 150, 70, -1)]
    L_ += [note(60, 580, "We pair on anything risky", YELLOW, 160, 78, -2), note(240, 586, "Core hours 10:00–15:00", YELLOW, 160, 78, 1),
           note(420, 580, "Reviews within one working day", YELLOW, 160, 78, -1), note(600, 588, "It's fine to say “I don't know”", YELLOW, 160, 78, 2),
           note(150, 668, "Cameras optional, voices welcome", YELLOW, 170, 72, 1)]
    L_ += [tick(864, 548), tick(864, 632), hand(866, 724, "Consent by default. Priya decides scope; the team decides how.", 16)]
    vals = [("Iteration length:", "2 weeks"), ("Planning:", "Mon 10:00, 1 hour"), ("Daily sync:", "09:30, 15 min"),
            ("Review:", "Fri, every other week"), ("Retro:", "Fri, after the review"), ("Board / tools:", "Jira + Miro"),
            ("Channels:", "#basket-team")]
    for i, (lab, v) in enumerate(vals):
        L_.append(hand(after(1275, lab), 546 + i * 30, v, 17))
    for i, v in enumerate(["Who it's for and why is clear", "Small enough to finish in a few days", "Examples agreed",
                           "Dependencies known"]):
        L_ += [tick(42, 886 + i * 30), hand(66, 884 + i * 30, v, 17)]
    for i, v in enumerate(["Code reviewed by a second person", "Automated tests pass", "Accessible (WCAG AA)",
                           "Deployed to staging", "Priya has accepted it"]):
        L_ += [tick(590, 886 + i * 30), hand(614, 884 + i * 30, v, 17)]
    L_ += [hand(1138, 884, "talk in person within a day; if we're stuck,", 17), hand(1138, 912, "Tom facilitates.", 17),
           tick(1138, 976), tick(1306, 976), hand(after(1138, "Signed by the team:"), 1018, "Priya · Sam · Jo · Alex · Mei · Tom", 17)]
    write_example("team-charter-board", "Team Charter", "".join(L_), ["Basket team", "3 March"])


def example_sprint_planning():
    L_ = [hand(286, 245, "returning customers can see their last order", 20),
          hand(66, 281, "on the home page and reorder it in one tap.", 20),
          hand(after(42, "We'll know we've achieved it when…"), 328, "a test user reorders in under 60 seconds", 17),
          hand(after(42, "It supports this product goal:"), 368, "Reorder made easy (repeat orders 22% → 30%)", 17)]
    caps = [("Working days:", "9 (one public holiday)"), ("People available:", "5 of 6"), ("Holidays & absences:", "Jo off Thu–Fri"),
            ("Other commitments:", "Support rota, 1 person"), ("Recent throughput (last 3):", "7 · 9 · 8 items"),
            ("Capacity this sprint:", "about 7 items (80%)")]
    for i, (lab, v) in enumerate(caps):
        L_.append(hand(after(864, lab), 232 + i * 30, v, 16))
    for i in (0, 1, 2, 3, 5):
        L_.append(tick(1275, 234 + i * 30))
    goal = ["Show last order on the home page", "Reorder button adds every item", "Offer a substitute if out of stock",
            "Track reorder events"]
    also = ["Save a basket as a favourite", "Reorder from order history", "Tidy the basket API (tech debt)"]
    for i, t in enumerate(goal):
        L_.append(note(52 + (i % 2) * 190, 560 + (i // 2) * 110, t, YELLOW, 170, 84, [-2, 1, 2, -1][i]))
    for i, t in enumerate(also):
        L_.append(note(660 + (i % 2) * 190, 560 + (i // 2) * 110, t, YELLOW, 170, 84, [1, -2, 2][i]))
    L_ += [note(1290, 580, "Stock API is owned by the Warehouse team: needed by Wed", PINK_ST, 170, 96, -2),
           note(1470, 600, "Analytics events need privacy sign-off", YELLOW, 160, 90, 2)]
    for i, (lab, v) in enumerate([("Day 1, we start with:", "Last-order card (Sam and Jo pair)"),
                                  ("Pairing / swarming on:", "Out-of-stock rules (Alex and Priya)"),
                                  ("First thing to finish:", "Last-order card, by Wednesday")]):
        L_.append(hand(after(42, lab), 948 + i * 34, v, 17))
    for k, n in ((2, 1), (3, 3), (4, 2)):
        cx = 916 + k * 108
        L_.append(hand(cx + 24, 964, "|" * n, 24, PEN))
    L_.append(hand(after(864, "Any 1s or 2s? Concerns raised:"), 1030, "None. Alex is worried about test data; Alex owns it.", 16))
    write_example("sprint-planning-board", "Sprint Planning", "".join(L_), ["Basket team", "Sprint 14 · 3–14 Mar"])


def example_prioritisation():
    L_ = [note(110, 290, "Reorder last basket", GREEN, 150, 70, -3), note(280, 330, "Save favourites", GREEN, 140, 66, 2),
          note(500, 300, "Subscription orders", BLUE_ST, 150, 70, 2), note(640, 380, "Personalised offers", BLUE_ST, 150, 70, -2),
          note(150, 560, "Dark mode", YELLOW, 130, 60, 1), note(560, 560, "Rebuild checkout from scratch", PINK_ST, 170, 76, -2)]
    rows = [("Reorder last basket", "8", "8", "3", "19", "2", "9.5", "1"), ("Save favourites", "5", "3", "2", "10", "2", "5.0", "2"),
            ("Subscription orders", "13", "5", "5", "23", "8", "2.9", "3"), ("Personalised offers", "8", "3", "8", "19", "13", "1.5", "4")]
    widths = [196, 66, 66, 92, 60, 80, 92]
    for r, row in enumerate(rows):
        x = 870
        for c, v in enumerate(row):
            L_.append(hand(x, 290 + r * 32, v, 17))
            x += widths[c] if c < len(widths) else 0
    for i, t in enumerate(["Reorder last basket", "Save favourites", "Reorder from history", "Subscriptions (next quarter)"]):
        L_.append(note(866 + i * 200, 600, t, YELLOW, 150, 76, [-2, 1, 2, -1][i]))
    road = [(["Reorder last basket", "Save favourites"], "Repeat orders 22% → 26%"),
            (["Subscription orders", "Reorder reminders"], "Repeat orders → 30%"),
            (["Personalised offers", "Family accounts"], "Bigger baskets")]
    for i, (items, outcome) in enumerate(road):
        cx = 34 + i * 541.3
        for j, t in enumerate(items):
            L_.append(note(cx + 40 + j * 200, 890, t, YELLOW, 170, 78, [-2, 2][j]))
        L_.append(hand(after(cx + 14, "Outcome:"), 1032, outcome, 17))
    write_example("prioritisation-board", "Prioritisation Board", "".join(L_), ["Reorder made easy", "10 March"])


def example_retro():
    cw = (1632 - 28) / 3
    cols = [["Pair on risky stories", "Demo to a real user", "Write examples before coding"],
            ["Starting new work while items are blocked", "Long debates in planning", "Skipping the retro when busy"],
            ["Walking the board every morning", "Friday demos", "Celebrating small wins"]]
    votes = [[3, 1, 2], [4, 2, 0], [1, 0, 1]]
    L_ = []
    for c, items in enumerate(cols):
        x = 24 + c * (cw + 14)
        for i, t in enumerate(items):
            nx, ny = x + 40 + (i % 2) * 230, 380 + (i // 2) * 200 + (i % 2) * 40
            L_.append(note(nx, ny, t, YELLOW if c != 0 or i else GREEN, 190, 96, [-3, 2, -1][i]))
            if votes[c][i]:
                L_.append(dots(nx + 20, ny + 112, votes[c][i]))
    L_.append(hand(880, 887, "sprint 14", 19, "#FDE68A"))
    acts = [("Pair on anything touching payments", "Sam", "every payments story has a pair"),
            ("WIP limit of 3 items in progress", "Tom", "the limit is on the board and kept for 2 weeks"),
            ("Example Mapping before planning", "Priya", "top 3 items mapped before each planning")]
    for i, (a, o, d) in enumerate(acts):
        x = 24 + i * 548
        L_ += [hand(x + 118, 940, a, 17), hand(after(x + 22, "Owner:"), 976, o, 17), hand(after(x + 22, "Done when:"), 1012, d, 16)]
    write_example("retro-board-start-stop-continue", "Start · Stop · Continue", "".join(L_))


def link(x1, y1, x2, y2, dash=""):
    """A hand-drawn connector between two stickies (dash matches the board's interaction-mode key)."""
    return L(x1, y1, x2, y2, PEN, 2.4, dash + ' stroke-linecap="round"')


def example_team_topology():
    L_ = []
    types = [["Basket · Search & Browse", "Checkout"], ["Store Platform (cloud, CI/CD)"],
             ["Test Automation coaches (to June)"], ["Payments"]]
    cw = (1632 - 28 - 36) / 4
    for i, names in enumerate(types):
        for j, t in enumerate(names):
            L_.append(hand(38 + 16 + i * (cw + 12), 354 + j * 26, t, 17))
    # team map: one value stream across the top, supporting teams below
    L_.append(hand(56, 548, "Customer shopping stream", 17))
    teams = {"search": (56, 566, "Search & Browse"), "basket": (296, 566, "Basket"), "checkout": (536, 566, "Checkout"),
             "pay": (836, 566, "Payments"), "plat": (296, 724, "Store Platform"), "coach": (676, 724, "Test Automation coaches")}
    xs = ' stroke-dasharray="8,5"'
    fac = ' stroke-dasharray="2,4"'
    L_ += [link(686, 594, 836, 594),
           link(686, 610, 836, 610, xs), link(371, 636, 371, 724, xs), link(611, 636, 451, 744, xs),
           link(131, 636, 296, 744, xs), link(751, 724, 431, 636, fac)]
    for k, (x, y, t) in teams.items():
        col = YELLOW
        L_.append(note(x, y, t, col, 150, 70, {"search": -2, "basket": 1, "checkout": -1, "pay": 2, "plat": -1, "coach": 1}[k]))
    L_.append(note(886, 690, "Every Checkout release waits for Payments sign-off", PINK_ST, 180, 86, 3))
    L_.append(hand(700, 588, "subscriptions", 15))
    # cognitive load
    rows = [("Basket", "basket, reorder, favourites", "M", "no"), ("Checkout", "checkout, promos, delivery slots", "H", "yes"),
            ("Payments", "cards, wallets, refunds, fraud", "H", "watch"), ("Search & Br.", "search, catalogue, recs", "M", "no"),
            ("Store Platform", "cloud, CI/CD, monitoring", "M", "no")]
    for i, row in enumerate(rows):
        x = 1144
        for c, v in enumerate(row):
            L_.append(hand(x, 574 + i * 40, v, 16))
            x += (120, 200, 90)[c] if c < 3 else 0
    L_.append(hand(1140, 852, "Checkout owns three domains: delivery slots should move.", 16))
    agree = [("Checkout", "Payments", "Collaboration", "Build subscription payments", "30 June"),
             ("Checkout", "Store Platform", "X-as-a-Service", "Self-service deploy pipeline", "September")]
    for i, row in enumerate(agree):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 1002 + i * 34, v, 17))
            x += (180, 180, 200, 330)[c] if c < 4 else 0
    for i, t in enumerate(["New Delivery Slots team takes slots from Checkout", "Payments publishes a self-service refunds API",
                           "Review Checkout–Payments collaboration on 30 June"]):
        L_.append(hand(1140, 969 + i * 26, t, 16))
    write_example("team-topology-board", "Team Topology Design", "".join(L_))


def example_skills_matrix():
    L_ = []
    skills = ["Discovery", "UX design", "Front end", "Accessibility", "Back end, APIs", "Payments", "Test automation",
              "Data", "Cloud, CI/CD", "Facilitation"]
    sk_w = (1632 - 28 - 380) / 10
    for i, s in enumerate(skills):
        L_.append(hand(38 + 170 + i * sk_w + 10, 249, s, 15))
    team = [("Priya", [3, 1, 0, 0, 0, 1, 0, 2, 0, 2], "SQL for our own reports"),
            ("Sam", [1, 0, 2, 1, 3, 3, 2, 1, 2, 0], "Facilitation"),
            ("Jo", [1, 2, 3, 3, 2, 0, 1, 0, 1, 1], "Payments"),
            ("Alex", [1, 0, 1, 2, 1, 1, 3, 1, 2, 0], "Cloud, CI/CD"),
            ("Mei", [2, 3, 1, 2, 0, 0, 0, 1, 0, 1], "Front end (CSS)"),
            ("Tom", [1, 0, 0, 0, 0, 0, 1, 1, 0, 3], "Data and analytics"),
            ("Ravi (new)", [0, 0, 2, 1, 2, 0, 1, 0, 1, 0], "Payments, test automation")]
    rh = (640 - 64 - 62 - 14) / 8
    for r, (name, scores, wants) in enumerate(team):
        ry = 274 + r * rh
        L_.append(hand(50, ry + rh - 25, name, 19))
        for i, v in enumerate(scores):
            L_.append(hand(208 + i * sk_w + sk_w / 2, ry + 38, str(v), 24, anchor="middle"))
        L_.append(hand(1444, ry + 38, wants, 16))
    for r, i in ((1, 5), (0, 7)):  # the only person at 2+ for a skill
        cx, cy = 208 + i * sk_w + sk_w / 2, 274 + r * rh + 30
        L_.append(f'<ellipse cx="{cx:g}" cy="{cy:g}" rx="24" ry="20" fill="none" stroke="#DC2626" stroke-width="2.2" '
                  f'transform="rotate(-8 {cx:g} {cy:g})"/>')
    L_ += [hand(42, 907, "Payments (only Sam) · Data (only Priya)", 17),
           hand(42, 997, "Cloud, CI/CD · Data", 17)]
    for i, row in enumerate([("Jo", "Payments", "Sam", "end of May"), ("Ravi", "Test automation", "Alex", "June"),
                             ("Tom", "Data", "Priya", "June"), ("Alex", "Cloud, CI/CD", "Platform team", "Q3")]):
        x = 596
        for c, v in enumerate(row):
            L_.append(hand(x, 920 + i * 34, v, 16))
            x += (120, 150, 120)[c] if c < 3 else 0
    L_ += [tick(1138, 920), tick(1138, 980), hand(after(1138, "Next review of the matrix:"), 1028, "start of Q3", 17)]
    write_example("skills-matrix-board", "Skills Matrix", "".join(L_))


def example_health_check():
    # (green, amber, red) votes from 7 people, trend (0 up, 1 flat, 2 down), notes
    rows = [((5, 2, 0), 0, ["Reorder card is a hit"]), ((1, 3, 3), 2, ["FOCUS: releases wait on", "Payments sign-off"]),
            ((4, 3, 0), 1, []), ((2, 4, 1), 1, ["Basket API debt growing"]), ((3, 3, 1), 0, ["Pairing is helping"]),
            ((6, 1, 0), 0, ["Repeat-order goal is clear"]), ((3, 3, 1), 1, ["Scope sometimes set for us"]),
            ((1, 2, 4), 2, ["FOCUS: 3 items blocked", "on other teams"]), ((4, 3, 0), 0, ["WIP limit is working"]),
            ((2, 4, 1), 1, ["Platform tickets are slow"]), ((5, 2, 0), 0, ["Ravi settling in well"])]
    cols = [("#22C55E", 504), ("#F59E0B", 742), ("#EF4444", 980)]
    L_ = []
    for i, (votes, trend, notes) in enumerate(rows):
        ry = 192 + i * 78
        for (col, cx), n in zip(cols, votes):
            L_ += [f'<circle cx="{cx + 26 + k * 24}" cy="{ry + 36}" r="8" fill="{col}" stroke="#fff" stroke-width="1.5"/>'
                   for k in range(n)]
        ax = 1218 + 176 / 2 + (trend - 1) * 46
        L_.append(f'<circle cx="{ax:g}" cy="{ry + 36}" r="20" fill="none" stroke="{PEN}" stroke-width="2.2"/>')
        for j, t in enumerate(notes):
            L_.append(hand(1414, ry + 25 + j * 22, t, 16))
    L_ += [hand(after(24, "Team:", 13), 1102, "Basket team", 19), hand(after(350, "Date:", 13), 1102, "end of Q1", 19),
           hand(after(580, "Facilitator:", 13), 1102, "Tom", 19)]
    write_example("team-health-check-board", "Team Health Check", "".join(L_))


def example_product_vision():
    L_ = [hand(220, 244, "busy households get their weekly shop done in two minutes,", 24),
          hand(44, 285, "and spend the time they save on things that matter more.", 24)]
    cols = [["Busy families who shop every week", "Older customers who buy the same things", "Not for: one-off bulk buyers"],
            ["Rebuilding the weekly shop takes 40 minutes", "Forget items, pay for a second delivery", "Today: a paper list or last receipt"],
            ["One-tap reorder of the last basket", "Saved favourites", "Smart substitutes when out of stock", "Subscriptions for staples"],
            ["Repeat orders 22% → 30%", "Lower cost to serve per order", "Win back lapsed customers"]]
    spots = [(30, 490, -2), (210, 505, 2), (30, 610, 1), (210, 625, -2)]
    for i, items in enumerate(cols):
        x = 24 + i * ((1632 - 42) / 4 + 14)
        for (dx, y, rot), t in zip(spots, items):
            L_.append(note(x + dx, y, t, YELLOW, 160, 92, rot))
    for i, row in enumerate([("Customers reorder easily", "weekly repeat orders", "22%", "30%"),
                             ("Shopping is faster", "median basket time", "38 min", "10 min"),
                             ("Fewer forgotten items", "2nd order within 2 days", "9%", "5%")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 940 + i * 32, v, 17))
            x += (300, 230, 118)[c] if c < 3 else 0
    L_ += [note(880, 948, "Customers want much the same basket each week", YELLOW, 180, 92, -2),
           note(1090, 952, "Stock data is good enough to suggest substitutes", PINK_ST, 180, 92, 2),
           note(1300, 948, "Payments can support subscriptions", YELLOW, 170, 92, -1)]
    write_example("product-vision-board", "Product Vision Board", "".join(L_), ["Basket", "Priya"])


def example_opportunity_tree():
    L_ = [hand(371, 267, "Weekly repeat orders rise from 22% to 30%", 18), hand(371, 291, "by the end of Q2", 18)]
    opps = [(["Rebuilding the weekly shop", "takes too long"],
             [(["Reorder last", "basket in one tap"], ["Customers want much", "the same basket"], ["Fake-door button", "on the home page"], "31% clicked ✓"),
              (["Saved favourites", "list"], ["People will keep", "a list up to date"], ["Interview six", "customers"], "Only 2 of 6 would")]),
            (["I forget items and have to", "place a second order"],
             [(["Reminders for", "usual items"], ["Reminders don't", "annoy people"], ["Email 500", "customers"], "Running"),
              (["“You usually buy”", "list at checkout"], ["Order history", "predicts well"], ["Back-test on the", "last 3 months"], "78% hit rate ✓")]),
            (["Staples run out between", "weekly shops"],
             [(["Subscriptions", "for staples"], ["Payments can do", "repeat billing"], ["Spike with the", "Payments team"], "Due 30 June"),
              (["Auto-add staples", "to the basket"], ["Customers trust", "auto-add"], ["Prototype test", "with 5 users"], "Not started")])]
    colw = (1082 - 40) / 3
    for i, (opp, sols) in enumerate(opps):
        ox = 24 + 20 + i * colw + colw / 2
        bw = colw - 30
        L_ += [hand(ox - bw / 2 + 14, 421 + j * 24, t, 18) for j, t in enumerate(opp)]
        sw = (bw - 12) / 2
        for j, (sol, risk, test, result) in enumerate(sols):
            sx = ox - bw / 2 + j * (sw + 12) + 10
            L_ += [hand(sx, 571 + k * 24, t, 16) for k, t in enumerate(sol)]
            L_ += [hand(sx, 685 + k * 24, t, 15) for k, t in enumerate(risk)]
            L_ += [hand(sx, 779 + k * 24, t, 15) for k, t in enumerate(test)]
            L_.append(hand(sx, 873, result, 15))
    L_ += [note(60, 976, "Shared family lists", BLUE_ST, 140, 64, -2, 15), note(220, 980, "Voice ordering", YELLOW, 130, 60, 2, 15),
           note(370, 976, "Recipe-to-basket", YELLOW, 130, 60, -1, 15)]
    L_ += [note(1420, 268, "Customers want the same basket", PINK_ST, 104, 70, -2, 14),
           note(1524, 318, "Payments can do repeat billing", PINK_ST, 104, 70, 2, 14),
           note(1200, 290, "Order history predicts well", PINK_ST, 110, 66, 1, 14),
           note(1200, 470, "Reminders don't annoy", PINK_ST, 110, 60, -1, 14),
           note(1440, 470, "Customers trust auto-add", PINK_ST, 110, 64, 2, 14)]
    for i, row in enumerate([("Same basket wanted", "Fake-door button", "over 20% click", "31% ✓"),
                             ("Repeat billing", "Payments spike", "test charge ok", "30 June"),
                             ("History predicts", "Back-test", "over 70% hits", "78% ✓"),
                             ("Reminders welcome", "Email 500 users", "under 2% opt out", "running")]):
        x = 1144
        for c, v in enumerate(row):
            L_.append(hand(x, 777 + i * 40, v, 15))
            x += (150, 140, 120)[c] if c < 3 else 0
    write_example("opportunity-solution-tree-board", "Opportunity Solution Tree", "".join(L_))


def example_okr():
    L_ = [hand(44, 234, "Regular customers are our most valuable, and too many drift away: make the weekly shop effortless "
                        "before the summer peak.", 20)]
    objs = [(["make the weekly shop", "effortless for regular customers"],
             [("Weekly repeat orders", "22%", "30%", "6"), ("Median basket time", "38 min", "10 min", "7"),
              ("Reorder satisfaction", "3.6", "4.3", "5")],
             "Basket, Search & Browse", ["Reorder last basket", "Smart substitutes", "Saved favourites"]),
            (["make sure nobody forgets", "an item again"],
             [("Second order within 2 days", "9%", "5%", "5"), ("Out-of-stock complaints", "120/wk", "60/wk", "6")],
             "Basket, Checkout", ["“You usually buy” list", "Reminders for usual items"]),
            (["make checkout quick", "and trustworthy"],
             [("Checkout drop-off", "18%", "12%", "6"), ("Failed payments", "2.1%", "1%", "4")],
             "Checkout, Payments, Platform", ["Wallet payments", "Self-service deploys", "Fewer payment retries"])]
    spots = [(30, 694, -2), (200, 704, 2), (370, 694, -1)]
    for i, (will, krs, teams, bets) in enumerate(objs):
        x = 24 + i * 548
        L_ += [hand(x + 116, 373, will[0], 21), hand(x + 22, 408, will[1], 21)]
        for r, row in enumerate(krs):
            cx = x + 24
            for c, v in enumerate(row):
                L_.append(hand(cx, 516 + r * 34, v + ("/10" if c == 3 else ""), 16))
                cx += (230, 70, 70)[c] if c < 3 else 0
        L_.append(hand(after(x + 18, "Teams contributing:"), 620, teams, 17))
        for (dx, y, rot), t in zip(spots, bets):
            L_.append(note(x + dx, y, t, YELLOW, 150, 84, rot))
    for i, v in enumerate(["Mondays at the Basket stand-up, 10 minutes", "Week 6, all three teams together",
                           "Last Friday of the quarter, 0 to 1.0"]):
        L_.append(hand(after(42, ["Weekly confidence check:", "Mid-period review:", "End-of-period scoring:"][i]), 976 + i * 28, v, 17))
    for i, v in enumerate(["Personalised offers (next quarter)", "Rebuilding checkout from scratch", "Family accounts"]):
        L_.append(hand(866, 981 + i * 26, v, 18))
    write_example("okr-board", "Objectives & Key Results", "".join(L_), ["Basket group", "Q2"])


def example_product_bet():
    L_ = []
    for y, lab, v in [(230, "Who has it:", "Families who buy the same staples every week"),
                      (264, "The problem, in their words:", "“We always run out of milk and nappies"),
                      (298, "", "between shops, then pay for a second delivery.”"),
                      (332, "How they cope today:", "A list on the fridge, a top-up at the"),
                      (366, "", "corner shop, or a phone reminder."),
                      (400, "How often, how painful (1–5):", "Every week · 4")]:
        L_.append(hand(after(42, lab) if lab else 46, y, v, 17))
    for y, lab, v in [(230, "We believe that (who):", "families who buy the same staples each week"),
                      (264, "will (do what):", "set up a staples subscription and keep it for 3+ months"),
                      (298, "if we (offer what):", "deliver their chosen staples automatically with each weekly shop"),
                      (332, "because (what we know):", "38% of baskets repeat 5+ staples; 7 of 10 people we interviewed asked for it")]:
        L_.append(hand(after(592, lab, 12), y, v, 18))
    L_ += [hand(after(592, "The smallest version we could try:"), 366, "a manual subscription: customers pick 5 staples and we add them by hand", 17),
           hand(596, 400, "to their next order, for 50 customers for 4 weeks (no change to Payments).", 17)]
    for y, lab, v in [(544, "Value to users:", "Never run out; one less thing to remember"),
                      (584, "", "Fewer second deliveries"),
                      (616, "Value to us:", "Predictable orders, easier stock planning"),
                      (656, "", "More repeat orders (Q2 objective 1)"),
                      (688, "Cost of doing nothing:", "A rival launched subscriptions in March"),
                      (724, "Roughly what it'll take:", "Test: 2 people, 4 weeks")]:
        L_.append(hand(after(42, lab) if lab else 46, y, v, 17))
    for i, (v, c) in enumerate([("Families keep it for 3+ months", "2"), ("They can pick and change staples easily", "3"),
                                ("Payments can do repeat billing", "2"), ("Margin holds with staples added", "3")]):
        ry = 558 + i * 48
        L_ += [hand(722, ry + 28, v, 17), hand(1040, ry + 28, c, 22)]
    for i, row in enumerate([("Fake-door sign-up", "over 5% of visitors sign up", "2 May"),
                             ("Manual test, 50 customers", "70% still subscribed at week 4", "6 June"),
                             ("Payments spike", "a test repeat charge works", "30 June")]):
        x = 1148
        for c, v in enumerate(row):
            L_.append(hand(x, 581 + i * 34, v, 16))
            x += (190, 242)[c] if c < 2 else 0
    for i, row in enumerate([("Customers with an active subscription", "0", "5,000", "end of Q3"),
                             ("Second order within 2 days", "9%", "5%", "end of Q3"),
                             ("Staples basket margin", "21%", "21% (hold)", "end of Q3")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 905 + i * 34, v, 17))
            x += (330, 120, 120)[c] if c < 3 else 0
    L_.append(hand(after(42, "We'll stop or change course if:"), 1026, "fewer than half keep it for 4 weeks", 17))
    L_ += [tick(1256, 874), hand(after(864, "Why:"), 946, "Value and feasibility are still guesses (2 out of 5)", 17),
           hand(after(864, "Decided by:"), 980, "Priya, with the Basket and Payments leads", 17),
           hand(after(864, "Revisit on:"), 1014, "6 June, after the manual test", 17)]
    write_example("product-bet-canvas", "Product Bet Canvas", "".join(L_), ["Staples subscription", "Priya", "14 April"])


def example_story_map():
    L_ = [hand(after(44, "Persona / user:", 12), 172, "Busy parent who shops weekly", 18),
          hand(after(546, "Their goal:", 12), 172, "Repeat the weekly shop in under a minute", 18),
          hand(after(1126, "Product / epic:", 12), 172, "Reorder made easy", 18)]
    acts = ["Find my last order", "Check the basket", "Fix the gaps", "Choose delivery", "Pay and confirm"]
    tasks = [["See last order", "Browse past orders"], ["Check items", "Change amounts"], ["Swap missing items", "Add forgotten items"],
             ["Pick a slot", "Delivery notes"], ["Pay with saved card", "Get confirmation"]]
    # (activity column, task 0/1, text) per release slice
    slices = [(482, [(0, 0, "Last order card on home page"), (1, 0, "Show items and total"), (1, 1, "Change an amount"),
                     (2, 0, "Remove unavailable items"), (3, 0, "Use their usual slot"), (4, 0, "Pay with saved card"),
                     (4, 1, "Email confirmation")]),
              (712, [(0, 1, "Reorder any past order"), (2, 0, "Suggest substitutes"), (2, 1, "“You usually buy” list"),
                     (3, 0, "Choose another slot"), (3, 1, "Leave a note"), (4, 1, "In-app confirmation")]),
              (912, [(0, 1, "Save favourite baskets"), (1, 1, "Share the basket with family"), (2, 1, "Reminders for usual items"),
                     (4, 0, "Wallet payments")])]
    for i, a in enumerate(acts):
        x0 = 286 + i * 274
        L_.append(note(x0 + 50, 234, a, BLUE_ST, 160, 62, [-2, 1, -1, 2, -1][i]))
        for j, t in enumerate(tasks[i]):
            L_.append(note(x0 + j * 134, 342, t, YELLOW, 124, 62, [1, -2][j], 15))
    for y, items in slices:
        for k, (c, j, t) in enumerate(items):
            L_.append(note(286 + c * 274 + j * 134, y, t, GREEN, 124, 66, [-1, 2, -2, 1][k % 4], 14))
    for (y, h), (o, tg) in zip([(468, 220), (698, 190), (898, 162)],
                               [("reorder in 60 s", "Sprint 15"), ("fewer 2nd orders", "end of Q2"), ("bigger baskets", "Q3")]):
        L_ += [hand(after(44, "Outcome:"), y + h - 56, o, 16), hand(after(44, "Target:"), y + h - 24, tg, 16)]
    write_example("story-map-board", "User Story Map", "".join(L_))


def example_example_mapping():
    L_ = [note(40, 160, "Reorder last basket", YELLOW, 300, 80, 0, 22),
          hand(after(362, "As a…", 12), 187, "returning customer", 19),
          hand(after(782, "I want…", 12), 187, "to reorder my last basket in one tap", 19),
          hand(after(1242, "so that…", 12), 187, "my weekly shop takes a minute", 19)]
    rules = [("Reorder adds every item from the last order",
              ["Last order had 12 items → basket gets all 12", "Milk already in basket → quantities add up"]),
             ("Out-of-stock items are flagged, not added",
              ["Bread out of stock → shown greyed out as “unavailable”", "Everything out of stock → message, nothing added"]),
             ("Prices are today's, not the old ones",
              ["Eggs were £2.00, now £2.20 → basket shows £2.20 and “price changed”"]),
             ("Only orders from the last 90 days",
              ["Last order 4 months ago → no card on the home page", "Last order yesterday → card shows it"])]
    cw = (1278 - 36) / 4
    for i, (rule, exs) in enumerate(rules):
        x = 24 + i * (cw + 12)
        L_.append(note(x + 14, 332, rule, BLUE_ST, cw - 28, 84, 0, 18))
        for j, e in enumerate(exs):
            L_.append(note(x + 22 + (j % 2) * 8, 474 + j * 116, e, GREEN, cw - 52, 96, [-1, 2][j], 16))
    for j, q in enumerate(["Suggest substitutes, or leave them out? (Priya asks Store Ops)",
                           "What if a product has been discontinued?", "Do promotion prices carry over?"]):
        L_.append(note(1342 + (j % 2) * 10, 420 + j * 120, q, PINK_ST, 280, 96, [2, -1, 1][j], 17))
    L_ += [tick(46, 1008), hand(after(594, "Story A:"), 970, "Reorder in-stock items (rules 1, 3 and 4)", 17),
           hand(after(594, "Story B:"), 1006, "Handle out-of-stock items (rule 2)", 17),
           hand(after(1142, "Owner:"), 970, "Priya (asks Store Ops)", 17),
           hand(after(1142, "Answer by:"), 1006, "Thursday, before planning", 17)]
    write_example("example-mapping-board", "Example Mapping", "".join(L_))


def example_event_storming():
    ev, cmd, act, pol, sysm, ext, rm, hot = ORANGE_ST, BLUE_ST, YELLOW, LILAC_ST, PALE_ST, PINK_ST, GREEN, ROSE_ST
    phases = [("Reorder", [(14, 452, "Customer", act, 88), (110, 440, "Reorder last basket", cmd), (250, 440, "Last order card", rm),
                           (20, 540, "Last order shown", ev), (140, 540, "Basket refilled", ev), (260, 540, "Missing items flagged", ev),
                           (140, 640, "Basket service", sysm), (260, 650, "Discontinued items?", hot)]),
              ("Checkout", [(14, 452, "Customer", act, 88), (110, 440, "Choose a slot", cmd), (250, 440, "Free slots", rm),
                            (20, 540, "Slot reserved", ev), (140, 540, "Checkout started", ev), (260, 540, "Slot released", ev),
                            (20, 640, "Delivery slots", sysm), (200, 640, "Whenever a slot is held 15 min, release it", pol, 170, 76)]),
              ("Payment", [(14, 452, "Customer", act, 88), (110, 440, "Pay", cmd), (250, 440, "Payment provider", ext),
                           (20, 540, "Payment authorised", ev), (140, 540, "Payment failed", ev), (260, 540, "Order placed", ev),
                           (20, 650, "Who signs off payment changes?", hot, 130, 70),
                           (200, 640, "Whenever payment fails, retry once, then ask for another card", pol, 160, 86)]),
              ("Fulfilment", [(14, 440, "Whenever an order is placed, reserve stock", pol, 140, 76), (170, 452, "Picker", act, 80),
                              (260, 440, "Pick the order", cmd), (20, 540, "Stock reserved", ev), (140, 540, "Substitute chosen", ev),
                              (260, 540, "Order delivered", ev), (20, 640, "Warehouse system", ext), (140, 640, "Pick list", rm),
                              (260, 650, "Substitutes: picker or customer decides?", hot, 120, 76)])]
    L_ = []
    pw = (1632 - 28) / 4
    for i, (phase, notes_) in enumerate(phases):
        px = 38 + i * pw
        L_.append(hand(after(px + 8, "Phase:", 10.5), 412, phase, 18))
        for k, n in enumerate(notes_):
            dx, y, t, col = n[:4]
            w, h = (n[4], n[5]) if len(n) > 5 else ((n[4], 48) if len(n) > 4 else (112, 64))
            L_.append(note(px + dx, y, t, col, w, h, [-2, 1, 2, -1, 1][k % 5], 14))
    for i, (q, o) in enumerate([("Discontinued items in a reorder?", "Priya"), ("Who signs off payment changes?", "Payments lead"),
                                ("Substitutes: picker or customer decides?", "Store Ops")]):
        L_ += [hand(48, 977 + i * 30, q, 16), hand(378, 977 + i * 30, o, 16)]
    for i, row in enumerate([("Basket", "Basket refilled, items flagged", "Basket"),
                             ("Checkout and slots", "Slot reserved, slot released", "Checkout"),
                             ("Payments", "Authorised, failed", "Payments")]):
        x = 598
        for c, v in enumerate(row):
            L_.append(hand(x, 977 + i * 30, v, 16))
            x += (170, 210)[c] if c < 2 else 0
    for i, (lab, v) in enumerate([("Zoom into (process or design):", "Failed payments (design)"),
                                  ("Who to invite next:", "Payments lead, a picker from Store Ops"),
                                  ("Next session:", "Tuesday 22 April, 2 hours")]):
        L_.append(hand(after(1142, lab), 948 + i * 36, v, 17))
    write_example("event-storming-board", "Event Storming", "".join(L_), ["Online grocery order", "15 April"])


def example_stakeholder_map():
    L_ = []
    for x, y, t, rot in [(520, 292, "Head of Digital (sponsor)", -2), (700, 300, "Store Ops", 2), (560, 380, "Payments lead", 1),
                         (740, 384, "Finance", -1), (110, 300, "Legal and privacy", 2), (290, 340, "Marketing director", -2),
                         (520, 545, "Customer service", 1), (710, 560, "Customer panel", -2), (580, 630, "Warehouse team", 2),
                         (120, 560, "Brand team", -1), (300, 610, "IT security", 1)]:
        L_.append(note(x, y, t, YELLOW, 140, 62, rot, 16))
    reg = [("Head of Digital", "Repeat orders up; worried about Q2", "Fortnightly 1:1", "Priya"),
           ("Store Ops", "Substitutes must not slow picking", "Weekly call", "Priya"),
           ("Payments lead", "Subscriptions without fraud risk", "Joint planning", "Tom"),
           ("Finance", "Margin on staples", "Monthly review", "Priya"),
           ("Legal and privacy", "Consent for reminders", "Before each launch", "Priya"),
           ("Marketing", "A launch date for the campaign", "Monthly update", "Priya"),
           ("Customer service", "Fewer “missing item” calls", "Demo at each review", "Alex"),
           ("Customer panel", "A faster weekly shop", "Monthly video call", "Mei")]
    for i, row in enumerate(reg):
        x = 962
        for c, v in enumerate(row):
            L_.append(hand(x, 266 + i * 36, v, 15))
            x += (150, 230, 190)[c] if c < 3 else 0
    comms = [("Sponsor and leads", "Progress against OKRs, risks, asks", "Status report", "Fortnightly", "Priya"),
             ("Whole Basket group", "What shipped, what's next", "Iteration review", "Every 2 weeks", "Tom"),
             ("Customer service", "What's changing for customers", "Demo and FAQ", "Before each release", "Alex"),
             ("Customer panel", "New features to try", "Video call", "Monthly", "Mei")]
    for i, row in enumerate(comms):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 899 + i * 34, v, 16))
            x += (210, 300, 190, 170)[c] if c < 4 else 0
    L_ += [note(1144, 908, "Store Ops could block substitutes if picking slows", PINK_ST, 152, 100, -2, 15),
           note(1310, 914, "Legal sign-off on reminders may take 6 weeks", PINK_ST, 152, 100, 2, 15),
           note(1476, 908, "Missing from the map: delivery drivers?", PINK_ST, 152, 100, -1, 15)]
    write_example("stakeholder-map-board", "Stakeholder Map", "".join(L_))


def example_raid_log():
    blocks = [(42, 148, (250, 92, 80, 216), [
                  ("Repeat billing turns out to be hard", "High", "High", "Reduce: spike early", "Tom"),
                  ("Legal sign-off on reminders is slow", "Med", "Med", "Avoid: draft in week 1", "Priya"),
                  ("Substitutes slow down picking", "Med", "High", "Reduce: trial in 1 store", "Priya"),
                  ("Ravi's onboarding takes longer", "Low", "Low", "Accept", "Tom")]),
              (864, 148, (300, 250, 88), [
                  ("Families want much the same basket", "Fake-door button (31% ✓)", "done", "Priya"),
                  ("Payments can do repeat billing", "Spike with Payments", "30 June", "Tom"),
                  ("Stock data is good enough for substitutes", "Back-test on 3 months", "16 May", "Sam")]),
              (42, 611, (250, 150, 196, 80), [
                  ("Releases wait on Payments sign-off", "2-day delays", "Agree self-service checks", "Tom", "9 May"),
                  ("Test data for reorders isn't realistic", "Bugs found late", "Copy anonymised orders", "Alex", "2 May"),
                  ("Platform tickets take a week", "Slows deploy fixes", "Raise at cross-team sync", "Tom", "Fri")]),
              (864, 611, (240, 150, 100, 100), [
                  ("Stock API for substitutes", "Warehouse → us", "Wed 7 May", "At risk", "Sam"),
                  ("Repeat billing", "Payments → us", "30 June", "On track", "Tom"),
                  ("Last-order data for search", "us → Search", "Sprint 15", "Done", "Jo"),
                  ("Privacy sign-off for events", "Legal → us", "16 May", "Waiting", "Priya")])]
    L_ = []
    for x, y, widths, rows in blocks:
        for i, row in enumerate(rows):
            cx = x + 6
            for c, v in enumerate(row):
                col = "#DC2626" if v in ("High", "At risk") else PEN
                L_.append(hand(cx, y + 117 + i * 34, v, 16, col))
                cx += widths[c] if c < len(widths) else 0
    write_example("raid-log-board", "RAID Log", "".join(L_), ["Reorder made easy", "28 April"])


def example_dependency_map():
    teams = ["Basket", "Checkout", "Payments", "Search & Browse", "Store Platform", "Warehouse"]
    it_w, rh = (1632 - 28 - 170) / 6, (600 - 104) / 6
    pos = lambda r, c, k=0: (212 + c * it_w + 10 + k * 112, 240 + r * rh + 12)
    # (row, iteration, text, colour, left/right half of the cell) and red strings from provider to the item that needs it
    items = {"reorder": (0, 0, "Reorder card", YELLOW, 0), "subs": (0, 2, "Subscriptions pilot", YELLOW, 0),
             "swap": (0, 1, "Substitutes", YELLOW, 0), "lastdata": (0, 0, "Last-order data", BLUE_ST, 1),
             "usual": (3, 1, "Usual-items search", YELLOW, 1), "faster": (1, 1, "Faster releases", YELLOW, 1),
             "wallet": (1, 3, "Wallet payments", YELLOW, 0), "deploys": (4, 0, "Self-service deploys", BLUE_ST, 1),
             "billing": (2, 2, "Repeat billing", BLUE_ST, 0), "walletapi": (2, 3, "Wallet API", BLUE_ST, 0),
             "stock": (5, 1, "Stock API", PINK_ST, 0)}
    links = [("stock", "swap"), ("billing", "subs"), ("deploys", "faster"), ("lastdata", "usual"), ("walletapi", "wallet")]
    L_ = [hand(50, 240 + r * rh + rh - 24, t, 17) for r, t in enumerate(teams)]
    centre = lambda k: (pos(*items[k][:2], items[k][4])[0] + 52, pos(*items[k][:2], items[k][4])[1] + 26)
    for a, b_ in links:
        (x1, y1), (x2, y2) = centre(a), centre(b_)
        L_.append(L(x1, y1, x2, y2, "#DC2626", 2.6, ' stroke-linecap="round" stroke-opacity=".85"'))
    for k, (r, c, t, col, n) in items.items():
        x, y = pos(r, c, n)
        L_.append(note(x, y, t, col, 104, 54, [-2, 1, 2, -1][len(t) % 4], 14))
    reg = [("1", "Basket", "Warehouse", "Stock API for substitutes", "Iteration 2", "at risk", "Sam"),
           ("2", "Basket", "Payments", "Repeat billing for subscriptions", "Iteration 3", "agreed", "Tom"),
           ("3", "Checkout", "Store Platform", "Self-service deploys", "Iteration 1", "done", "Checkout lead"),
           ("4", "Search & Browse", "Basket", "Last-order data", "Iteration 1", "done", "Jo"),
           ("5", "Checkout", "Payments", "Wallet API", "Iteration 4", "agreed", "Payments lead")]
    for i, row in enumerate(reg):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 879 + i * 34, v, 16, "#DC2626" if v == "at risk" else PEN))
            x += (40, 150, 150, 330, 120, 130)[c] if c < 6 else 0
    L_ += [tick(1138, 908), tick(1138, 938),
           hand(after(1138, "Top dependency to remove:"), 988, "Stock API: give Basket read access", 17),
           hand(after(1138, "Owner:"), 1022, "Sam, with the Warehouse lead", 17)]
    write_example("dependency-map-board", "Dependency Map", "".join(L_))


def example_cross_team_planning():
    L_ = []
    for i, row in enumerate([("Make the weekly shop effortless", "9", "Basket, Search & Browse"),
                             ("Make sure nobody forgets an item", "7", "Basket, Checkout"),
                             ("Make checkout quick and trustworthy", "8", "Checkout, Payments, Platform")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 265 + i * 34, v, 17))
            x += (420, 120)[c] if c < 2 else 0
    for i, (lab, v) in enumerate([("Product vision / goal:", "The weekly shop in two minutes"),
                                  ("Fixed dates & events:", "Summer campaign launches 30 June"),
                                  ("Capacity changes (holidays, hiring):", "Ravi joins Basket; Platform one person short in iteration 3"),
                                  ("Platform or architecture changes:", "New payment provider: Q3, not this period")]):
        L_.append(hand(after(864, lab), 234 + i * 36, v, 17))
    it_w = (1632 - 28 - 400) / 5
    rh = (500 - 120) / 6
    for i, d in enumerate(["7–18 Apr", "21 Apr – 2 May", "5–16 May", "19–30 May", "2–13 June"]):
        L_.append(hand(208 + i * it_w + 108, 479, d, 16))
    for i, t in ((1, "Reorder live"), (2, "Subscriptions pilot"), (4, "Summer campaign")):
        mx = 208 + i * it_w + it_w / 2
        L_ += [f'<path d="M{mx:g},514 l9,9 -9,9 -9,-9 z" fill="{ACCENT}"/>', hand(mx, 560, t, 16, anchor="middle")]
    plan = [("Basket", ["Reorder card", "Substitutes", "Subs pilot", "Reminders", "Favourites"], ["Needs the Stock API", "by iteration 2"]),
            ("Checkout", ["Self-service deploys", "Faster releases", None, "Wallet payments", "Promo codes"], ["Wallet API from", "Payments, iteration 4"]),
            ("Payments", ["Fraud rules", None, "Repeat billing", "Wallet API", None], ["Sign-off is a bottleneck:", "agree self-service checks"]),
            ("Search & Browse", ["Faster search", "Usual-items search", None, "Recipes", None], ["Last-order data from", "Basket (done)"]),
            ("Store Platform", ["Deploy pipeline", None, "Monitoring", None, "Cost review"], ["One person short", "in iteration 3"])]
    for r, (team, cells, risk) in enumerate(plan, 1):
        ry = 506 + r * rh
        L_.append(hand(50, ry + rh - 23, team, 17))
        for i, t in enumerate(cells):
            if t:
                col = PINK_ST if t in ("Substitutes", "Wallet payments") else YELLOW
                L_.append(note(208 + i * it_w + 30, ry + 6, t, col, 150, 44, [-1, 1, 2, -2][(r + i) % 4], 14))
        L_ += [hand(1428, ry + 24 + k * 20, t, 15, "#B91C1C") for k, t in enumerate(risk)]
    L_.append(hand(1428, 530, "Campaign date is fixed", 15, "#B91C1C"))
    for i, n in enumerate([0, 0, 4, 14, 6]):
        if n:
            L_.append(hand(84 + i * 100 + 24, 1012, f"×{n}", 18))
    L_.append(f'<circle cx="384" cy="1006" r="21" fill="none" stroke="{PEN}" stroke-width="2.2"/>')
    for i, t in enumerate(["Stock API slips → substitutes move to iteration 3 (Sam owns)",
                           "Payments sign-off becomes the bottleneck (reduced)", "The campaign date can't move (accepted)"]):
        L_.append(hand(592, 994 + i * 24, t, 16))
    for i, (lab, v) in enumerate([("Features %:", "70%"), ("Tech debt & enablers %:", "20%"), ("Unplanned buffer %:", "10%")]):
        L_.append(hand(after(1138, lab), 992 + i * 26, v, 17))
    write_example("cross-team-planning-board", "Cross-Team Planning", "".join(L_), ["Basket group", "Q2 · 5 iterations"])


def example_kanban_design():
    cols = [("Options", "none", ["Priya has ranked it", "in the top 10"], 1),
            ("Ready", "4", ["Example-mapped,", "small enough for", "a few days"], 1),
            ("Building", "3", ["Code done, tests", "pass, pull request", "raised"], 0),
            ("Review", "2", ["Reviewed by a", "second person"], 1),
            ("Testing", "2", ["Exploratory test", "done; meets WCAG AA"], 0),
            ("To release", "none", ["On staging and", "accepted by Priya"], 1),
            ("Done", "none", ["Released and", "reorder events seen"], None)]
    cw = (1632 - 28 - 60) / 7
    L_ = []
    for i, (name, wip, exit_, kind) in enumerate(cols):
        cx = 38 + i * (cw + 10)
        L_ += [hand(after(cx + 12, "Name:"), 264, name, 18), hand(after(cx + 12, "WIP limit:"), 298, wip, 18)]
        L_ += [hand(cx + 12, 361 + k * 26, t, 16) for k, t in enumerate(exit_)]
        if kind is not None:
            L_.append(tick(cx + 12 + kind * 76, 468))
    for i, (pol, lim) in enumerate([("Swarm on it now; it may break WIP limits", "1 at a time"),
                                    ("Start by the latest start date on the card", "2"),
                                    ("Pull the top item from Ready", "the rest"),
                                    ("At least one item every iteration", "1")]):
        L_ += [hand(498, 664 + i * 46, pol, 17), hand(938, 664 + i * 46, lim, 17)]
    for i, (lab, v) in enumerate([("We pull work when:", "a column is under its WIP limit"),
                                  ("Blocked items are marked by:", "a pink sticky with the date"),
                                  ("Replenishment: when & who:", "Mondays, Priya and Tom"),
                                  ("We walk the board at:", "09:30, right to left"),
                                  ("Definition of Done lives at:", "the wall next to the board"),
                                  ("Policies reviewed every:", "quarter, at the retro")]):
        L_.append(hand(after(1138, lab), 626 + i * 34, v, 17))
    for j in range(5):
        L_.append(tick(42 + (j % 3) * 200, 970 + (j // 3) * 28))
    L_.append(hand(after(42, "Swimlanes (if any):"), 1036, "Expedite lane at the top; no other lanes", 17))
    for j in range(5):
        L_.append(tick(864 + (j % 2) * 390, 946 + (j // 2) * 32))
    L_.append(hand(1508, 1006, "← from Q3", 16))
    write_example("kanban-board-design", "Kanban Board Design", "".join(L_), ["Basket team", "2 April"])


def example_status_report():
    L_ = [hand(210, 241, "Reorder is live and repeat orders are up; substitutes are one iteration late.", 21),
          f'<circle cx="1320" cy="258" r="21" fill="none" stroke="{PEN}" stroke-width="2.2"/>', tick(1444, 268),
          hand(after(42, "Because:"), 278, "repeat orders rose from 22% to 25% in four weeks, but the Stock API is at risk", 17)]
    for i, row in enumerate([("Customers reorder easily", "weekly repeat orders", "22%", "25%", "30%", "↑ rising"),
                             ("Shopping is faster", "median basket time", "38 min", "21 min", "10 min", "↑ improving"),
                             ("Fewer forgotten items", "2nd order within 2 days", "9%", "8%", "5%", "→ flat"),
                             ("Reorder satisfaction", "survey score (1–5)", "3.6", "4.0", "4.3", "↑ rising")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 435 + i * 44, v, 17))
            x += (310, 220, 100, 100, 100)[c] if c < 5 else 0
    for i, (lab, v) in enumerate([("Likely finish range:", "13–20 June (iteration 8)"), ("Work done / remaining:", "29 done, 14 left"),
                                  ("Scope change since last report:", "+3 items (substitutes split)")]):
        L_.append(hand(after(1138, lab), 398 + i * 40, v, 17))
    L_ += [tick(1500, 542), hand(after(1138, "Why:"), 578, "the Stock API is late, so substitutes moved", 17)]
    L_ += [hand(46, 811 + i * 26, t, 17) for i, t in enumerate(["Last order card on the home page", "One-tap reorder (in-stock items)",
                                                                  "Unavailable items flagged", "Email confirmation"])]
    L_ += [hand(46, 959 + i * 26, t, 17) for i, t in enumerate(["31% clicked the subscription fake door",
                                                                  "Customers want to approve substitutes",
                                                                  "Pairing on payments halved review time"])]
    for i, row in enumerate([("Stock API late (Warehouse)", "Read access as a fallback", "Sam"),
                             ("Payments sign-off delays", "Self-service checks", "Tom"),
                             ("Legal sign-off on reminders", "Draft sent in week 1", "Priya")]):
        x = 596
        for c, v in enumerate(row):
            L_.append(hand(x, 828 + i * 40, v, 16))
            x += (210, 180)[c] if c < 2 else 0
    for i, row in enumerate([("Give Basket read access to stock data", "Warehouse head", "16 May"),
                             ("Approve the subscriptions pilot", "Head of Digital", "23 May")]):
        x = 1144
        for c, v in enumerate(row):
            L_.append(hand(x, 829 + i * 44, v, 15))
            x += (230, 130)[c] if c < 2 else 0
    L_.append(hand(after(1138, "Next report:"), 1026, "Friday 23 May", 17))
    write_example("status-report-board", "Outcome Status Report", "".join(L_), ["Reorder made easy", "9 May"])


def example_value_metrics():
    L_ = []
    gw = (1632 - 36 - 32) / 3
    for i, goal in enumerate([["The first place families think of for", "the weekly shop (top 3 in our regions)"],
                              ["Repeat orders at 30% and basket time", "under 10 minutes, by the end of the year"],
                              ["Reorder made easy: one-tap reorder", "and substitutes, this quarter"]]):
        L_ += [hand(42 + i * (gw + 16), 253 + k * 26, t, 18) for k, t in enumerate(goal)]
    areas = [((0, 1), [("Repeat orders a week", "25%", "30%", "better"), ("Reorder satisfaction", "4.0", "4.3", "better"),
                       ("Weekly users", "182k", "200k", "flat")],
              ["Repeat customers come back more often;", "satisfaction is up since the reorder card."]),
             ((1, 2), [("Lapsed customers", "41k", "30k", "flat"), ("Want subscriptions", "31%", "", "new")],
              ["A third of visitors want subscriptions:", "a big need we don't serve yet."]),
             ((0, 1, 3), [("Lead time (85%)", "12 d", "7 d", "better"), ("Releases a week", "2", "5", "better"),
                          ("Time to fix", "3 d", "1 d", "flat")],
              ["Releases wait on Payments sign-off;", "self-service checks should halve lead time."]),
             ((0, 1, 3), [("New feature time", "55%", "70%", "better"), ("Blocked days", "9", "3", "worse"),
                          ("Escaped defects", "4", "1", "flat")],
              ["Blocked time is rising: three items", "waited on other teams last iteration."])]
    cw = (1632 - 3 * 14) / 4
    for i, (ticks, rows, notes) in enumerate(areas):
        x = 24 + i * (cw + 14)
        L_ += [tick(x + 18 + (j % 2) * 186, 454 + (j // 2) * 26) for j in ticks]
        for r, row in enumerate(rows):
            cx = x + 24
            for c, v in enumerate(row):
                L_.append(hand(cx, 567 + r * 38, v, 15, "#DC2626" if v == "worse" else PEN))
                cx += (150, 62, 62)[c] if c < 3 else 0
        L_ += [hand(x + 20, 747 + k * 26, t, 16) for k, t in enumerate(notes)]
    for i, row in enumerate([("Time to market", "Self-service release checks, agreed with Payments", "Lead time 12 → 7 days", "Tom"),
                             ("Ability to innovate", "Basket gets read access to stock data", "Blocked days 9 → 3", "Sam")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 1001 + i * 34, v, 16))
            x += (160, 430, 300)[c] if c < 3 else 0
    for i, (lab, v) in enumerate([("Measures updated every:", "iteration"), ("Reviewed with leaders at:", "the monthly product review"),
                                  ("Next review:", "Wednesday 4 June")]):
        L_.append(hand(after(1138, lab), 966 + i * 30, v, 17))
    write_example("value-metrics-board", "Value Metrics", "".join(L_), ["Basket group", "9 May"])


def example_cynefin():
    qw, qh = (1082 - 14) / 2, (1060 - 148 - 14) / 2
    domains = [["Will families keep a subscription?", "Which substitutes will customers accept?", "Why do customers drift away?"],
               ["Speed up the basket API", "Repeat billing with the payment provider", "Forecast the release date"],
               ["Checkout down on a Saturday morning (last month)"],
               ["Deploy to staging", "Refunds for missing items", "Accessibility checks (WCAG AA)"]]
    spots = [(40, 310, -2), (250, 330, 2), (90, 440, 1)]
    L_ = []
    for i, items in enumerate(domains):
        x, y = 24 + (i % 2) * (qw + 14), (i // 2) * (qh + 14)  # spots are measured on the top row
        for (dx, dy, rot), t in zip(spots, items):
            L_.append(note(x + dx, y + dy, t, YELLOW, 180, 92, rot, 16))
    # circle the situation the team chose to work on
    L_.append(f'<ellipse cx="364" cy="376" rx="112" ry="62" fill="none" stroke="{PEN}" stroke-width="2.2" '
              f'transform="rotate(-4 364 376)"/>')
    for i, v in enumerate(["Stock data accuracy → complicated", "What customers will accept → complex",
                           "Picking rules in store → clear"]):
        L_.append(hand(after(1138, f"Part {i + 1}:"), 330 + i * 34, v, 17))
    approach = [(578, "Situation:", "Will customers accept the substitutes"), (618, "", "we suggest when an item is missing?"),
                (650, "Main domain:", "Complex"), (686, "So we will:", "run small experiments, not a big design;"),
                (726, "", "learn from real orders before we scale up"),
                (758, "Safe-to-fail experiments:", "1. 200 customers approve substitutes"),
                (798, "", "2. Show two choices instead of one"), (834, "", "3. The picker phones the customer (one store)"),
                (866, "Signs it's working:", "over 70% of substitutes accepted"),
                (902, "Signs to stop:", "complaints rise or picking slows"),
                (938, "Amplify or dampen by:", "widen to the whole region, or"),
                (978, "", "switch it off within a day"), (1010, "Revisit on:", "Friday 30 May")]
    for y, lab, v in approach:
        L_.append(hand(after(1138, lab) if lab else 1142, y - 4, v, 17))
    write_example("cynefin-board", "Cynefin® Sense-Making", "".join(L_), ["Substitutes", "12 May"])


def example_cross_team_sync():
    rows = [("Basket", ["Reorder live: repeat orders at 25%", "In-stock substitutes done"], ["Out-of-stock substitutes", "Subscriptions pilot prep"],
             ["Stock API from Warehouse"], ["Stock API, due Wed 7 May"], "3"),
            ("Checkout", ["Self-service deploys done", "Now releasing 3 times a week"], ["Wallet payments"],
             ["Wallet API from Payments"], ["none"], "4"),
            ("Payments", ["Fraud rules live", "Repeat billing spike started"], ["Repeat billing", "Wallet API"],
             ["Two people on the support rota"], ["Wallet API for Checkout"], "3"),
            ("Search & Browse", ["Usual-items search in testing"], ["Recipe search"], ["nothing"], ["none"], "5"),
            ("Store Platform", ["Monitoring dashboards 60% done"], ["Cost review"], ["One person short"], ["none"], "4")]
    L_ = []
    for i, (team, *cells, conf) in enumerate(rows):
        y = 242 + i * 58
        L_.append(hand(48, y + 24, team, 17))
        x = 42 + 150
        for c, lines_ in enumerate(cells):
            L_ += [hand(x + 6, y + 22 + k * 24, t, 16, "#DC2626" if t.startswith("Stock API") else PEN) for k, t in enumerate(lines_)]
            x += (380, 280, 300, 300)[c]
        L_.append(hand(1452 + 93, y + 32, conf, 22, anchor="middle"))
    for x, y, t, rot in [(50, 740, "Payments sign-off needed for every Checkout release", -2),
                         (205, 830, "Staging down twice this week", 2),
                         (410, 740, "Stock API late: Basket asks for read access (Sam)", 1),
                         (580, 830, "Test data for reorders (Alex)", -2),
                         (770, 740, "Deploy queue: fixed by self-service deploys", 2),
                         (930, 830, "Shared on-call rota agreed", -1)]:
        L_.append(note(x, y, t, YELLOW, 160, 86, rot, 16))
    for i, row in enumerate([("Escalate Stock API to Head of Warehouse", "Tom", "Thu"),
                             ("Agree self-service release checks", "Payments lead", "16 May"),
                             ("Add a health alert for staging", "Platform", "Mon"),
                             ("Move the sync to Tue and Thu", "Tom", "now")]):
        x = 1144
        for c, v in enumerate(row):
            L_.append(hand(x, 739 + i * 34, v, 15))
            x += (290, 110)[c] if c < 2 else 0
    write_example("cross-team-sync-board", "Cross-Team Sync", "".join(L_), ["Basket group", "6 May"])


def example_portfolio_kanban():
    cols = [(None, "a sponsor and a problem", ["Family accounts", "Voice ordering", "Recipe-to-basket"]),
            ("4", "fits strategy; worth a case", ["Personalised offers", "Loyalty rewards"]),
            ("2", "lean case approved", ["Staples subscriptions", "New payment provider"]),
            ("3", "a team has capacity", ["Delivery Slots team"]),
            ("3", "MVP outcome measured", ["Reorder made easy", "Smart substitutes", "Faster checkout"]),
            (None, "benefits reviewed", ["Self-service deploys"])]
    cw = (1632 - 28 - 50) / 6
    L_ = []
    for i, (wip, exit_, items) in enumerate(cols):
        cx = 38 + i * (cw + 10)
        if wip:
            L_.append(hand(after(cx + 12, "WIP limit:", 10.5), 278, wip, 18))
        L_.append(hand(after(cx + 12, "Exit when:", 10.5), 308, exit_, 15))
        for j, t in enumerate(items):
            L_.append(note(cx + (20, 90, 20)[j], (340, 420, 500)[j], t, YELLOW, 150, 64, (-2, 2, -1)[j], 15))
    for y, lab, v in [(710, "Initiative:", "Staples subscriptions"),
                      (746, "Problem or opportunity:", "families run out of staples between weekly shops")]:
        L_.append(hand(after(42, lab), y, v, 17))
    for y, lab, v in [(814, "We believe…", "a staples subscription for weekly shoppers"),
                      (844, "will result in…", "repeat orders up 3 points, fewer second orders"),
                      (874, "We'll know when…", "5,000 active subscriptions by the end of Q3")]:
        L_.append(hand(after(54, lab), y, v, 17))
    L_ += [hand(after(42, "Smallest version (MVP):"), 922, "a manual subscription for 50 customers, 4 weeks", 17),
           hand(after(42, "Cost range:"), 958, "£40k–£70k to build fully", 17), tick(538, 966),
           hand(after(42, "Go / no-go criteria:"), 996, "go if 70% keep it for 4 weeks in the manual test", 17),
           tick(124, 1040)]
    for i, (target, actual) in enumerate([("15", "10"), ("45", "55"), ("20", "20"), ("15", "10"), ("5", "5"), ("100", "100")]):
        y = 752 + i * 40
        L_ += [hand(1060, y, target, 17), hand(1135, y, actual, 17, "#DC2626" if target != actual else PEN)]
    L_.append(hand(866, 1008, "Too little on new bets and tech debt", 16))
    L_ += [hand(after(1275, "Review cadence:"), 712, "monthly", 17),
           hand(after(1275, "Decision forum:"), 746, "the portfolio group", 17)]
    L_ += [tick(1275, 812 + i * 30) for i in (0, 1, 4)]
    L_.append(hand(after(1275, "Next review:"), 974, "Tuesday 3 June", 17))
    write_example("portfolio-kanban-board", "Portfolio Kanban & Investment Mix", "".join(L_), ["Online grocery", "6 May"])


def example_psych_safety():
    # seven anonymous votes per statement: strongly disagree … strongly agree
    votes = [[0, 1, 2, 3, 1], [0, 2, 2, 2, 1], [0, 0, 1, 4, 2], [0, 1, 3, 2, 1], [0, 0, 0, 3, 4], [0, 0, 1, 3, 3], [1, 2, 2, 2, 0]]
    sc_w, rh = (1082 - 36 - 470) / 5, (520 - 110) / 7
    L_ = []
    for r, row in enumerate(votes):
        ry = 244 + r * rh
        for i, n in enumerate(row):
            x0 = 512 + i * sc_w + sc_w / 2 - (n - 1) * 9
            L_ += [f'<circle cx="{x0 + k * 18:g}" cy="{ry + 26:g}" r="7" fill="#475569"/>' for k in range(n)]
    L_ += [tick(1138, 240 + i * 30) for i in range(5)]
    for i, row in enumerate([("2. Problems", "3 of 7", "2 of 7", "first run"), ("7. Ideas used", "2 of 7", "3 of 7", "first run"),
                             ("5. Asking for help", "7 of 7", "0 of 7", "first run")]):
        x = 1144
        for c, v in enumerate(row):
            L_.append(hand(x, 479 + i * 40, v, 16))
            x += (110, 120, 130)[c] if c < 3 else 0
    L_ += [note(48, 812, "Quieter people's ideas get lost in meetings", YELLOW, 160, 92, -2, 16),
           note(232, 826, "Problems get raised one-to-one, not in the room", YELLOW, 160, 92, 2, 16),
           note(130, 936, "Helping each other is a real strength", YELLOW, 160, 92, -1, 16)]
    L_ += [tick(590, 802), tick(590, 866), tick(590, 962),
           hand(590, 1010, "Priya and Tom will practise the ticked ones first", 17)]
    for i, row in enumerate([("Write silently before discussing ideas", "Tom", "next retro"),
                             ("Rotate who facilitates refinement", "everyone", "in 6 weeks"),
                             ("Priya shares one mistake at each review", "Priya", "end of June")]):
        x = 1144
        for c, v in enumerate(row):
            L_.append(hand(x, 801 + i * 40, v, 16))
            x += (260, 100)[c] if c < 2 else 0
    write_example("psych-safety-board", "Psychological Safety Check", "".join(L_))


def example_raci():
    roles = ["Priya (PO)", "Tom (SM)", "Sam (dev)", "Alex (test)", "Mei (design)", "Head of Digital", "Payments lead", "Legal"]
    rows = ["Pilot scope", "Repeat billing", "Subscription terms", "Go / no-go for the pilot", "Pilot test plan",
            "Messages to customers", "Release to 50 customers", "Retro on the pilot"]
    grid = [["A", "", "C", "", "R", "I", "C", ""], ["I", "", "R", "C", "", "", "A", ""], ["R", "", "", "", "", "I", "", "A"],
            ["R", "I", "I", "I", "I", "A", "C", "I"], ["C", "", "R", "A", "", "", "", ""], ["A", "", "", "", "R", "I", "", "C"],
            ["A", "I", "R", "C", "", "I", "C", ""], ["C", "A/R", "C", "C", "C", "I", "I", ""]]
    rw, rh = (1632 - 36 - 380) / 8, (470 - 136) / 8
    L_ = [hand(422 + i * rw + 10, 250, r, 15) for i, r in enumerate(roles)]
    for r, (item, cells) in enumerate(zip(rows, grid)):
        ry = 272 + r * rh
        L_.append(hand(52, ry + rh - 19, item, 17))
        L_ += [hand(422 + i * rw + rw / 2, ry + 28, v, 21, "#B91C1C" if "A" in v else PEN, anchor="middle")
               for i, v in enumerate(cells) if v]
    L_ += [tick(42 + i * 322, 716) for i in range(5)]
    log = [("1", "2 May", "Pilot with 50 customers, by hand", "Full build; fake door only", "Learn before spending £40k or more",
            "Priya, Head of Digital", "after 4 weeks"),
           ("2", "7 May", "Basket gets read access to stock data", "Wait for the Stock API; copy the data",
            "Unblocks substitutes now", "Head of Warehouse", "when the API ships"),
           ("3", "9 May", "Self-service release checks for Checkout", "Keep sign-off; sign off big changes only",
            "Sign-off was the bottleneck", "Payments lead", "after any incident")]
    for i, row in enumerate(log):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 874 + i * 38, v, 16))
            x += (40, 100, 380, 340, 360, 170)[c] if c < 6 else 0
    write_example("raci-decision-log-board", "RACI & Decision Log", "".join(L_), ["Subscriptions pilot", "9 May"])


def example_delegation():
    # (area, today's level, where we're heading, review by); levels are 1–7
    areas = [("Hiring into the team", 3, 4, "Q3"), ("Tools and technology", 5, 6, "Q3"), ("How we plan our work", 6, 7, "June"),
             ("Working hours", 6, 6, "—"), ("Spending up to £2k", 3, 5, "July"), ("Architecture choices", 5, 6, "Q3"),
             ("Who works on what", 7, 7, "—"), ("Release timing", 4, 6, "June")]
    lv_w, rh = (1632 - 36 - 510) / 7, (560 - 120) / 9
    cx = lambda lv: 382 + (lv - 1) * lv_w + lv_w / 2
    L_ = []
    for r, (area, now, goal, review) in enumerate(areas):
        ry = 420 + r * rh
        cy = ry + 21
        L_.append(hand(54, ry + rh - 22, area, 18))
        if goal != now:
            x1, x2 = cx(now) + 14, cx(goal) - 16
            L_ += [L(x1, cy, x2, cy, PEN, 2.4, ' stroke-linecap="round"'),
                   f'<path d="M{x2 - 8:g},{cy - 6:g} L{x2 + 2:g},{cy:g} L{x2 - 8:g},{cy + 6:g}" fill="none" stroke="{PEN}" stroke-width="2.4" stroke-linecap="round"/>',
                   f'<circle cx="{cx(goal):g}" cy="{cy:g}" r="11" fill="none" stroke="{PEN}" stroke-width="2.2" stroke-dasharray="4,3"/>']
        L_ += [f'<circle cx="{cx(now):g}" cy="{cy:g}" r="11" fill="{PEN}"/>', hand(1480, ry + 28, review, 18)]
    L_ += [hand(46, 989, "Spending over £2k needs Finance sign-off · customer data stays in the UK and EU", 17),
           hand(46, 1015, "Accessibility (WCAG AA) and security reviews always apply", 17)]
    L_ += [tick(864 + (i % 2) * 390, 980 + (i // 2) * 34) for i in range(3)]
    L_.append(hand(864, 1046, "Next to move: spending (3 → 5), from July", 17))
    write_example("delegation-board", "Delegation Board", "".join(L_), ["Basket team", "Head of Digital"])


def example_cross_team_retro():
    L_ = []
    for i, row in enumerate([("Make the weekly shop effortless", "9", "8", "Reorder landed; substitutes slipped an iteration"),
                             ("Make checkout quick and trustworthy", "8", "6", "Wallet payments waited on the Wallet API")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 257 + i * 26, v, 16))
            x += (560, 160, 160)[c] if c < 3 else 0
    cols = [(GREEN, ["Self-service deploys freed up Checkout", "Shared on-call rota", "Payments paired with Basket on billing",
                     "Daily sync caught blockers early"], None),
            (PINK_ST, ["Waiting on the Stock API", "The Payments sign-off queue", "Staging kept going down",
                       "The campaign date changed late"], [5, 3, 2, 1]),
            (BLUE_ST, ["Mocks and contracts so teams don't wait", "Read access instead of new APIs",
                       "One owner for the test environment", "Map dependencies before big-room planning"], None)]
    spots = [(30, 422, -2), (220, 438, 2), (40, 560, 1), (230, 574, -1)]
    for i, (col, items, votes) in enumerate(cols):
        x = 24 + i * 548
        for k, ((dx, y, rot), t) in enumerate(zip(spots, items)):
            L_.append(note(x + dx, y, t, col, 170, 88, rot, 16))
            if votes:
                L_.append(dots(x + dx + 20, y + 104, votes[k]))
    L_.append(hand(after(42, "Top problem (most dots):"), 808, "waiting on the Stock API", 17))
    for i, v in enumerate(["Warehouse had it as a low priority", "They didn't know our date",
                           "Dependencies weren't raised at planning", "Nobody sees who needs what, and when"]):
        L_.append(hand(after(42, f"Why {i + 1}?"), 842 + i * 34, v, 17))
    L_.append(hand(after(42, "Root cause:"), 988, "dependencies are agreed late, team to team", 17))
    for i, row in enumerate([("Dependency map at every big-room planning", "all five", "Tom"),
                             ("Warehouse joins the cross-team sync", "Basket, Warehouse", "Sam"),
                             ("Contract tests for the Stock API", "Basket, Warehouse", "Alex")]):
        x = 530
        for c, v in enumerate(row):
            L_.append(hand(x, 847 + i * 40, v, 16))
            x += (260, 150)[c] if c < 2 else 0
    L_ += [tick(1138, 814 + i * 30) for i in (0, 1, 3)]
    L_ += [hand(after(1138, "We'll measure success by:"), 958, "blocked days, 9 → 3 an iteration", 17),
           hand(after(1138, "Next cross-team retro:"), 998, "end of Q3", 17)]
    write_example("cross-team-retro-board", "Cross-Team Retro", "".join(L_))


def example_value_stream_map():
    qw = (1632 - 36 - 48) / 4
    L_ = [hand(after(42 + i * (qw + 16), lab), 236, v, 17)
          for i, (lab, v) in enumerate([("Starts when:", "a story is agreed"), ("Ends when:", "it's live for customers"),
                                        ("Unit of work:", "one story"), ("Measured over:", "the last 20 stories")])]
    steps = [("Refine", "Priya + team", "2 h", "70%", "6"), ("Build", "Sam, Jo", "2 d", "90%", "3"),
             ("Review", "another dev", "1 h", "80%", "2"), ("Test", "Alex", "4 h", "85%", "2"),
             ("Sign-off", "Payments lead", "30 min", "95%", "4"), ("Release", "Sam", "1 h", "90%", "1")]
    waits = ["5 d", "1 d", "2 d", "3 d", "2 d"]
    labels = ["Name:", "Who:", "Work time:", "% complete & accurate:", "People / WIP:"]
    cw = (1632 - 28 - 5 * 64) / 6
    for i, vals in enumerate(steps):
        cx = 38 + i * (cw + 64)
        L_ += [hand(after(cx + 12, lab, 10.5), 410 + j * 30, v, 16) for j, (lab, v) in enumerate(zip(labels, vals))]
        L_.append(hand(cx + cw / 2, 682, vals[2], 17, anchor="middle"))
        if i < 5:
            tx = cx + cw + 32
            col = "#DC2626" if waits[i] in ("5 d", "3 d") else PEN
            L_ += [hand(tx, 506, waits[i], 17, col, anchor="middle"), hand(tx, 626, waits[i], 17, col, anchor="middle")]
    tw = (1632 - 36 - 64) / 5
    L_ += [hand(42 + i * (tw + 16), 850, v, 20)
           for i, v in enumerate(["16 working days", "about 3 days", "19%", "5 days, waiting for planning", "Refine (70%)"])]
    L_ += [note(50 + i * 200, 960, t, c, 170, 76, (-2, 1, 2, -1)[i], 14)
           for i, (t, c) in enumerate([("Self-service release checks: no sign-off wait", GREEN),
                                       ("Refine just in time: no 5-day wait", YELLOW),
                                       ("Review the same day", GREEN), ("Platform owns one shared staging", YELLOW)])]
    for i, row in enumerate([("Self-service release checks", "Tom", "16 May"), ("Same-day review rule", "Sam", "next retro")]):
        x = 1144
        for c, v in enumerate(row):
            L_.append(hand(x, 1001 + i * 30, v, 16))
            x += (260, 110)[c] if c < 2 else 0
    write_example("value-stream-map-board", "Value Stream Map", "".join(L_), ["Story to live", "8 May"])


def example_pre_mortem():
    L_ = [hand(92, 245, "1 October", 24),
          hand(after(42, "Project, plan or release:"), 290, "the staples subscriptions pilot", 17),
          hand(after(854, "Failure looks like:"), 290, "customers cancel, Finance stops it, and the team is worn out", 17)]
    themes = [("Customers", [("Customers forgot they'd subscribed, then complained", 4), ("Felt pricier than one-off orders", 1)]),
              ("Payments & tech", [("Repeat billing failed on expired cards", 5), ("Wrong substitutes from stock data", 2)]),
              ("Operations", [("Pickers couldn't spot subscription items", 1), ("Adding items by hand didn't scale", 3)]),
              ("Us", [("We launched to everyone before the pilot ended", 2), ("Nobody owned it while Priya was away", 2)])]
    for i, (theme, items) in enumerate(themes):
        x = 50 + i * 262
        L_.append(hand(x, 470, theme, 18))
        for j, (t, n) in enumerate(items):
            nx, ny = x + j * 12, 484 + j * 118
            L_ += [note(nx, ny, t, PINK_ST, 200, 84, (-2, 2)[j], 15), dots(nx + 20, ny + 100, n)]
    for i, row in enumerate([("1", "Repeat billing fails", "Med", "High", "5"), ("2", "Customers forget, then complain", "High", "Med", "4"),
                             ("3", "Manual work doesn't scale", "High", "Med", "3"), ("4", "Launch before we've learned", "Med", "High", "2")]):
        x = 1144
        for c, v in enumerate(row):
            L_.append(hand(x, 449 + i * 36, v, 16))
            x += (34, 240, 70, 70)[c] if c < 4 else 0
    for i, row in enumerate([("Repeat billing fails", "Spike it with Payments, including expired cards", "Over 1% of charges fail", "Tom"),
                             ("Customers forget", "Reminder email 2 days before each delivery", "Complaints say “didn't know”", "Mei"),
                             ("Manual work doesn't scale", "Cap at 50; automate before growing", "Over 2 hours a day adding items", "Priya"),
                             ("Launch before learning", "Go / no-go on 6 June, with the data", "Pressure to set a launch date", "Priya")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 873 + i * 36, v, 16))
            x += (250, 330, 280)[c] if c < 3 else 0
    L_ += [tick(1138, 844 + i * 30) for i in range(3)]
    L_.append(hand(after(1138, "Review these risks on:"), 1012, "6 June, at the go / no-go", 17))
    write_example("pre-mortem-board", "Pre-mortem", "".join(L_))


def cards3(y, prefix, labels, rows):
    """Handwriting for three_cards(): each row is (title, value per field label)."""
    out = []
    for i, (title, *vals) in enumerate(rows):
        x = 24 + i * 548 + 22
        out.append(hand(x + text_w(f"{prefix} #{i + 1}", 13) + 18, y + 32, title, 17))
        out += [hand(after(x, lab), y + 68 + j * 36, v, 17) for j, (lab, v) in enumerate(zip(labels, vals))]
    return out


def example_lean_coffee():
    L_ = []
    todo = [("Too many meetings on Thursdays", 3), ("How's pairing with Ravi going?", 2), ("Better test data", 2),
            ("Celebrate the reorder launch?", 1), ("Is our WIP limit too low?", 1)]
    for i, (t, n) in enumerate(todo):
        x, y = 50 + (i % 2) * 280, 336 + (i // 2) * 140
        L_ += [note(x, y, t, YELLOW, 190, 84, (-2, 1, 2, -1, 1)[i], 16), dots(x + 20, y + 102, n)]
    L_ += [note(758, 284, "Should we stop estimating in points?", YELLOW, 164, 162, 0, 19), dots(790, 432, 5),
           tick(660, 514), tick(780, 514),
           f'<circle cx="840" cy="586" r="27" fill="none" stroke="{PEN}" stroke-width="2.2"/>']
    L_ += [hand(658, 711 + i * 24, t, 16) for i, t in enumerate(["Try counting items for two iterations;",
                                                                 "keep points for rough sizing of big work.",
                                                                 "Tom checks the forecast still works."])]
    for i, (topic, takeaway) in enumerate([("The retro format feels stale", "Try a Sailboat retro next time"),
                                           ("On-call handover gets missed", "Hand over in the Monday sync")]):
        y = 336 + i * 200
        L_ += [note(1080, y, topic, YELLOW, 190, 84, (-1, 2)[i], 16), note(1300, y + 20, takeaway, GREEN, 190, 84, (2, -2)[i], 16)]
    L_ += cards3(906, "Action", ["Owner:", "Done when:"],
                 [("Count items, not points, for 2 iterations", "Tom", "forecast compared at the retro"),
                  ("Move Thursday refinement to Tuesday", "Priya", "the calendar is updated"),
                  ("Copy anonymised orders for test data", "Alex", "test data is on staging")])
    write_example("lean-coffee-board", "Lean Coffee", "".join(L_))


def example_team_launch():
    L_ = [hand(292, 240, "Monday 3 March", 20),
          hand(46, 268, "a charter, a backlog ready for two iterations, and the last-order card on staging", 19),
          tick(1248, 236), hand(after(1138, "Launch owner:"), 262, "Tom", 17), hand(after(1398, "Daily check-in at:"), 262, "09:30", 17)]
    owners = [["Priya", "Priya", "Mei", "Priya", "Tom"], ["Tom", "Priya", "Tom", "Sam", "Priya"],
              ["Mei", "Priya", "Sam", "Alex", "Tom"], ["Tom", "Alex", "Tom", "Priya", "Tom"]]
    not_yet = {(0, 3), (2, 4), (3, 3)}
    cw = (1632 - 28 - 36) / 4
    for i, col in enumerate(owners):
        cx = 38 + i * (cw + 12)
        for j, who in enumerate(col):
            iy = 430 + j * 66
            if (i, j) not in not_yet:
                L_.append(tick(cx + 14, iy + 1))
            L_.append(hand(after(cx + 36, "Owner:", 10), iy + 36, who + ("  (week 2)" if (i, j) in not_yet else ""), 16))
    L_ += [hand(after(42, "Slice:"), 898, "last-order card on the home page (read-only)", 17),
           hand(after(42, "Who it's for:"), 934, "returning customers in the test group", 17),
           hand(after(42, "Done when:"), 970, "it shows a real last order on staging", 17), tick(42, 1026)]
    L_ += [tick(590, 872 + i * 30) for i in range(5)]
    L_.append(hand(820, 1022, "← still missing", 16, "#DC2626"))
    L_ += [tick(1138, 872 + i * 28) for i in range(4)]
    L_.append(hand(1360, 984, "← once test data is ready", 16, "#DC2626"))
    write_example("team-launch-board", "Team Launch", "".join(L_), ["Basket team", "17–28 February"])


def example_ai_agreement():
    cw3 = (808 - 36 - 28) / 3
    cols = [["Test ideas from our examples", "Summarising customer interviews", "First drafts of release notes",
             "Explaining unfamiliar code"],
            ["Writing code: always reviewed", "SQL for analysis: check results", "Refactoring, with tests first"],
            ["Anything about people's performance", "Customer or payment data", "Accessibility sign-off"]]
    L_ = []
    for i, items in enumerate(cols):
        L_ += [hand(42 + i * (cw3 + 14), 273 + k * 26, t, 16) for k, t in enumerate(items)]
    L_ += [tick(864, 234 + i * 30) for i in range(5)]
    L_ += [hand(after(864, "Approved tools:"), 392, "company assistant, code assistant", 16),
           hand(after(1261, "Policy owner / contact:"), 392, "IT security team", 16)]
    L_ += [tick(42, 548 + i * 30) for i in range(3)]
    L_ += [hand(46, 675 + i * 26, t, 17) for i, t in enumerate(["AI-assisted changes are labelled in the pull request",
                                                                  "Generated tests are read and understood, not just run",
                                                                  "A person checks facts and figures in customer copy"])]
    for i, (lab, v) in enumerate([("Shared prompts live at:", "team wiki"), ("We share what works at:", "the retro"),
                                  ("Who can help others:", "Sam, Mei"), ("Skills we'll keep sharp:", "reading code")]):
        L_.append(hand(after(864, lab), 546 + i * 46, v, 17))
    L_ += [note(1280, 604, "Invented API fields in generated code", PINK_ST, 160, 66, -2, 14),
           note(1462, 610, "Summaries that miss the nuance", PINK_ST, 160, 66, 2, 14),
           note(1300, 680, "New joiners learning less by doing", PINK_ST, 160, 66, 1, 14)]
    for i, row in enumerate([("Time to write tests for a story", "3 h", "2 h", "Faster, but check the edge cases"),
                             ("Review time per pull request", "40 min", "55 min", "Longer: more code to read"),
                             ("Bugs found after release", "4 a month", "4 a month", "No change yet")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 893 + i * 34, v, 16))
            x += (300, 140, 140)[c] if c < 3 else 0
    L_ += [hand(after(1138, lab), 862 + i * 36, v, 17)
           for i, (lab, v) in enumerate([("Review every:", "quarter"), ("Last reviewed:", "2 April"), ("Owner:", "Sam")])]
    L_ += [tick(1138, 986), tick(1138, 1016)]
    write_example("ai-working-agreement-board", "AI Working Agreement", "".join(L_), ["Basket team", "2 April"])


def example_project_kickoff():
    L_ = [hand(300, 241, "too many customers stop after a few orders, and", 19),
          hand(46, 276, "rebuilding the weekly shop is the main reason they give.", 19),
          hand(300, 321, "weekly repeat orders reach 30% and reordering", 19),
          hand(46, 356, "takes under a minute, by the end of Q2.", 19)]
    hw = (810 - 46) / 2
    for i, items in enumerate([["Reorder the last basket in one tap", "Substitutes for missing items", "Reorder from order history",
                                "Reorder events in analytics", "Accessible to WCAG AA"],
                               ["Subscriptions (a separate bet)", "Personalised offers", "Rebuilding checkout",
                                "Family accounts"]]):
        L_ += [hand(864 + i * (hw + 10), 253 + k * 28, t, 17) for k, t in enumerate(items)]
    # trade-off sliders: one dot per row; only time is fully fixed
    for i, pos in enumerate([0, 4, 2, 3, 1]):
        L_.append(f'<circle cx="{204 + pos * 140}" cy="{538 + i * 38}" r="9" fill="{PEN}"/>')
    L_ += [hand(866, 553 + i * 28, t, 17) for i, t in enumerate(["The summer campaign launches on 30 June",
                                                                   "Payments changes need Payments sign-off",
                                                                   "Must run on the current web platform",
                                                                   "Customer data stays in the UK and EU"])]
    L_ += [hand(after(1275, lab), 506 + i * 34, v, 16)
           for i, (lab, v) in enumerate([("Sponsor:", "Head of Digital"), ("Product owner:", "Priya"), ("Delivery lead:", "Tom"),
                                         ("Team(s):", "Basket, with Search"), ("Key experts:", "Store Ops, Payments"),
                                         ("Decision forum:", "fortnightly steering")])]
    L_ += [note(48, 864, "Stock data may not be good enough", PINK_ST, 150, 80, -2, 15),
           note(214, 876, "Payments sign-off slows releases", PINK_ST, 150, 80, 2, 15),
           note(380, 864, "Campaign date set before scope is clear", YELLOW, 150, 80, -1, 15),
           note(130, 962, "Store Ops may resist substitutes", YELLOW, 150, 76, 1, 15)]
    for i, row in enumerate([("Last-order card live", "returning customers see it", "end of March"),
                             ("One-tap reorder", "repeat orders at 25%", "end of April"),
                             ("Substitutes", "fewer second orders", "end of May"),
                             ("Campaign ready", "repeat orders at 30%", "30 June")]):
        x = 596
        for c, v in enumerate(row):
            L_.append(hand(x, 853 + i * 34, v, 16))
            x += (170, 210)[c] if c < 2 else 0
    L_ += [tick(1138, 822 + i * 30) for i in (0, 1, 2, 5)]
    L_.append(hand(after(1138, "Next review of this board:"), 1016, "end of each month", 17))
    write_example("project-kickoff-board", "Project Kickoff", "".join(L_), ["Reorder made easy", "Head of Digital"])


def example_release_forecast():
    cx0, cy0, cx1, cy1 = 104, 224, 1082, 676
    cw = (cx1 - cx0) / 12
    px = lambda i: cx0 + i * cw
    py = lambda v: cy1 - v / 48 * (cy1 - cy0)
    L_ = [hand(cx0 - 12, py(48 - 6 * j) + 6, str(48 - 6 * j), 15, anchor="end") for j in range(1, 8)]
    scope, done = [34, 36, 38, 40, 41, 43], [0, 5, 11, 16, 22, 29]
    path = lambda pts, col, dash, w=3: (f'<path d="M' + " L".join(f"{px(i):g},{py(v):g}" for i, v in pts)
                                        + f'" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{dash}/>')
    L_ += [path(list(enumerate(scope)), PURPLE[0], ' stroke-dasharray="7,4"'), path([(5, 43), (8.6, 46.6)], PURPLE[0], ' stroke-dasharray="3,5"', 2),
           path(list(enumerate(done)), EMERALD[0], ""),
           # each forecast line stops where it meets the growing scope: that's the finish
           path([(5, 29), (5 + 14 / 5.3, 43 + 14 / 5.3)], AMBER[0], ' stroke-dasharray="2,4"'),
           path([(5, 29), (5 + 14 / 4.3, 43 + 14 / 4.3)], AMBER[0], ' stroke-dasharray="2,4"')]
    L_ += [f'<circle cx="{px(i):g}" cy="{py(v):g}" r="4.5" fill="{EMERALD[0]}"/>' for i, v in enumerate(done) if i]
    L_ += [hand(px(5) + 8, py(29) + 22, "today: 29 done", 16),
           hand(px(5 + 14 / 5.3) - 14, py(45.6) - 10, "fast", 15, AMBER[0], anchor="end"),
           hand(px(5 + 14 / 4.3) + 10, py(46.3) + 20, "slow", 15, AMBER[0])]
    for r, row in enumerate([("1", "5", "—", "36"), ("2", "6", "2", "38"), ("3", "5", "2", "40"), ("4", "6", "1", "41"), ("5", "7", "2", "43")]):
        x = 1144
        for c, v in enumerate(row):
            L_.append(hand(x, 265 + r * 34, v, 17))
            x += 110 if c < 3 else 0
    L_ += [hand(after(1138, lab), 614 + i * 36, v, 17)
           for i, (lab, v) in enumerate([("Average per iteration:", "5.8"), ("Slowest 3, average:", "5.3"), ("Fastest 3, average:", "6.3")])]
    L_.append(hand(after(42, "Remaining items (incl. expected growth):"), 846, "16 (14 + 2 growth)", 17))
    for i, (rate, its, date) in enumerate([("5.3", "3.0", "20 June"), ("5.8", "2.8", "18 June"), ("6.3", "2.5", "13 June")]):
        y = 931 + i * 36
        L_ += [hand(208, y, rate, 17), hand(388, y, its, 17), hand(568, y, date, 17)]
    L_ += [note(870, 884, "Splitting substitutes added 3 items", YELLOW, 160, 76, -2, 15),
           note(1050, 890, "Stock API late: could stall substitutes", PINK_ST, 160, 76, 2, 15),
           note(1230, 884, "Ravi up to speed: more throughput", YELLOW, 160, 76, -1, 15),
           hand(after(864, "Next forecast update:"), 1036, "every Friday, after the review", 17)]
    write_example("release-forecast-board", "Release Forecast & Burn-up", "".join(L_), ["Reorder made easy", "13–20 June"])


def example_epic_breakdown():
    L_ = [hand(180, 235 + i * 34, t, 19) for i, t in enumerate([
        "busy households who shop weekly", "spend 40 minutes rebuilding the same basket", "Reorder made easy epic",
        "set of reorder features", "lets them repeat their shop in one tap", "searching for each item again",
        "remembers the basket and fills the gaps"])]
    L_ += [hand(866, 251 + i * 26, t, 17) for i, t in enumerate(["Repeat orders 22% → 30%", "Median basket time under 10 min"])]
    L_ += [hand(866, 375 + i * 26, t, 17) for i, t in enumerate(["Reorder clicks per visit", "Baskets started from a reorder"])]
    L_ += [hand(1277, 251 + i * 26, t, 17) for i, t in enumerate(["Last-order card with one-tap reorder,", "in-stock items only, for 10%",
                                                                    "of returning customers"])]
    L_ += [hand(after(1275, "Persevere if…"), 380, "25% use it within 4 weeks", 16),
           hand(after(1275, "Pivot or stop if…"), 420, "fewer than 10% use it", 16)]
    feats = [("Last-order card", "see the last basket", "at a glance", 1, True), ("One-tap reorder", "fill the basket", "in one tap", 1, True),
             ("Substitutes", "no gaps when", "items are out", 2, False), ("Order history", "reorder any", "past shop", 0, False),
             ("Usual-item reminders", "fewer forgotten", "items", 1, False)]
    cw = (1632 - 36 - 48) / 5
    for i, (name, ben1, ben2, size, mvp) in enumerate(feats):
        cx = 42 + i * (cw + 12)
        L_ += [hand(after(cx + 14, "Name:"), 596, name, 17), hand(after(cx + 14, "Benefit:"), 630, ben1, 17),
               hand(cx + 16, 657, ben2, 17), tick(cx + 56 + size * 50, 700)]
        if mvp:
            L_.append(tick(cx + 14, 734))
    L_ += [note(50 + i * 192, 898, t, YELLOW, 176, 70, (-2, 1, 2, -1)[i], 15)
           for i, t in enumerate(["Show the last order on the home page", "Reorder adds every in-stock item",
                                  "Flag unavailable items", "Track reorder clicks"])]
    L_.append(note(170, 976, "Hide the card for first-time customers", YELLOW, 176, 64, 1, 15))
    L_ += [hand(866, 879 + i * 26, t, 17) for i, t in enumerate(["Subscriptions", "Personalised offers", "Native app changes"])]
    L_ += [hand(866, 1001 + i * 26, t, 16) for i, t in enumerate(["Loads in under 1 second on mobile",
                                                                   "WCAG AA; works with a screen reader"])]
    L_ += [note(1280, 898, "Stock API from Warehouse (for substitutes)", YELLOW, 170, 72, -2, 14),
           note(1462, 904, "Analytics events need privacy sign-off", YELLOW, 170, 72, 2, 14),
           note(1360, 978, "Nothing needed from Payments for the MVP", YELLOW, 170, 64, -1, 14)]
    write_example("epic-breakdown-canvas", "Epic Breakdown Canvas", "".join(L_), ["Reorder made easy", "Priya"])


def example_daily_sync():
    L_ = [hand(258, 240, "returning customers can see their last order and reorder it in one tap", 19),
          hand(after(920, "Days left:"), 240, "6", 20)]
    L_ += [tick(1138, 228 + i * 24) for i in range(3)]
    cw = (1082 - 20 - 30) / 4
    cols = [[("Reorder from order history", YELLOW), ("Save favourites", YELLOW)],
            [("Offer a substitute if out of stock", PINK_ST), ("Reorder adds every item", YELLOW)],
            [("Track reorder events", YELLOW)], [("Show the last order on the home page", YELLOW)]]
    for i, items in enumerate(cols):
        cx = 34 + i * (cw + 10)
        for j, (t, col) in enumerate(items):
            L_.append(note(cx + 40 + j * 30, 472 + j * 120, t, col, 170, 76, (-2, 2)[j], 15))
    L_ += [hand(316, 576, "blocked 2 days: Stock API", 15, "#DC2626"), hand(586, 576, "waiting for privacy sign-off", 15)]
    for i, row in enumerate([("Offer a substitute", "Stock API (Warehouse)", "yes", "Sam, Jo"),
                             ("Track reorder events", "privacy sign-off", "no", "Priya")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 855 + i * 40, v, 16))
            x += (160, 160, 70)[c] if c < 3 else 0
    L_ += [note(600, 866, "Test data for reorders (Alex and Tom stay)", YELLOW, 180, 84, -2, 15),
           note(810, 878, "Too many meetings on Thursdays", YELLOW, 180, 84, 2, 15)]
    L_ += [tick(1138, 822 + i * 30) for i in (0, 1, 3, 4, 5)]
    L_.append(hand(after(1138, "If a check fails, we'll try:"), 1016, "oldest items first, right to left", 16))
    write_example("daily-sync-board", "Daily Sync", "".join(L_), ["Basket team", "09:30, at the board"])


def example_backlog_refinement():
    tw = (1632 - 36 - 32) / 3
    L_ = [hand(after(42 + i * (tw + 16), lab), 236, v, 17)
          for i, (lab, v) in enumerate([("Items to refine:", "the top 5 in the backlog"),
                                        ("Ready for (iteration or date):", "iteration 6 (from 12 May)"),
                                        ("Who's here:", "Priya, Sam, Jo, Alex, Mei")])]
    cards = [("Reorder from history moves up; Save favourites moves down", YELLOW, ["Customer panel cares", "less about favourites"]),
             ("For weekly shoppers. Done when the basket refills and gaps are flagged", YELLOW, ["Substitutes: only for", "out-of-stock items"]),
             ("Substitutes → (a) flag missing items (b) suggest swaps", YELLOW, ["Split by rule: in-stock", "first, then swaps"]),
             ("Bread out of stock → shown as unavailable", GREEN, ["Mapped reorder (4 rules)", "and substitutes (3)"]),
             ("Flag missing: S · Suggest swaps: L", YELLOW, ["All S or M except", "Suggest swaps (L)"]),
             ("Flag missing ✓ · Suggest swaps ✗ (needs Stock API)", YELLOW, ["2 ready, 1 half ready,", "2 need answers first"])]
    cw = (1604 - 50) / 6
    for i, (sticky_, col, note_lines) in enumerate(cards):
        cx = 38 + i * (cw + 10)
        L_.append(note(cx + 26, 478, sticky_, col, 206, 116, (-2, 1, 2, -1, 1, -2)[i], 16))
        L_ += [hand(cx + 16, 697 + k * 24, t, 15) for k, t in enumerate(note_lines)]
    rows = [("Reorder from history", "—", "yes", "M", "✓", "—"),
            ("Substitutes", "flag missing; suggest swaps", "yes", "S, L", "half", "Stock API date? (Sam)"),
            ("Save favourites", "—", "yes", "S", "✓", "—"),
            ("Share basket with family", "—", "partly", "S", "✗", "privacy wording (Priya)"),
            ("Usual-item reminders", "email; in-app", "no", "M", "✗", "consent wording (Mei)")]
    for i, row in enumerate(rows):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 893 + i * 36, v, 16, "#DC2626" if v == "✗" else PEN))
            x += (250, 220, 140, 80, 80)[c] if c < 5 else 0
    L_ += [tick(1138, 862 + i * 30) for i in (0, 1, 2, 4)]
    L_.append(hand(after(1138, "Next refinement:"), 1020, "Tuesday 13 May, 45 minutes", 17))
    write_example("backlog-refinement-board", "Backlog Refinement", "".join(L_), ["Basket team", "6 May"])


def example_kanban_cadences():
    # per cadence: (run it?, when, who, inputs → outputs)
    cads = [(True, "09:15, at the board", "the whole team", "board → today's focus"),
            (True, "Mondays, 10:00", "lead + requesting teams", "requests → items pulled"),
            (True, "before each release", "team + on-call", "done work → release plan"),
            (True, "every other Thursday", "team + Checkout, Basket", "metrics → one improvement"),
            (True, "monthly", "all platform teams", "capacity → shared fixes"),
            (False, "—", "—", "folded into operations review"),
            (True, "quarterly", "leads + Head of Digital", "goals → investment mix"),
            (True, "monthly: cloud cost review", "team + Finance", "the bill → savings to try")]
    cw, ch = (1632 - 28 - 36) / 4, (430 - 90) / 2
    L_ = []
    for i, (run, *vals) in enumerate(cads):
        r, c = divmod(i, 4)
        cx, cy = 38 + c * (cw + 12), 212 + r * (ch + 12)
        if run:
            L_.append(tick(cx + 18, cy + 26))
        L_ += [hand(after(cx + 18, lab, 10), cy + 96 + j * 26, v, 15) for j, (lab, v) in enumerate(zip(["When:", "Who:", "Inputs → outputs:"], vals))]
    L_ += [hand(after(42, "Space available (WIP limit minus items in progress):"), 676, "5 − 3 = 2", 17),
           hand(after(42, "How we choose:"), 710, "cost of delay first, then the oldest request", 17)]
    for i, t in enumerate(["Log retention change", "New staging per team", "Cost alerts", "Upgrade the database"]):
        L_.append(note(50 + (i % 2) * 180, 784 + (i // 2) * 120, t, YELLOW, 160, 70, (-2, 2, 1, -1)[i], 15))
    for i, row in enumerate([("Monitoring dashboards", "two incidents went unseen last month"),
                             ("Faster test environment", "blocking Basket's test data")]):
        L_ += [hand(439, 827 + i * 40, row[0], 16), hand(609, 827 + i * 40, row[1], 15)]
    sdr = [("5 days", "7 days", "split big requests"), ("8 a week", "7", "—"), ("0", "3", "swarm on the oldest first"),
           ("under 10%", "15%", "track waits on vendors"), ("4 out of 5", "3.8", "ask Checkout what's missing"),
           ("cost per order £0.04", "£0.05", "the cost review")]
    for i, (exp, act, action) in enumerate(sdr):
        y = 712 + i * 40
        worse = act in ("7 days", "3", "15%", "£0.05")
        L_ += [hand(1110, y, exp, 16), hand(1280, y, act, 16, "#DC2626" if worse else PEN), hand(1400, y, action, 16)]
    L_.append(hand(after(864, "Top improvement to try:"), 1016, "swarm on anything past its SLE before pulling new work", 16))
    write_example("kanban-cadences-board", "Kanban Cadences", "".join(L_), ["Store Platform", "15 May"])


def example_sprint_review():
    L_ = [hand(after(42, "Team & sprint:"), 226, "Basket team · Sprint 18 (28 April – 9 May)", 17),
          hand(after(42, "Sprint Goal:"), 262, "reorder in-stock items in one tap, and flag what's unavailable", 17),
          tick(274, 310), hand(after(42, "What we learned about the goal:"), 344, "flagging works; substitutes need the Stock API first", 16)]
    for i, row in enumerate([("Weekly repeat orders", "22%", "25%", "30%"), ("Median basket time", "38 min", "21 min", "10 min"),
                             ("Reorder clicks per visit", "—", "0.18", "0.25")]):
        x = 870
        for c, v in enumerate(row):
            L_.append(hand(x, 265 + i * 32, v, 17))
            x += (300, 140, 140)[c] if c < 3 else 0
    spots = [(40, 526, -2), (290, 538, 2), (40, 650, 1), (290, 662, -1), (165, 720, 2)]
    zones = [[("One-tap reorder (in-stock items)", YELLOW), ("Unavailable items flagged", YELLOW),
              ("Reorder from order history", YELLOW), ("Email confirmation", YELLOW)],
             [("Store Ops: flagging is clear", GREEN), ("Customer panel: “so much faster”", GREEN),
              ("Finance: worried about substitute margins", PINK_ST), ("Marketing: feature it in the summer campaign", BLUE_ST)],
             [("A rival launched subscriptions", YELLOW), ("Stock API slipping two weeks", YELLOW),
              ("Campaign date fixed: 30 June", YELLOW)]]
    for i, items in enumerate(zones):
        x = 24 + i * 548
        for (dx, y, rot), (t, col) in zip(spots, items):
            L_.append(note(x + dx, y, t, col, 190, 88, rot, 16))
    bw = (1082 - 20 - 20) / 3
    for i, items in enumerate([["Rule for discontinued items", "Margin check for substitutes"],
                               ["Substitutes move to Sprint 19", "Order history: a smaller first slice"], ["Dark mode"]]):
        cx = 34 + i * (bw + 10)
        L_ += [note(cx + 16 + j * 166, 920 + j * 14, t, YELLOW, 150, 74, (-2, 2)[j], 15) for j, t in enumerate(items)]
    L_ += [hand(after(1138, lab), 890 + i * 38, v, 16)
           for i, (lab, v) in enumerate([("Likely next Sprint Goal:", "substitutes for out-of-stock items"),
                                         ("Release / forecast update:", "13–20 June, unchanged"),
                                         ("Decisions needed from stakeholders:", "read access to stock data"),
                                         ("Who follows up:", "Priya, by Wednesday")])]
    write_example("sprint-review-board", "Sprint Review", "".join(L_))


def example_buffering_swarming():
    L_ = []
    for i, row in enumerate([("Sprint 14", "7 items", "2", "22%", "payments bug"), ("Sprint 15", "8", "1", "11%", ""),
                             ("Sprint 16", "7", "3", "30%", "Saturday incident"), ("Sprint 17", "8", "2", "20%", "Stock API workaround"),
                             ("Sprint 18", "8", "2", "20%", "test data")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 265 + i * 34, v, 16))
            x += (120, 170, 170, 120)[c] if c < 4 else 0
    L_ += [hand(after(42, "Average % unplanned over the last 5:"), 422, "about 20%", 17),
           hand(after(864, "Buffer this iteration (%):"), 232, "20%", 17), hand(after(864, "In days or items:"), 264, "about 2 items", 17)]
    L_ += [tick(864, 348 + i * 26) for i in range(3)]
    L_ += [hand(1277, 249 + i * 54, t, 16) for i, t in enumerate(["anything not in the plan when the sprint starts",
                                                                   "whoever is on the support rota",
                                                                   "Priya swaps out the lowest item",
                                                                   "pull in a tech debt item"])]
    for i, (bx, v) in enumerate([(276, "4"), (213, "9"), (339, "3"), (282, "2")]):
        L_.append(hand(bx, 548 + i * 34, v, 19, anchor="middle"))
    L_ += [tick(42, 556 + i * 34) for i in range(5)]
    L_.append(hand(after(42, "Our own trigger:"), 726, "someone says “I'm stuck” at two syncs in a row", 17))
    cw = (782 - 40) / 5
    for i, lines_ in enumerate([["Tom calls it", "at the board"], ["2 or 3 people,", "not everyone"], ["5 minutes,", "at the board"],
                                ["mob in the", "Basket room"], ["at the next", "daily sync"]]):
        L_ += [hand(860 + 14 + i * (cw + 10), 697 + k * 24, t, 15) for k, t in enumerate(lines_)]
    for i, row in enumerate([("6 May", "Substitute flag bug", "blocked 4+ hours", "Sam, Jo, Alex", "1 day", "pair on payments code"),
                             ("29 Apr", "Reorder double-adds", "older than 9 days", "Jo, Ravi", "2 days", "split it earlier"),
                             ("5 Apr", "Checkout outage", "severity 2 incident", "Sam, Platform", "4 hours", "we need better alerts")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 893 + i * 34, v, 16))
            x += (90, 220, 170, 170, 120)[c] if c < 5 else 0
    L_ += [hand(after(1138, "Buffer used last iteration (%):"), 860, "25%", 17), hand(after(1138, "Number of swarms:"), 894, "3", 17),
           tick(1138, 978), hand(after(1138, "Next iteration's buffer (%):"), 1016, "20%, unchanged", 17)]
    write_example("buffering-swarming-board", "Buffering & Swarming", "".join(L_), ["Basket team", "9 May"])


def example_ageing_wip():
    cx0, cy0, cx1, cy1 = 104, 224, 1082, 668
    colw = (cx1 - cx0) / 5
    py = lambda v: cy1 - v / 20 * (cy1 - cy0)
    L_ = [hand(cx0 - 12, py(2 * j) + 6, str(2 * j), 15, anchor="end") for j in range(1, 10)]
    L_ += [hand(cx0 + (i + 0.5) * colw, 688, n, 16, anchor="middle")
           for i, n in enumerate(["Building", "Review", "Testing", "Waiting sign-off", "To release"])]
    for v, col in ((4.5, EMERALD[0]), (6, AMBER[0]), (9, RED[0])):
        L_.append(L(cx0, py(v), cx1, py(v), col, 2.5, ' stroke-dasharray="8,4"'))
    # open items: (column, age in days, label for the old ones)
    items = [(0, 1, ""), (0, 2, ""), (0, 5, ""), (1, 3, ""), (1, 7, "Order history: 7 days"), (2, 2, ""),
             (2, 10, "Promo price rules: 10 days"), (3, 6, ""), (3, 8, "Billing spike: 8 days"), (4, 1, "")]
    seen = {}
    for c, age, lab in items:
        k = seen.get(c, 0)
        seen[c] = k + 1
        x = cx0 + (c + 0.5) * colw + (k - 1) * 22
        col = "#DC2626" if age > 9 else AMBER[0] if age > 6 else PEN
        L_.append(f'<circle cx="{x:g}" cy="{py(age):g}" r="9" fill="{col}"/>')
        if lab:
            L_.append(hand(x + 16, py(age) + 6, lab, 15, col))
    started = [("Last-order card", "3 Mar", "6 Mar", "3"), ("Reorder button", "5 Mar", "12 Mar", "5"),
               ("Flag unavailable", "17 Mar", "21 Mar", "4"), ("Email confirmation", "18 Mar", "20 Mar", "2"),
               ("Reorder events", "24 Mar", "1 Apr", "6"), ("Order history", "31 Mar", "10 Apr", "9"),
               ("Copy test data", "7 Apr", "10 Apr", "3"), ("Price-change tag", "14 Apr", "18 Apr", "4"),
               ("Favourites API", "22 Apr", "30 Apr", "7"), ("Out-of-stock rules", "14 Apr", "30 Apr", "12")]
    for i, row in enumerate(started):
        x = 1144
        for c, v in enumerate(row):
            L_.append(hand(x, 265 + i * 34, v, 15))
            x += (200, 90, 90)[c] if c < 3 else 0
    L_ += [hand(after(1138, lab), 644 + i * 30, v, 17)
           for i, (lab, v) in enumerate([("50th percentile (days):", "4.5"), ("70th percentile (days):", "6"),
                                         ("85th percentile (days):", "9")])]
    L_ += [hand(326, 860, "9", 26, anchor="middle"),
           hand(after(42, "Based on how many items, from when to when:"), 918, "the last 10, March to April", 17),
           hand(after(42, "The clock starts when:"), 956, "someone pulls it into Building", 17),
           hand(after(42, "The clock stops when:"), 994, "it's released to customers", 17)]
    L_ += [note(870 + i * 230, 966, t, PINK_ST, 210, 72, (-2, 2, -1)[i], 15)
           for i, t in enumerate(["Promo price rules, 10 days: swarm it today", "Billing spike, 8 days: what's needed to finish?",
                                  "Order history, 7 days: ask at the sync"])]
    write_example("ageing-wip-board", "Ageing WIP & Service Level Expectation", "".join(L_), ["Basket team", "9 May"])


def example_blocker_clustering():
    log = [("3 Apr", "Order history", "Waiting for Payments sign-off", "outside", "3"),
           ("8 Apr", "Reorder events", "Privacy sign-off", "outside", "4"),
           ("10 Apr", "Copy test data", "No staging access", "outside", "2"),
           ("15 Apr", "Favourites API", "Unclear acceptance criteria", "inside", "1"),
           ("17 Apr", "Checkout fix", "Waiting for Payments sign-off", "outside", "2"),
           ("22 Apr", "Substitutes", "Stock API not ready", "outside", "6"),
           ("24 Apr", "Price-change tag", "Staging down", "outside", "1"),
           ("29 Apr", "Reorder button", "Waiting for code review", "inside", "2"),
           ("2 May", "Promo price rules", "Waiting for Payments sign-off", "outside", "3")]
    L_ = []
    for i, row in enumerate(log):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 265 + i * 34, v, 16))
            x += (90, 220, 340, 170)[c] if c < 4 else 0
    for i, t in enumerate(["Privacy sign-off: 4 days", "No staging access: 2 days", "Staging down: 1 day",
                           "Review wait: 2 days", "Unclear criteria: 1 day", "Sign-off: 3 days"]):
        L_.append(note(1146 + (i % 3) * 164, 300 + (i // 3) * 120, t, PINK_ST, 146, 72, (-2, 1, 2, 1, -1, -2)[i], 15))
    clusters = [("Sign-offs", ["Payments 3d", "Privacy 4d", "Payments 2d", "Payments 3d"], "4", "12"),
                ("Other teams' APIs", ["Stock API 6d"], "1", "6"), ("Environments", ["Access 2d", "Staging 1d"], "2", "3"),
                ("Review waits", ["Code review 2d"], "1", "2"), ("Unclear requirements", ["Criteria 1d"], "1", "1")]
    cw = (1632 - 28 - 40) / 5
    for i, (name, items, n, days) in enumerate(clusters):
        cx = 38 + i * (cw + 10)
        L_.append(hand(after(cx + 12, "Cluster:"), 670, name, 17))
        L_ += [note(cx + 16 + (j % 2) * 140, 696 + (j // 2) * 64, t, PINK_ST, 126, 52, (-2, 2, 1, -1)[j], 14)
               for j, t in enumerate(items)]
        L_ += [hand(after(cx + 12, "Count:"), 848, n, 18), hand(after(cx + cw / 2 + 4, "Days:"), 848, days, 18,
                                                               "#DC2626" if days == "12" else PEN)]
    L_ += [hand(after(42, "Biggest cluster:"), 982, "sign-offs: 12 of 24 days", 17),
           hand(after(42, "Root cause:"), 1018, "every change waits for one person to approve it", 16),
           hand(after(574, "Experiment to fix it:"), 982, "self-service checks for low-risk changes", 16),
           hand(after(574, "Owner & review date:"), 1018, "Tom, review on 6 June", 16)]
    for i, row in enumerate([("March", "6", "15"), ("April", "9", "24")]):
        L_ += [hand(1144, 1007 + i * 30, row[0], 16), hand(1304, 1007 + i * 30, row[1], 16), hand(1444, 1007 + i * 30, row[2], 16)]
    write_example("blocker-clustering-board", "Blocker Clustering", "".join(L_))


def example_impediments():
    cols = [[("Thursday meeting overload · about 3 h a week each · Tom · 6 May", PINK_ST)],
            [("Test data isn't realistic · bugs found late · Alex · 10 Apr", PINK_ST),
             ("Reviews wait · 2 days an item · Sam · 29 Apr", PINK_ST)],
            [("Payments sign-off on every release · 2–3 days each · Head of Digital · 3 Apr", PINK_ST),
             ("Stock API late · substitutes stalled · Head of Warehouse · 22 Apr", PINK_ST)],
            [("No staging access for new joiners", PINK_ST), ("Platform added team access", GREEN),
             ("Deploy queue", PINK_ST), ("Self-service deploys", GREEN)]]
    L_ = []
    for i, items in enumerate(cols):
        x = 38 + i * 404
        for j, (t, col) in enumerate(items):
            if i == 3:
                nx, ny = x + 20 + (j % 2) * 180, 280 + (j // 2) * 150 + (j % 2) * 20
                L_.append(note(nx, ny, t, col, 170, 96, (-2, 2, 1, -1)[j], 16))
            else:
                L_.append(note(x + 30 + j * 40, 280 + j * 170, t, col, 230, 120, (-2, 2)[j], 17))
    rungs = [("the team, at the daily sync", "2"), ("Tom", "5"), ("Head of Digital", "10"), ("the portfolio group", "3 June")]
    for k, (who, days) in enumerate(rungs):
        ry, rx = 1042 - (k + 1) * 58 - k * 8, 42 + k * 48
        rw = 772 - k * 48
        L_ += [hand(after(rx + 250, "Who:", 10.5), ry + 30, who, 16), hand(rx + rw - 90, ry + 30, days, 17, anchor="middle")]
    for i, row in enumerate([("No staging access", "2 days per new joiner", "Platform", "6", "ask Platform first"),
                             ("Deploy queue", "a day per release", "Checkout, Platform", "21", "automate it"),
                             ("Unclear criteria", "rework", "Example Mapping", "14", "map it first")]):
        x = 870
        for c, v in enumerate(row):
            L_.append(hand(x, 839 + i * 36, v, 16))
            x += (230, 190, 150, 90)[c] if c < 4 else 0
    write_example("impediments-board", "Impediments Board", "".join(L_))


def example_pairing_mobbing():
    cw = (1632 - 28 - 36) / 4
    L_ = []
    for i, (use, swap) in enumerate([("risky payments code", "20 minutes"), ("new features, test first", "each test"),
                                     ("teaching Ravi the codebase", "15 minutes"), ("swarms and tricky bugs", "10 minutes")]):
        cx = 38 + i * (cw + 12)
        L_ += [hand(after(cx + 16, "Use it for:"), 344, use, 17), hand(after(cx + 16, "Swap every:"), 378, swap, 17)]
    names = ["Priya", "Sam", "Jo", "Alex", "Mei", "Tom", "Ravi"]
    cell_w, cell_h = (700 - 28 - 130) / 8, (400 - 130) / 8
    tallies = {(1, 0): 1, (2, 1): 4, (3, 0): 2, (3, 1): 2, (3, 2): 1, (4, 0): 3, (4, 2): 3, (5, 3): 1, (6, 1): 3, (6, 2): 2, (6, 3): 2}
    for r, n in enumerate(names):
        ry = 554 + r * cell_h
        L_.append(hand(64, ry + cell_h / 2 + 3, n, 15))
    for (r, c), k in tallies.items():
        L_.append(hand(168 + c * cell_w + cell_w / 2, 554 + r * cell_h + cell_h / 2 + 7, "|" * k, 20, anchor="middle"))
    L_ += [hand(after(756, lab), 546 + i * 36, v, 16)
           for i, (lab, v) in enumerate([("We pair or mob by default on:", "payments; new joiners' work"),
                                         ("We work solo on:", "small fixes, spikes"), ("Swap roles every (min):", "20"),
                                         ("Take a break every (min):", "50"), ("Rotate partners every:", "iteration"),
                                         ("Setup & tools:", "big screen, shared editor")])]
    L_ += [tick(756, 784), tick(756, 814)]
    for i, row in enumerate([("Payments", "Jo", "Sam", "pair"), ("Test automation", "Ravi", "Alex", "ping-pong"),
                             ("Data", "Tom", "Priya", "pair"), ("Cloud, CI/CD", "Alex", "Platform", "mob")]):
        x = 1236
        for c, v in enumerate(row):
            L_.append(hand(x, 579 + i * 36, v, 15))
            x += (130, 95, 95)[c] if c < 3 else 0
    for i, row in enumerate([("Substitute suggestions", "Sam + Jo", "driver / navigator"),
                             ("Reorder test suite", "Ravi + Alex", "ping-pong")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 991 + i * 34, v, 17))
            x += (330, 260)[c] if c < 2 else 0
    tw = (810 - 36 - 32) / 3
    for i, lines_ in enumerate([["Jo now reviews payments code", "fewer review waits"],
                                ["pairing all day is tiring", "the mob felt slow at first"],
                                ["a break every 50 minutes", "rotate pairs on Mondays"]]):
        L_ += [hand(866 + i * (tw + 16), 981 + k * 24, t, 16) for k, t in enumerate(lines_)]
    write_example("pairing-mobbing-board", "Pairing & Mobbing", "".join(L_), ["Basket team", "12 May"])


def example_adkar():
    hw = (1632 - 54) / 2
    L_ = [hand(after(42, "What's changing:"), 228, "pickers choose substitutes for out-of-stock items", 17),
          hand(after(42, "Why now:"), 262, "fewer second orders, and customers have asked for it", 17),
          hand(after(60 + hw, "Who's affected:"), 228, "pickers in 12 stores, store managers, customer service", 17),
          hand(after(60 + hw, "Key dates:"), 262, "pilot in one store from 2 June; all stores in July", 17)]
    names = ["Awareness", "Desire", "Knowledge", "Ability", "Reinforcement"]
    groups = [("Pickers, pilot store", [4, 3, 2, 1, 1]), ("Store managers", [5, 4, 3, 2, 2]),
              ("Customer service", [3, 3, 2, 2, 1]), ("Basket team", [5, 5, 4, 3, 2]), ("Store Ops lead", [5, 2, 3, 3, 2])]
    for r, (g, scores) in enumerate(groups):
        ry = 424 + r * 37
        L_.append(hand(52, ry + 20, g, 16))
        for i, s in enumerate(scores):
            cx = 292 + i * 222 + 111 - 60 + (s - 1) * 30
            L_.append(f'<circle cx="{cx:g}" cy="{ry + 18:g}" r="11" fill="none" stroke="{PEN}" stroke-width="2"/>')
        barrier = next(names[i] for i, s in enumerate(scores) if s <= 3)
        L_.append(hand(1422, ry + 22, barrier, 17, "#DC2626"))
    cw = (1632 - 48) / 5
    for i, act in enumerate(["Priya explains the why at huddles", "pickers help design the screen", "a one-page guide with examples",
                             "practice runs before the pilot", "share wins weekly with managers"]):
        L_.append(hand(after(24 + i * (cw + 12) + 16, "Our action:"), 866, act, 15))
    for i, row in enumerate([("Customer service", "Awareness", "a briefing on why, and what customers will see", "Priya", "23 May"),
                             ("Pickers, pilot store", "Desire", "two pickers co-design the substitute screen", "Mei", "30 May")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 1006 + i * 26, v, 15))
            x += (220, 160, 400, 140)[c] if c < 4 else 0
    L_ += [hand(after(1138, lab), 986 + i * 26, v, 15)
           for i, (lab, v) in enumerate([("We'll recognise success by:", "pickers suggest swaps without asking"),
                                         ("We'll measure adoption by:", "% of missing items with a substitute"),
                                         ("Re-assess on:", "4 weeks into the pilot")])]
    write_example("adkar-board", "ADKAR Change Readiness", "".join(L_), ["Substitutes in stores", "Head of Store Ops"])


def example_delivery_metrics():
    cw = (1632 - 28 - 36) / 4
    metrics = [("2 a week", "3 a week", "daily", "deploy pipeline log", 0), ("12 days", "7 days", "under 2 days", "commit to live", 0),
               ("18%", "12%", "under 10%", "incident tickets", 0), ("6 hours", "4 hours", "under 1 hour", "incident tickets", 1)]
    L_ = []
    for i, (ago, now, target, src, trend) in enumerate(metrics):
        cx = 38 + i * (cw + 12)
        L_ += [hand(after(cx + 16, lab), 320 + j * 30, v, 17) for j, (lab, v) in
               enumerate(zip(["3 months ago:", "Now:", "Target:"], [ago, now, target]))]
        L_ += [hand(after(cx + 16, "Measured from:"), 410, src, 16), tick(cx + 16 + trend * 90, 448)]
    debt = [("Basket API: one big endpoint", "Basket", "every change touches it; 2 days extra a feature", "L", "prudent, deliberate", "Sam"),
            ("No contract tests with Payments", "Checkout", "releases wait for manual sign-off", "M", "reckless, inadvertent", "Alex"),
            ("Copy-pasted price rules", "Basket", "bugs fixed twice; promo errors", "S", "reckless, deliberate", "Jo"),
            ("Old staging setup", "Platform", "staging goes down; blocked days", "M", "prudent, inadvertent", "Platform"),
            ("Flaky reorder tests", "Basket", "reruns waste 30 minutes a day", "S", "reckless, inadvertent", "Ravi")]
    for i, row in enumerate(debt):
        x = 48
        for c, v in enumerate(row):
            if c == 4:  # the debt type is two words: one per line to fit the column
                L_ += [hand(x, 613 + i * 36 + k * 14, part, 13) for k, part in enumerate(v.split(", "))]
            else:
                L_.append(hand(x, 621 + i * 36, v, 15))
            x += (230, 140, 300, 110, 110)[c] if c < 5 else 0
    L_ += [note(1196, 626, "Copy-pasted price rules", PINK_ST, 150, 56, -2, 14),
           note(1430, 626, "Basket API: one big endpoint", GREEN, 150, 56, 2, 14),
           note(1196, 764, "No contract tests; flaky tests", ORANGE_ST, 150, 56, 1, 14),
           note(1430, 764, "Old staging setup", BLUE_ST, 150, 56, -1, 14)]
    L_ += [hand(after(42, "% of each iteration for debt & enablers:"), 988, "20% (from the capacity split)", 17),
           hand(after(42, "This iteration we'll pay down:"), 1022, "contract tests with Payments, flaky reorder tests", 17),
           hand(after(864, "Metrics reviewed every:"), 988, "month, at the service delivery review", 17),
           hand(after(864, "What the trends tell us:"), 1022, "faster and more stable since self-service deploys", 17)]
    write_example("delivery-metrics-board", "Delivery Metrics & Tech Debt", "".join(L_), ["Checkout and Basket", "14 May"])


def example_coaching():
    L_ = [hand(after(42, "What do you want from this conversation?"), 230, "a way to raise test risks earlier, without slowing the team", 17),
          tick(1154, 234), hand(after(1354, "Time:"), 230, "45 minutes", 17)]
    notes = [["Alex: “I find the risky cases", "when it's too late to change", "the design.”", "Success: test risks raised at",
              "refinement, not in testing.", "Matters now: two bugs in", "Sprint 18 were found late."],
             ["Usually tests after the build.", "Hasn't spoken up in refinement:", "“feels like slowing people down”.",
              "Tried: a test checklist; nobody", "reads it.", "In control: own prep, and", "asking questions."],
             ["Ask one “what if…?” at each", "refinement", "Pair with Priya on Example", "Mapping", "Write test ideas on the card",
              "Run a 15-minute risk storm", "Ask Tom to prompt for risks"],
             ["Ask a “what if…?” question", "at each refinement, and pair", "with Priya on Example Mapping", "for the top item.",
              "First step: Tuesday's refinement.", "Might stop me: running out", "of time. Commitment: 8 of 10."]]
    cw = (1632 - 42) / 4
    for i, lines_ in enumerate(notes):
        x = 24 + i * (cw + 14) + 20
        L_ += [hand(x, 529 + k * 26, t, 16) for k, t in enumerate(lines_)]
    for i, row in enumerate([("Ask one “what if…?” question at each refinement", "from Tuesday", "Tom to leave room for it"),
                             ("Example Mapping with Priya for the top item", "next refinement", "Priya's time, 25 minutes"),
                             ("Share what changed at the retro", "end of Sprint 19", "none")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 964 + i * 34, v, 16))
            x += (520, 160)[c] if c < 2 else 0
    L_ += [hand(after(1138, "What I noticed:"), 934, "energy rose when we talked about pairing", 16),
           hand(after(1138, "Did I ask more than tell?"), 970, "mostly; I suggested one option", 16),
           hand(after(1138, "Follow up on:"), 1006, "the retro after Sprint 19", 16)]
    write_example("coaching-conversation-board", "Coaching Conversation", "".join(L_), ["Alex (coach: Tom)", "13 May"])


def example_incident_review():
    hw = (1082 - 54) / 2
    L_ = [hand(after(42, "What happened:"), 230, "checkout failed for most customers", 16),
          hand(after(42, "Impact (who, how long):"), 266, "~3,000 orders, 4 hours", 16),
          hand(after(60 + hw, "Detected by / how:"), 230, "customer service: complaints", 16),
          hand(after(60 + hw, "Duration to recover:"), 266, "4 hours (09:10–13:10)", 16), tick(264, 300)]
    L_ += [tick(1138, 232 + i * 24) for i in range(4)]
    timeline = [("08:55", "Payment provider rotated its API certificate", "nothing: no alert on certificate errors",
                 "nothing; we didn't know"),
                ("09:10", "Payments start failing at checkout", "a few complaints, looked like card issues", "customer service told people to retry"),
                ("10:30", "Complaints spike; customer service escalates", "something is wrong with checkout", "Sam paged; looked at our last release"),
                ("11:40", "Logs show certificate errors to the provider", "it's the provider's change, not ours", "Platform team joined; rolled back the release"),
                ("13:10", "New certificate installed; checkout recovers", "the fix worked", "watched for 30 minutes, then closed it")]
    for i, row in enumerate(timeline):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 450 + i * 36, v, 16))
            x += (120, 520, 420)[c] if c < 3 else 0
    cw = (1082 - 20 - 32) / 5
    factors = [["No alert on certificate errors", "Rollback took 40 min"], ["Provider changes not shared with us"],
               ["Only Sam knew the payment setup"], ["Saturday: fewer people around"], ["Customer service had no way to escalate quickly"]]
    for i, items in enumerate(factors):
        cx = 34 + i * (cw + 8)
        L_ += [note(cx + 12 + (j % 2) * 18, 732 + j * 90, t, PINK_ST, 170, 76, (-2, 2)[j], 15) for j, t in enumerate(items)]
    L_ += [note(1136, 714, "Customer service spotted it", GREEN, 110, 80, -2, 14), note(1252, 760, "Platform joined fast", GREEN, 110, 80, 2, 14),
           note(1410, 714, "Not on a big promo day", YELLOW, 110, 80, 2, 14), note(1526, 760, "Sam happened to be free", YELLOW, 110, 80, -2, 14)]
    for i, row in enumerate([("Alert on payment-provider errors over 2%", "detect", "Platform", "16 May")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 1040, v, 16))
            x += (640, 340, 260)[c] if c < 3 else 0
    L_.append(hand(48 + 640 + 340 + 260 + 120, 1040, "+ 3 more in the RAID log", 15))
    write_example("incident-review-board", "Blameless Incident Review", "".join(L_), ["Checkout outage, Sat 5 April", "9 April"])


def example_persona_journey():
    L_ = [f'<circle cx="102" cy="268" r="26" fill="none" stroke="{PEN}" stroke-width="2"/>',
          f'<path d="M62,322 q40,-40 80,0" fill="none" stroke="{PEN}" stroke-width="2"/>',
          hand(after(180, "Name:"), 238, "Sarah, 38", 17), hand(after(180, "Role / context:"), 272, "two kids, works full-time", 16),
          hand(after(180, "Tech comfort:"), 306, "high on her phone", 16),
          hand(after(42, "Goals:"), 362, "the weekly shop done fast, nothing forgotten", 15),
          hand(after(42, "Frustrations:"), 392, "rebuilding the same basket every week", 15),
          hand(after(42, "In their words:"), 422, "“I shop on my phone at 10 p.m.”", 15),
          hand(after(42, "Evidence from:"), 452, "12 interviews, order data", 15),
          hand(after(590, "Scenario or goal:"), 230, "doing the weekly shop on a Sunday evening", 17),
          hand(after(590, "Starts when:"), 268, "she opens the app", 17), hand(after(1124, "Ends when:"), 268, "the order is delivered", 17)]
    L_ += [hand(710, 349 + i * 36, t, 18) for i, t in enumerate(["it's Sunday night and the cupboards are nearly empty",
                                                                  "order our usual shop in a few minutes",
                                                                  "get on with my evening"])]
    stages = ["Open the app", "Build the basket", "Fix the gaps", "Pay and choose a slot", "Delivery"]
    sw = (1632 - 28 - 170) / 5
    rows = [(598, 80, ["Opens it on her phone", "Adds items one by one", "Swaps out-of-stock items", "Picks Tuesday's slot", "Checks the bags"], YELLOW),
            (690, 66, ["“What did I buy last time?”", "“Have I missed anything?”", "“Is this swap OK?”", "“Is Tuesday free?”", "“Did they bring it all?”"], BLUE_ST),
            (856, 76, ["Can't see the last order", "40 minutes of scrolling", "Swaps are a surprise", "Slots fill up early", "Missing milk: 2nd order"], PINK_ST),
            (944, 76, ["Last-order card", "One-tap reorder", "Choose swaps in advance", "Save a usual slot", "“You usually buy” list"], GREEN)]
    for x_i, s_ in enumerate(stages):
        L_.append(hand(208 + x_i * sw + 96, 573, s_, 16, "#FDE68A"))
    for y, h, items, col in rows:
        for i, t in enumerate(items):
            L_.append(note(208 + i * sw + 14, y + 4, t, col, sw - 34, h - 14, (-1, 1, -1, 1, -1)[i], 14))
    # emotion line: highs and lows across the five stages
    pts = [(208 + (i + 0.5) * sw, y) for i, y in enumerate([796, 832, 838, 818, 792])]
    L_.append(f'<path d="M' + " L".join(f"{x:g},{y:g}" for x, y in pts) + f'" fill="none" stroke="{PEN}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    L_ += [f'<circle cx="{x:g}" cy="{y:g}" r="5" fill="{PEN}"/>' for x, y in pts]
    write_example("persona-journey-board", "Persona & Journey Map", "".join(L_))


def example_impact_map():
    imp_y = [272.5 + 105 * k for k in range(6)]
    act_y = [325, 535, 745]
    box = lambda x, y, lines_, size=16: [hand(x + 14, y + 40 + k * 24, t, size) for k, t in enumerate(lines_)]
    L_ = box(44, 509, ["Weekly repeat orders from", "22% to 30% by end of Q2"], 17)
    L_.append(hand(after(58, "Measure:", 10.5), 625, "weekly repeat-order rate", 15))
    actors = [["Busy families who shop", "every week"], ["Store pickers"], ["Customer service team"]]
    impacts = [["Reorder instead of rebuilding", "the basket"], ["Come back every week, not", "every few weeks"],
               ["Choose good substitutes", "for missing items"], ["Pick reorders faster"],
               ["Point customers to reorder", "when they call"], ["Log “missing item” calls", "so we can spot patterns"]]
    deliverables = [["Last-order card, one-tap", "reorder"], ["Usual-item reminders"], ["Substitute screen in the", "picking app"],
                    ["Reorders grouped in the", "pick list"], ["A one-page reorder guide"], ["A call reason code"]]
    for a, lines_ in enumerate(actors):
        L_ += box(404, act_y[a], lines_)
    for k in range(6):
        L_ += box(794, imp_y[k], impacts[k]) + box(1244, imp_y[k], deliverables[k])
    L_ += [hand(after(42, "The impact we're least sure of:"), 1000, "pickers choosing substitutes customers accept", 16),
           hand(after(42, "How we'll test it:"), 1032, "pilot in one store; track how many swaps are accepted", 16),
           hand(after(864, "Deliverable to try first:"), 1000, "last-order card with one-tap reorder", 16),
           hand(after(864, "We'll know the impact happened when:"), 1032, "repeat orders rise past 25%", 16)]
    write_example("impact-map-board", "Impact Map", "".join(L_), ["Reorder made easy", "20 February"])


def example_estimation():
    L_ = []
    for i, row in enumerate([("Reorder from order history", "3, 8, 5, 5", "5"), ("Save favourites", "2, 3, 3, 2", "3"),
                             ("Suggest substitutes", "5, 13, 8, 8", "8, 8, 8, 13")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 385 + i * 30, v, 16))
            x += (400, 110, 110)[c] if c < 2 else 0
    L_ += [hand(48 + 400 + 110 + 110, 385, "5", 17), hand(668, 415, "3", 17), hand(668, 445, "8 (split it)", 17)]
    sw = (810 - 20 - 40) / 5
    for i, items in enumerate([["Price tag"], ["Favourites", "Email copy"], ["Order history", "Reminders"],
                               ["Substitutes"], ["Subscriptions"]]):
        cx = 856 + i * (sw + 10)
        L_ += [note(cx + 10, 262 + j * 76, t, YELLOW, sw - 20, 60, (-2, 2)[j], 14) for j, t in enumerate(items)]
    L_.append(hand(after(864, "Reference item that is an “M”:"), 448, "reorder events (6 days)", 16))
    # affinity: (text, x, row); the dashed boundaries fall in the gaps at x=430 and x=790
    items = [("Price-change tag", 50, 0), ("Email copy", 160, 1), ("Favourites", 280, 0), ("Flag missing items", 450, 1),
             ("Order history", 510, 0), ("Reminders", 640, 1), ("Family accounts", 810, 0), ("Subscriptions", 930, 1)]
    for k, (t, x, row) in enumerate(items):
        L_.append(note(x, 630 + row * 90, t, YELLOW, 130, 62, (-2, 2, 1, -1)[k % 4], 14))
    L_.append(f'<path d="M430,612 L430,830 M790,612 L790,830" stroke="{PEN}" stroke-width="2" stroke-dasharray="6,5"/>')
    L_ += [hand(240, 828, "small", 16, anchor="middle"), hand(610, 828, "medium", 16, anchor="middle"),
           hand(940, 828, "large: split", 16, anchor="middle")]
    for i, row in enumerate([("S", "Email confirmation", "one screen, no new data"), ("M", "Reorder events", "new data, privacy check"),
                             ("L", "Order history", "three screens, new API")]):
        x = 1144
        for c, v in enumerate(row):
            L_.append(hand(x, 617 + i * 44, v, 16))
            x += (70, 260)[c] if c < 2 else 0
    L_ += [tick(42, 1042), hand(398, 1033, "2", 18, anchor="middle")]
    L_ += [tick(1138, 990 + i * 26) for i in range(3)]
    write_example("estimation-board", "Estimation", "".join(L_), ["Basket team", "6 May"])


def example_adr():
    L_ = [hand(380, 232, "Read stock levels from a read-only replica for substitutes", 17),
          hand(after(1054, "Deciders:"), 232, "Sam, Warehouse lead, Platform", 17), tick(264, 266)]
    L_ += [hand(44, 399 + i * 26, t, 16) for i, t in enumerate([
        "Substitutes need live stock levels to suggest a swap.",
        "The Warehouse team's Stock API is two weeks late, and may slip again.",
        "Substitutes are our next Sprint Goal, and the campaign date is fixed (30 June).",
        "Warehouse already runs a read-only replica of the stock database for reporting.",
        "We need a decision before Sprint 19 planning on 12 May."])]
    drivers = [(True, "Ship substitutes before the campaign"), (True, "No extra load on the warehouse system"),
               (True, "Easy to switch to the Stock API later"), (False, "Data no more than 5 minutes old"),
               (True, "Customer data stays in the UK and EU")]
    for i, (ok, t) in enumerate(drivers):
        cy = 408 + i * 28
        if ok:
            L_.append(tick(864, cy))
        L_.append(hand(888, cy - 1, t, 16))
    opts = [("Do nothing: wait for the API", "no extra work; one clean interface", "substitutes slip past the campaign", "none", "no"),
            ("Read from the replica", "unblocks us now; warehouse unaffected", "up to 5 min stale; a second path", "S: 3 days", "yes ✓"),
            ("Copy stock data nightly", "simple; no live dependency", "a day stale: bad swaps", "M: 1 week", "no")]
    for i, row in enumerate(opts):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 730 + i * 44, v, 16, EMERALD[0] if "✓" in v else PEN))
            x += (300, 440, 440, 220)[c] if c < 4 else 0
    L_ += [hand(136, 994, "read stock levels from the replica behind one small adapter,", 17),
           hand(44, 1029, "and switch the adapter to the Stock API when it ships.", 17)]
    L_ += [hand(864, 1011, "substitutes can ship in Sprint 19", 15), hand(864, 1037, "one place to change later", 15),
           hand(1260, 1011, "swaps may use 5-minute-old stock", 15), hand(1260, 1037, "replica access to keep secure", 15)]
    write_example("adr-board", "Architecture Decision Record", "".join(L_), ["ADR 007", "8 May"])


def example_experiment_canvas():
    L_ = [tick(232, 296)]
    L_ += [hand(44, 379 + i * 26, t, 16) for i, t in enumerate(["Stories come back from testing with", "missed rules: 4 of the last 9 needed",
                                                               "rework after review."])]
    for i, t in enumerate(["map the top 3 items with Example Mapping before each planning",
                           "the Basket team's refinement",
                           "fewer stories bounce back from testing for missed rules",
                           "rework drops from 4 in 9 to 1 in 9 over two iterations"]):
        L_.append(hand(455, 255 + i * 56, t, 17))
    L_ += [hand(1277, 249 + i * 26, t, 16) for i, t in enumerate(["25 minutes of Example Mapping", "per item, the day before", "planning"])]
    L_ += [hand(1277, 379 + i * 26, t, 16) for i, t in enumerate(["Map just the top item for", "one iteration"])]
    bw = (808 - 36 - 24) / 3
    for i, lines_ in enumerate([["4 of 9 stories", "reworked"], ["1 of 9 or fewer"], ["the sprint board;", "Alex tags rework"]]):
        L_ += [hand(42 + i * (bw + 12) + 14, 620 + k * 24, t, 17) for k, t in enumerate(lines_)]
    L_ += [hand(after(42, "Leading indicator (early signal):"), 704, "pink question cards answered before planning", 16),
           hand(after(42, "Guardrail (what must not get worse):"), 744, "refinement stays under 1 hour a week", 16)]
    L_ += [hand(after(864, lab), 562 + i * 36, v, 16)
           for i, (lab, v) in enumerate([("Owner:", "Priya"), ("Supporters:", "Alex, Tom"), ("Start date:", "Sprint 15, 17 March"),
                                         ("Mid-point check-in:", "Sprint 15 retro"), ("Review date:", "end of Sprint 16")])]
    L_ += [tick(1034, 760),
           note(1278, 628, "People will make time the day before", YELLOW, 170, 72, -2, 15),
           note(1462, 640, "Priya may be in other meetings", YELLOW, 160, 72, 2, 15),
           note(1360, 718, "Tell Search: they share our backlog", YELLOW, 170, 64, -1, 15)]
    L_ += [hand(after(46, "Result vs. target:"), 924, "1 of 10 reworked: target met", 17),
           hand(48, 960, "Planning was quicker too: fewer debates", 16), hand(48, 990, "about what “done” means.", 16),
           tick(608, 941)]
    L_ += [hand(1144, 924, "Most rework came from rules nobody", 16), hand(1144, 954, "had said out loud. Mapping surfaces", 16),
           hand(1144, 984, "them while they're cheap to change.", 16), hand(after(1142, "Share the learning with:"), 1024, "Search & Browse, Checkout", 16)]
    write_example("experiment-canvas", "1% Experiment Canvas", "".join(L_), ["3", "Basket team"])


def example_root_cause():
    L_ = [hand(after(42, "What happened:"), 226, "reordered baskets show old promotion prices", 17),
          hand(after(854, "When, where, how often:"), 226, "after a promotion ends; 5 times in April", 17),
          hand(after(42, "Impact:"), 254, "refunds, complaints, and 2 days of fixes each time", 17)]
    bones = [(294, ["Only Jo knows the price code", "No time to tidy it"], ["Promotions end at midnight"], ),
             (524, ["Promo changes skip refinement"], ["Ops set promos in a spreadsheet"]),
             (754, ["Price rules copied in 3 places", "No test for promo expiry"], ["End dates not in the order data"])]
    for bx, top_items, bot_items in bones:
        L_ += [note(bx - 224, 422 + k * 60, t, PINK_ST, 108, 52, (-2, 2)[k], 13) for k, t in enumerate(top_items)]
        L_ += [note(bx - 224, 576 + k * 58, t, PINK_ST, 108, 52, (2, -2)[k], 13) for k, t in enumerate(bot_items)]
    L_ += [hand(928, 543 + i * 24, t, 15) for i, t in enumerate(["Old promo prices", "in reordered", "baskets"])]
    whys = [("Why does the basket keep the old price?", "it copies the price from the last order"),
            ("Why doesn't it re-check the price?", "the reorder path has its own price rules"),
            ("Why its own rules?", "copied in a hurry to hit the March launch"),
            ("Why wasn't it caught?", "no test covers a promotion ending"),
            ("Why no test?", "nobody owns pricing, so nobody adds them")]
    for i, (a, b_) in enumerate(whys):
        ry = 376 + i * 66
        L_ += [hand(1212, ry - 1, a, 15), hand(1140, ry + 26, b_, 15)]
    L_.append(hand(after(1148, "Root cause:", 12), 724, "price rules copied, with no owner and no tests", 16))
    L_ += [tick(42, 864 + i * 32) for i in range(5)]
    for i, row in enumerate([("One shared price service for every path", "Jo", "Sprint 20"),
                             ("Tests for promotion start and end", "Ravi", "Sprint 19"),
                             ("Pricing gets a named owner", "Priya", "this week")]):
        x = 596
        for c, v in enumerate(row):
            L_.append(hand(x, 894 + i * 36, v, 16))
            x += (280, 100)[c] if c < 2 else 0
    L_ += [hand(after(1138, lab), 862 + i * 40, v, 16) for i, (lab, v) in enumerate([
        ("We'll measure:", "wrong-price complaints a month"), ("Baseline:", "5 in April"), ("Check on:", "end of June"),
        ("Result:", "0 in June")])]
    L_.append(tick(1138, 1032))
    write_example("root-cause-board", "Root Cause Analysis", "".join(L_), ["Basket team", "14 May"])


def example_project_closeout():
    L_ = [hand(after(42, "Original goal:"), 228, "weekly repeat orders 22% → 30%, reordering under a minute", 16),
          hand(after(42, "What we delivered:"), 260, "one-tap reorder, substitutes, order history, reminders", 16)]
    for i, row in enumerate([("Weekly repeat orders", "30%", "29%", "nearly there; still rising"),
                             ("Median basket time", "10 min", "12 min", "reorder users: 3 min"),
                             ("Second order within 2 days", "5%", "6%", "substitutes helped most")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 349 + i * 32, v, 16))
            x += (250, 130, 130)[c] if c < 3 else 0
    for i, row in enumerate([("Repeat orders reach 30%", "end of Q3", "weekly dashboard", "Priya"),
                             ("Fewer missing-item calls", "September", "call reason codes", "Customer service"),
                             ("Lower cost per order", "Q4", "Finance report", "Finance"),
                             ("Subscriptions pilot decision", "6 June ✓", "pilot results", "Head of Digital")]):
        x = 870
        for c, v in enumerate(row):
            L_.append(hand(x, 266 + i * 34, v, 16))
            x += (260, 130, 230)[c] if c < 3 else 0
    L_ += [tick(42, 548 + i * 28) for i in (0, 1, 2, 3, 4, 6)]
    L_.append(hand(after(42, "Handed to:"), 766, "Basket team (it's their product now)", 16))
    sub = (1082 - 48) / 3
    learned = [[("Slicing thin and releasing weekly", YELLOW), ("Example Mapping before planning", GREEN),
                ("Pairing on payments code", YELLOW)],
               [("Agree dependencies at big-room planning", YELLOW), ("Name an owner for shared code early", YELLOW),
                ("Start the privacy sign-off in week 1", GREEN)],
               [("How fast customers took to reorder", BLUE_ST), ("How much time sign-offs cost", BLUE_ST)]]
    for i, items in enumerate(learned):
        sx = 588 + i * (sub + 10)
        L_ += [note(sx + 14 + (k % 2) * 160, 566 + (k // 2) * 104 + (k % 2) * 16, t, col, 150, 84, (-2, 2, 1)[k], 15)
               for k, (t, col) in enumerate(items)]
    for i, row in enumerate([("Retire the old reorder email", "Mei", "end of July"), ("Close the analytics test account", "Sam", "15 July"),
                             ("Hand the stock replica adapter to Warehouse", "Sam", "when the API ships")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 924 + i * 34, v, 16))
            x += (420, 170)[c] if c < 2 else 0
    L_ += [hand(after(864, "People and teams to thank:"), 888, "Store Ops, Payments, Warehouse, Platform", 16),
           hand(866, 926, "the customer panel, and the pilot-store pickers", 16),
           hand(after(864, "How we'll celebrate:"), 960, "team lunch, and a thank-you at the all-hands", 16),
           hand(after(864, "Share the story and lessons with:"), 996, "the other product groups, at the showcase", 16)]
    write_example("project-closeout-board", "Project Close-out", "".join(L_), ["Reorder made easy", "4 July"])


def example_team_onboarding():
    L_ = [tick(42, 234 + i * 32) for i in range(7) if i != 5]
    L_.append(hand(240, 391, "← picked on day 2", 15, "#DC2626"))
    cw = (1054 - 40) / 5
    for i, lines_ in enumerate([["laptop worked first time;", "staging access took a day"], ["Priya's customer tour", "was the highlight"],
                                ["paired with Alex on a", "reorder test"], ["first daily sync and", "refinement"],
                                ["shipped a copy fix;", "check-in with Tom"]]):
        cx = 588 + i * (cw + 10)
        L_ += [hand(cx + 14, 413 + k * 24, t, 15) for k, t in enumerate(lines_)]
    for i, row in enumerate([("Priya", "Product owner", "what we build and why", "✓"), ("Alex", "Tester, your buddy", "anything, any time", "✓"),
                             ("Sam", "Developer", "payments and the basket API", "✓"), ("Tom", "Scrum Master", "how we work; blockers", "✓"),
                             ("Store Ops lead", "Stores", "how picking really works", ""), ("Platform on-call", "Platform", "environments and deploys", "✓")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 609 + i * 32, v, 16))
            x += (200, 170, 320)[c] if c < 3 else 0
    L_ += [tick(864 + (i % 2) * 392, 580 + (i // 2) * 38) for i in range(10) if i != 8]
    L_ += [hand(after(42, lab), 888 + i * 38, v, 17) for i, (lab, v) in enumerate([
        ("Buddy:", "Alex"), ("We'll meet every:", "day for 15 minutes, then weekly"), ("Ask me about:", "tests, tools, who to ask"),
        ("Until (date):", "end of April")])]
    cw3 = (1082 - 48) / 3
    for i, (goal, date, going) in enumerate([("ship 3 small items", "16 April", "4 shipped; confident"),
                                             ("pick up items alone", "16 May", ""), ("lead a refinement", "16 June", "")]):
        cx = 588 + i * (cw3 + 10)
        L_ += [hand(after(cx + 14, "Goal:", 10.5), 942, goal, 16), hand(after(cx + 14, "Check-in date:", 10.5), 972, date, 16)]
        if going:
            L_.append(hand(after(cx + 14, "How it's going:", 10.5), 1002, going, 16))
    write_example("team-onboarding-board", "Team Onboarding", "".join(L_), ["Ravi", "17 March"])


def example_delivery_pipeline():
    cw = (1632 - 28 - 72) / 7
    stages = [("1 h", "4 h", "rarely", "review", "1 approval", "Git", "devs"),
              ("6 min", "—", "2%", "none", "it builds", "CI server", "Platform"),
              ("14 min", "—", "8% (flaky)", "none", "all pass", "CI server", "Alex"),
              ("5 min", "—", "1%", "none", "no high risks", "scanner", "Platform"),
              ("8 min", "—", "staging down", "none", "smoke tests", "deploy tool", "Platform"),
              ("3 min", "1 day", "rarely", "a button", "self-service checks", "deploy tool", "team"),
              ("—", "—", "—", "none", "alerts on errors", "dashboards", "on-call")]
    L_ = []
    for i, vals in enumerate(stages):
        cx = 38 + i * (cw + 12)
        for j, (lab, v) in enumerate(zip(["Time:", "Waits before:", "Fails:", "Manual steps:", "Gate:", "Tool:", "Owner:"], vals)):
            red = v in ("4 h", "1 day", "8% (flaky)", "staging down")
            L_.append(hand(after(cx + 14, lab, 10.5), 292 + j * 30, v, 14, "#DC2626" if red else PEN))
    for i, (lab, v) in enumerate([("Commit to production, typical:", "about 2 days"), ("Of that, time spent waiting:", "over 90%"),
                                  ("Pipeline runs per day:", "25"), ("Runs that fail:", "10%")]):
        L_.append(hand(after(42, lab), 648 + i * 40, v, 16))
    for i, (lab, v) in enumerate([("Time to fix a broken build:", "about 1 hour"), ("Flaky or skipped steps:", "6 flaky tests"),
                                  ("Deploys per week:", "3"), ("Releases rolled back:", "1 in April")]):
        L_.append(hand(after(436, lab), 648 + i * 40, v, 16))
    L_ += [note(870 + (i % 4) * 192, 640 + (i // 4) * 110, t, col, 172, 86, (-2, 2, 1, -1, 2, -2)[i], 15)
           for i, (t, col) in enumerate([("Reviews wait half a day", PINK_ST), ("Releases wait a day for a slot", PINK_ST),
                                         ("Flaky reorder tests: reruns", YELLOW), ("Staging goes down", PINK_ST),
                                         ("No alert on payment-provider errors", YELLOW), ("Rollback is a manual script", YELLOW)])]
    L_ += [hand(after(42, lab), 940 + i * 30, v, 16) for i, (lab, v) in enumerate([
        ("The change we'll make:", "fix or quarantine the 6 flaky tests"), ("Expected effect (which number moves?):", "runs that fail: 10% → 3%"),
        ("Owner:", "Ravi, with Alex"), ("Check it on:", "end of Sprint 19")])]
    L_ += [tick(864 + (i % 2) * 392, 954 + (i // 2) * 34) for i in (0, 1, 3, 4)]
    write_example("delivery-pipeline-board", "Delivery Pipeline Canvas", "".join(L_), ["Basket web app", "15 May"])


def example_test_strategy():
    layers = [("reorder journeys on real phones", "no", "each story, before release", "Alex"),
              ("reorder, checkout, substitutes", "yes: 12 journeys", "every merge to main", "Alex, Ravi"),
              ("basket API, prices, stock replica", "yes", "every commit", "developers"),
              ("price rules, basket maths", "yes: 1,400 tests", "every commit", "developers")]
    L_ = []
    for i, vals in enumerate(layers):
        yt = 232 + 163 * i
        L_ += [hand(after(416, lab, 10.5), yt + 64 + j * 28, v, 15)
               for j, (lab, v) in enumerate(zip(["What we test:", "Automated:", "Runs when:", "Owner:"], vals))]
    gates = [("Commit", "unit tests pass", "yes", "developer"), ("Pull request", "review + integration tests", "yes", "reviewer"),
             ("Main", "end-to-end journeys", "yes", "Alex"), ("Main", "security scan: no high risks", "yes", "Platform"),
             ("Staging", "accessibility check (WCAG AA)", "yes", "Mei"), ("Staging", "price and promo tests", "yes", "Ravi"),
             ("Release", "self-service checks", "yes", "team")]
    for i, row in enumerate(gates):
        x = 870
        for c, v in enumerate(row):
            L_.append(hand(x, 265 + i * 32, v, 15))
            x += (150, 300, 140)[c] if c < 3 else 0
    L_ += [tick(864, 628 + i * 32) for i in (0, 1, 2, 3, 4)]
    L_.append(hand(1040, 818, "← copy of real orders", 15, "#DC2626"))
    L_ += [note(1290, 624, "Promo prices after a promotion ends", PINK_ST, 160, 80, -2, 15),
           note(1468, 640, "Payments and refunds", PINK_ST, 150, 72, 2, 15),
           note(1300, 730, "Substitutes: right item, right price", YELLOW, 160, 80, 1, 15),
           note(1478, 744, "Screen reader on checkout", YELLOW, 140, 72, -2, 15)]
    L_ += [hand(44, 1003, "tests pass at every level, reviewed by a second person, accessible (WCAG AA),", 16),
           hand(44, 1033, "deployed to staging, and accepted by Priya", 16),
           hand(after(864, "Fix first:"), 1002, "6 flaky reorder tests (Ravi)", 16),
           hand(after(864, "Time set aside each iteration:"), 1034, "half a day, from the 20% for debt", 16)]
    write_example("test-strategy-board", "Test Strategy", "".join(L_), ["Basket web app", "16 May"])


def example_release_readiness():
    L_ = [hand(after(42, lab), 230 + i * 34, v, 15) for i, (lab, v) in enumerate([
        ("Release / version:", "Substitutes 1.0"), ("Outcome for users:", "no gaps when items are out"),
        ("Main changes:", "swap screen; customer approval"), ("Who's affected:", "pilot-store customers, pickers"),
        ("Deploy date:", "28 May (switched off)"), ("Switch-on date:", "2 June, one store")])]
    cw = (1082 - 48) / 3
    ch = (300 - 88) / 2
    L_ += [tick(588 + (i % 3) * (cw + 10) + 14, 212 + (i // 3) * (ch + 10) + 28) for i in (1, 4)]
    L_ += [hand(964, 300, "← switch on per store", 15), hand(964, 416, "← one store, then all 12 in July", 15)]
    L_ += [tick(42 + (i % 2) * 392, 552 + (i // 2) * 36) for i in range(10) if i != 7]
    L_.append(hand(632, 660, "n/a", 15))
    L_ += [tick(120, 768), hand(after(264, "Decided by:"), 764, "Priya, Store Ops lead", 15), hand(after(560, "When:"), 764, "30 May", 15)]
    L_ += [hand(after(864, lab), 548 + i * 42, v, 16) for i, (lab, v) in enumerate([
        ("If it goes wrong, we'll see:", "swap complaints, picking time up, error alerts"),
        ("We'll undo it by:", "turning the flag off for the store"), ("Time to undo:", "under 5 minutes"),
        ("Who decides to roll back:", "on-call developer, or the store manager"),
        ("What we can't undo (data, messages):", "swap emails already sent"), ("Rollback last tested on:", "27 May, on staging")])]
    for i, row in enumerate([("Pilot-store customers", "swaps are coming; how to approve them", "31 May", "email + app", "Mei"),
                             ("Pickers, pilot store", "the new swap screen", "29 May", "huddle + practice", "Store Ops"),
                             ("Customer service", "what customers will see, FAQs", "30 May", "briefing", "Priya"),
                             ("Other product teams", "it's live in one store", "2 June", "#releases", "Tom")]):
        x = 48
        for c, v in enumerate(row):
            L_.append(hand(x, 952 + i * 30, v, 15))
            x += (210, 380, 140, 160)[c] if c < 4 else 0
    L_ += [hand(after(1138, "Check the outcome on:"), 918, "16 June (two weeks in)", 16),
           hand(after(1138, "Remove the feature flag by:"), 954, "end of July, after all stores", 16)]
    write_example("release-readiness-board", "Release Readiness & Strategy", "".join(L_), ["Substitutes 1.0", "2 June"])


def example_cd_health():
    # (score 1–5, note) per practice, in board order; four groups of three
    scores = [(5, "everything in Git"), (3, "some branches live a week"), (4, "about 14 minutes"),
              (2, "6 flaky tests; we rerun"), (2, "copied by hand"), (4, "scan on every merge"),
              (4, "one button"), (3, "flags new for substitutes"), (3, "big promo changes"),
              (2, "outage found by complaints"), (3, "rollback is a script"), (4, "blameless reviews held")]
    L_ = []
    tops = [266 + 54 * k for k in range(3)] + [458 + 54 * k for k in range(3)] + [650 + 54 * k for k in range(3)] + \
           [842 + 54 * k for k in range(3)]
    for cy, (s, n) in zip(tops, scores):
        cx = 628 + (s - 1) * 28
        L_ += [f'<circle cx="{cx}" cy="{cy + 25}" r="10" fill="{PEN}"/>',
               T(cx, cy + 29, str(s), 10, "white", MONO, weight=600, anchor="middle"), hand(846, cy + 19, n, 14)]
    L_ += [note(1140, 228, "Test automation we trust: 2", PINK_ST, 160, 80, -2, 15),
           note(1316, 240, "Test data on demand: 2", PINK_ST, 160, 80, 2, 15),
           note(1480, 228, "Monitoring: 2", PINK_ST, 140, 80, -1, 15),
           note(1180, 360, "Small branches: votes from 2 to 5. Why?", YELLOW, 180, 90, 1, 15)]
    L_ += [hand(after(1138, lab), 660 + i * 32 + (14 if i > 2 else 0), v, 16) for i, (lab, v) in enumerate([
        ("Practice:", "test automation we trust"), ("We'll try:", "fix or quarantine the 6 flaky tests"),
        ("Owner / check on:", "Ravi · end of Sprint 19"), ("Practice:", "monitoring & observability"),
        ("We'll try:", "alerts on payment-provider errors"), ("Owner / check on:", "Platform · 16 May")])]
    L_ += [hand(after(1138, lab), 966 + i * 32, v, 16) for i, (lab, v) in enumerate([
        ("Last check (date and total):", "February: 33"), ("This check (total out of 60):", "39"), ("Next check:", "August")])]
    write_example("cd-health-check-board", "Continuous Delivery Health Check", "".join(L_), ["Basket and Checkout", "16 May"])


def example_roadmap():
    lane = (674 - 212) / 3
    goals = [(["Make the weekly shop", "effortless"], "repeat orders 30%"), (["Nobody forgets an", "item"], "2nd orders under 5%"),
             (["Checkout is quick", "and trustworthy"], "drop-off under 12%")]
    L_ = []
    for i, (lines_, m) in enumerate(goals):
        ly = 212 + i * lane
        L_ += [hand(44, ly + 45 + k * 26, t, 17) for k, t in enumerate(lines_)]
        L_.append(hand(after(42, "Measure:", 10.5), ly + 114, m, 15))
    cw = (1632 - 272 - 42) / 3
    cells = [[["Substitutes in all 12 stores"], ["Reminders for usual items"], ["Wallet payments"]],
             [["Subscriptions (if the pilot works)"], ["“You usually buy” list"], ["Faster checkout"]],
             [["Family accounts", "Recipe-to-basket"], ["Smart shopping list"], ["Saved cards across devices"]]]
    for c, col in enumerate(cells):
        x = 310 + c * (cw + 14)
        chip = BLUE_ST if c == 2 else YELLOW
        for r, items in enumerate(col):
            ly = 212 + r * lane
            L_ += [note(x + 40 + k * 190, ly + 36 + k * 14, t, chip, 170, 76, (-2, 2)[k], 15) for k, t in enumerate(items)]
    for i, row in enumerate([("Personalised offers", "no clear customer need yet"), ("Voice ordering", "few customers ask for it"),
                             ("Rebuild checkout", "fix the slow parts instead")]):
        L_ += [hand(48, 865 + i * 32, row[0], 16), hand(278, 865 + i * 32, row[1], 16)]
    for i, row in enumerate([("families keep subscriptions", "the 50-customer pilot"), ("reminders don't annoy", "email 500 customers"),
                             ("wallets cut drop-off", "a test with 10% of users")]):
        L_ += [hand(598, 865 + i * 32, row[0], 16), hand(858, 865 + i * 32, row[1], 16)]
    L_ += [hand(after(1142, "We review this every:"), 830, "month, after the review", 16),
           hand(after(1142, "Next review:"), 864, "4 July", 16),
           hand(after(1142, "An item moves to Now when:"), 898, "it's shaped and a team has room", 16),
           hand(1144, 931, "(its assumptions tested)", 16), hand(after(1142, "Shared with:"), 966, "the whole company, on the wiki", 16),
           tick(1142, 1030), tick(1392, 1030)]
    write_example("roadmap-board", "Now · Next · Later Roadmap", "".join(L_), ["Online grocery", "Priya", "6 June"])


def example_user_manual():
    people = [("Priya", "Product owner", "09:00–17:30", [
                  ["I've talked to customers that", "week"], ["a message; I reply within the", "hour"], ["in person, with an example"],
                  ["drains: status meetings;", "energises: customer calls"], ["“no” means “not yet”, not", "“never”"],
                  ["customer research, priorities"]]),
              ("Sam", "Developer", "08:00–16:00", [
                  ["I get a long block of focus", "time in the morning"], ["chat after 13:00; mornings", "are for focus"],
                  ["in writing first, then talk"], ["drains: context switching;", "energises: hard problems"],
                  ["quiet in meetings isn't", "disagreeing"], ["payments, APIs, debugging"]]),
              ("Jo", "Developer", "10:00–18:30", [
                  ["I'm pairing, or have music", "on and a clear task"], ["chat any time; I'll say if", "I'm busy"],
                  ["straight away, kindly"], ["drains: unclear tickets;", "energises: shipping things"],
                  ["I ask lots of questions", "because I'm interested"], ["front end, accessibility"]]),
              ("Mei", "Designer", "09:30–17:30, Thu off", [
                  ["I've seen the real problem,", "not just the solution"], ["tag me in the design", "channel"],
                  ["show me where users", "struggled"], ["drains: pixel debates;", "energises: user testing"],
                  ["a sketch is a question, not", "a decision"], ["journeys, prototypes, research"]])]
    hh = (1060 - 148 - 14) / 2
    L_ = []
    for k, (name, role, hours, answers) in enumerate(people):
        x, w = (24, 808) if k % 2 == 0 else (846, 810)
        y = 148 + (k // 2) * (hh + 14)
        L_ += [hand(after(x + 18, "Name:"), y + 80, name, 17), hand(after(x + 306, "Role:"), y + 80, role, 16),
               hand(after(x + 536, "Hours / time zone:"), y + 80, hours, 15)]
        cw = (w - 60) / 2
        for i, lines_ in enumerate(answers):
            px, py = x + 18 + (i % 2) * (cw + 24), y + 126 + (i // 2) * 106
            L_ += [hand(px + 2, py + 23 + j * 24, t, 16) for j, t in enumerate(lines_)]
    write_example("user-manual-board", "Personal User Manual", "".join(L_), ["Basket team", "5 March"])


def example_motivation():
    order = ["Status", "Power", "Order", "Honour", "Acceptance", "Freedom", "Goal", "Relatedness", "Curiosity", "Mastery"]
    move = {"Mastery": -1, "Curiosity": -1, "Relatedness": -1, "Order": 1, "Freedom": 1}  # -1 up (more), 1 down (less)
    cw = (1632 - 28 - 90) / 10
    L_ = [hand(after(42, "The change we're testing:"), 468, "learning payments by pairing with Sam for the next three months", 17)]
    for i, name in enumerate(order):
        cx = 38 + i * (cw + 10)
        y = {-1: 506, 0: 594, 1: 682}[move.get(name, 0)]
        L_.append(note(cx + 6, y, name, BLUE_ST, cw - 12, 64, (-2, 1, 2, -1)[i % 4], 17))
    L_ += [hand(after(42, lab), 904 + i * 36, v, 15) for i, (lab, v) in enumerate([
        ("What surprised me:", "status matters least; mastery most"), ("What I need more of:", "hard problems with someone to learn from"),
        ("What I'll ask for:", "keep some solo front-end work"), ("What I can offer others:", "accessibility pairing")])]
    kw = (1082 - 48) / 3
    kudos = [(0, "Alex", "finding the price bug before", "the promo went live", "Priya"),
             (2, "Sam", "patient pairing on payments", "code all week", "Jo"),
             (1, "Store Ops pickers", "great feedback on the", "substitute screen", "Mei")]
    for i, (box, to, f1, f2, frm) in enumerate(kudos):
        kx = 588 + i * (kw + 10)
        L_ += [tick(kx + 14 + box * 108, 916), hand(after(kx + 14, "To:"), 946, to, 16),
               hand(after(kx + 14, "For:"), 978, f1, 15), hand(kx + 16, 1005, f2, 15), hand(after(kx + 14, "From:"), 1030, frm, 16)]
    write_example("motivation-board", "Motivation & Recognition", "".join(L_), ["Jo", "12 May"],
                  strip=[f"Card {i}" for i in range(1, 11)])


def example_design_sprint():
    L_ = [hand(after(42, "The challenge:"), 230, "would families set up a staples subscription, and keep it?", 16),
          hand(after(42, "Long-term goal (in two years…):"), 264, "1 in 4 weekly shoppers has a staples subscription", 16),
          hand(after(42, "Sprint questions (what could stop us?):"), 298, "will they trust auto-add? Can they", 16),
          hand(46, 330, "change it easily? Will it feel like a lock-in?", 16)]
    L_ += [hand(after(864 + (i % 2) * 392, lab), 226 + (i // 2) * 40, v, 16) for i, (lab, v) in enumerate([
        ("Decider:", "Priya"), ("Facilitator:", "Tom"), ("Customer expert:", "customer service lead"), ("Tech expert:", "Sam"),
        ("Design:", "Mei"), ("Business / money:", "Finance partner")])]
    cw = (1632 - 56) / 5
    days = [([("Journey: pick staples → set day → skip a week", YELLOW), ("HMW make skipping easy?", YELLOW)],
             "first set-up and the first skip"),
            ([("Sketch: a staples shelf", YELLOW), ("Sketch: a “usual” toggle", YELLOW)], "7 four-step sketches"),
            ([("Heat-map dots on the toggle", YELLOW), ("Storyboard: 8 frames", YELLOW)], "a “usual” toggle, skip anytime"),
            ([("Clickable mock-up in a day", YELLOW), ("Interview script", YELLOW)], "clickable mobile mock-up"),
            ([("4 of 5 set it up unaided", GREEN), ("“Skip” was hard to find", PINK_ST)], "trust needs an easy skip")]
    for i, (stickies, out) in enumerate(days):
        x = 24 + i * (cw + 14)
        L_ += [note(x + 26 + (k % 2) * 30, 594 + k * 100, t, col, cw - 70, 84, (-2, 2)[k], 15) for k, (t, col) in enumerate(stickies)]
        lab = SPRINT_DAYS[i][4]
        L_.append(hand(after(x + 18, lab), 818, out, 14))
    marks = [("Families set it up without help", ["✓", "✓", "✓", "✗", "✓"]),
             ("They feel in control (skip, change)", ["?", "✗", "✓", "✗", "?"]),
             ("They'd pay for it each week", ["✓", "?", "✓", "✓", "✗"])]
    rest = (1082 - 36 - 482) / 5
    for i, (q, ms) in enumerate(marks):
        y = 970 + i * 30
        L_.append(hand(48, y, q, 16))
        L_ += [hand(48 + 482 + k * rest + rest / 2, y, m, 18, {"✓": EMERALD[0], "✗": "#DC2626"}.get(m, PEN), anchor="middle")
               for k, m in enumerate(ms)]
    L_ += [tick(1388, 952), hand(after(1138, "First step and owner:"), 1018, "make skip one tap, test again on 20 June: Mei", 15)]
    write_example("design-sprint-board", "Design Sprint", "".join(L_), ["Staples subscriptions", "9–13 June", "Priya"])


def example_ai_delivery():
    rows = [("summarise interviews", 0, "researcher reads all"), ("draft acceptance criteria", 0, "agreed at refinement"),
            ("code suggestions, tests", 1, "review + tests + scans"), ("generate test data", 1, "Alex checks samples"),
            ("release notes draft", 1, "Priya approves"), ("triage support tickets", 2, "weekly sample check")]
    L_ = []
    for i, (use, lvl, check) in enumerate(rows):
        y = 118 + 148 + i * 34
        L_ += [hand(238, y - 4, use, 15), tick((636, 751, 866)[lvl], y), hand(948, y - 4, check, 15)]
    L_ += [tick(42, 576 + i * 30) for i in range(7) if i != 4]
    L_.append(hand(330, 696, "← not yet", 15, "#DC2626"))
    for i, row in enumerate([("Invented API fields", "2×3", "tests catch them"), ("Customer data in prompts", "1×3", "approved tools only"),
                             ("Agent closes real tickets", "2×2", "weekly sample; can pause it"),
                             ("Skills fade", "2×2", "pair; keep reading code")]):
        x = 598
        for c, v in enumerate(row):
            L_.append(hand(x, 613 + i * 36, v, 15))
            x += (210, 70)[c] if c < 2 else 0
    L_ += [hand(after(1142, lab), 574 + i * 34, v, 15) for i, (lab, v) in enumerate([
        ("Owns the AI policy:", "Head of Digital"), ("Approves new tools:", "IT security"), ("Approves agent access:", "Platform lead"),
        ("Reviews AI incidents:", "incident review, as usual"), ("Trains and supports people:", "Sam and Mei"),
        ("Questions go to:", "#ai-help")])]
    for i, (before, now, target) in enumerate([("7 days", "6 days", "5 days"), ("12%", "11%", "under 10%"),
                                               ("1 in 9", "1 in 10", "same or better"), ("3.6 / 5", "3.9 / 5", "4 / 5")]):
        y = 918 + i * 34
        L_ += [hand(382, y, before, 16), hand(522, y, now, 16), hand(662, y, target, 16)]
    for i, row in enumerate([("Agent drafts support replies; a person sends them", "customer service lead", "1 July"),
                             ("AI writes test data from real order patterns", "Alex", "Sprint 20")]):
        x = 870
        for c, v in enumerate(row):
            L_.append(hand(x, 919 + i * 34, v, 15))
            x += (420, 160)[c] if c < 2 else 0
    L_.append(hand(after(864, "We review this whole board every:"), 1026, "quarter, with the AI Working Agreement", 15))
    write_example("ai-delivery-board", "AI in Delivery", "".join(L_), ["Basket group", "Head of Digital", "September"])


EXAMPLES = {"team-charter-board": example_team_charter, "sprint-planning-board": example_sprint_planning,
            "prioritisation-board": example_prioritisation, "retro-board-start-stop-continue": example_retro,
            "team-topology-board": example_team_topology, "skills-matrix-board": example_skills_matrix,
            "team-health-check-board": example_health_check, "product-vision-board": example_product_vision,
            "opportunity-solution-tree-board": example_opportunity_tree, "okr-board": example_okr,
            "product-bet-canvas": example_product_bet, "story-map-board": example_story_map,
            "example-mapping-board": example_example_mapping, "event-storming-board": example_event_storming,
            "stakeholder-map-board": example_stakeholder_map, "raid-log-board": example_raid_log,
            "dependency-map-board": example_dependency_map, "cross-team-planning-board": example_cross_team_planning,
            "kanban-board-design": example_kanban_design, "status-report-board": example_status_report,
            "value-metrics-board": example_value_metrics, "cynefin-board": example_cynefin,
            "cross-team-sync-board": example_cross_team_sync, "portfolio-kanban-board": example_portfolio_kanban,
            "psych-safety-board": example_psych_safety, "raci-decision-log-board": example_raci,
            "delegation-board": example_delegation, "cross-team-retro-board": example_cross_team_retro,
            "value-stream-map-board": example_value_stream_map, "pre-mortem-board": example_pre_mortem,
            "lean-coffee-board": example_lean_coffee, "team-launch-board": example_team_launch,
            "ai-working-agreement-board": example_ai_agreement, "project-kickoff-board": example_project_kickoff,
            "release-forecast-board": example_release_forecast, "epic-breakdown-canvas": example_epic_breakdown,
            "daily-sync-board": example_daily_sync, "backlog-refinement-board": example_backlog_refinement,
            "kanban-cadences-board": example_kanban_cadences, "sprint-review-board": example_sprint_review,
            "buffering-swarming-board": example_buffering_swarming, "ageing-wip-board": example_ageing_wip,
            "blocker-clustering-board": example_blocker_clustering, "impediments-board": example_impediments,
            "pairing-mobbing-board": example_pairing_mobbing, "adkar-board": example_adkar,
            "delivery-metrics-board": example_delivery_metrics, "coaching-conversation-board": example_coaching,
            "incident-review-board": example_incident_review, "persona-journey-board": example_persona_journey,
            "impact-map-board": example_impact_map, "estimation-board": example_estimation,
            "adr-board": example_adr, "experiment-canvas": example_experiment_canvas,
            "root-cause-board": example_root_cause, "project-closeout-board": example_project_closeout,
            "team-onboarding-board": example_team_onboarding, "delivery-pipeline-board": example_delivery_pipeline,
            "test-strategy-board": example_test_strategy, "release-readiness-board": example_release_readiness,
            "cd-health-check-board": example_cd_health, "roadmap-board": example_roadmap,
            "user-manual-board": example_user_manual, "motivation-board": example_motivation,
            "design-sprint-board": example_design_sprint, "ai-delivery-board": example_ai_delivery}


if __name__ == "__main__":
    build_retros()
    build_sailboat()
    write_redirects()
    build_health_check()
    build_experiment_canvas()
    build_lean_coffee()
    build_epic_breakdown()
    build_story_map()
    build_story_splitting()
    build_example_mapping()
    build_team_charter()
    build_product_vision()
    build_prioritisation()
    build_sprint_planning()
    build_sprint_review()
    build_project_kickoff()
    build_stakeholder_map()
    build_release_forecast()
    build_raid_log()
    build_cross_team_planning()
    build_dependency_map()
    build_okr()
    build_cross_team_sync()
    build_buffering_swarming()
    build_kanban_design()
    build_ageing_wip()
    build_blocker_clustering()
    build_skills_matrix()
    build_impediments()
    build_pairing_mobbing()
    build_pre_mortem()
    build_root_cause()
    build_value_metrics()
    build_opportunity_tree()
    build_team_topology()
    build_ai_agreement()
    build_status_report()
    build_adkar()
    build_portfolio_kanban()
    build_delivery_metrics()
    build_delegation()
    build_coaching_conversation()
    build_psych_safety()
    build_cross_team_retro()
    build_backlog_anatomy()
    build_value_stream_map()
    build_incident_review()
    build_raci()
    build_persona_journey()
    build_impact_map()
    build_estimation()
    build_facilitation_poster()
    build_adr()
    build_team_launch()
    build_daily_sync()
    build_backlog_refinement()
    build_kanban_cadences()
    build_events_poster()
    build_antipattern_spotter()
    build_leading_safety()
    build_delivery_pipeline()
    build_test_strategy()
    build_release_readiness()
    build_cd_health_check()
    build_sdlc_poster()
    build_right_size()
    build_project_closeout()
    build_team_onboarding()
    build_roadmap()
    build_user_manual()
    build_conflict_levels()
    build_feedback()
    build_motivation()
    build_design_sprint()
    build_product_bet()
    build_ai_delivery()
    build_event_storming()
    build_cynefin()
    for make in EXAMPLES.values():   # worked examples read the blank boards, so they run last
        make()
