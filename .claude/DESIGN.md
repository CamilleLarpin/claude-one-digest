# Design — claude-one-digest

> CONTAINS: problem space, use cases, user flows, solution approach, non-goals.
> NOT HERE: implementation details (→ CONTEXT.md), active tasks (→ TODOS.md), tech decisions (→ DECISIONS.md).
> Update when scope changes or a use case is validated/invalidated.
> Load tier: warm — update to cold when project reaches Running/Maintenance

---

## Problem Space

**Pain point**: Knowledge and progress from Claude sessions evaporate — there is no unified record of what was learned or achieved across three interfaces (Claude Code, Claude Desktop, Claude.ai).

**Current state**: Three separate interfaces produce invisible output. Sessions end, learnings disappear. No way to answer "what did I learn this week?" or "what did I actually ship?" without manually recalling each session. Interfaces overlap — designing happens in Claude Code sessions, not just on the web — so source ≠ category.

**Desired state**: On-demand (later: automatic) digest that surfaces two distinct analytical lenses — *Learnings* (new knowledge, concepts, corrections) and *Achievements* (decisions made, things shipped, things moved forward) — stored historically so past digests are browsable.

---

## Data Sources

| Source | Access method | Freshness | Schema |
|---|---|---|---|
| Claude Code | `~/.claude/projects/<slug>/*.jsonl` | Always fresh | Full turns: `{sessionId, type, message{role, content[]}, timestamp, cwd, gitBranch, slug}` |
| Claude.ai / Desktop | Manual export ZIP (Settings → Privacy) | Weekly or on-demand | ZIP with conversations + metadata as JSON — schema TBD on first export |

**`~/.claude/history.jsonl` is NOT used.** It contains user prompts only (truncated display strings, no assistant responses). 106 of 108 sessions in `history.jsonl` are already covered by `projects/*.jsonl`, which is the source of truth — full content, both sides.

**`projects/` schema** (confirmed from inspection):
```json
// One line per turn (user or assistant), or file-history-snapshot (skip)
{
  "type": "user" | "assistant",
  "sessionId": "<uuid>",
  "uuid": "<message uuid>",
  "parentUuid": "<uuid | null>",
  "timestamp": "<ISO8601>",
  "cwd": "/Users/.../projects/<slug>",
  "gitBranch": "<branch>",
  "slug": "<session-slug>",
  "message": {
    "role": "user" | "assistant",
    "content": [{"type": "text", "text": "..."}]
    // content may also contain tool_use / tool_result blocks — strip for digest
  }
}
```

**Critical constraint**: The pipeline must run usefully with Claude Code alone. Web/Desktop exports are additive — present when dropped in, absent otherwise. Never block on them.

**Future**: Automate the export trigger (browser extension, API if Anthropic exposes one). Not in scope now.

---

## Scope

**In scope**:
- Ingest Claude Code history automatically (file system read)
- Ingest Claude.ai / Desktop export ZIPs when manually dropped into a watched folder
- Normalize all sources to a unified conversation schema
- Filter by configurable time window (default: today / last 24h)
- Run Claude API analysis → produce Markdown digest with two sections: Learnings + Achievements
- Output to terminal (stdout)
- Store each digest as a file in `data/digests/YYYY-MM-DD.md`
- CLI trigger: `python digest.py` or `./digest.sh`

**Out of scope**:
- Real-time or live tracking
- Interactive conversation browser or search
- Automated export of Claude.ai/Desktop (future)
- Multi-user support
- Editing or annotating past conversations
- Telegram delivery (Phase 2)
- Cron scheduling (Phase 2)

---

## Success Criteria

- [ ] Running `digest.py` with no export ZIPs present produces a useful digest from Claude Code history alone
- [ ] When an export ZIP is present in `data/imports/`, it is merged into the same digest without duplication
- [ ] Each digest is stored in `data/digests/` and browsable as plain Markdown
- [ ] Learnings and Achievements are surfaced as two distinct, non-overlapping sections
- [ ] The digest covers a configurable time window (default: last 24h)

---

## Use Cases

### UC1 — End-of-day recap (on demand)
**Actor**: Camille
**Flow**:
1. Runs `./digest.sh` (or `python digest.py`) from terminal
2. Script reads `~/.claude/history.jsonl` + any ZIPs in `data/imports/` for the last 24h
3. Normalizes to unified schema, filters by time window
4. Sends grouped summaries to Claude API with digest prompt
5. Prints Markdown digest to terminal
6. Saves digest to `data/digests/YYYY-MM-DD.md`
**Expected output**: A concise Markdown digest with two sections — what was learned (new knowledge, corrections, concepts) and what was achieved (decisions, shipped things, progress made)

### UC2 — Weekly review with web/desktop conversations
**Actor**: Camille
**Flow**:
1. Exports Claude.ai/Desktop ZIP from Settings → Privacy
2. Drops ZIP into `data/imports/`
3. Runs `./digest.sh --days 7`
4. Script merges Claude Code history + exported conversations for the last 7 days
5. Produces and stores a weekly digest
**Expected output**: Same format as UC1 but covering a broader window and richer source mix

---

## Solution Approach

```
Sources:
  ~/.claude/history.jsonl                    [always available]
  ~/.claude/projects/<path>/*.jsonl          [always available]
  data/imports/*.zip (Claude.ai/Desktop)     [manual drop-in, optional]
        ↓
  Ingest + Normalize
  → unified: {source, ts, title, project, session_id, messages[]}
        ↓
  Filter by time window (--days N, default 1)
  Deduplicate by session_id / message hash
        ↓
  Group by project / conversation thread
        ↓
  Claude API — digest prompt per group
  → two analytical lenses:
      Learnings: new knowledge, concepts, corrections, surprises
      Achievements: decisions made, things shipped, progress moved
        ↓
  Render Markdown digest
  → stdout (terminal)
  → data/digests/YYYY-MM-DD.md (or YYYY-MM-DD--weekly.md)
```

**Normalization schema** (target for all sources):
```json
{
  "source": "claude-code | claude-ai | claude-desktop",
  "session_id": "<unique>",
  "ts_start": "<ISO8601>",
  "ts_end": "<ISO8601>",
  "project": "<slug or null>",
  "title": "<conversation title or null>",
  "messages": [
    {"role": "user|assistant", "ts": "<ISO8601>", "content": "<text>"}
  ]
}
```

**Digest prompt design** (to be refined during build):
- Send per-group summaries (not raw messages) to Claude to stay within context limits
- Prompt instructs Claude to distinguish *learning* (something Camille did not know before) from *achievement* (something moved forward or completed)
- Output is structured Markdown, not freeform prose

---

## Open Questions (resolve during build)

- [x] Do `~/.claude/projects/` transcripts overlap with `history.jsonl`? → YES, 106/108 sessions overlap. `history.jsonl` is redundant and dropped from scope.
- [ ] What is the exact schema of Claude.ai export ZIPs? (Validate when first export is available)
- [ ] Is per-group summarization before the Claude API call sufficient, or do some sessions need chunking first? (Some sessions have 82k+ input tokens — chunking likely needed)
