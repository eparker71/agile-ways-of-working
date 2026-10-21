"""The Basket team's story: every worked example in the order it happened.

STORY is (month, chapter name, [(sort key, date shown, tool key, what happened)]). Dates match the ones written on the
examples; where an example has none, the date here fits the story around it. build_recipes.py turns it into
basket-team-story.html, and build_boards.py uses its order for the previous / next links on each worked example.
"""

STORY = [
    ("February", "Getting started", [
        ("02-03", "3 Feb", "kickoff", "The Head of Digital sponsors “Reorder made easy”: repeat orders from 22% to 30% by the end of June, with only the campaign date fixed."),
        ("02-05", "5 Feb", "stakeholder", "Eleven stakeholders go on the map. Store Ops and Legal could block it, so they get the closest attention."),
        ("02-06", "6 Feb", "vision", "Priya writes the vision: busy households get their weekly shop done in two minutes."),
        ("02-10", "10 Feb", "persona", "Twelve interviews become Sarah, 38, who rebuilds the same basket on her phone every Sunday night."),
        ("02-12", "12 Feb", "ost", "One outcome, three opportunities, six solutions. A fake-door button shows 31% of customers want one-tap reorder."),
        ("02-18", "18 Feb", "epic", "The epic as a hypothesis, with an MVP: a last-order card and one-tap reorder for 10% of customers."),
        ("02-20", "20 Feb", "impact", "Families, pickers and customer service each need to behave differently; each gets a deliverable."),
        ("02-24", "24 Feb", "topology", "Four teams mapped by type. Checkout is carrying too much, and every release waits for Payments."),
        ("02-28", "17–28 Feb", "launch", "A two-week launch: charter drafted, backlog ready, and the last-order card running on staging."),
    ]),
    ("March", "Forming the team", [
        ("03-03", "3 Mar", "team-charter", "The Basket team agrees its purpose, values, working agreements and Definitions of Ready and Done."),
        ("03-03b", "3 Mar", "sprint-planning", "Sprint 14's goal: returning customers see their last order and reorder it in one tap."),
        ("03-05", "5 Mar", "user-manual", "Priya, Sam, Jo and Mei write how to work with them: focus time, feedback, what drains them."),
        ("03-07", "7 Mar", "storymap", "The reorder journey, sliced into an MVP, a second release and later."),
        ("03-10", "10 Mar", "prioritisation", "Cost of delay ranks reorder first and subscriptions third; the Now · Next · Later plan follows."),
        ("03-12", "12 Mar", "example", "“Reorder last basket” has four rules and three open questions, so it's split into two stories."),
        ("03-14", "14 Mar", "retro", "Sprint 14's retro: stop starting new work while items are blocked; try Example Mapping before planning."),
        ("03-17", "17 Mar", "onboarding", "Ravi joins, with Alex as his buddy and a first week that ends with something shipped."),
        ("03-20", "20 Mar", "skills", "The skills matrix shows two single points of failure: only Sam knows payments, only Priya knows the data."),
        ("03-28", "28 Mar", "health", "End of the quarter: releases and waiting on other teams are the two areas to fix."),
    ]),
    ("April", "Delivering, and the first knocks", [
        ("04-01", "1 Apr", "ctp", "Five teams plan the quarter together around three shared objectives; confidence vote: 4."),
        ("04-01b", "1 Apr", "okr", "Three objectives for Q2, from effortless weekly shops to a quicker, trustworthy checkout."),
        ("04-02", "2 Apr", "kanban", "The team redesigns its board: seven columns, WIP limits and exit policies."),
        ("04-02b", "2 Apr", "ai", "The team agrees where AI helps, where it's off limits, and how its output is reviewed."),
        ("04-09", "9 Apr", "incident", "Saturday 5 April: checkout fails for four hours. The blameless review finds no alert on certificate errors."),
        ("04-11", "11 Apr", "experiment", "Example Mapping before planning worked: rework fell from 4 in 9 stories to 1 in 10."),
        ("04-14", "14 Apr", "bet", "The staples subscription bet: test it by hand with 50 customers before building anything."),
        ("04-15", "15 Apr", "event-storming", "An order from reorder to delivery, mapped with Store Ops and Payments; three hotspots surface."),
        ("04-22", "22 Apr", "dependency", "Five dependencies across six teams; the Stock API that substitutes need is at risk."),
        ("04-23", "23 Apr", "psych-safety", "An anonymous check: problems are raised one to one, not in the room, so the team tries silent writing."),
        ("04-25", "25 Apr", "delegation", "Eight decision areas, and where each is heading; spending decisions move to the team in July."),
        ("04-28", "28 Apr", "raid", "The RAID log: repeat billing is the biggest risk, the Stock API the dependency at risk."),
    ]),
    ("May", "Under pressure", [
        ("05-01", "1 May", "lean-coffee", "The team's own agenda: they'll try counting items instead of story points for two iterations."),
        ("05-05", "5 May", "blockers", "April's blockers clustered: sign-offs cost 12 of 24 blocked days, so that's the one to fix."),
        ("05-06", "6 May", "daily", "Six days left in Sprint 18. Substitutes are blocked on the Stock API, so two people swarm on it."),
        ("05-06b", "6 May", "refinement", "Five items taken through order, understand, split, examples, size and ready."),
        ("05-06c", "6 May", "estimation", "Planning poker converges on most items; substitutes come out an 8, so they're split."),
        ("05-06d", "6 May", "sync", "Five teams in 20 minutes: the Stock API is escalated, and release checks are agreed."),
        ("05-06e", "6 May", "portfolio-kanban", "Twelve initiatives, WIP limits, and an investment mix that's drifted from what was agreed."),
        ("05-08", "8 May", "vsm", "From story to live takes 16 days, and only 3 of them are work. The longest wait is before building starts."),
        ("05-08b", "8 May", "adr", "ADR 007: read stock levels from a replica behind an adapter, and switch to the API when it ships."),
        ("05-09", "9 May", "sprint-review", "Sprint 18 met its goal partly; stakeholders want substitutes, and Finance worries about margins."),
        ("05-09b", "9 May", "forecast", "29 items done, 14 left, with scope still growing: likely finish 13–20 June."),
        ("05-09c", "9 May", "status", "Amber: reorder is live and repeat orders are at 25%, but substitutes are an iteration late."),
        ("05-09d", "9 May", "value", "Value metrics across the four areas: faster and more valued, but blocked time is rising."),
        ("05-09e", "9 May", "raci", "Who does what for the subscriptions pilot, and three decisions logged, including ADR 007."),
        ("05-09f", "9 May", "buffer", "A 20% buffer, sized from five sprints of unplanned work, and swarm triggers with real numbers."),
        ("05-09g", "9 May", "ageing", "Three items are past the 9-day SLE; the oldest gets swarmed today."),
        ("05-12", "12 May", "cynefin", "Will customers accept substitutes? It's complex, so three safe-to-fail experiments, not a big design."),
        ("05-12b", "12 May", "pairing", "A pair stair for seven people, and the skills from the matrix spread by pairing."),
        ("05-12c", "12 May", "motivation", "Jo ranks ten motivators against a change: learning payments by pairing with Sam."),
        ("05-12d", "12 May", "impediments", "Impediments from new to resolved, with an escalation ladder and what each one cost."),
        ("05-13", "13 May", "coaching", "Tom coaches Alex on raising test risks earlier; Alex commits to one “what if…?” per refinement."),
        ("05-14", "14 May", "delivery-metrics", "Faster and more stable since self-service deploys; five technical debts placed in the quadrant."),
        ("05-14b", "14 May", "rootcause", "Old promo prices in reordered baskets, traced to copied price rules with no owner."),
        ("05-15", "15 May", "cadences", "Meanwhile the Store Platform team, working in flow, reviews its service against SLEs."),
        ("05-15b", "15 May", "pipeline", "Seven pipeline stages: changes wait four hours for review and a day for release."),
        ("05-16", "16 May", "testing", "What each level of the pyramid tests, seven quality gates, and where to test hardest."),
        ("05-16b", "16 May", "cd-health", "Twelve practices scored: 39 out of 60, up from 33, with flaky tests and monitoring the gaps."),
        ("05-20", "20 May", "premortem", "It's 1 October and the subscriptions pilot has failed. Why? Repeat billing tops the list."),
        ("05-21", "21 May", "adkar", "Rolling substitutes out to store pickers: each group's barrier point, and what to do about it."),
    ]),
    ("June", "Shipping", [
        ("06-02", "2 June", "release", "Substitutes 1.0 switches on in one store, behind a feature flag, with a tested rollback."),
        ("06-06", "6 June", "roadmap", "The roadmap after the pilot: substitutes everywhere now; subscriptions next, if the pilot works."),
        ("06-13", "9–13 June", "design-sprint", "Five days on staples subscriptions: four of five customers set it up, but skipping a week was hard."),
        ("06-20", "20 June", "ai-delivery", "The group agrees where AI fits at each stage, how much it does alone, and who's accountable."),
        ("06-27", "27 June", "cross-retro", "Five teams look back on the quarter: the top cross-team problem was waiting on the Stock API."),
    ]),
    ("July", "Finishing well", [
        ("07-04", "4 July", "closeout", "Repeat orders reached 29%, nearly the 30% target. The team hands over, thanks people and records what it learned."),
    ]),
]


def story_order():
    """(tool key, date shown, month) for every step, in story order."""
    return [(k, date, month) for month, _, items in STORY for _, date, k, _ in sorted(items)]
