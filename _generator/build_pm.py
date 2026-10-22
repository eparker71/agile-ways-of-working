#!/usr/bin/env python3
"""Generate for-project-managers.html: familiar project management artefacts, and the toolkit tools that do the same job.

ARTEFACTS below is the content: (id, artefact, what it's for, [tool keys], what stays the same, what changes, watch out).
Tool keys come from TOOLS in build_roles.py. Written in our own words; PMI's terms are named as the source, with a
trademark notice.

Run:  python3 _generator/build_pm.py
"""
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (where each file lives; see paths.py)
from build_roles import TOOLS, FONT_URL  # noqa: E402
from brand import ACCENT, NAVY, CREDIT  # noqa: E402

OUT = Path(__file__).resolve().parent.parent

ARTEFACTS = [
    ("charter", "Project charter", "Authorise the project and agree why it exists.", ["kickoff", "vision"],
     "A sponsor, a purpose, measurable success and the people involved.",
     "Outcomes over a fixed scope; trade-off sliders say what can flex.",
     "A charter signed and never looked at again. Revisit it at each milestone."),
    ("business-case", "Business case", "Justify the investment.", ["bet", "value", "portfolio-kanban"],
     "The problem, the value, the cost and the risks.",
     "Treated as a bet with a stop rule, tested cheaply before the full spend.",
     "Spending the whole budget before testing the riskiest assumption."),
    ("approach", "Development approach and tailoring", "Decide how the project will be run.", ["approach", "right-size", "cynefin"],
     "A deliberate choice, made early and written down.",
     "Chosen per part of the work: agile, predictive or hybrid, with clear connections.",
     "One approach for everything, or an approach chosen by fashion."),
    ("scope", "Scope statement and requirements", "Agree what's in and out.", ["storymap", "epic", "backlog", "example"],
     "Explicit in and out of scope.",
     "Detail emerges just in time; examples replace long specifications.",
     "Writing every requirement up front for work that will change."),
    ("wbs", "Work breakdown structure (WBS)", "Break the work into manageable pieces.", ["epic", "storymap", "splitting"],
     "Big work is broken down until it's manageable.",
     "Broken down by value to users (thin slices), not by phase or component.",
     "Splitting by technical layer, so nothing is usable until everything is done."),
    ("schedule", "Schedule and baseline", "Say when things will happen.", ["forecast", "roadmap", "ctp"],
     "Milestones and dates that people can plan around.",
     "Forecast as a range from real throughput, and updated every iteration.",
     "A single date promised before anyone knows enough. See the Single-date promises anti-pattern."),
    ("critical-path", "Critical path and dependencies", "Find what could delay the end date.", ["dependency", "vsm", "ctp"],
     "Know which dependencies drive the dates.",
     "Dependencies made visible across teams, and removed where possible, not just managed.",
     "Managing the same dependency every month instead of changing team boundaries."),
    ("resources", "Responsibility matrix and resources", "Agree who does what.", ["raci", "skills", "topology"],
     "Clear accountability for each piece of work.",
     "Stable teams take on the work, rather than people being assigned to tasks.",
     "Moving people between projects every few weeks."),
    ("risk", "Risk register", "Find and respond to what could go wrong.", ["raid", "premortem"],
     "Risks with owners, likelihood, impact and responses.",
     "Reviewed every iteration, and surfaced early with a pre-mortem.",
     "A register filled in at the start and never reviewed."),
    ("issues", "Issue log", "Track problems happening now.", ["raid", "impediments", "blockers"],
     "Each issue has an owner and an action.",
     "Impediments are visible on the team's board and escalated on a time limit.",
     "Issues that wait for the next steering meeting."),
    ("change", "Change control and change log", "Decide how scope changes are handled.", ["prioritisation", "sprint-review", "raci"],
     "Changes are decided deliberately, by the right people, and recorded.",
     "Change is expected: new work is ordered against existing work, every iteration.",
     "A change board that slows every small decision. Match the control to the risk."),
    ("stakeholders", "Stakeholder register and engagement", "Keep the right people involved.", ["stakeholder", "sprint-review"],
     "Know who cares, how much, and how to engage them.",
     "Stakeholders see working results regularly, not just reports.",
     "Engaging stakeholders only at gates."),
    ("comms", "Communications plan", "Agree who hears what, when and how.", ["stakeholder", "status", "events"],
     "The right message to the right people at the right rhythm.",
     "The team's events (reviews, syncs) do much of the communicating.",
     "Reports nobody reads. Ask audiences what they actually need."),
    ("status", "Status reports and earned value", "Show progress against the plan.", ["status", "forecast", "value"],
     "Honest, regular reporting of progress, cost and risk.",
     "Progress measured by working results and outcomes; a burn-up shows scope and done together.",
     "Green until suddenly red. Report the forecast range and the decisions needed."),
    ("quality", "Quality management plan", "Agree how quality is assured.", ["testing", "release", "team-charter"],
     "Agreed standards and checks.",
     "Quality built in: a Definition of Done, automated tests and small, frequent releases.",
     "Testing as a phase at the end."),
    ("lessons", "Lessons learned register", "Improve the next project.", ["retro", "closeout", "experiment"],
     "Learning is captured and shared.",
     "Learning happens every iteration, and turns into small experiments straight away.",
     "Lessons recorded at the end, when it's too late to use them."),
    ("benefits", "Benefits realisation", "Check the project delivered its value.", ["closeout", "value", "okr"],
     "Benefits have owners and are measured after delivery.",
     "Outcomes are measured during the project too, so direction can change.",
     "Nobody checks the benefits once the project team has gone."),
]

