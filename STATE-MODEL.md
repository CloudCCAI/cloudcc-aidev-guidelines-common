---
title: State Model Reference
version: 4.1.3
---

# State Model Reference

This file defines the detailed state model used by `SKILL.md`.

## Core Principles

1. `current-status.md` is the mandatory entry point for every session.
2. `task-board.md` is the authoritative coordination queue for implementation and handoff work.
3. `task-archive.md` stores older completed or canceled work once the active board exceeds its retention window.
4. Non-trivial feature work should have a primary spec under `docs/specs/`.
5. Brownfield projects should establish `PROJECT-BASELINE.md` before broad legacy changes.
6. Other files are read and updated only when their trigger conditions fire.
7. A fact must have exactly one source-of-truth file.
8. Snapshots and history should be separated.
9. Verified evidence must be distinguishable from inference.
10. Project-root `README.md` and `AGENTS.md` must anchor the skill requirement for every agent.
11. Async parallel delivery should use identity records, manager assignments, per-task status slices, generated team status, and integration queues instead of shared hot-file diaries.
12. Repository documents must not store manager passwords, bearer tokens, private keys, or reusable secrets.
13. Manager-gated delivery should bind project identities to Git platform accounts, public SSH keys, and SSH commit signing fingerprints.
14. Local development must verify the current operator through SSH challenge-response login before any code edit when identity or assignment records exist.
15. Development must stop when login, preflight identity, assignment, branch, task-boundary, protected-path, file-scope checks, or hard identity gate prerequisites fail.
16. One Git platform account should map to one active identity by default; role sharing requires distinct SSH signing key fingerprints.
17. Test-environment pushes should merge the development branch into `dev`, use a declared source-branch-wins conflict policy, and push `dev` to the remote.
18. State should be disclosed progressively: `current-status.md` points to `task-board.md`, `task-board.md` points to per-task status files, and detailed design/evidence stays in its own source-of-truth file.

## Project Instruction Anchors

Projects using this protocol must keep a managed declaration block in the project-root `README.md` and `AGENTS.md`.

That block must say:

- the project follows `cc-aidev-guidelines-common`
- every AI agent must automatically use the skill
- if the skill is missing locally, install it from `https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common`

The recommended writer is `scripts/ensure-agent-guidance.sh`.

## Canonical File Semantics

### `current-status.md`

Use as the hot snapshot for the current phase, active task, next action, read hints, and async parallel index. This file is an index, not a session report.

Must contain:

- current phase
- active task
- next action
- read-next hints for other state files
- task-status index when async parallel delivery is enabled
- integration queue reference when async parallel delivery is enabled
- latest verification summary as a single reference when useful

Must not contain:

- full issue details
- full ADR content
- long test logs
- long chronological session history
- changed-file lists
- session progress logs
- per-developer routine progress when `.claw/tasks/TASK-xxx.md` exists
- complete integration queue details

Size budget:

- Keep under 60 lines.

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

Use as the compact queue for executable work items. It should point to per-task status files instead of embedding task detail. In async manager-gated delivery, it is normally written by the project manager or integration owner, not by each developer for routine progress.

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
- branch and change request URL or PR URL when work is done through Git branches
- assignment path and task status path when async parallel delivery is enabled
- parallel group, touch policy, shared contracts, merge policy, and integration owner when multiple tasks merge together and the fields are needed for coordination
- next action

Each active task must link to `.claw/tasks/TASK-xxx.md` through `task_status_path`.

Do not put long done-when checklists, changed-file lists, verification logs, or handoff narratives in the task card. Put those in `.claw/tasks/TASK-xxx.md`, `docs/specs/`, or `test-report.md`.

Do not require a developer assignment to include `task-board.md` just to record that work started. The assigned developer records routine status changes in `.claw/tasks/TASK-xxx.md`. The board can lag briefly, and the manager or integration owner reconciles it when coordination state changes, unless the assignment explicitly lists `task-board.md` in `scope_files`.

Size budget:

- Keep each task card under 20 lines.

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
- `project-manager`
- `integration-agent`
- `human`
- `shared`
- `unassigned`

Retention rule:

- Keep active work in `Active Tasks`.
- Keep only the most recent 20 task cards in `Completed Tasks`.
- Move older completed or canceled task cards to `task-archive.md` instead of deleting them.

### `integration-queue.md`

Use as the optional queue for async parallel integration across multiple branches or developers.

Record:

