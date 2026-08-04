# Answer Key — expected tags for `sample_responses.md`

For grading `pulse_insights.py` output. "Dimensions" lists every dimension a reasonable
reader should tag; primary dimension listed first. Sentiment is the tool's read of that
specific comment, not the respondent's mood in general.

| # | Dimension(s) | Sentiment | Note |
|---|---|---|---|
| 1 | Feedback loops | Negative | Slow CI, PR sits overnight |
| 2 | Feedback loops | Positive | Fast review turnaround, credits the SLA |
| 3 | Cognitive load | Negative | Stale ownership docs post-reorg |
| 4 | Cognitive load | Negative | Too many tools to hold in memory |
| 5 | — | Neutral | No real signal, don't force a tag |
| 6 | Flow state | Positive | No-meeting day protected focus time |
| 7 | Flow state | Negative | Meeting/interruption load kills heads-down time |
| 8 | Feedback loops | Negative | Flaky test suite, workaround not fix |
| 9 | — | Neutral | No real signal |
| 10 | Cognitive load | Positive | Better docs cut ramp-up time |
| 11 | Feedback loops (+ Cognitive load) | Negative | Approval bottleneck; secondary: unclear sign-off order |
| 12 | — | Positive (general) | No specific dimension signal, don't force a tag |
| 13 | Flow state | Negative | Unplanned triage breaks focus, cost of context switch |
| 14 | Cognitive load | Negative | Outdated onboarding docs, long setup |
| 15 | Feedback loops | Positive | Reliable, fast deploys |
| 16 | Feedback loops (+ Cognitive load) | Negative | Spec changes surface too late, causes rework |
| 17 | — | Neutral | No real signal |
| 18 | Cognitive load | Positive | Tool consolidation reduces context-juggling |

**Grading note:** don't expect exact match on secondary dimensions or exact wording — check
that the *primary* dimension and sentiment are right, and that responses 5, 9, 12, and 17
aren't forced into a dimension they don't actually speak to. That restraint (not manufacturing
signal from noise) is the actual thing being tested here.
