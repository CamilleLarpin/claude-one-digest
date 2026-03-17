# Decisions Archive — claude-one-digest

> Superseded or stable decisions moved here to keep DECISIONS.md under 100 lines.

---

## [stack] Language — Python script
- **Decision**: Python CLI script (no framework)
- **Rationale**: file I/O + JSON parsing + HTTP calls — no orchestration needed; stays consistent with other Python projects in the stack; alternatives: bash (too brittle for JSON), n8n (overkill, no local file access)
- **Date**: 2026-03-11
- **Status**: archived — stable, foundational, unlikely to change

## [ingest] Primary Claude Code source — `~/.claude/projects/` only
- **Decision**: ingest from `~/.claude/projects/**/*.jsonl`; ignore `~/.claude/history.jsonl`
- **Rationale**: `projects/` contains full transcripts (user + assistant); `history.jsonl` is user prompts only, truncated, and 106/108 sessions are already covered by `projects/`; adding it would require deduplication for no quality gain
- **Date**: 2026-03-11
- **Status**: archived — stable, foundational, unlikely to change
