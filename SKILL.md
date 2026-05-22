---
name: cc-aidev-guidelines-common
description: Externalizes compact project state into `.claw` or `.ai-dev` files, keeps hot files as indexes, tracks each task in its own small status file, and supports spec-driven delivery, greenfield and brownfield adoption, project-manager-gated async parallel delivery, Codeup review requests, and test-environment branch pushes. Use for AI-assisted software delivery, persistent project memory, progressive disclosure, task handoff, ADR tracking, issue tracking, test logging, multi-developer coordination, authorization gates, or agent coding standards.
skill_version: 4.1.1
---

# AI Agent Project State Protocol

Use this skill to turn project state into durable files that an AI agent can read, update, and audit across sessions.

## Skill Version

Canonical skill version: `4.1.1`

Use the `skill_version` field in this file's front matter as the source of truth for the installed skill version. If `README.md`, `CHANGELOG.md`, or other references drift, this field wins.

This skill has eight goals:

1. Build a stable project state storage layer.
2. Enforce explicit AI development rules.
3. Make multi-agent delivery resumable through task cards and feature specs.
4. Support asynchronous multi-developer delivery through explicit identity, assignment, status-slice, and integration records.
5. Gate multi-developer work through a project manager, mandatory SSH challenge-response login, SSH-signed identity bindings, and hard pre-edit scope checks.
6. Support Codeup-first change request submission while preserving GitHub as an optional platform example.
7. Support test-environment pushes by merging a development branch into `dev`, resolving conflicts with a declared source-branch-wins policy, and pushing `dev`.
8. Keep state loading compact through progressive disclosure: hot files are indexes, and each task owns a separate small status file.

## Directory Layout

Store the state under `.claw/` by default. `.ai-dev/` is an acceptable alias if the project already uses it.

```text
.claw/
├── current-status.md
├── goals.md
├── decisions.md
├── issue-list.md
├── task-board.md
├── task-archive.md
├── test-report.md
├── devops.md
├── team-status.md                # optional derived manager view for team status
├── integration-queue.md          # optional, created by init-state.sh for async parallel delivery
├── developers/                   # optional developer identity records
│   └── DEV-xxx.yaml
├── assignments/                  # optional manager-signed task assignments
│   └── TASK-xxx.yaml
└── tasks/                        # per-task current status slices
    └── TASK-xxx.md

docs/
└── specs/
    ├── _feature-spec-template.md
    ├── _project-baseline-template.md
    ├── PROJECT-BASELINE.md
    └── FEAT-xxx-feature-name.md
```

Use the state templates under `templates/` when initializing a project. Keep feature specs under `docs/specs/`.

Utility scripts are available under `scripts/`:

- `scripts/init-state.sh` initializes a state directory from templates
- `scripts/ensure-agent-guidance.sh` creates or refreshes the managed `README.md` and `AGENTS.md` declaration block
- `scripts/dev-login.py` verifies the local developer by SSH key possession before development starts
- `scripts/check-assignment.py` checks developer identity, manager assignment, branch, task-bounded write roots, protected paths, and exact file scope before development or in CI
- `scripts/store-yunxiao-token.py` stores a developer's local `YUNXIAO_TOKEN` outside Git-tracked files
- `scripts/create-codeup-change-request.py` creates a Codeup change request with Yunxiao OpenAPI
- `scripts/push-test-environment.py` merges a development branch into `dev`, resolves test-deploy conflicts from the source branch, and pushes `dev`
- `scripts/summarize-team-status.py` generates the derived manager team-status view
- `scripts/validate-state.py` validates required files, compact hot-file budgets, task cards, per-task status files, referenced feature specs, and optional async-parallel coordination files
- `templates/platforms/codeup/` documents the default Codeup change request flow
- `templates/github-workflows/check-assignment.yml` provides a GitHub Actions example for enforcing assignment scope on pull requests

## Project-Level Skill Declaration

Every project that adopts this skill must maintain a short managed declaration block in the project-root `README.md` and `AGENTS.md`.

That declaration must state all of the following:

- the project follows `cc-aidev-guidelines-common`
- every AI agent must automatically use this skill before project work
- if the skill is not installed in the current environment, install it first from `https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common`

Use `scripts/ensure-agent-guidance.sh <project-root>` to create or refresh those declarations.

For `Greenfield Mode`, create or update `README.md` and `AGENTS.md` during bootstrap.

For `Brownfield Adoption Mode`, inspect the existing `README.md` and `AGENTS.md` at adoption start and patch in the declaration block before broad project work continues.

## State Directory Resolution

Resolve the canonical state directory in this order:

