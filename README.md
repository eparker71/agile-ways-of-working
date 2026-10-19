# Agile Facilitation Toolkit

Printable boards and facilitator guides for teams and facilitators.

**Live site:** https://eparker71.github.io/my_agile_tools/

To browse everything locally, open `index.html`.

Each board comes as:
- **`.html`**: view in a browser or print. Boards print at A3 landscape; guides print at A4 portrait.
- **`.svg`**: import into Miro, Mural or FigJam as a locked background.

Every board page has a **Facilitator guide →** link (hidden when printing), and every guide links back to its boards.

## Tools and their guides

| Tool | Board files | Guide |
|---|---|---|
| Marginal Gains Workshop | `marginal-gains-workshop-board-sprint`, `-quarter` | `facilitator-guide-marginal-gains.html` |
| 1% Experiment Canvas | `experiment-canvas` | `facilitator-guide-experiment-canvas.html` |
| Team Health Check | `team-health-check-board` | `facilitator-guide-team-health-check.html` |
| Lean Coffee | `lean-coffee-board` | `facilitator-guide-lean-coffee.html` |
| Retro: Start · Stop · Continue | `retro-board-start-stop-continue-sprint`, `-quarter` | `facilitator-guide-retro-start-stop-continue.html` |
| Retro: The 4 Ls | `retro-board-4ls-sprint`, `-quarter` | `facilitator-guide-retro-4ls.html` |
| Retro: Mad · Sad · Glad | `retro-board-mad-sad-glad-sprint`, `-quarter` | `facilitator-guide-retro-mad-sad-glad.html` |
| Retro: Sailboat | `retro-board-sailboat-sprint`, `-quarter` | `facilitator-guide-retro-sailboat.html` |
| Epic Breakdown Canvas | `epic-breakdown-canvas` | `facilitator-guide-epic-breakdown-canvas.html` |
| User Story Map | `story-map-board` | `facilitator-guide-story-map.html` |
| Story Splitting poster | `story-splitting-poster` | `facilitator-guide-story-splitting.html` |
| Example Mapping | `example-mapping-board` | `facilitator-guide-example-mapping.html` |
| Team Charter | `team-charter-board` | `facilitator-guide-team-charter.html` |
| Product Vision Board | `product-vision-board` | `facilitator-guide-product-vision.html` |
| Prioritisation Board | `prioritisation-board` | `facilitator-guide-prioritisation.html` |
| Sprint Planning | `sprint-planning-board` | `facilitator-guide-sprint-planning.html` |
| Sprint Review | `sprint-review-board` | `facilitator-guide-sprint-review.html` |
| Project Kickoff | `project-kickoff-board` | `facilitator-guide-project-kickoff.html` |
| Stakeholder Map | `stakeholder-map-board` | `facilitator-guide-stakeholder-map.html` |
| Release Forecast & Burn-up | `release-forecast-board` | `facilitator-guide-release-forecast.html` |
| RAID Log | `raid-log-board` | `facilitator-guide-raid-log.html` |
| Pre-mortem | `pre-mortem-board` | `facilitator-guide-pre-mortem.html` |
| Root Cause Analysis | `root-cause-board` | `facilitator-guide-root-cause.html` |
| Objectives & Key Results | `okr-board` | `facilitator-guide-okr.html` |
| Cross-Team Planning | `cross-team-planning-board` | `facilitator-guide-cross-team-planning.html` |
| Dependency Map | `dependency-map-board` | `facilitator-guide-dependency-map.html` |
| Cross-Team Sync | `cross-team-sync-board` | `facilitator-guide-cross-team-sync.html` |
| Buffering & Swarming | `buffering-swarming-board` | `facilitator-guide-buffering-swarming.html` |
| Kanban Board Design | `kanban-board-design` | `facilitator-guide-kanban-board-design.html` |
| Ageing WIP & SLE | `ageing-wip-board` | `facilitator-guide-ageing-wip.html` |
| Blocker Clustering | `blocker-clustering-board` | `facilitator-guide-blocker-clustering.html` |
| Skills Matrix | `skills-matrix-board` | `facilitator-guide-skills-matrix.html` |
| Impediments Board | `impediments-board` | `facilitator-guide-impediments.html` |
| Pairing & Mobbing | `pairing-mobbing-board` | `facilitator-guide-pairing-mobbing.html` |
| Scrum Master & Agile Coach Cheat Sheet | `scrum-master-agile-coach-cheat-sheet.html` (two-sided A3, print double-sided) | Self-documenting reference; links to every board |
| Jira Cheat Sheet | `jira-cheat-sheet.html` (one-sided A3, Jira Cloud) | Self-documenting reference; companion to the cheat sheet above |

Each guide covers: when to use the tool, an at-a-glance summary, a prep checklist, a timed run-sheet (with sprint and quarter timings for retros), prompts for each section of the board, facilitation tips, common pitfalls, follow-up, and how the tool fits the rest of the toolkit.

## How the tools fit together

The toolkit follows the agile lifecycle and doesn't assume any one framework:

| Phase | Tools |
|---|---|
| Form the team | Team Charter |
| Envision | Product Vision Board |
| Plan | Prioritisation Board, then the break-down tools below |
| Build in iterations | Sprint Planning, Example Mapping, the cheat sheets |
| Review | Sprint Review |
| Reflect and improve | Retrospective Kit, Team Health Check, Marginal Gains Workshop, 1% Experiment Canvas, Root Cause Analysis |

Two further sets sit around that loop:

- **Run a project:** Project Kickoff, Stakeholder Map, Pre-mortem, Release Forecast & Burn-up, RAID Log.
- **Coordinate teams (program level):** Objectives & Key Results, Cross-Team Planning, Dependency Map, Cross-Team Sync.
- **Manage flow:** Kanban Board Design, Ageing WIP & SLE, Buffering & Swarming, Blocker Clustering, Skills Matrix, Impediments Board, Pairing & Mobbing.

**Diagnose** (Team Health Check) → **Explore** (Marginal Gains Workshop) → **Experiment** (1% Experiment Canvas) → **Reflect** (Retrospective Kit), then back round again. Lean Coffee is a general-purpose facilitation format that can be used at any point.

**Breaking down work** goes from big to small: Epic Breakdown Canvas (idea → MVP → features) → User Story Map (journey → release slices) → Story Splitting (stories small enough for a sprint) → Example Mapping (is each story understood and ready?).

## Editing and regenerating

Most files are generated by two scripts. Edit the scripts rather than the generated files, because edits to generated files are overwritten on the next run.

```sh
python3 _generator/build_boards.py   # all boards except Marginal Gains (SVG + HTML)
python3 _generator/build_guides.py   # all guides except Marginal Gains
```

- `build_boards.py` holds the shared visual components (header, panels, sticky zones, action cards, footer). Retro boards are built for each horizon in the `("sprint", "quarter")` list at the bottom.
- `build_guides.py` holds each guide's content in the `GUIDES` list. It copies its styling from `facilitator-guide-marginal-gains.html`.
- These files are hand-written and are not overwritten by the scripts: the Marginal Gains boards, `facilitator-guide-marginal-gains.html`, `scrum-master-agile-coach-cheat-sheet.html`, `jira-cheat-sheet.html` and `index.html`.

When you add a new board, also add a guide entry to `GUIDES` and a card to `index.html`.
