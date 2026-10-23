#!/usr/bin/env python3
"""Generate reports-by-role.html: one report for each role, with an example and an AI prompt to build it.

REPORTS below is the content, one per role in ROLES (build_roles.py), in the same order:
  (role id, report title, the question it answers, who it's for, how often, [what goes in it], [tool keys],
   example, prompt, watch-out)
The example is (heading, headline, [(measure, value, note)], next step), filled in for the fictional Basket team with the
same figures as the worked examples and story.py, so the two agree. Every prompt gets CHECK and ASK_BACK added here.

Run:  python3 _generator/build_reports.py
"""
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (where each file lives; see paths.py)
from build_roles import TOOLS, ROLES, FONT_URL  # noqa: E402
from build_prompts import ASK_BACK, COPY_JS  # noqa: E402
from brand import ACCENT, NAVY, CREDIT  # noqa: E402

CHECK = "Show the query or filter you used (for example, the JQL) and the count behind each figure, so I can check them."

REPORTS = [
    ("sm", "Iteration report", "Did we meet the iteration goal, and what got in the way?",
     "The team, the product owner and interested stakeholders", "At the end of each iteration, before the retro",
     ["The goal, and whether it was met", "Items finished, carried over and added mid-iteration",
      "Blocked time, and what caused it", "Progress on the last retro's actions"],
     ["sprint-review", "blockers", "retro", "ageing"],
     ("Basket team · Sprint 18 · 28 April – 9 May",
      "Goal partly met: one-tap reorder and flagging shipped; substitutes wait on the Stock API.",
      [("Items finished", "6 of 8 planned", "plus 1 added mid-iteration"),
       ("Carried over", "2", "substitutes, split into two stories"),
       ("Blocked days", "11", "8 of them waiting on the Stock API"),
       ("Oldest item in progress", "12 days", "out-of-stock rules; our SLE is 9 days"),
       ("Last retro's actions", "2 of 3 done", "silent writing still to try")],
      "Next: swarm on the Stock API work, and Example Mapping before Sprint 19 planning."),
     "Using the Jira or Azure DevOps project [KEY] and the iteration [name or dates], draft an iteration report for the "
     "team and stakeholders. Include: the iteration goal and whether it was met, saying how you judged it; items planned, "
     "finished, carried over and added mid-iteration; days items spent blocked or flagged, grouped by cause; the oldest "
     "item still in progress and its age; and the status of the last retrospective's actions: [paste or link]. Keep it to "
     "one page, at team level, in plain language.",
     "Don't report velocity as a score. Carry-over is information for planning, not a failure to explain away."),

    ("coach", "Team health trends", "Is the team getting healthier, and are our experiments working?",
     "The team, and their manager if the team agrees", "Each quarter, after the health check",
     ["Each health check area, with its trend since last time", "Signs of psychological safety",
      "Experiments tried, and what they showed", "One or two areas to focus on next"],
     ["health", "psych-safety", "experiment", "marginal"],
     ("Basket team · Q2 so far · 9 May",
      "Delivery is improving; waiting on other teams and quiet voices in meetings are the things to work on.",
      [("Releases", "improving", "self-service deploys since April"),
       ("Waiting on other teams", "still a problem", "3 items blocked on Platform and Payments"),
       ("Speaking up", "mixed", "problems raised one to one, not in the room"),
       ("Example Mapping", "kept", "rework fell from 4 in 9 stories to 1 in 10"),
       ("Counting items", "running", "a two-iteration trial instead of story points")],
      "Focus next: dependency waits, through the cross-team sync, and silent writing in retros."),
     "Here are our team health check results for the last [two or three] rounds: [paste results or link the Confluence "
     "page], and notes from our experiments: [paste]. Summarise how each area has moved and why, what each experiment "
     "showed against its measure, and suggest one or two areas to focus on next, with a small experiment for each. Quote "
     "the team's own words where they help, without identifying anyone.",
     "Health checks are the team's data. Share the trends only with the team's agreement, and never turn the scores into a target."),

    ("po", "Outcome and backlog report", "Are we moving the outcome, and is the backlog ready for what's next?",
     "Stakeholders and the team", "Each iteration, at the review",
     ["The outcome measures against their targets", "What shipped, and what we learned from users",
      "How much of the backlog is ready, and how old it is", "What's coming next, and why"],
     ["sprint-review", "refinement", "backlog", "value"],
     ("Reorder made easy · 9 May",
      "Repeat orders are up from 22% to 25%; the next two iterations are ready, with substitutes first.",
      [("Weekly repeat orders", "25%", "from 22%; target 30% by the end of June"),
       ("Median basket time", "21 min", "from 38; target 10"),
       ("Ready for the next two iterations", "9 items", "refined, with acceptance criteria"),
       ("Backlog items over 6 months old", "14", "to review at the next refinement"),
       ("Stakeholder requests", "4", "a margin check for substitutes added")],
      "Next: substitutes, once the Stock API arrives, then order history in a smaller first slice."),
     "Using the Jira or Azure DevOps project [KEY], draft a product owner's report for this iteration's review. Include: "
     "our outcome measures [list them with baselines and targets, or paste the latest figures]; the items finished this "
     "iteration and what each was for; how many backlog items meet our Definition of Ready [paste it] for the next two "
     "iterations; how many backlog items are more than six months old; and the next five items in order, with a line on "
     "why each. End with any decisions I need from stakeholders.",
     "Outcomes first, output second. A long list of finished items says little about whether customers are better off."),

    ("product", "Bet review", "Did the bet pay off, and should we continue, change course or stop?",
     "Product leadership and sponsors", "At each bet's checkpoint",
     ["The hypothesis, and the go or stop rule agreed up front", "What the test showed, against the rule",
      "What we learned that we didn't expect", "The decision, and the next step"],
     ["bet", "ost", "design-sprint", "roadmap"],
     ("Staples subscription · 16 June",
      "Continue to a pilot: 37 of 50 customers (74%) kept the manual subscription for four weeks, above the 70% go rule.",
      [("Go rule", "70% keep it for 4 weeks", "agreed on 14 April"),
       ("Manual test", "74% kept it", "37 of 50 customers"),
       ("Design sprint", "4 of 5 set it up", "but skipping a week was hard"),
       ("Surprise", "skipping matters", "holidays and big shops break the routine"),
       ("Decision", "pilot in Q3", "with skip-a-week; aim for 5,000 subscriptions")],
      "Still to check: the £40k–£70k build cost against margins, with Finance."),
     "Here is our product bet: [paste the hypothesis, the test and the go or stop rule], and the results: [paste figures, "
     "or link the Confluence page or dashboard]. Write a one-page bet review: the hypothesis, what we tested and with "
     "whom, the results against the rule we agreed up front, anything surprising, and a recommendation to continue, "
     "change course or stop, with the next step and its cost. Flag where the evidence is thin.",
     "Judge the result against the rule you set before the test, not one invented afterwards. Moving the goalposts turns a bet into a plan."),

    ("pm", "Outcome status report", "Are we on track, and what do we need from our sponsors?",
     "Sponsors and the steering group", "Every two weeks, or monthly",
     ["A one-line headline and an honest status", "Outcomes against their measures",
      "A forecast as a range, with its assumptions", "Top risks, and the decisions needed"],
     ["status", "forecast", "raid", "stakeholder"],
     ("Reorder made easy · 9 May · Amber",
      "Reorder is live and repeat orders are up; substitutes are one iteration late.",
      [("Weekly repeat orders", "25%", "from 22%; target 30%"),
       ("Forecast", "13–20 June", "29 done, 14 left, scope still growing"),
       ("Campaign date", "30 June", "fixed"),
       ("Top risk", "repeat billing", "in the subscriptions pilot; owned by Payments"),
       ("Dependency at risk", "Stock API", "two weeks late; substitutes wait on it")],
      "Decision needed: the Stock API's priority, agreed with Store Platform (Head of Digital, by 16 May)."),
     "Using the Jira or Azure DevOps project [KEY], the RAID log at [link] and these notes: [paste], draft a one-page "
     "status report for the steering group. Include: a one-line headline and a status (green, amber or red) with the "
     "reason; our outcome measures against their targets; a delivery forecast as a range based on recent throughput, with "
     "its assumptions; what was delivered; the top three risks or issues with owners; and the decisions we need, from "
     "whom, by when.",
     "Don't let the AI soften the message. If it's amber, say so, and say what would make it green."),

    ("program", "Programme roll-up", "Are the teams together moving our shared objectives, and where are they stuck?",
     "Programme sponsors and team leads", "Monthly",
     ["Each shared objective, with its key results", "Progress and confidence for each objective",
      "Cross-team dependencies and risks", "Decisions and escalations"],
     ["okr", "dependency", "sync", "raid"],
     ("Basket group · Q2 · 9 May",
      "Two of three objectives are on track; checkout is behind after the April outage.",
      [("Effortless weekly shop", "on track", "repeat orders 25%, target 30%"),
       ("Nobody forgets an item", "at risk", "substitutes wait on the Stock API"),
       ("Quick, trustworthy checkout", "behind", "drop-off 17%, target 12%"),
       ("Dependencies", "5 across 6 teams", "1 at risk: the Stock API"),
       ("Escalations", "1", "the Stock API, raised at the sync on 6 May")],
      "Ask: agree the Stock API's priority with Store Platform's manager this week."),
     "Using the Jira or Azure DevOps projects [KEYS] and our objectives and key results [paste or link], draft a monthly "
     "programme roll-up. For each objective: the latest key result figures against target, the teams contributing, and "
     "an on track, at risk or behind rating with the reason. Then list the cross-team dependencies that are late or at "
     "risk [from our dependency board or issue links], the top cross-team risks, and the decisions or escalations "
     "needed, with owners.",
     "Roll up outcomes, not activity. Don't compare teams' throughput or velocity: their work isn't the same size."),

    ("rte", "Planning-period progress", "Midway through the planning period, will we meet the objectives we committed to?",
     "The teams, product management and business owners", "Every two weeks in the planning period",
     ["Each team's objectives, and confidence now against confidence at planning", "Dependencies done, due and late",
      "Risks raised at planning, and their status", "What needs to change before the next sync"],
     ["ctp", "sync", "dependency", "cross-retro"],
     ("Five teams · Q2 · 16 May",
      "Confidence has dropped from 4 to 3: one late dependency, the Stock API, is holding up two teams.",
      [("Confidence vote", "3 out of 5", "it was 4 at planning on 1 April"),
       ("Team objectives", "11 of 14 on track", "3 at risk, 2 of them waiting on stock data"),
       ("Dependencies", "3 done, 1 due, 1 late", "late: the Stock API, by two weeks"),
       ("Risks from planning", "4 resolved, 2 open", "repeat billing is still open"),
       ("Release checks", "agreed", "at the sync on 6 May")],
      "Before the next sync: Store Platform confirms a Stock API date; Basket keeps the replica fallback ready (ADR 007)."),
     "Using the Jira or Azure DevOps projects [KEYS] for the teams in our planning period [dates], and the objectives each "
     "team committed to [paste or link], draft a progress report for the next cross-team sync. Include: each team's "
     "objectives with a status; the confidence vote now and at planning [paste both]; cross-team dependencies that are "
     "done, due or late; the risks raised at planning and their status; and the two or three things that need to change "
     "before the next sync, with owners.",
     "Confidence is the teams' call, not the AI's. Ask the teams to vote, and don't let a report guess it from ticket counts."),

    ("portfolio", "Portfolio view", "Are we working on the right things, and not too many at once?",
     "The portfolio board and investment owners", "Monthly or quarterly",
     ["Initiatives by stage, against the WIP limits", "The investment mix: agreed against actual",
      "Value delivered against the expected outcomes", "Proposals to start, stop or change"],
     ["portfolio-kanban", "value", "okr", "right-size"],
     ("Online grocery · 6 May",
      "Twelve initiatives on the board, and the investment mix has drifted away from new bets and tech debt.",
      [("New bets", "10%", "agreed 15%"),
       ("Technical debt", "10%", "agreed 15%"),
       ("Growing what we have", "55%", "agreed 45%"),
       ("Reorder made easy", "on track", "repeat orders 25% of a 30% target"),
       ("Staples subscriptions", "ready to start", "lean case approved; waiting for a team")],
      "Decision: finish or pause one initiative in delivery before starting subscriptions."),
     "Using our portfolio board [link] and the investment mix we agreed [paste], draft a portfolio report. Show: the "
     "number of initiatives at each stage against its WIP limit; the investment mix agreed against actual [from effort, "
     "cost or team allocation: say which]; expected against actual outcomes for initiatives in delivery or recently "
     "finished; and proposals to start, stop or change, with the reasoning for each.",
     "Count started work honestly. Starting more initiatives rarely makes any of them finish sooner."),

    ("leader", "One-page executive brief", "Is the work delivering the outcomes we're paying for, and what do you need from me?",
     "Executives and sponsors", "Monthly",
     ["Outcomes against strategy, in three lines", "The biggest risk, and what's being done",
      "What's changed since last month", "What we need from leadership"],
     ["value", "status", "okr", "portfolio-kanban"],
     ("Basket group · May",
      "Repeat orders are up from 22% to 25% since reorder launched; we need help with one dependency.",
      [("Repeat orders", "25%", "target 30% by the end of June"),
       ("Lead time", "12 days", "target 7; releases wait for sign-off"),
       ("Want subscriptions", "31% of visitors", "a need we don't serve yet; being tested"),
       ("Biggest risk", "Stock API", "two weeks late; substitutes depend on it"),
       ("Ask", "one decision", "the Stock API's priority, by 16 May")],
      "Also watch: Finance's concern about substitute margins; a margin check is in the backlog."),
     "Using these sources [our status reports, OKR updates and value metrics: links or paste], write a one-page brief for "
     "the executive team. Start with a two-sentence summary. Then: progress on our outcomes against strategy, in three "
     "lines at most; the single biggest risk and what's being done about it; what's changed since last month; and up to "
     "three specific asks of leadership, each with a deadline. No jargon, and no ticket-level detail.",
     "The asks matter most. If there are none, say so, rather than inventing work for leaders."),

    ("eng", "Delivery and quality report", "Are we delivering faster and more safely, and where is quality slipping?",
     "Engineering leads and the team", "Monthly",
     ["The four key metrics, with their trends", "Incidents, and reliability against SLOs",
      "Pipeline waits and flaky tests", "Technical debt: what's growing, and what's being paid down"],
     ["delivery-metrics", "cd-health", "slo", "incident"],
     ("Checkout and Basket · 14 May",
      "Faster and more stable since self-service deploys; flaky tests and monitoring are the gaps.",
      [("Deployment frequency", "3 a week", "from 2; aiming for daily"),
       ("Lead time for changes", "7 days", "from 12; aiming for under 2"),
       ("Change failure rate", "12%", "from 18%; aiming for under 10%"),
       ("Time to restore", "4 hours", "from 6; aiming for under 1"),
       ("CD health check", "39 out of 60", "up from 33 in February")],
      "Pay down first: the 6 flaky reorder tests (Ravi, end of Sprint 19) and alerts on payment errors (Platform)."),
     "Using our deployment pipeline [name it], incident tickets in [project KEY] and our SLO dashboard [link], draft a "
     "monthly delivery and quality report for the team. Include: the four key metrics (deployment frequency, lead time "
     "for changes, change failure rate and time to restore) for this month and the last three; incidents, and the error "
     "budget used; where changes wait longest in the pipeline; flaky or slow tests; and the technical debt that grew or "
     "was paid down. Say how each figure was calculated.",
     "These are team and system measures. Never break them down by person, or people will start gaming them."),

    ("ux", "Discovery summary", "What have we learned about users, and what does it change?",
     "The product trio, the team and stakeholders", "After each round of research or testing",
     ["What we set out to learn", "What we did, and with whom", "What we found, with the evidence",
      "What changes in the backlog or design"],
     ["persona", "ost", "cynefin", "design-sprint"],
     ("Substitutes · 12 May",
      "Customers want substitutes they can trust; three small experiments will show what trust means to them.",
      [("Interviews", "12", "weekly shoppers; Sarah, 38, is our persona"),
       ("Wanted one-tap reorder", "31%", "from a fake-door test in February"),
       ("Biggest unknown", "accepting substitutes", "complex, so we'll try things, not plan them"),
       ("Experiments", "3, safe to fail", "same brand, cheaper option, ask first"),
       ("Changes", "2 new stories", "an approve-substitutes step; a margin check")],
      "Next readout: 26 May, after two weeks of the experiments."),
     "Here are my research notes and test results: [paste interview notes, survey results or test data, or link the "
     "Confluence pages]. Write a one-page discovery summary: what we set out to learn; what we did and with whom; the "
     "main findings with the evidence for each, quoting users without names where it helps; how confident we are; and "
     "what this changes in the backlog, design or roadmap. Keep what users did separate from what they said.",
     "The AI will find patterns in anything. Check each finding against the raw notes, and keep “one person said” "
     "apart from “most people did”."),

    ("team", "Weekly flow snapshot", "How is our work flowing this week, and what should we swarm on?",
     "The team, for themselves", "Weekly, before a daily sync",
     ["Items finished this week", "Work in progress against our limits",
      "The oldest items, and any past our SLE", "Blockers, and how long they've waited"],
     ["daily", "ageing", "kanban", "blockers"],
     ("Basket team · week of 5 May",
      "Five items finished; three are past our 9-day SLE, so we swarm on the oldest first.",
      [("Finished this week", "5", "including one-tap reorder"),
       ("In progress", "7", "WIP limit 8"),
       ("Past the 9-day SLE", "3", "oldest: out-of-stock rules, at 12 days"),
       ("Blocked", "2", "Stock API (9 days), Payments sign-off (3 days)"),
       ("Unplanned work", "1 item", "within our 20% buffer")],
      "Swarm today on the out-of-stock rules, and escalate the Stock API at the sync."),
     "Using our board in Jira or Azure DevOps [project KEY and board name], give the team a short flow snapshot for this "
     "week: items finished; work in progress in each column against our WIP limits [paste them]; the five oldest items "
     "in progress with their age in days; any items older than our service level expectation of [N] days; and blocked or "
     "flagged items, with how long each has been blocked. Suggest which item to swarm on first, and why.",
     "This is for the team, not a manager's dashboard. If it's used to judge people, it stops being honest."),
]