- queue id or feature id
- integration branch
- integration owner
- merge order by task id or PR
- required validation gates
- current integration status
- rollback or deferral notes

Recommended statuses:

- `not_started`
- `collecting`
- `merging`
- `verifying`
- `ready`
- `blocked`
- `completed`

### `team-status.md`

Use as the optional generated manager view for team members, assigned tasks, contribution status, validation status, and integration status.

It is a derived view, not a source of truth.

Generate it from:

1. `.claw/developers/*.yaml`
2. `.claw/assignments/*.yaml`
3. `.claw/tasks/*.md`
4. `.claw/task-board.md`
5. `.claw/integration-queue.md`
6. external Git/review/CI evidence when that evidence has been imported into task status files or a future platform-specific summarizer

Recommended `contribution_status` values:

- `not_started`
- `assigned`
- `claimed`
- `in_progress`
- `code_submitted`
- `review_requested`
- `merged`
- `blocked`
- `canceled`

Recommended `validation_status` values:

- `not_run`
- `partial`
- `passed`
- `failed`
- `unknown`

Recommended `integration_status` values:

- `not_ready`
- `waiting_review`
- `ready_to_merge`
- `merging`
- `integrated`
- `blocked`

If `team-status.md` conflicts with source files, regenerate it or fix the source files first.

### `.claw/developers/DEV-xxx.yaml`

Use as the optional identity record for a developer or project manager.

Record:

- developer id
- display name
- role
- public key or verified Git identity
- Git platform and username
- SSH commit signing key fingerprint
- status
- managing project manager
- long-lived allowed scopes
- optional role-sharing exception note
- optional expiry or rotation note

Recommended statuses:

- `active`
- `suspended`
- `revoked`
- `expired`

Do not store private keys, passwords, bearer tokens, or reusable secrets.

When manager-gated authorization is enabled, developer records should bind `developer_id` to a Git platform account and a commit signing identity. For local developer login, store the public SSH key so `scripts/dev-login.py` can verify private-key possession through a one-time challenge. Prefer SSH commit signing for new teams. GPG signing is compatible for teams that already manage GPG keys. Sigstore/gitsign is an advanced option for CI and supply-chain audit.

Default identity binding:

- one Git platform username maps to one active `developer_id`
- a Git username may map to multiple active identities only when each identity has a distinct SSH signing key fingerprint and a `role_sharing_exception` note
- the same Git username plus the same SSH signing key fingerprint must not represent both a manager and a developer under the default policy

### `.claw-local/identity.json` or `.ai-dev-local/identity.json`

Use as an optional machine-local cache for `scripts/dev-login.py`.

Record:

- resolved developer id
- local private key path
- Git platform username
- SSH signing key fingerprint
- cache update timestamp

This file is not project state and is not a source of truth. It must be ignored by Git, must not be copied between developers, and must never contain private key contents, passwords, bearer tokens, or reusable secrets. Every development session should still re-run challenge-response verification before editing.

### Hard Identity Gate

Use as the mandatory pre-edit gate whenever a project using this skill contains any of:

- `.claw/developers/` or `.ai-dev/developers/`
- `.claw/assignments/` or `.ai-dev/assignments/`
- an active task with `assignment_path`
- an assignment with `local_login_required: true`
- a task card or feature spec that names `scripts/dev-login.py` as the identity check

When the hard identity gate is active:

- `scripts/dev-login.py` must return `allowed` in the current local session before any project implementation edit.
- Implementation edits include source code, tests, runtime configuration, migrations, generated application assets, feature specs, task status files, and other files that change project behavior or delivery state.
- A chat-declared `developer_id`, remembered user identity, Git author/email, visible OS user, prior successful PR, or `.claw-local/identity.json` cache entry is not sufficient.
- `scripts/check-assignment.py` is not a substitute for local challenge-response login. It is for CI, PR checks, and assignment-only validation after identity inputs are already trusted.
- If the task id, branch, intended file paths, private key path, developer record, or assignment is missing, the agent must stop before editing and ask for the missing input or project-manager authorization.
- The only permitted pre-login repository edits are explicit project-manager bootstrap or repair edits to create the identity and assignment records needed to make the gate runnable. These edits must not include application source, tests, runtime config, migrations, or generated assets.

### `.claw/assignments/TASK-xxx.yaml`

Use as the optional manager-authorized work contract for one task.

Record:

