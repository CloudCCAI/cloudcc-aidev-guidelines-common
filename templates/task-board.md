---
kind: task-board
version: 4
updated_at: YYYY-MM-DDTHH:MM:SSZ
updated_by: ai
board_status: active
---

# Task Board

`task-board.md` is a compact index. Each task keeps its detailed state in `.claw/tasks/TASK-xxx.md`.

Recommended statuses: `todo` / `ready` / `in_progress` / `blocked` / `review` / `done` / `canceled`
Recommended priorities: `critical` / `high` / `medium` / `low`

## Active Tasks

### TASK-001 - Establish the first delivery slice

- status: `ready`
- priority: `high`
- owner_role: `shared`
- spec_path: `none`
- task_status_path: `.claw/tasks/TASK-001.md`
- assignment_path: `none`
- depends_on: `none`
- blocked_by: `none`
- next_action: `Fill .claw/tasks/TASK-001.md with the current task state`

## Completed Tasks

- None.

## Maintenance Rules

- Keep each task card under 20 lines.
- Store only index fields here.
- Store current task details in `.claw/tasks/TASK-xxx.md`.
- Store old completed or canceled task cards in `.claw/task-archive.md`.
