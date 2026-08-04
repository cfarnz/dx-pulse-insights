#!/usr/bin/env python3
"""
DX Pulse Insights
------------------
Takes raw, self-reported developer survey comments and turns them into a leadership-ready
digest across the three DevEx dimensions (feedback loops, cognitive load, flow state), per
Noda/Forsgren/Storey/Greiler's DevEx framework (ACM Queue, 2023). Self-report only, by design
— no system telemetry is inferred or fabricated from comment text.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python pulse_insights.py
    python pulse_insights.py --responses sample_responses.md --framework devex_framework.md --out report.md
    python pulse_insights.py --model claude-haiku-4-5-20251001   # cheaper, for scale

The framework is the real work — see devex_framework.md. The model just applies it
consistently, the same way a rubric-driven review pipeline would.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

try:
    import anthropic
except ImportError:
    sys.exit("Missing dependency. Run:  pip install anthropic")

# Sonnet is the default: strong judgment at low cost — the right call for tagging survey
# comments at scale. Swap to Haiku to show the cost story, or Opus for the synthesis step.
DEFAULT_MODEL = "claude-sonnet-4-6"

TAG_SYSTEM_PROMPT = """You are tagging self-reported developer survey comments against a \
given DevEx framework. You apply only the dimensions defined in the framework — you do not \
invent a fourth dimension or infer system metrics the comment doesn't state. If a comment has \
no real signal for any dimension, tag it with an empty dimensions list rather than forcing a \
fit. Return only the requested JSON."""

TAG_USER_TEMPLATE = """Here is the DevEx framework:

<framework>
{framework}
</framework>

Tag this single survey comment:

<comment role="{role}">
{body}
</comment>

Return ONLY a JSON object, no prose, in exactly this shape:
{{
  "dimensions": ["feedback_loops" | "cognitive_load" | "flow_state", ...],
  "sentiment": "positive" | "negative" | "neutral",
  "theme": "a short label for what's actually being said, e.g. 'slow CI turnaround'",
  "quote": "the exact words from the comment that carry the signal"
}}
A comment with no real dimensional signal returns an empty "dimensions" array and \
"sentiment":"neutral"."""

SYNTH_SYSTEM_PROMPT = """You are a product manager writing a leadership-ready digest of a \
developer experience pulse survey for engineering leadership. You write in the register of \
an honest operator, not a hype AI product: real gains and real friction, no inflated claims, \
no manufacturing urgency where the data doesn't support it. You group findings under the \
three DevEx dimensions (feedback loops, cognitive load, flow state), you use the developers' \
own words as evidence, and you close with exactly one clear recommendation for where to focus \
next — not a list of everything that could be improved."""

SYNTH_USER_TEMPLATE = """Here are this quarter's tagged pulse survey comments, grouped by \
dimension, with sentiment and supporting quotes:

<tagged_data>
{tagged_data}
</tagged_data>

Write a leadership digest in markdown with this shape:
1. A one-paragraph overview: overall sentiment read, most notable pattern.
2. One section per DevEx dimension that has signal (skip dimensions with no real data) — a \
short narrative synthesis plus 1-3 representative quotes per section.
3. A closing "Where to focus next" section: exactly ONE recommended area, with a one-sentence \
rationale grounded in what the data actually shows. Do not hedge with multiple recommendations.

Do not fabricate statistics (response counts, percentages) beyond what's directly countable \
from the tagged data provided."""

RESPONSE_RE = re.compile(r"^##\s*RESPONSE\s*\d*\s*:?\s*(.*)$", re.IGNORECASE | re.MULTILINE)


def parse_responses(md: str):
    """Split the responses file into (role, body) pairs on '## RESPONSE N: role' headers."""
    matches = list(RESPONSE_RE.finditer(md))
    responses = []
    for i, m in enumerate(matches):
        role = m.group(1).strip() or f"Respondent {i + 1}"
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        body = md[start:end].strip()
        if body:
            responses.append((role, body))
    return responses


