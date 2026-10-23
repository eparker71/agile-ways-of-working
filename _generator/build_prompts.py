#!/usr/bin/env python3
"""Generate prompt-library.html: AI prompts for everyday agile work, plus every board's whiteboard prompt in one place.

PROMPTS below is the content: (id, home page section id, title, when to use it, prompt, watch-out, [tool keys]). Tool
keys come from TOOLS in build_roles.py; section ids are the <h2 id> sections of index.html. Each prompt gets the same
closing line (ASK_BACK) added here, so the data doesn't repeat it. The whiteboard section reads each guide's prompt
with guide_spec() from build_guides.py, so it stays in step with the boards.

Run:  python3 _generator/build_prompts.py
"""
import re
import sys
from html import escape, unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (where each file lives; see paths.py)
from build_roles import TOOLS, FONT_URL  # noqa: E402
from build_guides import GUIDES, guide_spec  # noqa: E402
from board_spec import spec as board_spec  # noqa: E402
from brand import ACCENT, NAVY, CREDIT, SITE  # noqa: E402

OUT = Path(__file__).resolve().parent.parent

ASK_BACK = "List any assumptions you made, and ask me questions if anything is unclear."

PROMPTS = [
    # set up the team
    ("charter", "setup", "Draft working agreements",
     "After a team discussion about how you want to work together.",
     "Here are notes from our team's discussion about how we want to work together: [paste notes]. Draft 6 to 8 working "
     "agreements. Write each as a short, positive behaviour we can see (for example \"We review pull requests within one "
     "working day\"), not a value or a wish. Keep our own words where you can, and flag any agreements that contradict "
     "each other.",
     "Agreements only work if the team writes and owns them. Use this as a first draft to edit together.",
     ["team-charter"]),
    ("manual", "setup", "Turn notes into a personal user manual",
     "When someone wants to share how they like to work, but finds it hard to write.",
     "Here are my rough notes about how I like to work: [paste notes]. Turn them into a short personal user manual with "
     "these headings: I do my best work when…, The best way to reach me is…, Give me feedback by…, What drains me and what "
     "energises me, Things people misread about me, and Ask me about…. Keep it under 200 words, in the first person and "
     "my own voice.",
     "Share only what you're comfortable sharing. It's yours to edit.",
     ["user-manual"]),
    ("onboarding", "setup", "Plan a new joiner's first week",
     "A week or two before someone joins the team.",
     "[Name] is joining our team as a [role] on [start date]. Our team [one line on what the team does]. Plan their first "
     "week, one theme a day: meeting people and getting set up, the product and its users, pairing on a small piece of "
     "work, joining our events, and finishing something small. For each day, suggest who they should meet and one thing "
     "they should finish.",
     "A plan, not a firehose. Leave room for questions and for the person's own priorities.",
     ["onboarding"]),
    # decide what to build
    ("bet", "decide", "Turn an idea into a product bet",
     "When an idea is gaining support before anyone has tested it.",
     "Here's an idea for our product: [describe the idea]. Rewrite it as a one-sentence bet: \"We believe that [who] will "
     "[do what] if we [offer what], because [what we know].\" Then list the riskiest assumptions under value, usability, "
     "feasibility and viability, and suggest the cheapest test for the riskiest one.",
     "The AI doesn't know your customers. Treat its assumptions as a starting list, then test them with real people.",
     ["bet"]),
    ("interview", "decide", "Write customer interview questions",
     "Before talking to customers about a problem.",
     "We want to understand this problem: [describe the problem and who has it]. Write 8 interview questions that ask "
     "about real past behaviour (\"Tell me about the last time…\"), not opinions or hypothetical futures. Avoid leading "
     "questions and don't mention our solution. Add two follow-up prompts for going deeper.",
     "Good interviews listen more than they ask. Don't read the questions out like a survey.",
     ["ost", "persona"]),
    ("insights", "decide", "Summarise interview notes",
     "After a round of customer interviews.",
     "Here are notes from [number] customer interviews: [paste notes, with names removed]. Summarise them into: the jobs "
     "people are trying to get done, their main pains, what they do today instead, and three or four short quotes that "
     "capture each theme. Say how many interviews support each theme, and note anything only one person said.",
     "Remove names and personal details first. Check the themes against the notes yourself.",
     ["persona", "ost"]),
    ("outcomes", "decide", "Rewrite features as outcomes",
     "When a roadmap or plan is a list of features and dates.",
     "Here is our list of planned features: [paste list]. For each one, suggest the outcome it's meant to achieve (what "
     "will be different for users or the business), and a measure that would show it worked. Group features that serve "
     "the same outcome, and flag any where the outcome is unclear.",
     "If nobody can name the outcome for a feature, that's a finding, not a gap for the AI to fill.",
     ["vision", "okr", "roadmap"]),
    ("rank", "decide", "Compare options by cost of delay",
     "When several items compete for the next slot.",
     "Here are the options we're choosing between, with what we know about each: [paste options]. For each, estimate "
     "user or business value, time criticality, and risk reduction on a 1, 2, 3, 5, 8, 13 scale, plus a rough size. "
     "Calculate cost of delay divided by size, rank them, and explain the ranking in plain words.",
     "The numbers are a conversation starter. The team's judgement, and what it knows about context, decides.",
     ["prioritisation"]),
    # break down work
    ("story", "breakdown", "Turn a request into a user story",
     "When a request arrives as a sentence in a chat or an email.",
     "Here's a request we've received: [paste request]. Write it as a user story (As a…, I want…, so that…), with 3 to 6 "
     "acceptance criteria written as concrete examples. Note what's out of scope, and list the questions we need answered "
     "before it's ready to build.",
     "Check who the user really is. The AI will guess if the request doesn't say.",
     ["backlog", "example"]),
    ("split", "breakdown", "Split a large story",
     "When a story is too big to finish in a few days.",
     "This story is too big for our team to finish in a few days: [paste story and criteria]. Suggest 3 to 6 ways to split "
     "it into thin, vertical slices that each deliver something a user could see or use. Use patterns such as workflow "
     "steps, business rules, data variations or simple first, then more. Recommend which slice to build first, and why.",
     "Avoid splits by technical layer (\"front end\", \"database\"). Each slice should be usable on its own.",
     ["splitting"]),
    ("examples", "breakdown", "Generate rules, examples and questions",
     "Before an Example Mapping session, or when a story feels fuzzy.",
     "Here's a user story: [paste story]. List the business rules it involves. Under each rule, give two or three concrete "
     "examples, including edge cases. Then list the open questions nobody has answered yet. If there are more than four "
     "rules, suggest splitting the story by rule.",
     "Use it to prepare, not to replace the conversation. The value of Example Mapping is the shared understanding.",
     ["example"]),
    ("epic", "breakdown", "Break down an epic",
     "When a large initiative needs shaping before work starts.",
     "Here's an epic: [describe it]. Write it as a hypothesis (For… who… the… is a… that… unlike… our solution…). "
     "Suggest the outcome and a leading indicator, the smallest version that would test the hypothesis, and three to five "
     "features that each deliver value on their own. Mark which features belong in the first version.",
     "Keep the first version small enough to learn from quickly. The AI tends to include too much.",
     ["epic", "storymap"]),
    # run events
    ("goal", "iterate", "Draft a sprint goal",
     "During planning, once the team has a rough selection of items.",
     "These are the items our team is considering for the next iteration: [paste items]. Our product goal is [goal]. "
     "Suggest two or three possible sprint goals: one sentence each, about an outcome for users rather than a list of "
     "tasks. For each, say which items support it, and which items don't fit.",
     "The team should agree the goal. Pick, edit or reject these together.",
     ["sprint-planning"]),
    ("review", "iterate", "Plan a review with stakeholders",
     "A few days before an iteration review.",
     "Our iteration review is [length] long. We finished: [list items]. Our goal was [goal], and the key measures are "
     "[measures]. Stakeholders attending: [who]. Draft an agenda with timings that shows working product rather than "
     "slides, makes room for feedback, and ends with what the review changes in the backlog. Suggest three questions to "
     "ask stakeholders.",
     "A review is a conversation, not a demo. Keep most of the time for feedback.",
     ["sprint-review"]),
    ("standup", "iterate", "Tighten a stand-up that runs long",
     "When the daily sync regularly overruns or turns into status reporting.",
     "Our daily sync is meant to take 15 minutes but often takes [time]. Here's what usually happens: [describe it]. "
     "Suggest five specific changes to make it shorter and more useful, such as walking the board right to left. For "
     "each, explain the problem it solves.",
     "Try one or two changes at a time, and check at the retro whether they helped.",
     ["daily"]),
    # manage flow
    ("blockers", "flow", "Group blockers by cause",
     "When the same kinds of blockers keep coming back.",
     "Here's our list of blockers from the last [period], with how many days each lasted: [paste list]. Group them into "
     "clusters by underlying cause (not by who caused them), total the blocked days for each cluster, and suggest one "
     "change that would tackle the biggest cluster.",
     "Blame the system, not people. Remove names before pasting.",
     ["blockers", "impediments"]),
    ("wip", "flow", "Suggest WIP limits and exit policies",
     "When designing or redesigning a Kanban board.",
     "Our team has [number] people. Our workflow columns are: [list columns]. Typically there are [number] items in each "
     "column. Suggest a starting WIP limit for each column and an explicit exit policy (when an item is done with that "
     "column). Explain your reasoning, and say what to watch to know if a limit is too tight or too loose.",
     "WIP limits are an experiment. Start a little tight, and review them after a few weeks.",
     ["kanban", "ageing"]),
    ("waste", "flow", "Find waste in a process",
     "Before a Waste Walk or Value Stream Map, or when work feels slow.",
     "Here's how work moves through our process, step by step, with rough times: [describe the steps]. Identify likely "
     "waste under the eight lean wastes (hand-offs, partly done work, task switching, waiting, features nobody uses, "
     "over-processing, defects, unused skills). Estimate which costs most, and suggest one change to try first.",
     "The AI only sees what you describe. Go and see the real work before acting on its guesses.",
     ["waste", "vsm", "lean"]),
    ("cycletime", "flow", "Explain cycle-time data",
     "When sharing flow data with people who don't use it every day.",
     "Here are the cycle times, in days, of our last [number] finished items: [paste numbers]. Work out the 50th, 70th and "
     "85th percentiles. Explain in plain words what they mean for someone asking \"when will my item be done?\", and "
     "suggest a service level expectation. Note any outliers worth looking at.",
     "Check the arithmetic. AIs can get percentiles wrong, so a spreadsheet is a good cross-check.",
     ["ageing", "forecast"]),
    # engineering practices
    ("adr", "engineering", "Draft an architecture decision record",
     "After the team has discussed a significant technical decision.",
     "Here are notes from our discussion about [decision]: [paste notes]. Draft an architecture decision record with: a "
     "title, context (the problem and constraints), decision drivers, at least two options considered (including doing "
     "nothing) with pros and cons, the decision, and its consequences: what becomes easier and what becomes harder.",
     "The record must reflect what the team actually decided and why. Correct anything the AI has smoothed over.",
     ["adr"]),
    ("tests", "engineering", "List test ideas and edge cases",
     "When refining a story, or before testing starts.",
     "Here's a feature and its acceptance criteria: [paste]. List test ideas grouped by happy path, edge cases, error "
     "handling, accessibility, security and performance. Highlight the five riskiest cases, and say which level of the "
     "test pyramid (unit, integration, end to end, or exploratory) suits each.",
     "Use it to widen your thinking, not as the test plan. Testers' knowledge of the system matters more.",
     ["testing"]),
    ("release", "engineering", "Draft a go / no-go checklist and rollback plan",
     "A week or so before a significant release.",
     "We're releasing [what] to [who] on [date], using [approach, e.g. a feature flag or canary]. Draft a go / no-go "
     "checklist, a rollback plan (how we'd know it's going wrong, how we'd undo it, how long that takes, and what can't be "
     "undone), and a list of who needs to know what, and when.",
     "Test the rollback before release day. A plan nobody has tried isn't a plan.",
     ["release"]),
    ("incident", "engineering", "Write a blameless incident timeline",
     "Before a post-incident review.",
     "Here are notes and chat messages from an incident: [paste, with names replaced by roles]. Build a timeline with: "
     "time, what happened, what people knew at that point, and what they did and why. Use neutral, blameless language. "
     "Then list possible contributing factors under technology, process, knowledge, environment and communication.",
     "Replace names with roles first. Contributing factors are for the review to agree, not the AI to decide.",
     ["incident"]),
    # reflect & improve
    ("retro-themes", "improve", "Group retro notes into themes",
     "After a retro with a lot of stickies, or a remote retro with typed notes.",
     "Here are the notes from our retrospective: [paste notes]. Group them into themes, and say how many notes each theme "
     "has. For the top three themes, suggest one specific action each, with a suggested owner role and a \"done when\" "
     "we could check by the next retro.",
     "The team chooses the actions. Use the themes to speed up sorting, not to skip the discussion.",
     ["retro"]),
    ("retro-fresh", "improve", "Freshen up a stale retro",
     "When retros have started to feel the same every time.",
     "Our team of [number] has been running the same retro format for [time], and it's gone stale. Recently we've been "
     "struggling with [topic]. Suggest five different retro formats or activities that would fit, each with a short "
     "description, timings for [length], and why it might help.",
     "Stale retros are often a sign that actions aren't being followed up. Check that first.",
     ["retro", "facilitation"]),
    ("whys", "improve", "Run five whys on a problem",
     "When a problem keeps coming back.",
     "This problem keeps happening: [describe it, with facts and examples]. Ask \"why?\" five times to work towards a root "
     "cause, writing down each answer. Then challenge the chain: point out any link that is a guess rather than a fact, "
     "and suggest one or two other branches worth exploring.",
     "Root causes are about the system, never a person. Check each link with real evidence.",
     ["rootcause", "a3"]),
    ("experiment", "improve", "Turn an idea into an experiment",
     "When someone suggests an improvement at a retro.",
     "Our team wants to try this improvement: [describe it]. The problem it's meant to fix is [problem]. Turn it into a "
     "small experiment: a hypothesis (If we…, for…, then we expect…, we'll know when we see…), a baseline and a target, "
     "a measure, a guardrail (what mustn't get worse), and a timebox of one or two iterations.",
     "Keep it small enough to start tomorrow.",
     ["experiment", "marginal"]),
    # run a project
    ("premortem", "project", "Run a pre-mortem",
     "At the start of a project or before a big milestone.",
     "Imagine it's [date] and our project, [describe it], has failed badly. List 15 plausible reasons why, in the past "
     "tense, grouped into themes such as people, technology, customers, money, dependencies and decisions. Then pick the "
     "five most likely, and for each suggest a way to prevent it and an early warning sign.",
     "The team's own fears matter more than the AI's list. Use it after the team has written its own.",
     ["premortem", "raid"]),
    ("status", "project", "Draft an outcome-based status report",
     "When writing a regular update for sponsors or a steering group.",
     "Here are this period's raw updates from the team: [paste updates]. Draft a one-page status report with: a one-line "
     "headline, outcomes against their measures, a forecast as a range with its assumptions, what was delivered and "
     "learned, the top three risks or issues with owners, and the decisions we need, from whom, by when.",
     "Don't let the AI turn amber into green. The report must be honest about problems.",
     ["status", "forecast"]),
    ("raid", "project", "Build a first RAID log",
     "At the start of a project.",
     "Here's our project brief: [paste brief]. Draft a first RAID log: risks (with likelihood, impact and a response), "
     "assumptions (and how we'd test each), current issues, and dependencies (who needs what from whom, and by when). "
     "Note which items need an owner from outside the team.",
     "The log is only useful if it's reviewed regularly and every item has an owner.",
     ["raid"]),
    ("stakeholders", "project", "Map stakeholders",
     "At the start of a project, or when someone important seems unhappy.",
     "Our project is [describe it]. Here are the people and groups involved: [list them, with what you know]. Place each "
     "on an influence and interest grid, say what each wants or worries about, and suggest how and how often to engage "
     "them. Then suggest who might be missing from the list.",
     "Keep personal judgements about named people out of shared tools.",
     ["stakeholder"]),
    # coordinate teams
    ("dependencies", "teams", "Find hidden dependencies across teams",
     "Before or during cross-team planning.",
     "Here are the plans for the next [period] from these teams: [paste each team's plan]. Find the dependencies between "
     "them: who needs what from whom, and by when. Flag ones that look late or at risk, and suggest which could be removed "
     "rather than managed, for example by reordering work or using a stub.",
     "The AI can only see dependencies that are written down. Ask the teams what's missing.",
     ["dependency", "ctp"]),
    # lead the organisation
    ("change", "lead", "Explain a change to the people affected",
     "Before announcing a change to how people work.",
     "We're changing [what's changing] for [who's affected], starting [when]. Draft a short message that explains why the "
     "change is needed now, what it means for them day to day, what's staying the same, what support they'll get, and "
     "how they can ask questions or raise concerns. Plain, honest language, under 250 words.",
     "A message is only the start. People also need to be heard. Follow up in person.",
     ["adkar"]),
    ("cynefin", "lead", "Sort situations into Cynefin® domains",
     "When a group disagrees about how to approach a problem.",
     "Here are the situations our team is facing: [list them]. Using the Cynefin® framework's domains (clear, "
     "complicated, complex, chaotic, and confused), suggest which domain each belongs in and why. For the complex ones, "
     "suggest two or three safe-to-fail experiments, with signs that one is working and signs to stop.",
     "The value is in the group's discussion of where things belong. Use the AI's view as one voice in it.",
     ["cynefin"]),
    # facilitate & coach
    ("coaching", "facilitate", "Prepare coaching questions",
     "Before a coaching conversation.",
     "I'm coaching someone who wants to [their goal, in their words]. Using the GROW model (goal, reality, options, will), "
     "suggest three open questions for each stage. Avoid questions that hide advice (\"Have you thought about…?\"). Add "
     "two questions to check their commitment at the end.",
     "Questions are a guide. Follow the person, not the list.",
     ["coaching"]),
    ("workshop", "facilitate", "Plan a workshop",
     "When you need to design a session from scratch.",
     "I'm running a [length] workshop for [who, and how many] to [purpose]. By the end we need [outcome]. Design it: an "
     "agenda with timings, a technique for each part (for example 1-2-4-All, dot voting, silent writing), what to prepare, "
     "and how to make sure quieter people are heard. Include a check-in and a close.",
     "Build in more time than you think. Workshops nearly always run long.",
     ["facilitation", "lean-coffee"]),
]

