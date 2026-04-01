---
title: State Model Reference
version: 2.0.0
---

# State Model Reference

This file defines the detailed state model used by `SKILL.md`.

## Core Principles

1. `current-status.md` is the mandatory entry point for every session.
2. Other files are read and updated only when their trigger conditions fire.
3. A fact must have exactly one source-of-truth file.
4. Snapshots and history should be separated.
5. Verified evidence must be distinguishable from inference.

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

## Front Matter Schema

Every state file should start with YAML front matter. Keep it small and stable.

Recommended minimum fields:

```yaml
---
kind: current-status
version: 2
updated_at: 2026-04-01T10:30:00Z
updated_by: ai
---
```

Recommended `kind` values:

- `current-status`
- `goals`
- `decisions`
- `issue-list`
- `test-report`
- `devops`

## Read Strategy

Use this read order:

1. Read `current-status.md`.
2. Inspect its `read_next` or equivalent hints.
3. Read only the additional files needed for the task.
4. Avoid loading cold files unless the task truly needs them.

## Update Strategy

Apply these rules:

1. Update `current-status.md` at the end of every meaningful session.
2. Update at most the triggered warm/cold files.
3. Prefer appending concise structured entries over rewriting unrelated content.
4. If a task changes no durable state, update only `current-status.md`.

## Conflict Resolution

If files disagree:

1. Identify the authoritative file from the source-of-truth table.
2. Keep the authoritative fact unless the current session verified it is outdated.
3. Repair summaries and references in non-authoritative files.
4. If the conflict involves user intent, preserve the user-authored version and mark the discrepancy for confirmation.

## Suggested `current-status.md` Read Index

Use a small hint block such as:

```yaml
read_next:
  goals: false
  decisions: false
  issue_list: true
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

## Maintenance Guidelines

- Keep hot files short enough to read quickly.
- Archive history outside the hot path when it grows.
- Prefer IDs and references over duplicating paragraphs.
- Keep terminology consistent across all files.