def extract_json(text: str) -> dict:
    """Pull the JSON object out of the model response, tolerating any stray prose."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def tag_response(client, model, framework, role, body) -> dict:
    """Send one survey comment + the framework to Claude and return the parsed tags."""
    message = client.messages.create(
        model=model,
        max_tokens=500,
        system=TAG_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": TAG_USER_TEMPLATE.format(framework=framework, role=role, body=body),
        }],
    )
    return extract_json(message.content[0].text)


def synthesize_digest(client, model, tagged: list) -> str:
    """Group tagged comments by dimension and ask Claude to write the leadership digest."""
    by_dimension = defaultdict(list)
    for r in tagged:
        tag = r["tag"]
        for dim in tag.get("dimensions", []):
            by_dimension[dim].append({
                "role": r["role"], "sentiment": tag.get("sentiment"),
                "theme": tag.get("theme"), "quote": tag.get("quote"),
            })

    tagged_data = json.dumps(dict(by_dimension), indent=2)
    message = client.messages.create(
        model=model,
        max_tokens=2000,
        system=SYNTH_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": SYNTH_USER_TEMPLATE.format(tagged_data=tagged_data),
        }],
    )
    return message.content[0].text


def build_report(responses_count, tagged, digest, model) -> str:
    """Render the tagging summary table + the synthesized leadership digest."""
    dim_counts = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})
    untagged = 0
    for r in tagged:
        tag = r["tag"]
        dims = tag.get("dimensions", [])
        if not dims:
            untagged += 1
        for dim in dims:
            dim_counts[dim][tag.get("sentiment", "neutral")] += 1

    lines = [
        "# DX Pulse Insights — Leadership Digest",
        f"_Generated {datetime.now():%Y-%m-%d %H:%M} · model: {model} · self-reported data only_",
        "",
        f"**{responses_count} responses tagged · {untagged} with no dimensional signal**",
        "",
        "## Tagging summary",
        "",
        "| Dimension | Positive | Negative | Neutral |",
        "|---|---|---|---|",
    ]
    for dim in ("feedback_loops", "cognitive_load", "flow_state"):
        c = dim_counts[dim]
        lines.append(f"| {dim.replace('_', ' ').title()} | {c['positive']} | {c['negative']} | {c['neutral']} |")

    lines += ["", "---", "", digest]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Turn self-reported dev survey comments into a leadership digest.")
    ap.add_argument("--responses", default="sample_responses.md")
    ap.add_argument("--framework", default="devex_framework.md")
    ap.add_argument("--out", default="report.md")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "No ANTHROPIC_API_KEY found.\n"
            "Get one at https://console.anthropic.com/settings/keys, then:\n"
            "    export ANTHROPIC_API_KEY=sk-ant-...\n"
            "and re-run.  (The framework, sample data, and code are all ready — this is the only step.)"
        )

    framework = open(args.framework).read()
    responses = parse_responses(open(args.responses).read())
    if not responses:
        sys.exit(f"No responses found in {args.responses} (expected '## RESPONSE N: role' headers).")

    client = anthropic.Anthropic()
    print(f"Tagging {len(responses)} responses with {args.model}...\n")

    tagged = []
    for i, (role, body) in enumerate(responses, 1):
        try:
            tag = tag_response(client, args.model, framework, role, body)
        except Exception as e:  # keep the batch alive if one response fails
            tag = {"dimensions": [], "sentiment": "neutral", "theme": f"ERROR: {e}", "quote": ""}
        dims = ", ".join(tag.get("dimensions", [])) or "no signal"
        print(f"  {i}. {role} — {dims} ({tag.get('sentiment')})")
        tagged.append({"role": role, "tag": tag})

    print("\nSynthesizing leadership digest...")
    digest = synthesize_digest(client, args.model, tagged)

    report = build_report(len(responses), tagged, digest, args.model)
    with open(args.out, "w") as f:
        f.write(report)
    print(f"\nReport written to {args.out}")


if __name__ == "__main__":
    main()
