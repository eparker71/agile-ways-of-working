<!--
Scenario Playbook: a running list of common situations and possible fixes.

To add a scenario, copy one of the entries below into the right area and edit it. Keep to this shape:

## The situation, in a few words
You'll notice: what people see or hear (optional, one line).
First moves:
- What to do this week.
Longer term:
- What to change so it happens less.
Tools: Tool Name, Another Tool Name

Tool names must match the toolkit's tool titles (see start-here-by-role.html). Then run:
    python3 _generator/build_scenarios.py
-->

# Delivery & deadlines

## The deadline has just been moved earlier
You'll notice: a new date arrives with the same scope, and the team goes quiet.
First moves:
- Re-forecast from the team's real throughput and show the range of likely dates.
- Ask what matters most by the new date, and offer scope options using MoSCoW.
- Agree which of scope, date or quality can flex, and write it down.
Longer term:
- Agree trade-off sliders at the start of each project.
- Keep the forecast up to date every iteration, so changes are a conversation, not a surprise.
Tools: Release Forecast & Burn-up, Prioritisation Board, Project Kickoff, Stakeholder Map

## The team missed its sprint goal
You'll notice: unfinished work, frustration, and pressure to "try harder".
First moves:
- Tell stakeholders early what will and won't be done.
- At the retrospective, look for causes without blame: capacity, unplanned work, item size or dependencies.
Longer term:
- Plan to the team's recent throughput, not hopes.
- Keep a buffer for unplanned work and split items smaller.
Tools: Retrospective Kit, Sprint Planning, Buffering & Swarming, Story Splitting

## Urgent work keeps interrupting the iteration
You'll notice: support requests and "quick favours" that never make it onto the board.
First moves:
- Put every interruption on the board and count them for two iterations.
- Agree an expedite policy: one urgent item at a time, and who can call one.
Longer term:
- Size a capacity buffer from the data you collected.
- Fix the biggest source of interruptions, such as poor quality or unclear support routes.
Tools: Buffering & Swarming, Kanban Board Design, Blocker Clustering

## A major incident hits in the middle of the iteration
You'll notice: everyone stops, and planned work stalls.
First moves:
- Swarm on recovery and pause new work.
- Keep stakeholders informed, and protect the people handling it.
Longer term:
- Run a blameless incident review within a week, and plan its actions in.
- Track recovery time and change failure rate.
Tools: Buffering & Swarming, Blameless Incident Review, Delivery Metrics & Tech Debt

## Leadership wants a single delivery date
You'll notice: requests for "just one date" and frustration with ranges.
First moves:
- Give a range with a confidence level, and the assumptions behind it.
- Explain what would move the date, and what the leaders could change to bring it in.
Longer term:
- Report the forecast and its trend every iteration in the same format.
Tools: Release Forecast & Burn-up, Outcome Status Report

## A fixed-price contract meets changing requirements
You'll notice: the contract lists features and a price, and every new idea becomes a change-request argument.
First moves:
- Agree with the customer which matters most: the date, the budget, or the exact feature list. Usually only one can be fixed.
- Order the contract's features by value, and deliver the most valuable ones first, so the money buys the most important work.
- Offer swaps instead of change requests: a new feature can replace one of similar size that hasn't been started.
Longer term:
- Write future contracts around outcomes and a capacity of work per period, with the right to stop early.
- Choose the approach per part of the work: fixed scope where it's truly known, iterative where it isn't.
Tools: Delivery Approach, Prioritisation Board, Project Kickoff, Release Forecast & Burn-up, RACI & Decision Log

## Lots of work is started but little is finished
You'll notice: everything is "nearly done", and the board's middle columns are full.
First moves:
- Walk the board right to left at the daily sync, and finish before starting.
- Swarm on the oldest items.
Longer term:
- Set WIP limits, track work item age, and agree a service level expectation.
Tools: Daily Sync, Kanban Board Design, Ageing WIP & SLE

