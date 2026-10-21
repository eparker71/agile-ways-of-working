#!/usr/bin/env python3
"""Generate start-here-by-role.html and the role filter on index.html.

ROLES below is the single source for which tools suit which role. The script:
  - writes start-here-by-role.html
  - tags each card on index.html with data-roles="..." (matched by its Open link)
  - inserts the role filter chips, CSS and script into index.html (between
    the <!-- roles:... --> markers, which it adds on first run)

Run:  python3 _generator/build_roles.py      (after adding a card to index.html)
"""
import re
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import ACCENT, NAVY, CREDIT, FONT_URL as _FONT_URL, SVG_LABEL, SVG_TIP  # noqa: E402  (edit brand.py to rebrand)
FONT_URL = _FONT_URL.replace("&", "&amp;")

# key: (title, board page, guide page or None, href prefix used to match index cards)
TOOLS = {
    "sm-cheat": ("Scrum Master & Agile Coach Cheat Sheet", "scrum-master-agile-coach-cheat-sheet.html", None, "scrum-master-agile-coach"),
    "jira": ("Jira Cheat Sheet", "jira-cheat-sheet.html", None, "jira-cheat-sheet"),
    "lean-coffee": ("Lean Coffee", "lean-coffee-board.html", "facilitator-guide-lean-coffee.html", "lean-coffee"),
    "launch": ("Team Launch (Sprint Zero)", "team-launch-board.html", "facilitator-guide-team-launch.html", "team-launch"),
    "spotter": ("Anti-Pattern Spotter", "anti-pattern-spotter-board.html", "facilitator-guide-anti-pattern-spotter.html", "anti-pattern-spotter"),
    "leading-safety": ("Leading for Psychological Safety", "leading-psych-safety-poster.html", "facilitator-guide-leading-psych-safety.html", "leading-psych-safety"),
    "team-charter": ("Team Charter", "team-charter-board.html", "facilitator-guide-team-charter.html", "team-charter"),
    "ai": ("AI Working Agreement", "ai-working-agreement-board.html", "facilitator-guide-ai-working-agreement.html", "ai-working-agreement"),
    "vision": ("Product Vision Board", "product-vision-board.html", "facilitator-guide-product-vision.html", "product-vision"),
    "ost": ("Opportunity Solution Tree", "opportunity-solution-tree-board.html", "facilitator-guide-opportunity-solution-tree.html", "opportunity-solution-tree"),
    "prioritisation": ("Prioritisation Board", "prioritisation-board.html", "facilitator-guide-prioritisation.html", "prioritisation"),
    "kickoff": ("Project Kickoff", "project-kickoff-board.html", "facilitator-guide-project-kickoff.html", "project-kickoff"),
    "stakeholder": ("Stakeholder Map", "stakeholder-map-board.html", "facilitator-guide-stakeholder-map.html", "stakeholder-map"),
    "premortem": ("Pre-mortem", "pre-mortem-board.html", "facilitator-guide-pre-mortem.html", "pre-mortem"),
    "forecast": ("Release Forecast & Burn-up", "release-forecast-board.html", "facilitator-guide-release-forecast.html", "release-forecast"),
    "raid": ("RAID Log", "raid-log-board.html", "facilitator-guide-raid-log.html", "raid-log"),
    "status": ("Outcome Status Report", "status-report-board.html", "facilitator-guide-status-report.html", "status-report"),
    "backlog": ("Backlog Item Anatomy", "backlog-anatomy-poster.html", "facilitator-guide-backlog-anatomy.html", "backlog-anatomy"),
    "epic": ("Epic Breakdown Canvas", "epic-breakdown-canvas.html", "facilitator-guide-epic-breakdown-canvas.html", "epic-breakdown"),
    "storymap": ("User Story Map", "story-map-board.html", "facilitator-guide-story-map.html", "story-map"),
    "splitting": ("Story Splitting", "story-splitting-poster.html", "facilitator-guide-story-splitting.html", "story-splitting"),
    "example": ("Example Mapping", "example-mapping-board.html", "facilitator-guide-example-mapping.html", "example-mapping"),
    "daily": ("Daily Sync", "daily-sync-board.html", "facilitator-guide-daily-sync.html", "daily-sync"),
    "refinement": ("Backlog Refinement", "backlog-refinement-board.html", "facilitator-guide-backlog-refinement.html", "backlog-refinement"),
    "cadences": ("Kanban Cadences", "kanban-cadences-board.html", "facilitator-guide-kanban-cadences.html", "kanban-cadences"),
    "events": ("Events & Cadences", "events-cadences-poster.html", "facilitator-guide-events-cadences.html", "events-cadences"),
    "sprint-planning": ("Sprint Planning", "sprint-planning-board.html", "facilitator-guide-sprint-planning.html", "sprint-planning"),
    "sprint-review": ("Sprint Review", "sprint-review-board.html", "facilitator-guide-sprint-review.html", "sprint-review"),
    "buffer": ("Buffering & Swarming", "buffering-swarming-board.html", "facilitator-guide-buffering-swarming.html", "buffering-swarming"),
    "kanban": ("Kanban Board Design", "kanban-board-design.html", "facilitator-guide-kanban-board-design.html", "kanban-board-design"),
    "ageing": ("Ageing WIP & SLE", "ageing-wip-board.html", "facilitator-guide-ageing-wip.html", "ageing-wip"),
    "blockers": ("Blocker Clustering", "blocker-clustering-board.html", "facilitator-guide-blocker-clustering.html", "blocker-clustering"),
    "skills": ("Skills Matrix", "skills-matrix-board.html", "facilitator-guide-skills-matrix.html", "skills-matrix"),
    "impediments": ("Impediments Board", "impediments-board.html", "facilitator-guide-impediments.html", "impediments"),
    "pairing": ("Pairing & Mobbing", "pairing-mobbing-board.html", "facilitator-guide-pairing-mobbing.html", "pairing-mobbing"),
    "okr": ("Objectives & Key Results", "okr-board.html", "facilitator-guide-okr.html", "okr-board"),
    "ctp": ("Cross-Team Planning", "cross-team-planning-board.html", "facilitator-guide-cross-team-planning.html", "cross-team-planning"),
    "dependency": ("Dependency Map", "dependency-map-board.html", "facilitator-guide-dependency-map.html", "dependency-map"),
    "sync": ("Cross-Team Sync", "cross-team-sync-board.html", "facilitator-guide-cross-team-sync.html", "cross-team-sync"),
    "topology": ("Team Topology Design", "team-topology-board.html", "facilitator-guide-team-topology.html", "team-topology"),
    "adkar": ("ADKAR Change Readiness", "adkar-board.html", "facilitator-guide-adkar.html", "adkar"),
    "portfolio-kanban": ("Portfolio Kanban & Investment Mix", "portfolio-kanban-board.html", "facilitator-guide-portfolio-kanban.html", "portfolio-kanban"),
    "delivery-metrics": ("Delivery Metrics & Tech Debt", "delivery-metrics-board.html", "facilitator-guide-delivery-metrics.html", "delivery-metrics"),
    "delegation": ("Delegation Board", "delegation-board.html", "facilitator-guide-delegation.html", "delegation-board"),
    "coaching": ("Coaching Conversation", "coaching-conversation-board.html", "facilitator-guide-coaching-conversation.html", "coaching-conversation"),
    "psych-safety": ("Psychological Safety Check", "psych-safety-board.html", "facilitator-guide-psych-safety.html", "psych-safety"),
    "cross-retro": ("Cross-Team Retro", "cross-team-retro-board.html", "facilitator-guide-cross-team-retro.html", "cross-team-retro"),
    "vsm": ("Value Stream Map", "value-stream-map-board.html", "facilitator-guide-value-stream-map.html", "value-stream-map"),
    "incident": ("Blameless Incident Review", "incident-review-board.html", "facilitator-guide-incident-review.html", "incident-review"),
    "raci": ("RACI & Decision Log", "raci-decision-log-board.html", "facilitator-guide-raci-decision-log.html", "raci-decision-log"),
    "persona": ("Persona & Journey Map", "persona-journey-board.html", "facilitator-guide-persona-journey.html", "persona-journey"),
    "impact": ("Impact Map", "impact-map-board.html", "facilitator-guide-impact-map.html", "impact-map"),
    "estimation": ("Estimation", "estimation-board.html", "facilitator-guide-estimation.html", "estimation-board"),
    "facilitation": ("Facilitation Techniques", "facilitation-techniques-poster.html", "facilitator-guide-facilitation-techniques.html", "facilitation-techniques"),
    "adr": ("Architecture Decision Record", "adr-board.html", "facilitator-guide-adr.html", "adr-board"),
    "value": ("Value Metrics", "value-metrics-board.html", "facilitator-guide-value-metrics.html", "value-metrics"),
    "health": ("Team Health Check", "team-health-check-board.html", "facilitator-guide-team-health-check.html", "team-health-check"),
    "marginal": ("Marginal Gains Workshop", "marginal-gains-workshop-board.html", "facilitator-guide-marginal-gains.html", "marginal-gains"),
    "experiment": ("1% Experiment Canvas", "experiment-canvas.html", "facilitator-guide-experiment-canvas.html", "experiment-canvas"),
    "rootcause": ("Root Cause Analysis", "root-cause-board.html", "facilitator-guide-root-cause.html", "root-cause"),
    "closeout": ("Project Close-out", "project-closeout-board.html", "facilitator-guide-project-closeout.html", "project-closeout"),
    "onboarding": ("Team Onboarding", "team-onboarding-board.html", "facilitator-guide-team-onboarding.html", "team-onboarding"),
    "right-size": ("Right-Size Your Structure", "right-size-poster.html", "facilitator-guide-right-size.html", "right-size"),
    "sdlc": ("SDLC at a Glance", "sdlc-poster.html", "facilitator-guide-sdlc.html", "sdlc"),
    "lean": ("Lean Principles", "lean-principles-poster.html", "facilitator-guide-lean-principles.html", "lean-principles"),
    "pipeline": ("Delivery Pipeline Canvas", "delivery-pipeline-board.html", "facilitator-guide-delivery-pipeline.html", "delivery-pipeline"),
    "testing": ("Test Strategy", "test-strategy-board.html", "facilitator-guide-test-strategy.html", "test-strategy"),
    "release": ("Release Readiness & Strategy", "release-readiness-board.html", "facilitator-guide-release-readiness.html", "release-readiness"),
    "cd-health": ("Continuous Delivery Health Check", "cd-health-check-board.html", "facilitator-guide-cd-health-check.html", "cd-health-check"),
    "roadmap": ("Now · Next · Later Roadmap", "roadmap-board.html", "facilitator-guide-roadmap.html", "roadmap"),
    "user-manual": ("Personal User Manual", "user-manual-board.html", "facilitator-guide-user-manual.html", "user-manual"),
    "conflict": ("Levels of Conflict", "conflict-levels-board.html", "facilitator-guide-conflict-levels.html", "conflict-levels"),
    "feedback": ("Feedback Conversation", "feedback-conversation-board.html", "facilitator-guide-feedback-conversation.html", "feedback-conversation"),
    "motivation": ("Motivation & Recognition", "motivation-board.html", "facilitator-guide-motivation.html", "motivation"),
    "design-sprint": ("Design Sprint", "design-sprint-board.html", "facilitator-guide-design-sprint.html", "design-sprint"),
    "bet": ("Product Bet Canvas", "product-bet-canvas.html", "facilitator-guide-product-bet-canvas.html", "product-bet-canvas"),
    "ai-delivery": ("AI in Delivery", "ai-delivery-board.html", "facilitator-guide-ai-delivery.html", "ai-delivery"),
    "event-storming": ("Event Storming", "event-storming-board.html", "facilitator-guide-event-storming.html", "event-storming"),
    "cynefin": ("Cynefin® Sense-Making", "cynefin-board.html", "facilitator-guide-cynefin.html", "cynefin"),
    "retro": ("Retrospective Kit", "retro-board-start-stop-continue.html", "facilitator-guide-retro-start-stop-continue.html", "retro-board-"),
}

