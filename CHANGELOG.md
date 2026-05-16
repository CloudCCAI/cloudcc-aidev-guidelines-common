# Changelog

## 3.6.0 - 2026-05-16

- Added project-manager-gated authorization for async multi-developer delivery.
- Made Git platform account binding plus SSH commit signing the default recommended identity model for new teams.
- Added `scripts/check-assignment.py` for local and CI preflight checks of developer identity, assignment status, branch, and file scope.
- Added `templates/github-workflows/check-assignment.yml` as a GitHub Actions PR gate example for assignment-scope enforcement.
- Updated developer and assignment templates with manager ownership, Git username, SSH signing fingerprint, assignment status, and preflight policy fields.
- Updated protocol docs and state model to block development when identity, assignment, branch, or `scope_files` checks fail.
- Extended validation expectations for manager-assigned task authorization metadata.

## 3.5.0 - 2026-05-01

- Added an optional identity-based asynchronous parallel delivery model for independent developers working through Git branches.
- Added public developer identity records, manager assignment records, per-task status slices, and an integration queue to the protocol.
- Added `team-status.md` as a derived manager view plus `scripts/summarize-team-status.py` for standard team status aggregation.
- Updated templates for feature specs, task cards, current status, integration queues, developer identities, task assignments, and task status files.
- Updated `scripts/init-state.sh` to create async parallel coordination directories and seed `.claw/integration-queue.md`.
- Extended `scripts/validate-state.py` to validate optional async parallel coordination files, team status files, and task references.
- Documented that manager passwords, bearer tokens, private keys, and reusable secrets must not be stored in repository documents.

## 3.4.0 - 2026-04-30

- Added `scripts/ensure-agent-guidance.sh` to create or refresh the managed `README.md` and `AGENTS.md` declaration block.
- Updated `scripts/init-state.sh` to write the project-level skill declaration automatically during bootstrap.
- Extended `scripts/validate-state.py` to require `README.md` and `AGENTS.md` guidance blocks, including the GitHub install source.
- Updated the skill protocol, state model, and README to require the declaration for both greenfield and brownfield adoption.

## 3.3.0 - 2026-04-24

- Added `task-archive.md` as the history file for completed or canceled tasks beyond the active board retention window.
- Defined the `Completed Tasks <= 20` retention rule for `task-board.md`.
- Updated README, state model, and task-board guidance to document the archive workflow.

## 3.2.0 - 2026-04-24

- Added `Brownfield Adoption Mode` so legacy projects can adopt the protocol without requiring full historical backfill.
- Added `PROJECT-BASELINE.md` guidance and a `project-baseline-template.md` scaffold for undocumented existing projects.
- Updated bootstrapping, validation wording, and README guidance to cover greenfield and brownfield entry paths.

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