_role_ids = [r[0] for r in ROLES]
assert [r[0] for r in REPORTS] == _role_ids, "REPORTS must have one report per role, in ROLES order"
for _r in REPORTS:
    for _k in _r[6]:
        assert _k in TOOLS, f"{_r[1]}: unknown tool {_k}"


def tool_link(k):
    return f'<a href="{TOOLS[k][1]}">{escape(TOOLS[k][0])}</a>'


def card(r, role_name):
    rid, title, question, who, when, contents, keys, (heading, headline, rows, nxt), prompt, watch = r
    full = f"{prompt} {CHECK} {ASK_BACK}"
    table = "".join(f'<tr><th scope="row">{escape(m)}</th><td><b>{escape(v)}</b></td><td>{escape(n)}</td></tr>' for m, v, n in rows)
    return f"""<section class="rp" id="{rid}">
  <p class="role">{escape(role_name)}</p>
  <h2>{escape(title)}</h2>
  <p class="q">“{escape(question)}”</p>
  <div class="cols">
    <div>
      <p class="lbl">Who it's for</p><p>{escape(who)}</p>
      <p class="lbl">How often</p><p>{escape(when)}</p>
      <p class="lbl">What goes in it</p><ul>{"".join(f"<li>{escape(c)}</li>" for c in contents)}</ul>
      <p class="lbl">Draws on</p><p class="tools">{" · ".join(tool_link(k) for k in keys)}</p>
    </div>
    <figure class="ex" aria-label="Example: {escape(title)} for the Basket team">
      <p class="tag">Example · fictional Basket team</p>
      <p class="eh">{escape(heading)}</p>
      <p class="hl">{escape(headline)}</p>
      <table>{table}</table>
      <p class="nx">{escape(nxt)}</p>
    </figure>
  </div>
  <div class="pr">
    <p class="lbl">Prompt to build it</p>
    <pre>{escape(full)}</pre>
    <button type="button" onclick="{escape(COPY_JS)}">Copy prompt</button>
    <p class="watch"><b>Watch out:</b> {escape(watch)}</p>
    <p class="more"><a href="start-here-by-role.html#{rid}">More tools for this role →</a></p>
  </div>
</section>"""


