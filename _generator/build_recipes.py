#!/usr/bin/env python3
"""Generate workshop-recipes.html: ready-made agendas that combine tools, plus the worked examples.

The source is _content/recipes.md (the format is explained at the top of that file). Tool titles are matched
against TOOLS in build_roles.py; an unknown title stops the build so links never break.

Run:  python3 _generator/build_recipes.py   (after build_boards.py, which makes the worked examples)
"""
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_roles import TOOLS, FONT_URL  # noqa: E402
from build_scenarios import _smart  # noqa: E402
from brand import ACCENT, NAVY, CREDIT  # noqa: E402

OUT = Path(__file__).resolve().parent.parent
SRC = OUT / "_content" / "recipes.md"
BY_TITLE = {re.sub(r"\s+", " ", v[0]).lower(): k for k, v in TOOLS.items()}
EXAMPLES = [("team-charter", "Team Charter", "A new team's purpose, values, agreements and Definitions of Ready and Done."),
            ("sprint-planning", "Sprint Planning", "A sprint goal, capacity, selected items, a dependency risk and a confidence vote."),
            ("prioritisation", "Prioritisation Board", "Value vs. effort, a cost-of-delay table, MoSCoW and a Now · Next · Later roadmap."),
            ("retro", "Start · Stop · Continue", "Stickies with dot votes, and three actions with owners and a done-when.")]


# Starter kits: the minimum toolset for each project size (see the Right-Size Your Structure poster).
# Each entry: (tool key from TOOLS, why it's in the kit). "start" items come first, in order; "grow" items when needed.
STARTER_KITS = [
    ("One team", "3–10 people", "#065F46",
     [("team-charter", "agree purpose, roles and how you'll work"), ("prioritisation", "decide what comes first"),
      ("kanban", "one visible board for all the work"), ("sprint-planning", "plan each iteration around a goal"),
      ("retro", "improve a little every few weeks")],
     [("premortem", "if the work is risky"), ("stakeholder", "if many people care about the result"),
      ("forecast", "when someone asks “when?”")]),
    ("Team of teams", "10–50 people · 2–5 teams", "#1E3A8A",
     [("right-size", "check you have enough structure, and not too much"), ("ctp", "plan together each planning period"),
      ("dependency", "see who needs what from whom"), ("sync", "a short weekly cross-team check-in"),
      ("raid", "one shared list of risks, assumptions, issues and dependencies"), ("status", "a one-page update for sponsors")],
     [("raci", "when decisions get lost or contested"), ("cross-retro", "when the same cross-team problems repeat"),
      ("release", "for coordinated releases")]),
    ("Programme", "50+ people · many teams", "#581C87",
     [("right-size", "set the level of governance on purpose"), ("okr", "outcomes everyone works toward"),
      ("portfolio-kanban", "decide what to fund and limit work in progress"), ("topology", "organise teams around the work"),
      ("value", "show whether the investment is paying off"), ("delegation", "push decisions to the right level")],
     [("adkar", "when the programme changes how people work"), ("vsm", "to find delays across the whole system"),
      ("sdlc", "to replace document gates with evidence")]),
]


def kits_html():
    out = []
    for name, size, colour, start, grow in STARTER_KITS:
        def item(k, why):
            if k not in TOOLS:
                sys.exit(f"STARTER_KITS: unknown tool key “{k}”")
            title, board, guide, _ = TOOLS[k]
            return f'<li><a href="{board}">{escape(title)}</a> <span>{escape(why)}</span></li>'
        out.append(f'<div class="kit" style="--k:{colour}"><h3>{escape(name)}</h3><p class="size">{escape(size)}</p>'
                   f'<b>Start with</b><ol>{"".join(item(k, w) for k, w in start)}</ol>'
                   f'<b>Add as you grow</b><ul>{"".join(item(k, w) for k, w in grow)}</ul></div>')
    return "".join(out)


