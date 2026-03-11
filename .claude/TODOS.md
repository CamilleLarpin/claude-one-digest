# Todos — claude-one-digest

> CONTAINS: active milestones, next actions, blocked items for this project.
> NOT HERE: decisions (→ DECISIONS.md), completed work (archive or delete when done), cross-project tasks.
> This is a working scratchpad for Camille + Claude. Keep it current — stale todos are noise.
> Load tier: warm

---

## Now
- [ ] Build digest module: group sessions by project, chunk long sessions, call Groq API, render Markdown output

## Next
- [ ] Wire digest output to stdout + save to `data/digests/YYYY-MM-DD.md`
- [ ] Tune prompt quality: test `llama-3.1-8b-instant` → evaluate `llama-3.3-70b-versatile`
- [ ] Add Claude.ai/Desktop ZIP ingest once first export is available

## Blocked
(none)

## Done (recent — clear periodically)
- [x] Project initialized — folder, git, GitHub repo, Notion linked
- [x] DESIGN.md written — problem space, data sources, scope, UC1+UC2, solution approach, normalization schema
- [x] Stack + LLM decisions recorded in DECISIONS.md
- [x] Ingest module built (`src/ingest_claude_code.py` + `src/models.py`) — reads ~/.claude/projects/, normalizes schema, filters by --days
