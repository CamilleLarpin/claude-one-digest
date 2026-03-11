# Decisions — [PROJECT NAME]

> CONTAINS: active choices made during this project — what was chosen, alternatives considered, rationale.
> NOT HERE: implementation steps, todos, bug reports, lessons (→ LESSONS.md), resolved decisions (→ DECISIONS_ARCHIVE.md).
> Archive at 100 lines → DECISIONS_ARCHIVE.md.
> When a decision applies beyond this project: flag with `→ PROMOTE: DECISIONS_GLOBAL.md — [reason]`
> Load tier: cool

---

## Format
```
## [category] Decision title
- **Decision**: what was chosen
- **Rationale**: why — include alternatives considered and why they were rejected
- **Date**: YYYY-MM-DD
- **Status**: active | superseded by [title] | archived
```

---

## [stack] Language — Python script
- **Decision**: Python CLI script (no framework)
- **Rationale**: file I/O + JSON parsing + HTTP calls — no orchestration needed; stays consistent with other Python projects in the stack; alternatives: bash (too brittle for JSON), n8n (overkill, no local file access)
- **Date**: 2026-03-11
- **Status**: active

## [stack] LLM for digest — Groq, dev→prod split
- **Decision**: `llama-3.1-8b-instant` during prompt development; `llama-3.3-70b-versatile` for quality evaluation; re-evaluate Claude API vs Groq after first real digest
- **Rationale**: Groq is OpenAI-compatible, free tier sufficient for daily digest volume (~10 grouped sessions), fast iteration; Claude API reserved as fallback if quality gap is material; alternatives: Claude API from day one (costs money before prompt is stable), local Ollama (too slow for 70B on Mac)
- **Date**: 2026-03-11
- **Status**: active

## [ingest] Primary Claude Code source — `~/.claude/projects/` only
- **Decision**: ingest from `~/.claude/projects/**/*.jsonl`; ignore `~/.claude/history.jsonl`
- **Rationale**: `projects/` contains full transcripts (user + assistant); `history.jsonl` is user prompts only, truncated, and 106/108 sessions are already covered by `projects/`; adding it would require deduplication for no quality gain
- **Date**: 2026-03-11
- **Status**: active
