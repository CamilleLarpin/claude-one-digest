# Todos — claude-one-digest

> CONTAINS: active milestones, next actions, blocked items for this project.
> NOT HERE: decisions (→ DECISIONS.md), completed work (archive or delete when done), cross-project tasks.
> This is a working scratchpad for Camille + Claude. Keep it current — stale todos are noise.
> Load tier: warm

---

## Now
- [ ] Retroactive tagging — add a way to flag a past session that wasn't tagged at the time (date + project override for `/digest`, or direct manual entry helper)

## Next
- [ ] Daily/weekly rollup — future phase, not planned

## Out of scope
- Claude.ai/Desktop ZIP ingest — future phase, deprioritised

## Blocked
(none)

## Done (recent — clear periodically)
- [x] Project-level auto-digest — `data/auto_digest_projects.txt` config; sessions auto-included without `/digest`
- [x] End-to-end validated: digest 2026-03-13 → 1 file, correct content, opens cleanly
- [x] Caching — skips API call if recap already exists; `--force` to regenerate
- [x] One file per day (not per project) — project sections within the file
- [x] Same-project same-day entries merged — descriptions combined, one API call
- [x] Prompt tightened — only generic transferable concepts qualify, not project decisions
- [x] Fixed (none) + reasoning block leak — model no longer outputs reasoning on empty sessions
- [x] Replaced queue.md with learning_log.md — permanent record, no done-marking
- [x] Created /digest Claude Code command — flags current session to learning log
- [x] Created digest shell script + alias — `digest [date]` generates and opens recaps
- [x] Removed digest step from /end-of-session — flagging is now a separate /digest command
