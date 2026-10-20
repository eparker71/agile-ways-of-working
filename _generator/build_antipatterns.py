#!/usr/bin/env python3
"""Generate anti-patterns.html: a searchable catalogue of common anti-patterns, each with why it hurts, what to try
and the toolkit tool that helps.

ANTIPATTERNS below is the content: (area, symptom, short label for the Spotter board, why it hurts, try this, [tool keys]).
Tool keys come from TOOLS in build_roles.py. build_boards.py reads the same list for the Anti-Pattern Spotter board.

Run:  python3 _generator/build_antipatterns.py
"""
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_roles import TOOLS, FONT_URL  # noqa: E402
from brand import ACCENT, NAVY, CREDIT  # noqa: E402

OUT = Path(__file__).resolve().parent.parent

AREAS = [("events", "Events"), ("backlog", "Backlog"), ("flow", "Flow"), ("teams", "Teams & roles"),
         ("scaling", "Multi-team"), ("leadership", "Leadership"), ("metrics", "Metrics & reporting")]

ANTIPATTERNS = [
    # events
    ("events", "The daily sync is a status report to the manager", "Daily sync is a status report",
     "People talk to one person instead of planning together, so the team stops owning the day.",
     "Walk the board, not the people. Rotate the facilitator, and ask managers to listen rather than lead.", ["daily"]),
    ("events", "The same issues come up at every retrospective", "Same issues at every retro",
     "Nothing changes, so people stop raising problems at all.",
     "Limit actions to one to three, each with an owner. Start each retro by reviewing the last actions, and dig into causes.",
     ["retro", "rootcause"]),
    ("events", "The review is a one-way demo with no feedback", "Review is a one-way demo",
     "Stakeholders watch politely, the backlog doesn't change, and the team learns nothing.",
     "Let stakeholders use the product. End by showing what changed in the backlog because of their feedback.",
     ["sprint-review"]),
    ("events", "Planning is just dragging tickets into the iteration", "Planning has no goal",
     "Without a goal there's no way to make sensible trade-offs when plans change.",
     "Agree the goal first, then select work that fits real capacity.", ["sprint-planning"]),
    ("events", "Meetings overrun and nobody is sure why they exist", "Meetings have no clear purpose",
     "Time and energy drain away from the work itself.",
     "Give every event a purpose, an output and a timebox. Merge or drop the ones without them.", ["events", "facilitation"]),
    ("events", "Refinement happens during planning", "Refinement happens in planning",
     "Planning turns into long design debates, and work starts late or unclear.",
     "Hold a short weekly refinement and refine one or two iterations ahead.", ["refinement", "example"]),
    # backlog
    ("backlog", "Stories are technical tasks, such as “set up the database”", "Stories are technical tasks",
     "Nothing is usable until every layer is done, so value and feedback arrive late.",
     "Slice vertically, through every layer, so each story is something a user can use.", ["splitting", "backlog"]),
    ("backlog", "Epics have no outcome or measure", "Epics have no outcome",
     "Nobody can tell whether the epic worked, or when to stop investing in it.",
     "Write each epic as a hypothesis with a measurable outcome.", ["epic", "backlog"]),
    ("backlog", "The backlog has hundreds of items, some years old", "Backlog graveyard",
     "It's impossible to see what matters, and refinement effort is wasted.",
     "Archive anything untouched for six months, and keep a short, ordered top of the backlog.", ["prioritisation"]),
    ("backlog", "Everything is a must-have or top priority", "Everything is top priority",
     "Priorities stop meaning anything, and teams spread themselves thin.",
     "Rank by cost of delay, and protect a genuine “could have” list.", ["prioritisation"]),
    ("backlog", "Stories carry over from one iteration to the next", "Stories keep carrying over",
     "Items are too big or unclear, and forecasts keep slipping.",
     "Split items smaller, and check each is understood with Example Mapping before starting.",
     ["splitting", "example", "ageing"]),
    ("backlog", "Acceptance criteria are written after the work", "Criteria written after the work",
     "Developers and testers disagree about what done means, so rework follows.",
     "Agree rules and examples together before work starts.", ["example"]),
    # flow
    ("flow", "Everyone has several things in progress at once", "Too much work in progress",
     "Work waits between people and nothing finishes.",
     "Set WIP limits, and stop starting so you can start finishing.", ["kanban", "buffer"]),
    ("flow", "Work sits blocked for days without anyone noticing", "Blocked work goes unnoticed",
     "Ageing items quietly become late items.",
     "Show age on every card, review the oldest items daily, and swarm on anything past your SLE.",
     ["ageing", "buffer", "blockers"]),
    ("flow", "“Done” means “development done”", "“Done” means dev done",
     "Hidden work piles up in testing and release, and delivery surprises everyone.",
     "Strengthen the Definition of Done, and make waiting steps visible on the board.", ["team-charter", "kanban"]),
    ("flow", "Unplanned work wrecks every plan", "Unplanned work wrecks plans",
     "The team keeps missing what it planned, and trust erodes.",
     "Measure how much unplanned work arrives, and plan a buffer for it.", ["buffer"]),
    ("flow", "One person is the only one who can do a key task", "Single point of failure",
     "Work queues for them, and a holiday or illness stops delivery.",
     "Pair to spread the skill, and check the bus factor with a skills matrix.", ["skills", "pairing"]),
    ("flow", "The same blockers keep coming back", "Recurring blockers",
     "Teams fix symptoms one at a time while the cause stays.",
     "Log blockers for a few weeks, cluster them, and fix the biggest cluster.", ["blockers", "rootcause"]),
    # teams & roles
    ("teams", "The product owner is rarely available", "Product owner unavailable",
     "Questions wait, the team guesses, and the wrong things get built.",
     "Agree regular PO time, and make the cost of waiting visible.", ["team-charter", "raci"]),
    ("teams", "The Scrum Master has become the team's secretary", "SM is the team's secretary",
     "Coaching stops, and the team stops owning its own process.",
     "Hand the tools back to the team and rotate facilitation.", ["sm-cheat", "facilitation"]),
    ("teams", "Nobody is sure who makes which decisions", "Unclear decision rights",
     "Decisions stall, or get made twice by different people.",
     "Make decision rights explicit, area by area.", ["delegation", "raci"]),
    ("teams", "Quiet people rarely speak in meetings", "Quiet voices go unheard",
     "Ideas and risks go unheard until it's too late.",
     "Use silent writing and round-robins, and check psychological safety.", ["facilitation", "psych-safety"]),
    ("teams", "The team avoids open disagreement", "Conflict is avoided",
     "Problems are discussed in corridors instead of in the room, and decisions don't stick.",
     "Agree how the team handles disagreement, and use an agreement scale to surface real views.",
     ["team-charter", "psych-safety"]),
    ("teams", "A new team starts work without agreeing how to work", "No agreed ways of working",
     "Friction surfaces later, under delivery pressure, when it's harder to fix.",
     "Run a short, timeboxed team launch and write a team charter.", ["launch", "team-charter"]),
    # scaling
    ("scaling", "Teams are constantly waiting on each other", "Teams wait on each other",
     "Lead times grow and plans slip together.",
     "Make dependencies visible, then remove them by changing team boundaries or skills.", ["dependency", "topology"]),
    ("scaling", "The cross-team sync is a status meeting", "Cross-team sync is status",
     "Real blockers between teams don't get solved.",
     "Focus the sync on dependencies and blockers, and give each impediment an owner.", ["sync"]),
    ("scaling", "Multi-team planning is a top-down announcement", "Top-down big-room planning",
     "Teams don't believe the plan, so it isn't really a plan.",
     "Let teams plan their own work against shared objectives, and take a confidence vote.", ["ctp"]),
    ("scaling", "One team owns far too much", "One team owns too much",
     "Quality and speed drop, and people burn out.",
     "Check cognitive load, then split the team's responsibilities or add a platform.", ["topology"]),
    ("scaling", "Problems between teams never get fixed", "Cross-team problems persist",
     "The same issues repeat every planning period.",
     "Hold a cross-team retrospective and solve one system problem together.", ["cross-retro"]),
    ("scaling", "Teams' velocity is compared", "Teams compared on velocity",
     "Points inflate, numbers lose meaning, and trust drops.",
     "Never compare teams' points. Use flow and outcome measures instead.", ["estimation", "delivery-metrics"]),
    # leadership
    ("leadership", "Far too many initiatives are in flight", "Too many initiatives",
     "Everything moves slowly and nothing finishes.",
     "Limit portfolio WIP. Stop something to start something.", ["portfolio-kanban"]),
    ("leadership", "Change is announced and expected to stick", "Change announced, not led",
     "People comply on the surface, then drift back to the old way.",
     "Find each group's barrier point and work on that first.", ["adkar"]),
    ("leadership", "Funding is decided once a year", "Annual funding only",
     "Teams can't adapt to what they learn during the year.",
     "Fund MVPs first, and review the portfolio regularly with evidence.", ["portfolio-kanban", "value"]),
    ("leadership", "Agile is mandated as a process rather than a goal", "Agile as a mandate",
     "Teams go through the motions without the benefits.",
     "Agree the outcomes you want, and let teams choose the practices that get them there.", ["value", "events"]),
    ("leadership", "Bad news travels slowly upwards", "Bad news travels slowly",
     "Problems surface too late to fix cheaply.",
     "Report confidence and trends, and thank people who bring bad news early.", ["status", "psych-safety"]),
    ("leadership", "Roadmaps are lists of features with dates", "Feature-and-date roadmaps",
     "Teams build what was promised, not what turns out to be valuable.",
     "Make roadmaps about outcomes: Now, Next and Later.", ["prioritisation", "okr"]),
    # metrics
    ("metrics", "Velocity is used as a target", "Velocity as a target",
     "Points inflate and the numbers stop meaning anything.",
     "Use velocity only for the team's own forecasting, or count items instead.", ["estimation", "forecast"]),
    ("metrics", "Single delivery dates are promised", "Single-date promises",
     "Dates slip and trust erodes each time.",
     "Forecast with ranges based on real throughput.", ["forecast"]),
    ("metrics", "Status is green until it's suddenly red", "Green until suddenly red",
     "Problems are hidden until it's too late to act.",
     "Report outcomes, a confidence rating and its trend, instead of traffic lights.", ["status"]),
    ("metrics", "People are measured by tickets closed", "Individuals measured by tickets",
     "People game the numbers and collaborate less.",
     "Measure team outcomes and flow, never individuals.", ["value", "delivery-metrics"]),
    ("metrics", "OKRs are task lists", "OKRs are task lists",
     "Effort gets measured instead of results.",
     "Write key results as measurable outcomes.", ["okr"]),
    ("metrics", "Delivery gets faster while quality drops", "Faster, but less stable",
     "Incidents and rework grow, and the speed doesn't last.",
     "Balance speed metrics with stability ones, and learn from every incident.", ["delivery-metrics", "incident"]),
]

