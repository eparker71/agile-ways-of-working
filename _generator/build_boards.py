#!/usr/bin/env python3
"""Generate the printable A3 facilitation boards (SVG + HTML) for my_agile_tools.

Every board shares the visual language of the Marginal Gains Workshop Board:
navy header band, orange accent, Instrument Serif / Geist / Geist Mono, the
eight colour-coded area pairs, dotted sticky-note zones and footer prompts.

Run:  python3 _generator/build_boards.py      (writes into the parent folder)
"""
import re
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
W, H = 1680, 1190

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import ACCENT, NAVY, SANS, SERIF, MONO, FONT_URL, CREDIT  # noqa: E402  (edit brand.py to rebrand)
INK = "#1E293B"
MUTED = "#64748B"
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
        T(24, 120, tagline, 9, "#475569", MONO, ls=".06em"),
        right,
    ])


def legend(items, x=1356):
    """items: list of (kind, color, label); kind is 'sticky' or 'dot'."""
    out = [T(x, 48 if len(items) != 3 else 44, "LEGEND", 8, "#475569", MONO, ls=".14em")]
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
        out.append(T(x, y, label.upper(), 8, "#475569", MONO, ls=".14em"))
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
        out.append(T(x + w - 16, y + 31, note, 8.5, "white", MONO, anchor="end", ls=".10em", op=".6"))
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
        T(1656, 1138, tag, 8, "#CBD5E1", MONO, anchor="end", ls=".08em"),
        T(24, 1138, CREDIT, 8, "#94A3B8", MONO, ls=".06em"),
    ])


# ---------------------------------------------------------------- output

def guide_for(slug):
    """Facilitator guide that documents a board slug."""
    m = re.match(r"retro-board-(.+)-(sprint|quarter)$", slug)
    if m:
        return f"facilitator-guide-retro-{m.group(1)}.html"
    return f"facilitator-guide-{slug.removesuffix('-board').removesuffix('-poster')}.html"


