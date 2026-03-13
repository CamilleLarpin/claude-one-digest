"""
Digest module — group sessions by project, call Claude API, render Markdown.

Usage:
    python src/digest.py --days 1
    python src/digest.py --date 2026-03-12 --dry-run
"""

import argparse
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import anthropic
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from ingest_claude_code import ingest
from models import Session

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-haiku-4-5-20251001"

# Per-turn cap to keep session formatting reasonable
MAX_TURN_CHARS = 400

# Phase 1: extract raw lessons from one session
EXTRACT_PROMPT = """\
You are reviewing a Claude coding session transcript (both Camille's messages and Claude's responses).

Your goal: find ONLY the messages where Camille explicitly asked Claude to explain something for her own understanding.

A qualifying message looks like one of these:
- "What is X?" / "What are X?"
- "How does X work?" / "How do I understand X?"
- "What's the difference between X and Y?"
- "Why do we use X instead of Y?"
- "Can you explain X?"
- "What does X mean?"
- A short follow-up question on a concept just explained ("And X?", "What about X?")

NOT qualifying:
- "Create X", "Add X", "Fix X", "Update X", "Run X" — any action request
- Casual mentions of a tool while working ("let's use X", "X is installed")
- Questions about what Claude just did or is about to do
- Meta questions about the session or workflow
- Commands /xxx

Rules:
- Only extract concepts from Camille's messages — ignore Claude's responses entirely when deciding
- If Camille asked follow-up questions on the same concept, output it once
- Keep concept names explicit and specific 
- If nothing qualifies, output exactly: (none)

Format (one entry per line, dash style):
- Docker layer caching
- FastAPI dependency injection

--- SESSION ---
{content}
--- END ---
"""

# Phase 2: deduplicate, re-explain, and format for Camille
MERGE_PROMPT = """\
You are writing a learning summary for Camille based on concepts she asked about during her Claude coding sessions.

Your job:
- Merge duplicates and near-duplicates into one entry
- For each concept, write a short, clear explanation (2-4 sentences) of how it works
- Group related concepts under a shared heading
- The output is a summary Camille can re-read to consolidate what she learned

Format:
## [Group heading]
**ConceptName** — explanation in plain language

If the input is empty or has no valid concepts, output exactly: (none)

--- CONCEPTS ---
{content}
--- END ---
"""


def format_session(session: Session) -> str:
    lines = [f"[{session.project} | {session.ts_start.strftime('%Y-%m-%d %H:%M')}]"]
    for turn in session.turns:
        prefix = "U" if turn.role == "user" else "C"
        lines.append(f"{prefix}: {turn.text[:MAX_TURN_CHARS]}")
    return "\n".join(lines)


def call_claude(prompt: str, content: str, client: anthropic.Anthropic, max_tokens: int = 400) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt.format(content=content)}],
    )
    return response.content[0].text.strip()


_NOISE_TOKENS = {
    "ls", "cat", "echo", "grep", "find", "cd", "pwd", "curl", "git", "ssh",
    "uv", "pip", "npm", "yarn", "make", "docker", "python", "node", "bash",
}


def _is_noise(concept: str) -> bool:
    """Return True for entries that are clearly not learning concepts."""
    c = concept.lstrip("- ").strip()
    if c.startswith("/"):  # slash command
        return True
    if len(c) < 8:  # too short to be a useful concept
        return True
    words = c.split()
    if len(words) == 1 and c.lower() in _NOISE_TOKENS:
        return True
    # Sentence fragments that start like questions or path-like strings
    if c.startswith(("/", "~", ".")):
        return True
    return False


def extract_lessons_per_session(sessions: list[Session], client: anthropic.Anthropic, verbose: bool = False) -> list[str]:
    """Phase 1: extract raw lessons from each session individually."""
    all_lessons = []
    for i, session in enumerate(sessions):
        label = f"{session.project} | {session.ts_start.strftime('%Y-%m-%d %H:%M')}"
        content = format_session(session)[:40_000]  # ~10k tokens, well within Haiku's 200k ctx
        print(f"  [{i+1}/{len(sessions)}] {label}", file=sys.stderr)
        result = call_claude(EXTRACT_PROMPT, content, client, max_tokens=600)
        if verbose:
            print(f"\n--- {label} ---", file=sys.stderr)
            print(result, file=sys.stderr)
        if result.strip() != "(none)":
            all_lessons.extend(result.splitlines())
    return [l for l in all_lessons if l.strip() and not _is_noise(l)]