1. If `.claw/` exists, use `.claw/`.
2. Else if `.ai-dev/` exists, use `.ai-dev/`.
3. Else initialize `.claw/` and `docs/specs/`.
4. If both exist, do not update both. Prefer the repo's declared convention. If the repo declares no convention, prefer `.claw/`, inspect `.ai-dev/` once for drift, and record the consolidation plan in `current-status.md`.

## Operating Model

Treat the eight state files as a layered memory system, not as eight equally-hot documents.

| Layer | File | Default read | Default update | Purpose |
|------|------|------|------|------|
| Hot | `current-status.md` | Every session | Every session | Compact entry index, current snapshot, next action |
| Warm | `task-board.md` | Every implementation or handoff session | Triggered | Compact task index, dependencies, owner roles, status-file pointers |
| Warm | `integration-queue.md` | Async parallel integration only | Triggered | Integration branches, merge order, merge gates |
| Warm | `team-status.md` | Manager review only | Generated | Derived team member, assignment, contribution, and integration summary |
| Warm | `developers/*.yaml` | Identity or assignment work only | Triggered | Developer identity, Git platform account, SSH signing fingerprint, role status |
| Warm | `assignments/*.yaml` | Assigned-task work only | Triggered | Project-manager-authorized task ownership and write scope |
| Warm | `tasks/*.md` | Active task work | Triggered | Per-task current state, progress, changed files, evidence, handoff notes |
| Cold | `task-archive.md` | Historical review or audit only | Triggered | Archived completed and canceled work beyond the active board window |
| Warm | `issue-list.md` | As needed | Triggered | Open problems, blockers, follow-up work |
| Warm | `test-report.md` | As needed | Triggered | Verified test outcomes from real runs |
| Cold | `goals.md` | Triggered | Triggered | Product scope, success criteria, constraints |
| Cold | `decisions.md` | Triggered | Triggered | Architecture and technical decisions |
| Cold | `devops.md` | Triggered | Triggered | Build, run, deploy, operations knowledge |

## Delivery Modes

Use the same skill in two modes:

- `Greenfield Mode`: a new project or a fresh module that can start directly with `task-board.md` and feature specs.
- `Brownfield Adoption Mode`: an existing project that has no prior state files or spec discipline.
- `Asynchronous Parallel Delivery Mode`: two or more developers work from different environments and coordinate through Git, task assignments, per-task status files, and an integration queue.
- `Project-Manager-Gated Authorization Mode`: async parallel delivery where a project manager is the only authority that can add team members, assign tasks, define task boundaries, change protected scopes, or approve scope expansion.

In `Brownfield Adoption Mode`:

- Create the minimum state skeleton first instead of backfilling the whole project history.
- Create or update the project-root `README.md` and `AGENTS.md` declaration block before the first substantial implementation session.
- Create `docs/specs/PROJECT-BASELINE.md` before broad implementation so new agents can resume legacy work safely.
- Mark facts in the baseline as `verified`, `inferred`, or `pending verification`.
- Apply full `task-board + spec` discipline from the current active work forward.
- Only backfill old modules when they are actively being changed or when the missing context is blocking progress.

In `Asynchronous Parallel Delivery Mode`:

- Use Git branches and platform review requests as the transport for code and review. Codeup change requests are the default platform flow; GitHub pull requests remain supported as an example.
- Treat repository files as the durable coordination layer, not as a replacement for branch protection, CI, or code review.
- Do not store manager passwords, bearer tokens, private keys, or reusable secrets in project documents, even encrypted.
- Store public identity material in `.claw/developers/`, and keep private keys in the developer's local keychain or approved secret system.
- For local "who is currently editing" checks, use SSH challenge-response login: derive the public key and fingerprint from the developer's local private key, match a registered identity, sign a one-time challenge, and verify it with the stored public key.
- Local identity cache files such as `.claw-local/identity.json` or `.ai-dev-local/identity.json` may remember a private key path and resolved `developer_id` on one machine, but they must be ignored by Git and must never contain private key material.
- Default to Git platform account binding plus SSH commit signing for strong identity enforcement. GPG signing is compatible when a team already uses it. Sigstore/gitsign is an advanced option for CI, artifact signing, and supply-chain audit.
- Use `.claw/assignments/TASK-xxx.yaml` to record who is authorized to work on a task, which branch they should use, which broad code roots and protected paths apply, which exact task documents they may edit, and which shared contracts they must preserve.
- Use `.claw/tasks/TASK-xxx.md` for every tracked task's current state, progress, evidence, changed-file summary, and handoff notes.
- Keep `current-status.md` as a hot index and mainline snapshot. Do not require every developer branch to update it for routine progress.
- Keep `task-board.md` as a compact task directory. It should point to task status files rather than embedding full task history or long checklists.
- Use `.claw/integration-queue.md` to record integration branches, merge order, validation gates, and the integration owner.
- Use `.claw/team-status.md` only as a generated manager summary. Do not treat it as a source of truth.
- A project manager or integration owner should reconcile per-task status files into `task-board.md` and `current-status.md` during integration.