- task id
- assignee developer id
- assigning manager id
- assignment status
- branch name
- change request URL or PR URL when available
- spec path
- task status path
- scope mode
- allowed write roots
- exact scope files
- protected paths
- task boundary
- change manifest requirement
- touch policy
- shared contracts
- assignment timestamp and expiry
- signature or external verification reference

Recommended `touch_policy` values:

- `exclusive`
- `shared`
- `read_only`

Recommended assignment statuses:

- `active`
- `paused`
- `revoked`
- `expired`
- `completed`

`assigned_by` should reference a `MANAGER-xxx` identity. The assignment is the source of truth for `branch`, `scope_mode`, `allowed_write_roots`, `scope_files`, `protected_paths`, and scope expansion approvals. Developers must not self-assign, expand their own protected-path access, or change their task boundary.

Recommended `scope_mode` values:

- `exact_files`: all changed files must match `scope_files`; use for narrow documentation, configuration, or sensitive tasks.
- `task_bounded_broad_code`: normal source and test changes may use `allowed_write_roots`; protected paths are blocked unless explicitly listed in `scope_files`; the linked task and feature spec define the work boundary.

Path semantics:

- `allowed_write_roots`, `protected_paths`, and developer `allowed_scopes` treat bare directories as recursive roots. For example, `frontend/src`, `frontend/src/`, and `frontend/src/**` all allow files below `frontend/src`.
- `scope_files` treats bare paths as exact file/path authorization unless the manager writes an explicit glob such as `docs/specs/**`.

### `scripts/dev-login.py`

Use as the mandatory local "who is currently editing" gate before manager-gated development starts.

Inputs:

- state directory
- local private SSH key path, or a previously saved ignored local cache
- optional expected developer id
- optional task id
- optional branch
- optional Git platform username
- changed or intended file paths

Checks:

- derives the public key and SSH fingerprint from the local private key
- finds the matching active `.claw/developers/*.yaml` identity by public key or fingerprint
- signs a one-time challenge with the local private key
- verifies the signature with the registered public key
- optionally calls `scripts/check-assignment.py` for task, branch, broad write root, protected path, and exact file-scope authorization
- writes only the local private key path and resolved public identity metadata to `.claw-local/identity.json` or `.ai-dev-local/identity.json`

Outputs:

- `allowed` with the resolved `developer_id` when login and optional assignment checks pass
- `blocked_*` findings with a non-zero exit code when the key is missing, identity is unknown or inactive, challenge verification fails, or assignment scope fails

### `scripts/check-assignment.py`

Use as the local and CI preflight gate for manager-gated authorization.

Inputs:

- state directory
- developer id
- task id
- optional branch
- optional Git platform username
- optional SSH signing key fingerprint
- changed or intended file paths

Checks:

- developer record exists and is `active`
- assignment exists and is `active`
- assignment `assignee` matches the developer id
- assignment `assigned_by` references `MANAGER-xxx`
- optional Git username and SSH signing fingerprint match the developer record
- active duplicate Git usernames follow the role-sharing exception rules
- optional branch matches the assignment branch
- for `scope_mode: exact_files`, every file path is inside assignment `scope_files`
- for `scope_mode: task_bounded_broad_code`, every file path is inside recursive `allowed_write_roots` or exact/glob `scope_files`
- changed files matching `protected_paths` are blocked unless explicitly authorized by `scope_files`

Outputs:

- `allowed` with a zero exit code when all checks pass
- `blocked_*` findings with a non-zero exit code when identity, assignment, branch, or scope checks fail

### `scripts/store-yunxiao-token.py`

Use as the local helper for storing a developer's Yunxiao personal access token outside Git-tracked files.

Behavior:

- prompts for `YUNXIAO_TOKEN` without echoing it
- writes `.claw-local/codeup.env` by default
- sets file permissions to owner read/write only
- never writes tokens to `.claw/`, `docs/`, source files, task status files, or logs

### `scripts/configure-codeup-change-request.py`

Use as the local helper for writing project-specific Codeup change request defaults after `YUNXIAO_TOKEN` is available.

Behavior:

- reads the current Codeup Git remote, local env file, and environment variables
- resolves the numeric Codeup repository id through the Yunxiao Codeup repository list API when `CODEUP_REPOSITORY_ID` is not already set
- writes `.claw-local/codeup.env` by default
- stores `CODEUP_REPOSITORY_ID`, `CODEUP_SOURCE_PROJECT_ID`, `CODEUP_TARGET_PROJECT_ID`, `CODEUP_TARGET_BRANCH`, and `CODEUP_CREATE_FROM`
- preserves `YUNXIAO_TOKEN` without printing it
- sets file permissions to owner read/write only