def get_tracker_diff_by_project(date: str | None, days: int) -> dict[str, list[str]]:
    """Diff PROJECT_TRACKER.md over the window; return changed lines grouped by project slug."""
    claude_dir = Path.home() / ".claude"

    if date:
        window_start = date
    else:
        window_start = (datetime.now() - timedelta(days=days - 1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).strftime("%Y-%m-%d")

    # Find the last commit before the window
    base = subprocess.run(
        ["git", "rev-list", "-n1", f"--before={window_start}", "HEAD"],
        cwd=claude_dir, capture_output=True, text=True,
    ).stdout.strip()

    if not base:
        return {}

    # Build line→project map from current file
    tracker = (claude_dir / "PROJECT_TRACKER.md").read_text(encoding="utf-8").splitlines()
    line_project: dict[int, str] = {}
    current: str | None = None
    in_projects = False
    for i, line in enumerate(tracker):
        if line.strip() == "## Projects":
            in_projects = True
            continue
        if in_projects and line.startswith("## "):
            in_projects = False
            current = None
            continue
        if in_projects and line.startswith("### "):
            current = line[4:].strip().lower().replace(" ", "-")
        if current:
            line_project[i + 1] = current  # 1-indexed

    # Parse diff using @@ offsets to resolve project
    diff = subprocess.run(
        ["git", "diff", base, "--", "PROJECT_TRACKER.md"],
        cwd=claude_dir, capture_output=True, text=True,
    ).stdout

    changes: dict[str, list[str]] = {}
    new_line = 0

    for line in diff.splitlines():
        if line.startswith(("+++", "---", "diff ", "index ")):
            continue
        if line.startswith("@@"):
            # Extract new-file start line from @@ -a,b +c,d @@
            try:
                new_line = int(line.split("+")[1].split(",")[0].split()[0])
            except (IndexError, ValueError):
                new_line = 0
            continue
        if line.startswith("+"):
            project = line_project.get(new_line)
            content = line[1:].strip()
            if project and content and not content.startswith(">"):
                changes.setdefault(project, []).append(content)
            new_line += 1
        elif line.startswith("-"):
            pass  # removed lines don't advance new-file counter
        else:
            new_line += 1  # context line

    return changes


def render_digest(sessions: list[Session], days: int, client: anthropic.Anthropic, date: str | None = None, verbose: bool = False) -> str:
    groups: dict[str, list[Session]] = defaultdict(list)
    for session in sessions:
        groups[session.project].append(session)

    date_str = date if date else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    label = "today" if days == 1 and not date else date if date else f"last {days}d"
    lines = [
        f"# Daily Digest — {date_str} ({label})",
        f"_{len(sessions)} sessions · {len(groups)} projects_",
        "",
        "---",
        "",
        "## Learnings",
        "",
    ]

    # Phase 1 — extract raw lessons from each session
    print(f"[digest] Phase 1 — extracting lessons from {len(sessions)} sessions...", file=sys.stderr)
    raw_lessons = extract_lessons_per_session(sessions, client, verbose=verbose)

    # Phase 2 — deduplicate and format
    print("[digest] Phase 2 — merging lessons...", file=sys.stderr)
    if not raw_lessons:
        lines.append("(none)")
    else:
        merged = call_claude(MERGE_PROMPT, "\n".join(raw_lessons), client, max_tokens=2000)
        if merged.strip() == "(none)":
            lines.append("(none)")
        else:
            lines.extend(merged.splitlines())

    return "\n".join(lines)


def save_digest(content: str, days: int, date: str | None) -> Path:
    label = date if date else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    suffix = f"--{days}d" if not date and days != 1 else ""
    out_dir = Path(__file__).parent.parent / "data" / "digests"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{label}{suffix}.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate a digest of Claude sessions")
    parser.add_argument("--days", type=int, default=1, help="Look back N calendar days (default: 1 = today)")
    parser.add_argument("--date", type=str, default=None, help="Specific date to digest (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout only, do not save")
    parser.add_argument("--verbose", action="store_true", help="Print per-session extracted lessons to stderr")
    args = parser.parse_args()

    if not ANTHROPIC_API_KEY:
        print("[error] ANTHROPIC_API_KEY not set — add it to .env", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    label = args.date if args.date else f"last {args.days} day(s)"
    print(f"[digest] Ingesting {label}...", file=sys.stderr)
    sessions = ingest(days=args.days, date=args.date)

    if not sessions:
        print("[digest] No sessions found in the given window.", file=sys.stderr)
        sys.exit(0)

    print(f"[digest] {len(sessions)} sessions across {len({s.project for s in sessions})} projects", file=sys.stderr)
    digest = render_digest(sessions, args.days, client, date=args.date, verbose=args.verbose)

    print(digest)

    if not args.dry_run:
        path = save_digest(digest, args.days, args.date)
        print(f"\n[digest] Saved → {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
