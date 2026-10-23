#!/usr/bin/env python3
"""Generate scenarios.html, the Scenario Playbook, from the running list in _content/scenarios.md.

The Markdown file is the source: "# Area" headings, "## Scenario" headings, then optional "You'll notice:",
"First moves:" and "Longer term:" bullet lists and a "Tools:" line of tool titles. Tool titles are matched
against TOOLS in build_roles.py; an unknown title stops the build so links never break.

Run:  python3 _generator/build_scenarios.py
"""
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (where each file lives; see paths.py)
from build_roles import TOOLS, FONT_URL  # noqa: E402
from brand import ACCENT, NAVY, CREDIT  # noqa: E402

OUT = Path(__file__).resolve().parent.parent
SRC = OUT / "_content" / "scenarios.md"
REPO = "https://github.com/eparker71/better-delivery-toolkit"
BY_TITLE = {re.sub(r"\s+", " ", v[0]).lower(): k for k, v in TOOLS.items()}


def _smart(t):
    """Curly quotes, so hand-typed straight quotes match the rest of the site."""
    return re.sub(r'"([^"]+)"', "“\\1”", t)


def parse():
    text = _smart(re.sub(r"<!--.*?-->", "", SRC.read_text(encoding="utf-8"), flags=re.S))
    areas, cur_area, cur = [], None, None
    mode = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            cur_area = {"name": line[2:].strip(), "items": []}
            areas.append(cur_area)
        elif line.startswith("## "):
            cur = {"title": line[3:].strip(), "notice": "", "first": [], "later": [], "tools": []}
            cur_area["items"].append(cur)
            mode = None
        elif line.lower().startswith("you'll notice:"):
            n = line.split(":", 1)[1].strip()
            cur["notice"] = n[:1].upper() + n[1:]
        elif line.lower().startswith("first moves"):
            mode = "first"
        elif line.lower().startswith("longer term"):
            mode = "later"
        elif line.lower().startswith("tools:"):
            for name in [n.strip() for n in line.split(":", 1)[1].split(",") if n.strip()]:
                key = BY_TITLE.get(name.lower())
                if not key:
                    sys.exit(f"scenarios.md: unknown tool “{name}” in “{cur['title']}”. Use a title from TOOLS in build_roles.py.")
                cur["tools"].append(key)
        elif line.startswith("- ") and mode:
            cur[mode].append(line[2:].strip())
    return areas