## The project has grown from 5 to 40 people
You'll notice: decisions get lost, teams duplicate or undo each other's work, meetings multiply, and nobody can see the whole plan.
First moves:
- Split the work into small, stable teams of ten or fewer, each owning a clear part of the product.
- Start a weekly cross-team sync and a shared dependency map.
- Agree who decides what, and start a decision log.
Longer term:
- Plan together each planning period with shared objectives, and hold a joint demo and retro.
- Review your practices against the next level up, and drop the habits that no longer help.
Tools: Right-Size Your Structure, Cross-Team Planning, Cross-Team Sync, Dependency Map, RACI & Decision Log, Team Topology Design

## Releases are slow, scary and happen late at night
You'll notice: big releases every few weeks or months, long release meetings, people on standby, and changes held back "for the next release".
First moves:
- Map the delivery pipeline with the team and find where changes wait longest.
- Plan the next release with a tested rollback and an agreed go/no-go checklist.
- Try releasing one change behind a feature flag, switched on later.
Longer term:
- Release smaller batches, more often, until releases become routine.
- Automate the manual steps, starting with the one that causes most delay or errors.
Tools: Delivery Pipeline Canvas, Release Readiness & Strategy, Continuous Delivery Health Check, Delivery Metrics & Tech Debt

## Bugs keep reaching production
You'll notice: users find problems before the team does, hotfixes interrupt planned work, and testing happens in a rush at the end.
First moves:
- Look at recent escaped bugs: where could each have been caught earlier?
- Agree examples for the next few stories before coding starts.
- Fix or remove the flakiest tests, so a red build means something.
Longer term:
- Agree a test strategy, with most checks automated and low in the pyramid.
- Add the quality bar to the Definition of Done, and test hardest where risk is highest.
Tools: Test Strategy, Example Mapping, Root Cause Analysis, Blameless Incident Review

## Governance wants sign-off at every stage
You'll notice: work waits for approval boards and documents, teams batch changes to get through gates, and agile feels slowed down.
First moves:
- List each gate, the question it's really asking, and how long it takes.
- Invite governance or risk colleagues to a review, to see working software and evidence.
- Offer evidence from the pipeline (tests run, approvals, who deployed what) instead of documents.
Longer term:
- Agree risk-based approval, so small, routine changes go straight through.
- Build compliance checks into the Definition of Done and the pipeline.
Tools: SDLC at a Glance, Delivery Pipeline Canvas, Value Stream Map, Stakeholder Map

# Team

## A new person joins the team
You'll notice: they're unsure how things work, and the team slows down a little.
First moves:
- Walk them through the team charter and the Definition of Done.
- Pair them on real work in their first week.
Longer term:
- Add them to the skills matrix, and revisit the charter together: a new member means a slightly new team.
Tools: Team Onboarding, Team Charter, Pairing & Mobbing, Skills Matrix

## Two team members are in open conflict
You'll notice: tension in meetings, side conversations, or people avoiding each other.
First moves:
- Talk to each person privately and listen. Focus on interests, not positions.
- If they're willing, bring them together with a clear, neutral structure.
Longer term:
- Revisit the team's working agreements and how it makes decisions.
- Check how safe it feels to disagree openly.
Tools: Coaching Conversation, Team Charter, Psychological Safety Check

## A new team doesn't know where to start
You'll notice: lots of discussion, no shared plan, and nothing delivered yet.
First moves:
- Run a timeboxed team launch of one or two weeks.
- Agree the purpose, a first slice of work, and how the team will work together.
Longer term:
- Review the charter after the first month.
Tools: Team Launch (Sprint Zero), Team Charter, Product Vision Board

## Retrospectives have gone stale
You'll notice: the same people speak, the same issues come up, and actions don't happen.
First moves:
- Change the format, and start by reviewing the last retro's actions.
- Limit the outcome to one to three actions, each with an owner.
Longer term:
- Rotate the facilitator, and bring data such as health check results or blocker clusters.
Tools: Retrospective Kit, Facilitation Techniques, Team Health Check

## Morale is low and people seem disengaged
You'll notice: cameras off, short answers, and less energy than usual.
First moves:
- Ask people one to one how things are, and listen.
- Run a team health check or psychological safety check.
Longer term:
- Act visibly on one finding, and check workload and purpose.
Tools: Team Health Check, Coaching Conversation, Psychological Safety Check