### `scripts/create-codeup-change-request.py`

Use as the default platform helper for creating Codeup change requests.

Behavior:

- loads `YUNXIAO_TOKEN` from the environment or `.claw-local/codeup.env`
- stops before the API call when `YUNXIAO_TOKEN` is missing
- prints the official Yunxiao personal access token documentation link when the token is missing
- calls Codeup `CreateChangeRequest` through Yunxiao OpenAPI
- accepts domain, repository, source project id, target project id, source branch, target branch, title, description, reviewers, and work item ids as CLI flags or local env values
- treats `repositoryId` as the request path parameter and sends numeric `sourceProjectId` and `targetProjectId` in the JSON body
- defaults both project ids to the numeric `repositoryId` for same-repository change requests, but requires explicit project ids when `repositoryId` is a full path

### `scripts/push-test-environment.py`

Use as the default helper when a user asks to push to the test environment.

Behavior:

- requires a clean Git working tree before switching branches
- treats the current branch as the source development branch unless `--source-branch` is provided
- treats `dev` as the target test-environment branch unless `--target-branch` is provided
- fetches the remote, checks out `dev`, fast-forwards it from the remote, merges the source branch, and pushes `dev`
- auto-resolves merge conflicts by taking the source development branch version
- restores the original branch after success unless `--no-restore` is provided

### `templates/platforms/codeup/`

Use as the default platform template for teams on Aliyun Yunxiao Codeup.

Adopting projects should configure protected branches and Yunxiao Flow checks so Codeup review requests cannot merge until review, automated checks, and assignment scope checks pass.

### `templates/github-workflows/check-assignment.yml`

Use as the optional GitHub Actions PR gate for manager-gated authorization.

Behavior:

- reads the PR author as the Git platform username
- resolves `TASK-xxx` from branch name, PR title, or PR body
- maps PR author to `developer_id` through `.claw/developers/*.yaml`
- collects changed files from the PR diff
- calls `scripts/check-assignment.py .claw`

GitHub-based projects should copy it into `.github/workflows/check-assignment.yml`, enable required status checks in branch protection, and adapt task-id parsing if their branch naming scheme differs.

### `.claw/tasks/TASK-xxx.md`

Use as the per-task status slice for one task. Every active task should have one small file here, even when the project is not using async parallel delivery.

Record:

- task id
- assignee developer id or `unassigned`
- owner role
- branch and change request URL or PR URL
- current status
- completed work
- changed files summary
- verification evidence from real commands
- blockers
- handoff notes

This file is the right place for routine progress, changed files, verification evidence, blocker detail, and handoff notes for one task. In async manager-gated delivery, it is also the developer-writable source of truth for contribution status such as `ready`, `in_progress`, `blocked`, and `review`. `current-status.md` should only link to it or summarize it briefly. `task-board.md` should link to it through `task_status_path`.

### `task-archive.md`

Use as the historical archive for completed and canceled task cards that aged out of `task-board.md`.

Archived tasks should retain:

- task id
- final status
- owner role
- related issues
- scope files
- handoff summary or completion context
- archived timestamp when available

Archived tasks should use only these statuses:

- `done`
- `canceled`

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
- `task-archive`
- `test-report`
- `devops`
- `integration-queue`
- `team-status`
- `task-status`

## Read Strategy

Use this read order:

1. Read `current-status.md`.
2. Inspect its `read_next` or equivalent hints.
3. Read `task-board.md` for implementation, prioritization, or handoff work.
4. Read the active task's `.claw/tasks/TASK-xxx.md`.
5. Read `task-archive.md` only when archived completed-work history matters.
6. In brownfield projects, open `PROJECT-BASELINE.md` before major legacy implementation when it exists.
7. Open the feature spec referenced by `spec_path` before non-trivial implementation.
8. In async parallel delivery, read only the referenced `developer`, `assignment`, and `integration_queue` files.
9. In manager-gated delivery, automatically run `scripts/dev-login.py` for local sessions before editing files. Use `scripts/check-assignment.py` for CI and assignment-only checks, not as a local-login substitute.
10. When a manager asks for team status, generate or read `team-status.md` through the standard aggregation method.
11. Read only the additional files needed for the task.
12. Avoid loading cold files or unrelated specs unless the task truly needs them.

