---
kind: directory-map
schema_version: 5
init_status: complete
init_completed_at: 2026-07-18T02:36:33Z
init_confirmed_by: Bimo
updated_at: 2026-07-18T02:36:33Z
updated_by: Bimo
project_mode: brownfield
---

# Directory Map

| Path | Responsibility | Main entry points | Evidence |
|---|---|---|---|
| `skill/` | independently publishable Skill package | `SKILL.md`, `STATE-MODEL.md` | verified |
| `skill/references/` | progressively loaded onboarding, module, and platform workflows | `onboarding.md`, `modules/`, `platforms/` | verified |
| `skill/scripts/` | deterministic preflight, initialization, state, gate, and review tooling | `project-preflight.py`, `project-onboarding.py`, `validate-state.py` | verified |
| `skill/templates/` | core, event, collaboration, review, and platform templates | `core/`, `project-state/`, `collaboration-gate/` | verified |
| `skill/tests/` | automated v5 and legacy regression coverage | `test_*.py` | verified |
| `skill/examples/` | Greenfield, Brownfield, and legacy fixtures | `README.md` | verified |
| `.claw/` | this repository's durable project-management state | `current-status.md`, `task-board.md`, `decisions.md` | verified |
| `docs/specs/` | approved and historical feature designs | `FEAT-*.md` | verified |

## Dependency Boundaries

- The publishable `skill/` package must not depend on root `.claw/` or root feature specs at runtime.
- Scripts may read package-local catalog, schemas, templates, and references; target-project state stays under that project's `.claw/`.
- Core Python workflows use the standard library. Optional Git, SSH, Codeup, and GitHub integrations are loaded only when invoked.
- Generated caches and `.claw-local/` are not source inputs and must remain untracked.

## Maintenance

- Protocol changes must keep `SKILL.md`, `STATE-MODEL.md`, catalog, templates, scripts, tests, examples, and project state aligned.
- New top-level responsibilities must be added here; do not enumerate transient cache or build directories.
