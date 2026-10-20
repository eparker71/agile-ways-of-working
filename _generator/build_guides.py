#!/usr/bin/env python3
"""Generate the A4 facilitator guides that accompany each board.

Styling is taken from facilitator-guide-marginal-gains.html (the hand-written
original), so every guide shares one look. Content lives in GUIDES below.

Run:  python3 _generator/build_guides.py      (writes into the parent folder)
"""
import re
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import ACCENT, NAVY, CREDIT, SITE, AUTHOR, FONT_URL as _FONT_URL  # noqa: E402  (edit brand.py to rebrand)
from docx_writer import Doc  # noqa: E402
from board_spec import spec as board_spec  # noqa: E402
FONT_URL = _FONT_URL.replace("&", "&amp;")

BLUE, EMERALD, PURPLE, ORANGE = ("#1E3A8A", "#DBEAFE"), ("#065F46", "#D1FAE5"), ("#581C87", "#EDE9FE"), ("#9A3412", "#FFEDD5")
RED, AMBER, FOREST, SKY = ("#991B1B", "#FEE2E2"), ("#92400E", "#FEF3C7"), ("#14532D", "#DCFCE7"), ("#0C4A6E", "#E0F2FE")
SLATE = ("#334155", "#F1F5F9")

EXTRA_CSS = """
.boards{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 0;}
.boards a{font:500 10.5px var(--mono);letter-spacing:.04em;color:#fff;text-decoration:none;border:1px solid #334155;border-radius:6px;padding:5px 10px;}
.boards a.primary{background:var(--accent);border-color:var(--accent);}
.content a{color:#9A3412;}
.example{border:1px solid var(--rule);border-radius:8px;overflow:hidden;margin:10px 0;}
.example div{display:grid;grid-template-columns:30% 1fr;border-bottom:1px solid var(--rule);}
.example div:last-child{border-bottom:none;}
.example b{background:#F8FAFC;padding:7px 12px;font:600 9px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);}
.example span{padding:7px 12px;font-size:12.5px;}
@media (max-width:640px){.example div{grid-template-columns:1fr;}}
@media print{.boards{display:none;}}
"""

RETRO_TOOLKIT = ("Feed experiment results from the <a href=\"experiment-canvas.html\">1% Experiment Canvas</a> into each retro, "
                 "and rotate formats (<a href=\"facilitator-guide-retro-start-stop-continue.html\">Start · Stop · Continue</a>, "
                 "<a href=\"facilitator-guide-retro-4ls.html\">4 Ls</a>, <a href=\"facilitator-guide-retro-mad-sad-glad.html\">Mad · Sad · Glad</a>, "
                 "<a href=\"facilitator-guide-retro-sailboat.html\">Sailboat</a>) so conversations stay fresh. "
                 "If the same theme keeps coming back, it is a system issue: take it to a "
                 "<a href=\"facilitator-guide-marginal-gains.html\">Marginal Gains Workshop</a>.")


# ------------------------------------------------------------------ shared retro content

def retro_agenda(write_note, discuss_note, extra_first=None):
    rows = [("0–5", "0–10", "Set the stage",
             "Read the Prime Directive (“everyone did the best job they could…”). Review last time's actions and any experiment results."),
            *( [extra_first] if extra_first else [] ),
            (("8–15", "15–30") if extra_first else ("5–15", "10–30")) + ("Silent writing", write_note),
            ("15–25", "30–50", "Read out & cluster", "Each person places and briefly reads their stickies. Group duplicates and name each cluster."),
            ("25–30", "50–60", "Dot vote", "3 dots each on the clusters that most deserve discussion."),
            ("—", "60–70", "Break", "Quarter format only."),
            ("30–48", "70–100", "Discuss", discuss_note),
            ("48–57", "100–112", "Agree actions", "Choose up to 3 actions for the strip at the bottom. Each needs an <b>owner</b> and a clear <b>done when</b>. Bigger ideas go on a 1% Experiment Canvas."),
            ("57–60", "112–120", "Close", "Read back the actions, then a quick ROTI (return on time invested, 1–5 fingers)."),
            ]
    return rows


RETRO_BEFORE = [
    "Print the board at A3, or load the SVG into Miro / Mural / FigJam. Write the period on the actions strip (sprint, month or quarter); allow about 60 min for a sprint and 2 h for a quarter",
    "Yellow and green stickies, markers, dot stickers (3 per person)",
    "Bring the actions from the last retro and their status",
    "Have data to hand: velocity or throughput, cycle time, escaped defects, any experiment results",
    "For quarter retros, invite key stakeholders and bring trends across the sprints",
    "Make sure the room (or call) is the team only, unless the team agrees otherwise",
]

RETRO_TIPS = [
    ("Write before you talk", "Silent writing gets every voice on the wall before the loudest voice sets the direction."),
    ("Systems, not people", "Ask “what made that hard?” instead of “who did that?”. Protect psychological safety at all times."),
    ("Fewer, better actions", "One action that gets done beats five that don't. Cap it at three, and check last time's actions before adding more."),
    ("Make actions visible", "Put actions on the team board or backlog, so they compete for capacity like any other work."),
    ("Quarter = zoom out", "In the quarter format, look for patterns across sprints and things outside the team's control that need escalating."),
    ("Vary the format", "The same retro every time leads to the same answers. Rotate formats every few sprints."),
]

RETRO_PITFALLS = ("actions with no owner; repeating the same complaints without asking why previous actions failed; "
                  "jumping to solutions during silent writing; letting one topic eat the whole timebox; managers in the room "
                  "who make people hold back.")

RETRO_AFTER = [
    ("Within 24 hours", "Photograph or export the board. Add each action to the team backlog with its owner, and share a short summary."),
    ("During the sprint / quarter", "Check actions at stand-up or in the weekly sync. Unblock early rather than reporting failure at the next retro."),
    ("At the next retro", "Open by reviewing each action: done, in progress, or dropped, and why. Celebrate the ones that worked."),
    ("Running remotely", "Lock the SVG as a background, pre-create sticky stacks in both colours, use built-in voting and a visible timer."),
]


GUIDES = [
    # -------------------------------------------------------------- team health check
    dict(
        slug="team-health-check",
        title="Team Health Check Guide",
        subtitle="How to run a team health check, read the results, and turn them into improvement.",
        tag="Facilitator Run-Sheet · Inspired by the Spotify Squad Health Check · Team & Facilitator Tool",
        boards=[("Open board", "team-health-check-board.html"), ("SVG", "team-health-check-board.svg")],
        lede="How healthy is our team right now, and which way is it trending?",
        intro=("The health check gives a team a structured, safe way to talk about how things really are across eleven "
               "dimensions, from delivering value to teamwork. It is a <b>conversation tool for the team</b>, not a "
               "management scorecard. Its value comes from discussing the votes and repeating the check every quarter so trends show up."),
        glance=[("Duration", "45–60 min"), ("Group", "One team<br>5–10 people"), ("Cadence", "Every quarter<br>or planning cycle"),
                ("Output", "1–2 focus areas<br>&amp; trend")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Green, amber and red dot stickers: one of each colour per person per dimension (or coloured cards for silent voting)",
                "Bring the previous health check so you can set the trend arrows",
                "Agree with the team who sees the results, and keep it within the team by default",
                "Pre-read each dimension's healthy and unhealthy description, and adapt the wording if your team uses different language",
                "Prepare a few copies of the 1% Experiment Canvas"],
        agenda_heads=["Time", "Activity", "Facilitator notes"],
        agenda=[("0–5", "Frame it", "Explain the purpose: an honest snapshot for the team, not a performance review. There are no wrong answers."),
                ("5–12", "Walk the dimensions", "Read each dimension and its healthy / unhealthy examples. Clarify meaning, but don't debate it yet."),
                ("12–22", "Vote", "Each person places one dot per row: green, amber or red. For more anonymity, vote with cards first and then place the dots."),
                ("22–27", "Set the trend", "Compare with last time and circle ↑ → ↓ for each row. If this is the first check, leave it for next time."),
                ("27–47", "Discuss", "Start with the reddest rows and rows where votes are split. Ask “What makes this red for you?” and capture notes in the right column."),
                ("47–57", "Pick focus areas", "Dot-vote or agree on 1–2 rows to improve. Start a 1% Experiment Canvas for each."),
                ("57–60", "Close", "Thank the team, confirm where results are kept, and set the date of the next check.")],
        sections_title="Probing questions by dimension",
        sections_intro="Use these to deepen the conversation on any row that is red, amber or split.",
        sections=[("1 · Delivering Value", EMERALD, ["How do we know customers value what we ship?", "When did we last see a user use our work?"]),
                  ("2 · Easy to Release", BLUE, ["What's the scariest part of releasing?", "How many manual steps are there?"]),
                  ("3 · Fun", ORANGE, ["What gives us energy? What drains it?", "When did we last celebrate something?"]),
                  ("4 · Health of Codebase", AMBER, ["Which part of the code do we avoid touching?", "Is tech debt visible in the backlog?"]),
                  ("5 · Learning", SKY, ["What did we learn this quarter?", "Is learning planned or squeezed in?"]),
                  ("6 · Mission", PURPLE, ["Could each of us explain why the team exists?", "How does our work link to our quarterly objectives?"]),
                  ("7 · Pawns or Players", RED, ["Which decisions do we wish we could make?", "Where do we feel we have no say?"]),
                  ("8 · Speed", FOREST, ["Where does work wait?", "What blocks us most often?"]),
                  ("9 · Suitable Process", SLATE, ["Which ritual adds the least value?", "What would we change if we could?"]),
                  ("10 · Support", BLUE, ["Who do we struggle to get help from?", "How long does it take to get unblocked?"]),
                  ("11 · Teamwork", EMERALD, ["Do we help each other or work in silos?", "How do we handle disagreement?"])],
        tips=[("Safety first", "If people don't feel safe, the dots will all be green. Keep results in the team, and never compare teams' scores."),
              ("Split votes are gold", "A row with green and red votes tells you more than an all-red row. Explore why people see it differently."),
              ("Trends beat snapshots", "A single check is a conversation starter. Three checks show whether things are actually changing."),
              ("Adapt the dimensions", "Swap or reword dimensions that don't fit your context, but keep them stable over time so you can compare."),
              ("Don't fix everything", "Pick 1–2 areas. Improving one red row is worth more than vague intentions on five."),
              ("Escalate what's outside", "Some reds (such as support or environments) need help from outside the team. Make them visible to leadership.")],
        pitfalls=("using results to rank or judge teams; managers voting or watching the vote; skipping the discussion and only collecting "
                  "colours; changing the dimensions every time so trends are lost; no follow-through on the chosen focus areas."),
        after=[("Within 24 hours", "Photograph the board and store it with previous checks. Record the votes per row so you can track trends."),
               ("Focus areas", "Turn each focus area into a 1% Experiment Canvas with an owner and review date."),
               ("Between checks", "Revisit the focus areas at retros. Did the experiments help?"),
               ("Next check", "Repeat at the same point next quarter, using the same dimensions, and set the trend arrows.")],
        toolkit=("The health check is the <b>diagnose</b> step of the toolkit. Feed red or amber rows into a "
                 "<a href=\"experiment-canvas.html\">1% Experiment Canvas</a>. Where the cause sits outside the team, take it to a "
                 "<a href=\"facilitator-guide-marginal-gains.html\">Marginal Gains Workshop</a>."),
        foot="“Which 1–2 areas would make the biggest difference if they got 1% better?”",
    ),

    # -------------------------------------------------------------- experiment canvas
    dict(
        slug="experiment-canvas",
        title="1% Experiment Canvas Guide",
        subtitle="How to turn a small improvement idea into an experiment that gets run, measured and reviewed.",
        tag="Facilitator Run-Sheet · Hypothesis-Driven Improvement · Build, Measure, Learn",
        boards=[("Open canvas", "experiment-canvas.html"), ("SVG", "experiment-canvas.svg")],
        lede="What's the smallest change that could prove us right or wrong?",
        intro=("Improvement ideas often die because they are vague: no owner, no measure, no end date. The canvas makes "
               "each idea testable. Fill it in when you choose an experiment (sections 1–6) and complete it at the review "
               "(section 7). Use one canvas per experiment."),
        glance=[("Duration", "20–30 min to fill in<br>15 min to review"), ("Group", "2–4 people<br>per canvas"),
                ("Used after", "Marginal Gains, retro<br>or health check"), ("Output", "A testable experiment<br>with an owner")],
        before=["Print one A3 canvas per experiment, or duplicate the SVG frame digitally",
                "Know which friction or idea you are testing, ideally from the Marginal Gains board or a retro",
                "Find the data source for your baseline before the session if you can",
                "Make sure the likely owner is in the room",
                "Book the review date before you leave the session"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–3", "1 · Friction", "Tick the board area and describe the pain point in the team's own words. Be specific: “PRs wait over a day for review”, not “slow reviews”."),
                ("3–10", "2 · Hypothesis", "Complete the If / for / then / we'll know sentence. If you can't name the signal, the idea isn't testable yet."),
                ("10–14", "3 · The 1% Change", "Describe exactly what will be different, then shrink it. What could we try tomorrow, with no approval needed?"),
                ("14–20", "4 · Measure", "Record the baseline (today), the target, and how it will be measured. Add an early-signal indicator and a guardrail metric."),
                ("20–24", "5 · Plan & Timebox", "Name one owner, any supporters, a start date, a mid-point check and a review date. Tick the timebox."),
                ("24–28", "6 · Risks", "What must be true? What could go wrong? Who needs to know? Use stickies for each risk."),
                ("Review", "7 · Result & Decision", "At the review date: result vs. target, then persevere, pivot or stop, and what we learned and who should hear it.")],
        sections_title="Making each section strong",
        sections_intro="A quick quality check for each section of the canvas.",
        sections=[("1 · Where's the Friction?", RED, ["Is it an observed problem, not a guess?", "Could someone outside the team understand it?"]),
                  ("2 · Hypothesis", PURPLE, ["Does it name the change, who it affects, the outcome and the signal?", "Could it be proven wrong?"]),
                  ("3 · The 1% Change", EMERALD, ["Could we start within a week?", "Is it within the team's control?"]),
                  ("4 · Measure", BLUE, ["Is there a number for the baseline?", "Is the target realistic for the timebox?", "Does the guardrail protect quality?"]),
                  ("5 · Plan & Timebox", ORANGE, ["Is there exactly one owner?", "Is the review date in calendars?"]),
                  ("6 · Risks & Assumptions", AMBER, ["What's the riskiest assumption?", "How will we spot early that it's failing?"]),
                  ("7 · Result & Decision", FOREST, ["Persevere = make it standard practice", "Pivot = adjust and run again", "Stop = no gain, so share why"])],
        example=[("Friction", "Engineering: pull requests wait more than a day for review."),
                 ("If we…", "hold a 15-minute review slot straight after stand-up"),
                 ("for…", "the team's own pull requests"),
                 ("then we expect…", "faster flow from code-complete to merge"),
                 ("We'll know when…", "median PR wait time drops"),
                 ("Baseline → Target", "26 hours → 18 hours, measured from repository analytics weekly"),
                 ("Guardrail", "Escaped defects do not increase"),
                 ("Owner · Timebox", "Tech lead · 2 sprints · review at the sprint 2 retro")],
        tips=[("Small beats perfect", "A small experiment run this week teaches more than a perfect one that never starts."),
              ("One owner", "The owner makes sure it happens and gets reviewed. Supporters do the work with them."),
              ("Measure before you change", "Capture the baseline before starting, or you can't show improvement."),
              ("Guardrails matter", "Speeding something up by cutting quality isn't a gain. Always pick a metric that must not get worse."),
              ("Stopping is success", "A clean “stop” with a clear learning is a good result. Share it so others don't repeat it."),
              ("Make it visible", "Put the canvas on the team wall or wiki next to the board, and review it at stand-up.")],
        pitfalls=("measures like “better quality” with no number; targets with no baseline; experiments that need another team's work; "
                  "no review date; quietly dropping experiments instead of deciding to stop; running too many at once."),
        after=[("Straight away", "Add the experiment to the team backlog. Book the mid-point check and the review."),
               ("Mid-point", "Check the early-signal indicator. If it's not started, find out why and remove the blocker."),
               ("At the review", "Complete section 7 together. Decide persevere, pivot or stop, and record what you learned."),
               ("Share", "Post completed canvases where other teams can see them, such as at the system demo or I&A.")],
        toolkit=("The canvas is the <b>experiment</b> step. Ideas come from the <a href=\"facilitator-guide-marginal-gains.html\">Marginal "
                 "Gains Workshop</a>, a <a href=\"facilitator-guide-team-health-check.html\">health check</a> or a retro. Results are "
                 "reviewed in the next retrospective."),
        foot="“If this works, who else would benefit from knowing?”",
    ),

    # -------------------------------------------------------------- lean coffee
    dict(
        slug="lean-coffee",
        title="Lean Coffee Guide",
        subtitle="How to run a structured, agenda-less meeting where the group decides what to talk about.",
        tag="Facilitator Run-Sheet · Participant-Driven Meetings · Timeboxed Conversations",
        boards=[("Open board", "lean-coffee-board.html"), ("SVG", "lean-coffee-board.svg")],
        lede="What's the most valuable thing we could talk about right now?",
        intro=("Lean Coffee replaces a fixed agenda with one the group builds on the spot. People propose topics, vote, and "
               "discuss them in priority order within short timeboxes. After each timebox the group votes to keep going or move on. "
               "It suits communities of practice, team syncs, leadership forums and open Q&amp;A sessions."),
        glance=[("Duration", "45–90 min"), ("Group", "4–12 people<br>(split if larger)"),
                ("Prep", "Minimal:<br>board, stickies, timer"), ("Output", "Prioritised talk<br>&amp; actions")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Yellow and green stickies, markers, dot stickers (3 per person)",
                "A visible timer (phone, or the meeting tool's timer)",
                "Decide the theme or scope, if any, and say it in the invite",
                "For groups over 12, prepare two boards and split into tables"],
        agenda_heads=["Time", "Activity", "Facilitator notes"],
        agenda=[("0–3", "Explain the format", "Walk the five steps at the bottom of the board. Agree the timebox: 8 minutes, then +4, then +2."),
                ("3–8", "Brainstorm topics", "Silent writing: one topic per yellow sticky in <b>To Discuss</b>. Topics can be questions, problems or ideas."),
                ("8–15", "Pitch & dot-vote", "Each author pitches their topic in one sentence. Group duplicates, then everyone places 3 dots. Sort by votes."),
                ("15–50", "Discuss in rounds", "Move the top topic to <b>Discussing</b> and start the timer. When it ends, vote ↑ keep going / → wrap up / ↓ move on. A majority ↑ adds time."),
                ("—", "After each topic", "Capture the key takeaway on a green sticky, then move the topic to <b>Discussed</b>."),
                ("50–57", "Takeaways & actions", "Review the Discussed column. Turn takeaways that need follow-up into actions with an owner."),
                ("57–60", "Close", "Quick feedback on the session. Unfinished topics can go to the next Lean Coffee.")],
        sections_title="Using each part of the board",
        sections_intro="What each area is for, and what to watch for as a facilitator.",
        sections=[("1 · To Discuss", BLUE, ["One topic per sticky, short enough to read from a distance", "Sort by votes, most at the top", "Merge duplicates before voting"]),
                  ("2 · Discussing", ORANGE, ["Only one topic at a time", "Tick each timebox round so the group can see time used", "Note the key takeaway before moving on"]),
                  ("3 · Discussed", EMERALD, ["Every topic here gets a green takeaway sticky", "This is the meeting's record, so photograph it"]),
                  ("Keep-going vote", AMBER, ["Thumbs up, sideways or down works as well as the board icons", "Majority ↑ extends the timer; otherwise move on", "Rounds get shorter: 8, then 4, then 2 minutes"]),
                  ("How it works row", SLATE, ["Point to it at the start so newcomers know the flow", "It keeps the group self-facilitating"]),
                  ("Takeaways & Actions", RED, ["Only for things that need follow-up", "Each action needs an owner and a done when"])],
        tips=[("Hold the timebox", "The timer is what makes Lean Coffee work. Stop when it goes off, even mid-sentence, and vote."),
              ("Let the group decide", "Your job is the process, not the content. Don't steer which topics win."),
              ("Shrink rounds", "Shortening the extensions (8, 4, 2) stops one topic taking over the meeting."),
              ("Unfinished is fine", "Not every topic gets covered. Low-vote topics can be handled offline or at the next session."),
              ("Remote works well", "Use a digital board with voting and a shared timer. Ask people to use reactions for the keep-going vote."),
              ("Make it a habit", "A regular Lean Coffee, such as monthly for a community of practice, builds trust and surfaces issues early.")],
        pitfalls=("skipping the timer; one person proposing most of the topics; letting the facilitator's agenda creep in; "
                  "no takeaways captured, so the discussion is lost; groups too large for everyone to speak."),
        after=[("Straight away", "Photograph the board. Share the Discussed column and the actions with participants."),
               ("Actions", "Track actions where the group will see them, such as the team board or community page."),
               ("Unfinished topics", "Carry high-vote topics that weren't reached to the top of the next session's To Discuss column."),
               ("Next session", "Start by reviewing last time's actions in two minutes, then brainstorm.")],
        toolkit=("Lean Coffee is a flexible <b>facilitate</b> tool. Use it to surface topics before a "
                 "<a href=\"facilitator-guide-marginal-gains.html\">Marginal Gains Workshop</a>, or as a lightweight alternative to a "
                 "retrospective when the team wants an open conversation."),
        foot="“Has this conversation run its course, or is there more value to unlock?”",
    ),

    # -------------------------------------------------------------- retros
    dict(
        slug="retro-start-stop-continue",
        title="Start · Stop · Continue Guide",
        subtitle="How to run the classic three-column retrospective, for a sprint or a quarter.",
        tag="Facilitator Run-Sheet · Retrospective Kit · Reflect, Learn, Adapt",
        boards=[("Open board", "retro-board-start-stop-continue.html"), ("SVG", "retro-board-start-stop-continue.svg")],
        lede="If we could only change one thing, what would it be?",
        intro=("A simple, action-oriented format: what should we start, stop, and keep doing? It works well for new teams, "
               "short timeboxes, and teams that want to focus on behaviour change rather than a long look back."),
        glance=[("Duration", "60 min (sprint)<br>2 h (quarter)"), ("Group", "One team<br>3–10 people"),
                ("Best for", "Clear, practical<br>changes"), ("Output", "Up to 3 actions<br>with owners")],
        before=RETRO_BEFORE,
        agenda_heads=["Sprint", "Quarter", "Activity", "Facilitator notes"],
        agenda=retro_agenda("Yellow stickies in each column. Aim for at least one per column, so “Continue” doesn't get skipped.",
                            "Take the top clusters in turn. For Stop items, ask what we'd do instead. Capture ideas on green stickies."),
        sections_title="Prompts for each column",
        sections_intro="Read these out if a column stays empty.",
        sections=[("1 · Start", EMERALD, ["What have other teams tried that we haven't?", "What experiment keeps getting postponed?", "What would make next sprint easier?"]),
                  ("2 · Stop", RED, ["What do we do out of habit that nobody would miss?", "Which meeting or step adds the least value?", "What slows us down every sprint?"]),
                  ("3 · Continue", BLUE, ["What worked so well we must protect it?", "Which recent change paid off?", "What should we tell other teams about?"]),
                  ("Actions strip", ORANGE, ["Up to 3 actions", "Owner + done when for each", "Bigger ideas go on a 1% Experiment Canvas"])],
        tips=RETRO_TIPS, pitfalls=RETRO_PITFALLS, after=RETRO_AFTER, toolkit=RETRO_TOOLKIT,
        foot="“What's the smallest step we can take on it tomorrow?”",
    ),
    dict(
        slug="retro-4ls",
        title="The 4 Ls Retrospective Guide",
        subtitle="How to run a Liked, Learned, Lacked, Longed For retrospective, for a sprint or a quarter.",
        tag="Facilitator Run-Sheet · Retrospective Kit · Reflect, Learn, Adapt",
        boards=[("Open board", "retro-board-4ls.html"), ("SVG", "retro-board-4ls.svg")],
        lede="What did we learn that we don't want to forget?",
        intro=("The 4 Ls balances positives and gaps, and puts learning in the spotlight. It suits the end of a project, a release "
               "or a quarter, and teams that want a reflective conversation rather than only listing problems."),
        glance=[("Duration", "60 min (sprint)<br>2 h (quarter)"), ("Group", "One team<br>3–10 people"),
                ("Best for", "Reflection &amp;<br>learning"), ("Output", "Up to 3 actions<br>&amp; key learnings")],
        before=RETRO_BEFORE,
        agenda_heads=["Sprint", "Quarter", "Activity", "Facilitator notes"],
        agenda=retro_agenda("Yellow stickies across all four columns. Encourage people to fill Learned, which often stays thin.",
                            "Celebrate Liked briefly, capture Learned, then spend most time on Lacked and Longed For, where the actions are."),
        sections_title="Prompts for each column",
        sections_intro="Read these out if a column stays empty.",
        sections=[("1 · Liked", FOREST, ["What did we enjoy doing?", "What went better than expected?", "Who helped us?"]),
                  ("2 · Learned", BLUE, ["What do we know now that we didn't before?", "What surprised us about users or the system?"]),
                  ("3 · Lacked", ORANGE, ["What was missing: information, people, time or tools?", "Where did we lack clarity or focus?"]),
                  ("4 · Longed For", PURPLE, ["What do we wish we had?", "If we had a magic wand, what would change?"]),
                  ("Actions strip", RED, ["Turn the strongest Lacked / Longed For into up to 3 actions", "Owner + done when for each"])],
        tips=RETRO_TIPS, pitfalls=RETRO_PITFALLS, after=RETRO_AFTER, toolkit=RETRO_TOOLKIT,
        foot="“Which ‘lacked’ or ‘longed for’ could we fix by 1%?”",
    ),
    dict(
        slug="retro-mad-sad-glad",
        title="Mad · Sad · Glad Guide",
        subtitle="How to run an emotion-focused retrospective, for a sprint or a quarter.",
        tag="Facilitator Run-Sheet · Retrospective Kit · Reflect, Learn, Adapt",
        boards=[("Open board", "retro-board-mad-sad-glad.html"), ("SVG", "retro-board-mad-sad-glad.svg")],
        lede="What's behind the strongest feelings on this board?",
        intro=("Mad · Sad · Glad surfaces how the work <em>felt</em>, which often reveals issues that a process-focused retro misses. "
               "It suits teams after a stressful period, teams where morale is uncertain, and anyone wanting to build empathy. "
               "It needs a safe room more than most formats."),
        glance=[("Duration", "60 min (sprint)<br>2 h (quarter)"), ("Group", "One team<br>3–10 people"),
                ("Best for", "Morale &amp; hidden<br>frustrations"), ("Output", "Up to 3 actions<br>with owners")],
        before=RETRO_BEFORE + ["Think about safety: is this the right format right now? Is anyone likely to feel exposed?"],
        agenda_heads=["Sprint", "Quarter", "Activity", "Facilitator notes"],
        agenda=retro_agenda("Yellow stickies in each column. Remind people that feelings are valid data and that we're discussing events, not people.",
                            "Start with Glad to build energy, then explore Mad and Sad. Ask “What would turn this into a Glad?”"),
        sections_title="Prompts for each column",
        sections_intro="Read these out if a column stays empty.",
        sections=[("1 · Mad", RED, ["What frustrated us again and again?", "What felt unfair or outside our control?", "When did we feel stuck?"]),
                  ("2 · Sad", SKY, ["What didn't go to plan?", "What opportunity did we miss?", "What expectation wasn't met?"]),
                  ("3 · Glad", EMERALD, ["What are we proud of?", "Who should we thank?", "What made us smile?"]),
                  ("Actions strip", ORANGE, ["Target the root cause of the strongest Mad", "Owner + done when for each"])],
        tips=[("Name the emotion, discuss the event", "Feelings are a signal. Ask what happened that caused them, and keep it about events, not people."),
              *RETRO_TIPS[2:]],
        pitfalls=RETRO_PITFALLS + " This format also invites venting. Make sure the conversation moves to causes and actions.",
        after=RETRO_AFTER, toolkit=RETRO_TOOLKIT,
        foot="“What would turn one ‘mad’ into a ‘glad’?”",
    ),
    dict(
        slug="retro-sailboat",
        title="Sailboat Retrospective Guide",
        subtitle="How to run a visual retrospective about goals, help, impediments and risks, for a sprint or a quarter.",
        tag="Facilitator Run-Sheet · Retrospective Kit · Reflect, Learn, Adapt",
        boards=[("Open board", "retro-board-sailboat.html"), ("SVG", "retro-board-sailboat.svg")],
        lede="Which anchor, if cut, would let us sail fastest?",
        intro=("The sailboat metaphor helps teams look both back and forward: the <b>island</b> is our goal, the <b>wind</b> is what "
               "pushes us forward, <b>anchors</b> are what slow us down, and <b>rocks</b> are the risks ahead. Including risks "
               "makes it a strong choice before a new planning cycle or at a quarter boundary."),
        glance=[("Duration", "60 min (sprint)<br>2 h (quarter)"), ("Group", "One team<br>3–12 people"),
                ("Best for", "Goals, impediments<br>&amp; risks"), ("Output", "Up to 3 actions<br>&amp; known risks")],
        before=RETRO_BEFORE,
        agenda_heads=["Sprint", "Quarter", "Activity", "Facilitator notes"],
        agenda=retro_agenda("Yellow stickies in Wind, Anchors and Rocks. Use green for ideas that would add wind or cut an anchor.",
                            "Discuss the biggest anchors first, then the rocks. For each risk, decide whether to act now or just watch it.",
                            extra_first=("5–8", "10–15", "Name the island", "Agree the goal first and write it in the Island zone: a sprint goal, quarterly objective or product outcome.")),
        sections_title="Prompts for each zone",
        sections_intro="Read these out if a zone stays empty.",
        sections=[("1 · Wind", FOREST, ["What helped us move faster?", "Who or what supported us?", "What should we do more of?"]),
                  ("2 · Island", EMERALD, ["Where are we heading?", "What does success look like at the end of the sprint or quarter?"]),
                  ("3 · Anchors", RED, ["What slowed us down?", "Which handoffs or waits hurt most?", "What drags on us every time?"]),
                  ("4 · Rocks", AMBER, ["What could sink us?", "Which dependencies or deadlines worry us?", "What are we not talking about?"]),
                  ("Actions strip", ORANGE, ["Cut one anchor, avoid one rock", "Owner + done when for each"])],
        tips=[("Island first", "Without a shared goal, wind and anchors are hard to judge. Spend a few minutes agreeing it."),
              ("Risks need owners too", "For each important rock, agree who will watch it and what would trigger action."),
              *RETRO_TIPS[2:]],
        pitfalls=RETRO_PITFALLS + " With the Sailboat in particular, don't let the drawing become the conversation. Keep moving.",
        after=RETRO_AFTER, toolkit=RETRO_TOOLKIT,
        foot="“What can we do next to steer clear of the rocks?”",
    ),
]

BREAKDOWN_TOOLKIT = ("The break-down tools work from big to small: the <a href=\"facilitator-guide-epic-breakdown-canvas.html\">Epic Breakdown "
                     "Canvas</a> turns an idea into an MVP and features, the <a href=\"facilitator-guide-story-map.html\">Story Map</a> lays out "
                     "the user journey and release slices, the <a href=\"facilitator-guide-story-splitting.html\">Story Splitting poster</a> "
                     "makes stories small enough for a sprint, and <a href=\"facilitator-guide-example-mapping.html\">Example Mapping</a> "
                     "checks that each story is understood and ready. The <a href=\"facilitator-guide-backlog-anatomy.html\">"
                     "Backlog Item Anatomy</a> poster shows what a good epic, feature and story look like.")

