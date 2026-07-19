---
kind: feature-spec
schema_version: 5
feature_id: FEAT-bimo-004
work_type: new_feature
title: "Project Documentation Directories"
status: verified
init_status: complete
init_completed_at: 2026-07-19T01:15:16Z
init_confirmed_by: user
owner_role: shared
owner_slug: bimo
created_at: 2026-07-19T01:15:16Z
created_by: "Bimo"
created_by_slug: bimo
created_by_source: global_git_config_user_name
created_by_developer_id: none
contributors: "Bimo"
task_ids: TASK-bimo-008
related_decisions: none
related_issues: none
policy_version: 3
updated_at: 2026-07-19T01:26:47Z
updated_by: "ai"
---

# FEAT-bimo-004 - Project Documentation Directories

## Background and Goal

- Initialized projects need stable locations for customer-facing product help and internal feature/flow design documents.
- Add these directories to the project documentation skeleton without conflicting with the existing `docs/specs` protocol path.

## Scope

### In Scope

- Initialize `docs/help/README.md` as the product usage-manual index and authoring guide.
- Initialize `docs/design/README.md` as the feature, interaction, state-transition, and business-flow design index and authoring guide.
- Generate English or Chinese content according to manifest language.
- Preserve existing files and create only missing documentation assets during start, adopt, and sync.
- Include the documentation assets in 5.0.2 strict validation and runnable examples.

### Out Of Scope

- Automatically writing product-specific help or design facts that have not been confirmed.
- Renaming the existing `docs/specs` directory or retroactively modifying legacy projects.
- Treating an empty directory as a durable Git artifact.

## Current and Target Behavior

- Current: v5 onboarding can create `docs/specs` for specifications, but it has no standard help/manual or design-document directory.
- Target: once language is confirmed, project onboarding idempotently creates `docs/help/README.md` and `docs/design/README.md`.

## Design

- Use canonical lowercase paths because `docs/specs` already exists; case-only `Docs`/`docs` variants are not portable across macOS, Windows, and Linux.
- Create localized README indexes rather than empty folders so Git preserves the directory contract and users receive clear content boundaries.
- Attach the assets to the project-state module and generate them from the same start/adopt/sync lifecycle as core project documentation.
- Never overwrite an existing README; missing assets are additive and a path occupied by a directory or non-file conflict fails safely.

## Interface and Data Impact

- New paths: `docs/help/README.md` and `docs/design/README.md`.
- New localized templates under `skill/templates/project-docs/` and `skill/templates/locales/zh-CN/project-docs/`.
- `state-catalog.json` declares the external documentation asset contract from Skill 5.0.2.
- Legacy and earlier v5 manifests remain readable without forced backfill.

## Task Breakdown

- `TASK-bimo-008`: implement initialization, templates, protocol updates, examples, validation, and tests.

## Acceptance Criteria

- New English and Chinese projects receive both documentation README files immediately after language-confirmed initialization.
- `docs/help` is explicitly for product help and usage manuals.
- `docs/design` explicitly covers feature design, interactions, business flows, states, exceptions, and related diagrams.
- Re-running onboarding preserves user-edited files and restores only missing assets.
- Project-state-disabled and legacy projects are not forced to create the directories.
- Unit, syntax, strict v5 fixture, legacy, and repository-state validation pass.

## Risks and Rollback

- Risk: `Docs` and `docs` diverge across filesystems. Mitigation: canonicalize to lowercase `docs` and document the reason.
- Risk: README placeholders may be mistaken for completed manuals/designs. Mitigation: clearly mark content as an index and require confirmed product facts in subsequent documents.
- Rollback: remove the external asset contract and initializer call; existing documentation remains ordinary project content and is never deleted.

## Handoff

- Read onboarding/project-state references, `project-onboarding.py`, `validate-state.py`, catalog, examples, and onboarding tests.
- User-confirmed intent: help stores the product usage manual; design stores feature and flow design documentation.
- Implemented and verified in Skill `5.0.2`; 79 unit tests, syntax checks, strict v5 fixtures, legacy fixture, and repository state all passed.
