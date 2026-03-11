# Context — [PROJECT NAME]

> CONTAINS: current state, architecture overview, file structure, key dependencies.
> NOT HERE: decisions with rationale (→ DECISIONS.md), todos (→ TODOS.md), solution design (→ DESIGN.md).
> Update this file when architecture changes or a milestone completes.
> Load tier: warm

---

## Current State
**As of**: [YYYY-MM-DD]
[2-3 sentences: where the project stands right now, what is working, what is not]

## Architecture
[Diagram or description of how components connect. Be specific about data flow.]

```
[e.g. Webhook → n8n → Claude API → GitHub → response]
```

## File Structure
```
[project-slug]/
  .claude/          # context files
  [src or main folder]/
  [other key folders]
```

## Key Dependencies
| Dependency | Version/URL | Purpose |
|---|---|---|
| [e.g. n8n] | [self-hosted] | [orchestration] |

## Environment
- **Dev**: [how to run locally]
- **Prod**: [where it runs]
- **Credentials**: [pointer only — e.g. "n8n credentials: OpenAI_Prod"]
