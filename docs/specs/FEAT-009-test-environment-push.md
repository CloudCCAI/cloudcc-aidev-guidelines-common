---
kind: feature-spec
feature_id: FEAT-009
title: Test environment branch push
status: implemented
owner_role: shared
task_ids: TASK-009
related_decisions: ADR-009
related_issues: none
updated_at: 2026-05-20T00:00:00Z
updated_by: codex
---

# FEAT-009 - Test environment branch push

## Requirement

When a user says "push to the test environment", the skill should guide the agent to merge the active development branch into `dev`, automatically resolve conflicts, and push `dev` to the remote test environment branch.

## Design

- Add `skill/scripts/push-test-environment.py` as the standard helper.
- Default source branch: current Git branch.
- Default target branch: `dev`.
- Default remote: `origin`.
- Require a clean working tree before switching branches.
- Fetch the remote, check out `dev`, fast-forward it from `origin/dev`, merge the source branch, and push `dev`.
- Conflict policy: testing deployment prefers the development branch version. The script first uses `git merge -X theirs`; if unmerged paths remain, it resolves each conflicted path from the source side and commits the merge.
- Restore the original branch after a successful push unless `--no-restore` is passed.

## Acceptance Criteria

- The protocol documents the "push to test environment" trigger.
- The helper can show a dry-run plan without changing the repository.
- The helper can merge a development branch into `dev` and push `dev`.
- Conflict handling is deterministic and documented as source-branch-wins for test deployment.
- Existing validation still passes.

## Verification

- `python3 skill/scripts/push-test-environment.py --help`
- `python3 skill/scripts/push-test-environment.py --dry-run --source-branch feature/example --target-branch dev --remote origin`
- `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile skill/scripts/push-test-environment.py`
- `python3 skill/scripts/validate-state.py .claw`
