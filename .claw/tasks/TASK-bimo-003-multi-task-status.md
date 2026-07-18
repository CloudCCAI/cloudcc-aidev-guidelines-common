---
kind: task-status
schema_version: 5
task_id: TASK-bimo-003
task_type: feature
feature_id: FEAT-bimo-001
policy_version: 2
created_at: 2026-07-18T02:05:46Z
created_by: Bimo
created_by_slug: bimo
created_by_source: git_config_user_name
created_by_developer_id: none
assignee: bimo
owner_slug: bimo
owner_role: shared
status: done
stage: complete
branch: main
assignment_path: none
next_action: none
updated_at: 2026-07-18T03:05:43Z
updated_by: Bimo
---

# TASK-bimo-003 - 多任务热状态

## Current State

- Status: `done`
- Spec: `docs/specs/FEAT-bimo-001-guided-project-management-lifecycle.md`
- Assignment: none
- Next action: none.

## Scope

- Multiple active tasks across users and chat windows.
- Field-level source-of-truth aggregation.
- Atomic current-status regeneration under a project lock.
- Compatibility with legacy singular `active_task` readers.

## Progress

- Implemented field-level aggregation for multiple users, windows, FEATs, tasks, branches, statuses, and next actions.
- Collection, sorting, rendering, and atomic replacement run under one project lock; terminal task truth overrides stale active cards.
- Hot output remains under 60 lines and preserves initialization metadata.

## Verification

- Status: `passed`
- Evidence: all current-status and team-status compatibility tests passed; forward Greenfield test generated two concurrent user workflows.

## Handoff

- Complete. Keep the hot index generated rather than manually appended.