# Extra search words for home page cards, so a search finds tools by the idea they come from (hidden on the page)
TAGS = {k: "lean" for k in ("lean", "vsm", "kanban", "cadences", "ageing", "buffer", "blockers", "rootcause", "marginal",
                            "experiment")}

# id, name, what you're there to do, start with (3), also useful
ROLES = [
    ("sm", "Scrum Master / Delivery Lead",
     "You help the team deliver well: smooth flow, useful events, and impediments removed.",
     ["sm-cheat", "retro", "impediments"],
     ["sprint-planning", "sprint-review", "team-charter", "ai", "health", "kanban", "ageing", "buffer", "blockers", "pairing",
      "skills", "example", "splitting", "rootcause", "experiment", "marginal", "lean-coffee", "jira", "adkar", "coaching", "psych-safety", "delivery-metrics", "backlog", "facilitation", "estimation", "vsm", "lean", "incident", "launch", "daily", "refinement", "cadences", "events", "spotter", "leading-safety", "sdlc", "pipeline", "release", "cd-health", "right-size", "sync", "dependency", "forecast", "closeout", "onboarding", "roadmap", "user-manual", "conflict", "feedback", "motivation", "ai-delivery", "cynefin"]),
    ("coach", "Agile Coach",
     "You help teams and leaders improve how they work, and coach the system beyond any one team.",
     ["health", "marginal", "topology"],
     ["sm-cheat", "retro", "team-charter", "ai", "experiment", "rootcause", "kanban", "ageing", "blockers", "skills",
      "value", "okr", "ctp", "sync", "impediments", "lean-coffee", "adkar", "coaching", "psych-safety", "delegation", "cross-retro", "portfolio-kanban", "backlog", "facilitation", "vsm", "lean", "incident", "launch", "events", "cadences", "daily", "spotter", "leading-safety", "sdlc", "pipeline", "cd-health", "right-size", "onboarding", "user-manual", "conflict", "feedback", "motivation", "design-sprint", "ai-delivery", "event-storming", "cynefin"]),
    ("po", "Product Owner / Product Manager",
     "You decide what's worth building, for whom, and in what order, and you prove it worked.",
     ["vision", "ost", "prioritisation"],
     ["epic", "storymap", "splitting", "example", "sprint-planning", "sprint-review", "okr", "value", "forecast",
      "stakeholder", "experiment", "jira", "portfolio-kanban", "backlog", "persona", "impact", "estimation", "facilitation", "launch", "refinement", "events", "sdlc", "release", "testing", "retro", "onboarding", "roadmap", "feedback", "bet", "design-sprint", "event-storming", "cynefin"]),
    ("pm", "Project Manager",
     "You get a defined piece of work delivered: scope, stakeholders, risks, forecasts and decisions.",
     ["kickoff", "raid", "status"],
     ["stakeholder", "premortem", "forecast", "prioritisation", "team-charter", "sprint-review", "dependency",
      "impediments", "lean-coffee", "jira", "adkar", "psych-safety", "raci", "facilitation", "launch", "events", "daily", "spotter", "leading-safety", "sdlc", "release", "right-size", "estimation", "closeout", "roadmap", "conflict", "feedback", "ai-delivery", "cynefin"]),
    ("program", "Program Manager",
     "You deliver a programme of related projects and teams: shared outcomes, budget, stakeholders, dependencies and risks in the open.",
     ["okr", "dependency", "status"],
     ["ctp", "sync", "topology", "raid", "forecast", "premortem", "value", "stakeholder", "impediments", "marginal", "adkar", "cross-retro", "portfolio-kanban", "delivery-metrics", "vsm", "lean", "raci", "facilitation", "launch", "events", "spotter", "leading-safety", "sdlc", "release", "pipeline", "right-size", "kickoff", "closeout", "roadmap", "conflict", "motivation", "bet", "ai-delivery", "cynefin"]),
    ("rte", "Release Train Engineer / Chief Scrum Master",
     "You facilitate a team of teams: big-room planning, the regular cross-team sync, system demos and inspect & adapt, "
     "and clearing impediments no single team can. Called a Release Train Engineer in SAFe and a Chief Scrum Master in Scrum@Scale.",
     ["ctp", "sync", "cross-retro"],
     ["dependency", "okr", "impediments", "blockers", "events", "cadences", "raid", "premortem", "forecast", "status", "value",
      "delivery-metrics", "vsm", "lean", "topology", "pipeline", "release", "sdlc", "portfolio-kanban", "stakeholder", "facilitation",
      "lean-coffee", "sm-cheat", "health", "psych-safety", "leading-safety", "coaching", "marginal", "adkar", "spotter", "jira", "right-size", "closeout", "roadmap", "conflict", "ai-delivery", "cynefin"]),
    ("portfolio", "Portfolio Manager / PMO",
     "You decide where the organisation invests, and check that the investment delivers value.",
     ["portfolio-kanban", "value", "prioritisation"],
     ["okr", "status", "kickoff", "premortem", "ctp", "topology", "stakeholder", "forecast", "adkar", "delegation", "delivery-metrics", "vsm", "lean", "raci", "impact", "events", "leading-safety", "sdlc", "right-size", "closeout", "roadmap", "bet", "ai-delivery", "cynefin"]),
    ("leader", "Executive / Sponsor",
     "You set direction, fund the work, remove the biggest obstacles, and shape how teams are organised.",
     ["value", "okr", "topology"],
     ["vision", "status", "stakeholder", "premortem", "kickoff", "impediments", "ai", "health", "adkar", "portfolio-kanban", "delegation", "psych-safety", "coaching", "vsm", "lean", "raci", "impact", "events", "spotter", "leading-safety", "sdlc", "right-size", "closeout", "roadmap", "feedback", "motivation", "bet", "ai-delivery", "cynefin"]),
    ("eng", "Engineering Manager / Tech Lead",
     "You build capable teams and healthy systems: skills, flow, quality and sensible team boundaries.",
     ["skills", "topology", "kanban"],
     ["pairing", "ageing", "buffer", "blockers", "ai", "team-charter", "rootcause", "example", "splitting",
      "dependency", "health", "impediments", "delivery-metrics", "psych-safety", "coaching", "delegation", "backlog", "vsm", "lean", "incident", "adr", "estimation", "launch", "daily", "refinement", "cadences", "spotter", "leading-safety", "pipeline", "testing", "release", "cd-health", "sdlc", "right-size", "experiment", "onboarding", "user-manual", "conflict", "feedback", "motivation", "design-sprint", "ai-delivery", "event-storming", "cynefin"]),
    ("ux", "Designer / Business Analyst",
     "You understand users and the problem, and help the team build the right thing, clearly specified.",
     ["ost", "storymap", "example"],
     ["vision", "splitting", "epic", "sprint-review", "premortem", "pairing", "backlog", "persona", "impact", "facilitation", "refinement", "testing", "sdlc", "experiment", "roadmap", "user-manual", "design-sprint", "bet", "event-storming"]),
    ("team", "Team Member",
     "You do the work, and you help decide how the team works and improves.",
     ["team-charter", "retro", "pairing"],
     ["ai", "sprint-planning", "sprint-review", "lean-coffee", "skills", "kanban", "buffer", "impediments", "example",
      "splitting", "health", "psych-safety", "backlog", "estimation", "incident", "facilitation", "adr", "launch", "daily", "refinement", "events", "spotter", "pipeline", "testing", "release", "cd-health", "ageing", "experiment", "jira", "rootcause", "onboarding", "user-manual", "feedback", "motivation", "design-sprint", "event-storming"]),
]

