# Lessons — claude-one-digest

> CONTAINS: mistakes made, patterns discovered, gotchas specific to this project.
> NOT HERE: decisions with rationale (→ DECISIONS.md), general cross-project patterns (→ LESSONS_GLOBAL.md).
> Split by load context at 150 lines — one file = one reason Claude loads it.
> When a lesson applies beyond this project: flag with `→ PROMOTE: LESSONS_GLOBAL.md — [reason]` (only if Rule or Guideline)
> Load tier: cool

---

## Format
```
## [category] · Rule|Guideline|Note · Short title
> YYYY-MM-DD · source: [project or session]
- what happened / what the trap is
- why it matters
- what to do instead
```

## Types
- **Rule**: must follow — violating it breaks things or causes silent failure
- **Guideline**: should follow unless explicitly justified
- **Note**: useful to know — no mandatory action

---

<!-- Add lessons below as they are discovered. Oldest at top, newest at bottom. -->

## [ingest] · Note · `history.jsonl` is prompts-only — not the source of truth for Claude Code sessions
> 2026-03-11 · source: claude-one-digest
- `~/.claude/history.jsonl` contains only user prompts, truncated for display — no assistant responses, no full content
- 106 of 108 sessions in `history.jsonl` are already present in `~/.claude/projects/**/*.jsonl` as full transcripts
- Always use `projects/*.jsonl` for analysis; `history.jsonl` is redundant and less rich

## [ingest] · Note · Claude Code session duration is unreliable — sessions left open overnight inflate it
> 2026-03-11 · source: claude-one-digest
- Some sessions show 5000+ minute duration because Claude Code was left open without activity
- Duration cannot be used as a signal for session weight or importance
- Use `ts_start` for grouping and filtering; ignore duration entirely in digest logic
