---
kind: test-report
version: 5
updated_at: 2026-07-18T12:41:57Z
updated_by: Bimo
last_run_at: 2026-07-18T12:39:25Z
last_run_status: passed
---

# Test Report

`test-report.md` records real verification evidence. Keep the latest useful result compact.

## Latest Run Summary

- 状态：`passed`
- Scope: `manifest language selection, bilingual templates and generators, v5 lifecycle, and legacy compatibility`
- Commands: 72-test unittest suite; four state fixture validations; pending/zh-CN/en forward projects; Python/Shell/JSON/YAML/frontmatter checks
- Environment: `local workspace`

## Result Summary

| Type | Total | Passed | Failed | Skipped | Coverage |
|------|-------|--------|--------|---------|----------|
| Python unit tests | 72 | 72 | 0 | 0 | n/a |
| Project state fixtures | 4 | 4 | 0 | 0 | n/a |
| Syntax/format checks | 6 | 6 | 0 | 0 | n/a |
| Independent forward-test tracks | 4 | 4 | 0 | 0 | n/a |
| Total | 86 | 86 | 0 | 0 | n/a |

## Failures

- None.

## Notes

- Greenfield, Brownfield, legacy adoption, language pending/resume, English/Chinese generation, module combinations, per-user ID allocation, FEAT confirmation, and multi-workflow aggregation were exercised.
- Standard `quick_validate.py` could not import PyYAML in this environment; the same frontmatter constraints were checked with Ruby YAML and passed.
- Commit/push authorization is release state, not test evidence; no change request or deployment was exercised by this test run.

## Common Commands

- `python3 skill/scripts/validate-state.py .claw`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skill/tests -p 'test_*.py' -v`
- `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-final-pycache python3 -m compileall -q skill/scripts skill/tests`
- `python3 skill/scripts/dev-login.py .claw --ssh-key ~/.ssh/id_ed25519_cc_dev --developer DEV-xxx --task TASK-xxx --files path/to/file`
- `python3 skill/scripts/check-assignment.py .claw --developer DEV-xxx --task TASK-xxx --files path/to/file`

## Maintenance Rules

- Update this file only after a real command runs.
- Keep only the latest useful evidence here.
- Move long historical testing narratives to release notes or dedicated audit artifacts when needed.