In `Project-Manager-Gated Authorization Mode`:

- A project must designate at least one `MANAGER-xxx` identity before adding developers or assignments.
- If a project uses this skill and has any `.claw/developers/`, `.ai-dev/developers/`, `.claw/assignments/`, `.ai-dev/assignments/`, `assignment_path`, or `local_login_required: true` record, the hard identity gate is enabled automatically.
- When the hard identity gate is enabled, no AI agent or developer may edit source code, tests, runtime configuration, migrations, generated application assets, feature docs, task status files, or other project implementation files until `scripts/dev-login.py` has returned `allowed` for the current local session and intended task scope.
- There is no chat, memory, or cache bypass for the hard identity gate. A declared `developer_id`, known user name, Git author/email, prior conversation, cached key path, or visible project role is not proof of identity.
- If `scripts/dev-login.py` cannot be found, cannot run, lacks a private key path, lacks a task when the edit is task-scoped, lacks intended file paths, or returns any `blocked_*` finding, the agent must stop before editing and ask the project manager or user to complete identity verification or assignment setup.
- Only the project manager may create, suspend, revoke, or rotate developer records.
- Only the project manager may create, revoke, extend, or expand assignment records.
- Developer records should bind `developer_id` to a Git platform account and an SSH commit signing key fingerprint.
- Default identity policy: one Git platform account should map to one active `developer_id`.
- If the same Git account must hold multiple active identities, each identity must use a different SSH commit signing key fingerprint and the project must mark that exception explicitly.
- The same Git account plus the same SSH signing key fingerprint must not represent both a `MANAGER-xxx` and a `DEV-xxx` identity unless the project has explicitly chosen a loose experimental policy.
- Assignment records must name `assigned_by: MANAGER-xxx`, `assignee: DEV-xxx`, `branch`, `touch_policy`, `status`, and a `signature` or external verification reference. They should also declare a scope model:
  - `scope_mode: exact_files` for narrow tasks where all intended write paths are known; `scope_files` is the hard file boundary.
  - `scope_mode: task_bounded_broad_code` for normal feature implementation; `allowed_write_roots` grants broad source/test write access, `protected_paths` blocks sensitive areas unless an exact protected file is explicitly listed in `scope_files`, and the task spec plus acceptance criteria define the work boundary.
- Developers and AI agents must run `scripts/dev-login.py` before local development when the hard identity gate is enabled. The login must verify identity status, SSH private key possession, and, when a task is provided, assignment scope.
- Developers and AI agents must run or logically perform the preflight authorization check before editing: identity active, assignment active, assignee matches, branch matches when known, and target files are permitted by the assignment scope mode.
- If the preflight result is not allowed, the agent must stop development and ask the project manager to update the assignment or team record.
- CI or platform automation should call `scripts/check-assignment.py` with the review author identity, branch, and changed files. Branch protection should require the check to pass before merge.
- For Codeup, each developer stores a local `YUNXIAO_TOKEN` outside the repository. Before creating a change request, `scripts/create-codeup-change-request.py` checks for `YUNXIAO_TOKEN`; if missing, it stops and links to the Yunxiao personal access token documentation. Use `scripts/store-yunxiao-token.py` to write the token to `.claw-local/codeup.env`. The create script treats `repositoryId` as the path parameter and sends numeric `sourceProjectId` and `targetProjectId` in the JSON body; when `repositoryId` is a full path, configure `CODEUP_SOURCE_PROJECT_ID` and `CODEUP_TARGET_PROJECT_ID` explicitly.
- When the user asks to "push to the test environment" or "推送到测试环境", use `scripts/push-test-environment.py` by default. It treats the current branch as the development branch, merges it into `dev`, uses a source-branch-wins policy for conflicts, pushes `dev` to the remote, and restores the original branch after success.
- For GitHub Actions, copy `templates/github-workflows/check-assignment.yml` into `.github/workflows/check-assignment.yml` in the adopting project and adapt it as needed.

Recommended identity and authorization flow:

