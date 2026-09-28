# Prompt Engineering — Design Notes

## Runtime prompt: story generation

The story-generation prompt (in `src/prompts.py`) is the core AI engineering artefact
in this project. This document explains the design decisions.

---

### System message structure

```
Role statement
↓
Output constraint (positive, not negative)
↓
Schema (embedded before the instruction)
↓
Rules
↓
One-shot example
↓
Generation instruction (last)
```

**Why schema before instruction:** the model generates tokens autoregressively. If it sees
the target schema and a complete example before the instruction to generate, it is primed
on the correct shape before it starts producing output. Placing these after the instruction
forces the model to revise its internal plan mid-generation, which produces less consistent
results.

**Why a positive constraint:** "Return only valid JSON matching this schema" outperforms
"Do not return prose" in practice. Negative constraints describe what to avoid; positive
constraints describe exactly what to produce. The model follows positive framing more
reliably.

**Why a one-shot example with fictional content:** the example uses a PDF-export story
unrelated to this project. This anchors quality and format without priming the model on
the *topics* it should generate — we want it to reason from the input text, not from the
example's subject matter.

---

### User message structure

```
Section 1: input text (full, normalised)
---
Section 2 (optional): existing backlog titles
"Existing backlog items — avoid duplicating these: ..."
```

**Why titles only, not full JSON:** injecting full story objects for deduplication context
wastes tokens and increases reasoning load. The model only needs titles to detect overlap.
A concise numbered list is enough.

**Why deduplication goes in warnings[], not silent drops:** the caller decides what to do
with overlapping items. Silent drops hide information; warnings surface it. This matches
the project's principle of surfacing reconciliation rather than hiding it.

---

### Iterations

**v1 — initial prompt**
Used `response_format={"type":"json_object"}`. Model returned stories as nested arrays
(`stories: [[{...}], [{...}]]`). Fixed by adding the explicit rule:
`"stories: flat array of objects — do NOT nest arrays"`.

**v2 — max_tokens tuning**
Set max_tokens=2048. The Nemotron model generates ~4000 tokens of reasoning before
outputting JSON; the response was cut off at the token limit before any JSON was produced.
Raised to 4096, then 8192 — both hit NVIDIA's 5-minute gateway timeout.

**v3 — streaming**
Switched `chat.completions.create` to `stream=True`. Streaming connections bypass the
5-minute gateway timeout — tokens arrive as they are generated, and the connection stays
open until the model finishes. The openai client auto-retried on 504s; request succeeded
on the third attempt.

**v4 — JSON extraction**
Even with streaming, `json.loads(content)` failed on the full response because the model
prefixes its output with reasoning text ("Here's a thinking process: ..."). Fixed with a
right-to-left scan: iterate `{` positions from end to start, returning the first span that
parses as valid JSON. This reliably finds the JSON object at the tail of the response.

---

### What worked well

- Schema-before-instruction placement produced well-formed output on first attempt.
- The validate-and-repair pattern caught schema drift (nested arrays) on the first live
  call and handled it gracefully.
- Streaming solved the gateway timeout without any prompt changes.

### What to improve next

- Add a system-prompt instruction to suppress reasoning output entirely for this model
  (NVIDIA may expose a `reasoning_effort` parameter in future API versions).
- Consider a two-pass approach: first extract key requirements as bullet points, then
  generate stories from the extracted list. This would reduce the model's reasoning
  burden per call and improve consistency.
- The few-shot example should be validated against the target model periodically — what
  anchors one model may confuse another.