def minutes(t):
    m = re.match(r"(\d+)\s*min", t)
    if not m:
        sys.exit(f"recipes.md: step length “{t}” should look like “30 min”")
    return int(m.group(1))


def parse():
    text = _smart(re.sub(r"<!--.*?-->", "", SRC.read_text(encoding="utf-8"), flags=re.S))
    areas, area, cur, mode = [], None, None, None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            area = {"name": line[2:].strip(), "items": []}
            areas.append(area)
        elif line.startswith("## "):
            cur = {"title": line[3:].strip(), "for": "", "time": "", "outcome": "", "before": [], "agenda": [], "after": []}
            area["items"].append(cur)
            mode = None
        elif re.match(r"(for|time|outcome):", line, re.I):
            k, v = line.split(":", 1)
            cur[k.lower()] = v.strip()
        elif re.match(r"(before|agenda|after):$", line, re.I):
            mode = line[:-1].lower()
        elif line.startswith("- ") and mode == "agenda":
            parts = [x.strip() for x in line[2:].split("|", 2)]
            if len(parts) != 3:
                sys.exit(f"recipes.md: agenda step “{line}” in “{cur['title']}” needs three parts: length | tool | what happens")
            length, tool, what = parts
            key = None
            if tool != "-":
                key = BY_TITLE.get(tool.lower())
                if not key:
                    sys.exit(f"recipes.md: unknown tool “{tool}” in “{cur['title']}”. Use a title from TOOLS in build_roles.py.")
            cur["agenda"].append((minutes(length), key, what))
        elif line.startswith("- ") and mode:
            cur[mode].append(line[2:].strip())
    return areas


def clock(m):
    return f"{m // 60}:{m % 60:02d}"


def card(r, slug):
    rows, t = [], 0
    for mins, key, what in r["agenda"]:
        if key:
            title, board, guide, _ = TOOLS[key]
            tool = f'<a href="{board}">{escape(title)}</a>' + (f' <a class="g" href="{guide}">guide</a>' if guide else "")
        else:
            tool = '<span class="none">—</span>'
        rows.append(f'<tr{"" if key else " class=\"brk\""}><td class="t">{clock(t)}</td><td class="m">{mins} min</td>'
                    f'<td class="tool">{tool}</td><td>{escape(what)}</td></tr>')
        t += mins
    lst = lambda xs: "".join(f"<li>{escape(x)}</li>" for x in xs)
    tools = sorted({TOOLS[k][0] for _, k, _ in r["agenda"] if k})
    return (f'<article class="rc" id="{slug(r["title"])}"><h3>{escape(r["title"])}</h3>'
            f'<dl><div><dt>For</dt><dd>{escape(r["for"])}</dd></div>'
            f'<div><dt>Time</dt><dd>{escape(r["time"])}</dd></div>'
            f'<div><dt>Outcome</dt><dd>{escape(r["outcome"])}</dd></div></dl>'
            f'<div class="cols"><div><b>Before</b><ul>{lst(r["before"])}</ul></div>'
            f'<div><b>After</b><ul>{lst(r["after"])}</ul></div></div>'
            f'<table><thead><tr><th>Start</th><th>Length</th><th>Tool</th><th>What happens</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>'
            f'<p class="uses">Uses {len(tools)} tools: {escape(", ".join(tools))}.</p></article>')