BREAKDOWN_GUIDES = [
    # -------------------------------------------------------------- epic breakdown
    dict(
        slug="epic-breakdown-canvas",
        title="Epic Breakdown Canvas Guide",
        subtitle="How to turn a big idea into a testable MVP, a set of valuable features, and the first stories.",
        tag="Facilitator Run-Sheet · Break Down Work · Epic Hypothesis · Minimum Viable Product",
        boards=[("Open canvas", "epic-breakdown-canvas.html"), ("SVG", "epic-breakdown-canvas.svg")],
        lede="What's the smallest thing we could build to learn whether this epic is worth it?",
        intro=("Big initiatives often arrive as a solution with a deadline. The canvas slows the group down just enough to agree "
               "<b>why</b> the epic exists, what outcome would prove it worked, and what the <b>smallest viable version</b> is. "
               "It then splits the epic into a few features that each deliver value, and identifies the first stories a team "
               "can start. Use it before quarterly planning, or whenever an epic is too vague to plan."),
        glance=[("Duration", "90–120 min"), ("Group", "PO / PM, architect,<br>team reps, stakeholders"),
                ("Use when", "A new epic or<br>big initiative"), ("Output", "MVP, 3–8 features<br>&amp; first stories")],
        before=["Print the canvas at A3 or larger, or load the SVG as a digital background",
                "Ask the epic owner to draft the hypothesis statement in advance",
                "Bring any evidence: customer research, data, competitor information",
                "Invite people who know the users, the technology and the constraints",
                "Yellow stickies and markers; a copy of the Story Splitting poster",
                "Agree who decides on MVP scope (usually the epic owner or product manager)"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "Frame the epic", "The epic owner explains the idea and why now. Clarify questions only; don't design solutions yet."),
                ("10–30", "1 · Epic Hypothesis", "Complete the For / who / the / is a / that / unlike / our solution statement together. If the group can't agree the “who”, stop and resolve that first."),
                ("30–45", "2 · Outcomes", "Agree 1–3 business outcomes and the leading indicators that would show early progress. Prefer numbers."),
                ("45–60", "3 · MVP", "Ask: what's the smallest thing that would test the hypothesis? Write the persevere and pivot-or-stop conditions."),
                ("60–85", "4 · Features", "Split the epic into 3–8 features, each with a name, benefit and rough size. Tick the ones needed for the MVP."),
                ("85–100", "6 · Out of Scope · 7 · Risks", "Write down what you are explicitly not doing, plus any non-functional needs. Add dependencies and risks as stickies."),
                ("100–115", "5 · First Stories", "For the MVP features, write the first few stories as vertical slices. Use the Story Splitting poster if any look too big."),
                ("115–120", "Close", "Confirm the next step: story mapping, release planning, or a go / no-go decision.")],
        sections_title="Making each section strong",
        sections_intro="Quality checks for each part of the canvas.",
        sections=[("1 · Epic Hypothesis", PURPLE, ["Is the customer specific, not “everyone”?", "Does “that…” describe value, not features?", "Could it be proven wrong?"]),
                  ("2 · Outcomes & Measures", EMERALD, ["Is there a baseline and a target?", "Would a leading indicator move within weeks?"]),
                  ("3 · MVP", BLUE, ["Is it the smallest test, not the first release of everything?", "Are the persevere / pivot conditions measurable?"]),
                  ("4 · Features", ORANGE, ["Does each feature deliver value by itself?", "Are there more than 8? Group or cut some", "Is the MVP set genuinely minimal?"]),
                  ("5 · First Stories", FOREST, ["Is each story a vertical slice?", "Could the team start one next sprint?"]),
                  ("6 · Out of Scope & NFRs", AMBER, ["Have stakeholders seen the out-of-scope list?", "Are security, performance and compliance needs captured?"]),
                  ("7 · Dependencies & Risks", RED, ["Who outside the room do we depend on?", "What's the riskiest assumption, and how will we test it early?"])],
        tips=[("Problem before solution", "Groups jump to features. Keep pulling the conversation back to the customer and the outcome until the hypothesis is solid."),
              ("MVP means learning", "An MVP is the smallest experiment that tests the hypothesis, not a cut-down version of the full plan."),
              ("Features must stand alone", "If a feature only delivers value once three others are done, it's a component. Re-slice it."),
              ("Write the out-of-scope list", "Saying what you won't do prevents scope creep later, and surfaces disagreement early."),
              ("Size roughly", "T-shirt sizes are enough at this stage. Precise estimates come later, from the teams."),
              ("Revisit after the MVP", "When the MVP results come in, update the canvas: persevere, pivot or stop.")],
        pitfalls=("a hypothesis that is really a feature list; an MVP that is most of the epic; features split by technical layer; "
                  "no measurable outcome; skipping out-of-scope so everything stays in; designing the solution in detail."),
        after=[("Straight away", "Photograph the canvas. Create the epic and its features in your backlog tool, linked to the canvas."),
               ("Next step", "Run a Story Map for the MVP features to lay out the user journey and the first release slice."),
               ("Before quarterly planning", "Refine the first stories with Example Mapping so teams can plan them."),
               ("After the MVP", "Review the outcomes and leading indicators against the persevere / pivot conditions.")],
        toolkit=BREAKDOWN_TOOLKIT,
        foot="“Which feature, if it were the only one, would still deliver value?”",
    ),

    # -------------------------------------------------------------- story map
    dict(
        slug="story-map",
        title="User Story Map Guide",
        subtitle="How to map a user journey and slice it into releases that each deliver a complete, usable path.",
        tag="Facilitator Run-Sheet · Break Down Work · Inspired by Jeff Patton's Story Mapping",
        boards=[("Open board", "story-map-board.html"), ("SVG", "story-map-board.svg")],
        lede="What's the smallest slice that lets a user reach their goal end-to-end?",
        intro=("A flat backlog hides the big picture. A story map arranges work along the user's journey: the <b>activities</b> "
               "across the top form the backbone, the <b>user tasks</b> beneath them form the walking skeleton, and stories hang "
               "below each task. Horizontal <b>release slices</b> then show what's in the MVP, what comes next, and what can wait. "
               "Each slice is a complete path a user can actually use."),
        glance=[("Duration", "1.5–3 h"), ("Group", "PO, team, UX,<br>a user if possible"),
                ("Use when", "A new product, feature<br>or epic"), ("Output", "A journey map &amp;<br>an MVP slice")],
        before=["Print the board at A1 or A0 if you can, or use a long wall or digital board, as maps grow wide",
                "Blue, yellow and green stickies, markers, and tape to mark slice lines",
                "Agree the persona and goal in advance, or plan to start with them",
                "Bring user research, journey maps or support data if you have them",
                "If the product is large, scope the map to one persona and one goal"],
        agenda_heads=["Time", "Activity", "Facilitator notes"],
        agenda=[("0–10", "Persona & goal", "Fill in the context bar: who is the user, what are they trying to achieve, and which product or epic is this?"),
                ("10–30", "1 · Activities", "Tell the user's story out loud, left to right. Write each big step as a blue sticky in the backbone. Aim for 4–10."),
                ("30–55", "2 · User tasks", "Under each activity, add the yellow steps the user takes. Walk the whole skeleton end-to-end to check that nothing is missing."),
                ("55–90", "Stories", "Brainstorm green stories under each task: options, variations, details. Order each column, most important at the top."),
                ("90–110", "Slice the MVP", "Draw the Release 1 line: the fewest stories that still let a user complete the journey end-to-end. Write its outcome."),
                ("110–125", "Next slices", "Slice Release 2 and Later. Give each slice an outcome and a target date."),
                ("125–135", "Check & close", "Walk the MVP slice as the user. Can they reach their goal? Agree the next step: splitting and refinement.")],
        sections_title="Using each part of the map",
        sections_intro="What goes where, and what to watch for.",
        sections=[("Context bar", SLATE, ["One persona and one goal per map", "Write the product or epic it serves"]),
                  ("1 · Activities", BLUE, ["Verb phrases: “Find a product”, “Pay”", "In the order users do them", "4–10 is typical"]),
                  ("2 · User Tasks", AMBER, ["The steps within each activity", "Together they form the walking skeleton", "Read them left to right as a story"]),
                  ("Stories", FOREST, ["Hang under the task they belong to", "Most important at the top", "Variations and details go lower"]),
                  ("Release 1 · MVP", EMERALD, ["At least one story under every task", "The thinnest path to the goal", "Has a clear outcome"]),
                  ("Release 2 & Later", SLATE, ["Make the journey better or broader", "Revisit after learning from Release 1"])],
        tips=[("Tell it as a story", "Narrate the journey: “first the user…, then…”. Gaps become obvious when you say them out loud."),
              ("Breadth before depth", "Get the whole backbone in place before adding detail anywhere. It's easy to over-detail the first activity."),
              ("Every column in the MVP", "An MVP that skips a task isn't usable end-to-end. Even a manual or basic version counts."),
              ("Slice by outcome", "Name what each release lets users do or learn, not just which stories it contains."),
              ("Keep it visible", "Leave the map on the wall and update it each sprint. It becomes the team's shared picture of the product."),
              ("One map per goal", "If the map sprawls, you probably have more than one persona or goal. Split it.")],
        pitfalls=("mapping system components instead of user steps; spending all the time on one activity; an MVP that is "
                  "everything in the first two columns; never revisiting the map after the workshop; stories that are really tasks."),
        after=[("Straight away", "Photograph the map in sections. Transfer stories to the backlog, keeping their slice and order."),
               ("Refine", "Split any Release 1 story that is too big using the Story Splitting poster, then use Example Mapping on each."),
               ("Each sprint", "Move completed stories, adjust slices as you learn, and review the map at Sprint Review."),
               ("After release", "Check the slice's outcome. Did users reach their goal? Re-slice what's next.")],
        toolkit=BREAKDOWN_TOOLKIT,
        foot="“What will we learn from releasing this slice?”",
    ),

    # -------------------------------------------------------------- story splitting
    dict(
        slug="story-splitting",
        title="Story Splitting Guide",
        subtitle="How to use the poster to split large stories into thin, vertical slices during refinement.",
        tag="Facilitator Run-Sheet · Break Down Work · INVEST · SPIDR · Vertical Slicing",
        boards=[("Open poster", "story-splitting-poster.html"), ("SVG", "story-splitting-poster.svg")],
        lede="If we could only ship half of this, which half?",
        intro=("Stories that are too big hide risk, block flow and carry over from sprint to sprint. The poster gives teams a quick "
               "<b>INVEST</b> check, nine proven <b>splitting patterns</b> with a running example, and a reminder to slice "
               "<b>vertically</b>, so every piece delivers something a user can use. Pin it up in the team area and bring it to "
               "every refinement session."),
        glance=[("Duration", "10–20 min<br>per story"), ("Group", "Team + PO<br>in refinement"),
                ("Use when", "A story won't fit<br>in a sprint"), ("Output", "2–5 smaller,<br>valuable stories")],
        before=["Print the poster at A3 and pin it where the team refines its backlog",
                "Pick the biggest or least clear stories from the top of the backlog",
                "Make sure the PO is in the session: they decide which slices matter most",
                "Bring the acceptance criteria, if any already exist"],
        agenda_heads=["Time", "Step", "Facilitator notes"],
        agenda=[("0–2", "Read the story", "The PO reads the story and why it matters. Clarify the user and the value."),
                ("2–5", "INVEST check", "Go through the six letters. If <b>Small</b> fails, split. If <b>Valuable</b> fails, rethink or drop the story instead."),
                ("5–12", "Try patterns", "Work through the patterns in order, starting with workflow steps. For each, ask “could we split it this way?” Sketch the candidate slices on stickies."),
                ("12–15", "Choose the split", "Pick the split that lets the PO deprioritise a slice, or that gives slices of similar size. Check each slice is vertical."),
                ("15–18", "Check the slices", "Run each new story through INVEST again. Still too big? Split again, often with a second pattern."),
                ("18–20", "Order & record", "The PO orders the new stories. Often the last slice can wait, or isn't needed at all.")],
        sections_title="When each pattern fits",
        sections_intro="Clues in the story that point to a particular pattern.",
        sections=[("1 · Workflow Steps", BLUE, ["The story describes a process or journey", "“…and then…” appears in the description"]),
                  ("2 · Business Rules", PURPLE, ["Lots of “if”, “unless” or “except”", "Different rules for different customers"]),
                  ("3 · Happy / Unhappy Paths", FOREST, ["Error handling dominates the discussion", "Edge cases are making it look big"]),
                  ("4 · Data Variations", SKY, ["Different types, formats or sources of data", "“…for all countries / file types…”"]),
                  ("5 · Interfaces", ORANGE, ["Multiple channels, devices or browsers", "Several input methods"]),
                  ("6 · Simple → Complex", EMERALD, ["A simple version would still help users", "Complex calculations or logic"]),
                  ("7 · Operations (CRUD)", AMBER, ["The word “manage”", "Create, edit and delete all lumped together"]),
                  ("8 · Defer Performance", RED, ["Speed or scale needs make it big", "The basic function would already be valuable"]),
                  ("9 · Spike First", SLATE, ["Nobody can estimate it", "A big technical or domain unknown"])],
        tips=[("Value in every slice", "Each slice must be something a user, customer or stakeholder could see and give feedback on."),
              ("Never split by layer", "“Build the database” and “build the UI” aren't stories. They deliver nothing on their own."),
              ("Let the PO choose", "A good split gives the PO options: most of the value early, and some slices they may never need."),
              ("Combine patterns", "Large stories often need two passes: split by workflow, then by rules within one step."),
              ("Spikes are timeboxed", "A spike's output is knowledge. Keep it short (a day or two), then split the real work."),
              ("Aim for several per sprint", "Smaller stories flow better. A useful target is 5–15 stories finished per sprint.")],
        pitfalls=("splitting into technical tasks; slices that only deliver value once all are done; creating “part 1” and “part 2” "
                  "stories with no value difference; using spikes to avoid committing; splitting so small that admin outweighs the work."),
        after=[("Straight away", "Replace the original story with the new slices in the backlog, ordered by the PO."),
               ("Next", "Run Example Mapping on the top slice so it's clearly understood before planning."),
               ("Over time", "Track how many stories carry over each sprint. Fewer carry-overs show splitting is working."),
               ("Retro", "If big stories keep appearing, discuss it at the retro, and consider splitting earlier, at the story-map stage.")],
        toolkit=BREAKDOWN_TOOLKIT,
        foot="“What's the thinnest slice that still delivers value to a user?”",
    ),

    # -------------------------------------------------------------- example mapping
    dict(
        slug="example-mapping",
        title="Example Mapping Guide",
        subtitle="How to explore a story through rules, examples and questions, and decide whether it's ready.",
        tag="Facilitator Run-Sheet · Break Down Work · Inspired by Matt Wynne's Example Mapping",
        boards=[("Open board", "example-mapping-board.html"), ("SVG", "example-mapping-board.svg")],
        lede="Lots of pink? We're not ready yet.",
        intro=("Example Mapping is a short, structured conversation that builds a shared understanding of one story. Each "
               "<b>rule</b> (an acceptance criterion) goes on a blue card, concrete <b>examples</b> of each rule go on green cards, "
               "and anything nobody can answer goes on a pink <b>question</b> card. After 25 minutes, the shape of the map tells you "
               "whether the story is ready, too big, or not yet understood."),
        glance=[("Duration", "25 min<br>per story"), ("Group", "The three amigos:<br>PO, dev, tester"),
                ("Use when", "Refining a story<br>before planning"), ("Output", "Rules, examples<br>&amp; a ready decision")],
        before=["Print the board at A3, or use a digital board with four sticky colours",
                "Yellow, blue, green and pink stickies (or index cards) and markers",
                "Pick stories from the top of the backlog that are next in line for planning",
                "Invite at least one person each for business, development and testing",
                "A visible timer set to 25 minutes"],
        agenda_heads=["Time", "Step", "Facilitator notes"],
        agenda=[("0–2", "The story", "The PO writes the story on the yellow card and reads the As a / I want / so that statement."),
                ("2–8", "Rules", "List the rules the story must satisfy: one per blue card, across the top. These become the acceptance criteria."),
                ("8–18", "Examples", "For each rule, give concrete examples on green cards beneath it: “Given a basket over £50, when…, then…”. Examples often reveal new rules."),
                ("—", "Questions", "Whenever nobody can answer something, write it on a pink card and move on. Don't let one question stall the session."),
                ("18–22", "Read the map", "Step back. Many blue cards means the story is big, so split by rule. Many pink cards means it isn't ready yet."),
                ("22–25", "Thumb vote", "Vote: ready to plan, needs splitting, or needs answers. Record the decision, any split, and who owns each question.")],
        sections_title="Reading the map",
        sections_intro="The shape of the finished map tells you what to do next.",
        sections=[("Yellow · Story", AMBER, ["One story per session", "If the group can't agree what it is, stop and clarify the value first"]),
                  ("Blue · Rules", BLUE, ["One per acceptance criterion", "More than 4–5 rules? Split the story by rule", "Rules with no examples aren't understood yet"]),
                  ("Green · Examples", FOREST, ["Concrete: real values and real users", "Given / when / then works well", "They become your acceptance tests"]),
                  ("Pink · Questions", ("#9D174D", "#FCE7F3"), ["Note who will find out, and by when", "Several pink cards means it isn't ready"]),
                  ("Outcome strip", ORANGE, ["Ready, split or needs answers", "Record any split as new stories", "Give every question an owner"])],
        tips=[("Keep to 25 minutes", "The timebox is the point. If you can't finish in 25 minutes, the story is too big or too unclear."),
              ("Examples, not scripts", "Keep examples short and concrete. They're for conversation, not a formal test script."),
              ("Questions are progress", "A pink card is a discovered unknown, so better now than mid-sprint."),
              ("Three amigos minimum", "Business, development and testing perspectives each find different rules and examples."),
              ("Write as you talk", "The facilitator, or the person speaking, writes the card straight away so nothing is lost."),
              ("Use the examples", "Turn green cards into acceptance tests, such as BDD scenarios, so the conversation becomes the specification.")],
        pitfalls=("running past the timebox; debating solutions instead of rules; abstract examples (“a big basket”); "
                  "leaving questions without an owner; mapping several stories at once; starting a story with lots of pink anyway."),
        after=[("Straight away", "Add the rules as acceptance criteria and the examples as test cases on the backlog item."),
               ("Questions", "Owners find the answers before planning. Re-map briefly once they're answered."),
               ("Split stories", "Add new stories from any split to the backlog, and map each one before it's planned."),
               ("During the sprint", "Use the examples as the basis for automated acceptance tests.")],
        toolkit=BREAKDOWN_TOOLKIT,
        foot="“Lots of blue? The story is too big, so split it by rule.”",
    ),
]
GUIDES += BREAKDOWN_GUIDES


LIFECYCLE_TOOLKIT = ("The lifecycle tools follow the work from start to finish: a <a href=\"facilitator-guide-team-charter.html\">Team Charter</a> "
                     "when a team forms, a <a href=\"facilitator-guide-product-vision.html\">Product Vision Board</a> to agree why the product "
                     "exists, the <a href=\"facilitator-guide-prioritisation.html\">Prioritisation Board</a> to decide what comes first, then "
                     "<a href=\"facilitator-guide-sprint-planning.html\">Sprint Planning</a> and <a href=\"facilitator-guide-sprint-review.html\">"
                     "Sprint Review</a> each iteration, with a retrospective from the Retro Kit to close the loop. The break-down tools "
                     "(Epic Canvas, Story Map, Story Splitting, Example Mapping) sit between vision and planning.")

LIFECYCLE_GUIDES = [
    # -------------------------------------------------------------- team charter
    dict(
        slug="team-charter",
        title="Team Charter Guide",
        subtitle="How to help a new or changing team agree its purpose, ways of working, and what Ready and Done mean.",
        tag="Facilitator Run-Sheet · Team Formation · Working Agreements · Definition of Ready & Done",
        boards=[("Open board", "team-charter-board.html"), ("SVG", "team-charter-board.svg")],
        lede="What would make this the best team any of us has worked on?",
        intro=("Teams that skip chartering discover their disagreements later, under delivery pressure. A charter makes the "
               "unwritten rules explicit: <b>why</b> the team exists, who is in it, what it values, how it works and decides, and "
               "the quality bar for starting and finishing work. The team writes it together, so they own it, and revisits it "
               "whenever the team or its work changes."),
        glance=[("Duration", "2–3 h<br>or two sessions"), ("Group", "The whole team,<br>PO included"),
                ("Use when", "A team forms, changes<br>or gets stuck"), ("Output", "An agreed charter<br>on the wall")],
        before=["Print the board at A3 or larger, or load the SVG as a digital background",
                "Ask the sponsor or product owner for a one-line draft of the team's purpose",
                "Gather any existing agreements, Definitions of Done or team norms",
                "Book a space where everyone can contribute, and make sure the whole team can attend",
                "Yellow stickies, markers and dot stickers for voting",
                "Plan an icebreaker that helps people share how they like to work"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–15", "Check-in", "Each person shares one thing that made a past team great, and one thing that made one hard."),
                ("15–40", "1 · Purpose", "Draft the three sentences together. Start with the sponsor's draft and challenge it until everyone could explain it."),
                ("40–55", "2 · Members & Roles", "Each person adds their name, role, and what they bring: skills, experience, interests."),
                ("55–75", "3 · Values", "Silent writing, cluster, then dot-vote down to 3–5 values. Give each value a concrete example."),
                ("75–105", "4 · Working Agreements", "Brainstorm agreements as “We…” statements. Discuss each; keep only those everyone can commit to."),
                ("105–120", "5 · How We Decide · 6 · Ways of Working", "Pick a default decision method and note who decides what. Fill in cadence, tools and channels."),
                ("120–145", "7 · Ready · 8 · Done", "Agree the checklist for starting an item and for calling it done. Keep each to what the team will really check."),
                ("145–160", "9 · Conflict & Review · Close", "Agree how to handle disagreement and when to review. Everyone signs; photograph the board.")],
        sections_title="Making each section strong",
        sections_intro="Quality checks for each part of the charter.",
        sections=[("1 · Purpose", PURPLE, ["Could a stakeholder repeat it?", "Does it name who the team serves?", "Is success observable?"]),
                  ("2 · Members & Roles", BLUE, ["Is everyone listed, part-time members too?", "Are skill gaps visible?"]),
                  ("3 · Values", EMERALD, ["3–5, not 12", "Each has an example of it in action"]),
                  ("4 · Working Agreements", ORANGE, ["Written as “We…”", "Specific enough to notice if broken", "Everyone can commit"]),
                  ("5 · How We Decide", SKY, ["A default method is chosen", "Who decides product, technical and process questions?"]),
                  ("6 · Ways of Working", SLATE, ["Cadence and times are filled in", "One place for the board and the backlog"]),
                  ("7 · Definition of Ready", AMBER, ["Short, and a guide not a gate", "Includes “small enough for an iteration”"]),
                  ("8 · Definition of Done", FOREST, ["Includes testing and review", "Done means releasable"]),
                  ("9 · Conflict & Review", RED, ["A first step when we disagree", "A review trigger is ticked"])],
        tips=[("The team writes it", "A charter handed down by a manager is a policy. Facilitate; don't author."),
              ("Specific beats nice", "“We respect each other” can't be broken. “We reply to review requests within a day” can."),
              ("Decide how you decide", "Many team conflicts are really about decision rights. Settle them before they matter."),
              ("Ready is a guide", "A strict Definition of Ready can become a hand-off gate. Use it to prompt conversation."),
              ("Done grows over time", "Start with what the team can achieve now, and raise the bar at retrospectives."),
              ("Keep it visible", "Pin it up or link it from the team board, and point to it when an agreement is broken.")],
        pitfalls=("a purpose written by someone outside the team; generic values with no examples; dozens of agreements nobody "
                  "remembers; a Definition of Done the team can't meet yet; signing it once and never looking at it again."),
        after=[("Straight away", "Photograph the board and put a copy where the team works, physically or online."),
               ("First retro", "Ask: which agreements are we keeping? Which aren't working? Update the charter."),
               ("When the team changes", "Walk new members through it and invite them to challenge it."),
               ("Every quarter", "Review the purpose and the Definition of Done. Raise the bar if the team is ready.")],
        toolkit=LIFECYCLE_TOOLKIT,
        foot="“Which of these agreements will we find hardest to keep?”",
    ),

    # -------------------------------------------------------------- product vision
    dict(
        slug="product-vision",
        title="Product Vision Board Guide",
        subtitle="How to agree the change a product will bring, who it's for, and how you'll know it's working.",
        tag="Facilitator Run-Sheet · Envision · Inspired by Roman Pichler's Product Vision Board",
        boards=[("Open board", "product-vision-board.html"), ("SVG", "product-vision-board.svg")],
        lede="What will be different for our users when this succeeds?",
        intro=("Without a shared vision, every backlog decision becomes an argument about opinions. The board, based on Roman "
               "Pichler's Product Vision Board, separates the <b>vision</b> (the change you want to bring about) from the "
               "<b>strategy</b> (target group, needs, product and business goals) underneath it. Adding <b>measures of success</b> "
               "and <b>riskiest assumptions</b> turns it into something you can test, not just a statement."),
        glance=[("Duration", "90–120 min"), ("Group", "PO / PM, team reps,<br>key stakeholders"),
                ("Use when", "A new product, or a<br>product that's drifting"), ("Output", "A testable vision<br>&amp; assumptions")],
        before=["Print the board at A3 or larger, or load the SVG as a digital background",
                "Bring evidence: user research, support data, analytics and market information",
                "Invite people who know the users, the business and the technology",
                "Ask the product owner to draft a vision sentence in advance, as a starting point",
                "Yellow and pink stickies, and markers"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "Frame", "Explain the board and the decision it supports. Share the evidence you brought."),
                ("10–25", "1 · Vision", "Write the positive change the product will bring. Not features. Keep it short enough to remember."),
                ("25–45", "2 · Target Group", "Who are the users and customers? Pick the most important group, and say who it's not for."),
                ("45–60", "3 · Needs", "What problem does each group have, and how do they solve it today? Prioritise the main need."),
                ("60–75", "4 · Product", "List the 3–5 things that make the product stand out and meet the main need."),
                ("75–90", "5 · Business Goals", "How does the product help the organisation? Pick the goal that matters most."),
                ("90–105", "6 · Measures of Success", "For the top outcomes, agree a measure, a baseline and a target."),
                ("105–120", "7 · Riskiest Assumptions · Close", "What must be true for this to work? Rank them and agree how to test the riskiest first.")],
        sections_title="Making each section strong",
        sections_intro="Quality checks for each part of the board.",
        sections=[("1 · Vision", PURPLE, ["Describes a change, not a product", "Would still hold if the product changed", "Memorable"]),
                  ("2 · Target Group", BLUE, ["Specific, not “everyone”", "Primary group is clear", "Says who it's not for"]),
                  ("3 · Needs", EMERALD, ["Problems, not features", "Based on evidence where possible"]),
                  ("4 · Product", ORANGE, ["3–5 key features at most", "Each links to a need"]),
                  ("5 · Business Goals", AMBER, ["Ranked", "Measurable over time"]),
                  ("6 · Measures of Success", FOREST, ["Baseline and target for each", "Outcomes, not output"]),
                  ("7 · Riskiest Assumptions", RED, ["Ranked by risk", "Each has a cheap way to test it"])],
        tips=[("Vision before features", "If people describe features in the vision box, ask “and what will that change for users?”"),
              ("One primary user", "Trying to serve everyone equally leads to a product that serves no one well."),
              ("Evidence over opinion", "Mark stickies that are backed by data. Treat the rest as assumptions to test."),
              ("Say who it's not for", "Excluding a group is a strategic choice, and makes later trade-offs easier."),
              ("Measures make it real", "A vision with no measure of success can't be proven wrong, so it can't guide decisions."),
              ("Revisit it", "Bring the board to quarterly planning and update it when evidence changes the picture."),
              ("Basics, performance, delighters", "The Kano model is a useful lens for the Product box: which features users simply expect, which add satisfaction the more you have, and which would delight them?")],
        pitfalls=("a vision that is a feature list; target group “everyone”; needs invented in the room with no evidence; "
                  "skipping measures; treating assumptions as facts; never testing the riskiest assumption."),
        after=[("Straight away", "Photograph the board and share it with stakeholders who weren't there."),
               ("Next week", "Turn the riskiest assumption into a test with the 1% Experiment Canvas or an MVP."),
               ("Then", "Use the Prioritisation Board to decide which needs and features come first."),
               ("Every quarter", "Check the measures of success. Update the board if the evidence has changed.")],
        toolkit=LIFECYCLE_TOOLKIT,
        foot="“Who is this not for?”",
    ),

    # -------------------------------------------------------------- prioritisation
    dict(
        slug="prioritisation",
        title="Prioritisation Board Guide",
        subtitle="How to compare options by value, effort and cost of delay, agree scope, and build a Now / Next / Later roadmap.",
        tag="Facilitator Run-Sheet · Plan · Value vs. Effort · Cost of Delay (WSJF) · MoSCoW · Now / Next / Later",
        boards=[("Open board", "prioritisation-board.html"), ("SVG", "prioritisation-board.svg")],
        lede="What does it cost us, each week, to not have this yet?",
        intro=("Most teams have more good ideas than capacity. The board combines four complementary techniques: a quick "
               "<b>value vs. effort</b> grid to sort many items, <b>cost of delay</b> to rank the top few with numbers (CD3 from Don "
               "Reinertsen, which SAFe calls <b>WSJF</b>, Weighted Shortest Job First), <b>MoSCoW</b> to agree scope for a fixed date, and a <b>Now / Next / Later</b> roadmap to share the "
               "result. Use the parts you need: a quick sort might only use the grid and the roadmap."),
        glance=[("Duration", "60–120 min"), ("Group", "PO / PM, team reps,<br>stakeholders"),
                ("Use when", "Quarterly planning, or<br>too many priorities"), ("Output", "A ranked list &amp;<br>a roadmap")],
        before=["Print the board at A3 or larger, or load the SVG as a digital background",
                "List the candidate items in advance: epics, features or outcomes, one per sticky",
                "Bring any data on value: customer demand, revenue, risk, deadlines",
                "Invite the people who decide priorities, and team members who can judge effort",
                "Agree who makes the final call if the group can't agree (usually the product owner)"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "Frame", "Recap the product goal or vision. Agree the scope: which items, and for what time horizon."),
                ("10–35", "1 · Value vs. Effort", "Place each sticky on the grid. Compare items to each other, not to an absolute scale. Discuss the outliers."),
                ("35–60", "2 · Cost of Delay (WSJF)", "Take the top 5–8 items. Score one column at a time across all items: value, then time criticality, then risk reduction. The smallest item in each column scores 1. Add them up for the cost of delay, divide by job size and rank."),
                ("60–75", "3 · MoSCoW", "If there's a fixed date or release, sort the ranked items into Must, Should, Could and Won't (this time)."),
                ("75–100", "4 · Now · Next · Later", "Place the items on the roadmap and write the outcome for each column. Only Now is committed."),
                ("100–110", "Close", "Read the roadmap back. Confirm the decision owner agrees, and who will share it with stakeholders.")],
        sections_title="Using each technique well",
        sections_intro="What each part is for, and what to watch for.",
        sections=[("1 · Value vs. Effort", BLUE, ["Relative placement is enough", "Big bets: slice before committing", "Drop the money pits"]),
                  ("2 · Cost of Delay (WSJF)", PURPLE, ["One column at a time, across all items", "Smallest item scores 1 in each column", "CoD / job size gives the order"]),
                  ("3 · MoSCoW", ORANGE, ["Musts should be about 60% of capacity", "Won't means not this time", "Needs a fixed date or scope"]),
                  ("4 · Now · Next · Later", FOREST, ["Outcomes, not dates", "Now is committed; Later is options", "Keep Next short"])],
        tips=[("Compare, don't score in isolation", "Ask “is this more or less valuable than that?” Relative judgements are faster and more reliable."),
              ("Make delay visible", "Ask what it costs each week not to have an item. Time-critical work often moves up."),
              ("Slice the big bets", "High-value, high-effort items usually hide a smaller, high-value slice. Use the Epic Canvas or Story Map."),
              ("Protect the Could list", "If everything is a Must, MoSCoW stops working. Push back until Musts fit comfortably."),
              ("One decision owner", "The group advises; one person decides. Say who before you start."),
              ("Roadmaps change", "Review Now / Next / Later every iteration or month. Moving items is learning, not failure."),
              ("Other scoring models", "RICE (reach × impact × confidence, divided by effort) suits teams with usage data; the Kano model sorts features into basics, performance and delighters. Pick one model and use it consistently.")],
        pitfalls=("scoring all of one item's columns before moving to the next (score one column across every item instead); scoring items in isolation; letting the loudest stakeholder set the order; everything as a Must; "
                  "a roadmap full of dates and features instead of outcomes; using cost of delay for 50 items; never revisiting it."),
        after=[("Straight away", "Photograph the board. Update the backlog order and the roadmap in your tools."),
               ("Share it", "Walk stakeholders through the roadmap and the reasons for the order."),
               ("Next", "Break the Now items down with the Epic Canvas and Story Map, ready for Sprint Planning."),
               ("Regularly", "Revisit the order at each Sprint Review, when feedback and data change the picture.")],
        toolkit=LIFECYCLE_TOOLKIT,
        foot="“If we could only do one thing this quarter, what would it be?”",
    ),

    # -------------------------------------------------------------- sprint planning
    dict(
        slug="sprint-planning",
        title="Sprint Planning Guide",
        subtitle="How to agree a sprint goal, size the work to real capacity, and leave with a plan the team believes in.",
        tag="Facilitator Run-Sheet · Build in Iterations · Sprint Goal · Capacity · Confidence Vote",
        boards=[("Open board", "sprint-planning-board.html"), ("SVG", "sprint-planning-board.svg")],
        lede="If we only achieve one thing this sprint, what should it be?",
        intro=("Planning that is just dragging tickets into a sprint produces a list, not a plan. The board puts the "
               "<b>sprint goal</b> first, checks the work against <b>real capacity</b>, splits items into those needed for the goal "
               "and those that are also planned, and ends with a <b>confidence vote</b> so concerns surface before the sprint starts, "
               "not halfway through. It works for any iteration length. Scrum calls this event Sprint Planning."),
        glance=[("Duration", "1–2 h for a<br>2-week sprint"), ("Group", "The whole team,<br>PO included"),
                ("Use when", "The start of every<br>iteration"), ("Output", "A goal, a forecast<br>&amp; a first-day plan")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Make sure the top of the backlog is refined and ordered (Example Mapping helps)",
                "Know who is away, and the team's throughput or velocity for the last three sprints",
                "Bring the last Sprint Review's feedback and the last retro's actions",
                "Yellow and pink stickies, markers, and the team's Definition of Done"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "Context", "The PO shares the product goal, recent feedback, and what's at the top of the backlog. Check the inputs."),
                ("10–25", "1 · Sprint Goal", "Draft a goal that explains why the sprint is valuable. Agree how you'll know it's achieved."),
                ("25–35", "2 · Capacity", "Count working days, absences and other commitments. Compare with recent throughput."),
                ("35–65", "4 · Selected Items", "Pull items in priority order into “Needed for the goal”, then “Also planned”. Stop at capacity."),
                ("65–80", "5 · Risks & Dependencies", "What could stop the goal? Who outside the team is needed, and when? Agree actions."),
                ("80–90", "6 · How We'll Start", "Agree what starts on day one, who pairs or swarms, and the first thing to finish."),
                ("90–95", "7 · Confidence Vote", "Fist of five. Anyone at 1 or 2 explains why; adjust the plan and re-vote.")],
        sections_title="Making each section strong",
        sections_intro="Quality checks for each part of the board.",
        sections=[("1 · Sprint Goal", PURPLE, ["One objective, not a list of items", "Says why, not just what", "Linked to the product goal"]),
                  ("2 · Capacity", BLUE, ["Absences are counted", "Based on recent throughput, not hope"]),
                  ("3 · Inputs Checked", EMERALD, ["Review feedback and retro actions included", "The top items are ready"]),
                  ("4 · Selected Items", ORANGE, ["Goal items come first", "Room left for unplanned work", "Items are small"]),
                  ("5 · Risks & Dependencies", RED, ["Each risk has an action", "External people know they're needed"]),
                  ("6 · How We'll Start", SKY, ["Focus on finishing, not starting everything", "Pairing or swarming planned"]),
                  ("7 · Confidence Vote", FOREST, ["Low votes are explored, not overruled", "Re-vote after changes"])],
        tips=[("Goal first, items second", "Agree why the sprint matters before choosing items. The goal guides trade-offs mid-sprint."),
              ("Plan to recent reality", "Use the last three sprints' throughput. Planning to an ideal leads to carry-over and lost trust."),
              ("Leave slack", "Plan to about 80% of capacity. Unplanned work always arrives."),
              ("It's a forecast", "The team commits to the goal, not to every item. Say so out loud."),
              ("Plan the start", "A clear first day stops everyone starting a different item at once."),
              ("Respect low votes", "A 1 or a 2 is information. Ask what would raise it, and adjust the plan.")],
        pitfalls=("no sprint goal, or a goal that just lists items; ignoring absences; planning to 100% capacity; the PO assigning work "
                  "to people; skipping the confidence vote; carrying over unfinished work without discussion."),
        after=[("Straight away", "Put the goal on the team board and update the backlog tool. Photograph the board."),
               ("Every day", "At the daily sync, ask: are we on track for the sprint goal? What's blocking it?"),
               ("Mid-sprint", "If the goal is at risk, renegotiate scope with the PO early. Don't wait for the review."),
               ("End of sprint", "Bring the goal to the Sprint Review and the retro: did we achieve it, and why?")],
        toolkit=LIFECYCLE_TOOLKIT,
        foot="“What would stop us from reaching the goal?”",
    ),

    # -------------------------------------------------------------- sprint review
    dict(
        slug="sprint-review",
        title="Sprint Review Guide",
        subtitle="How to inspect what was built with stakeholders, gather real feedback, and adapt the backlog together.",
        tag="Facilitator Run-Sheet · Review & Release · Inspect the Increment · Adapt the Backlog",
        boards=[("Open board", "sprint-review-board.html"), ("SVG", "sprint-review-board.svg")],
        lede="Based on what we've seen, what should we do next?",
        intro=("A review is a working session, not a demo. The team shows working product that meets the Definition of Done, "
               "stakeholders say what they think, and everyone looks at what has changed around the product. The output is "
               "a <b>changed backlog</b> and a clear view of what's next. If nothing in the backlog changes, the review didn't do "
               "its job. Scrum calls this event the Sprint Review."),
        glance=[("Duration", "45–90 min for a<br>2-week sprint"), ("Group", "Team, PO and<br>stakeholders"),
                ("Use when", "The end of every<br>iteration"), ("Output", "Feedback &amp; an<br>updated backlog")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Invite the stakeholders whose feedback matters most, including users if you can",
                "Prepare working product to show, in an environment people can try themselves",
                "Gather the data for key measures: before, now and target",
                "Green, pink, blue and yellow stickies, and markers",
                "Ask the PO to prepare a short update on the backlog, release and forecast"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–5", "Welcome", "Explain the purpose: to inspect the product and decide what's next together, not to approve work."),
                ("5–10", "1 · Sprint Goal & Result", "The PO states the goal and whether it was achieved. Be honest about what wasn't done."),
                ("10–15", "2 · Key Measures", "Share the numbers that matter. Did the last release move them?"),
                ("15–40", "3 · What We Built", "Team members show working product. Let stakeholders try it. Only Done work is shown."),
                ("—", "4 · Stakeholder Feedback", "Throughout the demo, stakeholders add green, pink and blue stickies. Ask questions; don't defend."),
                ("40–50", "5 · What's Changed", "What's new in the market, with users, budget or timelines? How does it affect the plan?"),
                ("50–65", "6 · Backlog Changes", "Turn feedback and changes into backlog additions, changes and removals. The PO decides."),
                ("65–75", "7 · What's Next · Close", "Share the likely next goal and any forecast update. Agree decisions needed and who follows up.")],
        sections_title="Making each section strong",
        sections_intro="Quality checks for each part of the board.",
        sections=[("1 · Sprint Goal & Result", PURPLE, ["An honest answer: yes, partly or no", "What we learned is captured"]),
                  ("2 · Key Measures", BLUE, ["Outcomes, not just velocity", "Before, now and target shown"]),
                  ("3 · What We Built", EMERALD, ["Only Done work", "Working product, not slides", "Stakeholders try it"]),
                  ("4 · Stakeholder Feedback", ORANGE, ["Concerns are welcomed", "Ideas are captured, not promised"]),
                  ("5 · What's Changed", SKY, ["Market, users, budget, timeline", "Impact on priorities discussed"]),
                  ("6 · Backlog Changes", AMBER, ["Something changed", "Removals are allowed", "The PO decides"]),
                  ("7 · What's Next", FOREST, ["Next goal is shared", "Decisions have an owner"])],
        tips=[("Not a demo", "If stakeholders only watch, you'll get politeness, not feedback. Hand them the product."),
              ("Show Done only", "Showing unfinished work creates false expectations. Mention it, but don't demo it."),
              ("Invite the right people", "A review with no stakeholders is just a team meeting. Chase the people whose opinion matters."),
              ("Listen, don't defend", "Write every piece of feedback down, especially the uncomfortable ones."),
              ("Change the backlog", "End by showing what changed. It proves the feedback was heard."),
              ("Keep it short and regular", "Same time each sprint, tight timebox. Stakeholders come back when it's useful.")],
        pitfalls=("a one-way demo with no feedback; showing work that isn't Done; no stakeholders present; defending every "
                  "criticism; promising every idea; no backlog changes at the end; a status report instead of working product."),
        after=[("Straight away", "Update the backlog with the agreed changes and share the board with anyone who missed it."),
               ("Follow up", "Owners chase the decisions needed from stakeholders before Sprint Planning."),
               ("Retro", "Bring anything about how the team worked to the retrospective, which usually comes next."),
               ("Next planning", "Use the feedback and backlog changes as inputs for the next sprint goal.")],
        toolkit=LIFECYCLE_TOOLKIT,
        foot="“What surprised you today?”",
    ),
]
GUIDES += LIFECYCLE_GUIDES


