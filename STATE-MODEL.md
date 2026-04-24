---
title: State Model Reference
version: 3.2.0
---

# State Model Reference

This file defines the detailed state model used by `SKILL.md`.

## Core Principles

1. `current-status.md` is the mandatory entry point for every session.
2. `task-board.md` is the authoritative execution queue for implementation and handoff work.
3. Non-trivial feature work should have a primary spec under `docs/specs/`.
4. Brownfield projects should establish `PROJECT-BASELINE.md` before broad legacy changes.
5. Other files are read and updated only when their trigger conditions fire.
6. A fact must have exactly one source-of-truth file.
7. Snapshots and history should be separated.
8. Verified evidence must be distinguishable from inference.

## Canonical File Semantics

### `current-status.md`

Use as the hot snapshot for the current phase, active task, next action, and read hints.

Must contain:

- current phase
- active task
- next action
- changed files summary
- read-next hints for other state files

Must not contain:

- full issue details
- full ADR content
- long test logs
- long chronological session history

### `goals.md`

Use as the durable description of scope and success.

Must contain:

- project vision
- in-scope outcomes
- out-of-scope items
- success metrics
- hard constraints

Update only when product intent changes.

### `task-board.md`

Use as the queue for executable work items and handoff state.

Each task should record:

- task id
- status
- priority
- owner role
- optional claimed-by runtime label
- dependencies or blockers
- related issues
- scope files
- spec path when required
- done-when checklist
- next action
- handoff note

Recommended statuses:

- `todo`
- `ready`
- `in_progress`
- `blocked`
- `review`
- `done`
- `canceled`

Recommended priority values:

- `critical`
- `high`
- `medium`
- `low`

Recommended `owner_role` values:

- `backend-agent`
- `frontend-agent`
- `fullstack-agent`
- `qa-agent`
- `release-agent`
- `human`
- `shared`
- `unassigned`

### `decisions.md`

Use as the ADR log.

Each decision should record:

- status
- date
- context
- options considered
- chosen option
- why it won
- consequences

Recommended statuses:

- `proposed`
- `accepted`
- `rejected`
- `superseded`

### `issue-list.md`

Use as the queue for bugs, blockers, risks, and follow-up work.

Each issue should record:

- id
- severity
- status
- owner
- summary
- evidence
- root cause status
- next action

Recommended statuses:

- `open`
- `in_progress`
- `blocked`
- `fixed`
- `verified`
- `closed`

Recommended severity values:

- `critical`
- `high`
- `medium`
- `low`

For root cause, use:

- `verified`
- `inferred`
- `unknown`

### `test-report.md`

Use as the record of the latest verified test evidence.

Must be updated only after a real command, CI job, or equivalent verification ran.

Recommended fields:

- last run timestamp
- command
- scope
- status
- pass/fail summary
- failing tests
- coverage summary

Recommended statuses:

- `passed`
- `failed`
- `partial`
- `not_run`

### `devops.md`

Use as the runbook for build, startup, deployment, environment, and operations.

Store:

- verified build commands
- verified run commands
- required services and environment variables
- deployment steps
- operational troubleshooting notes

Do not store speculative commands as final guidance.

### `docs/specs/FEAT-xxx-*.md`

Use as the primary delivery document for one feature or non-trivial change.

Each feature spec should record:

- feature id
- title
- status
- background and goals
- scope and out-of-scope
- current constraints
- design approach
- interfaces or data-shape changes
- task breakdown
- acceptance criteria
- risks and rollback notes
- implementation progress
- handoff notes

Recommended statuses:

- `draft`
- `in_design`
- `approved`
- `in_implementation`
- `implemented`
- `verified`
- `archived`

### `docs/specs/PROJECT-BASELINE.md`

Use as the brownfield adoption baseline for a legacy project that lacks prior state discipline.

The baseline should record:

- current project purpose and active delivery slice
- verified architecture facts
- inferred architecture facts
- active unknowns and pending verification
- legacy hotspots and risky modules
- known run, build, and dependency entry points
- first adoption tasks

Recommended statuses:

- `draft`
- `adopting`
- `active_reference`
- `verified`
- `archived`

## Front Matter Schema

Every state file should start with YAML front matter. Keep it small and stable.

Recommended minimum fields:

```yaml
---
kind: current-status
version: 3
updated_at: 2026-04-01T10:30:00Z
updated_by: ai
---
```

Recommended `kind` values:

- `current-status`
- `goals`
- `decisions`
- `issue-list`
- `task-board`
- `test-report`
- `devops`

## Read Strategy

Use this read order:

1. Read `current-status.md`.
2. Inspect its `read_next` or equivalent hints.
3. Read `task-board.md` for implementation, prioritization, or handoff work.
4. In brownfield projects, open `PROJECT-BASELINE.md` before major legacy implementation when it exists.
5. Open the feature spec referenced by `spec_path` before non-trivial implementation.
6. Read only the additional files needed for the task.
7. Avoid loading cold files or unrelated specs unless the task truly needs them.

## Update Strategy

Apply these rules:

1. Update `current-status.md` at the end of every meaningful session.
2. Update `task-board.md` whenever task state, owner role, dependency, or handoff context changed.
3. In brownfield projects, update `PROJECT-BASELINE.md` whenever verified legacy understanding materially changed.
4. Update at most the triggered warm/cold files and referenced delivery docs.
5. Prefer appending concise structured entries over rewriting unrelated content.
6. If a task changes no durable state, update only `current-status.md`.

## Conflict Resolution

If files disagree:

1. Identify the authoritative file from the source-of-truth table.
2. Keep the authoritative fact unless the current session verified it is outdated.
3. Repair summaries and references in non-authoritative files.
4. If the conflict involves user intent, preserve the user-authored version and mark the discrepancy for confirmation.

Priority examples:

- `task-board.md` wins over `current-status.md` for task status, dependencies, and owner role.
- `PROJECT-BASELINE.md` wins over `current-status.md` for legacy-baseline notes and current architectural unknowns.
- `docs/specs/FEAT-xxx-*.md` wins over `task-board.md` for feature-specific acceptance criteria and design details.
- `issue-list.md` wins over task cards for blocker details and root-cause status.

## Suggested `current-status.md` Read Index

Use a small hint block such as:

```yaml
read_next:
  goals: false
  decisions: false
  issue_list: true
  task_board: true
  test_report: false
  devops: false
```

Or a short markdown section such as:

```markdown
## Read Next
- `issue-list.md` - active blocker on login latency
- `decisions.md` - database adapter choice affects this task
```

Either format is acceptable as long as it is explicit.

## What To Record vs What To Avoid

Record:

- durable decisions
- task ownership by role
- task dependencies and handoff notes
- legacy baseline facts and active unknowns
- feature acceptance criteria
- verified commands
- verified failures
- active blockers
- next actions
- project constraints

Avoid:

- ephemeral thought process
- duplicate summaries of the same fact
- noisy line-by-line diaries
- unsupported assumptions presented as facts
- free-floating todos with no task id, status, or owner role
- feature specs that drift from the implemented approach
- brownfield baseline notes that do not distinguish `verified` from `inferred`

## Maintenance Guidelines

- Keep hot files short enough to read quickly.
- Archive history outside the hot path when it grows.
- Prefer IDs and references over duplicating paragraphs.
- Keep terminology consistent across all files.
