---
kind: feature-spec
feature_id: FEAT-011
title: Separate the distributable skill package from project documentation
status: implemented
owner_role: shared
task_ids: TASK-011
related_decisions: ADR-011
related_issues: none
updated_at: 2026-07-17T06:55:02Z
updated_by: codex
---

# FEAT-011 - Skill package layout

## Requirement

Separate the distributable skill files from this repository's project-management documentation. Keep project documentation and project state at the repository root, and place the complete skill package under `skill/`.

## Design

- Move `skill/SKILL.md`, `skill/STATE-MODEL.md`, `skill/scripts/`, `skill/templates/`, and `skill/examples/` into `skill/`.
- Keep `README.md`, `AGENTS.md`, `docs/`, `.claw/`, release history, and licensing files at the repository root.
- Preserve relative paths inside the skill package by moving its files as one unit.
- Update current project documentation and operational commands to reference `skill/` paths.
- Keep the skill version under the standard front matter extension field `metadata.skill_version`.
- Preserve historical paths in `CHANGELOG.md` as release history.

## Acceptance Criteria

- `skill/SKILL.md` is the skill entry point.
- Skill scripts still locate their templates and sibling scripts.
- Root `README.md` and `AGENTS.md` contain no stale root-level skill paths.
- The standard skill quick validator accepts `skill/SKILL.md`.
- Project state validation, Python syntax checks, Shell syntax checks, and a fresh initialization smoke test pass.

## Verification

- `python3 skill/scripts/validate-state.py .claw`
- `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-layout-pycache python3 -m py_compile skill/scripts/*.py`
- `bash -n skill/scripts/init-state.sh skill/scripts/ensure-agent-guidance.sh`
- Initialize and validate a temporary sample project with `skill/scripts/init-state.sh`.
