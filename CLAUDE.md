# claude-one-digest — Claude Context

> Load tier: hot

@~/.claude/CLAUDE.md

## Project
**Purpose**: Merge conversations from Claude Code, Claude Desktop, and claude.ai into a single pipeline and run daily analytics to surface what was learned and achieved.
**Status**: 🔵 Building
**Repo**: https://github.com/CamilleLarpin/claude-one-digest
**Stack**: TBD

## Context Files
- .claude/CONTEXT.md — current state, architecture, file structure, key dependencies
- .claude/DECISIONS.md — active decisions only (resolved → DECISIONS_ARCHIVE.md); always load alongside ~/.claude/DECISIONS_GLOBAL.md
- .claude/LESSONS.md — what to avoid: mistakes, patterns, gotchas (never delete); always load ~/.claude/LESSONS_GLOBAL.md index + relevant category files for current task domain
- .claude/DESIGN.md — problem space, use cases, user flows, solution approach, non-goals
- .claude/TODOS.md — active milestones, next actions, blocked items

## Active Constraints
- No secrets in repo — all credentials in .env or external secret store

## Quick Reference
- Notion: https://www.notion.so/Track-Conversations-for-Learning-Insights-320fef9576f1818389e5faf472504c42

## Current Focus
Building digest module — group sessions by project, call Groq API (llama-3.1-8b-instant), render Markdown output to stdout + store in data/digests/.
