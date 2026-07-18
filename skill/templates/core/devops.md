---
kind: devops
schema_version: 5
version: 5
init_status: not_started
init_completed_at: none
init_confirmed_by: none
updated_at: {{TIMESTAMP}}
updated_by: onboarding
project_mode: {{PROJECT_MODE}}
verification_status: pending
---

<!-- cc-aidev:onboarding-incomplete -->

> Onboarding reference: this marker means the required answers below are not yet confirmed. Write the real project answers, obtain user confirmation, and only then remove the marker before setting `init_status: complete`.

# Build, Run, Test, and Operations

`devops.md` owns verified operational entry points and explicitly identified pending verification.

## Build

- Command: `pending verification`
- Evidence: none

## Run

- Command: `pending verification`
- Entry point: `pending verification`
- Evidence: none

## Test

- Command: `pending verification`
- Evidence: none

## Deployment

- Target: `pending verification`
- Procedure: `pending verification`
- Evidence: none

## Environment and External Services

- Record environment variable names only; never record secret values.
- Required services: `pending verification`

## Operational Boundaries

- Health checks: `pending verification`
- Logs and diagnostics: `pending verification`
- Rollback path: `pending verification`

## Maintenance Rules

- A command may be marked verified only after it was actually run or confirmed by authoritative evidence.
- Initialization may complete with explicit pending verification, but never with invented success evidence.
