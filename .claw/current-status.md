---
kind: current-status
version: 4
updated_at: 2026-05-22T01:00:00Z
updated_by: codex
phase: review
active_task: "TASK-008"
next_action: "Commit and push Codeup local default configurator release 4.1.2"
read_next:
  goals: false
  decisions: true
  issue_list: false
  task_board: true
  active_task_status: true
  test_report: true
  devops: false
---

# Project Current Status

`current-status.md` is the hot index. Rewrite it as the latest snapshot; do not append session history.

## Snapshot

- Goal: make Codeup local change request defaults configurable for every adopting project.
- Focus: `TASK-008`
- Blocked: none
- Latest verification: `configure-codeup-change-request.py` dry-run passed for current repo id `6551067` and explicit repo id fallback; Python syntax passed.

## Read Next

- `.claw/task-board.md` - compact task index
- `.claw/tasks/TASK-008.md` - current task state and handoff
- `docs/specs/FEAT-008-codeup-change-request-submission.md` - Codeup create request design
- `.claw/test-report.md` - latest validation evidence

## Maintenance Rules

- Keep this file under 60 lines.
- Put task progress, changed files, verification, and handoff in `.claw/tasks/TASK-xxx.md`.
- Put feature requirements, design, and acceptance criteria in `docs/specs/`.
- Put real test evidence in `.claw/test-report.md`.