PROJECT_TOOLKIT = ("The project tools work together: run a <a href=\"facilitator-guide-project-kickoff.html\">Project Kickoff</a> first, "
                   "then build the <a href=\"facilitator-guide-stakeholder-map.html\">Stakeholder Map</a>, keep the "
                   "<a href=\"facilitator-guide-raid-log.html\">RAID Log</a> up to date, and refresh the "
                   "<a href=\"facilitator-guide-release-forecast.html\">Release Forecast</a> after every iteration. Inside the project, teams use "
                   "the lifecycle tools (Team Charter, Prioritisation, Sprint Planning and Review) and the break-down tools.")

PROGRAM_TOOLKIT = ("The program tools coordinate several teams: agree <a href=\"facilitator-guide-okr.html\">Objectives &amp; Key Results</a>, "
                   "plan together with the <a href=\"facilitator-guide-cross-team-planning.html\">Cross-Team Planning</a> board, make links "
                   "visible on the <a href=\"facilitator-guide-dependency-map.html\">Dependency Map</a>, and keep in step with a regular "
                   "<a href=\"facilitator-guide-cross-team-sync.html\">Cross-Team Sync</a>. Each team still plans, reviews and improves with "
                   "the team-level tools.")

PP_GUIDES = [
    # -------------------------------------------------------------- project kickoff
    dict(
        slug="project-kickoff",
        title="Project Kickoff Guide",
        subtitle="How to start an agile project with a shared why, clear scope, agreed trade-offs and named people.",
        tag="Facilitator Run-Sheet · Run a Project · Inception · Scope In & Out · Trade-off Sliders",
        boards=[("Open board", "project-kickoff-board.html"), ("SVG", "project-kickoff-board.svg")],
        lede="If we had to cut half the scope, what would we keep?",
        intro=("Projects that start with a plan but no shared understanding pay for it later. The kickoff board gets the sponsor, "
               "product owner and team to agree <b>why</b> the project exists, what's <b>in and out</b> of scope, which of scope, "
               "time, budget, quality and team size can <b>flex</b>, the constraints, the people, the biggest worries, and the first "
               "milestones. It draws on the inception deck idea from Jonathan Rasmusson's <i>The Agile Samurai</i>."),
        glance=[("Duration", "2–3 h"), ("Group", "Sponsor, PO, team,<br>key stakeholders"),
                ("Use when", "A project or major<br>initiative starts"), ("Output", "A shared start:<br>scope, trade-offs, people")],
        before=["Print the board at A3 or larger, or load the SVG as a digital background",
                "Ask the sponsor to come ready to explain why the project matters now",
                "Gather any business case, contract, deadlines or budget constraints",
                "Invite the people who will do the work, not just those who approved it",
                "Yellow and pink stickies, markers and dot stickers"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "Welcome", "Purpose of the session, and introductions. Explain that disagreement now is cheaper than later."),
                ("10–30", "1 · Why Are We Here?", "The sponsor explains the problem. The group writes the two sentences together until everyone agrees."),
                ("30–55", "2 · Scope", "List what's in and, just as importantly, what's out. Anything disputed goes to the sponsor to decide."),
                ("55–80", "3 · Trade-off Sliders", "For each row, agree how fixed it is. Only one can be fully fixed. Discuss what gives when plans change."),
                ("80–95", "4 · Constraints · 5 · People", "List the givens. Name the sponsor, product owner, delivery lead, teams, experts and decision forum."),
                ("95–115", "6 · What Keeps Us Up at Night", "Silent writing of risks and worries, then cluster. Move the biggest to the RAID Log."),
                ("115–135", "7 · First Milestones", "Agree 3–6 milestones described as outcomes, with target dates as ranges where possible."),
                ("135–150", "8 · Next Steps · Close", "Tick which tools come next and who owns them. Agree when to review this board.")],
        sections_title="Making each section strong",
        sections_intro="Quality checks for each part of the board.",
        sections=[("1 · Why Are We Here?", PURPLE, ["A problem, not a solution", "Success is observable"]),
                  ("2 · Scope", BLUE, ["Out of scope is as long as in scope", "Disputes have a decision owner"]),
                  ("3 · Trade-off Sliders", ORANGE, ["Only one fully fixed", "Everyone can say what flexes first"]),
                  ("4 · Constraints & Givens", SLATE, ["Real constraints, not preferences", "Each has a source"]),
                  ("5 · People & Roles", SKY, ["One accountable sponsor", "One product owner", "A named decision forum"]),
                  ("6 · What Keeps Us Up at Night", RED, ["Worries are spoken, not hidden", "Big ones go to the RAID Log"]),
                  ("7 · First Milestones", FOREST, ["Outcomes, not tasks", "Early ones test the riskiest parts"]),
                  ("8 · Next Steps", EMERALD, ["Each next step has an owner", "A review date is set"])],
        tips=[("Start with why", "If the group can't agree the problem, stop there. Everything else depends on it."),
              ("Make out-of-scope visible", "Saying what you won't do surfaces hidden expectations before they become complaints."),
              ("Sliders force honesty", "If someone wants every slider at Fixed, ask what should happen when the plan meets reality."),
              ("Invite the doers", "The team spots risks and constraints the sponsors can't see."),
              ("Milestones as outcomes", "“Customers can pay online” beats “payment module complete”."),
              ("Keep it alive", "Bring the board to reviews. Update it when scope, people or trade-offs change.")],
        pitfalls=("a sponsor who presents and leaves; no out-of-scope list; every slider fixed; milestones that are tasks; "
                  "ignoring the worries; treating the board as sign-off rather than a starting point."),
        after=[("Straight away", "Photograph the board and share it with everyone involved, including those who missed it."),
               ("This week", "Run the Team Charter, Product Vision Board and Stakeholder Map sessions."),
               ("First iteration", "Set up the RAID Log and the Release Forecast, and plan the first slice."),
               ("Each month", "Review the board: has the why, scope or any trade-off changed?")],
        toolkit=PROJECT_TOOLKIT,
        foot="“What problem are we solving, and for whom?”",
    ),

    # -------------------------------------------------------------- stakeholder map
    dict(
        slug="stakeholder-map",
        title="Stakeholder Map Guide",
        subtitle="How to identify the people who affect or are affected by the work, and plan how to involve each of them.",
        tag="Facilitator Run-Sheet · Run a Project · Influence vs. Interest · Communication Plan",
        boards=[("Open board", "stakeholder-map-board.html"), ("SVG", "stakeholder-map-board.svg")],
        lede="Who could stop this, and what do they need from us?",
        intro=("Agile work depends on fast feedback and clear decisions, and both depend on the right people being involved. "
               "The map places each stakeholder by <b>influence</b> and <b>interest</b>, which suggests how closely to involve "
               "them. The <b>register</b> records what each one wants and worries about, and the <b>communication plan</b> turns "
               "that into a regular rhythm. Watch-outs capture who might block the work and who is missing."),
        glance=[("Duration", "60–90 min"), ("Group", "PO, delivery lead,<br>sponsor, team reps"),
                ("Use when", "At kickoff, then<br>every month or so"), ("Output", "A map, a register<br>&amp; a comms plan")],
        before=["Print the board at A3 or larger, or load the SVG as a digital background",
                "List known stakeholders in advance: sponsors, users, customers, other teams, suppliers, regulators",
                "Bring an org chart if the organisation is large or new to the team",
                "Yellow and pink stickies and markers",
                "Agree that the map may be sensitive, and decide who it will be shared with"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–15", "Brainstorm", "Write one stakeholder per yellow sticky: people and groups. Ask “who is affected?” as well as “who decides?”"),
                ("15–35", "1 · Place them", "Place each sticky on the grid by influence and interest. Compare them to each other and discuss disagreements."),
                ("35–55", "2 · Register", "For the Manage Closely and Keep Satisfied groups first, write what they want, what worries them, and how you'll engage."),
                ("55–75", "3 · Communication Plan", "Group stakeholders into audiences. Agree what each needs, the format, the frequency and the owner."),
                ("75–85", "4 · Watch-outs", "Who could block this? Who is missing? Add pink stickies and agree actions."),
                ("85–90", "Close", "Agree who keeps the map up to date and when it's next reviewed.")],
        sections_title="What each quadrant means",
        sections_intro="Where a stakeholder sits suggests how to involve them, but always ask what they want too.",
        sections=[("Manage Closely", RED, ["Involve in key decisions", "Meet regularly", "Surprises here are costly"]),
                  ("Keep Satisfied", AMBER, ["Consult on what matters to them", "Short, focused updates"]),
                  ("Keep Informed", EMERALD, ["Regular updates", "Invite to reviews", "Great source of feedback"]),
                  ("Monitor", SLATE, ["Light-touch updates", "Watch for changes in interest"]),
                  ("Register & Comms Plan", PURPLE, ["Every Manage Closely stakeholder has an owner", "Formats match how people like to hear"])],
        tips=[("Think beyond the org chart", "Users, support staff, other teams and suppliers are stakeholders too."),
              ("Influence isn't just rank", "Some people have little authority but a lot of influence. Place them honestly."),
              ("Ask, don't assume", "Check what stakeholders want by talking to them, not by guessing in the room."),
              ("Reviews are engagement", "Invite Keep Informed and Manage Closely stakeholders to Sprint Reviews."),
              ("Move people", "Interest and influence change. Re-map monthly or when something big shifts."),
              ("Handle with care", "Notes about individuals can be sensitive. Agree where the board is kept.")],
        pitfalls=("only listing senior people; mapping once and never again; a comms plan that's just “monthly status report”; "
                  "writing unkind notes about individuals; nobody owning the relationship with key stakeholders."),
        after=[("Straight away", "Store the board where the agreed audience can see it, and nowhere else."),
               ("This week", "Owners contact their key stakeholders to check the register is right."),
               ("Every iteration", "Use the communication plan; invite the right people to the Sprint Review."),
               ("Monthly", "Review the map and move stakeholders as their interest or influence changes.")],
        toolkit=PROJECT_TOOLKIT,
        foot="“Who will be affected by this, and have we asked them?”",
    ),

    # -------------------------------------------------------------- release forecast
    dict(
        slug="release-forecast",
        title="Release Forecast Guide",
        subtitle="How to forecast a release date as a range, using a burn-up chart and the team's real throughput.",
        tag="Facilitator Run-Sheet · Run a Project · Burn-up · Throughput Forecasting · Ranges, Not Dates",
        boards=[("Open board", "release-forecast-board.html"), ("SVG", "release-forecast-board.svg")],
        lede="When will it be done? Here's the range, and here's what it depends on.",
        intro=("A single delivery date is a guess presented as a fact. The forecast board uses what the team has <b>actually "
               "finished</b> each iteration to give a <b>range</b>: slow, likely and fast. The <b>burn-up chart</b> shows done work "
               "rising toward a total-scope line, so scope growth is visible rather than hidden. Counting items usually works as "
               "well as story points if items are similar in size. For more precision, a Monte Carlo simulation can use the same data."),
        glance=[("Duration", "30–45 min<br>to set up"), ("Group", "PO, delivery lead,<br>team rep"),
                ("Use when", "A release or project<br>with a target date"), ("Output", "A dated range<br>&amp; its assumptions")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Collect done items per iteration for at least the last 3–5 iterations (more is better)",
                "Count the items remaining in the release, and estimate how much scope usually grows",
                "Agree whether you're counting items or points, and stick to it",
                "Bring the iteration calendar so you can turn iterations into dates"],
        agenda_heads=["Time", "Step", "Facilitator notes"],
        agenda=[("0–10", "2 · Throughput Data", "Fill in done, added and total scope for each past iteration. Work out the average, slowest 3 and fastest 3."),
                ("10–20", "1 · Burn-up Chart", "Set the scale, plot the done line and the total scope line, and draw the fast and slow forecast lines forward."),
                ("20–30", "3 · The Forecast", "Divide remaining items by each rate to get iterations left, then convert to dates. Share all three."),
                ("30–40", "4 · What Would Change It", "List what would move the forecast: scope growth, people changes, dependencies. Agree when to update it."),
                ("Every iteration", "Update", "Add the latest iteration, re-plot, and re-forecast. Share the new range and what changed.")],
        sections_title="Reading the board",
        sections_intro="What each part tells you.",
        sections=[("1 · Burn-up Chart", BLUE, ["Gap between lines = work left", "Rising scope line = growth", "Lines not meeting = not converging"]),
                  ("2 · Throughput Data", EMERALD, ["Use real data, not targets", "Note unusual iterations"]),
                  ("3 · The Forecast", AMBER, ["Always share the range", "Likely isn't a promise"]),
                  ("4 · What Would Change It", RED, ["Assumptions are explicit", "An update date is set"])],
        tips=[("Ranges build trust", "A range that holds is more useful than a date that slips. Explain why there's a range."),
              ("Show the scope line", "Burn-down charts hide scope growth. Burn-ups make it visible, so trade-offs become a conversation."),
              ("Count items", "If items are roughly similar in size, counting them is simpler than points and just as accurate."),
              ("Include growth", "Scope almost always grows. Add the team's usual growth rate to the remaining work."),
              ("Re-forecast often", "Update every iteration. The range narrows as you learn."),
              ("Don't push the rate", "If the forecast is too late, change scope or the date. Asking the team to “go faster” just adds risk.")],
        pitfalls=("sharing only the likely date; using a target velocity instead of real data; hiding scope growth; forecasting "
                  "from one iteration; treating the forecast as a commitment; never updating it."),
        after=[("Straight away", "Share the range and assumptions with the sponsor and key stakeholders."),
               ("Every iteration", "Update the data, re-plot the chart and re-forecast."),
               ("At the Sprint Review", "Show the burn-up chart. Discuss scope trade-offs if the range moves."),
               ("If the range slips", "Act early: cut scope, remove a dependency, or agree a new date range.")],
        toolkit=PROJECT_TOOLKIT,
        foot="“What would have to be true for the fast forecast to happen?”",
    ),

    # -------------------------------------------------------------- RAID log
    dict(
        slug="raid-log",
        title="RAID Log Guide",
        subtitle="How to keep a project's risks, assumptions, issues and dependencies visible, owned and acted on.",
        tag="Facilitator Run-Sheet · Run a Project · Risks · Assumptions · Issues · Dependencies",
        boards=[("Open board", "raid-log-board.html"), ("SVG", "raid-log-board.svg")],
        lede="What's the risk we're not talking about?",
        intro=("A RAID log brings four kinds of uncertainty into one view. <b>Risks</b> might happen; <b>assumptions</b> are "
               "believed but unproven; <b>issues</b> are happening now; <b>dependencies</b> are what you need from others, or they "
               "need from you. Keeping it on a board, reviewed every iteration, stops it becoming a spreadsheet nobody opens."),
        glance=[("Duration", "45 min to set up<br>15 min to review"), ("Group", "PO, delivery lead,<br>team reps"),
                ("Use when", "Any project with<br>real uncertainty"), ("Output", "Owned risks, tests<br>&amp; actions")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Bring the worries from the Project Kickoff and any existing risk register",
                "Bring the Dependency Map if you work with other teams",
                "Agree the scales: likelihood and impact as high / medium / low"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–15", "R · Risks", "List what might happen. Rate likelihood and impact. For the high ones, agree a response: avoid, reduce, transfer or accept."),
                ("15–25", "A · Assumptions", "What are we treating as true without evidence? Agree how and when to test the riskiest."),
                ("25–35", "I · Issues", "What's going wrong now? Agree the impact, an action, an owner and a due date."),
                ("35–45", "D · Dependencies", "What do we need from others, or they from us? Record who, by when, and the status."),
                ("Every iteration", "Review (15 min)", "Walk each quadrant: what's new, what's changed, what's closed? Move risks that happened to Issues.")],
        sections_title="Making each quadrant useful",
        sections_intro="Quality checks for each part of the log.",
        sections=[("R · Risks", RED, ["Written as cause → effect", "High risks have a response", "Each has an owner"]),
                  ("A · Assumptions", AMBER, ["Each has a test", "Proven or disproven ones are closed"]),
                  ("I · Issues", ORANGE, ["An action and a due date", "Escalated when the team can't fix it"]),
                  ("D · Dependencies", BLUE, ["Named teams and dates", "Status kept current", "The other side knows"])],
        tips=[("Cause and effect", "“If the supplier API is late, then integration testing slips” is actionable. “Supplier risk” isn't."),
              ("Test assumptions", "An untested assumption is a risk in disguise. Use the 1% Experiment Canvas for the big ones."),
              ("Owners, not committees", "Every row needs one named person who will act."),
              ("Keep it short", "If the log has 80 rows, nobody reads it. Close, merge and prioritise."),
              ("Review in the open", "A short review in the team's regular rhythm keeps it current and shared."),
              ("Escalate early", "Issues the team can't solve go to the decision forum straight away."),
              ("ROAM for shared risks", "In multi-team planning, SAFe sorts each risk as Resolved, Owned, Accepted or Mitigated. It's a quick way to make sure every risk ends with a decision.")],
        pitfalls=("vague risks with no cause or effect; no owners; never closing items; reviewing only at steering meetings; "
                  "assumptions that are never tested; dependencies the other team doesn't know about."),
        after=[("Straight away", "Photograph the board or move it into your tool. Tell owners what they own."),
               ("Every iteration", "Review in 15 minutes: new, changed, closed."),
               ("Monthly", "Share the top risks and issues with the sponsor, with the actions being taken."),
               ("At the end", "Review what happened. Which risks came true? What would you watch for next time?")],
        toolkit=PROJECT_TOOLKIT,
        foot="“Which assumption, if wrong, would hurt us most?”",
    ),

    # -------------------------------------------------------------- cross-team planning
    dict(
        slug="cross-team-planning",
        title="Cross-Team Planning Guide",
        subtitle="How to plan a period of work across several teams, so shared objectives, dependencies and risks are agreed together.",
        tag="Facilitator Run-Sheet · Coordinate Teams · Big-Room Planning · Shared Objectives",
        boards=[("Open board", "cross-team-planning-board.html"), ("SVG", "cross-team-planning-board.svg")],
        lede="What will we achieve together that no team could achieve alone?",
        intro=("When several teams work on one product or outcome, planning in isolation creates surprises. Cross-team planning, "
               "often called <b>big-room planning</b> (SAFe calls it PI Planning), brings the teams together to agree <b>shared "
               "objectives</b>, build each team's plan for the coming iterations, place <b>milestones</b>, surface risks and needs, "
               "and agree a <b>capacity split</b>. It ends with a confidence vote, so the plan is one everyone believes in."),
        glance=[("Duration", "Half a day to<br>two days"), ("Group", "All teams, POs,<br>leaders, key experts"),
                ("Use when", "Every quarter or<br>planning period"), ("Output", "Objectives, team plans<br>&amp; known risks")],
        before=["Print the board at A1 or A0, or use a digital board. One board for the whole group",
                "Prepare the vision, the top priorities and the shared objectives in draft",
                "Each team brings its refined backlog and its capacity for each iteration",
                "Bring the Dependency Map and RAID Log, or plan to start them on the day",
                "Book a room or video setup where teams can work separately and come back together",
                "Agree the decision-maker for trade-offs between teams"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–30", "Context", "Leaders share the vision, the priorities and any fixed dates. Fill in 2 · Context & Constraints."),
                ("30–60", "1 · Shared Objectives", "Present the draft objectives and their value. Teams ask questions; adjust if needed."),
                ("60–180", "3 · Team Plans (breakouts)", "Each team plans its row: what will be done in each iteration, risks and needs. Place milestones."),
                ("180–210", "Dependencies", "Teams walk the board together and link dependencies on the Dependency Map. Resolve conflicts."),
                ("210–240", "5 · Risks · 6 · Capacity", "Review risks to the plan and agree a response for each. Confirm the capacity split."),
                ("240–255", "4 · Confidence Vote", "Fist of five for the whole plan. Explore low votes, adjust and re-vote.")],
        sections_title="Making each section strong",
        sections_intro="Quality checks for each part of the board.",
        sections=[("1 · Shared Objectives", PURPLE, ["Few, outcome-based", "Each has a business value", "Teams named against each"]),
                  ("2 · Context & Constraints", SLATE, ["Fixed dates are real", "Capacity changes are known"]),
                  ("3 · Team Plans", BLUE, ["Each team planned its own row", "Last iteration has slack", "Milestones placed"]),
                  ("4 · Confidence Vote", FOREST, ["Every team votes", "Low votes change the plan"]),
                  ("5 · Risks to the Plan", RED, ["Each has an owner and response", "Sort them ROAM: resolved, owned, accepted, mitigated", "Big ones go to the RAID Log"]),
                  ("6 · Capacity Split", SKY, ["Agreed before planning", "Includes a buffer for unplanned work"])],
        tips=[("Teams plan their own work", "Leaders set objectives and priorities. Teams decide how much they can do."),
              ("Plan to capacity, not hope", "Use each team's real throughput. Leave the last iteration lighter for catch-up and improvement."),
              ("Dependencies in the open", "Walking the board together finds dependencies no single team saw."),
              ("Keep objectives few", "More than 5–7 shared objectives usually means there's no real priority."),
              ("Decide trade-offs in the room", "Have the decision-maker present, so conflicts are settled on the day."),
              ("Respect the vote", "A low-confidence plan is a plan to fail. Re-plan until confidence is reasonable.")],
        pitfalls=("leaders dictating team plans; planning to 100% capacity; objectives that are feature lists; dependencies "
                  "found after planning; no decision-maker present; ignoring a low confidence vote."),
        after=[("Straight away", "Photograph the board. Teams load their plans into their tools; publish the objectives."),
               ("Every week or two", "Run the Cross-Team Sync to track progress, dependencies and impediments."),
               ("Mid-period", "Check progress against the shared objectives; adjust plans if needed."),
               ("End of period", "Hold a joint review and a cross-team retrospective before the next planning.")],
        toolkit=PROGRAM_TOOLKIT,
        foot="“Which dependency, if it slips, takes the plan with it?”",
    ),

    # -------------------------------------------------------------- dependency map
    dict(
        slug="dependency-map",
        title="Dependency Map Guide",
        subtitle="How to make cross-team dependencies visible, track them, and find ways to remove them.",
        tag="Facilitator Run-Sheet · Coordinate Teams · Dependency Board · Red String",
        boards=[("Open board", "dependency-map-board.html"), ("SVG", "dependency-map-board.svg")],
        lede="Which dependency could we remove instead of managing?",
        intro=("Dependencies are one of the main reasons multi-team work runs late. The <b>dependency board</b> shows each team's "
               "work by iteration, with a red string linking each item to the team it depends on. Strings that run backwards "
               "in time, or that cross many teams, are the danger signs. The <b>register</b> tracks status and owners, and the "
               "<b>reduce</b> panel prompts the group to remove dependencies, not just manage them."),
        glance=[("Duration", "45–60 min, or as<br>part of planning"), ("Group", "A rep from each team,<br>POs, delivery leads"),
                ("Use when", "Cross-team planning,<br>then every sync"), ("Output", "Visible, owned<br>dependencies")],
        before=["Print the board at A1 or larger, or use a digital board with connectors",
                "Each team brings its planned items for the period",
                "Yellow, blue and pink stickies, red string or wool and tape (or digital connectors)",
                "Write the team names and iteration dates on the board in advance"],
        agenda_heads=["Time", "Step", "Facilitator notes"],
        agenda=[("0–15", "Place work", "Each team places its key items (yellow) in its row, in the iteration it plans to finish them."),
                ("15–30", "Add dependencies", "For each item that needs another team, add a blue sticky in the providing team's row, in the iteration it's needed. Link with red string."),
                ("30–40", "Spot problems", "Look for strings that point backwards in time, cross many teams, or land in a full iteration. Mark them pink."),
                ("40–50", "2 · Register", "Record each dependency: who needs it, who provides it, what, by when, status and owner."),
                ("50–60", "3 · Reduce", "For the riskiest dependencies, work through the reduce checklist. Agree the top one to remove.")],
        sections_title="Reading the board",
        sections_intro="Patterns that tell you where the risk is.",
        sections=[("Backwards strings", RED, ["Needed before it's planned", "Re-plan one side now"]),
                  ("Many strings to one team", ORANGE, ["That team is a bottleneck", "Consider moving skills or people"]),
                  ("Long strings", AMBER, ["Big gaps in time add risk", "Can the need move later?"]),
                  ("2 · Register", PURPLE, ["Both teams agree each row", "Status is current"]),
                  ("3 · Reduce", FOREST, ["Removal beats management", "Recurring links = team design issue"])],
        tips=[("Both sides agree", "A dependency isn't real until the providing team has agreed to it and planned it."),
              ("Remove before you manage", "Ask whether the needing team could do it themselves, with help or access."),
              ("Use contracts and stubs", "Agreeing an interface early lets both teams work in parallel."),
              ("Watch the bottleneck team", "If one team has most of the strings, fix the structure, not the schedule."),
              ("Keep it visible", "Leave the board up for the period and update it at each Cross-Team Sync."),
              ("Learn from patterns", "Recurring dependencies are a signal to change team boundaries or skills.")],
        pitfalls=("dependencies one side doesn't know about; only managing, never removing; ignoring backwards strings; "
                  "a register nobody updates; blaming the providing team instead of fixing the system."),
        after=[("Straight away", "Photograph the board and update the register in your tools."),
               ("Every sync", "Review status: agreed, at risk, blocked or done. Act on blocked ones that day."),
               ("Next planning", "Bring patterns from this period. Which dependencies keep recurring?"),
               ("Structure", "If the same teams depend on each other every period, propose a team design change.")],
        toolkit=PROGRAM_TOOLKIT,
        foot="“Who are we waiting on, and do they know?”",
    ),

    # -------------------------------------------------------------- OKRs
    dict(
        slug="okr",
        title="Objectives & Key Results Guide",
        subtitle="How to set a few ambitious objectives, measurable key results, and the bets teams will make to move them.",
        tag="Facilitator Run-Sheet · Coordinate Teams · OKRs · Outcomes Over Output",
        boards=[("Open board", "okr-board.html"), ("SVG", "okr-board.svg")],
        lede="If we achieved only one of these, which would matter most?",
        intro=("OKRs give several teams a shared direction without dictating the work. An <b>objective</b> is a qualitative, "
               "inspiring goal; its <b>key results</b> are measurable outcomes that show whether you got there. <b>Initiatives</b> "
               "are the bets teams make to move the key results. The method was developed at Intel by Andy Grove and spread "
               "through John Doerr's <i>Measure What Matters</i>. A short <b>not-doing</b> list keeps the focus honest."),
        glance=[("Duration", "2–3 h"), ("Group", "Leaders, POs,<br>team reps"),
                ("Use when", "The start of a quarter<br>or planning period"), ("Output", "3 objectives, KRs<br>&amp; first bets")],
        before=["Print the board at A3 or larger, or load the SVG as a digital background",
                "Bring the product vision, strategy, and last period's results",
                "Gather baseline data for likely measures",
                "Invite people who can commit their teams' effort",
                "Yellow stickies, markers and dot stickers"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–15", "Focus for This Period", "Agree why these objectives, and why now. Review last period's scores briefly."),
                ("15–50", "Objectives", "Brainstorm candidate objectives, dot-vote, and keep at most three. Write each as “We will…”"),
                ("50–100", "Key Results", "For each objective, agree 2–4 measurable outcomes with a start value and a target. Rate confidence 1–10."),
                ("100–130", "Initiatives", "Teams propose bets that could move each key result. Name the contributing teams."),
                ("130–145", "4 · Check-in Rhythm", "Agree when to check confidence, when to review mid-period, and how to score at the end."),
                ("145–160", "5 · Not Doing · Close", "List what you're explicitly not doing this period. Read the board back.")],
        sections_title="Making each part strong",
        sections_intro="Quality checks for objectives, key results and the rest of the board.",
        sections=[("Objectives", PURPLE, ["Qualitative and inspiring", "No more than three", "Clear why it matters"]),
                  ("Key Results", BLUE, ["Outcomes, not tasks", "Start and target values", "2–4 per objective"]),
                  ("Initiatives", EMERALD, ["Bets, not commitments", "Linked to a key result", "Teams choose them"]),
                  ("4 · Check-in Rhythm", AMBER, ["Confidence tracked weekly", "Scoring agreed up front"]),
                  ("5 · Not Doing", RED, ["Real things people expected", "Shared widely"])],
        tips=[("Outcomes, not output", "“Launch the new app” is a task. “Cut onboarding time from 10 to 3 minutes” is a key result."),
              ("Ambitious but honest", "Aim high. Scoring 0.7 on an ambitious key result is often a good result."),
              ("Few beats many", "Three objectives with focus beat ten that spread effort thin."),
              ("Teams pick the bets", "Leaders set the outcomes; teams decide how to move them."),
              ("Don't tie to pay", "OKRs linked to bonuses become sandbagged. Keep them for direction and learning."),
              ("Check confidence often", "A weekly 1–10 confidence check spots trouble early.")],
        pitfalls=("key results that are task lists; too many objectives; targets set without baselines; OKRs used for "
                  "performance reviews; never checking in until the end; no not-doing list, so nothing changes."),
        after=[("Straight away", "Publish the OKRs where every team can see them."),
               ("Planning", "Use them as the shared objectives on the Cross-Team Planning board."),
               ("Weekly", "Update confidence for each key result; discuss any that drop."),
               ("End of period", "Score each key result, reflect on what you learned, and set the next OKRs.")],
        toolkit=PROGRAM_TOOLKIT,
        foot="“How will we know, without asking anyone, that we've succeeded?”",
    ),

    # -------------------------------------------------------------- cross-team sync
    dict(
        slug="cross-team-sync",
        title="Cross-Team Sync Guide",
        subtitle="How to run a short, regular sync across teams that keeps shared objectives on track and clears blockers.",
        tag="Facilitator Run-Sheet · Coordinate Teams · Scrum of Scrums · Cross-Team Impediments",
        boards=[("Open board", "cross-team-sync-board.html"), ("SVG", "cross-team-sync-board.svg")],
        lede="What's blocking another team that we could help with today?",
        intro=("A cross-team sync, often called a <b>Scrum of Scrums</b>, is a short meeting where one person from each team "
               "shares progress toward the shared objectives, what's next, and what's blocking them. Its real job is to find "
               "and remove <b>cross-team impediments</b>: problems no single team can fix. Keep it short and focused on "
               "dependencies and blockers, not a status report."),
        glance=[("Duration", "15–30 min"), ("Group", "One rep per team,<br>a facilitator"),
                ("Use when", "Once or twice<br>a week"), ("Output", "Blockers owned,<br>decisions made")],
        before=["Print the board at A3 and reuse it, or keep a digital copy",
                "Bring the Cross-Team Planning board and the Dependency Map",
                "Ask each team to choose its rep: whoever knows the current blockers best",
                "Yellow stickies and markers, and a visible timer"],
        agenda_heads=["Time", "Step", "Facilitator notes"],
        agenda=[("0–12", "1 · Team Updates", "About 2 minutes per team: progress toward shared objectives, next up, blocked by or needs, dependencies at risk, confidence."),
                ("12–20", "2 · Impediments", "Add new cross-team impediments. Move the ones being worked, and close resolved ones, saying what fixed them."),
                ("20–27", "Problem-solve", "Pick the top impediment. Agree who will act and when. Take longer discussions offline with the right people."),
                ("27–30", "3 · Decisions & Actions", "Read back decisions and actions with owners and dates.")],
        sections_title="Making each part useful",
        sections_intro="What good looks like.",
        sections=[("1 · Team Updates", BLUE, ["About progress toward objectives, not activity", "Blockers named clearly", "Confidence 1–5"]),
                  ("2 · Cross-Team Impediments", ORANGE, ["Each has an owner", "Resolved ones say what fixed it"]),
                  ("3 · Decisions & Actions", FOREST, ["An owner and a due date", "Reviewed at the next sync"])],
        tips=[("Not a status meeting", "If updates are lists of activity, steer back to objectives, dependencies and blockers."),
              ("Timebox hard", "Keep to 15–30 minutes. Take deep discussions offline with the people who need to be there."),
              ("Right rep, not same rep", "Send whoever knows the current blockers. It can change each time."),
              ("Look at the boards", "Hold the sync in front of the Dependency Map so at-risk links are visible."),
              ("Escalate fast", "Impediments the group can't solve go to leaders the same day."),
              ("Close the loop", "Start each sync by checking last time's actions.")],
        pitfalls=("turning it into a status report for managers; running over time; the same blocker every week with no owner; "
                  "solving problems in the meeting with the wrong people; no follow-up on actions."),
        after=[("Straight away", "Share the decisions and actions with all teams."),
               ("Within a day", "Owners act on impediments, or escalate those they can't solve."),
               ("Next sync", "Start by reviewing actions and impediments from last time."),
               ("Retro", "Bring recurring impediments to a cross-team retrospective.")],
        toolkit=PROGRAM_TOOLKIT,
        foot="“Are we still on track for the shared objectives?”",
    ),
]
GUIDES += PP_GUIDES


