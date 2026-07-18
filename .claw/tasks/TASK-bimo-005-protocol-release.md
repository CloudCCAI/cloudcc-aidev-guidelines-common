---
kind: task-status
schema_version: 5
task_id: TASK-bimo-005
task_type: documentation
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
updated_at: 2026-07-18T03:10:11Z
updated_by: Bimo
---

# TASK-bimo-005 - 协议整合与发布准备

## Current State

- Status: `done`
- Spec: `docs/specs/FEAT-bimo-001-guided-project-management-lifecycle.md`
- Assignment: none
- Next action: none.

## Scope

- Keep `SKILL.md` concise and move detailed module/platform rules into references.
- Align STATE-MODEL, templates, scripts, examples, root guidance, and changelog.
- Run forward tests and end-to-end validation.
- Bump the skill version only after implementation is complete.

## Progress

- Reworked `SKILL.md` into the v5 router and moved onboarding, module, and platform detail into progressive references.
- Aligned STATE-MODEL, catalog, schemas, templates, scripts, examples, README, changelog, and project state at version `5.0.0`.
- Removed every old project-state directory literal; only `.claw/` and ignored `.claw-local/` remain.
- Completed three independent forward-test tracks and fixed all reported inconsistencies.

## Verification

- Status: `passed`
- Evidence: 67 unit tests, four project-state fixture validations, Python/Shell/workflow syntax, Skill frontmatter, old-path scan, and `git diff --check` passed.

## Handoff

- Complete. The implementation is release-ready; publishing/commit remains a separate user action.
