---
name: aidev-guideline-common
description: Externalizes project state into `.claw/` or `.ai-dev/` files and constrains AI coding behavior with explicit read/write triggers, source-of-truth rules, and verification requirements. Use for AI-assisted software delivery, persistent project memory, ADR tracking, issue tracking, test logging, or agent coding standards.
---

# AI Agent Project State Protocol

Use this skill to turn project state into durable files that an AI agent can read, update, and audit across sessions.

This skill has two goals:

1. Build a stable project state storage layer.
2. Enforce explicit AI development rules.

## Directory Layout

Store the state under `.claw/` by default. `.ai-dev/` is an acceptable alias if the project already uses it.

```text
.claw/
├── current-status.md
├── goals.md
├── decisions.md
├── issue-list.md
├── test-report.md
└── devops.md
```

Copy the templates from `templates/` when initializing a project.

Utility scripts are available under `scripts/`:

- `scripts/init-state.sh` initializes a state directory from templates
- `scripts/validate-state.py` validates required files and front matter

## Operating Model

Treat the six files as a layered memory system, not as six equally-hot documents.

| Layer | File | Default read | Default update | Purpose |
|------|------|------|------|------|
| Hot | `current-status.md` | Every session | Every session | Entry point, current snapshot, next action |
| Warm | `issue-list.md` | As needed | Triggered | Open problems, blockers, follow-up work |
| Warm | `test-report.md` | As needed | Triggered | Verified test outcomes from real runs |
| Cold | `goals.md` | Triggered | Triggered | Product scope, success criteria, constraints |
| Cold | `decisions.md` | Triggered | Triggered | Architecture and technical decisions |
| Cold | `devops.md` | Triggered | Triggered | Build, run, deploy, operations knowledge |

## Source Of Truth Rules

Do not maintain the same fact independently in multiple files.

| Fact | Source of truth | Other files may do |
|------|------|------|
| Current task, phase, next action | `current-status.md` | Reference it briefly |
| Product scope and success metrics | `goals.md` | Summarize only |
| Technical decisions and reversals | `decisions.md` | Link or reference only |
| Bugs, blockers, risks | `issue-list.md` | Mention issue IDs only |
| Test results and coverage | `test-report.md` | Copy only a short summary |
| Build, deploy, runtime operations | `devops.md` | Reference commands or sections only |

If files conflict, repair the summary file and preserve the source-of-truth file.

## Session Workflow

### 1. Session start

- Read `current-status.md` first.
- Read additional files only when triggered by the task or by `current-status.md`.
- Infer whether the task touches hot state only, or also warm/cold files.

### 2. During execution

- Update state only when a meaningful fact changes.
- Prefer concise deltas over narrative logs.
- Record verified facts, inferred hypotheses, and open questions separately.

### 3. Session end

- Always refresh `current-status.md`.
- Update any triggered file with only the facts established in the session.
- Do not fabricate test, deploy, or issue status.

## Read Triggers

Read these files only when the condition is true:

- `goals.md`: scope changed, priorities changed, MVP/V1 questions appeared, or the user asked "why are we doing this?"
- `decisions.md`: architecture changed, a tech choice was made, a previous decision was challenged, or trade-offs mattered.
- `issue-list.md`: a bug, blocker, regression, risk, or unresolved failure exists.
- `test-report.md`: tests were run, failures need context, coverage matters, or quality gates are part of the task.
- `devops.md`: build, startup, env vars, deployment, operations, or incident handling are involved.

Do not read all six files by default.

## Update Triggers

Update files only when the condition is true:

- `current-status.md`: at session end, or when task direction materially changes.
- `goals.md`: scope, milestones, success metrics, or constraints changed.
- `decisions.md`: a non-trivial technical decision was made, replaced, or rejected.
- `issue-list.md`: a new issue was discovered, issue state changed, or a blocker was resolved.
- `test-report.md`: and only after a real test command or verification step ran.
- `devops.md`: build/run/deploy instructions changed, or a verified operational fix was learned.

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

## Writing Rules

Use these conventions in all state files:

- Add YAML front matter for machine-stable fields.
- Use ISO-like timestamps such as `YYYY-MM-DDTHH:MM:SSZ`.
- Use stable status enums rather than free-form prose where possible.
- Keep each section scannable with short bullets.
- Keep long history out of `current-status.md`; it is a snapshot, not a transcript.
- If the repo needs session archives, create a separate history file or folder rather than bloating the hot file.

## Required Verification Rules

- Test outcomes go to `test-report.md` only after a real command ran.
- Root cause statements in `issue-list.md` must be marked as verified or inferred.
- Decision entries in `decisions.md` must explain why the chosen option won.
- `devops.md` should contain only commands or procedures that are known to work or are clearly marked as pending verification.

## Recommended Project Bootstrapping

1. Create `.claw/`.
2. Copy the six templates from `templates/`.
3. Initialize `current-status.md` first.
4. Fill `goals.md` with current scope and success criteria.
5. Keep the remaining files sparse until their triggers fire.

## File Roles

- `templates/current-status.md`: hot state snapshot and read index
- `templates/goals.md`: long-lived project intent
- `templates/decisions.md`: ADR log with status transitions
- `templates/issue-list.md`: active and resolved issues
- `templates/test-report.md`: latest verified test evidence
- `templates/devops.md`: operational runbook

For the full state model, enums, and maintenance rules, read [STATE-MODEL.md](STATE-MODEL.md).
For a complete sample state set, read [examples/README.md](examples/README.md).

## Anti-Patterns

- Reading all state files at the start of every task
- Writing the same fact into multiple files as if each were authoritative
- Updating `test-report.md` without running tests
- Recording guesses as if they were verified findings
- Turning `current-status.md` into a long chronological diary
- Letting AI-generated summaries overwrite explicit user decisions
