# Problem Statement

Engineering teams lose hours each sprint manually converting raw meeting notes and
requirement documents into structured backlog items. The conversion is error-prone:
stories are inconsistently formatted, acceptance criteria are missing or untestable,
priorities reflect whoever spoke last rather than business value, and duplicate items
accumulate silently against the existing backlog. The Smart Backlog Assistant eliminates
this toil by ingesting unstructured text or PDF input and producing well-formed user
stories — with acceptance criteria, MoSCoW priority, and a requirements summary — ready
for grooming rather than drafting.

---

## Use Cases

**UC-1 — Meeting notes to stories**
A product owner pastes last week's planning session notes into the tool. Within seconds
they receive a prioritised list of user stories derived from the discussion, each with
testable acceptance criteria, instead of spending an hour transcribing them manually.

**UC-2 — Requirements PDF to stories + summary**
A tech lead receives a client requirements document as a PDF. They feed it to the tool and
get a structured story list plus a summary of the key requirements identified — removing
the need to manually parse and reformat a multi-page document before grooming can begin.

**UC-3 — Backlog-aware generation**
A team with an active backlog provides it alongside new meeting notes. The tool generates
only net-new stories, flagging any overlap with existing items in a warnings list rather
than silently duplicating work already captured.

---

## AI tooling used in problem definition

Claude Code (AI pair-engineer) was used to pressure-test the problem framing, validate
that the three use cases are distinct and realistic, and ensure alignment between the
problem statement and the brief's evaluation criteria.
