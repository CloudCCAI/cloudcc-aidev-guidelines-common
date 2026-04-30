---
name: cc-aidev-guidelines-common
description: Externalizes project state into `.claw/` or `.ai-dev/` files, adds a task board and spec-driven delivery docs, supports greenfield and brownfield adoption, and constrains AI coding behavior with explicit read/write triggers, source-of-truth rules, and verification requirements. Use for AI-assisted software delivery, persistent project memory, task handoff, ADR tracking, issue tracking, test logging, or agent coding standards.
skill_version: 3.4.0
---

# AI Agent Project State Protocol

Use this skill to turn project state into durable files that an AI agent can read, update, and audit across sessions.

## Skill Version

Canonical skill version: `3.4.0`

Use the `skill_version` field in this file's front matter as the source of truth for the installed skill version. If `README.md`, `CHANGELOG.md`, or other references drift, this field wins.

This skill has three goals:

1. Build a stable project state storage layer.
2. Enforce explicit AI development rules.
3. Make multi-agent delivery resumable through task cards and feature specs.

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
└── devops.md

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
- `scripts/validate-state.py` validates required files, front matter, task cards, and referenced feature specs

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
| Hot | `current-status.md` | Every session | Every session | Entry point, current snapshot, next action |
| Warm | `task-board.md` | Every implementation or handoff session | Triggered | Execution queue, dependencies, owner roles, handoff notes |
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

In `Brownfield Adoption Mode`:

- Create the minimum state skeleton first instead of backfilling the whole project history.
- Create or update the project-root `README.md` and `AGENTS.md` declaration block before the first substantial implementation session.
- Create `docs/specs/PROJECT-BASELINE.md` before broad implementation so new agents can resume legacy work safely.
- Mark facts in the baseline as `verified`, `inferred`, or `pending verification`.
- Apply full `task-board + spec` discipline from the current active work forward.
- Only backfill old modules when they are actively being changed or when the missing context is blocking progress.

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

Small and isolated fixes may use only a concise task card if no durable design context is needed.

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
| Execution task queue, owner roles, dependencies, handoff notes | `task-board.md` | Reference task IDs only |
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
- Read `task-board.md` for any implementation, handoff, or prioritization work.
- Read `task-archive.md` only when completed-task history or archived handoff context matters.
- Read additional files only when triggered by the task, by `current-status.md`, or by the active task card.
- In brownfield projects, open `docs/specs/PROJECT-BASELINE.md` before major legacy changes when it exists.
- Open the referenced feature spec or baseline doc before major code changes when the task has `spec_path`.
- Infer whether the task touches hot state only, or also warm/cold files and feature docs.

### 2. During execution

- Update state only when a meaningful fact changes.
- Prefer concise deltas over narrative logs.
- Record verified facts, inferred hypotheses, and open questions separately.
- Keep task status, `owner_role`, and `next_action` aligned with real progress.
- If implementation diverges from the spec, update the spec before or with the code change.
- In brownfield adoption, prefer forward-filling the baseline over rewriting legacy history from memory.

### 3. Session end

- Always refresh `current-status.md`.
- Update any triggered file with only the facts established in the session.
- Update the active task card whenever status, scope, owner role, or handoff notes changed.
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
- `task-board.md`: a task was created, reprioritized, claimed, blocked, reviewed, completed, canceled, or handed off.
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

## Writing Rules

Use these conventions in all state files:

- Add YAML front matter for machine-stable fields.
- Use ISO-like timestamps such as `YYYY-MM-DDTHH:MM:SSZ`.
- Use stable status enums rather than free-form prose where possible.
- Use stable IDs such as `TASK-001`, `ISSUE-001`, `ADR-001`, and `FEAT-001`.
- Keep each section scannable with short bullets.
- Keep long history out of `current-status.md`; it is a snapshot, not a transcript.
- If the repo needs session archives, create a separate history file or folder rather than bloating the hot file.

## Required Verification Rules

