# Context — claude-one-digest

> CONTAINS: current state, architecture overview, file structure, key dependencies.
> NOT HERE: decisions with rationale (→ DECISIONS.md), todos (→ TODOS.md), solution design (→ DESIGN.md).
> Update this file when architecture changes or a milestone completes.
> Load tier: warm

---

## Current State
**As of**: 2026-03-16
Session recap generator built and validated. Pipeline is complete: flag → generate → review.

Daily digest pipeline (`digest.py`, Groq) is dead code — paused indefinitely. Claude.ai/Desktop ingest is out of scope (future phase, not planned).

## Architecture

**Session recap** (primary, active):
- Triggered by `digest [date]` shell script (defaults to today)
- Reads `data/learning_log.md` for entries matching the date
- Resolves `.jsonl` by date + project → extracts Q&A turns (strips ritual noise) → one Claude Haiku call → saves `data/digests/YYYY-MM-DD_project-slug.md`
- Opens saved files automatically
- Format: concept groups + re-explanation preserving original analogies + triggering question

**Flagging mechanism**:
- `/digest` Claude Code command — appends to `data/learning_log.md`: `YYYY-MM-DD | <project> | <description>`
- Entries are permanent — the log is a record of all rich learning sessions
- `data/auto_digest_projects.txt` — projects always included without manual flagging (currently: `finances-ezerpin`, `audio-intelligence-pipeline`, `data-engineering-notes`)

Ingest: `~/.claude/projects/**/*.jsonl` → normalized `Session` / `Turn` objects → filtered by date + project.

## File Structure
```
claude-one-digest/
  .claude/              # context files
  data/
    learning_log.md     # permanent log of flagged learning sessions
    digests/            # YYYY-MM-DD_project.md recap outputs (gitignored)
  src/
    models.py           # Session + Turn dataclasses
    ingest_claude_code.py  # reads ~/.claude/projects/, filters by --days or --date
    session_recap.py    # main pipeline: learning_log → ingest → Claude Haiku → save
    digest.py           # dead code — old Groq pipeline, not used
  digest                # shell entry point: digest [date]
    data/auto_digest_projects.txt  # projects always included without manual /digest flag
  .env                  # ANTHROPIC_API_KEY (gitignored)
  .env.example
  requirements.txt
```

## Key Dependencies
- `anthropic>=0.18.0` — Claude Haiku API
- `python-dotenv>=1.0.0`

## Environment
- **Dev**: Python 3.12 (pyenv)
- **Credentials**: `ANTHROPIC_API_KEY` in `.env`
- **Shell alias**: `alias digest='~/projects/claude-one-digest/digest'` in `.zshrc`