FLOW_TOOLKIT = ("The flow pack works as a set. <a href=\"facilitator-guide-kanban-board-design.html\">Kanban Board Design</a> makes "
                "the workflow visible and limits WIP. <a href=\"facilitator-guide-ageing-wip.html\">Ageing WIP &amp; SLE</a> shows which "
                "items are at risk and sets the swarm triggers used in <a href=\"facilitator-guide-buffering-swarming.html\">Buffering "
                "&amp; Swarming</a>. <a href=\"facilitator-guide-blocker-clustering.html\">Blocker Clustering</a> finds why work gets "
                "stuck, and the <a href=\"facilitator-guide-skills-matrix.html\">Skills Matrix</a> shows who can swarm. Bring the results "
                "to retrospectives and the Team Health Check.")

FLOW_GUIDES = [
    # -------------------------------------------------------------- buffering & swarming
    dict(
        slug="buffering-swarming",
        title="Buffering & Swarming Guide",
        subtitle="How to size a capacity buffer from real data, agree swarm triggers, and make swarming a team habit.",
        tag="Facilitator Run-Sheet · Manage Flow · Capacity Buffer · Swarm Triggers",
        boards=[("Open board", "buffering-swarming-board.html"), ("SVG", "buffering-swarming-board.svg")],
        lede="What would we stop starting so we could finish this?",
        intro=("Two habits keep work flowing when reality interrupts the plan. <b>Buffering</b> means deliberately leaving part "
               "of the team's capacity unplanned, sized from how much unplanned work actually arrives, so surprises don't wreck "
               "the plan. <b>Swarming</b> means that when an item is blocked, ageing or critical, people stop starting new work and "
               "gather on it until it's done. The board helps the team size the buffer, agree its rules, set clear triggers, "
               "agree how a swarm works, and learn from each one."),
        glance=[("Duration", "60–75 min to set up<br>10 min each retro"), ("Group", "The whole team,<br>PO included"),
                ("Use when", "Plans keep breaking,<br>or work stalls"), ("Output", "A buffer, rules<br>&amp; swarm triggers")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Pull data for the last five iterations: planned capacity and unplanned work (items, points or hours)",
                "If you have them, bring cycle time percentiles from the Ageing WIP board",
                "Bring the Skills Matrix if the team has one: it shows who can help in a swarm",
                "Agree with the PO in advance that a buffer is a planning tool, not idle time"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–15", "1 · Unplanned Work History", "Fill in the table from the data. Work out the average % unplanned. Discuss what kinds of work it was."),
                ("15–25", "2 · Size the Buffer", "Start with the average % unplanned as the buffer. Agree what it protects."),
                ("25–35", "3 · Buffer Rules", "Agree what counts as unplanned, who decides to use the buffer, and what happens if it runs out or isn't used."),
                ("35–50", "4 · Swarm Triggers", "Tick the triggers that fit and fill in the thresholds. Use your 85% SLE for the age trigger."),
                ("50–65", "5 · How We Swarm", "Walk through the five steps. Agree who calls a swarm, and how people join. Add notes to each step."),
                ("65–75", "Close", "Agree to try it for two iterations, logging every swarm, then review at the retro.")],
        sections_title="Making each section strong",
        sections_intro="Quality checks for each part of the board.",
        sections=[("1 · Unplanned Work History", BLUE, ["Based on data, not memory", "Types of unplanned work noted"]),
                  ("2 · Size the Buffer", EMERALD, ["Starts from the real average", "Clear what it's for"]),
                  ("3 · Buffer Rules", SLATE, ["Unused buffer goes to improvement or the next item", "Running out triggers a conversation"]),
                  ("4 · Swarm Triggers", RED, ["Specific thresholds", "Linked to the SLE", "Few enough to remember"]),
                  ("5 · How We Swarm", ORANGE, ["Anyone can call a swarm", "Just enough people join", "Finishing beats starting"]),
                  ("6 · Swarm Log", PURPLE, ["Every swarm recorded", "Learning captured"]),
                  ("7 · Iteration Check", FOREST, ["Buffer adjusted from use", "Did swarms help?"])],
        tips=[("Buffers aren't slack", "A buffer is planned capacity for work you know will come. Unused, it goes to improvement or the next item."),
              ("Size from data", "If 20% of the team's time goes on unplanned work, planning for 100% guarantees a missed plan."),
              ("Swarm on the oldest", "When in doubt, swarm on the item that has been open longest, not the newest."),
              ("Stop starting first", "The first step of a swarm is to not pick up anything new. That alone frees people up."),
              ("Not everyone, every time", "A swarm needs enough people to finish the item, not the whole team crowded round."),
              ("Ask why it needed a swarm", "Frequent swarms point to a cause: big items, missing skills, or blockers. Use Blocker Clustering.")],
        pitfalls=("a buffer that managers fill with extra features; triggers so vague nobody acts; swarming on everything; "
                  "the same expert always rescuing; never logging swarms, so nothing is learned; swarming without stopping new work."),
        after=[("Straight away", "Put the triggers and swarm steps on the team board where everyone can see them."),
               ("Every day", "At the daily sync, check: has anything hit a trigger? Call the swarm then."),
               ("Every retro", "Run the iteration check: buffer used, swarms, did they help? Adjust the buffer."),
               ("Over time", "If the same skill always needs the same person, update the Skills Matrix and learning plan.")],
        toolkit=FLOW_TOOLKIT,
        foot="“How much of our plan is really for surprises?”",
    ),

    # -------------------------------------------------------------- kanban board design
    dict(
        slug="kanban-board-design",
        title="Kanban Board Design Guide",
        subtitle="How to design a board that shows how work really flows, with WIP limits, exit policies and classes of service.",
        tag="Facilitator Run-Sheet · Manage Flow · Visualise · Limit WIP · Explicit Policies",
        boards=[("Open board", "kanban-board-design.html"), ("SVG", "kanban-board-design.svg")],
        lede="Where does work wait, and is that visible on our board?",
        intro=("Most team boards show “To do, Doing, Done”, which hides where work actually waits. Good board design starts "
               "from the team's <b>real workflow</b>, including the <b>queues</b> between steps, then adds <b>WIP limits</b> so the "
               "team finishes before starting, and explicit <b>exit policies</b> so everyone knows when an item can move. "
               "<b>Classes of service</b> make it clear how urgent and date-driven work is handled. The practices come from the "
               "Kanban Method (David J. Anderson) and the Kanban Guide."),
        glance=[("Duration", "90–120 min"), ("Group", "The whole team,<br>PO included"),
                ("Use when", "A new board, or the<br>board doesn't help"), ("Output", "A board design<br>&amp; written policies")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Take a photo or export of the current board",
                "Pick 3–5 recently finished items to trace through the workflow",
                "Bring cycle time and throughput data if you have it",
                "Sticky notes and markers; the team's Definition of Done"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–20", "Trace real work", "Walk recent items from request to done. Write every step and every place they waited."),
                ("20–45", "1 · Workflow Columns", "Turn those steps into columns, left to right. Mark each as active work or a queue. Write the exit policy for each."),
                ("45–60", "WIP limits", "Set a limit for each in-progress column. A useful start is the number of people who work in it, then lower it over time."),
                ("60–80", "2 · Classes of Service", "Agree when each class applies, how it's treated, and how many items of each can be in progress."),
                ("80–95", "3 · Policies · 4 · Cards", "Fill in the board policies, decide what each card shows, and whether you need swimlanes."),
                ("95–110", "5 · Metrics · Close", "Pick the flow metrics you'll track. Agree when to review the design (usually at retros).")],
        sections_title="Making each part strong",
        sections_intro="Quality checks for each part of the design.",
        sections=[("1 · Workflow Columns", BLUE, ["Matches real steps", "Queues are visible", "Each has an exit policy"]),
                  ("WIP limits", ORANGE, ["Every in-progress column has one", "Low enough to cause conversations"]),
                  ("2 · Classes of Service", PURPLE, ["Expedite is rare and limited", "Fixed-date work is visible early"]),
                  ("3 · Board Policies", SLATE, ["Pull, don't push", "Blocked items are obvious", "Written on the board"]),
                  ("4 · Cards & Swimlanes", SKY, ["Age is visible on each card", "Few or no swimlanes"]),
                  ("5 · Flow Metrics", FOREST, ["Two or three, reviewed regularly", "Used to learn, not to judge"])],
        tips=[("Model what is, not what should be", "Start with the real workflow, including the awkward parts. Improve it later."),
              ("Show the queues", "Waiting is usually most of the elapsed time. A “Waiting for review” column makes it visible."),
              ("WIP limits are a conversation", "When a column is full, the question is “how can I help finish something?”"),
              ("Expedite sparingly", "If everything is expedite, nothing is. Limit it to one item at a time."),
              ("Make age visible", "Show days in progress on each card so ageing work stands out."),
              ("Evolve the board", "Review the design at retros. Small, regular changes beat a big redesign.")],
        pitfalls=("columns named after people or teams; no queue columns; WIP limits set so high they never bite; ignoring "
                  "limits when busy; too many swimlanes; policies that exist only in someone's head."),
        after=[("Straight away", "Rebuild the physical or digital board to match the design. Write the policies on it."),
               ("First week", "Walk the board right to left at every daily sync. Notice when limits bite."),
               ("Each retro", "Ask: is the board still showing reality? Adjust one thing at a time."),
               ("After a month", "Start the Ageing WIP chart using the cycle time data the board now gives you.")],
        toolkit=FLOW_TOOLKIT,
        foot="“What would happen if we lowered this WIP limit by one?”",
    ),

    # -------------------------------------------------------------- ageing WIP
    dict(
        slug="ageing-wip",
        title="Ageing WIP & SLE Guide",
        subtitle="How to work out a service level expectation from cycle times, and use work item age to act before items are late.",
        tag="Facilitator Run-Sheet · Manage Flow · Work Item Age · Percentiles · Service Level Expectation",
        boards=[("Open board", "ageing-wip-board.html"), ("SVG", "ageing-wip-board.svg")],
        lede="Which item is oldest, and what would it take to finish it today?",
        intro=("Cycle time tells you how long finished work took; <b>work item age</b> tells you how long open work has been "
               "running. Plotting each open item's age against the team's <b>cycle time percentiles</b> shows which items are "
               "at risk while there's still time to act. The 85th percentile gives a <b>service level expectation</b> (SLE): "
               "“85% of our items finish within N days”. It's a forecast for a single item, not a target. Work item age and "
               "SLE are described in the Kanban Guide and in Daniel Vacanti's work on flow metrics."),
        glance=[("Duration", "45 min to set up<br>5 min each day"), ("Group", "The team, with<br>a flow-minded lead"),
                ("Use when", "Items surprise you<br>by running late"), ("Output", "An SLE &amp;<br>daily age checks")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Export start and finish dates for at least the last 20–30 finished items",
                "Agree when the clock starts (e.g. first in-progress column) and stops (e.g. Done)",
                "Know the in-progress columns of your board, left to right",
                "Small dot stickers or markers for plotting"],
        agenda_heads=["Time", "Step", "Facilitator notes"],
        agenda=[("0–10", "2 · Cycle Time Data", "List recently finished items with start, finish and days (count partial days as a whole day)."),
                ("10–20", "Percentiles", "Sort the days, smallest to largest. The 85th percentile is the value 85% of the way along the list. Repeat for 50th and 70th."),
                ("20–25", "3 · Our SLE", "Write the 85th percentile into the SLE sentence, with the data range and the clock start and stop."),
                ("25–35", "1 · Ageing WIP Chart", "Write the column names along the bottom and age in days up the side. Draw the three percentile lines. Plot each open item."),
                ("35–45", "4 · Act on Ageing Items", "For each item past a line, agree the action. Swarm the ones past the 85th."),
                ("Daily", "Update", "Move dots up a day and across as items progress. Start the daily sync with the oldest items.")],
        sections_title="Reading the chart",
        sections_intro="What the dots tell you.",
        sections=[("Below the 50th", EMERALD, ["On track", "No action needed"]),
                  ("Past the 50th", EMERALD, ["Worth a mention", "Is anything slowing it?"]),
                  ("Past the 70th", AMBER, ["At risk", "Ask what's needed to finish"]),
                  ("Past the 85th", RED, ["Likely to miss the SLE", "Swarm it"]),
                  ("Dots high in early columns", PURPLE, ["Stuck before real work started", "Check for blockers or big items"])],
        tips=[("Age is the leading signal", "Cycle time is only known at the end. Age tells you about risk while you can still act."),
              ("An SLE isn't a target", "Pushing people to hit it leads to gaming. Use it to spot risk and to answer “when?” for one item."),
              ("Use enough data", "Twenty to thirty items gives a reasonable start. Recalculate monthly."),
              ("Start with the oldest", "Walk the chart from the top. The oldest items need attention first."),
              ("Right-size before you start", "Ask “can we finish this within our SLE?” when pulling work. If not, split it."),
              ("Link it to swarming", "Use the 85th percentile as the age trigger in Buffering & Swarming.")],
        pitfalls=("treating the SLE as a deadline; using averages instead of percentiles; too little data; never updating the "
                  "dots; ignoring items in early columns; tracking age but never acting on it."),
        after=[("Straight away", "Put the SLE sentence on the team board and in the team's working agreements."),
               ("Every day", "Update the chart and discuss the oldest items first at the daily sync."),
               ("Each retro", "Look at items that passed the 85th line. Why? Feed causes into Blocker Clustering."),
               ("Monthly", "Recalculate the percentiles with new data and update the SLE.")],
        toolkit=FLOW_TOOLKIT,
        foot="“How long does work usually take here, really?”",
    ),

    # -------------------------------------------------------------- blocker clustering
    dict(
        slug="blocker-clustering",
        title="Blocker Clustering Guide",
        subtitle="How to log blockers over time, cluster them by cause, and fix the cluster that costs the most days.",
        tag="Facilitator Run-Sheet · Manage Flow · Inspired by Klaus Leopold & Troy Magennis",
        boards=[("Open board", "blocker-clustering-board.html"), ("SVG", "blocker-clustering-board.svg")],
        lede="Which cluster, if we fixed it, would give us the most days back?",
        intro=("Teams clear blockers one by one and rarely ask why they keep happening. Blocker clustering, a technique "
               "popularised by Klaus Leopold and Troy Magennis, collects every blocker over several weeks, with its cause and how "
               "many days it cost. Clustering similar causes shows which problem is really slowing the team down, so you can "
               "fix the system rather than the symptom."),
        glance=[("Duration", "4–6 weeks of logging<br>+ 60 min to cluster"), ("Group", "The team"),
                ("Use when", "Work is often blocked,<br>or flow is slow"), ("Output", "Top cause<br>&amp; an experiment")],
        before=["Print the board at A3 and put it next to the team board, or use a digital copy",
                "Plenty of pink stickies, and yellow stickies for cluster names",
                "Agree with the team to log every blocker, however small, for at least four weeks",
                "Agree a simple rule: a sticky goes on the card the moment it's blocked"],
        agenda_heads=["When", "Step", "Facilitator notes"],
        agenda=[("Ongoing", "1 · Log", "Every time work is blocked, add a pink sticky to the card with the cause and date. Add a row to the log."),
                ("Ongoing", "2 · Collect", "When the blocker clears, write the days blocked and move the sticky to the Blocker Stickies area."),
                ("Week 4–6 · 0–20", "3 · Cluster", "In a session, group similar stickies. Name each cluster on a yellow sticky. Count blockers and total days."),
                ("20–35", "Pick the biggest", "Rank clusters by total days blocked, not by count. Discuss the top one."),
                ("35–50", "4 · Fix", "Find the root cause (5 Whys works well) and agree an experiment to fix it, with an owner and review date."),
                ("50–60", "5 · Trend", "Agree to keep logging, and record the totals so you can see if the fix worked.")],
        sections_title="Making each part useful",
        sections_intro="Quality checks for each part of the board.",
        sections=[("1 · Blocker Log", RED, ["Every blocker, however small", "The cause, not who to blame", "Days counted"]),
                  ("2 · Blocker Stickies", SLATE, ["Kept after clearing", "Start date and days written on"]),
                  ("3 · Clusters", ORANGE, ["Similar causes grouped", "Each cluster named", "Count and days totalled"]),
                  ("4 · Fix the Biggest", FOREST, ["Chosen by days, not count", "A real root cause", "An owned experiment"]),
                  ("5 · Trend", BLUE, ["Compared period to period", "Shows whether the fix worked"])],
        tips=[("Log everything", "Small blockers add up. A two-hour wait three times a week is a cluster worth fixing."),
              ("Cause, not person", "“Waiting for test environment” helps. “Waiting for Sam” blames someone and hides the system."),
              ("Days beat counts", "Ten one-hour blockers matter less than one blocker that lasted two weeks."),
              ("Inside vs. outside", "Separate what the team controls from what needs help from others, and escalate the outside ones."),
              ("One fix at a time", "Tackle the top cluster, measure, then move to the next."),
              ("Make it routine", "Keep the board running. A quick look at each retro keeps the data honest.")],
        pitfalls=("logging only big blockers; blaming people; clustering too early with too little data; ranking by count; "
                  "fixing several clusters at once; stopping logging after the first session."),
        after=[("Straight away", "Start the experiment on the biggest cluster and put its review date in the calendar."),
               ("Each retro", "Glance at the log: any new patterns? Is the top cluster shrinking?"),
               ("Next cluster", "When the trend shows the fix worked, move on to the next biggest cluster."),
               ("Outside causes", "Take clusters outside the team's control to the Cross-Team Sync or to leaders, with the data.")],
        toolkit=FLOW_TOOLKIT,
        foot="“What keeps blocking us, and what does it cost?”",
    ),

    # -------------------------------------------------------------- skills matrix
    dict(
        slug="skills-matrix",
        title="Skills Matrix Guide",
        subtitle="How to map the team's skills, find single points of failure, and plan learning so the team can swarm.",
        tag="Facilitator Run-Sheet · Manage Flow · Team Capability · T-Shaped Skills",
        boards=[("Open board", "skills-matrix-board.html"), ("SVG", "skills-matrix-board.svg")],
        lede="If one person was away for a month, what would stop?",
        intro=("Swarming and steady flow need more than one person who can do each kind of work. A skills matrix maps the "
               "team's skills on a simple <b>0–3 scale</b>, from no experience to able to teach. It quickly shows <b>single points "
               "of failure</b> and skills nobody can teach, and it turns what people <b>want to learn</b> into a learning plan. "
               "It's a team tool for growth, not a performance assessment."),
        glance=[("Duration", "60–90 min"), ("Group", "The whole team"),
                ("Use when", "Work waits for one<br>person, or a team forms"), ("Output", "A matrix &amp;<br>a learning plan")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Agree up front that the matrix is for team learning, not for managers to rate people",
                "Draft a list of 8–10 skills the team's work needs: technical, domain and practice skills",
                "Markers; sticky notes for the wants-to-learn column"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "Purpose", "Explain why: to spread skills so the team can swarm and isn't stuck when someone is away."),
                ("10–25", "Skills", "Agree the skills that matter for the team's work. Write one per column. Keep to ten."),
                ("25–45", "1 · Self-assess", "Each person scores themselves 0–3 for each skill, then the team discusses any surprises."),
                ("45–55", "Wants to learn", "Each person adds what they'd like to learn."),
                ("55–70", "2 · Single Points of Failure", "List skills with only one person at 2 or 3, and skills with nobody at 3."),
                ("70–85", "3 · Learning Plan · 4 · Ready to Swarm?", "Pair learners with teachers, set dates, and check the readiness list.")],
        sections_title="Reading the matrix",
        sections_intro="Patterns to look for once it's filled in.",
        sections=[("One person at 2+", RED, ["A single point of failure", "Top of the learning plan"]),
                  ("Nobody at 3", AMBER, ["No one to teach it", "Consider outside help or training"]),
                  ("Lots of 0s in a row", BLUE, ["A specialist; check they're not overloaded", "Pair them with learners"]),
                  ("Wants to learn", EMERALD, ["Match with teachers", "Plan time for it"]),
                  ("4 · Ready to Swarm?", FOREST, ["Two or more people per key skill", "Pairing is planned"])],
        tips=[("Self-assess first", "People score themselves, then discuss. It builds trust and surfaces modesty or over-confidence."),
              ("Learning, not rating", "Never use the matrix for performance reviews. If you do, the scores stop being honest."),
              ("Aim for T-shapes", "Deep skill in one area plus working skill in others lets people help where the work is."),
              ("Pair to teach", "Pairing on real work spreads skills faster than courses."),
              ("Make time", "Plan learning into the iteration, or the matrix won't change."),
              ("Revisit it", "Update every quarter and celebrate the levels that went up.")],
        pitfalls=("managers filling it in about people; using it in performance reviews; too many skills; no time for learning; "
                  "experts never given time to teach; filling it in once and forgetting it."),
        after=[("Straight away", "Keep the matrix where the team can see it. Start the first learning pairs."),
               ("Each iteration", "Plan pairing time. Note when a learner helps in a swarm."),
               ("Each retro", "Ask: did work wait for one person? Update the learning plan."),
               ("Quarterly", "Re-score together and compare. Single points of failure should be falling.")],
        toolkit=FLOW_TOOLKIT,
        foot="“What would you like to learn, and who could teach you?”",
    ),
]
FLOW_GUIDES += [
    # -------------------------------------------------------------- impediments
    dict(
        slug="impediments",
        title="Impediments Board Guide",
        subtitle="How to make impediments visible, give each one an owner, escalate on time, and show the value of removing them.",
        tag="Facilitator Run-Sheet · Manage Flow · Team Impediments · Escalation Ladder",
        boards=[("Open board", "impediments-board.html"), ("SVG", "impediments-board.svg")],
        lede="What's slowing us down that we've stopped noticing?",
        intro=("An <b>impediment</b> is anything that limits how well the team works and that the team can't easily fix "
               "alone: a slow approval, a missing tool, an unclear decision owner, a flaky environment. Unlike a blocker on a "
               "single item, impediments often affect everything. The board makes each one visible with <b>what it costs</b>, "
               "gives it an owner, and uses an <b>escalation ladder</b> with time limits so nothing sits unresolved for weeks. "
               "The resolved log shows stakeholders the value of removing impediments."),
        glance=[("Duration", "30 min to set up<br>5 min each day"), ("Group", "The team, with the<br>SM or coach"),
                ("Use when", "Always on, next to<br>the team board"), ("Output", "Owned impediments<br>&amp; a resolved log")],
        before=["Print the board at A3 and put it next to the team board, or keep a digital copy",
                "Pink and green stickies, and markers",
                "Agree with management who sits on rungs 3 and 4 of the ladder, and that they'll respond in time",
                "Bring any impediments from recent retros or the Blocker Clustering board"],
        agenda_heads=["When", "Step", "Facilitator notes"],
        agenda=[("Set-up · 0–10", "2 · Escalation Ladder", "Agree who is on each rung and how many days an impediment stays at a level before moving up."),
                ("Set-up · 10–25", "1 · Seed the board", "Brainstorm current impediments. One pink sticky each: what, what it costs us, owner, date raised."),
                ("Set-up · 25–30", "Prioritise", "Order by cost. Agree a next step for the top ones and move them to Being worked."),
                ("Daily", "Review", "At the daily sync, check the board. Anything past its time limit moves up the ladder."),
                ("When resolved", "3 · Resolved Log", "Add a green sticky saying what fixed it. Record it in the log with the days open and the lesson."),
                ("Each retro", "Look back", "Review what was resolved, what's stuck, and whether the ladder's time limits are working.")],
        sections_title="Making each part work",
        sections_intro="Quality checks for each part of the board.",
        sections=[("1 · Impediments", RED, ["Each sticky shows its cost", "Each has an owner and a date", "Few in Being worked at once"]),
                  ("2 · Escalation Ladder", PURPLE, ["Named people at every rung", "Time limits are short", "Leaders agreed to respond"]),
                  ("3 · Resolved Log", FOREST, ["What it cost and what fixed it", "Shared with stakeholders", "Lessons feed improvement"])],
        tips=[("Show the cost", "“Waiting 3 days for approvals each sprint” gets action. “Approvals are slow” doesn't."),
              ("Owner, not escalator", "The owner drives the impediment to resolution, even after it's escalated."),
              ("Time-box each rung", "Without a time limit, impediments sit at the team level for months."),
              ("Limit work in progress", "Work on a few impediments at a time and finish them, just like backlog items."),
              ("Celebrate removals", "Share the resolved log at reviews. It builds support for removing the next one."),
              ("Look for patterns", "If the same kind keeps appearing, it's a system issue. Raise it at the retro or with leaders.")],
        pitfalls=("a board full of complaints with no owners; no time limits; escalating without the data on cost; leaders who "
                  "don't respond; the SM fixing everything alone; never recording what was resolved."),
        after=[("Straight away", "Put the board where the team and visitors can see it."),
               ("Every day", "Check it at the daily sync and move anything past its time limit."),
               ("Each review", "Share the resolved log and any escalations that need stakeholder help."),
               ("Quarterly", "Look at the log for patterns and bring them to the Team Health Check or leaders.")],
        toolkit=FLOW_TOOLKIT,
        foot="“Who could remove this, and do they know it's costing us?”",
    ),

    # -------------------------------------------------------------- pairing & mobbing
    dict(
        slug="pairing-mobbing",
        title="Pairing & Mobbing Guide",
        subtitle="How to introduce pairing and mobbing, choose a style, rotate partners, and use it to spread skills.",
        tag="Facilitator Run-Sheet · Manage Flow · Pair Programming · Mob / Ensemble Programming",
        boards=[("Open board", "pairing-mobbing-board.html"), ("SVG", "pairing-mobbing-board.svg")],
        lede="Who haven't we paired with yet, and what could we learn from each other?",
        intro=("Pairing means two people working on one thing at one screen; mobbing, or ensemble work, means the whole group "
               "does. Both finish work with fewer hand-offs, catch problems early, and spread skills quickly. They work for "
               "code, tests, analysis and design. The board covers four <b>styles</b>, a <b>pair stair</b> to track who has paired "
               "with whom, <b>session agreements</b>, the <b>skills</b> each pairing should spread, and a quick retro. Pair "
               "programming comes from Extreme Programming; strong-style pairing is from Llewellyn Falco; mob programming was "
               "popularised by Woody Zuill."),
        glance=[("Duration", "45 min to set up<br>then ongoing"), ("Group", "The whole team"),
                ("Use when", "Skills are siloed,<br>or work waits"), ("Output", "Agreements, rotation<br>&amp; learning pairs")],
        before=["Print the board at A3 and put it next to the team board, or keep a digital copy",
                "Bring the Skills Matrix: it shows which skills to spread",
                "Check the setup: a shared screen, two keyboards, or a remote pairing tool",
                "Agree a first trial: for example, pair on every item for two weeks, then review"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "Why", "Discuss what the team wants from pairing: fewer hand-offs, shared knowledge, fewer bugs, or faster swarming."),
                ("10–20", "1 · Styles", "Walk through the four styles. Agree what each is good for and how often to swap."),
                ("20–30", "3 · Session Agreements", "Agree when to pair or mob, when to work solo, breaks, rotation and setup."),
                ("30–40", "4 · Skills to Spread", "From the Skills Matrix, pick the skills to spread and match learners with teachers."),
                ("40–45", "2 · Pair Stair · 5 · Pairs", "Write names on the stair. Plan this week's pairs, mixing people who haven't paired."),
                ("Weekly", "6 · Quick Retro", "Five minutes: what worked, what was hard, what to change. Update the stair.")],
        sections_title="Choosing a style",
        sections_intro="Each style suits different work. Swap styles as the work changes.",
        sections=[("Driver / Navigator", PURPLE, ["Everyday pairing", "Swap every 15–30 minutes"]),
                  ("Ping-Pong", EMERALD, ["Test-driven development", "Keeps both people engaged"]),
                  ("Strong-Style", ORANGE, ["Teaching and onboarding", "The expert navigates, the learner drives"]),
                  ("Mob / Ensemble", SKY, ["Hard problems, swarming, new areas", "Rotate the driver every few minutes"]),
                  ("2 · Pair Stair", SLATE, ["Spread tallies evenly", "Empty cells are pairs to try"])],
        tips=[("Start with a trial", "Agree to pair for two weeks, then review. People adjust faster when it's an experiment."),
              ("Swap often", "Regular role swaps keep both people engaged and stop one person dominating."),
              ("Breaks matter", "Pairing is intense. Short, regular breaks keep it sustainable."),
              ("Strong-style to teach", "Let the learner drive and the expert navigate. Knowledge moves through the learner's hands."),
              ("Mob for hard problems", "When something is stuck or new, mobbing brings every perspective at once."),
              ("Not everything needs a pair", "Agree what's fine solo: simple, well-understood or exploratory work.")],
        pitfalls=("one person typing while the other watches; the same pairs every time; no breaks; forcing pairing on "
                  "everything without agreement; measuring individual output; experts never letting learners drive."),
        after=[("Straight away", "Put the agreements and the pair stair next to the team board."),
               ("Daily", "Plan pairs at the daily sync, using the stair to mix people."),
               ("Weekly", "Run the quick retro and update the tallies."),
               ("Quarterly", "Re-score the Skills Matrix. Pairing should show up as levels going up.")],
        toolkit=FLOW_TOOLKIT,
        foot="“What would finish faster if two of us worked on it?”",
    ),
]
GUIDES += FLOW_GUIDES


