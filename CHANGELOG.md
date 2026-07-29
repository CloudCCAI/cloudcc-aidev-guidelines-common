# Changelog

## 5.1.3 - 2026-07-29

- 明确从仓库 `skill/` 安装技能时，技能根目录下的目标目录必须命名为 `cc-aidev-guidelines-common`，不得沿用源目录名 `skill`。
- 同步项目声明块生成器、状态模型、仓库说明、示例和回归测试。

## 5.1.2 - 2026-07-24

- 将 `.claw/current-status.md` 明确为每个用户独立维护、可随时重建且不计入共享初始化完成度的本地派生状态，并由初始化器写入 Git 忽略规则。
- `generate-current-status.py` 新增 `--user`，只呈现当前用户的活跃任务；未显式指定时沿用 Git/OS 用户解析顺序。
- 新增个人状态字段、忽略规则校验、迁移说明和回归测试；多人共享事实继续保留在 task board、task status 与 team status。

## 5.1.1 - 2026-07-24

- 新增 `check-skill-version.py`，优先以 `git ls-remote` 解析 GitHub `main` 提交 SHA，Git 不可用时回退到带随机查询参数和 `no-cache` 的 GitHub API，再读取该提交下不可变的 `skill/SKILL.md`。
- 版本检查失败时明确返回未知状态，不再依赖可能命中缓存的固定分支 Raw URL。
- 同步新项目 AGENTS 指令、示例、状态模型和缓存穿透回归测试。

## 5.1.0 - 2026-07-24

- 将测试冷归档从 `test-report-archive.md` 简化为 `test-archive.md`，并同步 kind、catalog、模板、脚本、校验器和测试。
- 新写入统一使用新名称；校验器继续兼容已有项目中的旧文件名。

## 5.0.9 - 2026-07-24

- 将 `issue-list.md` 调整为未闭环问题与最近 5 条关闭索引的温数据文件。
- 新增 `issue-archive.md` 和 `archive-resolved-issues.py`，只移动 `verified` / `closed` 完整条目；`fixed` 待验证问题继续留在当前列表。
- 增加 catalog、模板、校验规则、确定性迁移与幂等回归测试。

## 5.0.8 - 2026-07-24

- 将当前 `test-report.md` 限制为 150 行以内，并只保留最新摘要、未解决状态索引和最近 5 条详细测试记录。
- 新增 `test-report-archive.md` 冷归档和 `archive-test-reports.py`；历史验证证据保持原文，归档批次中的未解决状态在当前报告保留紧凑索引。
- 增加 legacy 大文件的确定性迁移、catalog/模板/校验规则和回归测试。

## 5.0.7 - 2026-07-24

- 将 `task-board.md` 已完成区的保留上限从 20 张降为最新 5 张，减少实现和排期时的重复上下文。
- 新增带项目锁、原子写入和幂等去重的 `archive-completed-tasks.py`；第 6 张及更旧的终态卡片移动到 `task-archive.md`，任务事实文件保持不变。
- 同步状态模型、模块说明、模板、校验阈值和回归测试。

## 5.0.6 - 2026-07-24

- 将新写入的 UTC 时间从 `YYYY-MM-DDTHH:MM:SSZ` 改为普通日期时间格式 `YYYY-MM-DD HH:MM:SS`。
- 生成器、初始化器、登录状态、派生视图、示例和测试统一使用新格式；校验器继续兼容已有项目中的历史格式。

## 5.0.5 - 2026-07-23

- 为 `docs/design` 和 `docs/specs` 中每份 Markdown 增加同目录、同 basename 的离线 HTML 人类阅读视图；Markdown 保持唯一事实源。
- 新增标准库实现的 `generate-project-docs-html.py`，支持单文件刷新、项目批量同步和源内容摘要检查。
- 初始化器和 FEAT 分配器自动生成配对 HTML，状态校验器报告缺失或过期的阅读视图。

## 5.0.4 - 2026-07-23