1. A project manager initializes the project state and records their public key or verified Git identity.
2. The manager registers each developer in `.claw/developers/DEV-xxx.yaml`, including Git platform username and SSH signing key fingerprint when available.
3. The manager creates a task card and assignment file for each parallel task.
4. Each developer declares their `developer_id`, works only on their assigned branch and task boundary, avoids protected paths unless explicitly authorized, and updates only their task status slice.
5. Each local developer session runs `scripts/dev-login.py` before development; each review-request check runs `scripts/check-assignment.py` before merge.
6. The integration owner merges branches through the integration queue, runs real verification, updates `test-report.md`, and refreshes the hot state.

Recommended team-status aggregation flow:

1. Read `.claw/developers/*.yaml` for team members, roles, public identity, and identity status.
2. Read `.claw/assignments/*.yaml` for authorized task ownership, branch, change request URL or PR URL, write scope, and assignee.
3. Read `.claw/tasks/*.md` for per-task progress, assignee-reported status, change request URL or PR URL, blockers, and verification notes.
4. Read `.claw/task-board.md` for task title, priority, owner role, dependencies, and board status.
5. Read `.claw/integration-queue.md` for merge queue, integration owner, merge order, and integration status.
6. Derive each developer's assigned tasks, active tasks, contribution status, validation status, and integration status.
7. Print the summary or refresh `.claw/team-status.md` with `scripts/summarize-team-status.py`.

`team-status.md` must remain a derived view. If it conflicts with developer records, assignments, task status files, task board, or integration queue, repair or regenerate `team-status.md` rather than changing the source files to match it.

## Delivery Documentation Model

Use `docs/specs/` as the durable home for feature-level delivery documents.

- Keep one primary spec per feature, from requirement through rollout.
- In brownfield projects, create one `PROJECT-BASELINE.md` to describe the current legacy system before trying to normalize all feature docs.
- Put the full requirement, design, implementation plan, acceptance criteria, and handoff notes in that spec.
- Link the spec from `task-board.md` through `spec_path`.
- Keep `.claw/` for state and coordination, not for long-form feature design.

Create or update a feature spec before major implementation when the work is any of:

- a new feature
- a cross-module change
- an API or data-shape change
- a non-trivial refactor
- work likely to be handed off between agents or sessions

Small and isolated fixes may use only a concise task card plus `.claw/tasks/TASK-xxx.md` if no durable feature spec is needed.

Create or update `PROJECT-BASELINE.md` when the work is any of:

- the repo is an existing project with no prior state protocol
- major legacy areas are undocumented
- active work depends on inferred architecture or undocumented operational knowledge
- multiple agents need a shared baseline before feature-level specs are created

## Source Of Truth Rules

Do not maintain the same fact independently in multiple files.

| Fact | Source of truth | Other files may do |
|------|------|------|
| Current task, phase, next action | `current-status.md` | Reference it briefly |
| Execution task queue, owner roles, dependencies, status-file pointers | `task-board.md` | Reference task IDs only |
| Developer identity, Git platform account, SSH signing key fingerprint, role status, long-lived scope | `.claw/developers/DEV-xxx.yaml` | Reference developer IDs only |
| Task authorization, manager, branch, scope mode, write roots, protected paths, signed assignment, preflight status | `.claw/assignments/TASK-xxx.yaml` | Reference assignment path only |
| Individual task current state, progress, changed files, evidence, handoff | `.claw/tasks/TASK-xxx.md` | Summarize status only |
| Integration branch, merge order, merge gates | `.claw/integration-queue.md` | Reference queue ID or task IDs only |
| Team member and contribution summary | `.claw/team-status.md` | Derived from source files only; regenerate when stale |
| Archived completed and canceled tasks older than the active board window | `task-archive.md` | Reference archived task IDs only |
| Product scope and success metrics | `goals.md` | Summarize only |
| Legacy system baseline, undocumented architecture, active unknowns | `docs/specs/PROJECT-BASELINE.md` | Reference the path only |
| Feature-specific design and acceptance criteria | `docs/specs/FEAT-xxx-*.md` | Reference the `spec_path` only |
| Technical decisions and reversals | `decisions.md` | Link or reference only |
| Bugs, blockers, risks | `issue-list.md` | Mention issue IDs only |
| Test results and coverage | `test-report.md` | Copy only a short summary |
| Build, deploy, runtime operations | `devops.md` | Reference commands or sections only |

If files conflict, repair the summary file and preserve the source-of-truth file.

## Session Workflow

### 1. Session start