GUIDES += [
    # -------------------------------------------------------------- pre-mortem
    dict(
        slug="pre-mortem",
        title="Pre-mortem Guide",
        subtitle="How to surface the risks people are quietly worried about, by imagining the work has already failed.",
        tag="Facilitator Run-Sheet · Run a Project · Inspired by Gary Klein's Pre-mortem",
        boards=[("Open board", "pre-mortem-board.html"), ("SVG", "pre-mortem-board.svg")],
        lede="It's six months from now and this has failed. What happened?",
        intro=("Asking “what could go wrong?” gets polite, cautious answers. A pre-mortem, developed by psychologist Gary "
               "Klein, asks the group to imagine the project <b>has already failed</b> and explain why. This <b>prospective "
               "hindsight</b> makes it safe to voice worries, and it surfaces far more risks. The group then votes on the most "
               "likely causes and agrees how to <b>prevent</b> them, or at least <b>detect</b> them early."),
        glance=[("Duration", "45–60 min"), ("Group", "Team, PO, sponsor,<br>key stakeholders"),
                ("Use when", "Before a project, release<br>or big decision"), ("Output", "Top risks with<br>prevention &amp; signals")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Make sure everyone understands the plan being tested: share it beforehand",
                "Pink stickies, markers and dot stickers (3 per person)",
                "Invite people with different views, including sceptics",
                "Bring the RAID Log so top risks can be added straight away"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–5", "1 · The Scenario", "Fill in a date in the future. Read the scenario aloud: “It's that date and this has failed badly.”"),
                ("5–15", "2 · Why It Failed (silent)", "Everyone writes reasons alone, one per sticky, in the past tense. No discussion yet."),
                ("15–30", "Share & cluster", "Go round the room, one sticky at a time, until all are up. Cluster similar reasons."),
                ("30–35", "Dot vote", "Three dots each, on the reasons most likely to actually happen."),
                ("35–40", "3 · Top Risks", "Write the top 5–8 in the table with votes, likelihood and impact."),
                ("40–55", "4 · Prevent or Detect", "For each top risk, agree a prevention, an early warning sign and an owner."),
                ("55–60", "5 · Next Steps", "Tick off the follow-ups and set a review date.")],
        sections_title="Making each section strong",
        sections_intro="Quality checks for each part of the board.",
        sections=[("1 · The Scenario", PURPLE, ["A specific future date", "Failure is described concretely"]),
                  ("2 · Why It Failed", RED, ["Written in the past tense", "Silent writing first", "Wide range of causes"]),
                  ("3 · Top Risks", ORANGE, ["Chosen by vote", "Likelihood and impact noted"]),
                  ("4 · Prevent or Detect", FOREST, ["A real prevention or a clear warning sign", "Every risk has an owner"]),
                  ("5 · Next Steps", EMERALD, ["Risks reach the RAID Log", "A review date is set"])],
        tips=[("Past tense matters", "“We lost our key engineer” feels more real than “we might lose someone”, and gets better answers."),
              ("Silent first", "Writing alone stops the most senior or loudest person shaping everyone's thinking."),
              ("Welcome the uncomfortable", "The most valuable reasons are often about decisions, leadership or politics. Thank people for them."),
              ("Not just doom", "Close by focusing on what you'll do. The goal is a better plan, not a gloomy team."),
              ("Prevent or detect", "If a risk can't be prevented, agree the early warning sign that would tell you it's happening."),
              ("Repeat it", "Run a short pre-mortem again before each big milestone.")],
        pitfalls=("discussing reasons before everyone has written; the sponsor dismissing reasons in the room; only listing "
                  "technical risks; no owners for actions; not feeding risks into the RAID Log or the plan."),
        after=[("Straight away", "Add the top risks to the RAID Log and the prevention actions to the backlog."),
               ("This week", "Put the early warning signs where the team will notice them."),
               ("Each iteration", "Check the warning signs at the review or retro."),
               ("Before milestones", "Run a quick pre-mortem again on the next phase.")],
        toolkit=PROJECT_TOOLKIT,
        foot="“Which of these are we quietly hoping won't happen?”",
    ),

    # -------------------------------------------------------------- root cause
    dict(
        slug="root-cause",
        title="Root Cause Analysis Guide",
        subtitle="How to dig beneath a recurring problem with a fishbone diagram and 5 Whys, check the cause, and test a fix.",
        tag="Facilitator Run-Sheet · Improve · Fishbone (Ishikawa) · 5 Whys",
        boards=[("Open board", "root-cause-board.html"), ("SVG", "root-cause-board.svg")],
        lede="Why does this keep happening, and what in our system lets it?",
        intro=("When the same problem keeps coming back, fixing the symptom isn't enough. The board combines two classic "
               "techniques. The <b>fishbone</b> (Ishikawa) diagram explores possible causes across six categories, so the group "
               "looks wide before going deep. <b>5 Whys</b>, from the Toyota Production System, then follows the most likely "
               "branch down to a cause you can fix. A quick <b>check</b> makes sure it really is the root cause, and the "
               "countermeasures are treated as experiments."),
        glance=[("Duration", "60–90 min"), ("Group", "The people closest<br>to the problem"),
                ("Use when", "A problem recurs, or<br>a retro keeps raising it"), ("Output", "A checked root cause<br>&amp; a tested fix")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Collect facts about the problem: when, where, how often, and its impact",
                "Invite the people who experience the problem, not just those who manage it",
                "Yellow stickies and markers",
                "Agree up front that this is about the system, not about blaming a person"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "1 · The Problem", "Write a factual problem statement. Agree when, where and how often it happens, and its impact."),
                ("10–35", "2 · Fishbone", "Brainstorm possible causes onto the six bones. Aim for breadth: every category gets at least one sticky."),
                ("35–40", "Pick a branch", "Dot-vote the most likely cause on the fishbone. That's the starting point for the Whys."),
                ("40–55", "3 · 5 Whys", "Ask “why?” of that cause, writing each answer. Stop when you reach something you can change."),
                ("55–65", "4 · Check the Cause", "Run the checklist. Any “no”? Ask why again, or try another branch."),
                ("65–80", "5 · Countermeasures", "Agree small, testable fixes with owners and dates."),
                ("80–90", "6 · Did It Work?", "Agree what you'll measure, the baseline, and when you'll check.")],
        sections_title="Using each part well",
        sections_intro="What good looks like on each part of the board.",
        sections=[("1 · The Problem", SLATE, ["Facts, not opinions", "No names or blame", "Impact is clear"]),
                  ("2 · Fishbone", BLUE, ["Every bone considered", "Causes, not solutions"]),
                  ("3 · 5 Whys", PURPLE, ["Each answer is evidence-based", "Stop at something you can change", "It may take 3 or 7 whys"]),
                  ("4 · Check the Cause", AMBER, ["All boxes ticked", "Would explain the problem fully"]),
                  ("5 · Countermeasures", FOREST, ["Small and testable", "Owned and dated"]),
                  ("6 · Did It Work?", EMERALD, ["Measured against a baseline", "Checked on the date"])],
        tips=[("Wide, then deep", "Fill the fishbone before asking why, so you don't chase the first idea that comes up."),
              ("System, not person", "If a “why” lands on a person, ask why the system allowed it. People act sensibly in their context."),
              ("Five is a guide", "Stop when you reach a cause you can change. Sometimes that's three whys, sometimes seven."),
              ("Evidence beats opinion", "Check each answer against data where you can. Guesses lead to the wrong fix."),
              ("Several roots are normal", "Complex problems often have more than one cause. Pick the one with the most leverage."),
              ("Fix as an experiment", "Treat countermeasures like the 1% Experiment Canvas: measure, then persevere or pivot.")],
        pitfalls=("blaming a person; jumping to a solution in the first five minutes; following only one branch; stopping at a "
                  "symptom; answers based on opinion; fixing without measuring whether it worked."),
        after=[("Straight away", "Add the countermeasures to the backlog and share the board with those affected."),
               ("Next retro", "Report progress on the countermeasures."),
               ("On the check date", "Measure against the baseline and fill in Did It Work?"),
               ("If it didn't work", "Go back to the fishbone and try the next most likely branch.")],
        toolkit=("Root cause analysis pairs with the improvement tools: bring recurring retro themes or the biggest cluster from "
                 "<a href=\"facilitator-guide-blocker-clustering.html\">Blocker Clustering</a> here, then test the fix with the "
                 "<a href=\"facilitator-guide-experiment-canvas.html\">1% Experiment Canvas</a>. Use the "
                 "<a href=\"facilitator-guide-impediments.html\">Impediments Board</a> to escalate causes the team can't fix alone."),
        foot="“If we fixed the cause, what else would get better?”",
    ),
]


WAVE1_GUIDES = [
    # -------------------------------------------------------------- value metrics
    dict(
        slug="value-metrics",
        title="Value Metrics Guide",
        subtitle="How to measure the value you deliver and your ability to deliver more, using four key value areas.",
        tag="Facilitator Run-Sheet · Lead the Organisation · Inspired by Evidence-Based Management",
        boards=[("Open board", "value-metrics-board.html"), ("SVG", "value-metrics-board.svg")],
        lede="How do we know we're delivering value, not just output?",
        intro=("Velocity and on-time delivery say little about whether customers are better off. This board is based on "
               "Scrum.org's <b>Evidence-Based Management</b> (EBM), which looks at value through four <b>key value areas</b>: "
               "<b>current value</b> delivered today, <b>unrealised value</b> still on the table, <b>time to market</b>, and the "
               "<b>ability to innovate</b>. Each is tied to a strategic, intermediate and immediate goal, and the board ends with "
               "small experiments to improve the weakest area. It works for a product, a portfolio or a whole organisation."),
        glance=[("Duration", "90–120 min to set up<br>30 min to review"), ("Group", "Leaders, product<br>managers, POs"),
                ("Use when", "Quarterly, or when<br>“are we improving?” arises"), ("Output", "Measures, a baseline<br>&amp; experiments")],
        before=["Print the board at A3 or larger, or load the SVG as a digital background",
                "Bring whatever data exists: customer satisfaction, usage, cycle time, releases, defects, time on new work",
                "Agree the scope: one product, a group of products, or the organisation",
                "Invite people who can act on the results, not just report them",
                "Bring the product vision, OKRs or strategy so goals line up"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–20", "1 · Goals", "Agree the strategic goal, the next intermediate goal, and the immediate tactical goal."),
                ("20–70", "2–5 · Key Value Areas", "For each area, pick 1–3 measures from the examples or your own. Fill in now, target and trend where you have data."),
                ("70–85", "What the numbers tell us", "For each area, note what stands out. Where's the biggest gap or the weakest area?"),
                ("85–105", "6 · Experiments", "Pick one experiment for the weakest area, with the measure you expect to move and an owner."),
                ("105–115", "7 · Review Rhythm", "Agree how often measures are updated and when leaders review them.")],
        sections_title="The four key value areas",
        sections_intro="Each looks at value from a different angle; balance all four.",
        sections=[("Current Value", EMERALD, ["Value customers get today", "Satisfaction, usage, revenue", "Employee satisfaction too"]),
                  ("Unrealised Value", PURPLE, ["Value we could still create", "Unmet needs, market gaps"]),
                  ("Time to Market", BLUE, ["How fast we deliver and learn", "Lead time, release frequency"]),
                  ("Ability to Innovate", ORANGE, ["What slows new value", "Tech debt, defects, time on new work"]),
                  ("Goals", SLATE, ["Strategic, intermediate, tactical", "Measures link to them"])],
        tips=[("Balance the four", "Optimising one area, often time to market, can hurt another. Look at all four together."),
              ("Few measures", "One to three per area is enough. More measures mean less attention."),
              ("Trends over targets", "The direction over several reviews matters more than any single number."),
              ("Experiments, not mandates", "Treat improvements as hypotheses: measure, then keep, adapt or drop them."),
              ("Leaders own it", "The board is for decisions about investment and priorities, not for judging teams."),
              ("Start with what you have", "Imperfect data now beats perfect data never. Improve the measures as you go.")],
        pitfalls=("measuring only output; turning measures into team targets; too many measures; no baseline; reviewing numbers "
                  "without acting; using it to compare teams."),
        after=[("Straight away", "Share the board with the teams and stakeholders affected."),
               ("This month", "Start the experiments and set up the data you're missing."),
               ("Each review", "Update the measures, look at trends, and decide what to keep or change."),
               ("Quarterly", "Revisit the goals, and feed insights into OKRs and the Prioritisation Board.")],
        toolkit=("Value metrics sit above the rest of the toolkit: use them with <a href=\"facilitator-guide-okr.html\">OKRs</a> "
                 "to set direction, the <a href=\"facilitator-guide-prioritisation.html\">Prioritisation Board</a> to decide what to "
                 "fund, and the flow pack (for example <a href=\"facilitator-guide-ageing-wip.html\">Ageing WIP</a>) to improve "
                 "time to market. The <a href=\"facilitator-guide-status-report.html\">Outcome Status Report</a> is a good place to "
                 "share them."),
        foot="“What's stopping us from delivering more value, sooner?”",
    ),

    # -------------------------------------------------------------- opportunity solution tree
    dict(
        slug="opportunity-solution-tree",
        title="Opportunity Solution Tree Guide",
        subtitle="How to connect an outcome to customer opportunities and solutions, and test the riskiest assumptions first.",
        tag="Facilitator Run-Sheet · Continuous Discovery · Inspired by Teresa Torres",
        boards=[("Open board", "opportunity-solution-tree-board.html"), ("SVG", "opportunity-solution-tree-board.svg")],
        lede="What must be true for this solution to work, and how could we find out this week?",
        intro=("Teams often jump from a goal straight to a feature. The <b>opportunity solution tree</b>, from Teresa Torres' "
               "<i>Continuous Discovery Habits</i>, adds the missing step: start with one measurable <b>outcome</b>, map the "
               "customer <b>opportunities</b> (needs, pains and desires) that could move it, then explore several "
               "<b>solutions</b> for each. The <b>assumption map</b> sorts what must be true by importance and evidence, so the "
               "team tests the riskiest assumptions first with small, cheap experiments."),
        glance=[("Duration", "90 min, then<br>weekly updates"), ("Group", "Product trio: PO / PM,<br>designer, tech lead"),
                ("Use when", "Choosing what to<br>build next"), ("Output", "A tree, ranked<br>assumptions &amp; tests")],
        before=["Print the board at A3 or larger, or load the SVG as a digital background",
                "Agree one product outcome to focus on, ideally from the OKRs or Product Vision Board",
                "Bring evidence from customers: interviews, support tickets, analytics",
                "Blue, yellow, pink and green stickies, and markers",
                "Ideally, keep interviewing customers each week to feed the tree"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "Outcome", "Write one measurable product outcome at the top. Not a feature or an output."),
                ("10–30", "Opportunities", "From customer evidence, list needs and pains that could move the outcome. Group them and pick the top three."),
                ("30–50", "Solutions", "For each opportunity, brainstorm at least two or three solutions. Compare them; don't fall for the first one."),
                ("50–65", "2 · Assumption Map", "For the leading solutions, write what must be true (pink). Place each by importance and evidence."),
                ("65–80", "3 · Assumption Tests", "For the top-right assumptions, design small tests with a clear success measure."),
                ("80–90", "Close", "Agree who runs which tests this week, and when the trio will update the tree.")],
        sections_title="Making each level strong",
        sections_intro="Quality checks for each part of the tree and the map.",
        sections=[("Outcome", EMERALD, ["One measurable outcome", "Within the team's influence"]),
                  ("Opportunities", BLUE, ["From the customer's point of view", "Based on evidence", "Not solutions in disguise"]),
                  ("Solutions", AMBER, ["Several per opportunity", "Compared, not just listed"]),
                  ("Assumption Map", RED, ["Desirable, viable, feasible, usable, ethical", "Top-right tested first"]),
                  ("Assumption Tests", FOREST, ["Small, fast, cheap", "Success defined before running"])],
        tips=[("Outcome, not output", "“Increase repeat purchases” gives room to explore. “Build a loyalty scheme” doesn't."),
              ("Opportunities are customer words", "“I can't tell if my order shipped” is an opportunity. “Add tracking” is a solution."),
              ("Compare and contrast", "Exploring several solutions at once avoids falling in love with the first idea."),
              ("Test assumptions, not ideas", "Break each solution into what must be true, and test the riskiest part only."),
              ("Keep it alive", "Update the tree every week as you learn. It's a living map, not a plan."),
              ("Talk to customers weekly", "Regular interviews keep opportunities grounded in real evidence.")],
        pitfalls=("an output as the outcome; opportunities that are really features; only one solution per opportunity; "
                  "testing whole solutions instead of assumptions; building before testing; never updating the tree."),
        after=[("This week", "Run the assumption tests and record results on the board."),
               ("Each week", "The trio updates the tree with new interviews and test results."),
               ("When an assumption holds", "Move the solution into delivery: Epic Canvas, Story Map and splitting."),
               ("When it fails", "Celebrate the learning, then try the next solution or opportunity.")],
        toolkit=LIFECYCLE_TOOLKIT,
        foot="“Which customer need, if we solved it, would move our outcome most?”",
    ),

    # -------------------------------------------------------------- team topology
    dict(
        slug="team-topology",
        title="Team Topology Design Guide",
        subtitle="How to design teams around the flow of value, with clear team types, interaction modes and manageable load.",
        tag="Facilitator Run-Sheet · Coordinate Teams · Inspired by Team Topologies (Skelton & Pais)",
        boards=[("Open board", "team-topology-board.html"), ("SVG", "team-topology-board.svg")],
        lede="Which team is carrying more than it can hold?",
        intro=("Many delivery problems, such as dependencies, hand-offs and overloaded teams, come from how teams are "
               "organised. <i>Team Topologies</i> by Matthew Skelton and Manuel Pais offers four <b>team types</b> "
               "(stream-aligned, platform, enabling and complicated subsystem) and three <b>interaction modes</b> "
               "(collaboration, X-as-a-service and facilitating). It also asks whether each team's <b>cognitive load</b> is "
               "manageable. This board helps leaders and teams map today's structure and find changes worth trying."),
        glance=[("Duration", "2–3 h"), ("Group", "Leaders, eng managers,<br>team reps, architects"),
                ("Use when", "Dependencies or<br>overload keep growing"), ("Output", "A team map &amp;<br>changes to try")],
        before=["Print the board at A1 or A3, or load the SVG as a digital background",
                "List current teams with their size, what they own, and who they depend on",
                "Bring the Dependency Map and any recent Team Health Check results",
                "Invite people from several teams, not just leaders",
                "Yellow and pink stickies, markers, and three colours of pen or string for interaction modes"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–20", "1 · Team Types", "Explain the four types. Write each current team under the type it most resembles today."),
                ("20–50", "2 · Team Map", "Place each team on the map, grouped by value stream. Draw how they interact today, using the three line styles."),
                ("50–75", "3 · Cognitive Load", "For each team, list the domains and systems it owns and rate its load. Mark teams that hold too much."),
                ("75–100", "Spot problems", "Look for overloaded teams, long-running collaborations, and teams with many dependencies. Add pink stickies."),
                ("100–130", "4 · Interactions · 5 · Changes", "Agree intended interaction modes with end dates, and list changes to try, such as a platform or enabling team."),
                ("130–150", "Close", "Pick one change to try first, with an owner and a review date.")],
        sections_title="Reading the map",
        sections_intro="Patterns that suggest a change.",
        sections=[("Overloaded team", RED, ["Owns too many domains", "Split it, or move work to a platform"]),
                  ("Endless collaboration", PURPLE, ["Two teams always together", "Merge them, or define a service"]),
                  ("No stream-aligned teams", EMERALD, ["Work flows through many teams", "Re-form around value streams"]),
                  ("Skill gaps everywhere", BLUE, ["Consider an enabling team", "It should step back when done"]),
                  ("Interaction Agreements", SLATE, ["Each has a purpose", "Collaborations have an end date"])],
        tips=[("Stream-aligned first", "Most teams should own a flow of value end to end. Others exist to help them."),
              ("Load is the limit", "A team can only hold so much. If it owns too much, quality and speed drop."),
              ("Interactions are deliberate", "Choose the mode on purpose, and change it as the relationship matures."),
              ("Collaboration is temporary", "Close collaboration is expensive. Use it to discover, then move to a service."),
              ("Small changes first", "Try one boundary change at a time and watch dependencies and flow."),
              ("Involve the teams", "People in the teams know where the friction is. Design with them, not for them.")],
        pitfalls=("redrawing an org chart without changing how work flows; ignoring cognitive load; permanent collaboration; "
                  "platform teams that become gatekeepers; designing teams without the people in them; changing everything at once."),
        after=[("Straight away", "Share the map and the first change with the teams affected."),
               ("Over the next quarter", "Run the change and watch dependencies, flow and team health."),
               ("At the review date", "Check what changed and decide the next step."),
               ("Twice a year", "Re-map teams as products and strategy change.")],
        toolkit=PROGRAM_TOOLKIT,
        foot="“If we redrew one team boundary, which dependency would disappear?”",
    ),

    # -------------------------------------------------------------- AI working agreement
    dict(
        slug="ai-working-agreement",
        title="AI Working Agreement Guide",
        subtitle="How to help a team agree how it uses AI tools: where they help, the guardrails, review rules and impact.",
        tag="Facilitator Run-Sheet · Form the Team · Responsible Use · Human Review",
        boards=[("Open board", "ai-working-agreement-board.html"), ("SVG", "ai-working-agreement-board.svg")],
        lede="Where does AI genuinely help us, and where does it get in the way?",
        intro=("Most teams now use AI tools for drafting, summarising, analysis, tests or code, often without agreeing how. "
               "This board helps the team make its use <b>explicit</b>: which tasks AI is encouraged for, used with care, or "
               "not used for; the <b>guardrails</b> on data and tools; how output is <b>reviewed</b>; how skills are shared; "
               "the <b>risks</b> to watch; and how to <b>measure</b> whether it actually helps. It complements, and never "
               "replaces, your organisation's AI and data policies."),
        glance=[("Duration", "60–90 min"), ("Group", "The whole team,<br>PO included"),
                ("Use when", "AI use starts or grows,<br>or tools change"), ("Output", "An agreed, reviewed<br>way of working")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Find your organisation's AI, data and security policies, and the approved tools",
                "Ask team members how they use AI today, without judgement",
                "Gather a baseline for a few measures, such as cycle time or defects found later",
                "Invite someone from security or data protection if the team handles sensitive data"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "Today", "Go round: how does each person use AI now? What has helped, and what has gone wrong?"),
                ("10–25", "1 · Where We Use AI", "Sort tasks into encouraged, with care, and not for. Be specific about tasks."),
                ("25–40", "2 · Guardrails", "Check the boxes that apply, and fill in approved tools and the policy contact."),
                ("40–55", "3 · Quality & Review", "Agree review rules and any additions to the Definition of Done."),
                ("55–65", "4 · Skills · 5 · Risks", "Agree how the team shares what works and keeps skills sharp. List the risks to watch."),
                ("65–80", "6 · Measure the Impact", "Pick 2–4 measures with a baseline. Agree when to check them."),
                ("80–90", "7 · Review · Close", "Agree a review date (often monthly at first) and confirm everyone agrees.")],
        sections_title="Making each section strong",
        sections_intro="Quality checks for each part of the agreement.",
        sections=[("1 · Where We Use AI", BLUE, ["Named tasks, not “anything”", "Not-for list is explicit"]),
                  ("2 · Guardrails", RED, ["Matches organisation policy", "Data rules are clear"]),
                  ("3 · Quality & Review", PURPLE, ["Same bar for all work", "A person owns every result"]),
                  ("4 · Skills & Sharing", EMERALD, ["Good prompts are shared", "Core skills are practised"]),
                  ("5 · Risks We'll Watch", AMBER, ["Errors, data, bias, over-reliance", "Who notices and how"]),
                  ("6 · Measure the Impact", FOREST, ["A baseline exists", "Quality as well as speed"]),
                  ("7 · Review", SLATE, ["A short review cycle", "Whole team agreed"])],
        tips=[("Policy first", "The team agreement sits inside the organisation's rules. Check them before you start."),
              ("Specific tasks", "“Drafting release notes” is clear. “Writing” is not."),
              ("People own results", "Whoever uses AI is accountable for the output, as with any tool."),
              ("Measure quality too", "Faster isn't better if defects or rework go up. Track both."),
              ("Share openly", "Make it normal to say how work was produced. It builds trust and spreads good practice."),
              ("Review often", "Tools and policies change quickly. Revisit the agreement monthly at first.")],
        pitfalls=("ignoring organisation policy; banning AI so people use it quietly; no review of AI output; measuring only "
                  "speed; letting core skills fade; writing the agreement once and never revisiting it."),
        after=[("Straight away", "Put the agreement next to the Team Charter and link it from the team's space."),
               ("Each retro", "Ask: is the agreement working? Any near misses or great wins?"),
               ("Monthly", "Check the impact measures and update the agreement."),
               ("When tools change", "Revisit the guardrails and review rules before using new tools.")],
        toolkit=LIFECYCLE_TOOLKIT,
        foot="“Would we be comfortable explaining how this was made?”",
    ),

    # -------------------------------------------------------------- status report
    dict(
        slug="status-report",
        title="Outcome Status Report Guide",
        subtitle="How to write a one-page update built on outcomes, a forecast range, risks and the decisions you need.",
        tag="Facilitator Run-Sheet · Run a Project · Outcomes Over Output · Decisions, Not Just Status",
        boards=[("Open board", "status-report-board.html"), ("SVG", "status-report-board.svg")],
        lede="What decision do we need, and from whom?",
        intro=("Traditional status reports turn amber when it's already too late, and rarely ask for anything. This one-page "
               "report leads with a <b>headline</b>, a <b>confidence</b> rating and its trend, then shows progress on "
               "<b>outcomes</b>, the <b>forecast range</b> and what moved it, what was <b>delivered and learned</b>, the top "
               "<b>risks</b>, and the <b>decisions needed</b>. It's built from boards the team already keeps, so it takes "
               "minutes, not hours, to write."),
        glance=[("Duration", "20–30 min<br>to prepare"), ("Group", "PM or program lead,<br>with the PO"),
                ("Use when", "Every 2–4 weeks,<br>or for steering"), ("Output", "A one-page update<br>&amp; clear asks")],
        before=["Print the board at A3, or use a digital copy for each report",
                "Bring the latest Release Forecast, RAID Log and value or OKR measures",
                "Check what was released or demonstrated since the last report",
                "Know who the readers are and what decisions they own (see the Stakeholder Map)"],
        agenda_heads=["Step", "Section", "Notes"],
        agenda=[("1", "2 · Outcomes", "Update each outcome measure: start, now, target and trend."),
                ("2", "3 · Forecast", "Copy the range from the Release Forecast. Say if it moved, and why."),
                ("3", "4 · Delivered & Learned", "List working, in-use deliveries and anything that changed your thinking."),
                ("4", "5 · Top Risks & Issues", "Copy the top few from the RAID Log, with actions and owners."),
                ("5", "6 · Decisions Needed", "Write each decision, who must make it, and by when."),
                ("6", "1 · Headline", "Last: write one sentence, a confidence rating 1–5, and the trend since last time.")],
        sections_title="Making each section strong",
        sections_intro="Quality checks for each part of the report.",
        sections=[("1 · Headline", PURPLE, ["One honest sentence", "Confidence and trend are clear"]),
                  ("2 · Outcomes", EMERALD, ["Outcomes, not task lists", "Start, now and target shown"]),
                  ("3 · Forecast", AMBER, ["A range, not a date", "What moved it"]),
                  ("4 · Delivered & Learned", BLUE, ["Working and in use", "Learning is shared"]),
                  ("5 · Top Risks & Issues", RED, ["Each has an action and owner", "Matches the RAID Log"]),
                  ("6 · Decisions Needed", FOREST, ["Specific asks", "A named person and a date"])],
        tips=[("Write the headline last", "Once the rest is done, the one-sentence summary is easy and honest."),
              ("Confidence beats colours", "A 1–5 confidence rating with a trend says more than red, amber or green."),
              ("Lead with outcomes", "Readers care about what changed for customers and the business, not tasks completed."),
              ("Always ask for something", "If no decisions are needed, say so. Usually there's at least one."),
              ("Reuse the boards", "Copy from the Release Forecast and RAID Log rather than writing from scratch."),
              ("Same shape every time", "A consistent format lets readers spot changes quickly.")],
        pitfalls=("a wall of task updates; a single date instead of a range; hiding bad news until it's red; no decisions "
                  "requested; different formats every time; writing it from scratch instead of from the boards."),
        after=[("Straight away", "Send it to the readers and walk the key ones through it in person or on a call."),
               ("Follow up", "Chase the decisions needed before their dates."),
               ("Next report", "Start by noting what changed since this one."),
               ("Over time", "Ask readers what they use and what they don't, and trim the report.")],
        toolkit=PROJECT_TOOLKIT,
        foot="“What has changed for our customers since the last report?”",
    ),
]
GUIDES += WAVE1_GUIDES

