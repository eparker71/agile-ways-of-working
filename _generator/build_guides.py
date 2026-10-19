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
               "management scorecard. Its value comes from discussing the votes and repeating the check every PI so trends show up."),
        glance=[("Duration", "45–60 min"), ("Group", "One team<br>5–10 people"), ("Cadence", "Every PI<br>or quarter"),
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
                  ("5 · Learning", SKY, ["What did we learn this PI?", "Is learning planned or squeezed in?"]),
                  ("6 · Mission", PURPLE, ["Could each of us explain why the team exists?", "How does our work link to the PI objectives?"]),
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
               ("Next check", "Repeat at the same point next PI, using the same dimensions, and set the trend arrows.")],
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
               "or a PI, and teams that want a reflective conversation rather than only listing problems."),
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
               "makes it a strong choice before a new PI or at a quarter boundary."),
        glance=[("Duration", "60 min (sprint)<br>2 h (quarter)"), ("Group", "One team<br>3–12 people"),
                ("Best for", "Goals, impediments<br>&amp; risks"), ("Output", "Up to 3 actions<br>&amp; known risks")],
        before=RETRO_BEFORE,
        agenda_heads=["Sprint", "Quarter", "Activity", "Facilitator notes"],
        agenda=retro_agenda("Yellow stickies in Wind, Anchors and Rocks. Use green for ideas that would add wind or cut an anchor.",
                            "Discuss the biggest anchors first, then the rocks. For each risk, decide whether to act now or just watch it.",
                            extra_first=("5–8", "10–15", "Name the island", "Agree the goal first and write it in the Island zone: a sprint goal, PI objective or product outcome.")),
        sections_title="Prompts for each zone",
        sections_intro="Read these out if a zone stays empty.",
        sections=[("1 · Wind", FOREST, ["What helped us move faster?", "Who or what supported us?", "What should we do more of?"]),
                  ("2 · Island", EMERALD, ["Where are we heading?", "What does success look like at the end of the sprint or quarter?"]),
                  ("3 · Anchors", RED, ["What slowed us down?", "Which handoffs or waits hurt most?", "What drags on us every time?"]),
                  ("4 · Rocks", AMBER, ["What could sink us?", "Which dependencies or deadlines worry us?", "What are we not talking about?"]),
                  ("Actions strip", ORANGE, ["Cut one anchor, avoid one rock", "Owner + done when for each"])],
        tips=[("Island first", "Without a shared goal, wind and anchors are hard to judge. Spend a few minutes agreeing it."),
              ("Risks need owners too", "For each important rock, agree who will watch it and what would trigger action, such as a ROAM review in PI planning."),
              *RETRO_TIPS[2:]],
        pitfalls=RETRO_PITFALLS + " With the Sailboat in particular, don't let the drawing become the conversation. Keep moving.",
        after=RETRO_AFTER, toolkit=RETRO_TOOLKIT,
        foot="“What can we do next to steer clear of the rocks?”",
    ),
]


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
        f'<footer><span>{escape(g["foot"])}</span><span>Agile Release Train · Systems-Thinking · Continuous Improvement · POM 2.0</span></footer>',
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
    <span class="badge">PRODUCT OPERATING MODEL 2.0</span>
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
