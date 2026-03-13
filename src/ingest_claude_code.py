"""
Ingest Claude Code sessions from ~/.claude/projects/**/*.jsonl

Usage:
    python src/ingest_claude_code.py --days 1
    python src/ingest_claude_code.py --days 7
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from models import Session, Turn


PROJECTS_DIR = Path.home() / ".claude" / "projects"


def extract_text(content) -> str:
    """Extract plain text from a message content field. Strip tool blocks."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = [
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "\n".join(parts).strip()
    return ""


def project_slug_from_cwd(cwd: str) -> str:
    """Derive a readable project name from a cwd path."""
    if not cwd:
        return "unknown"
    parts = Path(cwd).parts
    # Return last path component (project folder name)
    return parts[-1] if parts else cwd


def load_sessions_from_file(jsonl_path: Path) -> dict[str, Session]:
    """Parse one .jsonl transcript file into a dict of session_id → Session."""
    sessions: dict[str, Session] = {}

    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get("type")
            if entry_type not in ("user", "assistant"):
                continue  # skip file-history-snapshot and other metadata

            message = entry.get("message")
            if not message:
                continue

            text = extract_text(message.get("content", ""))
            if not text:
                continue  # skip empty turns (e.g. tool-only messages)

            session_id = entry.get("sessionId", str(jsonl_path.stem))
            ts_raw = entry.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                ts = datetime.now(timezone.utc)

            if session_id not in sessions:
                cwd = entry.get("cwd", "")
                sessions[session_id] = Session(
                    session_id=session_id,
                    source="claude-code",
                    project=project_slug_from_cwd(cwd),
                    ts_start=ts,
                    ts_end=ts,
                    turns=[],
                )

            session = sessions[session_id]
            session.turns.append(Turn(role=message["role"], text=text, timestamp=ts))
            if ts < session.ts_start:
                session.ts_start = ts
            if ts > session.ts_end:
                session.ts_end = ts

    return sessions


def ingest(days: int = 1, date: str | None = None) -> list[Session]:
    """Load Claude Code sessions for a time window.

    - date="YYYY-MM-DD": sessions from midnight to midnight of that specific day
    - days=N: sessions from midnight N calendar days ago until now
    """
    now_local = datetime.now().astimezone()

    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d").astimezone()
        except ValueError:
            print(f"[error] Invalid date format '{date}' — expected YYYY-MM-DD", file=sys.stderr)
            sys.exit(1)
        cutoff_start = d.replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_end = cutoff_start + timedelta(days=1)
    else:
        cutoff_start = (now_local - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_end = None  # no upper bound

    all_sessions: dict[str, Session] = {}

    if not PROJECTS_DIR.exists():
        print(f"[error] Projects dir not found: {PROJECTS_DIR}", file=sys.stderr)
        return []

    for jsonl_path in PROJECTS_DIR.glob("*/*.jsonl"):
        file_sessions = load_sessions_from_file(jsonl_path)
        for sid, session in file_sessions.items():
            if session.ts_end >= cutoff_start:
                if cutoff_end is None or session.ts_start < cutoff_end:
                    if sid not in all_sessions:
                        all_sessions[sid] = session

    return sorted(all_sessions.values(), key=lambda s: s.ts_start)


def print_summary(sessions: list[Session]) -> None:
    print(f"\n{'='*60}")
    print(f"Claude Code sessions — {len(sessions)} found")
    print(f"{'='*60}")
    for s in sessions:
        print(
            f"  [{s.ts_start.strftime('%Y-%m-%d %H:%M')}] "
            f"{s.project:<30} "
            f"{len(s.turns):>3} turns  "
            f"{s.word_count:>5} words  "
            f"{s.duration_minutes:>5.0f}m"
        )
    total_words = sum(s.word_count for s in sessions)
    total_turns = sum(len(s.turns) for s in sessions)
    print(f"{'='*60}")
    print(f"  Total: {total_turns} turns, {total_words:,} words across {len(sessions)} sessions")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Claude Code sessions")
    parser.add_argument("--days", type=int, default=1, help="Look back N calendar days (default: 1 = today)")
    parser.add_argument("--date", type=str, default=None, help="Specific date (YYYY-MM-DD)")
    args = parser.parse_args()

    sessions = ingest(days=args.days, date=args.date)
    print_summary(sessions)
