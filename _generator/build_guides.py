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
FONT_URL = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&amp;family=Geist:wght@400;500;600"
            "&amp;family=Geist+Mono:wght@400;500;600&amp;display=swap")

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
    "Pick the <b>sprint</b> board (60 min) or <b>quarter</b> board (2 h) and print at A3, or load the SVG into Miro / Mural / FigJam",
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
        boards=[("Sprint board", "retro-board-start-stop-continue-sprint.html"), ("Quarter board", "retro-board-start-stop-continue-quarter.html"),
                ("SVG · Sprint", "retro-board-start-stop-continue-sprint.svg"), ("SVG · Quarter", "retro-board-start-stop-continue-quarter.svg")],
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
        boards=[("Sprint board", "retro-board-4ls-sprint.html"), ("Quarter board", "retro-board-4ls-quarter.html"),
                ("SVG · Sprint", "retro-board-4ls-sprint.svg"), ("SVG · Quarter", "retro-board-4ls-quarter.svg")],
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
        boards=[("Sprint board", "retro-board-mad-sad-glad-sprint.html"), ("Quarter board", "retro-board-mad-sad-glad-quarter.html"),
                ("SVG · Sprint", "retro-board-mad-sad-glad-sprint.svg"), ("SVG · Quarter", "retro-board-mad-sad-glad-quarter.svg")],
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
        boards=[("Sprint board", "retro-board-sailboat-sprint.html"), ("Quarter board", "retro-board-sailboat-quarter.html"),
                ("SVG · Sprint", "retro-board-sailboat-sprint.svg"), ("SVG · Quarter", "retro-board-sailboat-quarter.svg")],
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
                     "checks that each story is understood and ready.")

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
              ("Revisit it", "Bring the board to quarterly planning and update it when evidence changes the picture.")],
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
        tag="Facilitator Run-Sheet · Plan · Value vs. Effort · Cost of Delay · MoSCoW · Now / Next / Later",
        boards=[("Open board", "prioritisation-board.html"), ("SVG", "prioritisation-board.svg")],
        lede="What does it cost us, each week, to not have this yet?",
        intro=("Most teams have more good ideas than capacity. The board combines four complementary techniques: a quick "
               "<b>value vs. effort</b> grid to sort many items, <b>cost of delay</b> (CD3, from Don Reinertsen) to rank the top few "
               "with numbers, <b>MoSCoW</b> to agree scope for a fixed date, and a <b>Now / Next / Later</b> roadmap to share the "
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
                ("35–60", "2 · Cost of Delay", "Take the top 5–8 items. Score value, time criticality and risk reduction relative to each other. Divide by size and rank."),
                ("60–75", "3 · MoSCoW", "If there's a fixed date or release, sort the ranked items into Must, Should, Could and Won't (this time)."),
                ("75–100", "4 · Now · Next · Later", "Place the items on the roadmap and write the outcome for each column. Only Now is committed."),
                ("100–110", "Close", "Read the roadmap back. Confirm the decision owner agrees, and who will share it with stakeholders.")],
        sections_title="Using each technique well",
        sections_intro="What each part is for, and what to watch for.",
        sections=[("1 · Value vs. Effort", BLUE, ["Relative placement is enough", "Big bets: slice before committing", "Drop the money pits"]),
                  ("2 · Cost of Delay", PURPLE, ["Score each column relative to the lowest item", "CoD / size gives the order", "Use it for the top few only"]),
                  ("3 · MoSCoW", ORANGE, ["Musts should be about 60% of capacity", "Won't means not this time", "Needs a fixed date or scope"]),
                  ("4 · Now · Next · Later", FOREST, ["Outcomes, not dates", "Now is committed; Later is options", "Keep Next short"])],
        tips=[("Compare, don't score in isolation", "Ask “is this more or less valuable than that?” Relative judgements are faster and more reliable."),
              ("Make delay visible", "Ask what it costs each week not to have an item. Time-critical work often moves up."),
              ("Slice the big bets", "High-value, high-effort items usually hide a smaller, high-value slice. Use the Epic Canvas or Story Map."),
              ("Protect the Could list", "If everything is a Must, MoSCoW stops working. Push back until Musts fit comfortably."),
              ("One decision owner", "The group advises; one person decides. Say who before you start."),
              ("Roadmaps change", "Review Now / Next / Later every iteration or month. Moving items is learning, not failure.")],
        pitfalls=("scoring items in isolation; letting the loudest stakeholder set the order; everything as a Must; "
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


# ------------------------------------------------------------------ rendering

def guide_css():
    src = (OUT / "facilitator-guide-marginal-gains.html").read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    return css.rstrip() + "\n" + EXTRA_CSS.strip() + "\n"


def li(items):
    return "".join(f"<li>{i}</li>" for i in items)


def render(g, css):
    n = 0

    def h2(text, cls=""):
        nonlocal n
        n += 1
        c = f' class="{cls}"' if cls else ""
        return f'<h2{c}><span class="n">{n}</span>{text}</h2>'

    boards = "".join(f'<a{" class=\"primary\"" if i == 0 else ""} href="{href}">{escape(label)} →</a>'
                     for i, (label, href) in enumerate(g["boards"]))
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
        f'<p style="color:var(--muted);font-size:12px">← <a href="index.html">All tools</a></p>',
        f'<footer><span>{escape(g["foot"])}</span><span>Systems-Thinking · Continuous Improvement · Team-Led Change</span></footer>',
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


if __name__ == "__main__":
    css = guide_css()
    for g in GUIDES:
        path = OUT / f"facilitator-guide-{g['slug']}.html"
        path.write_text(render(g, css), encoding="utf-8")
        print("wrote", path.name)