GUIDE_LINK_CSS = (f"a.guide{{position:fixed;right:16px;bottom:16px;font:500 12px 'Geist',system-ui,sans-serif;color:#fff;"
                  f"background:{NAVY};border-left:4px solid {ACCENT};padding:9px 14px;border-radius:6px;text-decoration:none;"
                  f"box-shadow:0 6px 20px rgba(0,0,0,.25);}}\na.guide:hover{{background:{ACCENT};}}")


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
@media print{{@page{{size:A3 landscape;margin:0;}}html,body{{background:none;}}body{{padding:0;}}svg{{box-shadow:none;width:100%;}}a.guide{{display:none;}}}}
</style>
</head>
<body>
<a class="guide" href="{guide_for(slug)}">Facilitator guide →</a>
{svg_inline}
</body>
</html>
"""
    (OUT / f"{slug}.svg").write_text(svg_file, encoding="utf-8")
    (OUT / f"{slug}.html").write_text(page, encoding="utf-8")
    print("wrote", slug)


RETRO_LEGEND = [("sticky", YELLOW, "Yellow Sticky = What Happened"),
                ("sticky", GREEN, "Green Sticky = Idea / Action"),
                ("dot", ACCENT, "Dot = Vote (3 per person)")]
RETRO_TAG = "Retrospective Kit · Team Reflection · Continuous Improvement"


# ---------------------------------------------------------------- retro: column formats

def retro_columns(slug, title, subtitle, cols, foot_left, foot_right, horizon):
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
    body.append(strip(866, f"ACTIONS WE'LL TAKE INTO THE NEXT {horizon.upper()}"))
    body.append(three_cards(906, "Action", ["Owner:", "Done when:"]))
    body.append(footer(foot_left, foot_right, RETRO_TAG))
    desc = (f"A3 landscape retrospective board: {', '.join(c[0] for c in cols)}. "
            f"Sticky-note zones per column and three action slots for the next {horizon}.")
    write_board(f"{slug}-{horizon}", title, desc, "\n".join(body))


def build_retros(h):
    retro_columns(
        "retro-board-start-stop-continue", "Start · Stop · Continue",
        f"Looking back at the last {h}, what should we change about how we work together?",
        [("Start", EMERALD, "What should we start doing?",
          ["New practices worth trying", "Experiments we keep putting off", "Things other teams do well"]),
         ("Stop", RED, "What should we stop doing?",
          ["Waste and low-value work", "Habits that slow us down", "Meetings or steps nobody would miss"]),
         ("Continue", BLUE, "What should we keep doing?",
          ["What's working well", "Practices worth protecting", "Wins worth amplifying"])],
        "If we could only change one thing, what would it be?",
        "What's the smallest step we can take on it tomorrow?", h)

    retro_columns(
        "retro-board-4ls", "The 4 Ls Retrospective",
        f"Reflect on the last {h} through four lenses: what we liked, learned, lacked and longed for.",
        [("Liked", FOREST, "What did we enjoy?",
          ["Moments of good collaboration", "Things that went better than expected"]),
         ("Learned", BLUE, "What did we discover?",
          ["New skills, tools or insights", "Surprises about users or the system"]),
         ("Lacked", ORANGE, "What was missing?",
          ["Information, people or time", "Clarity, focus or support"]),
         ("Longed For", PURPLE, "What do we wish we had?",
          ["Things that would make work easier", "Changes we'd love to see"])],
        "What did we learn that we don't want to forget?",
        f"Which ‘lacked’ or ‘longed for’ could we fix by 1% next {h}?", h)

    retro_columns(
        "retro-board-mad-sad-glad", "Mad · Sad · Glad",
        f"How did the last {h} feel? Surface the emotions behind the work, then decide what to act on.",
        [("Mad", RED, "What frustrated us?",
          ["Blockers and recurring problems", "Things outside our control", "Moments we felt stuck"]),
         ("Sad", SKY, "What disappointed us?",
          ["Things that didn't go to plan", "Missed opportunities", "Unmet expectations"]),
         ("Glad", EMERALD, "What made us happy?",
          ["Wins and achievements", "People who helped us", "Moments we were proud of"])],
        "What's behind the strongest feelings on this board?",
        f"What would turn one ‘mad’ into a ‘glad’ next {h}?", h)


# ---------------------------------------------------------------- retro: sailboat

def build_sailboat(horizon):
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
                  [f"Our goal for the next {horizon}"], EMERALD[0]))
    b.append(zone(44, 572, 600, 264, 3, "ANCHORS", "What's holding us back?",
                  ["Impediments, waste, slow handoffs"], RED[0]))
    b.append(zone(1000, 572, 636, 264, 4, "ROCKS", "What risks lie ahead?",
                  ["Dependencies, unknowns, deadlines"], AMBER[0]))

    b.append(strip(866, f"ACTIONS WE'LL TAKE INTO THE NEXT {horizon.upper()}"))
    b.append(three_cards(906, "Action", ["Owner:", "Done when:"]))
    b.append(footer("Which anchor, if cut, would let us sail fastest?",
                    f"What can we do next {horizon} to steer clear of the rocks?", RETRO_TAG))
    write_board(f"retro-board-sailboat-{horizon}", "Sailboat Retrospective",
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
        b.append(T(x + 18 + text_w(lead, 20) * 0.82 + 12, ly, f"({hint})", 9, PURPLE[0], MONO, op=".55", ls=".04em"))
        b.append(L(x + 18, ly + 26, x + w - 18, ly + 26, PURPLE[0], 1, ' stroke-opacity=".25"'))
    b.append(T(x + w - 18, y + 306, "TIP: keep it small enough to start tomorrow", 8.5, PURPLE[0], MONO, anchor="end", op=".6", ls=".1em"))

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
        b.append(T(bx + 14, y + 104, hint, 10, BLUE[0], italic=True, op=".55"))
    b.append(field(x + 18, y + 226, "Leading indicator (early signal):", x + w - 18, BLUE[0]))
    b.append(field(x + 18, y + 266, "Guardrail (what must not get worse):", x + w - 18, BLUE[0]))
    b.append(L(x + 18, y + 300, x + w - 18, y + 300))

    # 5 plan
    x, w = 846, 397
    b.append(panel(x, y, w, 320, 5, "Plan & Timebox", ORANGE))
    for i, lab in enumerate(["Owner:", "Supporters:", "Start date:", "Mid-point check-in:", "Review date:"]):
        b.append(field(x + 18, y + 84 + i * 36, lab, x + w - 18, ORANGE[0]))
    b.append(T(x + 18, y + 278, "Timebox:", 11, ORANGE[0], weight=600))
    for i, lab in enumerate(["1 sprint", "2 sprints", "1 quarter"]):
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
               italic=True, anchor="middle", op=".7"))

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
            T(x + w / 2, y + h / 2 + 4, hint, 10, dark, italic=True, anchor="middle", op=".55"))


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
        b.append(T(x + w - 18, y + 90 + i * 34 - 6, h, 8.5, d, MONO, anchor="end", op=".45", ls=".04em"))

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
                                      "Too big for a sprint? Use the Story Splitting poster"], d))
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
            para(24 + 20, y + 54, desc, 10.5, "white", 15, op=".75"),
            R(264, y, 1392, h, light, 10, f' stroke="{dark}" stroke-opacity=".18" stroke-width="1.5"'),
            R(264, y, 1392, h, "url(#dots)", 10),
            T(1640, y + 20, note, 8.5, dark, MONO, anchor="end", op=".5", ls=".1em"),
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
            para(44, y + 52, sub, 10.5, dark, 15, op=".8"),
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
        T(1356, 50, "RUNNING EXAMPLE", 8, "#475569", MONO, ls=".14em"),
        para(1356, 74, ["“As a shopper, I want to check out", "my basket so that I receive", "my order.”"], 15, "#CBD5E1", 19, font=SERIF, italic=True),
    ])
    b = [header("Story Splitting",
                "When a story is too big to finish in a sprint, split it into thin, vertical slices that each deliver value.",
                "Break Down Work · INVEST · SPIDR · Story Splitting Patterns · Vertical Slicing", right)]

    # INVEST row
    invest = [("I", "Independent", ["Can it be built and", "released on its own?"]),
              ("N", "Negotiable", ["Is it a conversation,", "not a contract?"]),
              ("V", "Valuable", ["Does a user or customer", "get value from it?"]),
              ("E", "Estimable", ["Do we understand it", "well enough to size it?"]),
              ("S", "Small", ["Can we finish it in a", "few days, well within a sprint?"]),
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
        b.append(T(vx + 12, ly + 26, lab, 11, MUTED, op=".8"))
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
    b.append(bullets(x + 26, y + 106, ["Delivers value or learning by itself", "Fits comfortably in a sprint: aim for several per sprint",
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
        b.append(T(x + cw - 16, 444, "given · when · then", 9, FOREST[0], MONO, anchor="end", op=".55"))
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
        b.append(T(x + 18, y + 78, hint, 10.5, d, italic=True, op=".7"))
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
                "Plan · Value vs. Effort · Cost of Delay (CD3) · MoSCoW · Now / Next / Later Roadmap",
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
        b.append(T(qx + 16, qy + 46, sub, 10, dk, op=".75"))
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
    b.append(panel(x, y, w, h, 2, "Cost of Delay", PURPLE, "HIGHEST COST OF DELAY / SIZE GOES FIRST"))
    b.append(T(x + 18, y + 76, "Score each column 1, 2, 3, 5, 8 or 13, relative to the lowest item. CoD = value + time + risk.",
               10.5, d, italic=True, op=".75"))
    b.append(table(x + 18, y + 108, [("Item", 214), ("Value", 76), ("Time", 76), ("Risk / opp.", 92),
                                     ("CoD", 76), ("Size", 76), ("CoD / Size", 92), ("Rank", w - 36 - 702)], 5, d, 32))

    # 3 moscow
    x, y, w, h = 846, 452, 810, 296
    d = ORANGE[0]
    b.append(panel(x, y, w, h, 3, "MoSCoW", ORANGE, "FOR A FIXED DATE OR SCOPE"))
    mw = (w - 20 - 3 * 10) / 4
    for i, (name, sub, col) in enumerate([("Must", "Fails without it", RED), ("Should", "Important, not vital", ORANGE),
                                          ("Could", "Nice if there's time", AMBER), ("Won't (this time)", "Agreed out", SLATE)]):
        cx = x + 10 + i * (mw + 10)
        b.append(T(cx + 6, y + 78, name, 13, col[0], weight=600))
        b.append(T(cx + 6, y + 94, sub, 9.5, col[0], op=".7"))
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
        b.append(T(cx + rw - 14, y + 90, sub, 10, d, anchor="end", op=".7"))
        b.append(sticky_zone(cx + 8, y + 102, rw - 16, h - 166, d, chips=(YELLOW,)))
        b.append(field(cx + 14, y + h - 28, "Outcome:", cx + rw - 14, d))

    b.append(footer("What does it cost us, each week, to not have this yet?",
                    "If we could only do one thing this quarter, what would it be?", "Plan · Prioritise · Deliver Value Early"))
    write_board("prioritisation-board", "Prioritisation Board",
                "A3 landscape prioritisation board: value vs. effort grid, cost of delay table (CD3), MoSCoW columns, "
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
        b.append(T(cx + 6, y + 96, sub, 10, d, op=".7"))
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
        b.append(T(cx, y + 128, lab, 9.5, d, anchor="middle", op=".8"))
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
        b.append(T(cx + 6, y + 94, sub, 9.5, d, op=".7"))
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
        out.append(T(qx + 16, qy + 46, sub, 10, dk, op=".75"))
    out += [L(gx0, gy1, gx1, gy1, INK, 1.5), L(gx0, gy0, gx0, gy1, INK, 1.5),
            T(gx0, gy1 + 22, x_lo, 9, MUTED, MONO, ls=".12em"),
            T(gx1, gy1 + 22, x_hi, 9, MUTED, MONO, anchor="end", ls=".12em"),
            T(mx, gy1 + 22, x_name, 9, INK, MONO, weight=600, anchor="middle", ls=".12em"),
            rot_label(gx0 - 22, my, y_name)]
    return "".join(out)


def slider(x, y, w, name, color, lo="FLEX", hi="FIXED"):
    out = [T(x, y + 4, name, 12, color, weight=600),
           T(x + 120, y + 4, lo, 8.5, color, MONO, op=".6", ls=".1em"),
           T(x + w, y + 4, hi, 8.5, color, MONO, anchor="end", op=".6", ls=".1em")]
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
        out.append(T(cx + 6, y + 30, sub, 9.5, color, op=".7"))
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
               10.5, d, italic=True, op=".75"))
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
    b.append(T(x + 18, y + 134, "Anyone at 1–2? Explore, adjust the plan, re-vote.", 10, d, italic=True, op=".75"))

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
    b.append(T(x + 18, y + h - 16, "Status: agreed · at risk · blocked · done", 9, d, MONO, op=".6", ls=".08em"))

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
        out.append(T(cx + 14, y + h - 74, "Our note:", 9.5, dark, op=".6"))
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
             ("A sprint-goal item is at risk with", "days left"), ("A production incident at severity", "or higher"),
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
        b.append(T(cx + cw - 12, y + 86, hints[i], 9, d, italic=True, anchor="end", op=".55"))
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
        b.append(T(x + 24 + 150, ry, hint, 10.5, d, italic=True, op=".65"))

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
        b.append(T(cx + 130, cy, note, 10.5, d, italic=True, op=".7"))

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
        T(1356, 48, "LEVELS", 8, "#475569", MONO, ls=".14em"),
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
        b.append(T(cx + 10, gy0 + 16, f"SKILL {i + 1}", 8.5, d, MONO, op=".6", ls=".1em"))
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
        b.append(T(rx + 18, ry + 42, role, 10.5, d, op=".75"))
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
               10, d, italic=True, op=".7"))

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
    b.append(T(x + 18, y + 256, "Any “no”? Ask why again, or test another branch.", 10.5, d, italic=True, op=".75"))

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
        b.append(T(cx + gw, y + 80, hint, 10, d, italic=True, anchor="end", op=".6"))
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
        b.append(T(ox - bw / 2 + 14, oy + 40, "A customer need, pain or desire", 9.5, BLUE[0], italic=True, op=".6"))
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
               10.5, d, italic=True, op=".7"))
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
    b.append(T(x + 18, y2 + h2 - 14, "Types: desirable · viable · feasible · usable · ethical", 9, d, MONO, op=".6", ls=".06em"))

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
        b.append(T(cx, y + 98, hint, 9.5, col[0], italic=True, op=".7"))
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
    b.append(T(x + 18, y + h - 20, "Try: cycle time · defects found later · review time · rework · team confidence", 9, d, MONO, op=".6", ls=".06em"))

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
    b.append(T(x + 18, y + 330, "See the Release Forecast board for the burn-up.", 10, d, italic=True, op=".7"))

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
                b.append(T(cx + el_w / 2 - 60 + k * 30, ry + 22, str(k + 1), 10, dk, MONO, anchor="middle", op=".35"))
        b.append(R(bx + 3, ry, bar_w - 3, rh - 6, RED[1], 4, f' stroke="{RED[0]}" stroke-opacity=".2"'))
    b.append(T(gx0, y + h - 14, "Circle each score. Scores run 1 (not at all) to 5 (fully). The barrier point is the first element scored 3 or lower, "
               "working left to right. Fix it before working on later elements.", 10, SLATE[0], italic=True, op=".75"))

    y, h = 656, 240
    cw = (1632 - 4 * 12) / 5
    for i, (name, color, sub, missing, helps) in enumerate(ADKAR):
        x = 24 + i * (cw + 12)
        dk = color[0]
        b.append(panel(x, y, cw, h, name[0], name, color))
        b.append(T(x + cw - 16, y + 31, sub, 9, "white", italic=True, anchor="end", op=".75"))
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
        b.append(T(cx + 12, y + 106, sub, 9.5, d, op=".7"))
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
    b.append(T(x + 18, y + h - 20, "Is the actual mix what we intended?", 10.5, d, italic=True, op=".75"))

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
        b.append(T(cx + cw - 16, y + 94, kind, 8.5, cd, MONO, anchor="end", op=".6", ls=".12em"))
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
    b.append(T(x + 18, y + 80, "e.g. budget limits, legal and policy rules, security standards", 10.5, d, italic=True, op=".7"))
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
    b.append(T(x + 18, y + h - 18, "Re-run every 2–3 months to see the trend.", 10, d, italic=True, op=".7"))

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
    out.append(T(ax, ty, size_line, 8.5, dk, MONO, op=".7", ls=".1em"))
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
    right = "".join([T(1356, 60, "HOW TO READ IT", 8, "#475569", MONO, ls=".14em"),
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
    b.append(T(ax, y + 122, "DAYS · WITHIN YOUR SLE · ONE TEAM", 8.5, dk, MONO, op=".7", ls=".1em"))
    b.append(T(ax, y + 150, "TEMPLATE", 8.5, dk, MONO, weight=600, ls=".12em"))
    b.append(R(ax, y + 160, aw, 76, "white", 6, f' stroke="{dk}" stroke-opacity=".2"'))
    b.append(para(ax + 14, y + 182, ["As a [type of user], I want [goal]", "so that [reason]."], 14, dk, 18, font=SERIF, italic=True))
    b.append(T(ax + 14, y + 226, "+ acceptance criteria: Given · When · Then", 10, dk, op=".75"))
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


if __name__ == "__main__":
    for horizon in ("sprint", "quarter"):
        build_retros(horizon)
        build_sailboat(horizon)
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
