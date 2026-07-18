---
kind: team-status
schema_version: 5
updated_at: {{TIMESTAMP}}
updated_by: summarize-team-status
status: derived
---

# Team Status Summary

`team-status.md` is an on-demand manager view, not a source of truth.

## Aggregation Rules

1. `.claw/developers/*.yaml`
2. `.claw/assignments/*.yaml`
3. `.claw/tasks/*.md`
4. `.claw/task-board.md`
5. `.claw/integration-queue.md`

## Team Overview

| Metric | Count |
|---|---:|
| Developers | 0 |
| Active developers | 0 |
| Assigned tasks | 0 |
| Blocked tasks | 0 |

## Member Status

- Run `python3 scripts/summarize-team-status.py .claw --write` to generate the real view.