## Update Strategy

Apply these rules:

1. Update `current-status.md` at the end of every meaningful session by rewriting a compact snapshot.
2. Update `task-board.md` whenever compact index fields changed.
3. Update `.claw/tasks/TASK-xxx.md` whenever progress, changed files, verification, blocker detail, or handoff context changed.
4. When completed or canceled task cards exceed 20 items on the board, move the oldest cards into `task-archive.md`.
5. In brownfield projects, update `PROJECT-BASELINE.md` whenever verified legacy understanding materially changed.
6. In async parallel delivery, developers update their assigned `.claw/tasks/TASK-xxx.md` for routine progress, while the project manager or integration owner reconciles `task-board.md`, `current-status.md`, and `integration-queue.md`.
7. In manager-gated delivery, only the project manager updates developer records and assignment scope.
8. Regenerate `team-status.md` when the manager needs a current team view or when source contribution state changed.
9. Update at most the triggered warm/cold files and referenced delivery docs.
10. Prefer appending concise structured entries over rewriting unrelated content.
11. If a task changes no durable state, update only `current-status.md` and the active task status file if its next action changed.

## Conflict Resolution

If files disagree:

1. Identify the authoritative file from the source-of-truth table.
2. Keep the authoritative fact unless the current session verified it is outdated.
3. Repair summaries and references in non-authoritative files.
4. If the conflict involves user intent, preserve the user-authored version and mark the discrepancy for confirmation.

Priority examples:

- `task-board.md` wins over `current-status.md` for queue membership, board index status, dependencies, owner role, and task status path.
- `task-archive.md` wins over `task-board.md` for older completed or canceled tasks that have already been archived.
- `PROJECT-BASELINE.md` wins over `current-status.md` for legacy-baseline notes and current architectural unknowns.
- `docs/specs/FEAT-xxx-*.md` wins over `task-board.md` for feature-specific acceptance criteria and design details.
- `issue-list.md` wins over task cards for blocker details and root-cause status.
- `.claw/assignments/TASK-xxx.yaml` wins over `task-board.md` for authorized assignee, manager, branch, write scope, assignment status, and touch policy.
- `.claw/developers/DEV-xxx.yaml` wins over chat or Git author metadata for developer id, active status, Git platform username, and SSH signing fingerprint.
- `.claw-local/identity.json` and `.ai-dev-local/identity.json` are local caches only; if they conflict with `.claw/developers/*.yaml`, the developer record wins and login must be rerun.
- `.claw/tasks/TASK-xxx.md` wins over `current-status.md` and `task-board.md` for developer contribution status, task progress, changed files, evidence, blocker detail, and handoff notes.
- `.claw/integration-queue.md` wins over task cards for merge order and integration gate state.
- `developers`, `assignments`, `tasks`, `task-board`, and `integration-queue` all win over `team-status.md`; regenerate `team-status.md` when stale.

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
- archived completed-work history
- project-root skill declaration anchors in `README.md` and `AGENTS.md`
- developer IDs and public identity records when async parallel delivery is enabled
- manager-signed task assignments and write scopes
- per-task progress slices instead of hot-file diaries
- generated team status summaries for manager review
- integration branch, merge order, and validation gates
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
- unbounded growth in `Completed Tasks` when those tasks should have been archived
- projects that claim to use this protocol but omit the managed declaration block from `README.md` or `AGENTS.md`
- private keys, manager passwords, bearer tokens, or reusable secrets in repository files
- treating `.claw-local/identity.json` or `.ai-dev-local/identity.json` as proof without re-running challenge-response verification
- editing source, tests, config, migrations, generated assets, feature specs, or task status files before `scripts/dev-login.py` returns `allowed`
- using chat context, remembered identity, Git author/email, or `scripts/check-assignment.py` as a bypass for local SSH challenge-response login
- multi-developer progress journals inside `current-status.md`
- hand-maintained `team-status.md` presented as authoritative truth
- code changes outside an exact assignment `scope_files` without an updated assignment
- protected-path changes without exact `scope_files` authorization
- using narrow `scope_files` so aggressively that developers are pushed to implement fixes in the wrong module instead of the real call chain

## Maintenance Guidelines

- Keep hot files short enough to read quickly.
- Archive history outside the hot path when it grows.
- Prefer IDs and references over duplicating paragraphs.
- Keep terminology consistent across all files.
