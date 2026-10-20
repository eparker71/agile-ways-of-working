#!/usr/bin/env python3
"""Generate glossary.html: plain-language definitions of the terms used across the toolkit.

TERMS below is the content. Each entry: (term, definition, framework note or None, [tool keys]).
Tool keys come from TOOLS in build_roles.py, so links stay in step with the role page.

Run:  python3 _generator/build_glossary.py
"""
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_roles import TOOLS, FONT_URL  # noqa: E402
from brand import ACCENT, NAVY, CREDIT  # noqa: E402

OUT = Path(__file__).resolve().parent.parent

TERMS = [
    ("Acceptance criteria", "The conditions a backlog item must meet to be accepted. Often written as concrete examples in "
     "Given / When / Then form, so they double as tests.", None, ["example", "backlog"]),
    ("Backlog", "An ordered list of the work a team or product might do. The top is detailed and ready; the bottom is rough "
     "ideas. The order is the plan.", "Scrum calls it the Product Backlog, owned by the Product Owner.", ["prioritisation", "backlog"]),
    ("Blocker", "Something stopping a single work item from moving forward right now, such as waiting for a review or an "
     "environment. Compare impediment.", None, ["blockers", "buffer"]),
    ("Burn-up chart", "A chart showing work completed rising toward a total-scope line over time. Unlike a burn-down, it makes "
     "scope changes visible.", None, ["forecast"]),
    ("Capacity", "How much work a team can realistically take on in a period, after holidays, other commitments and a buffer "
     "for unplanned work.", None, ["sprint-planning", "buffer"]),
    ("Class of service", "A policy for how a type of work is treated, such as Expedite, Fixed date, Standard or Intangible.",
     "From the Kanban Method.", ["kanban"]),
    ("Cognitive load", "How much a team has to hold in its head to do its work: domains, systems and tools. Too much slows "
     "everything down.", "From Team Topologies (Skelton & Pais).", ["topology"]),
    ("Cost of delay", "The value lost for each week an item isn't delivered. Dividing it by size (CD3, or WSJF in SAFe) gives a priority order.",
     "Popularised by Don Reinertsen.", ["prioritisation", "portfolio-kanban"]),
    ("Cycle time", "How long an item takes from starting work to done. Look at percentiles, not averages. Compare lead time.",
     None, ["ageing", "kanban"]),
    ("Definition of Done", "The shared quality bar every item must meet before it counts as done, such as tested, reviewed and "
     "releasable.", "Part of Scrum, where it's the commitment for the Increment.", ["team-charter", "kanban"]),
    ("Definition of Ready", "A team's checklist for when an item is clear and small enough to start. Best used as a guide, not "
     "a gate.", "Not part of the Scrum Guide; a common team practice.", ["team-charter", "example"]),
    ("Dependency", "Something one team needs from another person, team or supplier before it can finish its work.", None,
     ["dependency", "raid"]),
    ("Enabler", "Work that doesn't deliver user value directly but makes future value possible, such as paying down technical "
     "debt or building infrastructure.", "SAFe uses this term formally; other teams say technical work or tech debt.",
     ["delivery-metrics", "backlog"]),
    ("Epic", "A big bet that should deliver a business outcome, too large for one iteration and broken into smaller items.",
     "Meaning varies: in SAFe an epic sits above features; in Jira an epic sits directly above stories; Scrum doesn't define "
     "epics at all.", ["epic", "backlog"]),
    ("Experiment", "A small, time-boxed test of a hypothesis, with a measure agreed in advance, so the result tells you whether "
     "to persevere, pivot or stop.", None, ["experiment", "ost"]),
    ("Feature", "A capability users can see and use that delivers part of an epic's value.",
     "In SAFe, a feature fits within one planning increment; elsewhere the term is used more loosely.", ["epic", "backlog"]),
    ("Flow efficiency", "The share of an item's elapsed time spent actively working on it, rather than waiting. Often "
     "surprisingly low.", None, ["kanban"]),
    ("Impediment", "Anything limiting how well the team works that it can't easily fix alone, such as slow approvals or missing "
     "tools. Compare blocker.", "A Scrum term; removing impediments is part of the Scrum Master's role.", ["impediments"]),
    ("Increment", "A usable, done piece of product produced by the team, which adds to everything delivered before.",
     "A Scrum term.", ["sprint-review"]),
    ("Iteration", "A short, fixed timebox, usually one to four weeks, in which a team plans, builds and reviews work.",
     "Scrum calls it a Sprint. Kanban doesn't use iterations; work flows continuously.", ["sprint-planning", "sprint-review"]),
    ("Lead time", "How long an item takes from being requested to being delivered. Includes waiting before work starts. "
     "Compare cycle time.", "In DORA's metrics, lead time for changes means commit to production.", ["delivery-metrics"]),
    ("Minimum viable product (MVP)", "The smallest version of a product or feature that tests whether an idea is worth "
     "pursuing. It's for learning, not a cut-down release.", None, ["epic", "kickoff"]),
    ("OKR", "Objectives and Key Results: a few inspiring objectives, each with measurable key results that show whether it was "
     "achieved.", "Developed at Intel by Andy Grove; spread by John Doerr.", ["okr"]),
    ("Outcome", "A change in customer or business behaviour or results, such as more repeat orders. Compare output, the things "
     "you build.", None, ["value", "status"]),
    ("Pair programming", "Two people working on one task at one screen, swapping roles regularly. Mob or ensemble programming "
     "is the whole group working together.", "From Extreme Programming (XP).", ["pairing"]),
    ("Planning period", "A fixed span, often a quarter, for which several teams plan together.",
     "SAFe calls this a Program Increment (PI).", ["ctp"]),
    ("Product goal", "The longer-term objective a product is working toward. Backlog items should move toward it.",
     "A Scrum term.", ["vision"]),
    ("Psychological safety", "A shared belief that it's safe to take interpersonal risks: to speak up, ask for help, admit a "
     "mistake or disagree.", "From Amy Edmondson's research.", ["psych-safety"]),
    ("Refinement", "The ongoing work of clarifying, splitting and ordering backlog items so the top of the backlog is ready.",
     "Scrum calls it Product Backlog refinement; it isn't a formal event.", ["splitting", "example"]),
    ("Retrospective", "A regular session where the team inspects how it works and agrees improvements to try.", None,
     ["retro", "cross-retro"]),
    ("Service level expectation (SLE)", "A forecast of how long a single item is likely to take, such as “85% of items finish "
     "within 8 days”.", "From the Kanban Guide.", ["ageing"]),
    ("Spike", "Time-boxed research to answer a question or reduce uncertainty. Its output is knowledge, not product.",
     "From Extreme Programming (XP).", ["splitting", "backlog"]),
    ("Sprint goal", "The single objective for a sprint, explaining why it's valuable. It guides trade-offs when plans change.",
     "A Scrum term.", ["sprint-planning"]),
    ("Stakeholder", "Anyone affected by, or able to affect, the work: users, customers, sponsors, other teams, regulators.",
     None, ["stakeholder"]),
    ("Story", "A thin, vertical slice of a feature that a user can use, small enough to finish in a few days. Often written "
     "“As a…, I want…, so that…”.", "From Extreme Programming (XP). Scrum uses the neutral term Product Backlog Item.",
     ["backlog", "splitting", "storymap"]),
    ("Story map", "A layout of the user's journey as activities and tasks, with stories underneath, sliced into releases.",
     "From Jeff Patton.", ["storymap"]),
    ("Swarming", "When several team members stop starting new work and gather on one item to finish it, often because it's "
     "blocked or ageing.", None, ["buffer", "pairing"]),
    ("Task", "A step the team takes to finish a story. Not tracked as value on its own.", None, ["backlog"]),
    ("Technical debt", "The future cost of shortcuts or outdated design in a system. Its “interest” is the extra effort it adds "
     "to every change.", "The metaphor is from Ward Cunningham.", ["delivery-metrics"]),
    ("Throughput", "The number of items a team finishes in a period. Used for forecasting.", None, ["forecast", "kanban"]),
    ("Timebox", "A fixed maximum time for an activity. When it's up, you stop and decide what's next.", None,
     ["lean-coffee", "example"]),
    ("Value stream", "All the steps needed to deliver value to a customer, from request to use. Teams are often organised "
     "around them.", None, ["topology", "value"]),
    ("Velocity", "The amount of work, often in story points, a team completes per iteration. Useful for the team's own "
     "forecasting; never for comparing teams.", None, ["forecast", "sprint-planning"]),
    ("Vertical slice", "A piece of work that cuts through every layer (interface, logic, data) so a user can use it. The "
     "opposite of splitting by technical layer.", None, ["splitting", "backlog"]),
    ("Work item age", "How long an item that isn't finished yet has been in progress. A leading signal of risk.",
     "From the Kanban Guide.", ["ageing"]),
    ("WIP (work in progress)", "The number of items started but not finished. Limiting WIP shortens cycle time and improves "
     "focus.", None, ["kanban", "portfolio-kanban"]),
    ("Delegation poker", "A game for agreeing decision rights: for each decision area, everyone shows a card from 1 (Tell) to 7 "
     "(Delegate) at once, then discusses the differences.", "From Management 3.0 (Jurgen Appelo).", ["delegation"]),
    ("Kano model", "A way to classify features by how they affect satisfaction: basics users simply expect, performance features "
     "where more is better, and delighters nobody asked for.", "From Professor Noriaki Kano.", ["vision", "ost"]),
    ("MoSCoW", "Sorting scope into Must have, Should have, Could have and Won't have (this time), usually for a fixed date or "
     "release.", "From Dai Clegg; part of the DSDM method.", ["prioritisation"]),
    ("Planning poker", "An estimation technique: everyone reveals a card at once (often 1, 2, 3, 5, 8, 13), the highest and "
     "lowest explain, and the group re-votes. It avoids anchoring on the first opinion.",
     "Described by James Grenning; popularised by Mike Cohn.", ["sprint-planning", "splitting"]),
    ("RICE", "A scoring model: Reach × Impact × Confidence, divided by Effort. Suits product teams that have usage data.",
     "Developed at Intercom.", ["prioritisation"]),
    ("ROAM", "A way to close out each risk with a decision: Resolved, Owned, Accepted or Mitigated.",
     "From SAFe's PI Planning.", ["raid", "ctp"]),
    ("Story points", "A relative measure of the size of backlog items, combining effort, complexity and uncertainty. Used with "
     "velocity for forecasting. Many teams now count items instead.", "Common in Scrum teams, but not part of the Scrum Guide.",
     ["sprint-planning", "forecast"]),
    ("WSJF (Weighted Shortest Job First)", "Ranking work by cost of delay divided by job size, so the most value per unit of "
     "effort, soonest, goes first.", "SAFe's name for CD3, from Don Reinertsen's work on cost of delay.",
     ["prioritisation", "portfolio-kanban"]),
    ("Working agreement", "A short set of norms a team agrees on, such as how it communicates, decides and handles "
     "interruptions.", None, ["team-charter", "ai"]),
]

