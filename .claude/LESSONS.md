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

## [git] · Rule · git diff hunks start mid-section — project header may not appear before changed lines
> 2026-03-12 · source: claude-one-digest
- `git diff` hunks start at the nearest context line before the change, not at the section header — if a `### Project` header is >3 lines above the change, it's outside the hunk and never seen by the parser
- Parsing `+` lines by scanning for the preceding `### ` line in the diff body silently produces empty results
- Fix: build a line→project map from the full current file first, then use `@@` hunk offsets to resolve which project each change belongs to

## [llm] · Rule · Groq free tier TPM and TPD limits are per-model and separate
> 2026-03-12 · source: claude-one-digest
- `llama-3.3-70b-versatile` free tier: 6000 TPM + 100k TPD — exhausted in one heavy session
- `llama-3.1-8b-instant` free tier: 6000 TPM + separate daily quota
- Use 8b-instant as daily driver; reserve 70b for occasional spot-checks; never assume quotas are shared

## [prompt] · Guideline · Word-count chunking is wrong for LLM token limits — use char count
> 2026-03-12 · source: claude-one-digest
- `CHUNK_WORD_LIMIT = 6000` words still produced 6585-token requests — words ≠ tokens (~1.3–1.5x ratio)
- Prompt template overhead (~300 tokens) also counts against the limit
- Use character-based chunking: `CHUNK_CHAR_LIMIT = 10_000` chars ≈ 2500 tokens, leaving headroom for prompt

## [ingest] · Note · `history.jsonl` is prompts-only — not the source of truth for Claude Code sessions
> 2026-03-11 · source: claude-one-digest
- `~/.claude/history.jsonl` contains only user prompts, truncated for display — no assistant responses, no full content
- 106 of 108 sessions in `history.jsonl` are already present in `~/.claude/projects/**/*.jsonl` as full transcripts
- Always use `projects/*.jsonl` for analysis; `history.jsonl` is redundant and less rich

## [llm] · Rule · Small models (8b) need `max_tokens` cap to prevent hallucination loops on list tasks
> 2026-03-13 · source: claude-one-digest
- `llama-3.1-8b-instant` generating a flat concept list entered a repetition loop ("versioning versioning versioning...") with no token cap
- The loop consumes quota, produces garbage output, and can hit rate limits
- Always set `max_tokens` on Groq calls for open-ended list generation; 400 is sufficient for Phase 1 concept extraction

## [prompt] · Guideline · LLM DROP rules unreliable for small models — use Python post-filter instead
> 2026-03-13 · source: claude-one-digest
- `llama-3.1-8b-instant` ignored DROP rules in the MERGE prompt — single-word tokens, path strings, and questions survived after deduplication
- Small models follow inclusion rules better than exclusion rules; DROP logic adds complexity they can't reliably execute
- Move deterministic filtering to Python (short entries, slash commands, known noisy tokens); keep the LLM prompt focused on merging and naming

## [prompt] · Rule · Prompt `{content}` placeholder must be present — missing it sends empty context to the LLM
> 2026-03-13 · source: claude-one-digest
- Both EXTRACT_PROMPT and MERGE_PROMPT lost their `{content}` placeholder after a manual edit — the LLM received the prompt template with no session data and responded as if no input was provided (e.g. "I don't see the list of concepts yet")
- The failure is silent: the pipeline runs without error, but output is garbage
- Always verify `{content}` is present in both the `--- SECTION ---` block and the `.format(content=content)` call; test with `assert '{content}' in PROMPT` if unsure

## [prompt] · Rule · Format example with a literal placeholder name causes the model to output it verbatim
> 2026-03-13 · source: claude-one-digest
- `Format:\n- ConceptName` in the prompt caused the model to output `- ConceptName` as the first line of its response
- The model treats the format example as a template to follow literally, including placeholder text
- Use a real example that looks like actual output (e.g. `- Docker layer caching`) not a generic label

## [ingest] · Rule · Session char cap must cover the full session — 8000 chars cuts off content that starts later
> 2026-03-13 · source: claude-one-digest
- Docker/FastAPI questions in a 30k-char session started at char 11593 — the 8000-char cap silently excluded them all
- Content order in a session is chronological; important questions can appear anywhere, not just at the start
- Use 40000 chars as the cap; Claude Haiku's 200k context window makes this safe and cheap

