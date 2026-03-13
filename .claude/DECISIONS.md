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

## [stack] LLM for digest — Claude Haiku via Anthropic API
- **Decision**: `claude-haiku-4-5-20251001` via Anthropic API for both Phase 1 and Phase 2
- **Rationale**: Groq 8b produced noise it couldn't filter and hallucination loops; 70b hit TPD in one session. Claude follows complex extraction instructions reliably. Cost is negligible for a daily personal tool. Groq dropped entirely.
- **Date**: 2026-03-13
- **Status**: active — supersedes "Groq llama-3.1-8b-instant as daily driver"

## [digest] Time window — calendar-day, not rolling 24h
- **Decision**: `--days N` filters from midnight of N days ago (local time); `--date YYYY-MM-DD` targets a specific calendar day exactly
- **Rationale**: rolling 24h window causes content drift as the script is re-run during the day — sessions near the edge drop in and out; calendar-day gives stable, reproducible results for an end-of-day use case
- **Date**: 2026-03-12
- **Status**: active

## [digest] Two-section format — Status + Learnings
- **Decision**: digest has two sections: Status (per-project achievements, max 2 bullets) and Learnings (cross-project concepts Camille engaged with)
- **Rationale**: separates "what got done" from "what was learned" — different audiences for each (project tracking vs personal knowledge); cross-project learnings require a single pass over all sessions, not per-project calls
- **Date**: 2026-03-12
- **Status**: Status section temporarily removed pending Learnings quality validation; will be re-added once Learnings is stable

## [learnings] Two-phase extraction pipeline
- **Decision**: Phase 1 extracts learning questions per session (one Claude call per session, up to 40k chars); Phase 2 groups, deduplicates, and writes a short explanation per concept (one call, max 2000 tokens). Output is a structured summary with headings and explanations Camille can re-read.
- **Rationale**: single-call hit token limits; per-session extraction with Claude is reliable; Phase 2 explanation format chosen over concept-names-only after concept-only output was deemed insufficient by Camille
- **Date**: 2026-03-13
- **Status**: active — under review; gold standard to be defined from Mar 12 Docker/FastAPI session before finalising

## [learnings] Python post-filter before Phase 2
- **Decision**: filter Phase 1 output in Python before sending to Phase 2 — remove slash commands, path-like strings, entries < 8 chars, known noise tokens (ls, cat, echo, etc.)
- **Rationale**: 8b model doesn't reliably apply complex DROP rules in the merge prompt; Python filter is deterministic and free; alternatives: stronger model for Phase 2 (risks TPD exhaustion), accepting noise (degrades digest quality)
- **Date**: 2026-03-13
- **Status**: active

## [ingest] Primary Claude Code source — `~/.claude/projects/` only
- **Decision**: ingest from `~/.claude/projects/**/*.jsonl`; ignore `~/.claude/history.jsonl`
- **Rationale**: `projects/` contains full transcripts (user + assistant); `history.jsonl` is user prompts only, truncated, and 106/108 sessions are already covered by `projects/`; adding it would require deduplication for no quality gain
- **Date**: 2026-03-11
- **Status**: active