def build():
    names = {rid: name for rid, name, *_ in ROLES}
    nav = "".join(f'<a href="#{r[0]}">{escape(names[r[0]].split(" / ")[0])}</a>' for r in REPORTS)
    cards = "\n".join(card(r, names[r[0]]) for r in REPORTS)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reports by Role</title>
<link rel="stylesheet" href="{FONT_URL}">
<style>
:root{{--accent:{ACCENT};--navy:{NAVY};--ink:#1E293B;--muted:#5B6B82;--rule:#E2E8F0;}}
*{{box-sizing:border-box;}}
html,body{{margin:0;background:#F1F5F9;}}
body{{font-family:'Geist',Inter,system-ui,sans-serif;color:var(--ink);font-size:14px;line-height:1.55;}}
header{{background:var(--navy);border-top:4px solid var(--accent);color:#fff;padding:36px 16px 26px;}}
.wrap{{max-width:1040px;margin:0 auto;padding:0 16px;}}
h1{{font:400 44px/1.05 'Instrument Serif',Georgia,serif;margin:0 0 8px;}}
header p{{color:#94A3B8;margin:0 0 12px;max-width:780px;}}
header p a{{color:#FDBA74;}}
header a.back{{color:#94A3B8;font:500 11px 'Geist Mono',monospace;letter-spacing:.06em;}}
nav.chips{{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px;}}
nav.chips a{{color:#fff;text-decoration:none;font-size:12.5px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:999px;padding:4px 11px;}}
nav.chips a:hover{{background:#C2410C;}}
main{{padding:20px 0 48px;}}
.rules{{background:#FFF7ED;border:1px solid #FED7AA;border-radius:10px;padding:14px 20px;margin:0 0 16px;}}
.rules h2{{font:600 13px 'Geist',sans-serif;margin:0 0 6px;color:#9A3412;}}
.rules ul{{margin:0;padding-left:18px;}}
.rules li{{margin:2px 0;}}
.rp{{background:#fff;border:1px solid var(--rule);border-left:4px solid #0C4A6E;border-radius:10px;padding:18px 22px;margin:0 0 14px;scroll-margin-top:12px;}}
.rp .role{{font:600 9.5px 'Geist Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#0C4A6E;margin:0;}}
.rp h2{{font:400 26px/1.15 'Instrument Serif',Georgia,serif;margin:2px 0 2px;}}
.rp .q{{font:italic 17px/1.35 'Instrument Serif',Georgia,serif;color:#0C4A6E;margin:0 0 10px;}}
.cols{{display:grid;grid-template-columns:5fr 6fr;gap:6px 26px;}}
.cols p{{margin:0;}}
.cols ul{{margin:0;padding-left:18px;}}
.lbl{{font:600 9.5px 'Geist Mono',monospace !important;letter-spacing:.12em;text-transform:uppercase;color:#9A3412;margin:10px 0 3px !important;}}
.tools a{{color:var(--ink);font-weight:500;}}
.ex{{margin:8px 0 0;background:#F8FAFC;border:1px solid var(--rule);border-radius:8px;padding:12px 14px;align-self:start;}}
.ex .tag{{font:600 9px 'Geist Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px;}}
.ex .eh{{font-weight:600;font-size:13px;margin:0;}}
.ex .hl{{font:italic 15.5px/1.35 'Instrument Serif',Georgia,serif;margin:4px 0 8px;}}
.ex table{{width:100%;border-collapse:collapse;font-size:12.5px;}}
.ex th,.ex td{{text-align:left;vertical-align:top;padding:5px 6px;border-top:1px solid var(--rule);}}
.ex th{{font-weight:500;width:36%;}}
.ex td:last-child{{color:var(--muted);}}
@media (min-width:761px){{.ex td:nth-child(2){{white-space:nowrap;}}}}
.ex .nx{{font-size:12.5px;margin:8px 0 0;padding-top:8px;border-top:1px solid var(--rule);}}
.pr{{margin-top:6px;}}
.pr pre{{white-space:pre-wrap;font:12.5px/1.5 'Geist Mono',monospace;background:#F8FAFC;border:1px solid var(--rule);border-radius:6px;padding:10px 12px;margin:0 0 8px;}}
button{{font:500 12.5px 'Geist',system-ui,sans-serif;color:#fff;background:#0C1A2E;border:0;border-radius:999px;padding:6px 13px;cursor:pointer;}}
button:hover{{background:#C2410C;}}
.watch{{margin:10px 0 4px;font-size:13px;}}
.watch b{{color:#9A3412;}}
.more{{margin:0;font-size:13px;}}
.more a{{color:#9A3412;}}
.note{{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:14px 18px;margin-top:22px;font-size:13px;}}
.note a{{color:#9A3412;}}
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#5B6B82;text-align:center;padding:0 16px 32px;}}
@media (max-width:760px){{.cols{{grid-template-columns:1fr;}} .ex th{{width:auto;}}}}
@media print{{header{{padding:16px;}} nav.chips,button{{display:none;}} .rp{{break-inside:avoid;}}}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="index.html">← All tools</a>
  <h1>Reports by Role</h1>
  <p>One report for each role in the <a href="start-here-by-role.html">role guide</a>: the question it answers, who it's for, what goes in it, an example filled in for the fictional <a href="basket-team-story.html">Basket team</a>, and an AI prompt to build it from your Jira, Azure DevOps or Confluence data with Atlassian Rovo, Microsoft Copilot or a similar assistant. More everyday prompts are in the <a href="prompt-library.html">Prompt Library</a>.</p>
  <nav class="chips" aria-label="Roles">{nav}</nav>
</div></header>
<main><div class="wrap">
<div class="rules">
  <h2>Before you send an AI-drafted report</h2>
  <ul>
    <li><b>Check the numbers.</b> AI assistants can miscount or misread fields. Every prompt asks for the query and the counts behind each figure, so check them.</li>
    <li><b>Keep it to teams.</b> Report on teams and outcomes, never individuals, and don't compare teams' velocity.</li>
    <li><b>Use approved tools.</b> Only share work data with AI tools your organisation allows. Assistants built into your tools, such as Rovo in Jira and Confluence or Copilot in Azure DevOps and Microsoft 365, can read the data where it lives; otherwise, export what you need and paste it in.</li>
    <li><b>Make it yours.</b> The AI drafts; you decide what it says. Read it as your audience would before it goes out.</li>
  </ul>
</div>
{cards}
<div class="note"><p>Every figure in the examples comes from the <a href="basket-team-story.html">Basket team's story</a> and its worked examples. Atlassian Rovo, Jira and Confluence are trademarks of Atlassian; Microsoft Copilot and Azure DevOps are trademarks of Microsoft. They're named as examples only. See also the <a href="good-practices.html">Good Practices</a> on measuring teams, not individuals.</p></div>
</div></main>
<footer>{escape(CREDIT)}</footer>
</body>
</html>
"""
    paths.write_page("reports-by-role.html", page)
    print(f"wrote reports-by-role.html ({len(REPORTS)} reports)")


if __name__ == "__main__":
    build()
