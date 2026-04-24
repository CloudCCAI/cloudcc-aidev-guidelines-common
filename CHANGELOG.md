# Changelog

## 3.1.0 - 2026-04-24

- Added the canonical `skill_version` marker to `SKILL.md` front matter so agents can detect the installed skill version directly.
- Documented version-marker usage in `README.md` and aligned the published version label to `3.1.0`.

## 3.0.0 - 2026-04-24

- Added `task-board.md` as a first-class state file for executable work, handoff, and role-based ownership.
- Added spec-driven delivery rules and a feature spec template under `docs/specs/`.
- Defined state-directory resolution rules for `.claw/` and `.ai-dev/`.
- Reworked the templates to be generic and multi-stack friendly instead of Node-specific.
- Fixed the `test-report.md` scaffold so it no longer reports `passed` before any real run.
- Extended `scripts/init-state.sh` to create `docs/specs/` and seed `_feature-spec-template.md`.
- Extended `scripts/validate-state.py` to validate `task-board.md`, referenced specs, and unresolved placeholder front matter.
- Expanded the sample project with `task-board.md` and a feature spec example.

## 2.0.0 - 2026-04-01

- Refactored the skill into a layered project state protocol.
- Added explicit read and update triggers for all six state files.
- Added source-of-truth rules to prevent duplicated facts.
- Added `STATE-MODEL.md` as a detailed reference document.
- Reworked all templates with YAML front matter and machine-stable fields.
- Added `scripts/init-state.sh` for quick project bootstrapping.
- Added `scripts/validate-state.py` for basic state structure validation.
- Added `examples/sample-project/.claw/` with a complete sample state set.
- Updated `README.md` for installation, validation, and publishing readiness.
