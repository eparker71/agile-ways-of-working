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
    ("Site reliability engineering (SRE)", "Running services with software engineering: automating operations work, setting "
     "reliability targets, and balancing reliability with new features using error budgets.", "Developed at Google.", ["slo", "incident"]),
    ("Service level indicator (SLI)", "A measure of how a service behaves as users feel it, usually good events divided by valid "
     "events, such as successful requests or fast page loads.", None, ["slo"]),
    ("Service level objective (SLO)", "A target for an SLI over a time window, such as 99.5% of checkouts succeeding over 30 "
     "days. An internal goal, set just high enough to keep users happy.", None, ["slo"]),
    ("Service level agreement (SLA)", "A promise to customers about a service's reliability, usually with penalties if it's "
     "missed. It should be looser than the SLO, so the team notices problems before customers are owed anything.", None, ["slo"]),
    ("Error budget", "The amount of unreliability a service can have while still meeting its SLO: 100% minus the target. While "
     "budget remains the team ships freely; when it runs out, reliability work comes first.", None, ["slo", "release"]),
    ("Toil", "Manual, repetitive operations work that could be automated and doesn't make the service better for good.", None,
     ["devops", "slo"]),
    ("CALMS", "Five parts of DevOps used as a health check: culture, automation, lean, measurement and sharing.",
     "Set out by Jez Humble, building on CAMS from John Willis and Damon Edwards.", ["devops", "cd-health"]),
    ("The three ways", "The principles behind DevOps: fast flow from idea to customer, fast feedback from customer to team, "
     "and a culture of continual learning and experimentation.", "From The Phoenix Project and The DevOps Handbook.", ["devops", "vsm"]),
    ("Predictive approach", "Planning and designing most of the work up front, then delivering to the plan with formal change "
     "control. Suits work that is well understood and costly to change.", "Often called waterfall.", ["approach"]),
    ("Hybrid approach", "Using agile and predictive approaches together, often for different parts of the same project, with "
     "agreed milestones, gates and reporting where they meet.", None, ["approach", "right-size"]),
    ("Tailoring", "Choosing and adapting the approach, events and artefacts to fit the project, instead of applying one method "
     "everywhere.", "A term from PMI's standards.", ["approach", "right-size"]),
    ("Work breakdown structure (WBS)", "A hierarchy that breaks the whole scope into smaller, manageable pieces of work. In agile "
     "delivery, epics, features and stories play this part, broken down by value to users.", None, ["epic", "storymap"]),
    ("Critical path", "The longest chain of dependent tasks in a schedule. Any delay on it delays the end date.", None,
     ["dependency", "ctp"]),
    ("Baseline", "The agreed version of the scope, schedule or cost that progress is measured against. Changing it goes through "
     "change control.", None, ["forecast", "status"]),
    ("Earned value", "A way of measuring progress by comparing the value of work completed with what was planned and what it "
     "cost. A burn-up chart shows a similar picture for agile work.", None, ["forecast", "status"]),
    ("Change control", "The agreed way of proposing, deciding and recording changes to the baseline.", None,
     ["raci", "prioritisation"]),
    ("Rolling-wave planning", "Planning the near future in detail and later work in outline, then adding detail as it gets "
     "closer.", None, ["roadmap", "ctp"]),
    ("Progressive elaboration", "Adding detail to plans and requirements as more becomes known, instead of fixing it all at the "
     "start.", None, ["refinement", "storymap"]),
    ("Lean", "A way of working that delivers what the customer values and steadily removes everything else, through flow, "
     "pull and continuous improvement.", "From the Toyota Production System. The five principles are from Womack and Jones, Lean Thinking (1996).",
     ["lean", "vsm", "kanban"]),
    ("Waste (muda)", "Anything that takes time or effort but adds no value for the customer. Lean names eight: transport, "
     "inventory, motion, waiting, overproduction, over-processing, defects and unused skills.", None, ["lean", "waste", "vsm", "blockers"]),
    ("Pull system", "Starting new work only when there is capacity and a real need for it, instead of pushing work in "
     "because a plan says so.", None, ["lean", "cadences", "kanban"]),
    ("Kaizen", "Continuous improvement in small steps, made by the people who do the work.", "Japanese for “change for the better”.",
     ["lean", "marginal", "experiment"]),
    ("Gemba", "Going to where the work happens to see it for yourself, instead of relying on reports.", "Japanese for “the real place”.",
     ["waste", "lean", "vsm"]),
    ("Takt time", "The pace work must be finished at to keep up with demand: available time divided by the number of items "
     "needed. Used to keep flow even.", None, ["lean", "cadences"]),
    ("A3 thinking", "Solving a problem on a single A3 sheet: background, current state, root cause, countermeasures and a plan "
     "to check the results.", "From Toyota.", ["a3", "lean", "rootcause"]),
    ("Poka-yoke", "Mistake-proofing: designing a step so the error can't happen, or is caught straight away.",
     "Japanese for “avoiding mistakes”.", ["lean", "testing", "pipeline"]),
    ("Jidoka (stop and fix)", "Stopping the work when something goes wrong, fixing the cause, and only then carrying on, so "
     "problems aren't passed down the line.", None, ["lean", "rootcause", "pipeline"]),
    ("SVG", "The file format of the boards: an image that stays sharp at any size and holds real, editable text. "
     "Open it in a web browser, add it to Miro, Mural or FigJam as a background, or change the words and colours in Figma "
     "or Inkscape.", None, []),
    ("AI autonomy levels", "How much an AI tool or agent may do on its own: it assists while a person decides, it acts and a "
     "person approves the result, or it acts alone within set limits and people check afterwards.", None, ["ai-delivery", "ai"]),
    ("Event Storming", "A workshop where business experts and engineers map a domain as a timeline of domain events on orange "
     "stickies, then add commands, actors, policies, systems and hotspots.", "From Alberto Brandolini.", ["event-storming"]),
    ("Domain event", "Something meaningful that happened in the business, written in the past tense, such as “Order Placed”.",
     "Used in Event Storming and domain-driven design.", ["event-storming"]),
    ("Cynefin®", "A sense-making framework that sorts situations into clear, complicated, complex and chaotic domains (with "
     "confusion in the centre), each calling for a different way to act.",
     "From Dave Snowden. Cynefin® is a registered trademark of Cognitive Edge Pte Ltd.", ["cynefin"]),
    ("Safe-to-fail experiment", "A small, reversible probe in a complex situation, designed so that failure is cheap and teaches "
     "something; run several in parallel and amplify the ones that work.", "From the Cynefin® framework (Dave Snowden).",
     ["cynefin", "experiment"]),
    ("Moving Motivators", "An exercise where each person ranks ten intrinsic motivators (such as curiosity, mastery and "
     "freedom) by importance, then moves each up or down to show how a change would affect it.",
     "From Management 3.0 (Jurgen Appelo).", ["motivation"]),
    ("Kudo cards", "Short written thank-yous for something specific a colleague did, given peer to peer and often, without "
     "any link to pay.", "From Management 3.0 (Jurgen Appelo).", ["motivation"]),
    ("Design sprint", "A five-day process for answering a big product question: map, sketch, decide, prototype and test with "
     "five customers, with a named Decider.", "From Jake Knapp at Google Ventures, described in Sprint (2016).", ["design-sprint"]),
    ("Four big risks", "The product risks to check before building: value (will they want it?), usability (can they use it?), "
     "feasibility (can we build it?) and viability (does it work for the business?).", "From Marty Cagan, Inspired.", ["bet"]),
    ("Now / Next / Later roadmap", "A roadmap that groups work by certainty instead of dates: Now is committed and in progress, "
     "Next is shaped and ready, and Later holds problems worth exploring. Each item links to a goal.",
     "Popularised by Janna Bastow (ProdPad).", ["roadmap"]),
    ("Personal user manual", "A short guide each person writes to working with them: when they work best, how to reach them, "
     "how they like feedback and what people misread about them.", "Popularised by Atlassian's Team Playbook.", ["user-manual"]),
    ("Levels of conflict", "Five stages a conflict can escalate through: problem to solve, disagreement, contest, crusade and "
     "world war. The language people use is the best clue to the level, and each level calls for a different response.",
     "From Speed B. Leas; brought to agile teams by Lyssa Adkins in Coaching Agile Teams.", ["conflict"]),
    ("SBI (Situation–Behaviour–Impact)", "A way to give specific feedback: describe the situation, the observable behaviour, "
     "and its impact, then listen. Works for praise as well as correction.", "From the Center for Creative Leadership.", ["feedback"]),
    ("Benefits realisation", "Checking, after a project ends, that the value it was meant to create really arrives, with a named "
     "owner and dates to measure each benefit.", "Common in project and programme management.", ["closeout", "value"]),
    ("Onboarding", "Helping a new team member get set up, understand how the team works and contribute, usually with a plan, a "
     "buddy and check-ins over the first few months.", None, ["onboarding"]),
    ("Brooks's law", "Adding people to a late software project makes it later, because new people need time to get up to speed "
     "and every extra person adds communication overhead.", "From Fred Brooks, The Mythical Man-Month (1975).", ["right-size"]),
    ("Release Train Engineer (RTE)", "The facilitator and servant leader for a team of teams: runs big-room planning, the regular "
     "cross-team sync, system demos and inspect & adapt, and clears impediments no single team can.",
     "SAFe's name for the role. Scrum@Scale's Chief Scrum Master is similar.", ["ctp", "sync", "cross-retro"]),
    ("Agile Release Train (ART)", "A long-lived team of agile teams, typically 50 to 125 people, that plans, delivers and improves "
     "together on a shared cadence toward common goals.", "SAFe term. Other names: team of teams; Scrum of Scrums (Scrum@Scale).",
     ["ctp", "sync", "dependency"]),
    ("Continuous integration (CI)", "Everyone merges small changes into the main branch often, at least daily, and every merge is "
     "built and tested automatically, so problems show up within minutes.", "Practice popularised by Extreme Programming (XP).",
     ["pipeline", "cd-health"]),
    ("Continuous delivery (CD)", "Keeping the software ready to release at any time: every change that passes the pipeline could "
     "go to production at the push of a button.", "Described by Jez Humble and David Farley.", ["pipeline", "cd-health", "release"]),
    ("Continuous deployment", "Going one step further than continuous delivery: every change that passes the pipeline goes to "
     "production automatically, with no manual release step.", None, ["pipeline", "release"]),
    ("Delivery pipeline", "The automated path a change takes from commit to production: build, test, checks, deploy and release. "
     "Also called a CI/CD pipeline or deployment pipeline.", None, ["pipeline"]),
    ("DevOps", "A way of working where development and operations share responsibility for building, releasing and running "
     "software, supported by automation and fast feedback.", None, ["devops", "pipeline", "cd-health", "incident"]),
    ("DORA metrics", "Four measures of delivery performance from the DORA research programme: deployment frequency, lead time for "
     "changes, change failure rate, and time to restore service.", "DORA: DevOps Research and Assessment.", ["delivery-metrics", "devops", "cd-health"]),
    ("Trunk-based development", "Working in small changes merged to one main branch (the trunk) at least daily, instead of long-lived "
     "branches that are hard to merge.", None, ["cd-health", "pipeline"]),
    ("Feature flag", "A switch in the code that turns a feature on or off without deploying again, so code can be deployed "
     "switched off and released later, or to some users only. Also called a feature toggle.", None, ["release", "cd-health"]),
    ("Canary release", "Releasing a change to a small share of users first, watching for problems, then widening it.", None, ["release"]),
    ("Blue-green deployment", "Running two copies of production: the new version goes to the idle copy, traffic switches to it, "
     "and switching back undoes the release.", None, ["release"]),
    ("Rollback", "Undoing a release by returning to the previous version. The alternative, fixing the problem with a new release, "
     "is called rolling forward or fixing forward.", None, ["release", "incident"]),
    ("Shift left", "Finding problems earlier in the lifecycle, when they're cheaper to fix: agreeing examples before coding, and "
     "checking quality, security and accessibility as you go.", None, ["testing", "example"]),
    ("Test pyramid", "A guide to balancing automated tests: many fast unit tests, fewer integration tests and a small number of slow "
     "end-to-end tests.", "Popularised by Mike Cohn.", ["testing"]),
    ("Exploratory testing", "People testing the software freely, learning as they go, to find problems that scripted tests don't "
     "look for.", None, ["testing"]),
    ("Go / no-go", "A short decision, against a checklist agreed in advance, on whether a release goes ahead.", None, ["release"]),
    ("SDLC (software development lifecycle)", "The stages software goes through from idea to use: typically discover, design, build, "
     "test, release, operate and learn. Traditional SDLCs run them once, in order; agile delivery runs the loop many times.", None,
     ["sdlc"]),
    ("Affinity estimation", "Sizing a whole backlog quickly by silently placing items in order from smallest to largest, then "
     "drawing size boundaries.", None, ["estimation"]),
    ("Architecture decision record (ADR)", "A short document recording one important technical decision: its context, the "
     "options considered, the decision and its consequences.", "Format described by Michael Nygard.", ["adr"]),
    ("Blameless review", "A review of an incident that looks at how the system made it possible, not at who to blame, so people "
     "share what really happened.", "Common in software reliability engineering.", ["incident", "rootcause"]),
    ("Customer journey map", "A picture of the stages a user goes through to reach a goal, with what they do, think and feel, "
     "pain points and opportunities.", None, ["persona"]),
    ("Dot voting", "A quick way to prioritise: everyone places a few dots on the options at the same time, and the most dots "
     "win.", None, ["facilitation", "lean-coffee"]),
    ("Fist of five", "A quick check of support: everyone shows zero to five fingers at once, and the lowest votes explain what's "
     "missing.", None, ["facilitation", "sprint-planning"]),
    ("Impact mapping", "A tree from a business goal to the actors who affect it, the behaviour changes needed, and the "
     "deliverables that might cause them.", "From Gojko Adzic.", ["impact"]),
    ("Jobs to be done", "A way of describing what users want in terms of progress: “When [situation], I want to [motivation], so "
     "I can [outcome].”", "Associated with Clayton Christensen and Tony Ulwick.", ["persona", "ost"]),
    ("Persona", "A short, evidence-based description of a type of user: their context, goals and frustrations.", None,
     ["persona", "vision"]),
    ("RACI", "A matrix showing who is Responsible, Accountable, Consulted and Informed for each piece of work. Exactly one person "
     "is accountable.", None, ["raci"]),
    ("T-shirt sizing", "Rough relative sizing using XS, S, M, L and XL, useful for many items or for roadmaps.", None, ["estimation"]),
    ("Value stream mapping", "Mapping every step from request to customer, with work and wait times, to find delays and improve "
     "flow.", "A lean technique, popularised by Mike Rother and John Shook.", ["vsm"]),
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
     "In SAFe, a feature fits within one planning increment. Azure DevOps includes a Feature level by default, between epic and story; elsewhere the term is used more loosely.", ["epic", "backlog"]),
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
    ("ESVP", "A quick, anonymous check-in at the start of a retrospective: each person says whether they feel like an "
     "Explorer, Shopper, Vacationer or Prisoner, which shows how engaged and safe the group feels.", None, ["retro"]),
    ("Learning zone", "The state where a team has both high psychological safety and high standards, so people speak up "
     "and stretch. Without standards it's a comfort zone; without safety, an anxiety zone.", "From Amy Edmondson.",
     ["leading-safety", "psych-safety"]),
    ("Prime Directive", "A statement read at the start of a retrospective: everyone did the best job they could with what "
     "they knew at the time. It sets a tone of learning, not blame.", "From Norm Kerth's book Project Retrospectives.",
     ["retro", "incident"]),
    ("Product goal", "The longer-term objective a product is working toward. Backlog items should move toward it.",
     "A Scrum term.", ["vision"]),
    ("Psychological safety", "A shared belief that it's safe to take interpersonal risks: to speak up, ask for help, admit a "
     "mistake or disagree. It isn't about being nice or lowering standards: the goal is high safety and high standards.",
     "From Amy Edmondson's research.", ["psych-safety", "leading-safety"]),
    ("Refinement", "The ongoing work of clarifying, splitting and ordering backlog items so the top of the backlog is ready.",
     "Scrum calls it Product Backlog refinement; it isn't a formal event.", ["splitting", "example"]),
    ("Retrospective", "A regular session where the team inspects how it works and agrees improvements to try.", None,
     ["retro", "cross-retro"]),
    ("Service level expectation (SLE)", "A forecast of how long a single item is likely to take, such as “85% of items finish "
     "within 8 days”.", "From the Kanban Guide.", ["ageing"]),
    ("Sprint Zero", "A short, timeboxed set-up period before a team's first iteration: forming the team, agreeing the vision, "
     "building a first backlog and setting up tools. Also called Iteration 0 or a team launch.",
     "Not part of the Scrum Guide, which expects every sprint to deliver something usable. Disciplined Agile calls it inception.",
     ["launch", "kickoff"]),
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
    ("Daily Scrum", "The team's daily 15-minute event to inspect progress toward the sprint goal and plan the next day. Often "
     "called a stand-up.", "A Scrum event.", ["daily", "events"]),
    ("Inspect & Adapt", "A multi-team event at the end of a planning period: a demo of the integrated work, a review of "
     "measures and a problem-solving workshop.", "A SAFe event; similar to LeSS's Overall Retrospective.", ["cross-retro", "events"]),
    ("Replenishment", "A regular meeting where a team chooses which options to pull into its system next, to fill free WIP "
     "capacity.", "A Kanban Method cadence.", ["cadences", "events"]),
    ("Service delivery review", "A regular review of flow and service levels, such as lead time and SLE, against what "
     "customers expect.", "A Kanban Method cadence.", ["cadences"]),
    ("Stand-up", "A short daily team meeting, often held standing to keep it brief. See Daily Scrum.", None, ["daily"]),
    ("System demo", "A demo of the integrated work of several teams, so stakeholders see the whole product working.",
     "A SAFe event.", ["events", "sprint-review"]),
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
:root{{--accent:{ACCENT};--navy:{NAVY};--ink:#1E293B;--muted:#5B6B82;--rule:#E2E8F0;}}
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
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#5B6B82;text-align:center;padding:0 16px 32px;}}
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
