---
kind: devops
schema_version: 5
init_status: complete
init_completed_at: 2026-01-01T00:07:00Z
init_confirmed_by: sample-owner
updated_at: 2026-01-01T00:07:00Z
updated_by: sample-owner
project_mode: greenfield
verification_status: pending
---

# Build, Run, Test, and Operations

- Build: `pending verification`; confirm after the application skeleton exists.
- Run: `pending verification`; planned entry point is `src/api/main.py`.
- Test: `pending verification`; planned runner is pytest.
- Deploy: containerized service and managed PostgreSQL, pending platform selection.
- Environment: record variable names only; never put secret values in this file.
- Next verification action: the first implementation task must run and record the actual commands.
