#!/usr/bin/env python3
"""Generate good-practices.html: the principles the toolkit is built on, the positive counterpart to anti-patterns.html.

PRACTICES below is the content: (id, group, title, principle, why, [what it looks like], origin or None, [tool keys],
[anti-pattern short labels it prevents]). Tool keys come from TOOLS in build_roles.py; anti-pattern labels must match
the short labels in build_antipatterns.py, which links each anti-pattern back to its practice.

Run:  python3 _generator/build_practices.py
"""
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_roles import TOOLS, FONT_URL  # noqa: E402
from build_antipatterns import ANTIPATTERNS, ap_id  # noqa: E402
from brand import ACCENT, NAVY, CREDIT  # noqa: E402

OUT = Path(__file__).resolve().parent.parent

GROUPS = [("work", "How we work"), ("facilitate", "How we facilitate")]

PRACTICES = [
    ("outcomes", "work", "Outcomes over output",
     "Judge work by what changed for users and the organisation, not by how much was shipped.",
     "Output is easy to count, but busy teams can deliver lots of features that change nothing.",
     ["Goals and epics state a measurable outcome", "Reviews ask “did it work?”, not just “is it done?”",
      "Roadmaps are organised by goals, not features and dates"],
     "Popularised by Joshua Seiden, Outcomes Over Output (2019).",
     ["value", "okr", "roadmap", "bet", "status"],
     ["Epics have no outcome", "OKRs are task lists", "Feature-and-date roadmaps"]),
    ("finish", "work", "Stop starting, start finishing",
     "Limit work in progress so work flows to done instead of piling up half-finished.",
     "Every extra item in progress slows all the others down and hides blocked work.",
     ["Explicit WIP limits on the board", "Swarm on blocked or ageing items before pulling new ones",
      "Fewer initiatives running at once at portfolio level"],
     "A saying from the Kanban community.",
     ["kanban", "ageing", "buffer", "portfolio-kanban"],
     ["Too much work in progress", "Blocked work goes unnoticed", "Unplanned work wrecks plans", "Too many initiatives"]),
    ("small", "work", "Small batches, early feedback",
     "Deliver in thin, usable slices so you learn from real users early and often.",
     "Big batches delay feedback, hide risk and make every change expensive.",
     ["Stories slice vertically through every layer", "Each release is small enough to roll back easily",
      "Stakeholders use the product at every review"],
     None,
     ["splitting", "storymap", "epic", "pipeline", "sprint-review"],
     ["Stories are technical tasks", "Stories keep carrying over", "Review is a one-way demo"]),
    ("no", "work", "Say no so the yes means something",
     "Keep priorities few and ranked, and say out loud what you're not doing.",
     "When everything is a priority, nothing is, and teams spread themselves thin.",
     ["One ordered list, not several “top priorities”", "A visible “not doing” list with reasons",
      "Old backlog items are archived, not kept forever"],
     None,
     ["prioritisation", "roadmap", "portfolio-kanban"],
     ["Everything is top priority", "Backlog graveyard", "Too many initiatives"]),
    ("visible", "work", "Make work and decisions visible",
     "Put the work, risks and decisions where everyone can see them.",
     "Hidden work and unrecorded decisions turn into surprises, rework and blame.",
     ["One board shows all the team's work, including unplanned work", "Decisions are written down with who made them",
      "Status shows confidence and trend, not only a colour"],
     None,
     ["kanban", "raid", "raci", "adr", "status"],
     ["Green until suddenly red", "Bad news travels slowly", "Unclear decision rights"]),
    ("safety", "work", "Safety before performance",
     "Make it safe to speak up, admit mistakes and disagree; performance follows.",
     "People hide problems and ideas when speaking up feels risky, so leaders learn too late.",
     ["Leaders respond to bad news with thanks and curiosity", "Disagreement happens openly, on the problem not the person",
      "Quiet voices are invited in"],
     "Psychological safety research by Amy Edmondson.",
     ["psych-safety", "leading-safety", "conflict", "feedback", "incident"],
     ["Quiet voices go unheard", "Conflict is avoided", "Bad news travels slowly"]),
    ("rhythm", "work", "Inspect and adapt on a rhythm",
     "Look at results and the way you work at short, regular intervals, and change something each time.",
     "Without a regular loop, problems repeat and plans drift away from reality.",
     ["Every event has a purpose and changes something", "Retro actions are reviewed at the next retro",
      "Cross-team problems get their own improvement loop"],
     "Empirical process control, at the heart of most agile methods.",
     ["events", "retro", "health", "cross-retro", "cadences"],
     ["Same issues at every retro", "Planning has no goal", "Cross-team problems persist"]),
    ("riskiest", "work", "Test the riskiest assumption first",
     "Treat ideas as bets and find the cheapest way to learn whether you're wrong.",
     "Building first and testing later is the most expensive way to find out nobody wanted it.",
     ["Assumptions are written down and scored", "Interviews, prototypes and fake doors come before full builds",
      "Funding follows evidence in stages"],
     None,
     ["bet", "experiment", "design-sprint", "ost", "premortem"],
     ["Annual funding only"]),
    ("fit", "work", "Match the approach to the situation",
     "Plan what's predictable, experiment where it isn't, and use only as much process as the work needs.",
     "One method applied everywhere either over-plans uncertain work or under-plans risky work.",
     ["Complex work gets experiments; complicated work gets analysis", "Forecasts are ranges, not single dates",
      "Structure is sized to the project, not copied from the last one"],
     "Draws on the Cynefin® framework (Dave Snowden).",
     ["cynefin", "right-size", "forecast"],
     ["Agile as a mandate", "Single-date promises"]),
    ("involve", "work", "Involve the people who do the work",
     "The people closest to the work help decide how it's done and how change happens.",
     "Imposed processes and changes get compliance at best; involvement gets commitment and better ideas.",
     ["Teams agree their own working agreements", "Decision rights are explicit, and delegated as far as is safe",
      "Change is led with people, not announced to them"],
     None,
     ["team-charter", "delegation", "launch", "adkar", "raci"],
     ["No agreed ways of working", "Unclear decision rights", "Product owner unavailable", "Change announced, not led"]),
    ("quality", "work", "Build quality in",
     "Make quality part of every step, with a shared Definition of Done and automation, instead of inspecting at the end.",
     "Quality added at the end is slow, costly and still misses things.",
     ["Acceptance criteria are agreed before work starts", "Tests and checks run automatically on every change",
      "“Done” means usable by users, not “dev done”"],
     "From W. Edwards Deming's “cease dependence on inspection”.",
     ["testing", "pipeline", "cd-health", "example", "team-charter"],
     ["“Done” means dev done", "Criteria written after the work", "Faster, but less stable"]),
    ("blame", "work", "Learn without blame",
     "When things go wrong, look at the system that let it happen, not the person who was nearest.",
     "Blame teaches people to hide mistakes, so the same failures come back.",
     ["Incident reviews ask how, not who", "Recurring problems are traced to root causes",
      "Lessons are shared beyond the team"],
     None,
     ["incident", "rootcause", "blockers", "retro"],
     ["Recurring blockers"]),
    ("whole", "work", "Optimise the whole, not the parts",
     "Improve the flow of value end to end, across teams, rather than making each team look busy.",
     "Local improvements can make the whole system slower, especially where teams depend on each other.",
     ["The value stream is mapped from idea to customer", "Team boundaries reduce hand-offs and dependencies",
      "Teams plan together, rather than being planned for"],
     "From systems thinking and lean (W. Edwards Deming, Taiichi Ohno).",
     ["vsm", "topology", "dependency", "ctp", "sync"],
     ["Teams wait on each other", "One team owns too much", "Cross-team sync is status", "Top-down big-room planning"]),
    ("measure", "work", "Measure to learn, not to judge",
     "Use metrics to understand and improve the system, never as targets for individuals or teams.",
     "When a measure becomes a target, people game it and it stops telling you anything.",
     ["Team measures, never individual ones", "Speed is always balanced with quality and outcomes",
      "Velocity stays inside the team that produced it"],
     "Goodhart's law (Charles Goodhart).",
     ["delivery-metrics", "estimation", "forecast", "value"],
     ["Velocity as a target", "Teams compared on velocity", "Individuals measured by tickets"]),
    ("heroes", "work", "Share knowledge, avoid heroes",
     "Spread skills so the team can keep going when anyone is away.",
     "A single expert becomes a bottleneck, and a risk the day they leave.",
     ["Skills are mapped and gaps planned for", "Pairing and mobbing are normal, not special",
      "New joiners are onboarded with a plan and a buddy"],
     None,
     ["skills", "pairing", "onboarding"],
     ["Single point of failure"]),
    ("accountable", "work", "People stay accountable, including for AI",
     "Tools, including AI agents, can do the work, but named people stay accountable for the result.",
     "Without clear ownership, mistakes from automated work fall between the cracks.",
     ["Autonomy for AI is agreed stage by stage", "AI output is reviewed like any other work",
      "Every decision and tool has a named owner"],
     None,
     ["ai-delivery", "ai", "raci"],
     []),
    ("alone", "facilitate", "Think alone, then talk together",
     "Give people silent time to write their own ideas before any group discussion.",
     "Open discussion favours the loudest and most senior voices; silent writing gets everyone's thinking.",
     ["Silent writing on stickies before sharing", "Dot voting instead of debate to choose",
      "Pairs or small groups before the whole room"],
     None,
     ["facilitation", "lean-coffee", "retro", "design-sprint"],
     ["Quiet voices go unheard"]),
    ("purpose", "facilitate", "Purpose, output, timebox",
     "Every session states why it exists, what it will produce, and how long it will take.",
     "Meetings without a clear purpose drift, overrun and leave people wondering why they came.",
     ["The purpose and output are written up at the start", "A visible timer for each part",
      "Events that lack a purpose are merged or dropped"],
     None,
     ["events", "facilitation", "daily", "refinement"],
     ["Meetings have no clear purpose", "Daily sync is a status report", "Refinement happens in planning"]),
    ("owner", "facilitate", "Close with an owner and a date",
     "Every action leaving a session has one named owner and a date.",
     "Actions owned by “the team” or with no date quietly disappear.",
     ["Few actions, each with one owner", "Actions are reviewed at the start of the next session",
      "Blockers go on a visible impediments list"],
     None,
     ["retro", "impediments", "raid"],
     ["Same issues at every retro"]),
    ("ask", "facilitate", "Ask more than you tell",
     "Facilitators and coaches help people find their own answers through questions.",
     "Answers people reach themselves stick; answers handed to them rarely do.",
     ["Open questions: what, how, who", "Silence is given time to work",
      "Advice is offered last, and labelled as advice"],
     None,
     ["coaching", "sm-cheat", "facilitation"],
     ["SM is the team's secretary"]),
]

