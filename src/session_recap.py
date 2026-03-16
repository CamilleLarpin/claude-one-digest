"""
Session recap generator — processes sessions flagged in data/learning_log.md

Usage:
    python src/session_recap.py --date 2026-03-13
    python src/session_recap.py --date 2026-03-13 --dry-run
    python src/session_recap.py --date 2026-03-13 --verbose
    python src/session_recap.py --date today
"""

import argparse
import os
import sys
from datetime import date as date_type
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

LEARNING_LOG_PATH = Path(__file__).parent.parent / "data" / "learning_log.md"
DIGESTS_DIR = Path(__file__).parent.parent / "data" / "digests"

RECAP_PROMPT = """\
You are writing a learning recap for Camille based on a Claude Code session transcript.

Your goal: extract only generic, transferable technical concepts that Camille asked to have explained — things she could apply in any future project, regardless of context.

A concept qualifies if:
- It is a general technical concept (how a tool, protocol, or system works)
- The explanation would be useful to any developer, not just in this specific project
- Camille explicitly asked "What is X?", "How does X work?", "What's the difference between X and Y?", "Why do we use X instead of Y?", or asked a follow-up on a concept just explained

A concept does NOT qualify if:
- It is project-specific analysis ("which project should I choose", "how should I structure this feature")
- It is a project decision or recommendation ("use X instead of Y for this project")
- It is a question about what Claude just did or produced
- It is an action request ("create X", "fix X", "update X")
- The explanation only makes sense in the context of this specific project or session

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

If no qualifying concepts were found, output exactly: (none)
Do not explain why. Do not add reasoning. Output only (none) and nothing else.

--- SESSION TRANSCRIPT ---
{content}
--- END ---
"""


def parse_learning_log(path: Path, date: str) -> list[tuple[str, str, str]]:
    """Return (date, project_slug, description) for entries matching the given date."""
    entries = []
    if not path.exists():
        return entries
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("---"):
            continue
        parts = [p.strip() for p in stripped.split("|")]
        if len(parts) != 3:
            continue
        entry_date, project, description = parts
        if entry_date != date:
            continue
        entries.append((entry_date, project, description))
    return entries


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
    verbose: bool,
) -> str | None:
    """Process one learning log entry. Returns recap text on success, None if no concepts found."""
    print(f"[recap] {date} | {project}", file=sys.stderr)

    sessions = ingest(date=date)
    matching = [s for s in sessions if s.project == project]

    if not matching:
        print(f"  [warn] No sessions found for {project} on {date}", file=sys.stderr)
        return None

    total_turns = sum(len(s.turns) for s in matching)
    print(f"  Found {len(matching)} session(s), {total_turns} turns", file=sys.stderr)

    transcript = format_transcript(matching)
    if verbose:
        preview = transcript[:2000]
        print(f"\n--- TRANSCRIPT PREVIEW ---\n{preview}\n{'...' if len(transcript) > 2000 else ''}", file=sys.stderr)

    result = call_claude(RECAP_PROMPT, transcript, client)
    result = result.strip()
    # Handle (none) whether it appears alone, at start, or at end
    if result.startswith("(none)") or result.endswith("(none)") or result == "(none)":
        result = ""

    if verbose:
        print(f"\n--- RECAP ---\n{result}\n", file=sys.stderr)

    if not result.strip():
        print("  [info] No qualifying concepts found", file=sys.stderr)
        return None

    return result


def main():
    parser = argparse.ArgumentParser(description="Generate session recaps from learning log")
    parser.add_argument("--date", type=str, required=True, help="Date to process (YYYY-MM-DD or 'today')")
    parser.add_argument("--dry-run", action="store_true", help="Print output, do not save")
    parser.add_argument("--force", action="store_true", help="Regenerate even if recap already exists")
    parser.add_argument("--verbose", action="store_true", help="Print transcript preview and raw recap to stderr")
    args = parser.parse_args()

    target_date = str(date_type.today()) if args.date == "today" else args.date

    out_path = DIGESTS_DIR / f"{target_date}.md"
    if out_path.exists() and not args.force and not args.dry_run:
        print(f"[recap] Recap already exists for {target_date} — use --force to regenerate.", file=sys.stderr)
        print(str(out_path))
        return

    if not ANTHROPIC_API_KEY:
        print("[error] ANTHROPIC_API_KEY not set — add it to .env", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    entries = parse_learning_log(LEARNING_LOG_PATH, target_date)
    if not entries:
        print(f"[recap] No entries in learning_log.md for {target_date}.", file=sys.stderr)
        sys.exit(0)

    # Group by (date, project) — multiple entries for same project are merged into one recap
    groups: dict[tuple[str, str], list[str]] = {}
    for entry_date, project, description in entries:
        key = (entry_date, project)
        groups.setdefault(key, []).append(description)

    print(f"[recap] {len(groups)} project(s) to process for {target_date}", file=sys.stderr)

    sections = []
    for (entry_date, project), descriptions in groups.items():
        recap_text = process_entry(entry_date, project, " · ".join(descriptions), client, verbose=args.verbose)
        if recap_text:
            sections.append(f"## {project}\n\n{recap_text}")

    if not sections:
        print("[recap] Done. No qualifying concepts found.", file=sys.stderr)
        return

    combined = f"# Learning Recap — {target_date}\n\n---\n\n" + "\n\n---\n\n".join(sections)

    if args.dry_run:
        print(combined)
        return

    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DIGESTS_DIR / f"{target_date}.md"
    out_path.write_text(combined, encoding="utf-8")
    print(f"[recap] Done. Saved → {out_path}", file=sys.stderr)
    print(str(out_path))


if __name__ == "__main__":
    main()