INDEX = paths.read_index()
SECTIONS = [(sid, unescape(re.sub(r"<[^>]+>", "", name))) for sid, name in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', INDEX)]
_ids = [p[0] for p in PROMPTS]
assert len(_ids) == len(set(_ids)), "duplicate prompt id"
for pid, sec, title, *_r, keys in PROMPTS:
    assert sec in dict(SECTIONS), f"{title}: unknown home page section {sec}"
    for k in keys:
        assert k in TOOLS, f"{title}: unknown tool {k}"

COPY_JS = ("(function(b){var t=b.parentNode.querySelector('pre').textContent;navigator.clipboard.writeText(t).then("
           "function(){var o=b.textContent;b.textContent='Copied ✓';setTimeout(function(){b.textContent=o},2000)})})(this)")


def tool_link(k):
    return f'<a href="{TOOLS[k][1]}">{escape(TOOLS[k][0])}</a>'


def prompt_card(pid, title, when, text, watch, keys):
    full = f"{text} {ASK_BACK}"
    search = " ".join([title, when, text, watch] + [TOOLS[k][0] for k in keys]).lower()
    return (f'<div class="pc" id="{pid}" data-text="{escape(search)}"><h3>{escape(title)}</h3>'
            f'<p class="when">{escape(when)}</p><pre>{escape(full)}</pre>'
            f'<button type="button" onclick="{escape(COPY_JS)}">Copy prompt</button>'
            f'<p class="watch"><b>Watch out:</b> {escape(watch)}</p>'
            f'<p class="pairs">Pairs with: {" · ".join(tool_link(k) for k in keys)}</p></div>')


def whiteboard_rows():
    rows = []
    for g in GUIDES:
        text = guide_spec(g)
        if text:
            rows.append((re.sub(r" Guide$", "", g["title"]), f"facilitator-guide-{g['slug']}.html#whiteboard", text))
    mg = paths.path("marginal-gains-workshop-board.svg")  # hand-written board and guide, not in GUIDES
    rows.append(("Marginal Gains Workshop", "facilitator-guide-marginal-gains.html",
                 board_spec(mg, f"https://{SITE}/{paths.site_path('marginal-gains-workshop-board.html')}")))
    return sorted(rows, key=lambda r: r[0].lower())


def build():
    groups = {}
    for pid, sec, title, when, text, watch, keys in PROMPTS:
        groups.setdefault(sec, []).append(prompt_card(pid, title, when, text, watch, keys))
    present = [(sid, name) for sid, name in SECTIONS if sid in groups]
    chips = "".join(f'<a href="#p-{sid}">{escape(name)}</a>' for sid, name in present) + '<a href="#whiteboards">Rebuild a board</a>'
    sections = "\n".join(f'<section class="grp" id="p-{sid}"><h2>{escape(name)} <span>{len(groups[sid])}</span></h2>'
                         f'<div class="grid">{"".join(groups[sid])}</div></section>' for sid, name in present)
    wb = whiteboard_rows()
    wb_rows = "".join(f'<li data-text="{escape(t.lower())}"><span class="wt">{escape(t)}</span><a href="{href}">Guide</a>'
                      f'<button type="button" onclick="{escape(COPY_JS)}">Copy prompt</button><pre hidden>{escape(spec)}</pre></li>'
                      for t, href, spec in wb)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prompt Library</title>
<link rel="stylesheet" href="{FONT_URL}">
<style>
:root{{--accent:{ACCENT};--navy:{NAVY};--ink:#1E293B;--muted:#5B6B82;--rule:#E2E8F0;}}
*{{box-sizing:border-box;}}
html,body{{margin:0;background:#F1F5F9;}}
body{{font-family:'Geist',Inter,system-ui,sans-serif;color:var(--ink);font-size:14px;line-height:1.55;}}
header{{background:var(--navy);border-top:4px solid var(--accent);color:#fff;padding:36px 16px 26px;}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 16px;}}
h1{{font:400 44px/1.05 'Instrument Serif',Georgia,serif;margin:0 0 8px;}}
header p{{color:#94A3B8;margin:0 0 14px;max-width:760px;}}
header p a{{color:#FDBA74;}}
header a.back{{color:#94A3B8;font:500 11px 'Geist Mono',monospace;letter-spacing:.06em;}}
input{{font:14px 'Geist',system-ui,sans-serif;padding:8px 12px;border-radius:6px;border:1px solid #334155;background:#0F2236;color:#fff;width:100%;max-width:360px;margin-bottom:12px;}}
input::placeholder{{color:#64748B;}}
nav.chips{{display:flex;flex-wrap:wrap;gap:8px;}}
nav.chips a{{color:#fff;text-decoration:none;font-size:12.5px;border:1px solid #334155;border-radius:999px;padding:5px 12px;background:#0F2236;}}
nav.chips a:hover{{border-color:var(--accent);}}
main{{padding:20px 0 48px;}}
.care{{background:#FFF7ED;border:1px solid #FED7AA;border-left:4px solid #C2410C;border-radius:8px;padding:14px 18px;font-size:13px;}}
.care b{{color:#9A3412;}}
.care ul{{margin:6px 0 0;padding-left:18px;}}
.care a{{color:#9A3412;}}
h2{{font:500 11px 'Geist Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:28px 0 10px;scroll-margin-top:12px;}}
h2 span{{margin-left:6px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;}}
.pc{{background:#fff;border:1px solid var(--rule);border-top:4px solid #1E3A8A;border-radius:8px;padding:14px 16px;display:flex;flex-direction:column;}}
.pc h3{{margin:0 0 4px;font-size:15.5px;}}
.pc .when{{margin:0 0 8px;color:var(--muted);font-size:12.5px;}}
.pc pre{{white-space:pre-wrap;font:12.5px/1.5 'Geist Mono',monospace;background:#F8FAFC;border:1px solid var(--rule);border-radius:6px;padding:10px 12px;margin:0 0 8px;flex:1;}}
button{{align-self:flex-start;font:500 12.5px 'Geist',system-ui,sans-serif;color:#fff;background:#0C1A2E;border:0;border-radius:999px;padding:6px 13px;cursor:pointer;}}
button:hover{{background:#C2410C;}}
.pc .watch{{margin:10px 0 4px;font-size:12.5px;}}
.pc .watch b{{color:#9A3412;}}
.pc .pairs{{margin:0;font-size:12px;color:var(--muted);}}
.pc .pairs a{{color:var(--ink);}}
.wb{{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:14px 18px;}}
.wb p{{margin:0 0 10px;font-size:13px;}}
.wb ul{{list-style:none;margin:0;padding:0;columns:2;column-gap:28px;}}
.wb li{{display:flex;align-items:center;gap:10px;padding:5px 0;border-bottom:1px solid var(--rule);break-inside:avoid;}}
.wb .wt{{flex:1;font-size:13px;}}
.wb li a{{font-size:12px;color:var(--muted);}}
.wb button{{padding:4px 10px;font-size:12px;}}
.hidden{{display:none !important;}}
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#5B6B82;text-align:center;padding:0 16px 32px;}}
@media (max-width:700px){{.wb ul{{columns:1;}}}}
@media print{{header{{padding:16px;}} input,nav.chips,button{{display:none;}} .pc{{break-inside:avoid;}}}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="index.html">← All tools</a>
  <h1>Prompt Library</h1>
  <p>{len(PROMPTS)} prompts for everyday agile work, grouped like the toolkit, each paired with the board it supports. They work with any AI assistant, such as ChatGPT, Claude, Copilot or Atlassian Rovo: copy one, fill in the [square brackets], and paste it in. Further down, every board's whiteboard prompt is in one place. For reports, such as an iteration report or an executive brief, see <a href=\"reports-by-role.html\">Reports by Role</a>.</p>
  <input type="search" placeholder="Search prompts, e.g. “retro” or “story”…" aria-label="Search prompts">
  <nav class="chips" aria-label="Sections">{chips}</nav>
</div></header>
<main><div class="wrap">
<div class="care"><b>Use it responsibly.</b><ul>
<li>Don't paste confidential, customer or personal data into tools your organisation hasn't approved. Replace names with roles.</li>
<li>A person reviews everything before it's used. AI makes confident mistakes, so check facts and numbers.</li>
<li>Use AI to prepare and to speed things up, not to replace the team's conversation or decisions.</li>
<li>Agree how your team uses AI with the <a href="ai-working-agreement-board.html">AI Working Agreement</a>.</li></ul></div>
{sections}
<section id="whiteboards"><h2>Rebuild a board in your whiteboard <span>{len(wb)}</span></h2>
<div class="wb"><p>Each prompt recreates one board as an editable, native whiteboard in Miro AI, Atlassian Rovo or a general assistant. Results vary by tool, so expect to tidy it up. The same prompts are in each facilitator guide.</p>
<ul>{wb_rows}</ul></div></section>
</div></main>
<footer>{escape(CREDIT)}</footer>
<script>
(function(){{
  var input=document.querySelector('input');
  input.addEventListener('input', function(){{
    var q=input.value.trim().toLowerCase();
    document.querySelectorAll('.grp').forEach(function(sec){{
      var any=false;
      sec.querySelectorAll('.pc').forEach(function(c){{
        var ok=!q || c.dataset.text.indexOf(q)>=0; c.classList.toggle('hidden', !ok); if(ok) any=true;
      }});
      sec.classList.toggle('hidden', !any);
    }});
    document.querySelectorAll('.wb li').forEach(function(li){{
      li.classList.toggle('hidden', !!q && li.dataset.text.indexOf(q)<0);
    }});
  }});
}})();
</script>
</body>
</html>
"""
    paths.write_page("prompt-library.html", page)
    print(f"wrote prompt-library.html ({len(PROMPTS)} prompts, {len(wb)} whiteboard prompts)")


if __name__ == "__main__":
    build()