GUIDES.append(dict(
    slug="adkar",
    title="ADKAR Change Readiness Guide",
    subtitle="How to find where people are in a change, spot the barrier point, and act on the right thing first.",
    tag="Facilitator Run-Sheet · Lead the Organisation · Inspired by Prosci's ADKAR® Model",
    boards=[("Open board", "adkar-board.html"), ("SVG", "adkar-board.svg")],
    lede="What's the first thing stopping them, and what would help most?",
    intro=("Organisations change only when people do, one person at a time. The ADKAR® model, created by Jeff Hiatt and "
           "developed by Prosci, describes five things each person needs, in order: <b>Awareness</b> of why the change is "
           "needed, <b>Desire</b> to support it, <b>Knowledge</b> of how to change, <b>Ability</b> to do it in practice, and "
           "<b>Reinforcement</b> to make it stick. Scoring each element shows the <b>barrier point</b>: the first one that's "
           "missing. Effort spent on later elements is wasted until it's fixed; training doesn't help people who don't yet "
           "see why. Use it for any change, from a new way of working to a new tool or an agile transformation. "
           "ADKAR® is a registered trademark of Prosci, Inc."),
    glance=[("Duration", "60–90 min, then<br>re-assess monthly"), ("Group", "Change lead, sponsor,<br>managers, coaches"),
            ("Use when", "A change is planned,<br>or has stalled"), ("Output", "Barrier points<br>&amp; targeted actions")],
    before=["Print the board at A3, or load the SVG as a digital background",
            "Agree the change you're assessing, and its sponsor",
            "List the groups or people affected; the Stakeholder Map is a good source",
            "Gather evidence: survey results, questions people ask, adoption data, manager feedback",
            "Decide whether to score groups together or ask people to score themselves (often more honest)"],
    agenda_heads=["Time", "Section", "Facilitator notes"],
    agenda=[("0–10", "1 · Change on a Page", "Write what's changing, why now, who's affected and the key dates."),
            ("10–20", "The model", "Walk through the five elements and the idea of the barrier point. Use the element panels for examples."),
            ("20–45", "2 · Readiness Grid", "For each person or group, score each element 1–5 from evidence. Circle the barrier point: the first score of 3 or lower."),
            ("45–65", "Element panels", "For each barrier point, look at what helps for that element and write your own action."),
            ("65–80", "3 · Action Plan", "One action per barrier point, with an owner and a date. Focus effort on the earliest barriers."),
            ("80–90", "4 · Reinforce · Close", "Agree how you'll recognise success, measure adoption, and when to re-assess.")],
    sections_title="The five elements",
    sections_intro="Each must be in place before the next can work.",
    sections=[("Awareness", BLUE, ["Do people know why?", "Sponsor and managers explain it", "Share the cost of not changing"]),
              ("Desire", PURPLE, ["Do people want to take part?", "Involve them in shaping it", "Address what's in it for them"]),
              ("Knowledge", SKY, ["Do people know how?", "Training, guides, examples"]),
              ("Ability", EMERALD, ["Can they do it for real?", "Coaching, practice, time", "Remove blockers"]),
              ("Reinforcement", ORANGE, ["Will it last?", "Recognition, measures", "Stop rewarding the old way"]),
              ("Barrier point", RED, ["The first score of 3 or lower", "Fix it before later elements"])],
    tips=[("Order matters", "Training (Knowledge) won't help if people don't see why (Awareness) or don't want to (Desire)."),
          ("Score from evidence", "Use what people say and do, not what leaders hope. Self-scores are often more honest."),
          ("Groups differ", "Different groups often have different barrier points. Plan separate actions."),
          ("Desire is personal", "It can't be ordered. Listen to concerns and involve people in shaping the change."),
          ("Ability needs time", "Knowing isn't doing. Plan practice, coaching and pairing, and expect a dip at first."),
          ("Don't skip reinforcement", "Without it, people drift back. Measure adoption and recognise it.")],
    pitfalls=("starting with training; scoring from leaders' assumptions; one plan for everyone; treating resistance as a "
              "character flaw; declaring success at go-live; never re-assessing."),
    after=[("Straight away", "Share the barrier points and actions with the sponsor and managers."),
           ("Each week", "Owners act on their barrier points; managers check in with their teams."),
           ("Monthly", "Re-score the grid. Barrier points should move right as the change takes hold."),
           ("After go-live", "Keep reinforcing and measuring adoption until the new way is normal.")],
    toolkit=("ADKAR is about the people side of change. Use the <a href=\"facilitator-guide-stakeholder-map.html\">Stakeholder "
             "Map</a> to find who's affected, the <a href=\"facilitator-guide-skills-matrix.html\">Skills Matrix</a> and "
             "<a href=\"facilitator-guide-pairing-mobbing.html\">Pairing &amp; Mobbing</a> to build Ability, the "
             "<a href=\"facilitator-guide-team-health-check.html\">Team Health Check</a> to see how teams are coping, and "
             "<a href=\"facilitator-guide-value-metrics.html\">Value Metrics</a> to show the change is paying off."),
    foot="“Where is each group in this change, really?”",
))


LEAD_TOOLKIT = ("The leadership tools work together: <a href=\"facilitator-guide-value-metrics.html\">Value Metrics</a> show "
                "whether investment is paying off, the <a href=\"facilitator-guide-portfolio-kanban.html\">Portfolio Kanban</a> "
                "decides what to fund and limits how much runs at once, the <a href=\"facilitator-guide-delegation.html\">Delegation "
                "Board</a> makes decision rights explicit, and <a href=\"facilitator-guide-adkar.html\">ADKAR Change Readiness</a> "
                "helps people through the change. <a href=\"facilitator-guide-okr.html\">OKRs</a> and "
                "<a href=\"facilitator-guide-team-topology.html\">Team Topology Design</a> connect them to the teams.")

GUIDES += [
    # -------------------------------------------------------------- portfolio kanban
    dict(
        slug="portfolio-kanban",
        title="Portfolio Kanban & Investment Mix Guide",
        subtitle="How to limit how many big initiatives run at once, decide with a lean business case, and balance investment.",
        tag="Facilitator Run-Sheet · Lead the Organisation · Lean Portfolio Management",
        boards=[("Open board", "portfolio-kanban-board.html"), ("SVG", "portfolio-kanban-board.svg")],
        lede="What would we stop to make room for this?",
        intro=("Most organisations start far more initiatives than they can finish, so everything moves slowly. A "
               "<b>portfolio Kanban</b> applies the same flow ideas as a team board to big initiatives: every idea enters a "
               "funnel, moves forward only when there's capacity, and each column has a <b>WIP limit</b> and exit criteria. A "
               "<b>lean business case</b> replaces long proposals with a testable hypothesis and an MVP, and the <b>investment "
               "mix</b> keeps new bets, growth, maintenance and tech debt in a deliberate balance. These ideas come from lean "
               "portfolio management and the Kanban Method."),
        glance=[("Duration", "2 h to set up<br>60 min each review"), ("Group", "Portfolio leaders,<br>product heads, finance"),
                ("Use when", "Too much in flight,<br>or funding is annual"), ("Output", "A limited, visible<br>portfolio &amp; a mix")],
        before=["Print the board at A1 or A3, or load the SVG as a digital background",
                "List every current initiative and every proposal waiting for approval",
                "Gather what's known about each: stage, cost so far, expected outcome",
                "Bring the strategy, OKRs and any Value Metrics",
                "Invite the people who can stop as well as start initiatives"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–25", "1 · Place initiatives", "Put each initiative in the column that reflects reality, not plans. Count how many are in Implementing."),
                ("25–45", "WIP limits & exits", "Agree a WIP limit and exit criteria for each column. Most portfolios need to stop or pause some work to meet them."),
                ("45–70", "2 · Lean Business Case", "For one initiative in Analysing, complete the case: hypothesis, MVP, cost range, cost of delay and go/no-go."),
                ("70–90", "3 · Investment Mix", "Agree the target split by type of work, then estimate the actual split today."),
                ("90–110", "Decide", "Use the gaps to decide what to stop, pause or pull forward. Stop something to start something."),
                ("110–120", "4 · Review", "Agree the review cadence and decision forum.")],
        sections_title="Making each part work",
        sections_intro="Quality checks for the board.",
        sections=[("1 · Portfolio Kanban", BLUE, ["Reality, not the plan", "WIP limits are respected", "Exit criteria are clear"]),
                  ("2 · Lean Business Case", PURPLE, ["A testable hypothesis", "An MVP, not the full scope", "Go/no-go agreed up front"]),
                  ("3 · Investment Mix", EMERALD, ["Target agreed by leaders", "Actual compared regularly"]),
                  ("4 · Portfolio Review", AMBER, ["A regular cadence", "Outcomes checked, not just spend"])],
        tips=[("Count what's in flight", "Seeing everything in one place is often enough to start the conversation about stopping."),
              ("Stop to start", "Make it a rule: a new initiative enters Implementing only when another leaves."),
              ("Fund the MVP first", "Approve the smallest test of the hypothesis, then decide again with evidence."),
              ("Show cost of delay", "Ranking by cost of delay, not by who shouts loudest, makes trade-offs visible."),
              ("Protect the mix", "Without a target, run-and-maintain and urgent work slowly squeeze out new bets and debt."),
              ("Review often", "Quarterly or monthly reviews beat annual funding cycles for adapting to what you learn.")],
        pitfalls=("no WIP limits, so everything stays in flight; business cases that are full project plans; approving everything; "
                  "never stopping an initiative; tracking spend but not outcomes; an investment mix nobody checks."),
        after=[("Straight away", "Communicate what's paused or stopped, and why."),
               ("Each review", "Update the board, check WIP limits and the mix, and decide what moves."),
               ("Per initiative", "When an MVP finishes, decide persevere, pivot or stop from its evidence."),
               ("Quarterly", "Compare outcomes with Value Metrics and adjust the target mix.")],
        toolkit=LEAD_TOOLKIT,
        foot="“Which initiative, if it were the only one, would we finish first?”",
    ),

    # -------------------------------------------------------------- delivery metrics
    dict(
        slug="delivery-metrics",
        title="Delivery Metrics & Tech Debt Guide",
        subtitle="How to track delivery speed and stability with four key metrics, and keep technical debt visible and managed.",
        tag="Facilitator Run-Sheet · Manage Flow · Inspired by DORA · Technical Debt Quadrant",
        boards=[("Open board", "delivery-metrics-board.html"), ("SVG", "delivery-metrics-board.svg")],
        lede="Are we getting faster without getting less stable?",
        intro=("The four key metrics from the DORA research programme (DevOps Research and Assessment) balance <b>speed</b> "
               "(deployment frequency and lead time for changes) with <b>stability</b> (change failure rate and recovery time). "
               "Improving one pair at the expense of the other shows up straight away. The <b>tech debt register</b> makes "
               "debt visible with its <b>interest</b>, the ongoing cost of leaving it, and Martin Fowler's <b>technical debt "
               "quadrant</b> helps the team talk about why the debt exists without blame."),
        glance=[("Duration", "60–90 min to set up<br>30 min monthly"), ("Group", "Eng manager,<br>tech lead, team"),
                ("Use when", "Releases feel slow<br>or risky"), ("Output", "Baselines, a debt<br>register &amp; a plan")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Pull data for the four metrics from your pipeline, release and incident tools, if you can",
                "Agree definitions: what counts as a deployment, a failure and a recovery",
                "Ask the team to list known technical debt in advance",
                "Bring the Blocker Clustering and Ageing WIP boards if you use them"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–25", "1 · Four Key Metrics", "Agree definitions, then fill in 3 months ago, now and target for each. Note where the data comes from."),
                ("25–30", "Read the pattern", "Speed up but stability down? Or the reverse? Discuss what the pattern says."),
                ("30–60", "2 · Tech Debt Register", "List the main debt items with where they are, the interest they cost, effort and an owner."),
                ("60–70", "3 · Debt Quadrant", "Place each item in a quadrant. Talk about the reckless ones without blame: what made it happen?"),
                ("70–80", "4 · Time to Pay It Down", "Agree a share of each iteration for debt and enablers, and what you'll pay down first."),
                ("80–90", "5 · Review", "Agree how often to review the metrics and the register.")],
        sections_title="Reading the metrics",
        sections_intro="Look at the four together; they're designed to balance each other.",
        sections=[("Deployment Frequency", EMERALD, ["More often, smaller releases", "Lower risk per release"]),
                  ("Lead Time for Changes", SKY, ["Commit to production", "Look for waiting time"]),
                  ("Change Failure Rate", ORANGE, ["% of releases needing a fix", "Rises if speed outruns quality"]),
                  ("Recovery Time", RED, ["How fast you restore service", "Practice and automation help"]),
                  ("Tech Debt Register", PURPLE, ["Interest, not just size", "Owned and prioritised"])],
        tips=[("Trends, not league tables", "Compare a team with its own past, never with other teams."),
              ("Balance speed and stability", "If one pair improves while the other worsens, slow down and find out why."),
              ("Debt has interest", "Prioritise the debt that slows every change, not the debt that's merely ugly."),
              ("Make time explicit", "A fixed share of each iteration for debt beats waiting for a quiet period that never comes."),
              ("No blame in the quadrant", "Reckless debt usually comes from pressure or missing skills. Fix the cause."),
              ("Automate the data", "Collect the metrics from your tools so measuring doesn't become a chore.")],
        pitfalls=("using the metrics to rank teams or people; gaming deployment counts; ignoring stability; a debt list with no "
                  "interest or owner; no time set aside to pay debt down; arguing about definitions forever."),
        after=[("Straight away", "Add the top debt items to the backlog with their interest noted."),
               ("Each iteration", "Spend the agreed share on debt and enablers."),
               ("Monthly", "Update the four metrics and review the trend with the team."),
               ("Quarterly", "Share the trend and debt progress in the Value Metrics review (ability to innovate).")],
        toolkit=FLOW_TOOLKIT,
        foot="“Which debt is costing us most every week we leave it?”",
    ),

    # -------------------------------------------------------------- delegation
    dict(
        slug="delegation",
        title="Delegation Board Guide",
        subtitle="How to agree who decides what, at which of seven levels, and how to move decisions toward the team over time.",
        tag="Facilitator Run-Sheet · Lead the Organisation · Inspired by Management 3.0",
        boards=[("Open board", "delegation-board.html"), ("SVG", "delegation-board.svg")],
        lede="Which decisions could the team make without us?",
        intro=("Empowerment isn't all or nothing. The delegation board, from Jurgen Appelo's Management 3.0, uses <b>seven "
               "levels</b> from <b>Tell</b> (the leader decides) to <b>Delegate</b> (the team decides and doesn't need to report "
               "back). For each <b>decision area</b>, the leader and team agree today's level and where they want to get to. "
               "Making it explicit avoids two common problems: teams waiting for permission they already have, and leaders "
               "overruling decisions they'd said were delegated."),
        glance=[("Duration", "60–90 min"), ("Group", "A leader and<br>their team"),
                ("Use when", "Decision rights are<br>unclear or contested"), ("Output", "Agreed levels<br>&amp; guardrails")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "List decision areas the team cares about, or ask the team to bring them",
                "Leaders: think about which areas you're genuinely ready to delegate further",
                "Bring any policies or limits that always apply (budget, legal, security)",
                "Optionally, use delegation poker cards (1–7) for voting"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "The seven levels", "Walk through the levels with an example for each. Stress that every level is fine for some decisions."),
                ("10–25", "Decision areas", "List 6–9 decision areas. Use the hints on the board if the team is stuck."),
                ("25–55", "Agree levels", "For each area, everyone votes a level at once (delegation poker). Discuss differences, then mark today's level."),
                ("55–70", "Where we're heading", "Draw an arrow to the level you want to reach, and set a review date."),
                ("70–80", "2 · Guardrails", "Write the limits that apply at every level, such as budget or policy."),
                ("80–90", "3 · Next Steps · Close", "Agree which area moves up first, and post the board where everyone can see it.")],
        sections_title="The seven levels",
        sections_intro="Each level describes who decides and how the other party is involved.",
        sections=[("1 Tell · 2 Sell", RED, ["The leader decides", "Sell explains why"]),
                  ("3 Consult", AMBER, ["Leader asks, then decides", "Input is genuinely considered"]),
                  ("4 Agree", PURPLE, ["Decided together", "Takes the most time"]),
                  ("5 Advise · 6 Inquire", BLUE, ["The team decides", "Leader advises or hears afterwards"]),
                  ("7 Delegate", EMERALD, ["The team decides alone", "No need to report back"]),
                  ("Guardrails", SLATE, ["Limits at every level", "Written down, not assumed"])],
        tips=[("Every level is valid", "The aim isn't level 7 for everything. It's clarity about the right level for each area."),
              ("Vote simultaneously", "Delegation poker stops people anchoring on the leader's view."),
              ("Leaders go first in trust", "Moving an area up one level is a small, concrete way to build trust."),
              ("Guardrails enable delegation", "Clear limits make it easier for leaders to let go."),
              ("Keep your word", "Overruling a delegated decision costs more trust than never delegating it."),
              ("Revisit it", "As the team grows, move areas up. Review every few months.")],
        pitfalls=("leaders announcing levels instead of agreeing them; everything at level 7 on paper but not in practice; "
                  "overruling delegated decisions; vague decision areas; no guardrails; never reviewing it."),
        after=[("Straight away", "Post the board where the team and leader can both see it."),
               ("When a decision comes up", "Check the board first: who decides, at what level?"),
               ("At the review date", "Move areas up where the team is ready; discuss any that went wrong."),
               ("When people change", "Revisit the board with new leaders or team members.")],
        toolkit=LEAD_TOOLKIT,
        foot="“What would we need to trust to move this up one level?”",
    ),

    # -------------------------------------------------------------- coaching conversation
    dict(
        slug="coaching-conversation",
        title="Coaching Conversation Guide",
        subtitle="How to run a one-to-one coaching conversation with the GROW model: goal, reality, options and will.",
        tag="Facilitator Run-Sheet · Facilitate · GROW Model (Sir John Whitmore)",
        boards=[("Open board", "coaching-conversation-board.html"), ("SVG", "coaching-conversation-board.svg")],
        lede="What do you want to be different by the end of this conversation?",
        intro=("Coaching helps people find their own answers rather than being told what to do. The <b>GROW</b> model, "
               "popularised by Sir John Whitmore in <i>Coaching for Performance</i>, gives a one-to-one conversation a simple "
               "shape: agree the <b>Goal</b>, explore the current <b>Reality</b>, generate <b>Options</b>, and finish with the "
               "coachee's <b>Will</b>, their committed next steps. The canvas starts with a short contract and ends with the "
               "coach's own reflection. Scrum Masters, agile coaches, managers and mentors can all use it."),
        glance=[("Duration", "30–60 min"), ("Group", "One coach,<br>one coachee"),
                ("Use when", "1:1s, career talks,<br>stuck problems"), ("Output", "The coachee's own<br>commitments")],
        before=["Print the canvas at A3, or use it on screen; the coachee can keep it afterwards",
                "Book a private space and enough uninterrupted time",
                "Agree in advance that this is coaching, not a performance review",
                "Clear your head: plan to ask more than you tell"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–5", "1 · Contract", "Ask what they want from the conversation. Agree confidentiality and how long you have."),
                ("5–15", "2 · Goal", "Help them describe what they want and what success looks like. Make it specific."),
                ("15–30", "3 · Reality", "Explore what's happening now, what they've tried, and what's in their control. Listen more than talk."),
                ("30–45", "4 · Options", "Generate many options. Keep asking “what else?” Hold back your own ideas, or offer them last."),
                ("45–55", "5 · Will", "Ask which option they'll take, the first step, what might stop them, and how committed they are."),
                ("55–60", "6 · Commitments · 7 · Reflection", "They write the commitments in their own words. Afterwards, reflect on your coaching.")],
        sections_title="Using each stage well",
        sections_intro="What to aim for in each part of the conversation.",
        sections=[("Goal", PURPLE, ["Their goal, not yours", "Specific and meaningful"]),
                  ("Reality", BLUE, ["Facts and feelings", "What they control"]),
                  ("Options", EMERALD, ["Quantity before quality", "Their ideas first"]),
                  ("Will", ORANGE, ["A first step and a date", "Commitment 1–10"]),
                  ("Coach's Reflection", AMBER, ["Did I ask or tell?", "What will I follow up?"])],
        tips=[("Ask, then wait", "Silence gives people room to think. Count to five before you speak."),
              ("Open questions", "Start with what, how and who. “Why” can sound like judgement; use it gently."),
              ("Their words", "Write commitments in the coachee's words, not your summary."),
              ("Loop back", "If options stall, return to Reality or Goal. GROW isn't strictly one-way."),
              ("Low commitment is useful", "If they say 5 out of 10, ask what would make it an 8."),
              ("Follow up", "Start the next conversation by asking how the commitments went.")],
        pitfalls=("giving advice too early; turning it into a status update; setting the goal for them; leading questions; "
                  "running out of time before Will; no follow-up."),
        after=[("Straight away", "Give the coachee the canvas or a photo of it."),
               ("Before the next one", "Read your reflection notes and the commitments."),
               ("Next conversation", "Start with the commitments: what happened, what did you learn?"),
               ("For yourself", "Ask for feedback on your coaching every few sessions.")],
        toolkit=("Coaching conversations connect to the rest of the toolkit: use the "
                 "<a href=\"scrum-master-agile-coach-cheat-sheet.html\">Scrum Master &amp; Agile Coach Cheat Sheet</a> for "
                 "coaching stances and powerful questions, the <a href=\"facilitator-guide-skills-matrix.html\">Skills Matrix</a> "
                 "for learning goals, and <a href=\"facilitator-guide-adkar.html\">ADKAR</a> when the topic is a change someone is "
                 "going through."),
        foot="“What's the smallest step you could take this week?”",
    ),

    # -------------------------------------------------------------- psychological safety
    dict(
        slug="psych-safety",
        title="Psychological Safety Check Guide",
        subtitle="How to run an anonymous check of how safe it feels to speak up, and act on what the team learns.",
        tag="Facilitator Run-Sheet · Diagnose · Inspired by Amy Edmondson's Research",
        boards=[("Open board", "psych-safety-board.html"), ("SVG", "psych-safety-board.svg")],
        lede="What would make it easier to say what you really think here?",
        intro=("Psychological safety is the shared belief that it's safe to take interpersonal risks: to speak up, ask for "
               "help, admit a mistake or disagree. Amy Edmondson's research, and Google's Project Aristotle, found it to be one "
               "of the strongest signs of an effective team. This board uses seven statements, written for this toolkit and "
               "inspired by Edmondson's work, with an <b>anonymous</b> five-point vote. It's a conversation starter, not a "
               "validated survey. What matters most is how the team and its leaders respond to the results."),
        glance=[("Duration", "45–60 min"), ("Group", "One team; leaders<br>step out to vote"),
                ("Use when", "Quiet retros, conflict,<br>or every quarter"), ("Output", "A picture of safety<br>&amp; experiments")],
        before=["Print the board at A3, or run the vote in an anonymous online form",
                "Agree with leaders that they'll step out while the team votes, and won't ask who voted what",
                "Decide in advance who sees the results; by default, only the team",
                "Bring dot stickers or markers",
                "Think about facilitation: someone outside the team's reporting line often helps"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–5", "Why", "Explain the purpose and the rules: anonymous, no one explains their vote, results stay with the team."),
                ("5–15", "1 · The Check", "Everyone places one dot per statement, privately. Turn the board away, or use an online form."),
                ("15–20", "2 · Results", "Count agree and disagree for each statement. Note the change from last time."),
                ("20–35", "3 · What We Notice", "Discuss patterns: which statements are lowest, and what might explain it? Talk about situations, not people."),
                ("35–45", "4 · What Leaders Can Do", "If leaders rejoin, share the patterns and ask them to pick behaviours to practise."),
                ("45–55", "5 · Our Experiments", "Agree one or two small experiments and when to check them.")],
        sections_title="Reading the results",
        sections_intro="Look for patterns, not a single score.",
        sections=[("Mistakes & risk (1, 4)", RED, ["Low here: people hide errors", "Celebrate learning from failure"]),
                  ("Speaking up (2, 7)", PURPLE, ["Low here: quiet meetings", "Ask for dissent explicitly"]),
                  ("Belonging (3, 6)", BLUE, ["Low here: people feel outside", "Check who's not being heard"]),
                  ("Help (5)", EMERALD, ["Low here: people struggle alone", "Normalise asking"]),
                  ("Change over time", SLATE, ["Trend matters most", "Re-run every 2–3 months"])],
        tips=[("Anonymity is everything", "If people suspect they can be identified, the results will look better than reality."),
              ("Leaders model it", "Safety grows when leaders admit mistakes, ask questions and thank people for bad news."),
              ("Talk about situations", "“When we discussed X, it felt risky to disagree” helps. Naming people doesn't."),
              ("Small experiments", "Try one change, such as round-robin input or a devil's advocate role, and check it."),
              ("Don't shoot the messenger", "A low score is a gift of honesty. Thank the team for it."),
              ("Not a performance measure", "Never use the results to evaluate a manager or team.")],
        pitfalls=("leaders in the room during voting; asking who voted low; sharing results without the team's agreement; "
                  "treating it as a score to hit; no follow-up; running it once and never again."),
        after=[("Straight away", "Photograph the results, then clear the board so votes aren't on display."),
               ("Next few weeks", "Run the experiments and notice what changes in meetings."),
               ("Each retro", "Check in: is it easier to speak up? What's helping?"),
               ("Every 2–3 months", "Re-run the check and compare. Feed themes into the Team Health Check.")],
        toolkit=("Psychological safety underpins everything else. Use it alongside the "
                 "<a href=\"facilitator-guide-team-health-check.html\">Team Health Check</a>, run safer retros from the Retro "
                 "Kit, agree norms in the <a href=\"facilitator-guide-team-charter.html\">Team Charter</a>, and use the "
                 "<a href=\"facilitator-guide-coaching-conversation.html\">Coaching Conversation</a> canvas for one-to-one follow-up."),
        foot="“When did someone last speak up, and what happened next?”",
    ),

    # -------------------------------------------------------------- cross-team retro
    dict(
        slug="cross-team-retro",
        title="Cross-Team Retro Guide",
        subtitle="How to run a retrospective across several teams that finds and fixes problems no single team can solve.",
        tag="Facilitator Run-Sheet · Coordinate Teams · Joint Retrospective · Inspect & Adapt",
        boards=[("Open board", "cross-team-retro-board.html"), ("SVG", "cross-team-retro-board.svg")],
        lede="What got in the way between teams, not within them?",
        intro=("Team retros improve how each team works, but many problems live between teams: hand-offs, dependencies, "
               "shared environments and unclear decisions. A cross-team retro, held at the end of a planning period, brings "
               "representatives from every team together to review the <b>shared objectives</b>, collect what went well and "
               "what didn't <b>across teams</b>, and solve the biggest system problem in mixed-team groups. SAFe calls this "
               "the Inspect &amp; Adapt event's problem-solving workshop."),
        glance=[("Duration", "90–120 min"), ("Group", "Reps from every team,<br>POs, leaders"),
                ("Use when", "End of each planning<br>period"), ("Output", "One system fix<br>&amp; owners")],
        before=["Print the board at A1 or A3, or use a digital board with breakout areas",
                "Bring the shared objectives and their results from the Cross-Team Planning board",
                "Ask each team to bring the top cross-team themes from their own retros",
                "Bring the Dependency Map and the Impediments boards",
                "Green, pink and blue stickies, dot stickers and markers"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–15", "1 · What We Set Out to Do", "Review the shared objectives: planned value, achieved, and what was learned."),
                ("15–40", "2–4 · Gather", "Silent writing on green, pink and blue stickies. Focus on between-team topics. Cluster duplicates."),
                ("40–45", "Dot vote", "Three dots each on the cross-team problems. Pick the top one or two."),
                ("45–80", "5 · Solve the Top Problem", "In mixed-team groups, run 5 Whys to a root cause and propose improvements."),
                ("80–95", "Agree improvements", "Groups share proposals. Agree which to do, the teams involved and an owner."),
                ("95–105", "6 · Follow Through", "Add improvements to the next cross-team plan and agree how to measure success.")],
        sections_title="Making each part strong",
        sections_intro="Quality checks for the board.",
        sections=[("1 · What We Set Out to Do", SLATE, ["Data, not opinions", "Learning, not blame"]),
                  ("2 · Went Well Across Teams", EMERALD, ["Specific examples", "Worth repeating"]),
                  ("3 · Cross-Team Problems", RED, ["Between teams, not within", "Dot-voted"]),
                  ("4 · Ideas", BLUE, ["Anyone can contribute", "Small and testable"]),
                  ("5 · Solve the Top Problem", PURPLE, ["Mixed-team groups", "A root cause, not a symptom"]),
                  ("6 · Follow Through", FOREST, ["Improvements in the next plan", "Each has an owner"])],
        tips=[("Focus between teams", "Steer team-internal issues back to team retros. This session is for the system."),
              ("Mix the groups", "Problem-solving groups with people from several teams see the whole picture."),
              ("One problem, solved", "Fixing one system problem well beats a long list of half-fixes."),
              ("Leaders as participants", "Leaders can remove system constraints that teams can't. Invite them to help solve."),
              ("Plan it in", "Put improvements into the next planning period's capacity, or they won't happen."),
              ("Close the loop", "Start the next cross-team retro by reviewing the last one's improvements.")],
        pitfalls=("teams airing internal issues; blaming other teams; too many improvements; no owners; improvements not "
                  "planned into the next period; skipping it when a period goes well."),
        after=[("Straight away", "Share the improvements and owners with all teams."),
               ("Next planning", "Plan the improvements into the Cross-Team Planning board's capacity."),
               ("During the period", "Track progress at the Cross-Team Sync."),
               ("Next retro", "Review the improvements first: did they help?")],
        toolkit=PROGRAM_TOOLKIT,
        foot="“What one change would help every team next period?”",
    ),
]


