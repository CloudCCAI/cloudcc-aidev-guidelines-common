---
kind: decisions
schema_version: 5
version: 5
init_status: not_started
init_completed_at: none
init_confirmed_by: none
architecture_init_status: not_started
architecture_reviewed_at: none
architecture_confirmed_by: none
updated_at: {{TIMESTAMP}}
updated_by: onboarding
project_mode: {{PROJECT_MODE}}
---

<!-- cc-aidev:onboarding-incomplete -->

> Onboarding reference: this marker means the required answers below are not yet confirmed. Write the real project answers, obtain user confirmation, and only then remove the marker before setting `init_status: complete`.

# Architecture and Technical Decisions

`decisions.md` owns the current `ARCHITECTURE` snapshot and the history explaining non-trivial decisions.

## ARCHITECTURE

### Evidence Convention

- Greenfield plans use `planned` until implemented and verified.
- Brownfield facts use `verified`, `inferred`, or `pending verification`.

### System Type and Technology Stack

- Pending user confirmation.

### Architecture Style and Runtime Flow

- Pending user confirmation.

### Components and Boundaries

- Pending user confirmation.

### Data Storage, Flow, and Consistency

- Pending user confirmation.

### External Systems and Dependencies

- Pending user confirmation.

### Build, Deployment, and Runtime Topology

- Pending user confirmation.

### Non-functional Constraints

- Performance: pending user confirmation
- Security: pending user confirmation
- Availability: pending user confirmation
- Compliance: pending user confirmation

### Pending Verification

- Record explicit unknowns, evidence needed, and the next verification action.

## ADR Index

No ADR has been accepted.

## ADR Rules

- Record context, considered options, the selected option, why it won, consequences, and verification.
- Do not create a placeholder ADR merely to complete onboarding.
- An ADR that invalidates the current snapshot sets `architecture_init_status` to `needs_review`.