for _id, name, _purpose, keys, *_rest in ARTEFACTS:
    for k in keys:
        assert k in TOOLS, f"{name}: unknown tool {k}"


def build():
    rows = []
    for aid, name, purpose, keys, same, change, watch in ARTEFACTS:
        tools = " · ".join(f'<a href="{TOOLS[k][1]}">{escape(TOOLS[k][0])}</a>' for k in keys)
        rows.append(f'<section class="pm" id="{aid}"><h2>{escape(name)}</h2><p class="for">{escape(purpose)}</p>'
                    f'<p class="tools"><b>In the toolkit:</b> {tools}</p>'
                    f'<div class="cols"><div><p class="lbl">Stays the same</p><p>{escape(same)}</p></div>'
                    f'<div><p class="lbl">What changes</p><p>{escape(change)}</p></div>'
                    f'<div><p class="lbl">Watch out</p><p>{escape(watch)}</p></div></div></section>')
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>For Project Managers</title>
<link rel="stylesheet" href="{FONT_URL}">
<style>
:root{{--accent:{ACCENT};--navy:{NAVY};--ink:#1E293B;--muted:#5B6B82;--rule:#E2E8F0;}}
*{{box-sizing:border-box;}}
html,body{{margin:0;background:#F1F5F9;}}
body{{font-family:'Geist',Inter,system-ui,sans-serif;color:var(--ink);font-size:14px;line-height:1.55;}}
header{{background:var(--navy);border-top:4px solid var(--accent);color:#fff;padding:36px 16px 26px;}}
.wrap{{max-width:1000px;margin:0 auto;padding:0 16px;}}
h1{{font:400 44px/1.05 'Instrument Serif',Georgia,serif;margin:0 0 8px;}}
header p{{color:#94A3B8;margin:0 0 12px;max-width:760px;}}
header p a{{color:#FDBA74;}}
header a.back{{color:#94A3B8;font:500 11px 'Geist Mono',monospace;letter-spacing:.06em;}}
main{{padding:20px 0 48px;}}
.pm{{background:#fff;border:1px solid var(--rule);border-left:4px solid #92400E;border-radius:10px;padding:16px 20px;margin:0 0 12px;scroll-margin-top:12px;}}
.pm h2{{font:400 24px/1.15 'Instrument Serif',Georgia,serif;margin:0 0 2px;}}
.pm .for{{margin:0 0 8px;color:var(--muted);}}
.pm .tools{{margin:0 0 6px;font-size:13.5px;}}
.pm .tools a{{color:var(--ink);font-weight:500;}}
.pm .tools a:hover{{color:#9A3412;}}
.cols{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px 20px;}}
.cols p{{margin:0;font-size:13px;}}
.lbl{{font:600 9.5px 'Geist Mono',monospace !important;letter-spacing:.12em;text-transform:uppercase;color:#9A3412;margin:8px 0 3px !important;}}
.note{{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:14px 18px;margin-top:22px;font-size:13px;}}
.note a{{color:#9A3412;}}
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#5B6B82;text-align:center;padding:0 16px 32px;}}
@media (max-width:700px){{.cols{{grid-template-columns:1fr;}}}}
@media print{{header{{padding:16px;}} .pm{{break-inside:avoid;}}}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="index.html">← All tools</a>
  <h1>For Project Managers</h1>
  <p>The artefacts you know from PMI's standards, such as the project charter, WBS, risk register and change log, and the tools in this kit that do the same job in an agile or hybrid way. For each: what stays the same, what changes, and what to watch. Start with the <a href="delivery-approach-board.html">Delivery Approach</a> board to choose how each part of a project should run.</p>
</div></header>
<main><div class="wrap">
{chr(10).join(rows)}
<div class="note"><p>Written in our own words. PMI®, PMP®, PMI-ACP® and PMBOK® are registered trademarks of Project Management Institute, Inc. This toolkit isn't affiliated with or endorsed by PMI. See also the <a href="start-here-by-role.html#pm">Project Manager tools</a>, the <a href="right-size-poster.html">Right-Size Your Structure</a> poster, and the <a href="glossary.html">Glossary</a> for terms like baseline, earned value and rolling-wave planning.</p></div>
</div></main>
<footer>{escape(CREDIT)}</footer>
</body>
</html>
"""
    paths.write_page("for-project-managers.html", page)
    print(f"wrote for-project-managers.html ({len(ARTEFACTS)} artefacts)")


if __name__ == "__main__":
    build()