- 新生成的项目 `AGENTS.md` 会要求 Agent 在每次新聊天或新会话中读取上游 `SKILL.md` 的 `metadata.skill_version`，发现新版本时自动更新并重新加载技能。
- 保持已有完整受控声明块和所有块外内容不变，避免初始化或同步静默覆盖项目自定义指令。

## 5.0.3 - 2026-07-19

- 将简体中文提升为唯一规范的人类可读模板，新项目不再询问或重配置文档语言。
- 保留早期 v5 `en`、`zh-CN`、`pending` 和缺失语言字段的读取兼容；5.0.3 起要求 `language: zh-CN`，既有文档不自动翻译。
- 删除 locale 镜像、无运行入口的 v4/Codeup 模板、派生 team-status 模板和死代码，派生视图与指导块固定输出中文。
- 合并 Codeup 本地配置读写，token 轮换不再覆盖项目配置，并使用原子 `0600` 写入。
- 让 DevOps 外部资产契约由 catalog 驱动 onboarding 与 validator，并修复重复执行时无变化却刷新状态时间的问题。
- 将两个 v5 示例升级为中文 5.0.3，新增历史兼容、固定中文、Codeup 配置权限和二次清理回归测试。

## 5.0.2 - 2026-07-19

- 增加按客户环境拆分的根目录 `DevOps/`，每个环境独立维护 Dockerfile 和 `.env.example`；客户未定时可确认预留 DEV/UAT/PROD。
- 增加 `docs/help` 产品使用手册目录和 `docs/design` 功能/流转设计目录，并通过 catalog 幂等补齐索引。
- 将 FEAT/TASK 自动命名来源固定为全局 Git `user.name`、项目本地 Git `user.name`、操作系统用户名的顺序。

## 5.0.1 - 2026-07-18

- Added manifest `language` selection with resumable `pending`, `en`, and `zh-CN` states.
- Added deterministic English and Simplified Chinese templates for all v5 human-readable project-management documents.
- Made onboarding, FEAT/TASK allocation, current-status generation, team-status generation, and managed README/AGENTS blocks honor the selected language.
- Preserved v4 and early v5 compatibility without automatically translating existing files.
- Updated validation, schema, catalog, examples, documentation, and tests for document policy version 3.

## 5.0.0 - 2026-07-18

- Added `.claw/manifest.yaml` and a shared state catalog for guided, resumable Greenfield/Brownfield initialization.
- Added independent switches for project state, collaboration gate, and Codeup/GitHub change review with conditional resource loading.
- Added per-file initialization states, the `ARCHITECTURE` module in `decisions.md`, `directory-map.md`, empty task-board bootstrap, and event-created state files.
- Added per-user FEAT/TASK names and counters, atomic ID reservation, and multi-workstream `current-status.md` generation.
- Added legacy document snapshots and v4/v5 validation so existing files remain grandfathered while new files follow policy version 2.
- Simplified `SKILL.md` into a progressive router and moved detailed onboarding, module, and platform workflows into references.
- Standardized project state on `.claw/` and local private configuration on `.claw-local/`.

## 4.1.3 - 2026-05-27

- Clarified async manager-gated task status ownership: developers record routine contribution progress in `.claw/tasks/TASK-xxx.md`, while `task-board.md` remains a manager/integration-owned coordination index unless explicitly authorized in assignment scope.
- Fixed assignment path matching so bare directory entries in `allowed_write_roots`, `protected_paths`, and developer `allowed_scopes` are treated as recursive roots, while `scope_files` remains exact unless a glob is explicit.

## 4.1.2 - 2026-05-22

- Added `scripts/configure-codeup-change-request.py` so each Codeup-hosted project can resolve its own repository id and write local `CODEUP_REPOSITORY_ID`, `CODEUP_SOURCE_PROJECT_ID`, `CODEUP_TARGET_PROJECT_ID`, `CODEUP_TARGET_BRANCH`, and `CODEUP_CREATE_FROM` defaults.
- Updated Codeup setup documentation to run token storage first, then local project-default configuration.

