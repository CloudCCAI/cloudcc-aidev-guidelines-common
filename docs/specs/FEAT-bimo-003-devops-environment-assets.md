---
kind: feature-spec
schema_version: 5
feature_id: FEAT-bimo-003
work_type: feature_iteration
title: "DevOps environment asset initialization"
status: verified
init_status: complete
init_completed_at: 2026-07-19T01:00:09Z
init_confirmed_by: user
owner_role: shared
owner_slug: bimo
created_at: 2026-07-19T00:59:10Z
created_by: "Bimo"
created_by_slug: bimo
created_by_source: global_git_config_user_name
created_by_developer_id: none
contributors: "Bimo"
task_ids: TASK-bimo-007
related_decisions: none
related_issues: none
policy_version: 3
updated_at: 2026-07-19T01:26:47Z
updated_by: "ai"
---

# FEAT-bimo-003 - DevOps environment asset initialization

## Background and Goal

- `.claw/devops.md` records build, deployment, environment, and operations facts, but initialized projects do not receive a matching root deployment-asset directory.
- Create a deterministic `DevOps/` asset tree after the customer environment list is confirmed during DevOps onboarding.
- When the customer has not decided the environment list, recommend and, after confirmation, reserve `DEV`, `UAT`, and `PROD` for later editing.

## Scope

### In Scope

- Add a resumable onboarding command that creates environment-specific deployment assets under root `DevOps/`.
- Give every environment its own `Dockerfile` and `.env.example`.
- Create localized `DevOps/README.md` guidance and record the asset inventory in `.claw/devops.md`.
- Preserve existing files, reject unsafe or duplicate environment names, and make repeat runs idempotent.
- Ignore real `.env` files while keeping `.env.example` committed.
- Validate the initialized asset tree before DevOps onboarding can be marked complete.

### Out Of Scope

- Producing application-specific runnable container images without confirmed build facts.
- Storing passwords, tokens, certificates, private keys, or other secret values.
- Automatically deleting or renaming customer environment directories.
- Retrofitting legacy projects unless they explicitly adopt or run the new configuration command.

## Current and Target Behavior

- Current: onboarding creates `.claw/devops.md` only; environment assets and Dockerfiles are unmanaged.
- Target: after environment confirmation, onboarding creates `DevOps/<environment>/Dockerfile` and `DevOps/<environment>/.env.example`. Undecided customers can explicitly accept the recommended `DEV/UAT/PROD` reservation.

## Design

- Do not create `DevOps/` during the initial `start` skeleton because customer environments are not known yet.
- Add `project-onboarding.py devops-assets` with either repeated `--environment` values or `--recommended-environments`.
- Use safe environment directory names, preserve customer casing, and reject path separators, traversal, and case-insensitive duplicates.
- Reserved Dockerfiles are deliberately non-runnable comment-only placeholders until real build facts are confirmed; this prevents invented deployment success.
- Update a controlled inventory block and machine fields in `.claw/devops.md`; new or changed assets move DevOps initialization back to `in_progress` or `needs_review`.
- Repeated commands only create missing files. Existing customer-edited files are never overwritten.

## Interface and Data Impact

- New CLI: `project-onboarding.py devops-assets <project> [--environment NAME ... | --recommended-environments]`.
- New root paths: `DevOps/README.md`, `DevOps/<environment>/Dockerfile`, and `DevOps/<environment>/.env.example`.
- New `.claw/devops.md` fields: `devops_assets_root` and `environment_names`.
- Existing v5 and legacy projects remain readable; the new completion requirement applies when the new DevOps asset fields are configured.

## Task Breakdown

- `TASK-bimo-007`: implement the asset initializer, protocol updates, templates, examples, validation, and tests.

## Acceptance Criteria

- Custom environment lists create one distinct Dockerfile and `.env.example` per environment.
- `--recommended-environments` creates exactly `DEV`, `UAT`, and `PROD` after customer acceptance.
- Repeat execution is a no-op for existing files and never overwrites modified content.
- Unsafe names and case-insensitive duplicates fail before writing.
- Real `.env` files are ignored and no secret values are generated.
- DevOps completion fails when configured assets are missing.
- English and Chinese onboarding guidance, examples, full tests, and v4/v5 validation pass.

## Risks and Rollback

- Risk: placeholder Dockerfiles could be mistaken for deployable assets. Mitigation: keep them comment-only with an explicit fail-safe warning and `pending verification` documentation.
- Risk: environment changes could overwrite customer work. Mitigation: exclusive create, additive updates, and no automatic removal.
- Rollback: remove the new command/templates and the new completion check; existing customer-created `DevOps/` files remain ordinary project assets and are not deleted.

## Handoff

- Read `skill/references/onboarding.md`, both DevOps core templates, `project-onboarding.py`, `state-catalog.json`, and onboarding/validator tests.
- User-confirmed decisions: independent Dockerfile per environment; custom customer list wins; `DEV/UAT/PROD` is the recommended reservation when the customer is undecided.
- Implementation and compatibility verification completed in Skill `5.0.2`; all 79 unit tests and all v4/v5 fixture validations passed.
