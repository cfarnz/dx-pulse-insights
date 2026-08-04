# DX Pulse Insights

A prototype of the product I'd be pitching to build: it takes raw, self-reported developer
survey comments — the messy open-text kind, not a clean spreadsheet — and turns them into a
leadership-ready digest across the three dimensions of developer experience defined in Abi
Noda, Nicole Forsgren, Margaret-Anne Storey, and Michaela Greiler's DevEx framework
(*DevEx: What Actually Drives Productivity*, ACM Queue, 2023): **feedback loops, cognitive
load, and flow state**.

Built for a real pitch: DX's Self-Reported Insights product — the survey/experience side of
their platform, not the system-telemetry side. This tool is scoped to exactly that boundary
and says so explicitly, because a self-reported comment shouldn't be dressed up as a system
metric. That's the same anti-hype standard DX's own founder writes about — real signal, no
inflated claims.

> **Why this exists:** the actual skill being demonstrated isn't survey tagging — it's the
> move I've made for years in operator roles at Capital One and CU Anschutz: take messy
> qualitative input (MBR/QBR prep, stakeholder feedback, field reports) and turn it into a
> narrative leadership can act on. This is that same move, pointed at the product surface I'd
> be hired to own.

---

## What's here
| File | Role |
|---|---|
| `devex_framework.md` | **The differentiator.** The codified DevEx framework — three dimensions, tagging rules — drawn directly from the source paper. |
| `sample_responses.md` | 18 simulated pulse-survey comments — realistic friction, realistic praise, a few with no real signal (deliberately, to test restraint). |
| `ANSWER_KEY.md` | The eval set — expected tags per comment, for grading the tool's output. |
| `pulse_insights.py` | The engine — tags each comment against the framework via Claude, then synthesizes a leadership digest. |
| `report.md` | Generated output — the digest itself. |

## Run it
```bash
pip3 install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # from console.anthropic.com/settings/keys
python3 pulse_insights.py
```

Outputs `report.md`: a per-response tagging summary, followed by a leadership digest —
dimension-by-dimension narrative, real quotes as evidence, and exactly one recommended focus
area (not a wishlist of everything that could be improved).

## Scope, on purpose
This tool only handles the self-reported half of DevEx measurement. The paper it's built on
is explicit that perceptual data and system telemetry each tell only half the story — this
prototype doesn't pretend otherwise. Swap `sample_responses.md` for a real survey export and
it works the same way; it does not, and shouldn't, try to infer build times or deploy
frequency from comment text.