- Resolve the canonical state directory.
- Read `current-status.md` first.
- Read `task-board.md` for any implementation, handoff, or prioritization work, then read only the active task's `.claw/tasks/TASK-xxx.md` file.
- Read `task-archive.md` only when completed-task history or archived handoff context matters.
- Read additional files only when triggered by the task, by `current-status.md`, by `task-board.md`, or by the active task status file.
- In brownfield projects, open `docs/specs/PROJECT-BASELINE.md` before major legacy changes when it exists.
- Open the referenced feature spec or baseline doc before major code changes when the task has `spec_path`.
- In asynchronous parallel delivery, read the referenced developer record, assignment file, task status file, and integration queue only when the task index or current work references them.
- Before editing when the hard identity gate is enabled, run `scripts/dev-login.py` for local challenge-response identity verification and assignment scope. Do this automatically; do not wait for the user to ask for identity verification. Use `scripts/check-assignment.py` only for CI or assignment-only checks, not as a replacement for local `dev-login.py`.
- If the hard identity gate is enabled and identity verification has not succeeded in the current session, stop before file edits. Ask for the SSH key path, task id, branch, or assignment update needed to run `scripts/dev-login.py`.
- When a manager asks for team status, generate or read `.claw/team-status.md` using the standard aggregation flow before making management decisions.
- Infer whether the task touches hot state only, or also warm/cold files and feature docs.

### 2. During execution

- Update state only when a meaningful fact changes.
- Prefer concise deltas over narrative logs.
- Record verified facts, inferred hypotheses, and open questions separately.
- Keep task status, `owner_role`, and `next_action` aligned with real progress.
- If implementation diverges from the spec, update the spec before or with the code change.
- In brownfield adoption, prefer forward-filling the baseline over rewriting legacy history from memory.
- Update `.claw/tasks/TASK-xxx.md` for routine task progress, changed files, verification evidence, blockers, and handoff notes. The task board should only change when index fields change.
- In asynchronous parallel delivery, developers update only their assigned task status file for routine progress. The manager or integration owner updates `task-board.md`, `current-status.md`, and `integration-queue.md` when coordination state changes.
- `team-status.md` should be regenerated from source files after assignments, per-task status, integration queue, or task board changed.
- Before editing files in parallel work, compare the requested changes with the assignment scope model and `touch_policy`. If the identity is unknown, the assignment is inactive, the assignee does not match, the branch does not match, the change falls outside broad write roots, or the change touches protected paths without exact authorization, stop and ask the project manager or user to update the assignment.
- If the hard identity gate is enabled, perform the identity gate before this comparison and before any file modification. Scope comparison without a successful local login is not sufficient.

### 3. Session end

- Always refresh `current-status.md` by rewriting it as the latest compact snapshot, not by appending a session log.
- Update any triggered file with only the facts established in the session.
- Update the active task card only when compact index fields changed: status, priority, owner role, dependency, blocker, branch, review URL, spec path, assignment path, task status path, or next action.
- Update the active `.claw/tasks/TASK-xxx.md` file when progress, evidence, changed files, blocker detail, or handoff context changed.
- Regenerate `team-status.md` when the user asks for team status or when manager-facing contribution state changed.
- When `Completed Tasks` in `task-board.md` grows past 20 task cards, move the oldest completed or canceled task cards into `task-archive.md`.
- Update the feature spec's implementation progress and handoff notes when delivery facts changed.
- Update `PROJECT-BASELINE.md` when the session verified or corrected legacy understanding that future work will depend on.
- Do not fabricate test, deploy, or issue status.

## Read Triggers

Read these files only when the condition is true:

- `goals.md`: scope changed, priorities changed, MVP/V1 questions appeared, or the user asked "why are we doing this?"
- `decisions.md`: architecture changed, a tech choice was made, a previous decision was challenged, or trade-offs mattered.
- `issue-list.md`: a bug, blocker, regression, risk, or unresolved failure exists.
- `task-board.md`: implementation started, work must be split, multiple agents may touch the project, or a handoff is likely.
- `integration-queue.md`: multiple developer branches are being merged, a merge order matters, or validation gates are coordinated across tasks.
- `team-status.md`: the manager asks for team status, contribution status, assigned work, or integration readiness.
- `.claw/developers/DEV-xxx.yaml`: a developer identity, role, public key, or active status must be verified.
- `.claw/assignments/TASK-xxx.yaml`: a task is assigned to a specific developer, branch, or write scope.
- `.claw/tasks/TASK-xxx.md`: a task is active, a developer reports progress, changed files, evidence, blockers, or handoff for one task.
- `task-archive.md`: historical completed work must be reviewed, a resumed task depends on archived context, or the board overflowed its completion window.
- `test-report.md`: tests were run, failures need context, coverage matters, or quality gates are part of the task.
- `devops.md`: build, startup, env vars, deployment, operations, or incident handling are involved.
- `docs/specs/PROJECT-BASELINE.md`: the repo is legacy, undocumented behavior blocks progress, or new agents need a shared baseline.
- `docs/specs/FEAT-xxx-*.md`: a task card references `spec_path`, a non-trivial feature is being designed or implemented, or a new agent must resume feature work.