## A key person is leaving
You'll notice: worry about who knows what, and a rush to "write everything down".
First moves:
- List what only they know, and pair others with them intensively before they go.
- Record important decisions and their reasons.
Longer term:
- Reduce single points of failure across the team.
Tools: Skills Matrix, Pairing & Mobbing, Architecture Decision Record

## Someone was shut down or embarrassed in a meeting
You'll notice: they go quiet afterwards, and others say less too.
First moves:
- Check in with the person privately, and listen.
- If you saw it, address it with the person who did it, privately and soon.
Longer term:
- Agree meeting norms in the team charter, and use structures that give everyone a voice.
Tools: Team Charter, Facilitation Techniques, Psychological Safety Check

## A leader reacts badly to bad news
You'll notice: problems stop being reported, or arrive late and softened.
First moves:
- Give the leader specific, private feedback on the effect their reaction had.
- Agree how bad news will be raised, and thank the next person who brings it.
Longer term:
- Coach leaders on responding productively, and report confidence rather than traffic lights.
Tools: Leading for Psychological Safety, Coaching Conversation, Outcome Status Report

## People hide mistakes until it's too late
You'll notice: problems surface at the last minute, with an "I didn't want to worry anyone".
First moves:
- Treat the next mistake that's raised with thanks and curiosity, publicly.
- Run a blameless review of the latest one.
Longer term:
- Make learning from mistakes a normal part of retrospectives, and check psychological safety regularly.
Tools: Blameless Incident Review, Leading for Psychological Safety, Psychological Safety Check

## Developers don't keep Jira up to date
You'll notice: tickets moved in a rush just before the stand-up or a report, stale statuses, and managers chasing people for updates. The same happens with any tracker, such as Azure DevOps or Trello.
First moves:
- Ask the team, without blame, what makes updating it a chore and who they think it's for.
- Run the Daily Sync from the board, walking it right to left, so updating happens in the meeting that uses it.
- Cut it down: remove fields and statuses nobody reads, and match the columns to how work really flows.
Longer term:
- Make the board useful to the team first (blockers, ageing work, WIP limits), and build reports from it, not the other way round.
- Agree in the team charter what "up to date" means and why, and stop using the data to judge individuals.
Tools: Jira Cheat Sheet, Azure DevOps Cheat Sheet, Kanban Board Design, Daily Sync, Team Charter

# Product & backlog

## Stakeholders keep adding work mid-iteration
You'll notice: new requests in chat, and the plan changing every few days.
First moves:
- Ask what the new work replaces, and show the goal and capacity.
- If it's truly urgent, let the product owner swap scope openly.
Longer term:
- Make one visible place for requests, and agree classes of service.
Tools: Sprint Planning, Kanban Board Design, Stakeholder Map

## The product owner is overloaded or rarely available
You'll notice: questions wait for days, and the team guesses.
First moves:
- Agree regular time with the product owner each week.
- Share story writing and refinement with the team.
Longer term:
- Make decision rights explicit, so the team can decide more on its own.
Tools: RACI & Decision Log, Delegation Board, Backlog Refinement

## Nobody can agree what to build next
You'll notice: long debates and the loudest voice winning.
First moves:
- Go back to the product vision and the outcome you're aiming for.
- Compare options by value and cost of delay, not opinion.
Longer term:
- Explore opportunities and test assumptions continuously.
Tools: Product Vision Board, Prioritisation Board, Opportunity Solution Tree

## A big request arrives with the solution already decided
You'll notice: "just build this" with a feature list and a date.
First moves:
- Ask what problem it solves and how you'd know it worked.
- Write it as a hypothesis with a measure, and find the smallest test.
Longer term:
- Help stakeholders bring problems and outcomes, not solutions.
Tools: Impact Map, Epic Breakdown Canvas, Opportunity Solution Tree

## Stories keep turning out bigger than expected
You'll notice: items carry over, and estimates are always low.
First moves:
- Split stories before planning, and map examples for the top items.
Longer term:
- Hold a regular refinement session, and aim for several small items per iteration.
Tools: Story Splitting, Example Mapping, Backlog Refinement

