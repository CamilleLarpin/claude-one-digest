# Design — claude-one-digest

> CONTAINS: problem space, use cases, user flows, solution approach, non-goals.
> NOT HERE: implementation details (→ CONTEXT.md), active tasks (→ TODOS.md), tech decisions (→ DECISIONS.md).
> Update when scope changes or a use case is validated/invalidated.
> Load tier: warm — update to cold when project reaches Running/Maintenance

---

## Problem Space

**Pain point**: Sessions with Claude that contain deep conceptual teaching — new mental models, analogies, explanations built step by step — disappear completely when the session ends. There's no way to review, reinforce, or look up what was learned.

**Validated user need** (2026-03-13 design step-back):
- Camille does not go back to raw sessions — too noisy, too long
- She wants to review a session recap the evening after or next morning, and reference it weeks later ("how did Docker layer caching work again?")
- A daily/weekly push would become noise she ignores — on demand is the right model
- Only sessions where Claude explains concepts are worth processing — not bug fixes, not architecture-only sessions
- Analogies are critical to memory retention — the recap must preserve the exact analogies from the conversation, not substitute generic explanations

**Desired state**: When a session teaches something real, Camille flags it at `/end-of-session`. A readable recap is generated and stored. She can review it when she wants and find it when she needs it.

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

- [ ] Session recap matches gold standard quality: concepts grouped, analogies preserved, plain-language re-explanation, triggering question included
- [ ] `python digest.py --queue` processes all entries in `data/queue.md` and saves one `.md` per session to `data/digests/`
- [ ] Output is readable as plain Markdown, browsable by project/date
- [ ] Gold standard test: Mar 12 audio-intelligence-pipeline session recap matches quality of manually-produced recap from 2026-03-13

---

## Use Cases

### UC1 — Session recap (primary, building now)
**Actor**: Camille
**Trigger**: After a teaching-heavy session, flags it via `/end-of-session` step 3 → written to `data/queue.md`
**Flow**:
1. Runs `python digest.py --queue` from terminal
2. Script reads `data/queue.md`, finds matching `.jsonl` by date + project
3. Extracts Q&A turns (strips ritual noise: `/start`, `/commit-push`, tool calls, system blocks)
4. One Claude Haiku call with gold-standard prompt
5. Saves to `data/digests/YYYY-MM-DD_project-slug.md`
**Expected output**: Concept-grouped recap with plain-language re-explanations preserving the original analogies from the conversation

### UC2 — Reference lookup (on demand)
**Actor**: Camille
**Trigger**: "How did Docker layer caching work again?"
**Flow**: Opens `data/digests/`, searches by project or concept name
**Expected output**: Finds the relevant recap, reads the section

### UC3 — Daily/weekly rollup (deferred)
Will be addressed once UC1 is validated. Likely: aggregate `data/queue.md` entries by day/week into a rolled-up view.

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