def build():
    areas = parse()
    total = sum(len(a["items"]) for a in areas)
    slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    toc = "".join(f'<div><b>{escape(a["name"])}</b>' + "".join(
        f'<a href="#{slug(r["title"])}">{escape(r["title"])} <span>{escape(re.split(r" \(|,", r["time"])[0])}</span></a>'
        for r in a["items"]) + "</div>" for a in areas)
    sections = "\n".join(f'<section><h2>{escape(a["name"])}</h2>' + "".join(card(r, slug) for r in a["items"]) + "</section>"
                         for a in areas)
    ex = []
    for key, title, desc in EXAMPLES:
        board, guide = TOOLS[key][1], TOOLS[key][2]
        if not (OUT / f"worked-example-{board}").exists():
            sys.exit(f"missing worked-example-{board}: run build_boards.py first")
        ex.append(f'<a class="ex" href="worked-example-{board}"><img src="worked-example-{board.replace(".html", ".svg")}" alt="" loading="lazy">'
                  f'<b>{escape(title)}</b><span>{escape(desc)}</span></a>')
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Workshop Recipes & Worked Examples</title>
<link rel="stylesheet" href="{FONT_URL}">
<style>
:root{{--accent:{ACCENT};--navy:{NAVY};--ink:#1E293B;--muted:#64748B;--rule:#E2E8F0;}}
*{{box-sizing:border-box;}}
html,body{{margin:0;background:#F1F5F9;}}
body{{font-family:'Geist',Inter,system-ui,sans-serif;color:var(--ink);font-size:14px;line-height:1.55;}}
header{{background:var(--navy);border-top:4px solid var(--accent);color:#fff;padding:36px 16px 26px;}}
.wrap{{max-width:1040px;margin:0 auto;padding:0 16px;}}
h1{{font:400 44px/1.05 'Instrument Serif',Georgia,serif;margin:0 0 8px;}}
header p{{color:#94A3B8;margin:0 0 18px;max-width:720px;}}
header a.back{{color:#94A3B8;font:500 11px 'Geist Mono',monospace;letter-spacing:.06em;}}
.toc{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;}}
.toc b{{display:block;font:600 9px 'Geist Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin-bottom:6px;}}
.toc a{{display:block;color:#fff;text-decoration:none;font-size:13px;margin:0 0 6px;}}
.toc a:hover{{color:var(--accent);}}
.toc a span{{color:#64748B;font-size:11.5px;}}
main{{padding:8px 0 48px;}}
h2{{font:500 11px 'Geist Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:28px 0 10px;}}
.exs{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}}
.ex{{background:#fff;border:1px solid var(--rule);border-radius:8px;overflow:hidden;text-decoration:none;color:var(--ink);display:flex;flex-direction:column;}}
.ex:hover{{border-color:var(--accent);}}
.ex img{{width:100%;aspect-ratio:1680/1190;object-fit:cover;border-bottom:1px solid var(--rule);background:#E2E8F0;}}
.ex b{{padding:10px 12px 0;font-size:14px;}}
.ex span{{padding:2px 12px 12px;color:var(--muted);font-size:12.5px;}}
.intro{{color:var(--muted);margin:0 0 12px;max-width:760px;}}
.intro a{{color:#9A3412;}}
.kits{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}}
.kit{{background:#fff;border:1px solid var(--rule);border-top:4px solid var(--k);border-radius:8px;padding:14px 18px;}}
.kit h3{{margin:0;font:400 24px/1.1 'Instrument Serif',Georgia,serif;}}
.kit .size{{margin:2px 0 10px;color:var(--muted);font:500 11px 'Geist Mono',monospace;}}
.kit b{{display:block;font:600 9px 'Geist Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--k);margin-top:8px;}}
.kit ol,.kit ul{{margin:4px 0 0;padding-left:20px;font-size:13px;}}
.kit li{{margin:4px 0;}}
.kit li a{{color:var(--ink);font-weight:500;}}
.kit li span{{display:block;color:var(--muted);font-size:12px;}}
.rc{{background:#fff;border:1px solid var(--rule);border-left:4px solid var(--accent);border-radius:8px;padding:16px 20px;margin:0 0 14px;scroll-margin-top:12px;}}
.rc:target{{box-shadow:0 0 0 3px rgba(235,108,54,.35);}}
.rc h3{{margin:0 0 8px;font:400 26px/1.1 'Instrument Serif',Georgia,serif;}}
dl{{margin:0 0 10px;display:grid;gap:3px;}}
dl div{{display:grid;grid-template-columns:80px 1fr;}}
dt{{font:600 9px/2.2 'Geist Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#9A3412;}}
dd{{margin:0;}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:10px;}}
.cols b{{font:600 9px 'Geist Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#065F46;}}
.cols ul{{margin:4px 0 0;padding-left:18px;font-size:13px;}}
table{{width:100%;border-collapse:collapse;font-size:13px;table-layout:fixed;}}
th:nth-child(1){{width:56px;}} th:nth-child(2){{width:72px;}} th:nth-child(3){{width:30%;}}
th{{text-align:left;font:600 9px 'Geist Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--rule);padding:6px 8px;}}
td{{border-bottom:1px solid #F1F5F9;padding:6px 8px;vertical-align:top;}}
td.t,td.m{{font:500 12px 'Geist Mono',monospace;color:var(--muted);white-space:nowrap;}}
td.tool{{width:30%;}}
td.tool a{{color:var(--ink);font-weight:500;}}
td.tool a.g{{font:500 10px 'Geist Mono',monospace;color:#9A3412;font-weight:400;margin-left:4px;}}
tr.brk td{{color:var(--muted);background:#F8FAFC;}}
.none{{color:#CBD5E1;}}
.uses{{font-size:12px;color:var(--muted);margin:10px 0 0;}}
.more{{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:16px 18px;margin-top:28px;font-size:13px;}}
.more h3{{margin:0 0 6px;font-size:15px;}}
code{{font:12px 'Geist Mono',monospace;background:#F1F5F9;border-radius:4px;padding:1px 5px;}}
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#94A3B8;text-align:center;padding:0 16px 32px;}}
@media (max-width:820px){{.toc,.exs{{grid-template-columns:1fr 1fr;}} .kits{{grid-template-columns:1fr;}}}}
@media (max-width:560px){{.toc,.exs,.cols{{grid-template-columns:1fr;}} td.t{{display:none;}} dl div{{grid-template-columns:1fr;}}}}
@media print{{header{{padding:16px;}} .toc,.exs,#examples-h,.intro.ex-intro{{display:none;}} .rc{{break-inside:avoid;}}}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="index.html">← All tools</a>
  <h1>Workshop Recipes</h1>
  <p>{total} ready-made agendas that combine tools from the toolkit, with timings, preparation and follow-up. Use them as they are, or as a starting point. Below them are <a href="#starter-kits" style="color:#FDBA74">starter kits</a> for each size of project, and worked examples: real boards filled in for a fictional team.</p>
  <nav class="toc">{toc}</nav>
</div></header>
<main><div class="wrap">
{sections}
<h2 id="starter-kits">Starter kits by project size</h2>
<p class="intro">The minimum set of tools for each size of project, in the order to use them. A four-person project needs far less structure than a forty-person one; see <a href="right-size-poster.html">Right-Size Your Structure</a> for why, and for when to turn the dial up.</p>
<div class="kits">{kits_html()}</div>
<h2 id="examples">Worked examples</h2>
<p class="intro ex-intro">What a finished board can look like, filled in by the “Basket team”, a fictional team at an online grocery service (the same example as the <a href="backlog-anatomy-poster.html">Backlog Item Anatomy</a> poster). Each one has a link back to the blank board.</p>
<div class="exs">{"".join(ex)}</div>
<div class="more"><h3>Add a recipe</h3><p>To add one to your own copy, edit <code>_content/recipes.md</code> and run <code>python3 _generator/build_recipes.py</code>; the format is explained at the top of the file.</p></div>
</div></main>
<footer>{escape(CREDIT)}</footer>
</body>
</html>
"""
    (OUT / "workshop-recipes.html").write_text(page, encoding="utf-8")
    print(f"wrote workshop-recipes.html ({total} recipes in {len(areas)} areas)")


if __name__ == "__main__":
    build()