## Users aren't using what we built
You'll notice: low adoption, or features nobody mentions.
First moves:
- Talk to users, and look at the journey where they drop off.
- Check whether the outcome measure moved at all.
Longer term:
- Test assumptions before building, and measure value, not output.
Tools: Persona & Journey Map, Opportunity Solution Tree, Value Metrics

## We're a startup with months of runway and no proof anyone will pay
You'll notice: lots of building, a growing feature list, and no paying customers yet.
First moves:
- Write the idea as a bet: who has the problem, what you believe, and what would prove you wrong.
- Pick the riskiest assumption and test it this week, with a landing page, a call or a manual version, before writing code.
- Agree a stop rule now, while you're calm: what result by what date would make you change course.
Longer term:
- Run one small experiment at a time, and judge progress by paying, returning customers, not features shipped.
- Keep a light rhythm: a weekly look at the bets, and a monthly look back at what you learned.
Tools: Product Bet Canvas, Opportunity Solution Tree, 1% Experiment Canvas, Design Sprint

# Stakeholders & reporting

## Stakeholders don't come to the review
You'll notice: an empty room, or a demo to the team itself.
First moves:
- Ask the key stakeholders what would make the review worth their time.
- Show working product they can try, and ask for specific feedback.
Longer term:
- Map stakeholders and plan how each will be involved.
Tools: Sprint Review, Stakeholder Map

## The steering group wants traffic-light status
You'll notice: everything is green until it's suddenly red.
First moves:
- Offer a one-page outcome report with a confidence rating and trend.
- Bring the top risks and the decisions you need from them.
Longer term:
- Use the same report every time, so changes stand out.
Tools: Outcome Status Report, RAID Log

## The PMO wants a baseline schedule, but the team works in iterations
You'll notice: a request for a Gantt chart with dates for every feature, and a team that plans two weeks at a time.
First moves:
- Ask what the schedule is for: funding, dependencies, a launch date or reporting. Then give that, not a task list.
- Offer milestones with forecast ranges from real throughput, plus a Now, Next and Later view of the scope.
- Agree a reporting rhythm that uses the team's reviews and a one-page status report.
Longer term:
- Agree with the PMO which gates and evidence a hybrid project uses, and write it down once for every project.
- Plan in rolling waves: detail for the next few iterations, outline beyond that, re-forecast every iteration.
Tools: Delivery Approach, Release Forecast & Burn-up, Now · Next · Later Roadmap, Outcome Status Report, SDLC at a Glance

## A senior stakeholder keeps overriding priorities
You'll notice: the backlog order changes after every conversation with them.
First moves:
- Understand what they need and why; show the trade-off openly.
- Use cost of delay to make the comparison visible.
Longer term:
- Agree who decides priorities, and how others are consulted.
Tools: Stakeholder Map, Prioritisation Board, Delegation Board

# Multi-team

## Teams keep blocking each other
You'll notice: "we're waiting on team X" at every sync.
First moves:
- Make dependencies visible, and agree dates and owners for each.
- Hold a short cross-team sync focused on blockers.
Longer term:
- Remove recurring dependencies by changing team boundaries or skills.
Tools: Dependency Map, Cross-Team Sync, Team Topology Design

## Agile teams depend on a supplier who works to a fixed plan
You'll notice: the teams change direction every few weeks, but the supplier's plan and contract don't, and hand-offs keep slipping.
First moves:
- Map the dependencies on the supplier, with dates, and agree the few that really drive the plan.
- Agree a stable interface or contract between the parts early, so each side can change behind it.
- Invite the supplier to cross-team planning and the review, even if they plan differently.
Longer term:
- Choose an approach for each part on purpose, and agree milestones where they meet.
- Reduce the dependency over time: bring the knowledge in-house, or use stubs and contract tests.
Tools: Delivery Approach, Dependency Map, Cross-Team Planning, RAID Log, Stakeholder Map