Do not read all state files or all specs by default.

## Update Triggers

Update files only when the condition is true:

- `current-status.md`: at session end, or when task direction materially changes.
- `goals.md`: scope, milestones, success metrics, or constraints changed.
- `decisions.md`: a non-trivial technical decision was made, replaced, or rejected.
- `issue-list.md`: a new issue was discovered, issue state changed, or a blocker was resolved.
- `task-board.md`: a task was created, reprioritized, claimed, blocked, reviewed, completed, canceled, or its compact index fields changed.
- `integration-queue.md`: an integration branch, merge order, merge gate, or integration owner changed.
- `team-status.md`: generated only by the standard aggregation method after source files changed or the manager requested a current view.
- `.claw/developers/DEV-xxx.yaml`: a developer was added, suspended, rotated, or had identity metadata changed.
- `.claw/assignments/TASK-xxx.yaml`: a manager assigned, revoked, extended, or changed the authorized task scope.
- `.claw/tasks/TASK-xxx.md`: task progress, changed files, verification, blocker detail, implementation notes, or handoff context changed.
- `task-archive.md`: `Completed Tasks` exceeded 20 items, archived work needed historical correction, or older completed tasks must be preserved during cleanup.
- `test-report.md`: and only after a real test command or verification step ran.
- `devops.md`: build/run/deploy instructions changed, or a verified operational fix was learned.
- `docs/specs/PROJECT-BASELINE.md`: verified legacy understanding changed, active unknowns were resolved, or adoption coverage expanded.
- `docs/specs/FEAT-xxx-*.md`: requirement, design, task breakdown, acceptance criteria, implementation progress, or handoff context changed.

## AI Behavior Rules

Follow these rules whenever this skill is active:

1. Read the minimum state required to do the task safely.
2. Update only the files whose trigger conditions fired.
3. Never invent results for tests, builds, incidents, or deployments.
4. Keep summaries short; keep durable knowledge structured.
5. Preserve user-authored intent. Do not silently overwrite goals or decisions.
6. Separate fact from inference from pending confirmation.
7. Use repository tools and project commands before ad-hoc shell exploration.
8. Record only reusable project knowledge, not transient chain-of-thought.
9. When fixing conflicts between files, preserve the source-of-truth file and repair summaries around it.
10. Prefer incremental updates over rewriting history.
11. For non-trivial delivery work, create or update a feature spec before major code changes.
12. Use `owner_role` as the durable responsibility field. Treat `claimed_by` as optional runtime context.
13. In brownfield projects, create or refresh `PROJECT-BASELINE.md` before attempting large legacy changes.
14. Do not require complete historical backfill before using this skill on an old project.
15. Keep `task-board.md` current, but archive older completed or canceled tasks instead of deleting them outright.
16. In asynchronous parallel delivery, do not store manager passwords, developer tokens, private keys, or reusable secrets in the repository.
17. Developers must not knowingly edit outside their assignment task boundary, broad write roots, exact protected-path authorization, or their own task status slice without explicit reassignment.
18. `current-status.md` is a mainline hot index, not a per-developer diary. Keep routine per-task progress in `.claw/tasks/TASK-xxx.md`.
19. `task-board.md` is a directory of tasks, not a task diary. Every active task should link to a small `.claw/tasks/TASK-xxx.md` file.
20. `team-status.md` is a generated manager view. Do not hand-edit it as authoritative project state.
21. In manager-gated mode, only project managers may add team members or change assignment scope.
22. Default new teams to Git platform account binding plus SSH commit signing. Do not rely on local Git author name or email as proof of identity.
23. If preflight authorization fails, block development instead of making speculative changes.
24. Do not bind one Git platform account to multiple active identities by default. If role sharing is unavoidable, require distinct SSH signing key fingerprints per identity and record the exception.
25. For local developer login, verify private-key possession through a one-time SSH signature challenge and store only local key paths in ignored cache files.
26. When the hard identity gate is enabled, `scripts/dev-login.py` must return `allowed` before any code, test, config, migration, generated app asset, feature spec, or task status edit. There are no exceptions based on chat context, remembered identity, Git metadata, or cache presence.

## Writing Rules

Use these conventions in all state files:

