"""
Session recap generator — processes flagged sessions from data/queue.md

Usage:
    python src/session_recap.py --queue
    python src/session_recap.py --queue --dry-run
    python src/session_recap.py --queue --verbose
"""

import argparse
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from ingest_claude_code import ingest
from models import Session

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-haiku-4-5-20251001"
MAX_TURN_CHARS = 600
MAX_SESSION_CHARS = 40_000

QUEUE_PATH = Path(__file__).parent.parent / "data" / "queue.md"
DIGESTS_DIR = Path(__file__).parent.parent / "data" / "digests"

RECAP_PROMPT = """\
You are writing a session recap for Camille based on a Claude Code session transcript.

Your goal: extract every concept Camille explicitly asked to have explained, and write a clear re-explanation for each.

A qualifying question looks like:
- "What is X?" / "What are X?"
- "How does X work?" / "How do I understand X?"
- "What's the difference between X and Y?"
- "Why do we use X instead of Y?"
- "Can you explain X?"
- A short follow-up question on a concept just explained

NOT qualifying:
- Action requests ("Create X", "Fix X", "Update X")
- Questions about what Claude just did
- Meta questions about the session or workflow

Rules:
- Group related concepts under a shared heading
- For each concept: re-explain in plain language (2-4 sentences)
- Preserve the exact analogy used in the conversation — do not substitute a generic explanation
- Include the triggering question Camille asked

Format:
## [Group heading]

**ConceptName**
> Q: Camille's exact question
Plain-language explanation. Include the analogy from the conversation here.

If no concepts were taught, output: (none)

--- SESSION TRANSCRIPT ---
{content}
--- END ---
"""


def parse_queue(path: Path) -> list[tuple[int, str, str, str]]:
    """Return (line_index, date, project_slug, description) for each unprocessed entry."""
    entries = []
    if not path.exists():
        return entries
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("---") or stripped.startswith("[x]"):
            continue
        parts = [p.strip() for p in stripped.split("|")]
        if len(parts) != 3:
            continue
        date, project, description = parts
        # Validate date looks like YYYY-MM-DD before treating as a real entry
        if len(date) != 10 or date[4] != "-" or date[7] != "-":
            continue
        entries.append((i, date, project, description))
    return entries


def mark_done(path: Path, line_indices: list[int]) -> None:
    """Prefix processed lines with [x] in queue.md."""
    lines = path.read_text(encoding="utf-8").splitlines()
    for i in line_indices:
        if i < len(lines) and not lines[i].startswith("[x]"):
            lines[i] = "[x] " + lines[i]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def is_noise(text: str) -> bool:
    """Return True for ritual/command turns that should be excluded from the transcript."""
    if not text or len(text.strip()) < 5:
        return True
    t = text.strip()
    if t.startswith("/"):
        return True
    if "<command-name>" in t or "<command-message>" in t or "<local-command-caveat>" in t:
        return True
    return False


def format_transcript(sessions: list[Session]) -> str:
    """Format sessions as a labelled Q&A transcript for the recap prompt."""
    lines = []
    for session in sessions:
        lines.append(f"[{session.project} | {session.ts_start.strftime('%Y-%m-%d %H:%M')}]")
        for turn in session.turns:
            if is_noise(turn.text):
                continue
            prefix = "Camille" if turn.role == "user" else "Claude"
            lines.append(f"{prefix}: {turn.text[:MAX_TURN_CHARS]}")
    return "\n".join(lines)[:MAX_SESSION_CHARS]


def call_claude(prompt: str, content: str, client: anthropic.Anthropic) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt.format(content=content)}],
    )
    return response.content[0].text.strip()


def process_entry(
    date: str,
    project: str,
    description: str,
    client: anthropic.Anthropic,
    dry_run: bool,
    verbose: bool,
) -> bool:
    """Process one queue entry. Returns True on success (including no-concept sessions)."""
    print(f"[recap] {date} | {project}", file=sys.stderr)

    sessions = ingest(date=date)
    matching = [s for s in sessions if s.project == project]

    if not matching:
        print(f"  [warn] No sessions found for {project} on {date}", file=sys.stderr)
        return False

    total_turns = sum(len(s.turns) for s in matching)
    print(f"  Found {len(matching)} session(s), {total_turns} turns", file=sys.stderr)

    transcript = format_transcript(matching)
    if verbose:
        preview = transcript[:2000]
        print(f"\n--- TRANSCRIPT PREVIEW ---\n{preview}\n{'...' if len(transcript) > 2000 else ''}", file=sys.stderr)

    result = call_claude(RECAP_PROMPT, transcript, client)
    # Strip trailing (none) that Claude sometimes appends after listing concepts
    result = result.rstrip()
    if result.endswith("(none)"):
        result = result[:-len("(none)")].rstrip()

    if verbose:
        print(f"\n--- RECAP ---\n{result}\n", file=sys.stderr)

    if result.strip() == "(none)" or not result.strip():
        print("  [info] No qualifying concepts found — skipping save", file=sys.stderr)
        return True

    header = f"# Session Recap — {date} · {project}\n_{description}_\n\n---\n\n"
    output = header + result

    if dry_run:
        print(output)
        return True

    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DIGESTS_DIR / f"{date}_{project}.md"
    out_path.write_text(output, encoding="utf-8")
    print(f"  Saved → {out_path}", file=sys.stderr)
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate session recaps from queue")
    parser.add_argument("--queue", action="store_true", help="Process all unprocessed entries in data/queue.md")
    parser.add_argument("--dry-run", action="store_true", help="Print output, do not save or mark done")
    parser.add_argument("--verbose", action="store_true", help="Print transcript preview and raw recap to stderr")
    args = parser.parse_args()

    if not args.queue:
        print("[error] Specify --queue", file=sys.stderr)
        sys.exit(1)

    if not ANTHROPIC_API_KEY:
        print("[error] ANTHROPIC_API_KEY not set — add it to .env", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    entries = parse_queue(QUEUE_PATH)
    if not entries:
        print("[recap] Queue is empty or all entries already processed.", file=sys.stderr)
        sys.exit(0)

    print(f"[recap] {len(entries)} entries to process", file=sys.stderr)

    done_indices = []
    for line_idx, date, project, description in entries:
        ok = process_entry(date, project, description, client, dry_run=args.dry_run, verbose=args.verbose)
        if ok and not args.dry_run:
            done_indices.append(line_idx)

    if done_indices and not args.dry_run:
        mark_done(QUEUE_PATH, done_indices)
        print(f"[recap] Marked {len(done_indices)} entries done in queue.md", file=sys.stderr)

    print("[recap] Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