## Several teams need to plan together for the first time
You'll notice: separate plans that don't fit, and surprises late in the quarter.
First moves:
- Agree a few shared objectives, then let teams plan their own work against them.
- Make dependencies and risks visible, and take a confidence vote.
Longer term:
- Set up a regular rhythm of multi-team events.
Tools: Cross-Team Planning, Objectives & Key Results, Events & Cadences

## One team is overloaded while another waits
You'll notice: one team is the bottleneck for everyone else.
First moves:
- Map the value stream, and see where the work queues.
- Check the overloaded team's cognitive load.
Longer term:
- Move work, skills or responsibilities to balance the flow.
Tools: Value Stream Map, Team Topology Design, Cross-Team Sync

## The same cross-team problem repeats every quarter
You'll notice: it's on every retro, and nobody owns it.
First moves:
- Hold a cross-team retrospective and pick that one problem.
- Find the root cause with people from every team involved.
Longer term:
- Give the fix an owner and plan it into the next period.
Tools: Cross-Team Retro, Root Cause Analysis

# Leadership & change

## Leadership wants to "go agile" across the organisation
You'll notice: a mandate, a date, and worried teams.
First moves:
- Agree why: the outcomes the change should achieve, and how you'll measure them.
- Start with a few willing teams, and learn from them.
Longer term:
- Treat it as change for people, not just a new process.
Tools: Value Metrics, ADKAR Change Readiness, Team Topology Design, Events & Cadences

## We've been told to move to a product operating model
You'll notice: a reorganisation announced from the top, project managers being retitled product managers, and nobody sure what will actually change.
First moves:
- Ask what problem the change should solve, such as slow decisions or building things nobody uses, and write it down.
- Score the six shifts on the Product Operating Model poster together, and tick the signs that it's only a rename.
- Pick the one shift that would help most and is within your control, and start small.
Longer term:
- Bring finance in early: if money still arrives project by project, teams will still behave like projects.
- Give product managers time and coaching for discovery, and give teams problems and outcomes, not feature lists.
Tools: Product Operating Model, Portfolio Kanban & Investment Mix, Team Topology Design, Objectives & Key Results, Delegation Board

## A change is meeting resistance
You'll notice: people agree in meetings, then carry on as before.
First moves:
- Find where each group is stuck: awareness, desire, knowledge, ability or reinforcement.
- Act on that barrier first.
Longer term:
- Keep reinforcing and measuring adoption well after launch.
Tools: ADKAR Change Readiness, Stakeholder Map, Coaching Conversation

## Too many projects are running at once
You'll notice: everything is a priority, and nothing finishes.
First moves:
- Put every initiative on one board and count how many are in progress.
- Pause or stop some, so the rest can finish.
Longer term:
- Set portfolio WIP limits, and agree an investment mix.
Tools: Portfolio Kanban & Investment Mix, Value Metrics

## Teams wait for managers to make decisions
You'll notice: work stalls until the right person is free.
First moves:
- List the decisions that cause the most waiting.
- Agree the delegation level for each, with guardrails.
Longer term:
- Move one decision area up a level every few months.
Tools: Delegation Board, RACI & Decision Log

## The team is asked to start using AI tools
You'll notice: excitement, worry, and no shared rules.
First moves:
- Agree where AI helps, where it needs care, and the guardrails.
- Check your organisation's policy and approved tools.
Longer term:
- Measure the impact on quality as well as speed, and review the agreement often.
Tools: AI Working Agreement, Delivery Metrics & Tech Debt

# Remote & hybrid

## Remote people go quiet in hybrid meetings
You'll notice: the room talks, and remote people listen.
First moves:
- Have everyone join from their own device, even in the room.
- Use silent writing on a shared board, then round-robins.
Longer term:
- Name a facilitator for every meeting, and check in on inclusion at retros.
Tools: Facilitation Techniques, Daily Sync, Psychological Safety Check

## The team is spread across time zones
You'll notice: decisions made while half the team is asleep.
First moves:
- Agree a daily overlap window, and keep it for conversations that need everyone.
- Write decisions down, with the reasons.
Longer term:
- Make more work asynchronous, and record it in the team's working agreements.
Tools: Team Charter, RACI & Decision Log, Daily Sync
