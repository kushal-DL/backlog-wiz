# backlog-wiz

An AI-powered CLI that converts meeting notes or requirements documents into structured,
prioritised user stories with acceptance criteria.

```
python3 src/main.py --input samples/meeting_notes.txt --backlog samples/backlog.json
```

---

## What it does

Feed it a `.txt`, `.md`, or `.pdf` file and it returns:

- User stories in *"As a / I want / So that"* format
- Testable acceptance criteria (≥2 per story)
- MoSCoW priority and category
- A summary of key requirements identified
- Warnings for stories that overlap your existing backlog

---

## Architecture

```
CLI (main.py)
  │
  ├─▶ ingest.py     — text / PDF → clean string
  ├─▶ context.py    — backlog.json → title list for deduplication
  ├─▶ prompts.py    — builds system + user messages
  ├─▶ ai_client.py  — OpenAI-compatible Chat Completions (streaming)
  ├─▶ validate.py   — schema check; one bounded retry on failure
  └─▶ output.py     — writes output.json + prints readable summary
```

All LLM calls go through `ai_client.py` only. Swap the endpoint by changing `MODEL_URL`
and `MODEL_NAME` — no code changes required.

---

## Prerequisites

- Python 3.10+
- An API key for an OpenAI-compatible LLM endpoint

---

## Setup

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd backlog-wiz

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Edit .env and set MODEL_KEY to your API key
```

`.env` variables:

| Variable | Required | Default | Description |
|---|---|---|---|
| `MODEL_KEY` | ✅ | — | API key for the LLM endpoint |
| `MODEL_URL` | ✅ | `https://integrate.api.nvidia.com/v1` | OpenAI-compatible base URL |
| `MODEL_NAME` | ✅ | `nvidia/nemotron-3.5-lightning-30b-a3b` | Model identifier |

---

## Run

### Meeting notes → stories

```bash
python3 src/main.py --input samples/meeting_notes.txt
```

### With existing backlog (enables deduplication)

```bash
python3 src/main.py --input samples/meeting_notes.txt --backlog samples/backlog.json
```

### Requirements PDF → stories

```bash
python3 src/main.py --input samples/requirements.pdf --output results.json
```

### Test wiring without an API key

```bash
python3 src/main.py --input samples/meeting_notes.txt --mock
```

### Override model at runtime

```bash
python3 src/main.py --input samples/meeting_notes.txt --model gpt-4o-mini
```

---

## Output

Results are written to `output.json` (override with `--output`) and printed to the console.

```json
{
  "stories": [
    {
      "id": "S-001",
      "title": "Add resend verification email button",
      "description": "As a new user, I want a resend verification email button...",
      "acceptance_criteria": ["Button appears after 60 seconds.", "..."],
      "priority": "Must",
      "category": "feature",
      "source_reference": "resend verification email button after 60 seconds"
    }
  ],
  "summary": "The sprint focuses on improving onboarding...",
  "warnings": []
}
```

---

## Project structure

```
backlog-wiz/
├── src/
│   ├── main.py        # CLI entry point
│   ├── schemas.py     # output data contract (single source of truth)
│   ├── ingest.py      # text + PDF ingestion
│   ├── context.py     # existing backlog loader
│   ├── prompts.py     # all prompt strings
│   ├── ai_client.py   # LLM wrapper (streaming)
│   ├── validate.py    # schema validation + repair
│   └── output.py      # JSON writer + console renderer
├── samples/
│   ├── meeting_notes.txt   # sample sprint planning notes
│   ├── backlog.json        # sample existing backlog (3 items)
│   └── requirements.pdf   # sample requirements document (PDF)
├── docs/
│   ├── problem.md          # problem statement and use cases
│   ├── expected.md         # expected outputs per sample input
│   └── prompt_engineering.md  # prompt design decisions and iterations
├── tests/
├── .env.example
└── requirements.txt
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `MODEL_KEY environment variable is not set` | `.env` missing or key not set | Copy `.env.example` to `.env` and add your key |
| `Authentication failed` | Invalid API key | Check `MODEL_KEY` value in `.env` |
| `504 Gateway Timeout` (retried automatically) | NVIDIA endpoint busy | The client retries automatically; no action needed |
| `No extractable text found` warning | Scanned/image-only PDF | Use a text-based PDF or convert to `.txt` first |
| `Could not extract valid JSON` | Model response truncated | Increase `max_tokens` in `ai_client.py` or shorten input |

---

## Notes on the NVIDIA Nemotron model

The `nvidia/nemotron-3.5-lightning-30b-a3b` model generates chain-of-thought reasoning
before producing JSON output. Responses can take 3–10 minutes. The tool uses streaming
(`stream=True`) to keep the connection alive and a right-to-left JSON scan to extract
the output from the tail of the response. See `docs/prompt_engineering.md` for details.