- Test outcomes go to `test-report.md` only after a real command ran.
- Root cause statements in `issue-list.md` must be marked as verified or inferred.
- Decision entries in `decisions.md` must explain why the chosen option won.
- `devops.md` should contain only commands or procedures that are known to work or are clearly marked as pending verification.
- Tasks in `in_progress` must have a non-empty `owner_role`.
- Tasks with `spec_path` must reference a real spec or baseline document under `docs/specs/`.
- `PROJECT-BASELINE.md` must separate verified facts from inferred legacy understanding.
- `task-board.md` should keep at most 20 task cards in `Completed Tasks`; archive older completed or canceled cards into `task-archive.md`.
- Project-root `README.md` and `AGENTS.md` must contain the managed `cc-aidev-guidelines-common` declaration block, including the GitHub install source.

## Recommended Project Bootstrapping

### Greenfield

1. Create `.claw/`.
2. Create or update the project-root `README.md` and `AGENTS.md` declaration block.
3. Create `docs/specs/`.
4. Copy the eight state templates from `templates/`.
5. Copy `_feature-spec-template.md` into `docs/specs/`.
6. Initialize `current-status.md` first.
7. Fill `goals.md` with current scope and success criteria.
8. Create the first task card in `task-board.md`.
9. Create the first feature spec before major implementation when required.
10. Keep the remaining files sparse until their triggers fire.

### Brownfield Adoption

1. Create `.claw/`.
2. Create or update the project-root `README.md` and `AGENTS.md` declaration block.
3. Create `docs/specs/`.
4. Copy the eight state templates from `templates/`.
5. Copy `_feature-spec-template.md` and `_project-baseline-template.md` into `docs/specs/`.
6. Initialize `current-status.md` first.
7. Create `docs/specs/PROJECT-BASELINE.md` from the baseline template.
8. Record only the current verified state, inferred architecture, active unknowns, and live delivery constraints.
9. Create the first adoption task in `task-board.md`, which may reference `PROJECT-BASELINE.md`.
10. Add feature specs only for the legacy areas that are actively being changed.
11. Keep the remaining history sparse until those areas are touched.

## File Roles

- `templates/current-status.md`: hot state snapshot and read index
- `templates/goals.md`: long-lived project intent
- `templates/decisions.md`: ADR log with status transitions
- `templates/issue-list.md`: active and resolved issues
- `templates/task-board.md`: delivery queue, owner roles, and handoff state
- `templates/task-archive.md`: archived completed or canceled task cards beyond the board retention window
- `templates/test-report.md`: latest verified test evidence
- `templates/devops.md`: operational runbook
- `scripts/ensure-agent-guidance.sh`: managed project-root `README.md` and `AGENTS.md` skill declaration
- `templates/docs/feature-spec-template.md`: one-feature requirement, design, implementation, and handoff template
- `templates/docs/project-baseline-template.md`: legacy-project baseline, inferred architecture, and adoption handoff template

For the full state model, enums, and maintenance rules, read [STATE-MODEL.md](STATE-MODEL.md).
For a complete sample state set, read [examples/README.md](examples/README.md).

## Anti-Patterns

- Reading all state files at the start of every task
- Writing the same fact into multiple files as if each were authoritative
- Treating `task-board.md` like a bug log or a design document
- Deleting completed tasks from `task-board.md` without archiving them when the board exceeds its retention window
- Updating `test-report.md` without running tests
- Recording guesses as if they were verified findings
- Writing code for a non-trivial feature before a feature spec exists
- Requiring a legacy repo to backfill every historical decision before the skill can be used
- Mixing baseline notes into `current-status.md` instead of `PROJECT-BASELINE.md`
- Turning `current-status.md` into a long chronological diary
- Using `owner` as an unstable agent nickname instead of a durable `owner_role`
- Letting AI-generated summaries overwrite explicit user decisions
- Leaving `README.md` or `AGENTS.md` without the managed skill declaration block in a project that claims to follow this protocol
