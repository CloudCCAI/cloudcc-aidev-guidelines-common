---
kind: feature-spec
schema_version: 5
feature_id: {{FEATURE_ID}}
work_type: {{WORK_TYPE}}
title: "{{TITLE}}"
status: draft
init_status: awaiting_confirmation
init_completed_at: none
init_confirmed_by: none
owner_role: shared
owner_slug: {{OWNER_SLUG}}
created_at: {{TIMESTAMP}}
created_by: "{{CREATED_BY}}"
created_by_slug: {{CREATED_BY_SLUG}}
created_by_source: {{CREATED_BY_SOURCE}}
created_by_developer_id: {{CREATED_BY_DEVELOPER_ID}}
contributors:
  - "{{CREATED_BY}}"
task_ids: none
related_decisions: none
related_issues: none
policy_version: 3
updated_at: {{TIMESTAMP}}
updated_by: "{{CREATED_BY}}"
---

# {{FEATURE_ID}} - {{TITLE}}

## Background and Goal

- Describe the user problem, current project state, and desired outcome.

## Scope

### In Scope

- List behavior that must be delivered.

### Out Of Scope

- List behavior explicitly excluded from this delivery.

## Current and Target Behavior

- Current: record verified existing behavior.
- Target: record user-confirmed target behavior.

## Design

- Record the design overview, key flow, and rationale.

## Interface and Data Impact

- Record API, event, message, data structure, migration, and compatibility impact.

## Task Breakdown

- Create and link real TASK documents only after the user confirms this FEAT.

## Acceptance Criteria

- Record verifiable user behavior and technical conditions.

## Risks and Rollback

- Record known risks, monitoring points, and rollback steps.

## Handoff

- Record the source files and open questions the next contributor must read first.
