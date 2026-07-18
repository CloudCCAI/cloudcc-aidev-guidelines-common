---
kind: current-status
schema_version: 5
version: 5
init_status: not_started
init_completed_at: none
init_confirmed_by: none
updated_at: {{TIMESTAMP}}
updated_by: onboarding
phase: onboarding
active_task: "none"
active_task_count: 0
active_tasks: []
next_action: "Complete guided project initialization"
read_next:
  goals: true
  decisions: true
  directory_map: true
  devops: true
  task_board: true
---

# Project Current Status

`current-status.md` is the compact hot index. It does not own task progress or design detail.

## Snapshot

- Project mode: `{{PROJECT_MODE}}`
- Phase: `onboarding`
- Active workflows: `0`
- Next action: complete the first unfinished core file

## Active Workflows

No active workflow has been created.

## Read Next

- Read only the first unfinished core file reported by `project-onboarding.py resume`.
- After initialization, load task and feature details only when an active workflow references them.

## Maintenance Rules

- Keep this file under 60 lines.
- Do not create a placeholder task during initialization.
- Rebuild this index from authoritative task and board state.
