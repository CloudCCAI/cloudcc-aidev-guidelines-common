---
kind: decisions
schema_version: 5
init_status: complete
init_completed_at: 2026-01-02T00:07:00Z
init_confirmed_by: sample-maintainer
architecture_init_status: complete
architecture_reviewed_at: 2026-01-02T00:07:00Z
architecture_confirmed_by: sample-maintainer
updated_at: 2026-01-02T00:07:00Z
updated_by: sample-maintainer
project_mode: brownfield
---

# Architecture and Technical Decisions

## ARCHITECTURE

- Verified: the current implementation is a Python library module with one public calculation function.
- Verified boundary: callers pass on-hand and reserved integer quantities and receive a non-negative integer.
- Inferred: packaging, API transport, persistence, and runtime topology are owned outside this fixture.
- Pending verification: production dependency direction, error policy, and operational constraints.
- Compatibility rule: do not change the function signature or zero-clamping behavior without an approved FEAT and caller evidence.

## ADR Index

No historical rationale has been recovered; do not invent one.
