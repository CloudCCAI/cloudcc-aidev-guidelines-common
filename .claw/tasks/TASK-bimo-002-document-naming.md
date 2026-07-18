---
kind: task-status
schema_version: 5
task_id: TASK-bimo-002
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

# TASK-bimo-002 - 文档命名与个人编号

## Current State

- Status: `done`
- Spec: `docs/specs/FEAT-bimo-001-guided-project-management-lifecycle.md`
- Assignment: none
- Next action: none.

## Scope

- New FEAT and TASK filename/ID rules with stable author slugs.
- Per-user counters that never reuse allocated values.
- Atomic reservation for concurrent chats.
- New/legacy ID coexistence and event templates.

## Progress

- Implemented stable username slugs, separate per-user FEAT/TASK counters, locked atomic allocation, canonical template rendering, and non-reused reservations.
- Implemented dual legacy/v5 ID parsing, numeric-owner edge cases, immutable legacy snapshots, and explicit adoption boundaries.
- TASK allocation and strict validation reject references to unconfirmed v5 FEAT documents.

## Verification

- Status: `passed`
- Evidence: document-ID, concurrent allocation, Codeup parsing, legacy snapshot, and legacy adoption regression suites passed.

## Handoff

- Complete. Attribution remains separate from collaboration-gate authorization.
