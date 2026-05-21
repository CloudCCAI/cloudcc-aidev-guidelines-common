---
kind: task-board
version: 4
updated_at: 2026-05-21T07:05:27Z
updated_by: codex
board_status: active
---

# Task Board

`task-board.md` is a compact task index. Each active task links to one task status file.

## Active Tasks

### TASK-001 - Add project-root skill declaration automation

- status: `review`
- priority: `high`
- owner_role: `fullstack-agent`
- spec_path: `docs/specs/FEAT-001-project-skill-declaration.md`
- task_status_path: `.claw/tasks/TASK-001.md`
- assignment_path: `none`
- depends_on: `none`
- blocked_by: `none`
- next_action: `User review declaration automation behavior`

### TASK-002 - Add identity-based asynchronous parallel delivery protocol

- status: `review`
- priority: `high`
- owner_role: `shared`
- spec_path: `docs/specs/FEAT-002-identity-parallel-delivery.md`
- task_status_path: `.claw/tasks/TASK-002.md`
- assignment_path: `none`
- depends_on: `none`
- blocked_by: `none`
- next_action: `User review identity parallel delivery protocol`

### TASK-003 - Add standard team status aggregation

- status: `review`
- priority: `high`
- owner_role: `shared`
- spec_path: `docs/specs/FEAT-003-team-status-aggregation.md`
- task_status_path: `.claw/tasks/TASK-003.md`
- assignment_path: `none`
- depends_on: `TASK-002`
- blocked_by: `none`
- next_action: `User review team status aggregation output`

### TASK-004 - Add project-manager-gated team authorization

- status: `review`
- priority: `high`
- owner_role: `shared`
- spec_path: `docs/specs/FEAT-004-project-manager-gated-authorization.md`
- task_status_path: `.claw/tasks/TASK-004.md`
- assignment_path: `none`
- depends_on: `TASK-002, TASK-003`
- blocked_by: `none`
- next_action: `User review manager-gated authorization behavior`

### TASK-005 - Add local SSH challenge-response developer login

- status: `review`
- priority: `high`
- owner_role: `shared`
- spec_path: `docs/specs/FEAT-005-local-identity-login.md`
- task_status_path: `.claw/tasks/TASK-005.md`
- assignment_path: `none`
- depends_on: `TASK-004`
- blocked_by: `none`
- next_action: `User review local identity login flow`

### TASK-006 - Harden local identity login as mandatory pre-edit gate

- status: `review`
- priority: `critical`
- owner_role: `shared`
- spec_path: `docs/specs/FEAT-006-hard-identity-gate.md`
- task_status_path: `.claw/tasks/TASK-006.md`
- assignment_path: `none`
- depends_on: `TASK-005`
- blocked_by: `none`
- next_action: `User review hard identity gate rules`

### TASK-007 - Add task-bounded broad code authorization

- status: `review`
- priority: `critical`
- owner_role: `shared`
- spec_path: `docs/specs/FEAT-007-task-bounded-broad-code-authorization.md`
- task_status_path: `.claw/tasks/TASK-007.md`
- assignment_path: `none`
- depends_on: `TASK-006`
- blocked_by: `none`
- next_action: `User review broad code authorization model`

### TASK-008 - Add Codeup change request submission flow

- status: `review`
- priority: `high`
- owner_role: `shared`
- spec_path: `docs/specs/FEAT-008-codeup-change-request-submission.md`
- task_status_path: `.claw/tasks/TASK-008.md`
- assignment_path: `none`
- depends_on: `TASK-007`
- blocked_by: `none`
- next_action: `User review Codeup change request defaults`

### TASK-009 - Add test environment branch push flow

- status: `review`
- priority: `high`
- owner_role: `shared`
- spec_path: `docs/specs/FEAT-009-test-environment-push.md`
- task_status_path: `.claw/tasks/TASK-009.md`
- assignment_path: `none`
- depends_on: `TASK-008`
- blocked_by: `none`
- next_action: `User review source-branch-wins test deploy policy`

### TASK-010 - Add progressive state indexing and per-task status files

- status: `review`
- priority: `critical`
- owner_role: `shared`
- spec_path: `docs/specs/FEAT-010-progressive-state-indexing.md`
- task_status_path: `.claw/tasks/TASK-010.md`
- assignment_path: `none`
- depends_on: `TASK-009`
- blocked_by: `none`
- next_action: `User review progressive state indexing model`

## Completed Tasks

- None.

## Maintenance Rules

- Keep each task card under 20 lines.
- Store current task details in `.claw/tasks/TASK-xxx.md`.
- Store feature design in `docs/specs/` and validation evidence in `.claw/test-report.md`.