SHORTS = {a[2] for a in ANTIPATTERNS}
for _id, grp, title, _p, _w, looks, _o, keys, prevents in PRACTICES:
    assert grp in dict(GROUPS), grp
    for k in keys:
        assert k in TOOLS, f"{title}: unknown tool {k}"
    for s in prevents:
        assert s in SHORTS, f"{title}: unknown anti-pattern {s}"


def practice_for(short):
    """The practices that prevent an anti-pattern, as (id, title) pairs."""
    return [(pid, title) for pid, _g, title, *_r, prevents in PRACTICES if short in prevents]


def build():
    long_name = {a[2]: a[1] for a in ANTIPATTERNS}
    sections, n = [], 0
    for gid, gname in GROUPS:
        cards = []
        for pid, grp, title, principle, why, looks, origin, keys, prevents in PRACTICES:
            if grp != gid:
                continue
            n += 1
            tools = " · ".join(f'<a href="{TOOLS[k][1]}">{escape(TOOLS[k][0])}</a>' for k in keys)
            prev = (f'<p class="prev">Prevents: ' + " · ".join(
                f'<a href="anti-patterns.html#{ap_id(s)}">{escape(long_name[s])}</a>' for s in prevents) + "</p>") if prevents else ""
            src = f'<p class="src">{escape(origin)}</p>' if origin else ""
            text = " ".join([title, principle, why] + looks).lower()
            cards.append(f'<div class="gp" id="{pid}" data-text="{escape(text)}"><span class="num">{n:02d}</span>'
                         f'<h3>{escape(title)}</h3><p class="principle">{escape(principle)}</p>'
                         f'<p class="why"><b>Why it matters:</b> {escape(why)}</p>'
                         f'<p class="lbl">What it looks like</p><ul>{"".join(f"<li>{escape(x)}</li>" for x in looks)}</ul>'
                         f'{src}<p class="see">Tools: {tools}</p>{prev}</div>')
        sections.append(f'<section class="grp"><h2>{escape(gname)} <span>{len(cards)}</span></h2>'
                        f'<div class="grid">{"".join(cards)}</div></section>')
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Good Practices</title>
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
input{{font:14px 'Geist',system-ui,sans-serif;padding:8px 12px;border-radius:6px;border:1px solid #334155;background:#0F2236;color:#fff;width:100%;max-width:360px;}}
input::placeholder{{color:#64748B;}}
main{{padding:16px 0 48px;}}
h2{{font:500 11px 'Geist Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:26px 0 10px;}}
h2 span{{color:#5B6B82;margin-left:6px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:12px;}}
.gp{{position:relative;background:#fff;border:1px solid var(--rule);border-top:4px solid #065F46;border-radius:8px;padding:14px 16px;scroll-margin-top:16px;}}
.gp:target{{box-shadow:0 0 0 3px #C2410C;}}
.gp .num{{position:absolute;top:12px;right:14px;font:500 11px 'Geist Mono',monospace;color:var(--muted);}}
.gp h3{{margin:0 30px 6px 0;font-size:16px;line-height:1.3;}}
.gp p{{margin:0 0 6px;font-size:13px;}}
.gp .principle{{font:italic 17px/1.35 'Instrument Serif',Georgia,serif;color:#065F46;margin-bottom:8px;}}
.gp .why{{color:var(--muted);}}
.gp .lbl{{font:600 9.5px 'Geist Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:10px 0 4px;}}
.gp ul{{margin:0 0 8px;padding-left:18px;font-size:13px;}}
.gp li{{margin:2px 0;}}
.gp .src{{font-size:12px;color:var(--muted);font-style:italic;}}
.gp .see,.gp .prev{{font-size:12px;color:var(--muted);margin-top:6px;}}
.gp .see a{{color:var(--ink);}}
.gp .prev a{{color:#991B1B;}}
.gp a:hover{{color:var(--accent);}}
.note{{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:16px 18px;margin-top:28px;font-size:13px;}}
.note h3{{margin:0 0 6px;font-size:15px;}}
.note a{{color:#9A3412;}}
.hidden{{display:none !important;}}
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#5B6B82;text-align:center;padding:0 16px 32px;}}
@media print{{header{{padding:16px;}} input{{display:none;}} .gp{{break-inside:avoid;}}}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="index.html">← All tools</a>
  <h1>Good Practices</h1>
  <p>{n} principles that run through the whole toolkit, each with why it matters, what it looks like, the tools that put it into practice, and the <a href="anti-patterns.html">anti-patterns</a> it prevents. They're good practices, not “best practices”: what works depends on your situation.</p>
  <input type="search" placeholder="Search practices, e.g. “feedback” or “WIP”…" aria-label="Search good practices">
</div></header>
<main><div class="wrap">
{chr(10).join(sections)}
<div class="note"><h3>Why “good”, not “best”</h3><p>A single best practice only exists when cause and effect are obvious. Most delivery work is complex, where the right move depends on context and has to be discovered. Use these as principles to reason from, and adapt them; the <a href="cynefin-board.html">Cynefin® Sense-Making</a> board helps you decide which approach fits. For situations rather than principles, see the <a href="scenarios.html">Scenario Playbook</a>.</p></div>
</div></main>
<footer>{escape(CREDIT)}</footer>
<script>
(function(){{
  var input=document.querySelector('input');
  input.addEventListener('input', function(){{
    var q=input.value.trim().toLowerCase();
    document.querySelectorAll('.grp').forEach(function(sec){{
      var any=false;
      sec.querySelectorAll('.gp').forEach(function(c){{
        var ok=!q || c.dataset.text.indexOf(q)>=0; c.classList.toggle('hidden', !ok); if(ok) any=true;
      }});
      sec.classList.toggle('hidden', !any);
    }});
  }});
}})();
</script>
</body>
</html>
"""
    (OUT / "good-practices.html").write_text(page, encoding="utf-8")
    print(f"wrote good-practices.html ({n} practices)")


if __name__ == "__main__":
    build()
