# Context — claude-one-digest

> CONTAINS: current state, architecture overview, file structure, key dependencies.
> NOT HERE: decisions with rationale (→ DECISIONS.md), todos (→ TODOS.md), solution design (→ DESIGN.md).
> Update this file when architecture changes or a milestone completes.
> Load tier: warm

---

## Current State
**As of**: 2026-03-13
Pivoted from daily digest to per-session recap as primary output. Gold standard established from Mar 12 audio-intelligence-pipeline DevOps session (0b6d250f). Queue mechanism in place. Session recap generator not yet built.

Previous daily digest pipeline (Status + Learnings, Groq → Claude Haiku) is on hold pending session recap validation.

## Architecture
Two distinct outputs (currently only recap is active):

**Session recap** (primary, building now):
- Triggered by `--queue` or `--session <path>`
- Reads flagged session `.jsonl` → extracts Q&A turns (strips ritual noise) → one Claude Haiku call → saves `data/digests/YYYY-MM-DD_project-slug.md`
- Format: concept groups + re-explanation preserving original analogies + triggering question

**Daily digest** (on hold):
- Two-phase Claude Haiku pipeline: Status (per-project) + Learnings (cross-project)
- Paused — will resume once session recap is validated

**Flagging mechanism**:
- `/end-of-session` step 3 appends to `data/queue.md`: `YYYY-MM-DD | <project> | <description>`
- `--queue` mode reads queue, resolves to `.jsonl` by date + project, processes, marks done

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
