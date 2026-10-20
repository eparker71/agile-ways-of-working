"""Turn a generated board SVG into a plain-text spec that an AI whiteboard assistant (or a person) can follow.

The spec is read from the SVG itself, so it stays in step with the board: panels (rects drawn by panel(),
which carry filter="url(#fc)") become sections, the white text in each panel's header is its title and
note, and the text inside becomes its content. Used by build_guides.py for the "Recreate it in your
whiteboard" section of each guide.
"""
import re
from collections import Counter
from html import unescape

W, H = 1680, 1190
TOP, BOTTOM = 148, 1060

COLOURS = {"#1E3A8A": "blue", "#065F46": "emerald green", "#581C87": "purple", "#9A3412": "orange", "#991B1B": "red",
           "#92400E": "amber", "#14532D": "dark green", "#0C4A6E": "sky blue", "#334155": "slate grey", "#9D174D": "pink",
           "#0C1A2E": "navy"}
SKIP = {"Add your sticky notes here", "Stickies", "Items", "sketch", "Sticky per item", "+", "−", "›", "W", "wait", "work",
        "Initiatives", "Pink stickies", "Cleared blocker stickies", "Items, smallest on the left"}

ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')


def _attrs(tag):
    return dict(ATTR.findall(tag))


def _texts(svg):
    out = []
    for m in re.finditer(r"<text([^>]*)>(.*?)</text>", svg, re.S):
        a = _attrs(m.group(1))
        if "transform" in a:
            continue
        try:
            x, y = float(a.get("x", 0)), float(a.get("y", 0))
        except ValueError:
            continue
        t = " ".join(unescape(re.sub(r"<[^>]+>", "", m.group(2))).split())
        if t:
            out.append(dict(x=x, y=y, t=t, size=float(a.get("font-size", 11)), fill=a.get("fill", ""),
                            weight=a.get("font-weight", ""), mono="Mono" in a.get("font-family", "")))
    return out


def _panels(svg):
    out = []
    for m in re.finditer(r"<rect([^>]*)/>", svg):
        a = _attrs(m.group(1))
        if a.get("filter") != "url(#fc)":
            continue
        x, y, w, h = (float(a[k]) for k in ("x", "y", "width", "height"))
        if w > 1600 and h > 1000:
            continue
        out.append(dict(x=x, y=y, w=w, h=h, fill=a.get("stroke", a.get("fill", ""))))
    return out


def _zones(svg):
    out = []
    for m in re.finditer(r"<rect([^>]*)/>", svg):
        a = _attrs(m.group(1))
        if "stroke-dasharray" not in a or float(a.get("width", 0)) < 300 or float(a.get("height", 0)) < 150:
            continue
        out.append(dict(x=float(a["x"]), y=float(a["y"]), w=float(a["width"]), h=float(a["height"]), zone=True))
    return out


def _rows(texts):
    """Group loose text into horizontal bands separated by vertical gaps."""
    rows, cur = [], []
    for t in sorted(texts, key=lambda t: (t["y"], t["x"])):
        if cur and t["y"] - cur[-1]["y"] > 34:
            rows.append(cur)
            cur = []
        cur.append(t)
    if cur:
        rows.append(cur)
    return rows


def _where(p):
    cx, cy = (p["x"] + p["w"] / 2) / W, (p["y"] + p["h"] / 2 - TOP) / (BOTTOM - TOP)
    wf, hf = p["w"] / (W - 48), p["h"] / (BOTTOM - TOP)
    horiz = "full width" if wf > 0.9 else ("left" if cx < 0.36 else "centre" if cx < 0.64 else "right")
    vert = "top" if cy < 0.34 else "middle" if cy < 0.67 else "bottom"
    return f"{vert} {horiz}, about {round(wf * 100 / 5) * 5}% wide and {round(hf * 100 / 5) * 5}% tall"


def _colour(svg, p):
    # the panel's header strip is a path filled with the panel's dark colour, starting at the panel's top-left
    m = re.search(rf'<path d="M{p["x"]:g},{p["y"] + 52:g} [^"]*" fill="(#[0-9A-Fa-f]{{6}})"', svg)
    return COLOURS.get(m.group(1).upper() if m else "", "")


def _merge(items):
    """Join wrapped lines (same x, size and colour, next line just below) and list numbers with their text."""
    items = sorted(items, key=lambda t: (round(t["y"] / 6), t["x"]))
    out = []
    for t in items:
        t = dict(t)
        if t["mono"] and t["t"].isupper() and len(t["t"].split()) <= 4:
            t["t"] = t["t"].capitalize() + ("" if t["t"].endswith((":", "?")) else ":")
        prev = out[-1] if out else None
        if prev and re.fullmatch(r"\d+\.?", prev["t"]) and abs(prev["y"] - t["y"]) < 3 and t["x"] > prev["x"]:
            prev["t"] = f"{prev['t'].rstrip('.')}. {t['t']}"
            prev.update(x2=t["x"], numbered=True)
            continue
        if (prev and not prev.get("numbered") and not re.fullmatch(r"\d+\.?", t["t"])
                and abs(prev["x"] - t["x"]) < 2 and prev["size"] == t["size"] and prev["fill"] == t["fill"]
                and 0 < t["y"] - prev["y"] <= t["size"] * 1.6 and not prev["t"].endswith((".", "?", "!", ":", "…"))):
            prev["t"] = prev["t"] + " " + t["t"]
            prev["y"] = t["y"]
            continue
        out.append(t)
    return out