for _a, _s, short, _w, _t, keys in ANTIPATTERNS:
    assert len(short) <= 34, short
    for k in keys:
        assert k in TOOLS, f"{_s}: unknown tool {k}"


def build():
    chips = '<button type="button" data-area="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-area="{aid}">{escape(name)}</button>' for aid, name in AREAS)
    sections = []
    for aid, name in AREAS:
        items = [a for a in ANTIPATTERNS if a[0] == aid]
        cards = []
        for _a, symptom, _short, why, try_, keys in items:
            links = " · ".join(f'<a href="{TOOLS[k][1]}">{escape(TOOLS[k][0])}</a>' for k in keys)
            text = (symptom + " " + why + " " + try_).lower()
            cards.append(f'<div class="ap" data-text="{escape(text)}"><h3>{escape(symptom)}</h3>'
                         f'<p class="why"><b>Why it hurts:</b> {escape(why)}</p>'
                         f'<p class="try"><b>Try this:</b> {escape(try_)}</p>'
                         f'<p class="see">Tools: {links}</p></div>')
        sections.append(f'<section class="area" data-area="{aid}"><h2>{escape(name)} <span>{len(items)}</span></h2>'
                        f'<div class="grid">{"".join(cards)}</div></section>')
    pitfalls = " · ".join(f'<a href="{g}">{escape(t)}</a>' for t, b, g, _ in sorted(TOOLS.values()) if g)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anti-Pattern Catalogue</title>
