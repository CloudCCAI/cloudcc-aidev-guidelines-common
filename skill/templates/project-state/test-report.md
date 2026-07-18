---
kind: test-report
schema_version: 5
updated_at: {{TIMESTAMP}}
updated_by: "{{UPDATED_BY}}"
last_run_at: {{TIMESTAMP}}
last_run_status: {{TEST_STATUS}}
---

# Test Report

Create `test-report.md` only after a real command, CI job, or equivalent validation runs.

## Latest Run Summary

- Status: `{{TEST_STATUS}}`
- Scope: {{TEST_SCOPE}}
- Command: `{{TEST_COMMAND}}`
- Environment: {{TEST_ENVIRONMENT}}
- Evidence: {{TEST_EVIDENCE}}

## Result Summary

- Passed: {{PASSED_COUNT}}
- Failed: {{FAILED_COUNT}}
- Skipped: {{SKIPPED_COUNT}}

## Failures

- {{FAILURE_SUMMARY}}

## Maintenance Rules

- Never report an unexecuted validation as passed.
- Current status references only the latest summary and does not copy full evidence.
