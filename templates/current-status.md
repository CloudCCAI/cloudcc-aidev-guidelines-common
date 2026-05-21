---
kind: current-status
version: 4
updated_at: YYYY-MM-DDTHH:MM:SSZ
updated_by: ai
phase: bootstrap
active_task: "TASK-001"
next_action: "Create the first task status file and link it from task-board.md"
read_next:
  goals: true
  decisions: false
  issue_list: false
  task_board: true
  active_task_status: true
  test_report: false
  devops: false
---

# Project Current Status

`current-status.md` is the hot index. Rewrite it as the latest snapshot; do not append session history.

## Snapshot

- Goal: establish compact project state and first executable task
- Focus: `TASK-001`
- Blocked: none
- Latest verification: `not_run`

## Read Next

- `.claw/task-board.md` - compact task index
- `.claw/tasks/TASK-001.md` - current task state
- `docs/specs/FEAT-xxx-feature-name.md` - only when the active task references a real spec

## Maintenance Rules

- Keep this file under 60 lines.
- Keep historical progress out of this file.
- Put task progress, verification, changed files, and handoff notes in `.claw/tasks/TASK-xxx.md`.
- Put feature requirements, design, and acceptance criteria in `docs/specs/`.
- Put real test evidence in `.claw/test-report.md`.
