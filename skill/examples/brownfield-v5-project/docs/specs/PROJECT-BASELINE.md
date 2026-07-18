---
kind: project-baseline
schema_version: 5
title: Inventory service project baseline
status: verified
init_status: complete
init_completed_at: 2026-01-02T00:04:00Z
init_confirmed_by: sample-maintainer
owner_role: shared
updated_at: 2026-01-02T00:04:00Z
updated_by: sample-maintainer
project_mode: brownfield
---

# PROJECT-BASELINE

## Verified Facts

- `src/inventory.py` computes available stock as non-negative on-hand minus reserved stock.
- Existing callers depend on the function name and its two positional parameters.

## Inferred Facts

- The single module suggests a library boundary, but no packaging metadata is present.

## Pending Verification

- Production callers, supported Python versions, and deployment ownership are not represented in this fixture.
- Before changing behavior, ask the maintainer for caller evidence and run the real downstream suite.

## Legacy Hotspots

- The availability rule is compatibility-sensitive because callers may rely on clamping negative values to zero.

## Adoption Plan

- Preserve the public function contract and document only facts needed by the next real change.