for _id, _n, _d, start, also in ROLES:
    for k in start + also:
        assert k in TOOLS, f"{_id}: unknown tool {k}"


def roles_for(href):
    """Role ids for the index card whose Open link is href."""
    if href.startswith(("start-here-by-role", "glossary", "make-it-yours", "anti-patterns", "scenarios")):
        return [rid for rid, *_ in ROLES]
    for key, (_, _, _, prefix) in TOOLS.items():
        if href.startswith(prefix):
            return [rid for rid, _, _, start, also in ROLES if key in start or key in also]
    return None


# ------------------------------------------------------------------ role page

def tool_link(key, primary=False):
    title, board, guide, _ = TOOLS[key]
    g = f'<a class="g" href="{guide}">guide</a>' if guide else ""
    cls = "tool start" if primary else "tool"
    return f'<span class="{cls}"><a href="{board}">{escape(title)}</a>{g}</span>'


def build_page():
    nav = "".join(f'<a href="#{rid}">{escape(name.split(" / ")[0])}</a>' for rid, name, *_ in ROLES)
    sections = []
    for rid, name, desc, start, also in ROLES:
        sections.append(f"""  <section class="role" id="{rid}">
    <div class="rh"><h2>{escape(name)}</h2><a class="filter" href="index.html#role={rid}">Show on the home page →</a></div>
    <p>{escape(desc)}</p>
    <div class="lbl">Start with</div>
    <div class="tools">{"".join(tool_link(k, True) for k in start)}</div>
    <div class="lbl">Also useful</div>
    <div class="tools">{"".join(tool_link(k) for k in also)}</div>
  </section>""")
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Start Here by Role</title>
<link rel="stylesheet" href="{FONT_URL}">
<style>
:root{{--accent:{ACCENT};--navy:{NAVY};--ink:#1E293B;--muted:#5B6B82;--rule:#E2E8F0;}}
*{{box-sizing:border-box;}}
html,body{{margin:0;background:#F1F5F9;}}
body{{font-family:'Geist',Inter,system-ui,sans-serif;color:var(--ink);font-size:14px;line-height:1.5;}}
header{{background:var(--navy);border-top:4px solid var(--accent);color:#fff;padding:36px 16px 28px;}}
.wrap{{max-width:1040px;margin:0 auto;padding:0 16px;}}
h1{{font:400 44px/1.05 'Instrument Serif',Georgia,serif;margin:0 0 8px;}}
header p{{color:#94A3B8;margin:0 0 18px;max-width:680px;}}
header a.back{{color:#94A3B8;font:500 11px 'Geist Mono',monospace;letter-spacing:.06em;}}
nav{{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px;}}
nav a{{font:500 11px 'Geist Mono',monospace;letter-spacing:.04em;color:#fff;text-decoration:none;border:1px solid #334155;border-radius:14px;padding:5px 11px;}}
nav a:hover{{border-color:var(--accent);color:var(--accent);}}
main{{padding:24px 0 48px;}}
.role{{background:#fff;border:1px solid var(--rule);border-radius:10px;padding:20px 22px;margin:0 0 16px;box-shadow:0 1px 3px rgba(0,0,0,.05);scroll-margin-top:16px;}}
.rh{{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;}}
.role h2{{font:400 26px/1.1 'Instrument Serif',Georgia,serif;margin:0;}}
.role p{{margin:6px 0 14px;color:var(--muted);}}
a.filter{{font:500 11px 'Geist Mono',monospace;color:#9A3412;text-decoration:none;}}
a.filter:hover{{text-decoration:underline;}}
.lbl{{font:600 9px 'Geist Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:10px 0 6px;}}
.tools{{display:flex;flex-wrap:wrap;gap:8px;}}
.tool{{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--rule);border-radius:6px;padding:5px 10px;font-size:13px;}}
.tool a{{color:var(--ink);text-decoration:none;}}
.tool a:hover{{color:var(--accent);}}
.tool a.g{{font:500 10px 'Geist Mono',monospace;color:var(--muted);border-left:1px solid var(--rule);padding-left:8px;}}
.tool.start{{background:var(--ink);border-color:var(--ink);}}
.tool.start a{{color:#fff;font-weight:600;}}
.tool.start a.g{{color:#94A3B8;border-color:#475569;font-weight:500;}}
footer{{font:9px 'Geist Mono',monospace;letter-spacing:.08em;color:#5B6B82;text-align:center;padding:0 16px 32px;}}
@media print{{header{{padding:20px 16px;}} nav,a.filter{{display:none;}} .role{{break-inside:avoid;box-shadow:none;}}}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="index.html">← All tools</a>
  <h1>Start Here by Role</h1>
  <p>Find the tools that fit your role. Each role has three to start with, then others worth knowing. Roles overlap, so use whichever lists help.</p>
  <nav>{nav}</nav>
</div></header>
<main><div class="wrap">
{chr(10).join(sections)}
</div></main>
<footer>{escape(CREDIT)}</footer>
</body>
</html>
"""
    (OUT / "start-here-by-role.html").write_text(page, encoding="utf-8")
    print("wrote start-here-by-role.html")


# ------------------------------------------------------------------ index filter

FILTER_CSS = """/* roles:css */
.rolebar{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px;align-items:center;}
.rolebar span{font:500 9px 'Geist Mono',monospace;letter-spacing:.12em;color:#94A3B8;text-transform:uppercase;margin-right:4px;}
.rolebar button{font:500 11px 'Geist Mono',monospace;letter-spacing:.04em;color:#fff;background:none;border:1px solid #334155;border-radius:14px;padding:5px 11px;cursor:pointer;}
.rolebar button:hover{border-color:var(--accent);color:var(--accent);}
.rolebar button[aria-pressed="true"]{background:#C2410C;border-color:#C2410C;color:#fff;}
.sections{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.96);backdrop-filter:blur(6px);border-bottom:1px solid var(--rule);}
.sections .wrap{display:flex;gap:10px;align-items:center;padding-top:8px;padding-bottom:8px;}
.sections .links{display:flex;gap:2px;flex:1;min-width:0;overflow-x:auto;scrollbar-width:thin;}
.sections a{flex:none;font:500 11.5px 'Geist',system-ui,sans-serif;color:var(--ink);text-decoration:none;border-radius:6px;padding:5px 7px;white-space:nowrap;}
.sections a:hover{background:#F1F5F9;color:#9A3412;}
.sections input{flex:none;font:13px 'Geist',system-ui,sans-serif;padding:6px 10px;border:1px solid var(--rule);border-radius:6px;width:170px;}
.rolenote{display:none;margin:0 0 4px;font-size:13px;color:var(--muted);}
.rolenote.on{display:block;}
.rolenote a{color:#9A3412;}
.hidden{display:none !important;}
@media (max-width:720px){.sections input{width:120px;}.sections .links{padding-right:28px;-webkit-mask-image:linear-gradient(to right,#000 calc(100% - 36px),transparent);mask-image:linear-gradient(to right,#000 calc(100% - 36px),transparent);}}
@media (max-width:640px){.rolebar{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding-right:32px;-webkit-mask-image:linear-gradient(to right,#000 calc(100% - 36px),transparent);mask-image:linear-gradient(to right,#000 calc(100% - 36px),transparent);}.rolebar::-webkit-scrollbar{display:none;}.rolebar span,.rolebar button{flex:none;white-space:nowrap;}}
/* /roles:css */
"""

# short labels for the sticky section menu (h2 id -> label); falls back to the full heading
SHORT = {"setup": "Team set-up", "decide": "What to build", "breakdown": "Break down", "iterate": "Events",
         "flow": "Flow", "engineering": "Engineering", "improve": "Improve", "project": "Projects",
         "teams": "Multi-team", "lead": "Leadership", "facilitate": "Facilitation"}

FILTER_JS = """<!-- roles:js -->
<script>
(function(){
  var buttons=document.querySelectorAll('.rolebar button'), note=document.querySelector('.rolenote'),
      search=document.querySelector('.sections input'), role='all';
  function apply(){
    var q=(search && search.value || '').trim().toLowerCase();
    buttons.forEach(function(b){b.setAttribute('aria-pressed', String(b.dataset.role===role));});
    document.querySelectorAll('.card').forEach(function(c){
      var r=(c.dataset.roles||'').split(' '), okRole=role==='all' || r.indexOf(role)>=0,
          okText=!q || c.textContent.toLowerCase().indexOf(q)>=0;
      c.classList.toggle('hidden', !(okRole && okText));
    });
    document.querySelectorAll('main h2').forEach(function(h){
      var g=h.nextElementSibling, any=g && g.querySelector('.card:not(.hidden)');
      h.classList.toggle('hidden', !any); if(g) g.classList.toggle('hidden', !any);
      var link=document.querySelector('.sections a[href="#'+h.id+'"]'); if(link) link.classList.toggle('hidden', !any);
    });
    var b=document.querySelector('.rolebar button[data-role="'+role+'"]'), parts=[];
    if(role!=='all' && b) parts.push('Showing tools for <b>'+b.dataset.name+'</b>. <a href="start-here-by-role.html#'+role+'">Where to start</a>');
    if(q) parts.push('Matching “'+q.replace(/[<>&]/g,'')+'”');
    if(parts.length){ note.innerHTML=parts.join(' · ')+' · <a href="#" data-clear>Show all</a>'; note.classList.add('on'); }
    else note.classList.remove('on');
  }
  buttons.forEach(function(b){b.addEventListener('click',function(){
    role=b.dataset.role; history.replaceState(null,'',role==='all'?location.pathname:'#role='+role); apply();
  });});
  if(search) search.addEventListener('input', apply);
  note.addEventListener('click',function(e){ if(e.target.hasAttribute('data-clear')){e.preventDefault(); role='all'; if(search) search.value=''; history.replaceState(null,'',location.pathname); apply();} });
  var m=location.hash.match(/role=([a-z-]+)/); if(m) role=m[1]; apply();
})();
</script>
<!-- /roles:js -->
"""


def build_index_filter():
    p = OUT / "index.html"
    s = p.read_text(encoding="utf-8")

    # CSS
    s = re.sub(r"/\* roles:css \*/.*?/\* /roles:css \*/\n", "", s, flags=re.S)
    s = s.replace("</style>", FILTER_CSS + "</style>", 1)

    # chips in the header
    chips = "".join(f'<button type="button" data-role="{rid}" data-name="{escape(name)}">{escape(name.split(" / ")[0])}</button>'
                    for rid, name, *_ in ROLES)
    bar = (f'<!-- roles:bar --><div class="rolebar"><span>I\'m a…</span><button type="button" data-role="all" '
           f'data-name="everyone">All tools</button>{chips}</div><!-- /roles:bar -->')
    s = re.sub(r"\n*<!-- roles:bar -->.*?<!-- /roles:bar -->\n", "\n", s, flags=re.S)
    s = s.replace("</div></header>", bar + "\n</div></header>", 1)

    # sticky section menu with search, built from the h2 ids in <main>
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', s)
    links = "".join(f'<a href="#{hid}" title="{name}">{SHORT.get(hid, name)}</a>' for hid, name in heads)
    nav = (f'<!-- roles:nav --><nav class="sections" aria-label="Sections"><div class="wrap"><div class="links">{links}</div>'
           f'<input type="search" placeholder="Search tools…" aria-label="Search tools"></div></nav><!-- /roles:nav -->')
    s = re.sub(r"<!-- roles:nav -->.*?<!-- /roles:nav -->\n", "", s, flags=re.S)
    s = s.replace("</div></header>\n", "</div></header>\n" + nav + "\n", 1)

    # note above the first section
    s = re.sub(r'<p class="rolenote"></p>\n', "", s)
    s = s.replace("<main><div class=\"wrap\">\n", "<main><div class=\"wrap\">\n<p class=\"rolenote\"></p>\n", 1)

    # data-roles on each card, the board-file link's plain label, and an "Example" link when the board has a worked example
    def tag(m):
        card_open, rest = m.group(1), m.group(2)
        href = re.search(r'class="primary" href="([^"]+)"', rest)
        roles = roles_for(href.group(1)) if href else None
        card_open = re.sub(r' data-roles="[^"]*"', "", card_open)
        if roles is not None:
            card_open = card_open[:-1] + f' data-roles="{" ".join(roles)}">'
        rest = re.sub(r'<a class="ex" href="worked-example-[^"]+">Example</a>', "", rest)
        rest = re.sub(r'<span class="tags" hidden>[^<]*</span>', "", rest)
        key = next((k for k, v in TOOLS.items() if href and v[1] == href.group(1)), None)
        if key in TAGS:
            rest = rest.replace('</div><div class="links">', f'<span class="tags" hidden>{TAGS[key]}</span></div><div class="links">', 1)
        rest = re.sub(r'<a href="([^"]+\.svg)"[^>]*>[^<]*</a>',
                      lambda v: f'<a href="{v.group(1)}" title="{escape(SVG_TIP)}">{SVG_LABEL}</a>', rest)
        if href and (OUT / f"worked-example-{href.group(1)}").exists():
            rest = re.sub(r'(<div class="links">.*?)(</div></div>\n)$',
                          lambda l: f'{l.group(1)}<a class="ex" href="worked-example-{href.group(1)}">Example</a>{l.group(2)}',
                          rest, flags=re.S)
        return card_open + rest
    s = re.sub(r'(<div class="card"[^>]*>)(.*?</div></div>\n)', tag, s, flags=re.S)

    # script
    s = re.sub(r"<!-- roles:js -->.*?<!-- /roles:js -->\n", "", s, flags=re.S)
    s = s.replace("</body>", FILTER_JS + "</body>", 1)

    p.write_text(s, encoding="utf-8")
    untagged = re.findall(r'<div class="card">', s)
    print(f"tagged index.html cards ({len(untagged)} untagged)")


if __name__ == "__main__":
    build_page()
    build_index_filter()
