# Todos — claude-one-digest

> CONTAINS: active milestones, next actions, blocked items for this project.
> NOT HERE: decisions (→ DECISIONS.md), completed work (archive or delete when done), cross-project tasks.
> This is a working scratchpad for Camille + Claude. Keep it current — stale todos are noise.
> Load tier: warm

---

## Now
- [ ] Validate Mar 12 recap quality against gold standard (manual review) — content ✅, format renders well in preview

## Next
- [ ] Filter `projects` pseudo-project from digest (sessions run from ~/projects/ root, not a real project)
- [ ] Add Claude.ai/Desktop ZIP ingest once first export is available
- [ ] Daily/weekly rollup — deferred until session recap is validated

## Blocked
(none)

## Done (recent — clear periodically)
- [x] Built `src/session_recap.py` — queue parser, noise filter, Claude Haiku single-call, save + mark done
- [x] Switched from Groq to Claude API (claude-haiku-4-5-20251001) for Learnings extraction
- [x] Removed Status section temporarily — focus on Learnings quality first
- [x] Fixed missing `{content}` placeholders in EXTRACT_PROMPT and MERGE_PROMPT
- [x] Raised session char cap 8000 → 40000 — covers full sessions (Docker content was at char 11593)
- [x] Raised MERGE max_tokens 400 → 2000 — output was being cut mid-response
- [x] Fixed format example — replaced `- ConceptName` placeholder with real example to prevent literal output
- [x] Validated Phase 1 on Docker/FastAPI session — correct questions extracted
- [x] Validated Phase 2 output — structured Learnings with grouped headings and explanations
- [x] Status section built — line→project map + @@ hunk offsets (working, temporarily removed)
- [x] Calendar-day windowing — `--days N` from midnight, `--date YYYY-MM-DD`
