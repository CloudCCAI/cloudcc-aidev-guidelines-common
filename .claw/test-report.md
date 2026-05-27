---
kind: test-report
version: 4
updated_at: 2026-05-27T09:21:22Z
updated_by: codex
last_run_at: 2026-05-27T09:21:22Z
last_run_status: passed
---

# Test Report

`test-report.md` records real verification evidence. Keep the latest useful result compact.

## Latest Run Summary

- 状态：`passed`
- Scope: `release 4.1.3, bare directory write-root matching, protected-path recursion, exact scope_files behavior, Python syntax, state validation, diff whitespace`
- Commands: temporary assignment fixture with `allowed_write_roots: frontend/src`; temporary exact `scope_files` fixture; `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/check-assignment.py scripts/dev-login.py scripts/validate-state.py`; `python3 scripts/validate-state.py .claw`; `git diff --check`
- Environment: `local workspace`

## Result Summary

| Type | Total | Passed | Failed | Skipped | Coverage |
|------|-------|--------|--------|---------|----------|
| Assignment fixture | 3 | 3 | 0 | 0 | n/a |
| Python syntax | 1 | 1 | 0 | 0 | n/a |
| State validation | 1 | 1 | 0 | 0 | n/a |
| Diff whitespace | 1 | 1 | 0 | 0 | n/a |
| Total | 6 | 6 | 0 | 0 | n/a |

## Failures

- None.

## Notes

- `allowed_write_roots: frontend/src` allowed nested files under `frontend/src/...`.
- Bare `protected_paths: .claw/assignments` still blocked `.claw/assignments/TASK-138.yaml` unless explicitly listed in `scope_files`.
- Exact `scope_files: docs/specs/FEAT-138.md` allowed that file but did not allow `docs/specs/FEAT-138.md.bak`.
- State validation passed after updating `.claw/current-status.md`, `.claw/tasks/TASK-007.md`, and `.claw/test-report.md`.

## Common Commands

- `python3 scripts/validate-state.py .claw`
- `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/validate-state.py scripts/summarize-team-status.py scripts/check-assignment.py scripts/dev-login.py`
- `python3 scripts/dev-login.py .claw --ssh-key ~/.ssh/id_ed25519_cc_dev --developer DEV-xxx --task TASK-xxx --files path/to/file`
- `python3 scripts/check-assignment.py .claw --developer DEV-xxx --task TASK-xxx --files path/to/file`

## Maintenance Rules

- Update this file only after a real command runs.
- Keep only the latest useful evidence here.
- Move long historical testing narratives to release notes or dedicated audit artifacts when needed.