- Add YAML front matter for machine-stable fields.
- Use ISO-like timestamps such as `YYYY-MM-DDTHH:MM:SSZ`.
- Use stable status enums rather than free-form prose where possible.
- Use stable IDs such as `TASK-001`, `ISSUE-001`, `ADR-001`, and `FEAT-001`.
- Use stable identity IDs such as `MANAGER-001` and `DEV-alice` when asynchronous parallel delivery is enabled.
- Keep each section scannable with short bullets.
- Keep long history out of `current-status.md`; it is a snapshot, not a transcript.
- If the repo needs session archives, create a separate history file or folder rather than bloating the hot file.

## Progressive Disclosure Rules

Use indexes first, then disclose detail only when a task requires it:

1. `current-status.md` points to the active task and the next files to read.
2. `task-board.md` lists task IDs, status, owner role, dependencies, blockers, and `task_status_path`.
3. `.claw/tasks/TASK-xxx.md` stores the current state for that one task.
4. `docs/specs/FEAT-xxx-*.md` stores feature requirements, design, acceptance criteria, and durable implementation context.
5. `test-report.md`, `issue-list.md`, `decisions.md`, and `devops.md` store their own evidence and domain facts.

Size budgets:

- Keep `current-status.md` under 60 lines.
- Keep each task card in `task-board.md` under 20 lines.
- Keep `task-board.md` as an index; do not embed long `Done When`, verification logs, changed-file lists, or handoff narratives there.
- Keep each `.claw/tasks/TASK-xxx.md` focused on one task. Split historical detail into specs, archives, or test reports when it stops being immediately useful for the current task.
- Use `task-archive.md` for completed or canceled task cards that age out of the active board window.

## Required Verification Rules

- Test outcomes go to `test-report.md` only after a real command ran.
- Root cause statements in `issue-list.md` must be marked as verified or inferred.
- Decision entries in `decisions.md` must explain why the chosen option won.
- `devops.md` should contain only commands or procedures that are known to work or are clearly marked as pending verification.
- Tasks in `in_progress` must have a non-empty `owner_role`.
- Tasks with `spec_path` must reference a real spec or baseline document under `docs/specs/`.
- `PROJECT-BASELINE.md` must separate verified facts from inferred legacy understanding.
- `task-board.md` should keep at most 20 task cards in `Completed Tasks`; archive older completed or canceled cards into `task-archive.md`.
- Active task cards should reference a real `.claw/tasks/TASK-xxx.md` file through `task_status_path`.
- `current-status.md` must not contain session-log sections such as `本次会话进展`, `修改文件`, or `已验证事实`.
- Project-root `README.md` and `AGENTS.md` must contain the managed `cc-aidev-guidelines-common` declaration block, including the GitHub install source.
- Assignment files must not contain private keys, manager passwords, bearer tokens, or reusable secrets.
- When an assignment uses `scope_mode: exact_files`, code changes must stay inside `scope_files` unless a manager updates the assignment.
- When an assignment uses `scope_mode: task_bounded_broad_code`, normal source and test changes may use `allowed_write_roots`, but protected paths require explicit `scope_files` authorization and every changed file must be explainable by the linked task and feature spec.
- `team-status.md` must have valid front matter when generated, but its contents are derived and may be regenerated at any time.
- Developer records should bind Git platform username and SSH signing key fingerprint when a project uses manager-gated authorization.
- Developer records should include the public SSH key when local challenge-response login is used; fingerprints alone are not enough to prove private-key possession.
- Active developer records should not reuse the same `git_username` unless each record has a distinct `ssh_signing_key_fingerprint` and an explicit role-sharing note.
- Active manager and developer records must not share both `git_username` and `ssh_signing_key_fingerprint` under the default identity policy.
- Assignment files should use `assigned_by: MANAGER-xxx` and `status: active` before development starts.
- `scripts/dev-login.py` must return `allowed` before local development proceeds when the hard identity gate is enabled.
- `scripts/check-assignment.py` must return `allowed` before CI merge checks proceed.
- Broad code authorization is not a bypass for product scope: PRs should include or maintain a change manifest explaining why each touched module is needed for the assigned task.

## Recommended Project Bootstrapping

### Greenfield

1. Create `.claw/`.
2. Create or update the project-root `README.md` and `AGENTS.md` declaration block.
3. Create `docs/specs/`.
4. Copy the eight core state templates from `templates/`.
5. Copy `_feature-spec-template.md` into `docs/specs/`.
6. Create optional async parallel directories: `.claw/developers/`, `.claw/assignments/`, `.claw/tasks/`, and `.claw/integration-queue.md`.
7. Create optional derived manager view `.claw/team-status.md`.
8. Initialize `current-status.md` first.
9. Fill `goals.md` with current scope and success criteria.
10. Create the first compact task card in `task-board.md`.
11. Create `.claw/tasks/TASK-001.md` for the task's current state.
12. Create the first feature spec before major implementation when required.
13. Keep the remaining files sparse until their triggers fire.

