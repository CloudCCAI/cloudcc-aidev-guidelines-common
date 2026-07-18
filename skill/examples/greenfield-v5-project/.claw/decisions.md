---
kind: decisions
schema_version: 5
init_status: complete
init_completed_at: 2026-01-01T00:05:00Z
init_confirmed_by: sample-owner
architecture_init_status: complete
architecture_reviewed_at: 2026-01-01T00:05:00Z
architecture_confirmed_by: sample-owner
updated_at: 2026-01-01T00:05:00Z
updated_by: sample-owner
project_mode: greenfield
---

# Architecture and Technical Decisions

## ARCHITECTURE

- Evidence status: `planned`.
- System type: one HTTP API service.
- Stack: Python, FastAPI, PostgreSQL, and pytest.
- Boundary: the API layer calls application services; persistence adapters own SQL access.
- Data: PostgreSQL is the system of record; note writes use database transactions.
- External systems: none in the initial scope.
- Deployment: one stateless service plus one managed database.
- Non-functional constraints: authenticated access, structured logs, and recoverable database backups.

## ADR Index

No ADR is needed until a non-trivial choice is accepted.
