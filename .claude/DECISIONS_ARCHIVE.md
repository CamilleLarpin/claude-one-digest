# Decisions Archive — claude-one-digest

> Superseded or resolved decisions. Load only if historical context is needed.

---

## [digest] Two-section format — Status + Learnings
- **Decision**: digest has two sections: Status (per-project achievements) and Learnings (cross-project concepts)
- **Rationale**: separates "what got done" from "what was learned"
- **Date**: 2026-03-12
- **Status**: superseded by "Per-session recap as primary output" — Status section removed, Learnings pivoted to per-session recap format

## [learnings] Two-phase extraction pipeline
- **Decision**: Phase 1 extracts learning questions per session; Phase 2 groups, deduplicates, and explains
- **Rationale**: single-call hit token limits; per-session extraction with Claude is reliable
- **Date**: 2026-03-13
- **Status**: on hold — superseded by single-call per-session recap; will resume if daily/weekly rollup is built

## [learnings] Python post-filter before Phase 2
- **Decision**: filter Phase 1 output in Python before Phase 2 — remove slash commands, path strings, short entries
- **Rationale**: 8b model doesn't reliably apply DROP rules; Python filter is deterministic
- **Date**: 2026-03-13
- **Status**: archived — Phase 2 pipeline not active; filter logic retained in session_recap.py noise filter
