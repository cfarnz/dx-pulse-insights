# DevEx Framework (Self-Reported)

Source: Noda, Forsgren, Storey & Greiler, "DevEx: What Actually Drives Productivity,"
ACM Queue, 2023. This tool applies their three-dimension model to raw, self-reported
developer survey comments, the "voice of the developer" half of DevEx measurement rather than
system telemetry. Do not infer or fabricate system-level metrics from comment text; tag only
what the developer actually said.

## The three dimensions

### 1. Feedback loops
The speed and quality of responses to actions developers take: waiting on builds, tests,
CI, code review, or approvals. Fast feedback loops let developers keep moving; slow ones
force context switches, waiting, or abandoning the task.

Signals to listen for: build/test/CI wait times, review turnaround, deploy pipeline
friction, approval bottlenecks, "waiting on," "blocked by," "sits in review."

### 2. Cognitive load
The amount of mental effort required to do a task, driven by complexity, unfamiliar
systems, poor documentation, or badly organized code. High cognitive load means developers
spend effort just holding the system in their head instead of solving the actual problem.

Signals to listen for: complaints about undocumented or poorly organized code, unclear
ownership, too many tools/systems to track, steep ramp-up on unfamiliar areas, "I have to
remember," "hard to find," "not sure who owns this," "context switching."

### 3. Flow state
The mental state of energized, focused immersion in work, and what disrupts it.
Interruptions, unplanned work, excessive meetings, and lack of autonomy over how work is
structured all work against flow; clear goals and uninterrupted blocks of time support it.

Signals to listen for: meeting load, interruptions, unplanned/ad hoc work breaking focus,
Slack/ping fatigue, "in the zone," "can't get heads-down time," "constant interruptions,"
autonomy over task structure.

## Tagging rules

- A single comment can touch more than one dimension. Tag all that genuinely apply, but do
  not force a tag onto a dimension the comment doesn't actually speak to.
- Sentiment is independent of dimension: a comment can be positive ("code review turnaround
  is great now") and still tag to a dimension (feedback loops).
- Do not invent a fourth dimension or a KPI/North-Star metric. This framework is scoped to
  the three dimensions only, applied to self-reported perceptions.
- Quote the developer's own words when identifying the theme; don't paraphrase away the
  specific complaint or praise.