GUIDES.append(dict(
    slug="backlog-anatomy",
    title="Backlog Item Anatomy Guide",
    subtitle="How to use the poster to help teams write good epics, features and stories, and spot weak ones.",
    tag="Facilitator Run-Sheet · Break Down Work · Epics, Features & Stories",
    boards=[("Open poster", "backlog-anatomy-poster.html"), ("SVG", "backlog-anatomy-poster.svg")],
    lede="Who is this for, and what will be better for them?",
    intro=("Teams often write epics that are just big tasks, features that are technical layers, and stories that "
           "deliver nothing on their own. The poster shows each level with a <b>definition</b>, a <b>template</b>, a "
           "<b>good example</b> and a <b>weak example</b>, using one running example so people can see how a big bet "
           "becomes a thin slice. It also covers <b>INVEST</b> (from Bill Wake), acceptance criteria in "
           "<b>Given / When / Then</b> form, and the other kinds of backlog item. Names vary by framework and tool: in "
           "SAFe an epic sits above features, while in Jira an epic sits directly above stories. Use the levels your "
           "organisation uses, and see the <a href=\"glossary.html\">glossary</a> for the differences."),
    glance=[("Duration", "45–60 min<br>as a workshop"), ("Group", "Team, PO, BA,<br>stakeholders"),
            ("Use when", "Onboarding, or the backlog<br>is hard to work with"), ("Output", "Rewritten items<br>&amp; shared standards")],
    before=["Print the poster at A3 and pin it where the team refines its backlog",
            "Pick 6–10 real backlog items: a mix of epics, features and stories, good and bad",
            "Write each on a card or sticky, without saying which level it is",
            "Bring the team's Definition of Ready, if it has one"],
    agenda_heads=["Time", "Step", "Facilitator notes"],
    agenda=[("0–10", "Walk the poster", "Read the running example from top to bottom. Ask: how does the story serve the epic's outcome?"),
            ("10–25", "Sort", "In pairs, sort the real items: which level is each, and is it good or weak? Use the poster's templates."),
            ("25–45", "Rewrite", "Rewrite the weak ones using the templates. Split anything that's too big with the Story Splitting poster."),
            ("45–55", "Agree standards", "Agree two or three standards the team will apply, and add them to the Definition of Ready."),
            ("55–60", "Close", "Pick who will tidy the rest of the backlog, and when.")],
    sections_title="What good looks like at each level",
    sections_intro="Quick checks to apply when writing or refining items.",
    sections=[("Epic", PURPLE, ["An outcome, not a solution", "A measure that could prove it wrong", "Broken into features"]),
              ("Feature", BLUE, ["Usable on its own", "A clear benefit to a named user", "Fits in a planning period"]),
              ("Story", EMERALD, ["A vertical slice", "Passes INVEST", "Has acceptance criteria"]),
              ("Acceptance criteria", AMBER, ["Given · When · Then", "Concrete and testable", "Agreed before work starts"]),
              ("Task · Spike · Bug · Enabler", SLATE, ["Tasks live inside stories", "Spikes are time-boxed", "Enablers make future value possible"])],
    tips=[("Start from the user", "Every level should say who benefits. If it can't, it's probably a task."),
          ("Outcomes at the top", "Epics need a measure. Without one, nobody can tell when to stop investing."),
          ("Watch for “and”", "A story with “and” in it is usually two stories."),
          ("Avoid developer stories", "“As a developer, I want…” almost always hides a technical task. Find the user story it serves."),
          ("Criteria make it testable", "Writing two or three Given / When / Then examples often reveals the story is too big."),
          ("Templates are a start", "A good conversation matters more than perfect wording. The template prompts the conversation.")],
    pitfalls=("using the story template for everything, including tasks; epics with no outcome or measure; features split by "
              "technical layer; acceptance criteria written after the work; arguing about labels instead of value."),
    after=[("Straight away", "Leave the poster up in the team space and refer to it in refinement."),
           ("Next refinement", "Check new items against the poster before they're ready."),
           ("Over time", "Add your own good examples from the team's real backlog."),
           ("With stakeholders", "Share the poster when stakeholders bring requests, so ideas arrive as outcomes.")],
    toolkit=BREAKDOWN_TOOLKIT,
    foot="“Could a user use this slice on its own?”",
))


WAVE3_GUIDES = [
    # -------------------------------------------------------------- value stream map
    dict(
        slug="value-stream-map",
        title="Value Stream Map Guide",
        subtitle="How to map every step from request to customer, find where work waits, and design a faster future state.",
        tag="Facilitator Run-Sheet · Manage Flow · Inspired by Lean Value Stream Mapping",
        boards=[("Open board", "value-stream-map-board.html"), ("SVG", "value-stream-map-board.svg")],
        lede="Where does work wait, and why?",
        intro=("Most of the time it takes to deliver something is spent <b>waiting</b>, not working: in queues, hand-offs and "
               "approvals. A value stream map, a lean technique popularised by Mike Rother and John Shook's <i>Learning to "
               "See</i>, follows one type of work from request to customer. It records each step's <b>work time</b> and the "
               "<b>waits</b> between steps, then calculates <b>flow efficiency</b>: work time as a share of total lead time. "
               "The <b>% complete and accurate</b> measure, from Karen Martin and Mike Osterling, shows where rework starts."),
        glance=[("Duration", "2–4 h"), ("Group", "People from every step,<br>plus a sponsor"),
                ("Use when", "Delivery is slow, or<br>teams blame each other"), ("Output", "Current state, totals<br>&amp; a future state")],
        before=["Print the board at A1 or A3, or load the SVG as a digital background",
                "Pick one value stream and one type of work, such as a customer feature request",
                "Gather data where you can: dates for recent items, queue sizes, rework rates",
                "Invite someone who does each step; people closest to the work know where it waits",
                "Ideally, walk the process first (go and see) with a real item"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–15", "1 · Scope", "Agree where the stream starts and ends, the unit of work, and the period you're measuring."),
                ("15–60", "2 · Current state", "Fill in each step: name, who, work time, % complete and accurate, people and WIP. Then estimate the wait before each step."),
                ("60–75", "Timeline", "Write work times on the lower line and waits on the upper line."),
                ("75–90", "3 · Totals", "Add up lead time and work time, calculate flow efficiency, and mark the biggest wait and the most rework."),
                ("90–130", "4 · Future state", "Brainstorm changes: remove waits, combine steps, cut hand-offs, build quality in earlier."),
                ("130–150", "5 · Improvement plan", "Pick one or two changes, with owners and a date to re-measure.")],
        sections_title="Reading the map",
        sections_intro="Patterns to look for.",
        sections=[("Waits much bigger than work", AMBER, ["Common: efficiency under 15%", "Attack the biggest wait first"]),
                  ("Low % complete & accurate", RED, ["Rework starts upstream", "Fix quality at the source"]),
                  ("Many hand-offs", BLUE, ["Each adds a wait and a risk", "Combine or co-locate steps"]),
                  ("High WIP in a step", PURPLE, ["A bottleneck", "Limit WIP, swarm, or add skills"]),
                  ("Future State", FOREST, ["A small number of changes", "Measured again after"])],
        tips=[("Map reality", "Map what actually happens, including workarounds, not the official process."),
              ("Time, not effort", "Measure elapsed time. A step with one hour of work can take a week."),
              ("Estimates are fine", "Rough numbers from the people doing the work are enough to start. Refine later."),
              ("No blame", "Waits are almost always caused by the system: approvals, priorities, handovers."),
              ("Go and see", "Walking a real item through the process reveals steps nobody mentions."),
              ("Re-map later", "Repeat after the changes. The improvement in lead time is the result.")],
        pitfalls=("mapping the ideal process; mixing several types of work; optimising one step while the biggest wait sits "
                  "elsewhere; leaving out the people who do the work; mapping without changing anything."),
        after=[("Straight away", "Share the map and the biggest wait with leaders and every team in the stream."),
               ("Next month", "Run the improvement changes as experiments."),
               ("Each review", "Track lead time and flow efficiency."),
               ("Quarterly", "Re-map the stream and pick the next constraint.")],
        toolkit=FLOW_TOOLKIT,
        foot="“What would it take to halve the lead time?”",
    ),

    # -------------------------------------------------------------- incident review
    dict(
        slug="incident-review",
        title="Blameless Incident Review Guide",
        subtitle="How to learn from an incident by understanding how it made sense at the time, and improving the system.",
        tag="Facilitator Run-Sheet · Improve · Blameless Post-Incident Review",
        boards=[("Open board", "incident-review-board.html"), ("SVG", "incident-review-board.svg")],
        lede="Why did it make sense to them at the time?",
        intro=("After an incident, the question “who caused this?” stops learning: people get defensive and hide what really "
               "happened. A <b>blameless</b> review asks instead how the system made the incident possible. It rebuilds the "
               "<b>timeline</b> with what people knew at each point, looks for several <b>contributing factors</b> rather than "
               "one root cause, notes what helped and where you got lucky, and ends with actions to prevent, detect or recover "
               "sooner. The approach is widely used in software reliability engineering, including Google's SRE practice."),
        glance=[("Duration", "60–90 min"), ("Group", "Everyone involved,<br>plus a neutral facilitator"),
                ("Use when", "Within a week of any<br>significant incident"), ("Output", "Shared learning<br>&amp; actions")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Collect facts: logs, alerts, chat messages, the timeline from the incident channel",
                "Choose a facilitator who wasn't directly involved",
                "Invite everyone who responded, and anyone affected who can add context",
                "Remind people in the invitation that the review is blameless"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–5", "2 · Ground Rules", "Read the rules aloud. Make it clear that no one is being judged."),
                ("5–15", "1 · Summary", "Agree the facts: what happened, impact, how it was detected, duration and severity."),
                ("15–45", "3 · Timeline", "Rebuild events in order. For each, ask what people knew then and why their action made sense."),
                ("45–65", "4 · Contributing Factors", "Add stickies under each category. Look for several factors, not one cause."),
                ("65–75", "5 · Helped · 6 · Lucky", "What reduced the impact? Where did luck, not design, save you?"),
                ("75–90", "7 · Actions", "Agree a few actions to prevent, detect sooner or recover faster, each with an owner.")],
        sections_title="Making each part strong",
        sections_intro="Quality checks for the review.",
        sections=[("2 · Ground Rules", PURPLE, ["Read aloud", "Facilitator steps in if blame appears"]),
                  ("3 · Timeline", BLUE, ["What people knew then", "Not hindsight"]),
                  ("4 · Contributing Factors", ORANGE, ["Several categories", "Systems, not individuals"]),
                  ("5 · What Helped", EMERALD, ["Things to keep and strengthen"]),
                  ("6 · Where We Got Lucky", AMBER, ["Hidden risks", "Often the most useful insight"]),
                  ("7 · Follow-up Actions", FOREST, ["Few and specific", "Owned and dated"])],
        tips=[("Ask how, not who", "“How did the change reach production?” invites learning. “Who approved it?” invites blame."),
              ("Avoid hindsight", "It's obvious now. Ask what people could see at the time."),
              ("Several factors", "Incidents usually need several things to go wrong at once. Look for them all."),
              ("Count the luck", "Near misses and lucky breaks show risks that will strike again."),
              ("Fewer, better actions", "Three meaningful actions that happen beat ten that don't."),
              ("Share widely", "Publish the review so other teams learn too.")],
        pitfalls=("naming someone as the cause; stopping at “human error”; one root cause for a complex incident; too many "
                  "actions; actions with no owner; reviews only for big incidents, not near misses."),
        after=[("Within a day", "Write up the review and share it openly."),
               ("This iteration", "Plan the actions into the backlog."),
               ("Next month", "Check the actions were done, and whether they helped."),
               ("Over time", "Look across reviews for repeating factors, and bring them to the Root Cause board.")],
        toolkit=("Incident reviews connect to the improvement tools: take repeating factors to "
                 "<a href=\"facilitator-guide-root-cause.html\">Root Cause Analysis</a>, track recovery time in "
                 "<a href=\"facilitator-guide-delivery-metrics.html\">Delivery Metrics</a>, and use the "
                 "<a href=\"facilitator-guide-psych-safety.html\">Psychological Safety Check</a> if people are reluctant to speak openly."),
        foot="“What would make the next incident less likely, or easier to recover from?”",
    ),

    # -------------------------------------------------------------- RACI & decision log
    dict(
        slug="raci-decision-log",
        title="RACI & Decision Log Guide",
        subtitle="How to agree who is responsible and accountable for each piece of work, and keep a clear record of decisions.",
        tag="Facilitator Run-Sheet · Run a Project · RACI · Decision Log",
        boards=[("Open board", "raci-decision-log-board.html"), ("SVG", "raci-decision-log-board.svg")],
        lede="Who is accountable for this, just one person?",
        intro=("Confusion about roles slows projects down: work falls between people, or several people think they decide. "
               "A <b>RACI</b> matrix lists the work, deliverables or decisions, and for each role marks who is "
               "<b>Responsible</b> (does it), <b>Accountable</b> (owns the outcome, exactly one person), <b>Consulted</b> "
               "(gives input) and <b>Informed</b> (kept up to date). The <b>decision log</b> records key decisions, the "
               "options considered and why, so the same debates don't restart every month. Use it alongside the "
               "Delegation Board, which covers how much a team decides."),
        glance=[("Duration", "45–60 min"), ("Group", "PM, sponsor,<br>key role holders"),
                ("Use when", "A project starts, or<br>roles feel unclear"), ("Output", "An agreed matrix<br>&amp; a decision log")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "List the main work items, deliverables and decisions in advance",
                "List the roles (not names, where possible): sponsor, product owner, team lead, architect and so on",
                "Invite the people in those roles, so they agree to what's assigned"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "Set up", "Write the roles across the top and the work items down the side."),
                ("10–35", "1 · Fill in", "For each row, agree the A first, then the Rs, then the Cs and Is."),
                ("35–45", "2 · Check", "Run the five checks. Fix rows with no A, two As, or too many Cs."),
                ("45–55", "3 · Decision log", "Record any decisions already made, with the options and the reasons."),
                ("55–60", "Close", "Agree where the matrix and log live, and who keeps them current.")],
        sections_title="Making it work",
        sections_intro="Quality checks for the matrix and the log.",
        sections=[("Responsible", BLUE, ["Does the work", "Can be several people"]),
                  ("Accountable", RED, ["Owns the outcome", "Exactly one person"]),
                  ("Consulted", AMBER, ["Gives input before", "Keep the list short"]),
                  ("Informed", SLATE, ["Told after", "No input expected"]),
                  ("Decision Log", PURPLE, ["Options and reasons", "A revisit trigger"])],
        tips=[("One A, always", "Shared accountability means no accountability. Pick one person."),
              ("Watch the Cs", "Every consulted person adds delay. Make some of them Informed instead."),
              ("Roles, not names", "Use roles so the matrix survives people changing."),
              ("Agree, don't assign", "People named on the matrix should agree to it, or it won't hold."),
              ("Log the why", "Recording why a decision was made is more useful than the decision itself."),
              ("Set revisit triggers", "Say what would make you revisit a decision, such as new data or a budget change.")],
        pitfalls=("two As on a row; everyone Consulted on everything; a matrix nobody agreed to; using RACI to avoid "
                  "conversations; a decision log with no reasons; never updating either."),
        after=[("Straight away", "Share the matrix with everyone named and store it with the project."),
               ("Each decision", "Add it to the log within a day, with the options and the reasons."),
               ("When people change", "Review the matrix with new role holders."),
               ("At project close", "Use the decision log in the lessons-learned session.")],
        toolkit=PROJECT_TOOLKIT,
        foot="“Why did we decide that, and what would make us revisit it?”",
    ),

    # -------------------------------------------------------------- persona & journey map
    dict(
        slug="persona-journey",
        title="Persona & Journey Map Guide",
        subtitle="How to describe a real type of user and map their journey to find the moments that matter most.",
        tag="Facilitator Run-Sheet · Envision & Plan · Personas · Customer Journey Mapping",
        boards=[("Open board", "persona-journey-board.html"), ("SVG", "persona-journey-board.svg")],
        lede="What is this person really trying to get done?",
        intro=("A <b>persona</b> is a short, evidence-based description of a type of user: their context, goals and "
               "frustrations. A <b>customer journey map</b> follows that person through a scenario in <b>stages</b>, "
               "showing what they do, think and feel, where it goes wrong, and where you could help. The board also frames the "
               "journey as a <b>job to be done</b> (“When…, I want to…, so I can…”), an idea from Clayton Christensen and others. "
               "Opportunities found here feed the Opportunity Solution Tree."),
        glance=[("Duration", "90–120 min"), ("Group", "PO, designer,<br>team, support staff"),
                ("Use when", "Starting discovery, or<br>users are vague"), ("Output", "A persona, a journey<br>&amp; opportunities")],
        before=["Print the board at A3 or larger, or load the SVG as a digital background",
                "Bring real evidence: interviews, support tickets, analytics, sales notes",
                "Agree which user type and which scenario to map first",
                "Invite people who talk to users: support, sales, customer success",
                "Yellow, blue, pink and green stickies, and markers"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–20", "1 · Persona", "Fill in the persona from evidence. Mark anything that's a guess, to check later."),
                ("20–30", "2 · The Journey", "Agree the scenario, where it starts and ends, and the job to be done."),
                ("30–40", "Stages", "Name 4–6 stages of the journey across the top."),
                ("40–70", "Doing · Thinking", "For each stage, add what they do (yellow) and what they're thinking (blue)."),
                ("70–80", "Feeling", "Draw the emotion line across the stages, high and low."),
                ("80–100", "Pain points · Opportunities", "Add pain points (pink) at the lows, then opportunities (green) to help."),
                ("100–110", "Close", "Vote on the top opportunities to take into the Opportunity Solution Tree.")],
        sections_title="Making each part strong",
        sections_intro="Quality checks for the persona and the journey.",
        sections=[("Persona", PURPLE, ["Based on evidence", "Specific, not average", "Guesses are marked"]),
                  ("Job to Be Done", BLUE, ["A situation, a motivation, an outcome", "Not a feature"]),
                  ("Doing & Thinking", AMBER, ["In the user's words", "Every stage covered"]),
                  ("Feeling", PURPLE, ["Highs and lows shown", "Lows explained"]),
                  ("Pain points & Opportunities", FOREST, ["Opportunities match pain points", "Ranked"])],
        tips=[("Evidence, not imagination", "A persona invented in the room reflects the team's assumptions. Ground it in real data."),
              ("One persona per map", "Different users have different journeys. Map them separately."),
              ("Include before and after", "Journeys often start before people reach your product, and end after."),
              ("The lows matter most", "The deepest dips in the feeling line are usually the biggest opportunities."),
              ("Invite the front line", "Support and sales staff hear pain points every day."),
              ("Validate it", "Show the map to a few real users and ask what's missing.")],
        pitfalls=("personas based on demographics, not needs; one map for every user; mapping your internal process instead "
                  "of the user's journey; no evidence; filing the map away instead of using it."),
        after=[("Straight away", "Take the top opportunities into the Opportunity Solution Tree."),
               ("This week", "Check guesses on the persona with a few user interviews."),
               ("Next", "Use the journey to choose the backbone of a Story Map."),
               ("Every few months", "Update the persona and map as you learn.")],
        toolkit=LIFECYCLE_TOOLKIT,
        foot="“Where in the journey do we lose them, and why?”",
    ),

    # -------------------------------------------------------------- impact map
    dict(
        slug="impact-map",
        title="Impact Map Guide",
        subtitle="How to connect a business goal to the people whose behaviour you need to change, and what to build.",
        tag="Facilitator Run-Sheet · Envision & Plan · Inspired by Gojko Adzic's Impact Mapping",
        boards=[("Open board", "impact-map-board.html"), ("SVG", "impact-map-board.svg")],
        lede="Whose behaviour has to change for us to reach this goal?",
        intro=("Impact mapping, introduced by Gojko Adzic, builds a simple tree from a <b>goal</b> (why) to the <b>actors</b> "
               "who can help or hinder it (who), the <b>impacts</b> on their behaviour you need (how), and the "
               "<b>deliverables</b> that might cause those impacts (what). Every feature then traces back to the goal, which "
               "makes it easy to say no to work that doesn't, and to test the riskiest assumption first."),
        glance=[("Duration", "60–90 min"), ("Group", "PO, sponsor,<br>team reps"),
                ("Use when", "A goal needs a plan,<br>or the roadmap is a wish list"), ("Output", "A traceable map<br>&amp; a first step")],
        before=["Print the board at A3 or larger, or load the SVG as a digital background",
                "Agree one measurable business goal, ideally from the OKRs or Product Vision Board",
                "Bring what you know about users, customers and other actors",
                "Invite people who understand the business and the users"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–10", "Goal", "Write the goal and its measure. Check it's an outcome, not a feature."),
                ("10–25", "Actors", "Who can help us reach the goal, or get in the way? Include users, partners, internal teams."),
                ("25–45", "Impacts", "For each actor, how must their behaviour change? Write it as a behaviour, not a feature."),
                ("45–65", "Deliverables", "What could we build or do to cause each impact? Several options per impact are fine."),
                ("65–80", "2 · Riskiest Assumption", "Which impact are we least sure will happen? How will we test it?"),
                ("80–90", "3 · First Step", "Pick the deliverable to try first, and how you'll know the impact happened.")],
        sections_title="Making each level strong",
        sections_intro="Quality checks for each level of the map.",
        sections=[("Goal", EMERALD, ["Measurable", "An outcome, not output"]),
                  ("Actors", BLUE, ["Specific groups", "Include those who could block it"]),
                  ("Impacts", ORANGE, ["Behaviour changes", "Observable"]),
                  ("Deliverables", AMBER, ["Options, not commitments", "Each links to an impact"]),
                  ("Riskiest Assumption", RED, ["Tested first", "Cheaply"])],
        tips=[("Impacts are behaviour", "“Customers reorder weekly” is an impact. “Add a reorder button” is a deliverable."),
              ("Include blockers", "Actors who could get in the way are as important as those who help."),
              ("Many options", "Several deliverables per impact give you choices. Pick the cheapest that might work."),
              ("Cut freely", "Deliverables that don't trace to an impact don't belong on the roadmap."),
              ("Test the riskiest link", "If the behaviour change doesn't happen, nothing below it matters."),
              ("Keep it visible", "Revisit the map when the goal or evidence changes.")],
        pitfalls=("a goal that's a feature; impacts written as features; one deliverable per impact; mapping everything "
                  "already planned and calling it done; never testing the riskiest impact."),
        after=[("Straight away", "Share the map and the first deliverable with the team and stakeholders."),
               ("This iteration", "Build or test the first deliverable."),
               ("When results come in", "Did the impact happen? Keep, change or drop that branch."),
               ("Next", "Use the map to choose epics for the Epic Breakdown Canvas.")],
        toolkit=LIFECYCLE_TOOLKIT,
        foot="“If we built only one thing, which impact would it move?”",
    ),

    # -------------------------------------------------------------- estimation
    dict(
        slug="estimation",
        title="Estimation Guide",
        subtitle="How to size work quickly and fairly with planning poker, T-shirt sizing or affinity estimation, or skip it.",
        tag="Facilitator Run-Sheet · Iterate · Planning Poker · T-Shirt Sizing · Affinity Estimation",
        boards=[("Open board", "estimation-board.html"), ("SVG", "estimation-board.svg")],
        lede="Is this bigger or smaller than the last thing we finished?",
        intro=("Estimates help teams plan and spot items that are too big, but they cost time and are often misused. The board "
               "offers three ways to estimate <b>relatively</b>, comparing items with each other rather than guessing hours. "
               "<b>Planning poker</b> (described by James Grenning, popularised by Mike Cohn) suits a handful of items. "
               "<b>T-shirt sizing</b> roughly sorts many items. <b>Affinity estimation</b> sizes a whole backlog in an hour. "
               "It also suggests the alternative many teams find works as well: split items small and <b>count</b> them."),
        glance=[("Duration", "15–60 min"), ("Group", "The people who<br>will do the work"),
                ("Use when", "Planning, refinement,<br>or release forecasting"), ("Output", "Relative sizes<br>or a count")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "Bring the items to estimate, ideally refined with Example Mapping first",
                "Agree 3–5 reference items everyone remembers, for the Reference Items table",
                "Planning poker cards, or a phone app, if you use poker"],
        agenda_heads=["Use", "Technique", "How to run it"],
        agenda=[("A few items", "1 · Planning Poker", "Read the item, everyone picks a card privately, reveal together. The highest and lowest explain, then re-vote. Two rounds at most."),
                ("Many items", "2 · T-Shirt Sizing", "Agree what a reference “M” is, then place each item in XS to XL. Discuss only items people disagree on."),
                ("A whole backlog", "3 · Affinity Estimation", "Silently place items left to right by size. Anyone can move anything. Discuss items that keep moving, then draw boundaries."),
                ("Any", "4 · Reference Items", "Keep shared examples for each size, and compare new items against them."),
                ("Consider", "5 · Don't Estimate", "If items are split to finish within your SLE, count them and forecast from throughput instead.")],
        sections_title="Choosing a technique",
        sections_intro="Pick the lightest technique that gives you what you need.",
        sections=[("Planning Poker", PURPLE, ["A few items in detail", "Surfaces different assumptions"]),
                  ("T-Shirt Sizing", BLUE, ["Rough sizes for roadmaps", "Quick for many items"]),
                  ("Affinity Estimation", ORANGE, ["A whole backlog", "Mostly silent, very fast"]),
                  ("Reference Items", EMERALD, ["Keep sizes consistent", "Update occasionally"]),
                  ("Don't Estimate", SLATE, ["Right-size and count", "Forecast from throughput"])],
        tips=[("The conversation is the value", "When estimates differ, the discussion reveals hidden work or risk."),
              ("Relative beats absolute", "People compare sizes far better than they guess hours."),
              ("Don't average", "If votes differ widely, talk and re-vote. Averaging hides the disagreement."),
              ("Split the big ones", "Anything at 13 or above is usually too big. Split it before estimating again."),
              ("Estimates aren't promises", "Use them to forecast, never to judge people or compare teams."),
              ("Try counting", "Many teams find counting small items forecasts as accurately as points, with less effort.")],
        pitfalls=("estimating in hours; managers estimating for the team; averaging votes; treating points as a performance "
                  "measure; comparing velocity across teams; spending longer estimating than the work would take."),
        after=[("Straight away", "Record sizes in your backlog tool and note any items to split."),
               ("Planning", "Use sizes or counts with recent throughput to plan capacity."),
               ("Each retro", "Compare forecasts with what happened, and adjust."),
               ("Every few months", "Try a few iterations of counting items, and compare the forecast accuracy.")],
        toolkit=LIFECYCLE_TOOLKIT,
        foot="“Do we need a number, or do we just need to know it's small?”",
    ),

    # -------------------------------------------------------------- facilitation techniques
    dict(
        slug="facilitation-techniques",
        title="Facilitation Techniques Guide",
        subtitle="How to use the poster's twelve techniques to design sessions where every voice is heard and decisions stick.",
        tag="Facilitator Run-Sheet · Facilitate · Include Every Voice · Remote & Hybrid",
        boards=[("Open poster", "facilitation-techniques-poster.html"), ("SVG", "facilitation-techniques-poster.svg")],
        lede="Who hasn't spoken yet, and how could we make it easy for them?",
        intro=("Most meetings follow the same shape: a few people talk, everyone else listens, and decisions are fuzzy. Small "
               "changes in structure fix this. The poster collects <b>twelve simple techniques</b>, from check-ins and silent "
               "writing to dot voting and agreement scales, each with when to use it, how to run it, and a tip. The bottom "
               "strip covers <b>remote and hybrid</b> sessions. For a larger library of structures, see "
               "<a href=\"https://www.liberatingstructures.com\">Liberating Structures</a>, a separately licensed collection."),
        glance=[("Duration", "Any session"), ("Group", "Anyone who<br>runs meetings"),
                ("Use when", "Designing a workshop,<br>retro or meeting"), ("Output", "A better-designed<br>session")],
        before=["Print the poster at A3 and keep it where you plan sessions",
                "For each session, write the purpose and the decision or output you need",
                "Choose techniques for the opening, the middle and the close",
                "For remote sessions, set up the shared board and test it beforehand"],
        agenda_heads=["Phase", "Techniques", "Why"],
        agenda=[("Open", "1 Check-in", "Everyone speaks once early, which makes speaking later easier."),
                ("Generate ideas", "2 Silent Writing · 3 Think · Pair · Share · 4 Round-Robin", "Diverge: get every view out before discussion narrows it."),
                ("Make sense", "5 Affinity Clustering · 10 Parking Lot · 11 Fishbowl", "Group and explore ideas without losing any."),
                ("Decide", "6 Dot Voting · 7 Fist of Five · 8 Agreement Scale", "Converge: prioritise and test real support."),
                ("Throughout", "9 Timeboxing", "Keep energy up and end on time."),
                ("Close", "12 Check-out", "Capture takeaways and learn how the session went.")],
        sections_title="Designing a session",
        sections_intro="A simple shape that works for most meetings and workshops.",
        sections=[("Open", SLATE, ["Purpose and outcome stated", "Everyone speaks once"]),
                  ("Diverge", PURPLE, ["Silent writing first", "Quantity before quality"]),
                  ("Make sense", EMERALD, ["Cluster, then name", "Park what's off-topic"]),
                  ("Converge", ORANGE, ["Vote together", "Test support, don't assume it"]),
                  ("Close", BLUE, ["Decisions and owners read back", "One takeaway each"])],
        tips=[("Structure frees people", "A clear structure makes it safer for quieter people to contribute."),
              ("Diverge before converging", "Mixing idea generation and decision-making leads to early, weak decisions."),
              ("Write before talking", "Silent writing stops the first speaker setting the agenda."),
              ("Show the time", "A visible timer keeps everyone, including the facilitator, honest."),
              ("Test agreement", "Silence isn't consent. Use a fist of five or an agreement scale."),
              ("Equal in hybrid", "If one person is remote, everyone joins from their own device.")],
        pitfalls=("no clear purpose; discussing before writing; voting with hands raised one at a time; running over time; "
                  "remote participants as spectators; ending without decisions and owners."),
        after=[("After each session", "Use the check-out scores to adjust the next design."),
               ("Over time", "Build a short list of favourite techniques for each kind of meeting."),
               ("Share", "Teach one technique to others on your team each month."),
               ("Go further", "Explore other facilitation libraries and books once these feel natural.")],
        toolkit=("The techniques appear throughout the toolkit: silent writing and dot voting in the retros and Lean Coffee, fist "
                 "of five in Sprint and Cross-Team Planning, and timeboxing in Example Mapping. The "
                 "<a href=\"scrum-master-agile-coach-cheat-sheet.html\">Scrum Master &amp; Agile Coach Cheat Sheet</a> has more "
                 "facilitation moves and decision methods."),
        foot="“Are we still exploring, or is it time to decide?”",
    ),

    # -------------------------------------------------------------- ADR
    dict(
        slug="adr",
        title="Architecture Decision Record Guide",
        subtitle="How to record important technical decisions so future team members understand what was decided, and why.",
        tag="Facilitator Run-Sheet · Manage Flow · Inspired by Michael Nygard's ADR Format",
        boards=[("Open board", "adr-board.html"), ("SVG", "adr-board.svg")],
        lede="Will someone joining next year understand why we did this?",
        intro=("Teams make important technical decisions all the time, then forget why. An <b>architecture decision record</b> "
               "(ADR), a format described by Michael Nygard, is a short document for one decision: its <b>context</b>, the "
               "<b>drivers</b> that matter, the <b>options</b> considered, the <b>decision</b> itself, and its "
               "<b>consequences</b>. Kept together, usually alongside the code, ADRs become a history of the system's "
               "design that new people can read in an afternoon."),
        glance=[("Duration", "30–60 min<br>per decision"), ("Group", "Tech lead, engineers,<br>architect"),
                ("Use when", "A decision is costly<br>to reverse"), ("Output", "One short,<br>numbered record")],
        before=["Print the board at A3, or copy the structure into a Markdown file in your repository",
                "Agree which decisions deserve an ADR: hard to reverse, affecting several teams, or often questioned",
                "Gather the facts: requirements, constraints, any prototypes or measurements",
                "Invite the people who will live with the decision"],
        agenda_heads=["Time", "Section", "Facilitator notes"],
        agenda=[("0–5", "1 · Title & Status", "Give it a number and a short, present-tense title. Mark it Proposed."),
                ("5–15", "2 · Context", "Describe the problem and the forces at play, without arguing for a solution yet."),
                ("15–20", "3 · Decision Drivers", "List what matters most, such as cost, performance, skills or reversibility."),
                ("20–40", "4 · Options", "Compare at least two options, including doing nothing, against the drivers."),
                ("40–50", "5 · Decision", "Write the decision: “We will…”. Mark it Accepted once agreed."),
                ("50–60", "6 · Consequences", "Record what becomes easier and what becomes harder.")],
        sections_title="Making each part strong",
        sections_intro="Quality checks for an ADR.",
        sections=[("Title & Status", SLATE, ["Short and specific", "Status kept up to date"]),
                  ("Context", BLUE, ["Facts and forces", "Readable by a newcomer"]),
                  ("Decision Drivers", PURPLE, ["Ranked", "Agreed before choosing"]),
                  ("Options Considered", ORANGE, ["At least two", "Honest pros and cons"]),
                  ("Decision & Consequences", FOREST, ["Clear “We will…”", "Trade-offs written down"])],
        tips=[("Keep it short", "One or two pages. If it's longer, it's probably several decisions."),
              ("Write it at the time", "Record decisions when they're made, while the reasons are fresh."),
              ("Never edit, supersede", "When a decision changes, write a new ADR and mark the old one Superseded."),
              ("Store it with the code", "A folder of numbered Markdown files in the repository is easy to find and review."),
              ("Include the rejected", "Options you rejected, and why, save the next team from repeating the analysis."),
              ("Review like code", "Propose ADRs in a pull request so others can comment.")],
        pitfalls=("writing ADRs for trivial choices; skipping the options; editing old records instead of superseding them; "
                  "storing them where nobody looks; writing them months after the decision."),
        after=[("Straight away", "Save the ADR with a number in your repository or wiki."),
               ("When it changes", "Write a new ADR and mark the old one Superseded."),
               ("Onboarding", "Point new team members to the ADR folder."),
               ("Quarterly", "Review open Proposed ADRs and decide them.")],
        toolkit=FLOW_TOOLKIT,
        foot="“What would make us revisit this decision?”",
    ),
]
GUIDES += WAVE3_GUIDES