### Brownfield Adoption

1. Create `.claw/`.
2. Create or update the project-root `README.md` and `AGENTS.md` declaration block.
3. Create `docs/specs/`.
4. Copy the eight core state templates from `templates/`.
5. Copy `_feature-spec-template.md` and `_project-baseline-template.md` into `docs/specs/`.
6. Create optional async parallel directories and `integration-queue.md`.
7. Create optional derived manager view `.claw/team-status.md`.
8. Initialize `current-status.md` first.
9. Create `docs/specs/PROJECT-BASELINE.md` from the baseline template.
10. Record only the current verified state, inferred architecture, active unknowns, and live delivery constraints.
11. Create the first compact adoption task in `task-board.md`, which may reference `PROJECT-BASELINE.md`.
12. Create `.claw/tasks/TASK-001.md` for the adoption task's current state.
13. Add feature specs only for the legacy areas that are actively being changed.
14. Keep the remaining history sparse until those areas are touched.

## File Roles

- `templates/current-status.md`: compact hot state snapshot and read index
- `templates/goals.md`: long-lived project intent
- `templates/decisions.md`: ADR log with status transitions
- `templates/issue-list.md`: active and resolved issues
- `templates/task-board.md`: compact delivery queue, owner roles, dependencies, and task status pointers
- `templates/task-archive.md`: archived completed or canceled task cards beyond the board retention window
- `templates/test-report.md`: latest verified test evidence
- `templates/devops.md`: operational runbook
- `templates/team-status.md`: generated manager view scaffold
- `templates/integration-queue.md`: optional async parallel integration queue
- `templates/parallel/developer.yaml`: optional developer identity record template
- `templates/parallel/assignment.yaml`: optional manager-signed task assignment template
- `templates/parallel/task-status.md`: per-task current status template
- `templates/platforms/codeup/`: default Codeup change request flow and description template
- `scripts/ensure-agent-guidance.sh`: managed project-root `README.md` and `AGENTS.md` skill declaration
- `scripts/dev-login.py`: local SSH challenge-response developer login and optional assignment gate
- `scripts/check-assignment.py`: manager-gated preflight authorization check for local development and CI, supporting both exact file scopes and task-bounded broad code roots with protected paths
- `scripts/store-yunxiao-token.py`: local Yunxiao token storage helper
- `scripts/create-codeup-change-request.py`: Codeup change request creation helper
- `scripts/push-test-environment.py`: test-environment branch push helper
- `templates/github-workflows/check-assignment.yml`: example GitHub Actions PR gate for assignment scope
- `templates/docs/feature-spec-template.md`: one-feature requirement, design, implementation, and handoff template
- `templates/docs/project-baseline-template.md`: legacy-project baseline, inferred architecture, and adoption handoff template

For the full state model, enums, and maintenance rules, read [STATE-MODEL.md](STATE-MODEL.md).
For a complete sample state set, read [examples/README.md](examples/README.md).

## Anti-Patterns

- Reading all state files at the start of every task
- Writing the same fact into multiple files as if each were authoritative
- Treating `task-board.md` like a bug log, design document, or task diary
- Deleting completed tasks from `task-board.md` without archiving them when the board exceeds its retention window
- Updating `test-report.md` without running tests
- Recording guesses as if they were verified findings
- Writing code for a non-trivial feature before a feature spec exists
- Requiring a legacy repo to backfill every historical decision before the skill can be used
- Mixing baseline notes into `current-status.md` instead of `PROJECT-BASELINE.md`
- Turning `current-status.md` into a long chronological diary
- Leaving task progress in `task-board.md` instead of `.claw/tasks/TASK-xxx.md`
- Hand-editing `team-status.md` instead of regenerating it from source files
- Using `owner` as an unstable agent nickname instead of a durable `owner_role`
- Letting AI-generated summaries overwrite explicit user decisions
- Leaving `README.md` or `AGENTS.md` without the managed skill declaration block in a project that claims to follow this protocol
- Treating Git author name or email as strong identity proof without platform verification or commit signing
- Treating a cached private key path as proof of identity without re-running challenge-response verification
- Editing project files after a chat-declared identity but before `scripts/dev-login.py` returns `allowed`
- Treating `scripts/check-assignment.py` as a substitute for local SSH challenge-response login
- Letting a developer self-assign new scopes without project manager authorization