for t, _d, _n, keys in TERMS:
    for k in keys:
        assert k in TOOLS, f"{t}: unknown tool {k}"


def slug(term):
    return re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")


def build():
    terms = sorted(TERMS, key=lambda t: t[0].lower())
    letters = sorted({t[0][0].upper() for t in terms})
    jump = "".join(f'<a href="#letter-{l}">{l}</a>' for l in letters)
    rows, current = [], None
    for term, definition, note, keys in terms:
        letter = term[0].upper()
        if letter != current:
            rows.append(f'<h2 id="letter-{letter}">{letter}</h2>')
            current = letter
        links = " · ".join(f'<a href="{TOOLS[k][1]}">{escape(TOOLS[k][0])}</a>' for k in keys)
        n = f'<p class="note">{escape(note)}</p>' if note else ""
        rows.append(f'<div class="term" id="{slug(term)}" data-text="{escape((term + " " + definition).lower())}">'
                    f'<h3>{escape(term)}</h3><p>{escape(definition)}</p>{n}<p class="see">See: {links}</p></div>')
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Glossary</title>
<link rel="stylesheet" href="{FONT_URL}">
<style>
:root{{--accent:{ACCENT};--navy:{NAVY};--ink:#1E293B;--muted:#64748B;--rule:#E2E8F0;}}
*{{box-sizing:border-box;}}
html,body{{margin:0;background:#F1F5F9;}}
body{{font-family:'Geist',Inter,system-ui,sans-serif;color:var(--ink);font-size:14px;line-height:1.55;}}
header{{background:var(--navy);border-top:4px solid var(--accent);color:#fff;padding:36px 16px 28px;}}
.wrap{{max-width:860px;margin:0 auto;padding:0 16px;}}
h1{{font:400 44px/1.05 'Instrument Serif',Georgia,serif;margin:0 0 8px;}}
header p{{color:#94A3B8;margin:0 0 16px;max-width:680px;}}
header a.back{{color:#94A3B8;font:500 11px 'Geist Mono',monospace;letter-spacing:.06em;}}
.tools{{display:flex;flex-wrap:wrap;gap:6px;align-items:center;}}
.jump a{{font:500 11px 'Geist Mono',monospace;color:#fff;text-decoration:none;border:1px solid #334155;border-radius:4px;padding:3px 7px;}}
.jump a:hover{{border-color:var(--accent);color:var(--accent);}}
input{{font:14px 'Geist',system-ui,sans-serif;padding:8px 12px;border-radius:6px;border:1px solid #334155;background:#0F2236;color:#fff;width:100%;max-width:360px;margin-bottom:12px;}}
input::placeholder{{color:#64748B;}}
main{{padding:16px 0 48px;}}
h2{{font:500 11px 'Geist Mono',monospace;letter-spacing:.14em;color:var(--muted);margin:24px 0 8px;scroll-margin-top:12px;}}
.term{{background:#fff;border:1px solid var(--rule);border-left:4px solid var(--accent);border-radius:8px;padding:14px 18px;margin:0 0 10px;scroll-margin-top:12px;}}
.term:target{{box-shadow:0 0 0 3px rgba(235,108,54,.35);}}
.term h3{{margin:0 0 4px;font-size:16px;}}
.term p{{margin:0 0 6px;}}
.term .note{{font-size:12.5px;color:#9A3412;background:#FFF7ED;border-radius:4px;padding:4px 8px;display:inline-block;}}
.term .see{{font-size:12px;color:var(--muted);margin:2px 0 0;}}
.term .see a{{color:var(--ink);}}
.term .see a:hover{{color:var(--accent);}}
.hidden{{display:none;}}
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#94A3B8;text-align:center;padding:0 16px 32px;}}
@media print{{header{{padding:16px;}} input,.jump{{display:none;}} .term{{break-inside:avoid;}}}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="index.html">← All tools</a>
  <h1>Glossary</h1>
  <p>Plain-language definitions of the terms used across the toolkit. Orange notes give where a term comes from, or where frameworks and tools use it differently.</p>
  <input type="search" placeholder="Filter terms…" aria-label="Filter terms">
  <div class="tools jump">{jump}</div>
</div></header>
<main><div class="wrap">
{chr(10).join(rows)}
</div></main>
<footer>{escape(CREDIT)}</footer>
<script>
(function(){{
  var input=document.querySelector('input'), terms=document.querySelectorAll('.term'), heads=document.querySelectorAll('main h2');
  input.addEventListener('input',function(){{
    var q=input.value.trim().toLowerCase();
    terms.forEach(function(t){{ t.classList.toggle('hidden', q && t.dataset.text.indexOf(q)<0); }});
    heads.forEach(function(h){{
      var n=h.nextElementSibling, any=false;
      while(n && n.tagName!=='H2'){{ if(!n.classList.contains('hidden')) any=true; n=n.nextElementSibling; }}
      h.classList.toggle('hidden', !any);
    }});
  }});
}})();
</script>
</body>
</html>
"""
    (OUT / "glossary.html").write_text(page, encoding="utf-8")
    print(f"wrote glossary.html ({len(terms)} terms)")


if __name__ == "__main__":
    build()
