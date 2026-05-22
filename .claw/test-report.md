---
kind: test-report
version: 4
updated_at: 2026-05-22T00:00:00Z
updated_by: codex
last_run_at: 2026-05-22T00:00:00Z
last_run_status: passed
---

# Test Report

`test-report.md` records real verification evidence. Keep the latest useful result compact.

## Latest Run Summary

- 状态：`passed`
- Scope: `Codeup CreateChangeRequest payload dry-run, local Codeup config, full-path repository guard, Python syntax, state validation, diff whitespace`
- Commands: Codeup `ListRepositories` lookup for `cloudcc-aidev-guidelines-common`; `python3 scripts/create-codeup-change-request.py --dry-run --source-branch codex/test --title '[TASK-008] dry-run local config'`; `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/create-codeup-change-request.py scripts/store-yunxiao-token.py scripts/check-assignment.py scripts/validate-state.py scripts/summarize-team-status.py scripts/dev-login.py scripts/push-test-environment.py`; `python3 scripts/validate-state.py .claw`; `git diff --check`
- Environment: `local workspace`

## Result Summary

| Type | Total | Passed | Failed | Skipped | Coverage |
|------|-------|--------|--------|---------|----------|
| Codeup dry-run | 4 | 4 | 0 | 0 | n/a |
| Python syntax | 1 | 1 | 0 | 0 | n/a |
| State validation | 1 | 1 | 0 | 0 | n/a |
| Diff whitespace | 1 | 1 | 0 | 0 | n/a |
| Total | 7 | 7 | 0 | 0 | n/a |

## Failures

- None.

## Notes

- Numeric `repositoryId` dry-run included numeric `sourceProjectId` and `targetProjectId` in the payload.
- URL-encoded full-path `repositoryId` without project ids failed with explicit missing project-id guidance.
- URL-encoded full-path `repositoryId` with explicit project ids produced the expected endpoint and payload.
- Codeup `ListRepositories` resolved current repository `cloudcc-aidev-guidelines-common` to repository id `6551067`.
- Local `.claw-local/codeup.env` dry-run used `/repositories/6551067/changeRequests` and body ids `6551067`.

## Common Commands

- `python3 scripts/validate-state.py .claw`
- `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/validate-state.py scripts/summarize-team-status.py scripts/check-assignment.py scripts/dev-login.py`
- `python3 scripts/dev-login.py .claw --ssh-key ~/.ssh/id_ed25519_cc_dev --developer DEV-xxx --task TASK-xxx --files path/to/file`
- `python3 scripts/check-assignment.py .claw --developer DEV-xxx --task TASK-xxx --files path/to/file`

## Maintenance Rules

- Update this file only after a real command runs.
- Keep only the latest useful evidence here.
- Move long historical testing narratives to release notes or dedicated audit artifacts when needed.
