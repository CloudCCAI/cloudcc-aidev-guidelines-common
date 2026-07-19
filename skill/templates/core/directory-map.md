---
kind: directory-map
schema_version: 5
version: 5
init_status: not_started
init_completed_at: none
init_confirmed_by: none
updated_at: {{TIMESTAMP}}
updated_by: onboarding
project_mode: {{PROJECT_MODE}}
---

<!-- cc-aidev:onboarding-incomplete -->

> Onboarding reference: this marker means the required answers below are not yet confirmed. Write the real project answers, obtain user confirmation, and only then remove the marker before setting `init_status: complete`.

# Directory Map

`directory-map.md` is the source of truth for repository directory responsibilities and dependency boundaries.

## Directory Responsibilities

| Path | Responsibility | Entry Points | Evidence Status |
|---|---|---|---|
| `.` | Pending user confirmation | Pending user confirmation | `{{EVIDENCE_STATUS}}` |
| `docs/help/` | Customer-facing product help and usage manuals | `README.md` | initialized |
| `docs/design/` | Detailed feature, interaction, business-flow, state, and exception-path designs | `README.md` | initialized |

## Allowed Dependencies

- Pending user confirmation.

## Forbidden Dependencies

- Pending user confirmation.

## Generated and External Content

- Record generated, vendored, cache, build-output, and externally managed paths that agents should not edit.

## Pending Verification

- Record ambiguous directories and the smallest action needed to confirm each responsibility.

## Maintenance Rules

- Describe meaningful project directories rather than every generated subdirectory.
- Do not mark an inferred Brownfield responsibility as verified without evidence.
