# Context — claude-one-digest

> CONTAINS: current state, architecture overview, file structure, key dependencies.
> NOT HERE: decisions with rationale (→ DECISIONS.md), todos (→ TODOS.md), solution design (→ DESIGN.md).
> Update this file when architecture changes or a milestone completes.
> Load tier: warm

---

## Current State
**As of**: 2026-03-12
Digest module built and working end-to-end. Outputs to stdout and saves to `data/digests/`. Prompt quality iterated — two-section format (Status + Learnings) with calendar-day windowing and `--date` flag.

## Architecture
Two-phase Groq pipeline:
1. **Status** — one call per project group → high-level achievements (max 2 bullets)
2. **Learnings** — one cross-project call → non-obvious concepts Camille engaged with

Ingest: `~/.claude/projects/**/*.jsonl` → normalized `Session` / `Turn` objects → grouped by project → chunked at 10k chars.

## File Structure
```
claude-one-digest/
  .claude/              # context files
  data/
    digests/            # YYYY-MM-DD.md outputs (gitignored)
    imports/            # Claude.ai/Desktop ZIPs (gitignored, not yet used)
  src/
    models.py           # Session + Turn dataclasses
    ingest_claude_code.py  # reads ~/.claude/projects/, filters by --days or --date
    digest.py           # main pipeline: ingest → group → Groq → render → save
  .env                  # GROQ_API_KEY (gitignored)
  .env.example
  requirements.txt
```

## Key Dependencies
- `openai>=1.0.0` — Groq API (OpenAI-compatible)
- `python-dotenv>=1.0.0`

## Environment
- **Dev**: Python 3.12 (pyenv)
- **Credentials**: `GROQ_API_KEY` in `.env`