## 4.1.1 - 2026-05-22

- Corrected `scripts/create-codeup-change-request.py` to align Codeup `CreateChangeRequest` payloads with the Yunxiao OpenAPI contract: `repositoryId` stays in the path, while numeric `sourceProjectId` and `targetProjectId` are sent in the body.
- Documented the same-repository default where a numeric `repositoryId` supplies both project ids, and the full-path repository case that requires explicit project ids.
- Stored the current repository's local ignored Codeup defaults in `.claw-local/codeup.env` after resolving repository id `6551067` through the Codeup repository list API.

## 4.1.0 - 2026-05-21

- Added progressive state disclosure rules: `current-status.md` is a hot index, `task-board.md` is a compact task directory, and each active task links to `.claw/tasks/TASK-xxx.md`.
- Updated templates so new projects start with compact hot files and per-task status slices.
- Added validation guardrails for hot-file size, forbidden session-history sections, task-card size, and required active `task_status_path` references.
- Migrated this repository's active tasks into individual `.claw/tasks/TASK-xxx.md` files.

## 4.0.0 - 2026-05-20

- Added `scripts/push-test-environment.py` to merge a development branch into `dev`, resolve conflicts with a source-branch-wins policy, and push `dev` for test-environment deployment.
- Documented the "push to test environment" trigger in the skill protocol, README, and state model.
- Added `FEAT-009` and `ADR-009` for the test-environment branch push policy.

## 3.9.0 - 2026-05-19

- Made Aliyun Yunxiao Codeup the default platform flow for review request submission.
- Added `scripts/store-yunxiao-token.py` to store each developer's local `YUNXIAO_TOKEN` outside Git-tracked files.
- Added `scripts/create-codeup-change-request.py` to create Codeup change requests through Yunxiao OpenAPI and stop with token setup guidance when `YUNXIAO_TOKEN` is missing.
- Added `templates/platforms/codeup/` with Codeup change request conventions and a description template.
- Preserved the existing GitHub Actions assignment gate as an optional platform example.

## 3.8.0 - 2026-05-18

- Added task-bounded broad code authorization for manager-gated assignments.
- Introduced `scope_mode: task_bounded_broad_code`, `allowed_write_roots`, `protected_paths`, `task_boundary`, and `change_manifest_required` guidance.
- Kept `scope_mode: exact_files` as the backward-compatible default for narrow tasks and existing assignments.
- Updated `scripts/check-assignment.py` so normal source/test changes can be authorized by broad write roots while protected paths require exact `scope_files` authorization.
- Updated templates, README, STATE-MODEL, validation rules, and feature specs to treat task authorization as the main gate and file-level control as protection for sensitive areas.

## 3.7.1 - 2026-05-17

- Hardened local identity verification from recommended guidance into a mandatory hard pre-edit gate when identity or assignment records exist.
- Documented that chat-declared identity, remembered context, Git author/email, cached key paths, and `scripts/check-assignment.py` cannot bypass local `scripts/dev-login.py` challenge-response login.
- Required agents to stop before editing source, tests, runtime config, migrations, generated app assets, feature specs, or task status files when `dev-login.py` is missing, cannot run, lacks required inputs, or returns `blocked_*`.
- Clarified that only explicit PM bootstrap or repair edits to identity/assignment records may happen before local login, and those edits must not touch implementation files.

## 3.7.0 - 2026-05-17

- Added `scripts/dev-login.py` for local SSH challenge-response identity verification before development starts.
- Added optional local identity cache guidance for `.claw-local/identity.json`; caches store only key paths and public identity metadata.
- Documented the local login flow: derive public key and fingerprint from a private key, match `.claw/developers/*.yaml`, sign a one-time challenge, verify with the registered public key, then run assignment checks.
- Updated protocol docs to require public SSH keys when projects want login-style verification of the current local operator.
- Updated README, state model, templates, state files, and validation evidence for the new local login gate.

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
- Defined state-directory resolution rules for `.claw/`.
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
