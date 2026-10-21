#!/usr/bin/env python3
"""Generate tools-by-industry.html: which tools suit different kinds of work, and how to say things there.

INDUSTRIES below is the content: (id, name, what's different here, [start-with tool keys (3)], [also-useful tool keys],
[(toolkit term, what people there might say)], [(watch-out, anti-pattern short label or None)], [tools to skip or
adapt], skip note). Tool keys come from TOOLS in build_roles.py; anti-pattern labels must match the short labels in
build_antipatterns.py. A toolkit term links to the glossary when the glossary has it.

Run:  python3 _generator/build_industries.py
"""
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_roles import TOOLS, FONT_URL  # noqa: E402
from build_antipatterns import ANTIPATTERNS, ap_id  # noqa: E402
from build_glossary import TERMS, slug  # noqa: E402
from brand import ACCENT, NAVY, CREDIT  # noqa: E402

OUT = Path(__file__).resolve().parent.parent

INDUSTRIES = [
    ("software", "Software & digital products",
     "Most of the toolkit was written with you in mind. Work is uncertain, you can release often, and feedback is fast "
     "if you build for it. The risk is busyness: shipping lots of output without checking that it changed anything.",
     ["ost", "example", "pipeline"],
     ["storymap", "refinement", "testing", "release", "cd-health", "adr", "event-storming", "delivery-metrics",
      "incident", "ai-delivery"],
     [("Increment", "release, version"), ("Spike", "time-boxed investigation"), ("Definition of Done", "release checklist"),
      ("Technical debt", "the cost of shortcuts, to non-technical people")],
     [("Work is “done” when it's merged, not when customers have it", "“Done” means dev done"),
      ("Going faster while incidents and rework rise", "Faster, but less stable"),
      ("Using velocity to compare or push teams", "Velocity as a target")],
     [], "Nearly everything fits. Use the project tools (RAID Log, Status Report) when you have a fixed-scope project, "
         "not for ongoing product work."),
    ("marketing", "Marketing & communications",
     "Work arrives as campaigns with fixed launch dates, many reviewers and approvers, and results you only see after "
     "launch. Small, frequent experiments beat one big launch you can't change.",
     ["kanban", "prioritisation", "experiment"],
     ["stakeholder", "okr", "persona", "roadmap", "bet", "design-sprint", "lean-coffee", "retro"],
     [("Backlog", "campaign pipeline"), ("Story", "deliverable, asset"), ("Definition of Done", "ready to publish"),
      ("Increment", "launch"), ("WIP (work in progress)", "campaigns in flight"), ("Retrospective", "campaign wash-up")],
     [("Approvals wait out of sight: show “waiting for sign-off” as its own column", None),
      ("Every campaign is urgent, so nothing gets finished", "Everything is top priority"),
      ("Counting posts and emails sent instead of leads or sign-ups", None)],
     ["event-storming", "cd-health", "testing", "pipeline", "adr"],
     "These are about building and releasing software. Release Readiness still works for a big launch."),
    ("hr", "HR & people teams",
     "Your customers are employees and managers, and much of your work is change: new policies, systems and ways of "
     "working. Some work is confidential, and roll-outs succeed or fail on adoption, not on the launch date.",
     ["kanban", "stakeholder", "adkar"],
     ["persona", "experiment", "okr", "onboarding", "raci", "psych-safety", "user-manual", "motivation", "feedback",
      "coaching", "retro"],
     [("Stakeholder", "managers, leaders, unions"), ("Persona", "employee or candidate persona"),
      ("Increment", "roll-out, pilot"), ("Story", "“As a new starter, I want…”"),
      ("Minimum viable product (MVP)", "pilot with one team")],
     [("Announcing a change and calling it done", "Change announced, not led"),
      ("Rolling out several big changes at once", "Too many initiatives"),
      ("Putting confidential cases on a shared board: use a private lane with no names", None)],
     ["pipeline", "cd-health", "testing", "adr", "event-storming"],
     "These are for software delivery. For a new HR system, the delivery team will use them; you'll need Release "
     "Readiness."),
    ("itops", "IT operations & service desks",
     "Work arrives unpredictably, much of it urgent, with service levels to meet. Planning fixed iterations rarely "
     "survives the first day, so manage flow: limit work in progress, make queues visible and learn from incidents.",
     ["kanban", "ageing", "blockers"],
     ["buffer", "cadences", "incident", "rootcause", "vsm", "delivery-metrics", "impediments", "raci", "marginal"],
     [("Backlog", "ticket queue"), ("Class of service", "priority (P1 to P4)"),
      ("Service level expectation (SLE)", "service level target"), ("Increment", "change"),
      ("Swarming", "major-incident response")],
     [("Planned work collapses under urgent tickets", "Unplanned work wrecks plans"),
      ("The same blockers come back every week", "Recurring blockers"),
      ("Ranking people by tickets closed", "Individuals measured by tickets")],
     ["storymap", "sprint-planning", "design-sprint", "example"],
     "Fixed iterations fit badly with unplanned work. Use Kanban Cadences instead of sprint events, and keep "
     "Story Mapping for bigger improvement projects."),
    ("data", "Data & analytics",
     "Work is a mix of requests, exploration and building pipelines. Many questions turn out to be the wrong question, "
     "and a dashboard nobody uses is waste. Start from the decision the work will inform.",
     ["kanban", "ost", "splitting"],
     ["experiment", "persona", "stakeholder", "refinement", "example", "adr", "testing", "pipeline", "value",
      "ai-delivery"],
     [("Story", "question, analysis request"), ("Spike", "exploration"), ("Acceptance criteria", "the decision this informs"),
      ("Definition of Done", "checked, documented and handed over"), ("Increment", "dataset or dashboard version")],
     [("Tickets that say “build table X” with no question behind them", "Stories are technical tasks"),
      ("Requests pile up that nobody will ever use", "Backlog graveyard"),
      ("Dashboards nobody opens: ask what decision each one informs", None)],
     ["storymap", "release", "design-sprint"],
     "Story maps and release plans fit products better than analysis. A data product with users is the exception."),
    ("hardware", "Hardware, manufacturing & engineering",
     "Changes cost more once something is built, parts have long lead times, and testing needs physical builds. You "
     "can still work iteratively: short build-test-learn cycles on prototypes, and flow on the factory floor.",
     ["vsm", "kanban", "premortem"],
     ["rootcause", "marginal", "experiment", "dependency", "ctp", "raid", "forecast", "testing", "adr", "incident",
      "design-sprint"],
     [("Iteration", "build-test cycle"), ("Increment", "prototype, build"), ("Spike", "proof of concept"),
      ("Definition of Done", "passes test and inspection"), ("Minimum viable product (MVP)", "engineering prototype")],
     [("Promising one ship date when parts and testing are uncertain", "Single-date promises"),
      ("Teams blocked by each other's parts and sign-offs", "Teams wait on each other"),
      ("Forcing two-week sprints on a six-week build cycle: match the cadence to the work", None)],
     ["pipeline", "cd-health", "splitting"],
     "Pipeline and CD tools are for software, so use them only for firmware. Splitting still works, but slice by "
     "capability or test, not by user story."),
    ("public", "Public sector & government",
     "Services must work for everyone, decisions are scrutinised, and funding and governance often assume you know "
     "everything up front. Show learning early, through research, pilots and open plans, to build trust.",
     ["persona", "stakeholder", "roadmap"],
     ["kickoff", "impact", "bet", "premortem", "raid", "status", "value", "adkar", "raci", "design-sprint", "closeout"],
     [("Persona", "service user"), ("Stakeholder", "ministers, policy teams, the public"),
      ("Minimum viable product (MVP)", "pilot, private beta"), ("Increment", "go-live of a service change"),
      ("Product goal", "policy intent")],
     [("Annual business cases that fix scope a year ahead", "Annual funding only"),
      ("Roadmaps of features and dates that become commitments", "Feature-and-date roadmaps"),
      ("Agile introduced by decree, without changing governance", "Agile as a mandate")],
     ["event-storming", "cd-health"],
     "Use them only where you build digital services in-house. Accessibility isn't optional here: put it in your "
     "Definition of Done."),
    ("healthcare", "Healthcare",
     "Work is safety-critical and regulated, clinical time is scarce, and teams run on shifts. Healthcare already has a "
     "strong improvement tradition (small Plan-Do-Study-Act cycles), and the toolkit fits it well: map the patient "
     "pathway, test small changes safely, and make it safe to speak up.",
     ["vsm", "experiment", "incident"],
     ["rootcause", "kanban", "daily", "blockers", "persona", "stakeholder", "psych-safety", "health", "marginal", "adkar",
      "raci"],
     [("Value stream", "patient pathway"), ("Experiment", "PDSA cycle (Plan-Do-Study-Act)"), ("Stand-up", "safety huddle"),
      ("Persona", "patient or carer"), ("Blocker", "delay in the pathway"), ("Retrospective", "debrief")],
     [("Junior staff don't raise safety concerns", "Quiet voices go unheard"),
      ("Problems reach leaders only when they've become incidents", "Bad news travels slowly"),
      ("Changing clinical practice without governance: run small, safe tests with clinical sign-off", None)],
     ["pipeline", "cd-health", "adr", "event-storming", "estimation"],
     "These are for software teams. If you build clinical software, you'll need them, plus your regulatory checks."),
    ("finance", "Finance & accounting",
     "Work follows the calendar: month-end close, audits, budgets and forecasts, with hard deadlines and peaks. "
     "Accuracy and controls matter, so improve the flow of the cycle rather than rushing it. Finance is also where "
     "annual budgeting can change into more frequent funding decisions.",
     ["kanban", "vsm", "raci"],
     ["cadences", "buffer", "blockers", "ageing", "rootcause", "stakeholder", "portfolio-kanban", "okr", "value",
      "experiment", "retro"],
     [("Iteration", "month-end cycle"), ("Backlog", "request queue"), ("Definition of Done", "reconciled and reviewed"),
      ("Class of service", "statutory deadline, standard, ad hoc"), ("Stakeholder", "budget holders, auditors"),
      ("Swarming", "close-week all hands")],
     [("Funding fixed once a year, a year ahead", "Annual funding only"),
      ("Nobody's sure who can approve what", "Unclear decision rights"),
      ("A new control after every mistake until nothing moves: review controls at the retro", None)],
     ["pipeline", "cd-health", "testing", "event-storming", "design-sprint", "storymap"],
     "These are for building products. Portfolio Kanban is the place to start moving beyond annual budgets."),
    ("legal", "Legal",
     "Work comes as matters with deadlines, much of it waits on clients, counterparties or courts, and it's "
     "confidential. Expert judgement is the bottleneck, so make the queue visible, triage it, and protect focus "
     "time.",
     ["kanban", "ageing", "prioritisation"],
     ["blockers", "raci", "stakeholder", "buffer", "refinement", "skills", "rootcause", "okr", "coaching", "retro"],
     [("Backlog", "matter list, intake queue"), ("Story", "matter, request"),
      ("Definition of Ready", "intake complete: facts, deadline, owner"),
      ("Class of service", "court deadline, standard, advisory"), ("Blocker", "waiting on the client or other side"),
      ("Throughput", "matters closed")],
     [("Every request is urgent, so lawyers switch all day", "Everything is top priority"),
      ("Matters waiting on others sit unseen for weeks", "Blocked work goes unnoticed"),
      ("Judging people only by billable hours", "Individuals measured by tickets"),
      ("Client details on a shared board: use matter codes, not names", None)],
     ["pipeline", "cd-health", "testing", "adr", "event-storming", "storymap", "design-sprint"],
     "These are for building products and software."),
    ("nonprofit", "Non-profit & education",
     "Capacity is tight, people wear many hats, volunteers come and go, and funders want evidence of impact. Keep "
     "tools light, make priorities explicit, and measure difference made, not activity.",
     ["impact", "kanban", "retro"],
     ["okr", "stakeholder", "experiment", "lean-coffee", "health", "raci", "roadmap", "onboarding", "motivation",
      "closeout", "value"],
     [("Persona", "beneficiary, learner, member"), ("Outcome", "impact"), ("Stakeholder", "funders, trustees, parents"),
      ("Iteration", "term, unit, funding round"), ("Retrospective", "end-of-term review")],
     [("Saying yes to every project a funder suggests", "Too many initiatives"),
      ("Everything is urgent because everything matters", "Everything is top priority"),
      ("Volunteers relearn how things work: keep ways of working on one page with a Team Charter", None)],
     ["pipeline", "cd-health", "testing", "adr", "event-storming", "estimation"],
     "These assume a software team or detailed estimates. Simple counts of finished work are enough here."),
]

