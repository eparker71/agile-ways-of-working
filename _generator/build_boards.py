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

SANS = "'Geist',Inter,system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',Consolas,monospace"
FONT_URL = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
            "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")

ACCENT = "#eb6c36"
NAVY = "#0C1A2E"
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

FOOT_TAG = "Agile Release Train · Systems-Thinking · Continuous Improvement · POM 2.0"


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
        R(1448, 14, 208, 22, ACCENT, 11, ' fill-opacity=".18"'),
        T(1552, 29, "PRODUCT OPERATING MODEL 2.0", 8.5, ACCENT, MONO, anchor="middle", ls=".10em"),
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
    ])


# ---------------------------------------------------------------- output

def guide_for(slug):
    """Facilitator guide that documents a board slug."""
    m = re.match(r"retro-board-(.+)-(sprint|quarter)$", slug)
    if m:
        return f"facilitator-guide-retro-{m.group(1)}.html"
    return f"facilitator-guide-{slug.removesuffix('-board').removesuffix('-poster')}.html"


GUIDE_LINK_CSS = ("a.guide{position:fixed;right:16px;bottom:16px;font:500 12px 'Geist',system-ui,sans-serif;color:#fff;"
                  "background:#0C1A2E;border-left:4px solid #eb6c36;padding:9px 14px;border-radius:6px;text-decoration:none;"
                  "box-shadow:0 6px 20px rgba(0,0,0,.25);}\na.guide:hover{background:#eb6c36;}")


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
RETRO_TAG = "Retrospective Kit · Team Reflection · Continuous Improvement · POM 2.0"


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
        T(1656, 1138, "Vote with coloured dots · Repeat each PI to see trends · Feed red/amber areas into the 1% Experiment Canvas",
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
    for i, lab in enumerate(["1 sprint", "2 sprints", "1 quarter / PI"]):
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
                    "Lean Coffee · Participant-Driven Meetings · Facilitation Toolkit · POM 2.0"))
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


BREAKDOWN_TAG = "Break Down Work · Vertical Slicing · Deliver Value Early · POM 2.0"


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
                    "INVEST (Bill Wake) · SPIDR (Mike Cohn) · Splitting Patterns (Richard Lawrence) · POM 2.0"))
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
