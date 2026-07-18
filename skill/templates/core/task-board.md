---
kind: task-board
schema_version: 5
version: 5
init_status: not_started
init_completed_at: none
init_confirmed_by: none
updated_at: {{TIMESTAMP}}
updated_by: onboarding
board_status: active
---

# Task Board

`task-board.md` is the compact coordination index. Detailed task state belongs in event-created `.claw/tasks/TASK-*.md` files.

## Active Tasks

No active tasks.

## Completed Tasks

No completed tasks.

## Maintenance Rules

- Initialization must not create a placeholder task.
- Every task card must reference an existing task status file.
- Non-trivial delivery work references an existing feature spec.
- Keep long progress, verification, changed files, and handoff notes out of this index.