SHORTS = {a[2] for a in ANTIPATTERNS}
GLOSSARY = {t[0].lower(): slug(t[0]) for t in TERMS}
for _id, name, _w, start, also, words, watch, skip, _s in INDUSTRIES:
    assert len(start) == 3, name
    for k in start + also + skip:
        assert k in TOOLS, f"{name}: unknown tool {k}"
    assert not set(start + also) & set(skip), f"{name}: a tool is both suggested and skipped"
    for term, _ in words:
        assert term.lower() in GLOSSARY, f"{name}: {term} isn't in the glossary"
    for _t, s in watch:
        assert s is None or s in SHORTS, f"{name}: unknown anti-pattern {s}"


def link(k, cls=""):
    return f'<a{cls} href="{TOOLS[k][1]}">{escape(TOOLS[k][0])}</a>'


def build():
    chips, cards = [], []
    for iid, name, why, start, also, words, watch, skip, skip_note in INDUSTRIES:
        chips.append(f'<a href="#{iid}">{escape(name)}</a>')
        first = "".join(f'<li>{link(k)}</li>' for k in start)
        rows = "".join(f'<tr><td><a href="glossary.html#{GLOSSARY[t.lower()]}">{escape(t)}</a></td><td>{escape(w)}</td></tr>'
                       for t, w in words)
        warn = "".join(f'<li>{escape(t)}' + (f' <a class="ap" href="anti-patterns.html#{ap_id(s)}">anti-pattern →</a>' if s else "")
                       + "</li>" for t, s in watch)
        skip_html = ((" · ".join(link(k) for k in skip) + ". ") if skip else "") + escape(skip_note)
        cards.append(f'''<section class="ind" id="{iid}">
<h2>{escape(name)}</h2>
<p class="why">{escape(why)}</p>
<div class="cols">
<div><p class="lbl">Start with</p><ol class="start">{first}</ol>
<p class="lbl">Also useful</p><p class="also">{" · ".join(link(k) for k in also)}</p></div>
<div><p class="lbl">Say it this way</p><table><tr><th>In the toolkit</th><th>Here you might say</th></tr>{rows}</table></div>
</div>
<div class="cols">
<div><p class="lbl">Watch out for</p><ul class="warn">{warn}</ul></div>
<div><p class="lbl">Skip or adapt</p><p class="skip">{skip_html}</p></div>
</div>
</section>''')
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tools by Industry</title>
<link rel="stylesheet" href="{FONT_URL}">
<style>
:root{{--accent:{ACCENT};--navy:{NAVY};--ink:#1E293B;--muted:#5B6B82;--rule:#E2E8F0;}}
*{{box-sizing:border-box;}}
html,body{{margin:0;background:#F1F5F9;}}
body{{font-family:'Geist',Inter,system-ui,sans-serif;color:var(--ink);font-size:14px;line-height:1.55;}}
header{{background:var(--navy);border-top:4px solid var(--accent);color:#fff;padding:36px 16px 26px;}}
.wrap{{max-width:1040px;margin:0 auto;padding:0 16px;}}
h1{{font:400 44px/1.05 'Instrument Serif',Georgia,serif;margin:0 0 8px;}}
header p{{color:#94A3B8;margin:0 0 16px;max-width:740px;}}
header p a{{color:#FDBA74;}}
header a.back{{color:#94A3B8;font:500 11px 'Geist Mono',monospace;letter-spacing:.06em;}}
nav.chips{{display:flex;flex-wrap:wrap;gap:8px;}}
nav.chips a{{color:#fff;text-decoration:none;font-size:12.5px;border:1px solid #334155;border-radius:999px;padding:5px 12px;background:#0F2236;}}
nav.chips a:hover{{border-color:var(--accent);}}
main{{padding:20px 0 48px;}}
.ind{{background:#fff;border:1px solid var(--rule);border-left:4px solid var(--accent);border-radius:10px;padding:18px 22px;margin:0 0 16px;scroll-margin-top:16px;}}
.ind:target{{box-shadow:0 0 0 3px #C2410C;}}
.ind h2{{font:400 28px/1.15 'Instrument Serif',Georgia,serif;margin:0 0 6px;}}
.ind .why{{margin:0 0 10px;max-width:820px;}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:6px 28px;}}
.lbl{{font:600 9.5px 'Geist Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#9A3412;margin:12px 0 6px;}}
ol.start{{margin:0;padding-left:20px;font-weight:600;}}
ol.start li{{margin:3px 0;}}
.ind a{{color:var(--ink);}}
.ind a:hover{{color:#9A3412;}}
.also,.skip{{margin:0;font-size:13px;color:var(--muted);}}
.also a,.skip a{{color:var(--ink);}}
table{{border-collapse:collapse;width:100%;font-size:13px;}}
th{{text-align:left;font:600 9.5px 'Geist Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding:0 8px 4px 0;border-bottom:1px solid var(--rule);}}
td{{padding:4px 8px 4px 0;border-bottom:1px solid var(--rule);vertical-align:top;}}
td:first-child{{width:42%;}}
ul.warn{{margin:0;padding-left:18px;font-size:13px;}}
ul.warn li{{margin:3px 0;}}
a.ap{{color:#991B1B;font-size:12px;white-space:nowrap;}}
.note{{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:16px 18px;margin-top:24px;font-size:13px;}}
.note h3{{margin:0 0 6px;font-size:15px;}}
.note a{{color:#9A3412;}}
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#5B6B82;text-align:center;padding:0 16px 32px;}}
@media (max-width:700px){{.cols{{grid-template-columns:1fr;}} .ind{{padding:16px;}}}}
@media print{{header{{padding:16px;}} nav.chips{{display:none;}} .ind{{break-inside:avoid;}}}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="index.html">← All tools</a>
  <h1>Tools by Industry</h1>
  <p>Agile ideas started in software, but the tools work wherever work is uncertain and people need to learn as they go. For each kind of work: where to start, what else helps, the words people there use, what to watch for, and what to skip. Pair it with <a href="start-here-by-role.html">Tools by role</a> and <a href="right-size-poster.html">Right-size your project</a>.</p>
  <nav class="chips" aria-label="Industries">{"".join(chips)}</nav>
</div></header>
<main><div class="wrap">
{chr(10).join(cards)}
<div class="note"><h3>Not on the list?</h3><p>Pick the closest kind of work: a construction or lab team often works like hardware (physical builds, long lead times), a retail, hospitality or customer service team like IT operations (unpredictable demand, service levels), and an operations or procurement team like finance (calendar-driven cycles and controls). Then start with three tools, use them for a few weeks, and keep what helps. The <a href="scenarios.html">Scenario Playbook</a> covers specific situations, and the <a href="glossary.html">Glossary</a> explains any term.</p></div>
</div></main>
<footer>{escape(CREDIT)}</footer>
</body>
</html>
"""
    (OUT / "tools-by-industry.html").write_text(page, encoding="utf-8")
    print(f"wrote tools-by-industry.html ({len(INDUSTRIES)} industries)")


if __name__ == "__main__":
    build()
