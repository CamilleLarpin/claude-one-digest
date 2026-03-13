# Todos — claude-one-digest

> CONTAINS: active milestones, next actions, blocked items for this project.
> NOT HERE: decisions (→ DECISIONS.md), completed work (archive or delete when done), cross-project tasks.
> This is a working scratchpad for Camille + Claude. Keep it current — stale todos are noise.
> Load tier: warm

---

## Now
- [ ] **Build `src/session_recap.py`** — plan defined (2026-03-13):
  1. Read `data/queue.md`, resolve each entry to the matching `.jsonl` (by date + project slug)
  2. Extract Q&A turns — strip ritual noise (lines with `/start`, `/commit-push`, `command-name`, `command-message`, `Caveat:`, tool call/result blocks)
  3. One Claude Haiku call with gold-standard prompt: group by concept, preserve analogies, re-explain in plain language, include triggering question
  4. Save to `data/digests/YYYY-MM-DD_project-slug.md`
  5. Mark processed entries done in `queue.md`
  6. Test against Mar 12 audio-intelligence-pipeline session — compare against manually-produced gold standard

## Next
- [ ] Filter `projects` pseudo-project from digest (sessions run from ~/projects/ root, not a real project)
- [ ] Add Claude.ai/Desktop ZIP ingest once first export is available
- [ ] Daily/weekly rollup — deferred until session recap is validated

## Blocked
(none)

## Done (recent — clear periodically)
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