def build():
    areas = parse()
    total = sum(len(a["items"]) for a in areas)
    slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    chips = '<button type="button" data-area="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-area="{slug(a["name"])}">{escape(a["name"])}</button>' for a in areas)
    sections = []
    for a in areas:
        cards = []
        for s in a["items"]:
            tools = " · ".join(f'<a href="{TOOLS[k][1]}">{escape(TOOLS[k][0])}</a>' for k in s["tools"])
            text = " ".join([s["title"], s["notice"], *s["first"], *s["later"]]).lower()
            notice = f'<p class="notice">{escape(s["notice"])}</p>' if s["notice"] else ""
            first = "".join(f"<li>{escape(x)}</li>" for x in s["first"])
            later = "".join(f"<li>{escape(x)}</li>" for x in s["later"])
            cards.append(f'<div class="sc" id="{slug(s["title"])}" data-text="{escape(text)}"><h3>{escape(s["title"])}</h3>{notice}'
                         f'<div class="cols"><div><b>First moves</b><ul>{first}</ul></div>'
                         f'<div><b>Longer term</b><ul>{later}</ul></div></div>'
                         f'<p class="see">Tools: {tools}</p></div>')
        sections.append(f'<section class="area" data-area="{slug(a["name"])}"><h2>{escape(a["name"])} <span>{len(a["items"])}</span></h2>'
                        f'<div class="grid">{"".join(cards)}</div></section>')
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scenario Playbook</title>
<link rel="stylesheet" href="{FONT_URL}">
<style>
:root{{--accent:{ACCENT};--navy:{NAVY};--ink:#1E293B;--muted:#5B6B82;--rule:#E2E8F0;}}
*{{box-sizing:border-box;}}
html,body{{margin:0;background:#F1F5F9;}}
body{{font-family:'Geist',Inter,system-ui,sans-serif;color:var(--ink);font-size:14px;line-height:1.55;}}
header{{background:var(--navy);border-top:4px solid var(--accent);color:#fff;padding:36px 16px 26px;}}
.wrap{{max-width:1040px;margin:0 auto;padding:0 16px;}}
h1{{font:400 44px/1.05 'Instrument Serif',Georgia,serif;margin:0 0 8px;}}
header p{{color:#94A3B8;margin:0 0 16px;max-width:720px;}}
header p a{{color:#FDBA74;}}
header a.back{{color:#94A3B8;font:500 11px 'Geist Mono',monospace;letter-spacing:.06em;}}
.bar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;}}
.bar button{{font:500 11px 'Geist Mono',monospace;color:#fff;background:none;border:1px solid #334155;border-radius:14px;padding:5px 11px;cursor:pointer;}}
.bar button:hover{{border-color:var(--accent);color:var(--accent);}}
.bar button[aria-pressed="true"]{{background:#C2410C;border-color:#C2410C;}}
.top{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px;}}
input{{font:14px 'Geist',system-ui,sans-serif;padding:8px 12px;border-radius:6px;border:1px solid #334155;background:#0F2236;color:#fff;width:100%;max-width:360px;}}
input::placeholder{{color:#64748B;}}
a.suggest{{font:500 12px 'Geist',system-ui,sans-serif;color:#fff;background:#C2410C;border-radius:6px;padding:8px 12px;text-decoration:none;}}
main{{padding:16px 0 48px;}}
h2{{font:500 11px 'Geist Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:26px 0 10px;}}
h2 span{{color:#5B6B82;margin-left:6px;}}
.grid{{display:grid;grid-template-columns:1fr;gap:12px;}}
.sc{{background:#fff;border:1px solid var(--rule);border-left:4px solid var(--accent);border-radius:8px;padding:14px 18px;scroll-margin-top:12px;}}
.sc:target{{box-shadow:0 0 0 3px rgba(235,108,54,.35);}}
.sc h3{{margin:0 0 4px;font-size:16px;}}
.sc .notice{{margin:0 0 8px;color:var(--muted);font-style:italic;font-size:13px;}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
.cols b{{font:600 9px 'Geist Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#9A3412;}}
.cols div:last-child b{{color:#065F46;}}
.cols ul{{margin:4px 0 0;padding-left:18px;font-size:13px;}}
.cols li{{margin:2px 0;}}
.see{{font-size:12px;color:var(--muted);margin:10px 0 0;}}
.see a{{color:var(--ink);}}
.see a:hover{{color:var(--accent);}}
.more{{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:16px 18px;margin-top:28px;font-size:13px;}}
.more h3{{margin:0 0 6px;font-size:15px;}}
.more a{{color:#9A3412;}}
code{{font:12px 'Geist Mono',monospace;background:#F1F5F9;border-radius:4px;padding:1px 5px;}}
.hidden{{display:none !important;}}
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#5B6B82;text-align:center;padding:0 16px 32px;}}
@media (max-width:640px){{.cols{{grid-template-columns:1fr;}}}}
@media print{{header{{padding:16px;}} .top,.bar{{display:none;}} .sc{{break-inside:avoid;}}}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="index.html">← All tools</a>
  <h1>Scenario Playbook</h1>
  <p>A running list of {total} common situations, each with first moves, longer-term fixes and the tools that help. For recurring habits rather than one-off situations, see the <a href="anti-patterns.html">Anti-Pattern Catalogue</a>.</p>
  <div class="top"><input type="search" placeholder="Search, e.g. “deadline” or “new team”…" aria-label="Search scenarios">
  <a class="suggest" href="{REPO}/issues/new?template=scenario.yml">Suggest a scenario</a></div>
  <div class="bar">{chips}</div>
</div></header>
<main><div class="wrap">
{chr(10).join(sections)}
<div class="more"><h3>Add to the list</h3><p>This is a running list. To suggest a scenario, <a href="{REPO}/issues/new?template=scenario.yml">open a suggestion on GitHub</a>. To add one to your own copy, edit <code>_content/scenarios.md</code> and run <code>python3 _generator/build_scenarios.py</code>; the format is explained at the top of the file.</p></div>
</div></main>
<footer>{escape(CREDIT)}</footer>
<script>
(function(){{
  var input=document.querySelector('input'), buttons=document.querySelectorAll('.bar button'), area='all';
  function apply(){{
    var q=input.value.trim().toLowerCase();
    buttons.forEach(function(b){{b.setAttribute('aria-pressed', String(b.dataset.area===area));}});
    document.querySelectorAll('.area').forEach(function(sec){{
      var any=false;
      sec.querySelectorAll('.sc').forEach(function(c){{
        var ok=(area==='all'||sec.dataset.area===area) && (!q || c.dataset.text.indexOf(q)>=0);
        c.classList.toggle('hidden', !ok); if(ok) any=true;
      }});
      sec.classList.toggle('hidden', !any);
    }});
  }}
  input.addEventListener('input', apply);
  buttons.forEach(function(b){{b.addEventListener('click', function(){{area=b.dataset.area; apply();}});}});
}})();
</script>
</body>
</html>
"""
    paths.write_page("scenarios.html", page)
    print(f"wrote scenarios.html ({total} scenarios in {len(areas)} areas)")


if __name__ == "__main__":
    build()
