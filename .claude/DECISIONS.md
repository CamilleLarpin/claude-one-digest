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

## [digest] Per-session recap as primary output — daily/weekly deferred
- **Decision**: build per-session recap first; daily and weekly rollup deferred until recap quality is validated
- **Rationale**: design step-back (2026-03-13) revealed the real need is retrieval and review of specific teaching sessions, not a pushed daily summary; Camille explicitly said daily/weekly would become noise she ignores; recap-first unblocks the daily/weekly rollup naturally once it exists
- **Date**: 2026-03-13
- **Status**: active — supersedes "Two-section format — Status + Learnings" as primary build target

## [digest] On-demand trigger only — no cron, no push
- **Decision**: no scheduled runs; Camille triggers recap generation explicitly (via `--queue` or `--session`) after flagging a session at `/end-of-session`
- **Rationale**: Camille explicitly said she worries a daily/weekly would force her and she wouldn't do it; on-demand matches her use pattern (review evening after or next morning, reference later); aligns with global principle "user label as inclusion rule — human decides, AI executes"
- **Date**: 2026-03-13
- **Status**: active

## [digest] Gold standard format — concept + re-explanation preserving original analogies
- **Decision**: session recaps group by concept (not chronologically), re-explain each concept in plain language, preserve the exact analogies from the conversation, and include the question that triggered the explanation
- **Rationale**: gold standard established from Mar 12 DevOps session — quality came from reading actual Q&A exchanges and preserving analogies ("knock at a door", "bouncer at the entrance", "envelope", "two guards"); Camille confirmed analogies help memory retention; keyword extraction or concept lists rejected as insufficient
- **Date**: 2026-03-13
- **Status**: active

## [recap] Session recap uses a single Claude call — not two-phase
- **Decision**: one Claude Haiku call per session: extract qualifying questions, group by concept, re-explain, include triggering question and analogies — all in one prompt
- **Rationale**: two-phase pipeline (digest.py) was built for cross-session deduplication; single-session recap has no deduplication need; one call is simpler, faster, and cheaper; quality validated on Mar 12 gold standard
- **Date**: 2026-03-13
- **Status**: active

## [recap] Noise filtering — pattern-based, turn-level
- **Decision**: filter turns where text starts with `/`, or contains `<command-name>` / `<command-message>` / `<local-command-caveat>` XML tags; skip turns < 5 chars
- **Rationale**: ritual noise (slash commands, CLI invocations injected by Claude Code) inflates the transcript and confuses the model; tool blocks already stripped by `extract_text()`; pattern matching is deterministic and requires no LLM call
- **Date**: 2026-03-13
- **Status**: active

## [recap] One file per day — projects as sections
- **Decision**: `digest [date]` produces one file `data/digests/YYYY-MM-DD.md`; projects appear as `## project` sections within it
- **Rationale**: Camille wants a daily review, not per-project files; one file = one open = one read; multiple files per day create friction and visual noise
- **Date**: 2026-03-16
- **Status**: active — supersedes per-project file naming

## [recap] Flagging via /digest command, not /end-of-session
- **Decision**: `/digest` is a standalone Claude Code command that appends to `data/learning_log.md`; the digest step is removed from `/end-of-session`
- **Rationale**: flagging is a separate intent from session wrap-up; decoupling lets Camille flag mid-session or not at all; `/end-of-session` stays focused on docs/lessons/tracker
- **Date**: 2026-03-16
- **Status**: active

## [recap] Permanent learning log — no done-marking
- **Decision**: `data/learning_log.md` keeps all entries permanently; no `[x]` marking; entries are a record, not a task list
- **Rationale**: the log is a historical artifact — "sessions where Camille learnt a great deal from Claude"; marking done would imply entries are consumed and loses the archive value; idempotent regeneration (caching) makes done-marking unnecessary
- **Date**: 2026-03-16
- **Status**: active

## [recap] Only generic transferable concepts qualify — project decisions excluded
- **Decision**: the recap prompt explicitly excludes project-specific analysis, decisions, and recommendations; only concepts a developer could apply in any future project qualify
- **Rationale**: Camille's feedback — "I want only what I learnt, not decisions I made"; project decisions belong in DECISIONS.md, not in a learning recap; the distinction: would this explanation be useful to any developer regardless of project?
- **Date**: 2026-03-16
- **Status**: active

## [recap] Auto-digest via config file — no manual flagging for selected projects
- **Decision**: `data/auto_digest_projects.txt` lists project slugs whose sessions are always included in the recap pipeline without `/digest`; the file is plain text, one slug per line; retroactive (works for any past date)
- **Rationale**: for high-frequency projects (finances-ezerpin, audio-intelligence-pipeline, data-engineering-notes) requiring `/digest` every session is friction; config file keeps inclusion logic simple, visible, and user-controlled; dedup logic prevents double-processing if a project is also manually flagged
- **Date**: 2026-03-17
- **Status**: active

## [recap] Caching — skip regeneration if file exists
- **Decision**: `session_recap.py` skips the API call if `data/digests/YYYY-MM-DD.md` already exists; `--force` flag overrides
- **Rationale**: LLM output is non-deterministic — re-running produces different classifications; caching makes the result stable and avoids unnecessary API cost; `--force` covers the explicit regeneration case
- **Date**: 2026-03-16
- **Status**: active

