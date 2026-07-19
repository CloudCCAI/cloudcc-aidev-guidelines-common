---
kind: directory-map
schema_version: 5
init_status: complete
init_completed_at: 2026-01-01T00:06:00Z
init_confirmed_by: sample-owner
updated_at: 2026-01-01T00:06:00Z
updated_by: sample-owner
project_mode: greenfield
---

# Directory Map

| Path | Responsibility | Entry points | Evidence |
|---|---|---|---|
| `src/api/` | HTTP transport and request validation | `src/api/main.py` | planned |
| `src/application/` | use cases and transaction boundaries | service modules | planned |
| `src/persistence/` | PostgreSQL adapters and migrations | repository modules | planned |
| `tests/` | unit and API verification | pytest | planned |
| `docs/help/` | customer-facing product help and usage manuals | `README.md` | verified |
| `docs/design/` | detailed feature and flow designs | `README.md` | verified |

Allowed dependencies flow from API to application interfaces and from adapters toward those interfaces. Application code must not import the HTTP framework or concrete database adapters.
