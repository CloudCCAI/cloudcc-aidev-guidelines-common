---
kind: feature-spec
feature_id: FEAT-008
title: Codeup change request submission
status: implemented
owner_role: shared
task_ids: TASK-008
related_decisions: ADR-008
related_issues: none
updated_at: 2026-05-19T00:00:00Z
updated_by: codex
---

# FEAT-008 - Codeup change request submission

## Requirement

Adopt Aliyun Yunxiao Codeup as the default review request platform. Keep GitHub guidance as an optional platform example.

Developers should be able to create a Codeup change request through OpenAPI. Before creation, the tool must check for a local `YUNXIAO_TOKEN`. If the token is missing, the tool must stop and show the official personal access token documentation link.

## Design

- Add `scripts/store-yunxiao-token.py` to store a token in `.claw-local/codeup.env`.
- Add `scripts/create-codeup-change-request.py` to call Codeup `CreateChangeRequest`.
- Add `.gitignore` entries for local secret files.
- Add `templates/platforms/codeup/` as the default platform guide.
- Keep `templates/github-workflows/check-assignment.yml` as an optional GitHub example.
- Preserve GitHub `3.8.0` hard identity and task-bounded broad authorization changes; publish this Codeup layer as `3.9.0`.

## Acceptance Criteria

- Missing `YUNXIAO_TOKEN` exits before any OpenAPI request and prints the token document link.
- Token storage writes only to ignored local files.
- Codeup create script supports dry-run output without exposing the token.
- Codeup create script sends `repositoryId` only in the API path and always sends numeric `sourceProjectId` and `targetProjectId` in the body.
- README, SKILL, STATE-MODEL, templates, and changelog describe Codeup as the default flow.
- Existing validation still passes.

## Verification

- `python3 scripts/create-codeup-change-request.py --dry-run --domain https://example.com --repository-id 123 --source-branch feat/TASK-008-codeup --title "[TASK-008] Codeup"` without token returns setup guidance.
- `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/create-codeup-change-request.py scripts/store-yunxiao-token.py`
- `python3 scripts/validate-state.py .claw`