GUIDES.append(dict(
    slug="team-launch",
    title="Team Launch Guide",
    subtitle="How to get a new team or initiative ready to deliver in one or two weeks, without endless up-front planning.",
    tag="Facilitator Run-Sheet · Set Up the Team · Sprint Zero · Iteration 0",
    boards=[("Open board", "team-launch-board.html"), ("SVG", "team-launch-board.svg")],
    lede="What's the least we need to agree before we can start delivering?",
    intro=("New teams and initiatives need a short period to get going: agree the purpose and vision, form the team, build a "
           "first backlog, and set up the board, tools and environments. It's often called <b>Sprint Zero</b> or "
           "<b>Iteration 0</b>; Disciplined Agile calls it inception. The Scrum Guide doesn't include it, because every sprint "
           "should deliver something usable, and the common criticism is that it drifts into weeks of design with nothing "
           "delivered. This board keeps it <b>timeboxed</b> to one or two weeks, uses a <b>checklist</b> that points to the "
           "right tool for each item, insists on a <b>thin first slice</b> of real work, and ends with a clear "
           "<b>ready-to-start</b> check."),
    glance=[("Duration", "1–2 weeks,<br>timeboxed"), ("Group", "The new team,<br>PO and sponsor"),
            ("Use when", "A team forms, or a new<br>initiative starts"), ("Output", "A ready team<br>&amp; a first slice")],
    before=["Print the board at A1 or A3 and put it on the team wall, or load the SVG as a digital board",
            "Agree the timebox and the launch owner with the sponsor",
            "Book the key sessions in the first week: kickoff, charter, vision, story map",
            "Arrange access to tools and environments before day one, if you can",
            "Pick only the checklist items this team needs; strike out the rest"],
    agenda_heads=["When", "Focus", "Sessions and tools"],
    agenda=[("Day 1", "Why and who", "Project Kickoff (half day). Start the Team Charter. Set the launch goal and timebox on the board."),
            ("Days 2–3", "What and for whom", "Product Vision Board, Persona & Journey Map, and an Impact Map or OKRs for the first outcome."),
            ("Days 3–5", "The backlog", "User Story Map for the first release slice; Epic Breakdown for the main epic; split the top items."),
            ("Week 1, throughout", "Environment", "Repository, pipeline, board and access. Pair on the walking skeleton as soon as the tools work."),
            ("Week 2, early", "Ways of working", "Kanban Board Design, Definition of Done, Skills Matrix, AI Working Agreement, risks (Pre-mortem)."),
            ("Week 2, late", "Ready to start", "Example Mapping on the top items, a first forecast, the exit check, then plan the first real iteration.")],
    sections_title="Making the launch work",
    sections_intro="What good looks like for each part of the board.",
    sections=[("1 · Launch Goal", PURPLE, ["A date to start delivering", "What “ready” means, in one line"]),
              ("2 · Timebox", SLATE, ["One or two weeks", "A daily check-in on progress"]),
              ("3 · Launch Checklist", BLUE, ["Only the items you need", "Each has an owner", "Just enough, not perfect"]),
              ("4 · Thin First Slice", EMERALD, ["Something real by the end", "End to end, however small"]),
              ("5 · Environment & Tools", SKY, ["Everyone can work on day one", "Pipeline to a test environment"]),
              ("6 · Ready to Start?", RED, ["Every exit item ticked", "If not, decide: extend briefly or start anyway"])],
    tips=[("Timebox it hard", "Set the end date first. Unfinished items carry into the first iteration, as backlog items."),
          ("Just enough", "Aim for a vision and backlog good enough to start, not complete. They'll change once you learn."),
          ("Deliver anyway", "A walking skeleton or one usable story proves the tools, pipeline and team work together."),
          ("Strike out what you don't need", "A small internal team may not need a RACI or a stakeholder map. Skip them."),
          ("Start the habits early", "Hold daily check-ins and a short retro at the end of the launch, so the rhythms start now."),
          ("Don't make it a phase", "If the launch is turning into months of design, stop and start delivering.")],
    pitfalls=("no timebox; trying to complete every checklist item; detailed design of the whole solution; no working "
              "environment until week three; nothing delivered; repeating a “sprint zero” before every release."),
    after=[("End of the launch", "Run a short retro on the launch itself, and plan the first iteration."),
           ("First iteration", "Carry over unfinished launch items as normal backlog items."),
           ("After a month", "Revisit the Team Charter and Definition of Done with what you've learned."),
           ("Next time", "Keep the checklist the team found useful for future launches.")],
    toolkit=("The launch board is a map of the toolkit's set-up tools: Project Kickoff, Team Charter, Product Vision Board, "
             "Persona &amp; Journey Map, User Story Map, Epic Breakdown, Kanban Board Design and the others named on each "
             "checklist item. Once the team is ready, it moves on to <a href=\"facilitator-guide-sprint-planning.html\">Sprint "
             "Planning</a> or its first replenishment, and the rest of the lifecycle."),
    foot="“What could we deliver this week, however small?”",
))


EVENTS_TOOLKIT = ("The event tools follow a team's rhythm: <a href=\"facilitator-guide-sprint-planning.html\">Sprint Planning</a> "
                  "or replenishment, the <a href=\"facilitator-guide-daily-sync.html\">Daily Sync</a>, "
                  "<a href=\"facilitator-guide-backlog-refinement.html\">Backlog Refinement</a>, "
                  "<a href=\"facilitator-guide-sprint-review.html\">Sprint Review</a> and a retrospective from the Retro Kit. "
                  "Teams working in continuous flow use the <a href=\"facilitator-guide-kanban-cadences.html\">Kanban Cadences</a>. "
                  "The <a href=\"facilitator-guide-events-cadences.html\">Events &amp; Cadences</a> poster shows them all, "
                  "including multi-team and leadership events.")

GUIDES += [
    # -------------------------------------------------------------- daily sync
    dict(
        slug="daily-sync",
        title="Daily Sync Guide",
        subtitle="How to run a short daily check that moves the team toward its goal, instead of a round of status updates.",
        tag="Facilitator Run-Sheet · Run Events · Daily Scrum · Stand-up · Kanban Meeting",
        boards=[("Open board", "daily-sync-board.html"), ("SVG", "daily-sync-board.svg")],
        lede="What will we finish today?",
        intro=("Most teams meet briefly every day, whether they call it the <b>Daily Scrum</b>, a <b>stand-up</b> or the "
               "<b>Kanban meeting</b>. Its purpose is to inspect progress toward the goal and adapt the plan for the next day. "
               "It often turns into a round of status reports to a manager. The board fixes that by putting the "
               "<b>goal</b> at the top, <b>walking the board right to left</b> so finishing comes before starting, "
               "focusing on <b>blocked and ageing</b> work, and moving detailed discussion to a <b>parking lot</b>. A weekly "
               "health check keeps the habit honest."),
        glance=[("Duration", "15 min, daily"), ("Group", "The team; others<br>may listen"),
                ("Use when", "Every working day"), ("Output", "Today's plan<br>&amp; owned blockers")],
        before=["Hold it at the same time and place every day, in front of the team's board",
                "Put the current goal where everyone can see it",
                "Agree who facilitates; rotating the role works well",
                "For remote teams, share the board on screen and keep cameras optional"],
        agenda_heads=["Minutes", "Step", "Facilitator notes"],
        agenda=[("0–1", "1 · Goal", "Read the goal and the days left. Ask: are we on track?"),
                ("1–10", "3 · Walk the board", "Start at the right: what's nearly done and what's needed to finish it? Then blocked and old items. Then what to finish today."),
                ("10–13", "5 · Blockers & swarms", "Give each blocker an owner. Decide whether to swarm on anything."),
                ("13–15", "Plan & park", "Confirm what we'll finish today. Note parking-lot topics and who stays for them."),
                ("Weekly", "7 · Health check", "Tick the health check together and agree one thing to try if a check fails.")],
        sections_title="Making it work",
        sections_intro="What good looks like for each part of the board.",
        sections=[("1 · Our Goal", PURPLE, ["Visible every day", "Discussion links back to it"]),
                  ("3 · Walk the Board", BLUE, ["Right to left", "Oldest and blocked first", "Finish before starting"]),
                  ("4 · Questions to Ask", EMERALD, ["About the work, not people", "The classic three are optional"]),
                  ("5 · Blockers & Swarms", RED, ["Every blocker has an owner", "Swarm when the goal is at risk"]),
                  ("6 · Parking Lot", AMBER, ["Details after the sync", "Only the people needed stay"]),
                  ("7 · Health Check", FOREST, ["Weekly", "One change when a check fails"])],
        tips=[("Talk about work items, not people", "Walking the board item by item avoids a round of personal status reports."),
              ("Right to left", "Finishing work delivers value; starting it only adds to WIP."),
              ("Keep it to 15 minutes", "If it overruns, the parking lot isn't being used. Move discussions after the sync."),
              ("It's the team's meeting", "Managers and stakeholders can listen, but the team runs it and decides the plan."),
              ("Rotate the facilitator", "Taking turns stops it becoming one person's update meeting."),
              ("Look for the oldest item", "Work that's been open longest is usually the biggest risk to the goal.")],
        pitfalls=("a status report to a manager; no reference to the goal; walking people instead of work; problem-solving in "
                  "the meeting; overrunning; starting new work while items sit blocked; skipping it when “busy”."),
        after=[("Straight away", "Parking-lot groups meet; blocker owners act."),
               ("During the day", "Update the board as work moves, not just before the next sync."),
               ("Weekly", "Run the health check and adjust the format."),
               ("At the retro", "Ask whether the sync is helping the team reach its goal.")],
        toolkit=EVENTS_TOOLKIT,
        foot="“Who needs help, and who can give it?”",
    ),

    # -------------------------------------------------------------- backlog refinement
    dict(
        slug="backlog-refinement",
        title="Backlog Refinement Guide",
        subtitle="How to run a regular refinement session that gets the next items ordered, understood, split, sized and ready.",
        tag="Facilitator Run-Sheet · Run Events · Backlog Refinement",
        boards=[("Open board", "backlog-refinement-board.html"), ("SVG", "backlog-refinement-board.svg")],
        lede="Which items do we need ready for the next iteration?",
        intro=("Refinement is the ongoing work of getting the next few backlog items ready: <b>ordered</b> by value, "
               "<b>understood</b> by the team, <b>split</b> small enough to finish in a few days, explored through <b>examples</b>, "
               "and roughly <b>sized</b>. Scrum describes it as an ongoing activity rather than a formal event. Many teams "
               "hold a regular session, often taking around 10% of their capacity. The board walks each item through six "
               "steps and points to the toolkit tool for each one, so the session stays focused and finishes with ready items."),
        glance=[("Duration", "45–90 min,<br>weekly"), ("Group", "PO, developers,<br>testers, experts"),
                ("Use when", "Every week, or before<br>planning"), ("Output", "Ready items for the<br>next 1–2 iterations")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "The PO brings the top items in order, with any context or data",
                "Have the Story Splitting poster and Example Mapping board to hand",
                "Agree the team's Definition of Ready, if you have one",
                "Invite experts only for the items that need them"],
        agenda_heads=["Minutes", "Step", "Facilitator notes"],
        agenda=[("0–5", "1 · Session goal", "Agree which items to refine and the iteration they need to be ready for."),
                ("5–15", "Order", "Confirm the order with the PO. Drop or defer anything no longer valuable."),
                ("15–60", "Understand · Split · Examples", "For each item: who it's for and why, split it if it's too big, then map rules and examples."),
                ("60–75", "Size", "Size the items quickly, or check they're small enough to count."),
                ("75–85", "Ready?", "Check each item against the Definition of Ready. Record open questions with owners."),
                ("85–90", "Close", "Read back what's ready and what isn't, and when the next session is.")],
        sections_title="Making each step strong",
        sections_intro="Quality checks for each step of the flow.",
        sections=[("Order", BLUE, ["Most valuable first", "Drop what's no longer needed"]),
                  ("Understand", PURPLE, ["Who it's for, and why", "What done looks like"]),
                  ("Split", ORANGE, ["Finishes in a few days", "Vertical slices"]),
                  ("Examples", FOREST, ["Rules and examples", "Questions have owners"]),
                  ("Size", AMBER, ["Relative and quick", "Or just count small items"]),
                  ("Ready?", RED, ["Checked against the DoR", "A guide, not a gate"])],
        tips=[("Just in time", "Refine one or two iterations ahead. Refining further out wastes effort when plans change."),
              ("Whole team", "Developers and testers find hidden work and risks the PO can't see alone."),
              ("Timebox each item", "If an item takes more than 15–20 minutes, it probably needs splitting or a spike."),
              ("Questions are progress", "An open question found now is cheaper than one found mid-iteration."),
              ("Don't design it all", "Agree enough to start. The team will work out details while building."),
              ("Little and often", "A short weekly session beats one long, tiring one before planning.")],
        pitfalls=("refining too far ahead; the PO presenting while the team listens; designing solutions in detail; no "
                  "splitting; endless debate on one item; treating the Definition of Ready as a gate."),
        after=[("Straight away", "Update the backlog: splits, examples, sizes and open questions."),
               ("Before planning", "Question owners find the answers."),
               ("At planning", "Ready items go in first."),
               ("At the retro", "Ask whether items arrived in planning ready enough.")],
        toolkit=EVENTS_TOOLKIT,
        foot="“What don't we know yet that would stop us starting?”",
    ),

    # -------------------------------------------------------------- kanban cadences
    dict(
        slug="kanban-cadences",
        title="Kanban Cadences Guide",
        subtitle="How to set up a rhythm of short, focused reviews that keep work flowing and services improving.",
        tag="Facilitator Run-Sheet · Manage Flow · Inspired by the Kanban Method",
        boards=[("Open board", "kanban-cadences-board.html"), ("SVG", "kanban-cadences-board.svg")],
        lede="Which conversation would most improve our flow if we had it regularly?",
        intro=("Teams working in continuous flow don't need iterations, but they still need feedback loops. The Kanban Method "
               "(David J. Anderson) describes a set of <b>cadences</b>: a daily Kanban meeting, <b>replenishment</b> to choose what "
               "to pull in next, delivery planning, a <b>service delivery review</b> of flow and service levels, and wider "
               "operations, risk and strategy reviews. You don't need them all. Start with the daily meeting, replenishment and "
               "a service delivery review, then add others as the system grows."),
        glance=[("Duration", "60 min to design<br>the cadence"), ("Group", "The team, PO or<br>service manager"),
                ("Use when", "Moving to flow, or<br>meetings feel random"), ("Output", "An agreed rhythm<br>of reviews")],
        before=["Print the board at A3, or load the SVG as a digital background",
                "List the meetings the team already holds, and how often",
                "Bring flow data: lead time, throughput, items past their SLE, blocked time",
                "Have your Kanban board and its WIP limits to hand"],
        agenda_heads=["Minutes", "Step", "Facilitator notes"],
        agenda=[("0–10", "Today", "List current meetings. Which ones help flow, and which could go?"),
                ("10–30", "1 · Choose cadences", "Tick the cadences you'll run. Fill in when, who, and inputs and outputs for each."),
                ("30–45", "2 · Replenishment", "Agree how you'll calculate free capacity and choose items to pull in."),
                ("45–55", "3 · Service delivery review", "Agree the measures, their expectations or SLE, and who attends."),
                ("55–60", "Close", "Put the cadences in the calendar and agree when to review the rhythm itself.")],
        sections_title="The main cadences",
        sections_intro="Start with the first three; add others as you grow.",
        sections=[("Daily Kanban Meeting", BLUE, ["Walk the board right to left", "Blockers and ageing work"]),
                  ("Replenishment", PURPLE, ["Pull to fill free WIP", "Clear selection policy"]),
                  ("Service Delivery Review", ORANGE, ["Flow against expectations", "Customers or PO present"]),
                  ("Delivery Planning", EMERALD, ["What's ready to release, and when"]),
                  ("Operations · Risk · Strategy", SLATE, ["Wider, less frequent", "For several services or teams"])],
        tips=[("Start small", "Three cadences done well beat seven done half-heartedly."),
              ("Decouple the cadences", "Replenishment, delivery and review can each run at their own pace, unlike a single iteration."),
              ("Pull, don't push", "Replenish only to fill free WIP. Never overload the system to look busy."),
              ("Bring data", "Service delivery reviews work best with lead time and SLE data, not opinions."),
              ("Invite the customer", "Hearing expectations directly keeps the service focused on what matters."),
              ("Review the rhythm", "Every few months, ask whether each cadence is still worth its time.")],
        pitfalls=("copying every cadence at once; replenishing beyond WIP limits; reviews without data; no customer voice; "
                  "keeping meetings that no longer help."),
        after=[("Straight away", "Book the cadences as recurring calendar events."),
               ("First month", "Hold each at least once, and adjust timing and attendees."),
               ("Every quarter", "Review the rhythm: add, drop or change a cadence."),
               ("Always", "Bring service delivery review findings to the retrospective.")],
        toolkit=EVENTS_TOOLKIT,
        foot="“Are we meeting what our customers expect, and how do we know?”",
    ),

    # -------------------------------------------------------------- events & cadences poster
    dict(
        slug="events-cadences",
        title="Events & Cadences Guide",
        subtitle="How to use the poster to design a simple, purposeful set of events, whatever framework you use.",
        tag="Facilitator Run-Sheet · Run Events · Scrum · Kanban · SAFe · LeSS · Scrum@Scale",
        boards=[("Open poster", "events-cadences-poster.html"), ("SVG", "events-cadences-poster.svg")],
        lede="Does every event we hold have a clear purpose and output?",
        intro=("Frameworks name their events differently, but the needs underneath are the same: plan, sync, refine, review, "
               "reflect, and do the same across teams and for the organisation. The poster lists <b>twelve common events</b> "
               "with what each framework calls them, their <b>purpose</b>, typical <b>cadence and timebox</b>, who comes, the "
               "<b>output</b>, and the tool in this kit that helps. Use it to design a lean set of events for a team or a "
               "group of teams, or to translate between frameworks. Timeboxes are typical; Scrum's are maximums for each "
               "week of a sprint."),
        glance=[("Duration", "45–60 min"), ("Group", "Team, PO, coach,<br>or group leads"),
                ("Use when", "Setting up, or when<br>meetings feel too many"), ("Output", "An agreed set of events<br>&amp; calendar")],
        before=["Print the poster at A3, or share it on screen",
                "List the meetings the team or group holds today, with their length and frequency",
                "Bring the team's working agreements or charter",
                "Invite the people who'd attend the events"],
        agenda_heads=["Minutes", "Step", "Facilitator notes"],
        agenda=[("0–10", "Today", "Map current meetings to the rows on the poster. Which rows are missing? Which meetings don't fit any row?"),
                ("10–25", "Purpose", "For each event you keep, agree its purpose and output in one line."),
                ("25–40", "Cadence", "Set the frequency and timebox. Merge or drop events with no clear output."),
                ("40–50", "Tools", "Pick the toolkit board for each event and who facilitates."),
                ("50–60", "Close", "Book the calendar, and agree when to review the set of events.")],
        sections_title="Reading the poster",
        sections_intro="How the three groups fit together.",
        sections=[("Team events", BLUE, ["Plan, sync, refine, review, reflect", "Weekly to daily rhythm"]),
                  ("Multi-team events", PURPLE, ["The same needs across teams", "Period or quarterly rhythm"]),
                  ("Organisation events", FOREST, ["Funding and outcomes", "Monthly or quarterly"]),
                  ("Also called", SLATE, ["Translate between frameworks", "Pick names your people use"])],
        tips=[("Purpose first", "An event without a clear purpose and output is a candidate to drop."),
              ("Fewer, better", "A lean set of well-run events beats a full calendar."),
              ("Same needs, different names", "Use the “also called” column to stop arguments about terminology."),
              ("Timebox everything", "Shorter, regular events are easier to keep focused than long, rare ones."),
              ("Scale the timebox", "Scrum's timeboxes scale with sprint length; a two-week sprint needs half the time of a four-week one."),
              ("Review the set", "Every quarter, ask which events still earn their time.")],
        pitfalls=("adding every event from every framework; events with no output; long meetings with the wrong people; "
                  "arguing about names instead of purpose; never reviewing the calendar."),
        after=[("Straight away", "Put the agreed events in the calendar with their purpose in the invite."),
               ("First month", "Use the toolkit board for each event."),
               ("At retros", "Ask whether each event is helping."),
               ("Every quarter", "Review the whole set with the poster.")],
        toolkit=EVENTS_TOOLKIT,
        foot="“Which event could we shorten, merge or drop?”",
    ),
]

GUIDES.append(dict(
    slug="anti-pattern-spotter",
    title="Anti-Pattern Spotter Guide",
    subtitle="How to help a team spot the anti-patterns holding it back, choose the ones that matter, and act on them.",
    tag="Facilitator Run-Sheet · Reflect & Improve · Common Anti-Patterns",
    boards=[("Open board", "anti-pattern-spotter-board.html"), ("SVG", "anti-pattern-spotter-board.svg")],
    lede="If we fixed only one, which would make the biggest difference?",
    intro=("Every team slips into habits that quietly slow it down: daily syncs that turn into status reports, stories that "
           "are really tasks, too much work in progress. Naming them is the first step to fixing them. The board lists "
           "<b>28 common anti-patterns</b> in seven areas, from events and the backlog to leadership and metrics. People "
           "<b>tick</b> the ones they recognise, <b>vote</b> on those that hurt most, then choose a <b>tool</b> to tackle the "
           "top three. Each symptom has a fuller entry, with why it hurts and what to try, in the "
           "<a href=\"anti-patterns.html\">Anti-Pattern Catalogue</a>."),
    glance=[("Duration", "45–60 min"), ("Group", "One team, or a<br>group of teams"),
            ("Use when", "Something feels off,<br>or every quarter"), ("Output", "Top three anti-patterns<br>&amp; actions")],
    before=["Print the board at A3 or larger, or load the SVG as a digital background",
            "Open the Anti-Pattern Catalogue so you can read out fuller descriptions",
            "Dot stickers (three per person) and markers",
            "Agree that this is about the system, not about blaming anyone",
            "For leaders and teams together, consider anonymous ticking first"],
    agenda_heads=["Minutes", "Step", "Facilitator notes"],
    agenda=[("0–5", "Frame", "Explain that every team has some of these. The aim is to pick a few to improve, not to score the team."),
            ("5–15", "Spot", "Everyone ticks the symptoms they recognise, in silence. Add any missing ones in the Our Own panel."),
            ("15–20", "Vote", "Three dots each on the anti-patterns that hurt most."),
            ("20–40", "Understand", "For the top three, read the catalogue entry and discuss why it's happening here."),
            ("40–55", "Act", "Pick a tool to try for each, with an owner and a date to check."),
            ("55–60", "Close", "Book a re-run in six to eight weeks.")],
    sections_title="Using each part well",
    sections_intro="What to aim for on each part of the board.",
    sections=[("Spot", BLUE, ["Silent and individual", "Honest, not defensive"]),
              ("Vote", ORANGE, ["Three dots each", "Hurt most, not easiest"]),
              ("Our Own", SLATE, ["Add what's missing", "In the team's words"]),
              ("Our Top Three", RED, ["Why it's happening here", "A tool and an owner"]),
              ("Next Time", FOREST, ["Re-run regularly", "Celebrate ticks that go"])],
    tips=[("Normalise it", "Every team has anti-patterns. Saying so up front makes honest ticking easier."),
          ("Symptoms, not people", "The board names patterns in the system, never individuals."),
          ("Three is plenty", "Working on three anti-patterns well beats a long list of good intentions."),
          ("Ask why here", "The same anti-pattern has different causes in different teams. Discuss yours."),
          ("Use the catalogue", "Each entry says why the pattern hurts and what to try, which keeps discussion constructive."),
          ("Track progress", "Re-running the board shows which ticks have disappeared, a visible sign of improvement.")],
    pitfalls=("using it to judge a team or a person; trying to fix everything at once; voting on the easiest instead of "
              "the most harmful; no owners; never re-running it."),
    after=[("Straight away", "Start the three actions, using the tools you chose."),
           ("Each retro", "Check progress on the top three."),
           ("In 6–8 weeks", "Re-run the spotter and compare."),
           ("Share patterns", "Coaches can collect anonymised results across teams to spot system-wide issues.")],
    toolkit=("The spotter is a way in to the rest of the toolkit: every symptom points to a tool. Use it with the "
             "<a href=\"anti-patterns.html\">Anti-Pattern Catalogue</a>, the <a href=\"facilitator-guide-team-health-check.html\">"
             "Team Health Check</a> and the <a href=\"facilitator-guide-psych-safety.html\">Psychological Safety Check</a> "
             "to understand how a team is doing."),
    foot="“Which of these would we be embarrassed for a new joiner to see?”",
))


# ------------------------------------------------------------------ rendering

def guide_css():
    src = (OUT / "facilitator-guide-marginal-gains.html").read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    css = css.replace("#eb6c36", ACCENT).replace("#0C1A2E", NAVY)
    return css.rstrip() + "\n" + EXTRA_CSS.strip() + "\n"


def li(items):
    return "".join(f"<li>{i}</li>" for i in items)


def guide_spec(g):
    """The AI whiteboard prompt for the guide's board, read from the board's SVG (or "" if there isn't one)."""
    board = g["boards"][0][1]
    svg = OUT / board.replace(".html", ".svg")
    if not svg.exists():
        return ""
    return board_spec(svg, f"https://{SITE}/{board}")


SPEC_NOTE = ("Paste this into your whiteboard's AI assistant (for example Miro AI or Atlassian Rovo) or a general assistant, "
             "to get an editable, native version of the board. Results vary by tool, so expect to tidy it up. For an exact "
             "copy, import the SVG as a locked background instead.")


def spec_html(g):
    text = guide_spec(g)
    if not text:
        return ""
    return ('<section class="spec"><h3>Recreate it in your whiteboard</h3>'
            f'<p>{escape(SPEC_NOTE)}</p>'
            '<button type="button" onclick="(function(b){var t=b.parentNode.querySelector(\'pre\').textContent;'
            'navigator.clipboard.writeText(t).then(function(){b.textContent=\'Copied ✓\';setTimeout(function(){b.textContent=\'Copy AI prompt\'},2000)})})(this)">'
            'Copy AI prompt</button>'
            f'<details><summary>Show the prompt</summary><pre>{escape(text)}</pre></details></section>')


def render(g, css):
    n = 0

    def h2(text, cls=""):
        nonlocal n
        n += 1
        c = f' class="{cls}"' if cls else ""
        return f'<h2{c}><span class="n">{n}</span>{text}</h2>'

    boards = "".join(f'<a{" class=\"primary\"" if i == 0 else ""} href="{href}">{escape(label)} →</a>'
                     for i, (label, href) in enumerate(g["boards"]))
    boards += f'<a href="facilitator-guide-{g["slug"]}.docx" download>Word (editable) ↓</a>'
    glance = "".join(f"<div><b>{k}</b><span>{v}</span></div>" for k, v in g["glance"])
    heads = "".join(f"<th>{h}</th>" for h in g["agenda_heads"])
    rows = []
    for r in g["agenda"]:
        *times, act, note = r
        rows.append("<tr>" + "".join(f'<td class="t">{t}</td>' for t in times) +
                    f'<td class="a">{act}</td><td>{note}</td></tr>')
    areas = "".join(
        f'<div class="area" style="background:{light};color:{dark}"><h4 style="background:{dark}">{escape(name)}</h4>'
        f'<ul>{li(escape(p) for p in prompts)}</ul></div>'
        for name, (dark, light), prompts in g["sections"])
    tips = "".join(f'<div class="tip"><b>{escape(t)}</b>{escape(d)}</div>' for t, d in g["tips"])
    after = "".join(f"<div><h3>{escape(t)}</h3><p>{escape(d)}</p></div>" for t, d in g["after"])

    parts = [
        f'<p class="lede">“{escape(g["lede"])}”</p>',
        f'<p>{g["intro"]}</p>',
        f'<div class="glance">{glance}</div>',
        h2("Before the session"),
        f'<ul class="check">{li(g["before"])}</ul>',
        h2("Agenda &amp; run-sheet"),
        f'<table><thead><tr>{heads}</tr></thead><tbody>{"".join(rows)}</tbody></table>',
        h2(escape(g["sections_title"]), "pb"),
        f'<p>{escape(g["sections_intro"])}</p>',
        f'<div class="areas">{areas}</div>',
    ]
    if g.get("example"):
        ex = "".join(f"<div><b>{escape(k)}</b><span>{escape(v)}</span></div>" for k, v in g["example"])
        parts += [h2("Worked example"), f'<div class="example">{ex}</div>']
    parts += [
        h2("Facilitation tips"),
        f'<div class="tips">{tips}</div>',
        f'<div class="callout"><b>Common pitfalls:</b> {escape(g["pitfalls"])}</div>',
        h2("After the session"),
        f'<div class="two">{after}</div>',
        h2("How it fits the toolkit"),
        f'<p>{g["toolkit"]}</p>',
        spec_html(g),
        f'<p style="color:var(--muted);font-size:12px">← <a href="index.html">All tools</a> · <a href="glossary.html">Glossary of terms</a></p>',
        f'<footer><span>{escape(g["foot"])}</span><span>{escape(CREDIT)}</span></footer>',
    ]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(g["title"])}</title>
<link rel="stylesheet" href="{FONT_URL}">
<style>{css}</style>
</head>
<body>
<div class="page">
  <header class="masthead">
    <h1>{escape(g["title"])}</h1>
    <p>{escape(g["subtitle"])}</p>
    <div class="tag">{escape(g["tag"])}</div>
    <div class="boards">{boards}</div>
  </header>
  <div class="content">
    {chr(10).join("    " + p for p in parts).lstrip()}
  </div>
</div>
</body>
</html>
"""


def render_docx(g):
    """An editable Word copy of the guide, with the same content as the HTML page."""
    d = Doc(g["title"], AUTHOR)
    d.heading(g["title"], 0)
    d.para(g["subtitle"], italic=True)
    d.para(g["tag"], "Small")
    d.quote(f"“{g['lede']}”")
    d.para(g["intro"])
    d.table([k for k, _ in g["glance"]], [[v for _, v in g["glance"]]])
    d.heading("Before the session")
    d.bullets(g["before"])
    d.heading("Agenda & run-sheet")
    n = len(g["agenda_heads"])
    widths = [1300, 2300, 5400] if n == 3 else None
    d.table(g["agenda_heads"], [list(r) for r in g["agenda"]], widths)
    d.heading(g["sections_title"])
    d.para(g["sections_intro"])
    for name, _color, prompts in g["sections"]:
        d.heading(name, 2)
        d.bullets(prompts)
    if g.get("example"):
        d.heading("Worked example")
        d.table(["", "Example"], [list(r) for r in g["example"]], [2700, 6300])
    d.heading("Facilitation tips")
    for t, desc in g["tips"]:
        d.labelled(t + ".", desc)
    d.labelled("Common pitfalls:", g["pitfalls"])
    d.heading("After the session")
    for t, desc in g["after"]:
        d.labelled(t + ":", desc)
    d.heading("How it fits the toolkit")
    d.para(g["toolkit"])
    text = guide_spec(g)
    if text:
        d.heading("Recreate it in your whiteboard")
        d.para(SPEC_NOTE, "Small")
        for line in text.split("\n"):
            if line.strip():
                d.para(escape(line))
    d.para(f"Boards: https://{SITE}/{g['boards'][0][1]}  ·  Online guide: https://{SITE}/facilitator-guide-{g['slug']}.html", "Small")
    d.para(CREDIT + " · Adapt it freely; please keep the credit and say what you changed.", "Small")
    d.save(OUT / f"facilitator-guide-{g['slug']}.docx")


if __name__ == "__main__":
    css = guide_css()
    for g in GUIDES:
        path = OUT / f"facilitator-guide-{g['slug']}.html"
        path.write_text(render(g, css), encoding="utf-8")
        render_docx(g)
        print("wrote", path.name, "+ .docx")