<link rel="stylesheet" href="{FONT_URL}">
<style>
:root{{--accent:{ACCENT};--navy:{NAVY};--ink:#1E293B;--muted:#64748B;--rule:#E2E8F0;}}
*{{box-sizing:border-box;}}
html,body{{margin:0;background:#F1F5F9;}}
body{{font-family:'Geist',Inter,system-ui,sans-serif;color:var(--ink);font-size:14px;line-height:1.55;}}
header{{background:var(--navy);border-top:4px solid var(--accent);color:#fff;padding:36px 16px 26px;}}
.wrap{{max-width:1040px;margin:0 auto;padding:0 16px;}}
h1{{font:400 44px/1.05 'Instrument Serif',Georgia,serif;margin:0 0 8px;}}
header p{{color:#94A3B8;margin:0 0 16px;max-width:700px;}}
header p a{{color:#FDBA74;}}
header a.back{{color:#94A3B8;font:500 11px 'Geist Mono',monospace;letter-spacing:.06em;}}
.bar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;}}
.bar button{{font:500 11px 'Geist Mono',monospace;color:#fff;background:none;border:1px solid #334155;border-radius:14px;padding:5px 11px;cursor:pointer;}}
.bar button:hover{{border-color:var(--accent);color:var(--accent);}}
.bar button[aria-pressed="true"]{{background:var(--accent);border-color:var(--accent);}}
input{{font:14px 'Geist',system-ui,sans-serif;padding:8px 12px;border-radius:6px;border:1px solid #334155;background:#0F2236;color:#fff;width:100%;max-width:360px;margin-bottom:12px;}}
input::placeholder{{color:#64748B;}}
main{{padding:16px 0 48px;}}
h2{{font:500 11px 'Geist Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:26px 0 10px;}}
h2 span{{color:#94A3B8;margin-left:6px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:12px;}}
.ap{{background:#fff;border:1px solid var(--rule);border-top:4px solid #991B1B;border-radius:8px;padding:14px 16px;}}
.ap h3{{margin:0 0 8px;font-size:15px;line-height:1.35;}}
.ap p{{margin:0 0 6px;font-size:13px;}}
.ap .why{{color:var(--muted);}}
.ap .try b{{color:#065F46;}}
.ap .see{{font-size:12px;color:var(--muted);margin-top:8px;}}
.ap .see a{{color:var(--ink);}}
.ap .see a:hover{{color:var(--accent);}}
.more{{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:16px 18px;margin-top:28px;font-size:13px;}}
.more h3{{margin:0 0 6px;font-size:15px;}}
.more a{{color:#9A3412;}}
.hidden{{display:none !important;}}
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#94A3B8;text-align:center;padding:0 16px 32px;}}
@media print{{header{{padding:16px;}} input,.bar{{display:none;}} .ap{{break-inside:avoid;}}}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="index.html">← All tools</a>
  <h1>Anti-Pattern Catalogue</h1>
  <p>{len(ANTIPATTERNS)} common anti-patterns, each with why it hurts, what to try, and the tool that helps. Start from a symptom you recognise. To find them with your team, use the <a href="anti-pattern-spotter-board.html">Anti-Pattern Spotter board</a>.</p>
  <input type="search" placeholder="Search symptoms, e.g. “retro” or “blocked”…" aria-label="Search anti-patterns">
  <div class="bar">{chips}</div>
</div></header>
<main><div class="wrap">
{chr(10).join(sections)}
<div class="more"><h3>More pitfalls, tool by tool</h3><p>Every facilitator guide ends with the common pitfalls for that tool: {pitfalls}.</p></div>
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
      sec.querySelectorAll('.ap').forEach(function(c){{
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
    (OUT / "anti-patterns.html").write_text(page, encoding="utf-8")
    print(f"wrote anti-patterns.html ({len(ANTIPATTERNS)} anti-patterns)")


if __name__ == "__main__":
    build()