## [ingest] · Note · Claude Code session duration is unreliable — sessions left open overnight inflate it
> 2026-03-11 · source: claude-one-digest
- Some sessions show 5000+ minute duration because Claude Code was left open without activity
- Duration cannot be used as a signal for session weight or importance
- Use `ts_start` for grouping and filtering; ignore duration entirely in digest logic

## [ingest] · Guideline · Identify high-signal sessions by keyword density, not file size
> 2026-03-13 · source: claude-one-digest
- File size (KB) alone doesn't indicate teaching content — a large session may be mostly tool output and ritual noise
- `grep -c "keyword1\|keyword2" *.jsonl` counts matching lines per file; the highest count reliably identifies the most concept-dense session
- Use keyword density as a fast proxy when scanning for a specific teaching session across multiple files of similar size

## [recap] · Rule · Queue parser must validate date format — comment lines with pipes are silently treated as entries
> 2026-03-13 · source: claude-one-digest
- `Format: \`YYYY-MM-DD | <project> | <description>\`` in queue.md has two `|` characters — parsed as a 3-part entry; `ingest(date="Format: \`YYYY-MM-DD")` crashes with "Invalid date format"
- Any header or comment line containing `|` will be parsed as an entry without a date check
- Always validate the date field matches `YYYY-MM-DD` (len=10, dashes at positions 4 and 7) before processing; skip silently otherwise

## [llm] · Guideline · Strip trailing `(none)` from LLM responses that mix content with a fallback marker
> 2026-03-13 · source: claude-one-digest
- Prompt said "If no concepts, output: (none)" — Claude sometimes appends `(none)` at the end of a response that already contains valid content, treating it as a section terminator
- The stray `(none)` appears in the saved file and confuses readers
- Strip trailing `(none)` after receiving the response: `if result.endswith("(none)"): result = result[:-len("(none)")].rstrip()`

## [prompt] · Rule · LLM outputs reasoning after (none) unless explicitly forbidden
> 2026-03-16 · source: claude-one-digest
- Prompt said "output: (none)" — model output `(none)\n\n**Reasoning:** ...` explaining why no concepts qualified; the reasoning block ends up in the saved file
- Check `result.startswith("(none)")` not just `result == "(none)"` to catch this; also add "output ONLY (none), no reasoning, no explanation" to the prompt

## [recap] · Guideline · Cache recaps by date — skip API call if file already exists
> 2026-03-16 · source: claude-one-digest
- Re-running `digest` on the same date regenerates from the API every time — wasteful and non-deterministic (LLM may classify differently on each call)
- Check if `data/digests/YYYY-MM-DD.md` exists before calling the API; expose `--force` to regenerate explicitly

## [ghostty] · Note · Ghostty tab title overridden by Claude Code's OSC 2 escape — fix via shell integration
> 2026-03-17 · source: claude-one-digest session — outcome pending test
- Goal: show the current folder name (e.g. `claude-one-digest`) as the Ghostty window/tab title
- Attempt 1 (failed): `precmd`/`chpwd` hooks in `.zshrc` sending `\e]2;%1d\a` + `title = ""` in Ghostty config. Works at the shell prompt but Claude Code sends its own `OSC 2` title (`"Claude Code"`) while running, overriding the hook since no prompt is drawn during Claude Code's execution
- Attempt 2 (pending): removed manual hooks; added `shell-integration = zsh` + `shell-integration-features = title` to `~/.config/ghostty/config`. Ghostty tracks CWD via `OSC 7` (separate from `OSC 2`) and may use it as the title independently of what the running app sets
- If attempt 2 fails: only remaining options are (a) wrapping the `claude` command to restore the title at exit (fixes it after Claude Code exits, not during), or (b) accepting the limitation
- → PROMOTE to `LESSONS_ARCHITECTURE.md` as Guideline if attempt 2 is confirmed working

## [recap] · Rule · Read Q&A pairs, not just assistant turns — questions are what make analogies interpretable
> 2026-03-13 · source: claude-one-digest
- A high-quality session recap requires reading both the user question ("is my computer a server?") and the full assistant answer — the question gives the analogy its context and makes the explanation memorable
- Extracting only assistant turns produces correct facts but loses the "why did this concept come up" framing that anchors memory
- Always include both roles when building the recap input; filter noise by content pattern, not by role