def _content(items):
    items = _merge(items)
    seen = Counter(i["t"] for i in items)
    out, done = [], set()
    for i in items:
        t = i["t"]
        if t in done:
            continue
        done.add(t)
        out.append(f"{t} (×{seen[t]})" if seen[t] > 1 else t)
    return out


def spec(svg_path, board_url=""):
    svg = open(svg_path, encoding="utf-8").read()
    texts = _texts(svg)
    title = next((t["t"] for t in texts if t["size"] >= 40), "")
    subtitle = next((t["t"] for t in texts if t["size"] == 13 and t["y"] < 140), "")
    head_right = [t for t in texts if t["x"] >= 1350 and t["y"] < 140]
    fields = [t["t"].title() for t in head_right if t["mono"] and t["t"] not in ("LEGEND", "HOW TO READ IT", "LEVELS")]
    legend = [t["t"] for t in head_right if not t["mono"]]

    panels = sorted(_panels(svg), key=lambda p: (round(p["y"] / 40), p["x"]))
    expanded = []
    for p in panels:
        has_head = any(t["fill"] == "white" and p["x"] <= t["x"] <= p["x"] + p["w"] and p["y"] <= t["y"] <= p["y"] + 46
                       for t in texts)
        zones = [z for z in _zones(svg) if p["x"] <= z["x"] and z["x"] + z["w"] <= p["x"] + p["w"] + 1
                 and p["y"] <= z["y"] and z["y"] + z["h"] <= p["y"] + p["h"] + 1]
        expanded += zones if (not has_head and zones) else [p]
    panels = sorted(expanded, key=lambda p: (round(p["y"] / 40), p["x"]))
    used = set()
    lines = []
    for n, p in enumerate(panels, 1):
        inside = [t for t in texts if p["x"] <= t["x"] <= p["x"] + p["w"] and p["y"] <= t["y"] <= p["y"] + p["h"]]
        head = [t for t in inside if t["y"] <= p["y"] + 46 and t["fill"] == "white"]
        if p.get("zone"):
            head = [t for t in inside if t["y"] <= p["y"] + 40 and (t["weight"] == "600" or t["size"] >= 16)]
        name = next((t["t"] for t in head if not t["mono"] and not t["t"].isdigit() and len(t["t"]) > 1
                     and not (p.get("zone") and t["size"] >= 16)), f"Section {n}")
        if name.isupper():
            name = name.capitalize()
        if p.get("zone"):
            q = next((t["t"] for t in head if t["size"] >= 16), "")
            note = q
            head = [t for t in head]
        if not p.get("zone"):
            note = next((t["t"] for t in head if t["mono"]), "")
        body = [t for t in inside if t not in head and t["t"] not in SKIP]
        body.sort(key=lambda t: (round(t["y"] / 6), t["x"]))
        for t in inside:
            used.add(id(t))
        colour = _colour(svg, p)
        lines.append(f"{n}. {name}: {_where(p)}" + (f"; header colour {colour}" if colour else "") + ".")
        if note:
            lines.append(f"   Subtitle: {note.capitalize()}")
        content = _content(body)
        if content:
            lines.append("   Content: " + " · ".join(content))
    # strips and other notable text outside panels (not header, not footer credit)
    extra = [t for t in texts if id(t) not in used and TOP <= t["y"] <= BOTTOM and t["t"] not in SKIP and len(t["t"]) > 2]
    footer_q = [t["t"] for t in texts if t["y"] > 1090 and t["y"] < 1120 and t["t"].startswith("“")]

    out = [f'Create an editable whiteboard for “{title}”, a workshop board.', "",
           f"Purpose: {subtitle}", "",
           "Layout: a wide landscape board (about 16:11). Make one frame per section below, placed as described. "
           "In each frame, add the section name as a heading, then its content as short text labels or empty fields to "
           "fill in. Leave space in each frame for sticky notes. Use the header colour given. Keep the wording as written "
           "and don't add extra content."]
    if fields:
        out += ["", "Header fields to fill in: " + ", ".join(fields)]
    if legend:
        out += ["Key: " + " · ".join(legend)]
    out += ["", "Sections:"] + lines
    if not panels and extra:
        out += ["Rows, top to bottom (each is a full-width band; the first label in bold is the row heading):"]
        for k, row in enumerate(_rows(extra), 1):
            label = next((t["t"] for t in row if t["weight"] == "600" and not t["mono"]), "")
            rest = " · ".join(c for c in _content(row) if c != label)
            out.append(f"{k}. " + (label + (": " + rest if rest else "") if label else rest))
    elif extra and not (len(panels) and all(p.get("zone") for p in panels) and False):
        out += ["", "Also on the board: " + " · ".join(_content(sorted(extra, key=lambda t: (round(t["y"] / 6), t["x"]))))]
    if footer_q:
        out += ["", "Footer questions: " + " ".join(footer_q)]
    if board_url:
        out += ["", f"Original board for reference: {board_url}"]
    return "\n".join(out)


if __name__ == "__main__":
    import sys
    print(spec(sys.argv[1]))
