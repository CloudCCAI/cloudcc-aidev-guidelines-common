---
kind: task-board
version: 3
updated_at: 2026-05-19T00:00:00Z
updated_by: codex
board_status: active
---

# 任务看板

`task-board.md` 是执行任务、责任角色、依赖关系和交接说明的唯一事实源。

推荐状态值：`todo` / `ready` / `in_progress` / `blocked` / `review` / `done` / `canceled`  
推荐优先级：`critical` / `high` / `medium` / `low`

推荐 `owner_role`：

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

## Active Tasks

### TASK-001 - Add project-root skill declaration automation

- status: `review`
- priority: `high`
- owner_role: `fullstack-agent`
- claimed_by: `codex`
- spec_path: `docs/specs/FEAT-001-project-skill-declaration.md`
- depends_on: `none`
- blocked_by: `none`
- related_issues: `none`
- scope_files: `SKILL.md, README.md, STATE-MODEL.md, CHANGELOG.md, scripts/init-state.sh, scripts/ensure-agent-guidance.sh, scripts/validate-state.py, AGENTS.md, examples/README.md, examples/sample-project/README.md, examples/sample-project/AGENTS.md, .claw/current-status.md, .claw/goals.md, .claw/task-board.md, .claw/test-report.md, docs/specs/PROJECT-BASELINE.md, docs/specs/FEAT-001-project-skill-declaration.md`

#### Done When

- 技能协议明确要求项目根目录 README/AGENTS 声明块
- 初始化脚本会自动刷新声明块
- 校验器会检查声明块、技能名和 GitHub 安装来源
- 仓库自身和示例项目都体现新的声明要求

#### Next Action

- 复查差异并确认是否还需要补充更多老项目接入说明

#### Handoff Note

- 下一位接手者先看 `docs/specs/FEAT-001-project-skill-declaration.md`，再根据真实外部项目反馈决定是否调整声明块策略

### TASK-002 - Add identity-based asynchronous parallel delivery protocol

- status: `review`
- priority: `high`
- owner_role: `shared`
- claimed_by: `codex`
- spec_path: `docs/specs/FEAT-002-identity-parallel-delivery.md`
- depends_on: `none`
- blocked_by: `none`
- related_issues: `none`
- scope_files: `SKILL.md, README.md, STATE-MODEL.md, CHANGELOG.md, scripts/init-state.sh, scripts/validate-state.py, templates/current-status.md, templates/task-board.md, templates/docs/feature-spec-template.md, templates/integration-queue.md, templates/parallel/developer.yaml, templates/parallel/assignment.yaml, templates/parallel/task-status.md, .claw/current-status.md, .claw/goals.md, .claw/decisions.md, .claw/task-board.md, .claw/test-report.md, .claw/integration-queue.md, docs/specs/_feature-spec-template.md, docs/specs/FEAT-002-identity-parallel-delivery.md`
- branch: `n/a`
- pr_url: `n/a`
- assignment_path: `none`
- task_status_path: `none`
- parallel_group: `protocol-identity-parallel`
- touch_policy: `shared`
- shared_contracts: `docs/specs/FEAT-002-identity-parallel-delivery.md`
- merge_policy: `direct_workspace_update`
- integration_queue: `.claw/integration-queue.md`
- integration_owner: `codex`

#### Done When

- 技能协议明确身份、公钥、任务授权、单任务状态和集成队列模型
- 模板和 README/STATE-MODEL 同步说明异步多开发者协作流程
- 初始化脚本创建并行协作目录和集成队列模板
- 校验器能轻量检查可选身份/授权/任务状态文件
- 当前仓库状态校验通过并记录真实验证结果

#### Next Action

- 用户 review 身份化异步并行交付协议，并决定是否需要补充示例项目

#### Handoff Note

- 本任务已实现协议、模板、初始化脚本、校验器和状态文件更新；后续如需强化安全性，应新增独立签名/验签工具，而不是把 token 或口令写入仓库

### TASK-003 - Add standard team status aggregation

- status: `review`
- priority: `high`
- owner_role: `shared`
- claimed_by: `codex`
- spec_path: `docs/specs/FEAT-003-team-status-aggregation.md`
- depends_on: `TASK-002`
- blocked_by: `none`
- related_issues: `none`
- scope_files: `SKILL.md, README.md, STATE-MODEL.md, CHANGELOG.md, scripts/init-state.sh, scripts/validate-state.py, scripts/summarize-team-status.py, templates/team-status.md, .claw/current-status.md, .claw/task-board.md, .claw/test-report.md, .claw/team-status.md, docs/specs/FEAT-003-team-status-aggregation.md`
- branch: `n/a`
- pr_url: `n/a`
- assignment_path: `none`
- task_status_path: `none`
- parallel_group: `protocol-team-status`
- touch_policy: `shared`
- shared_contracts: `docs/specs/FEAT-003-team-status-aggregation.md`
- merge_policy: `direct_workspace_update`
- integration_queue: `.claw/integration-queue.md`
- integration_owner: `codex`

#### Done When

- 技能协议明确 `team-status.md` 是派生汇总视图
- README 说明管理者如何运行标准汇总方法
- 新增团队状态模板和汇总脚本
- 初始化脚本和校验器支持 `team-status.md`
- 当前仓库状态校验和汇总脚本验证通过

#### Next Action

- 用户 review 团队状态汇总协议和脚本输出格式

#### Handoff Note

- 本任务已实现 `team-status.md` 派生视图、汇总脚本、初始化脚本和校验器支持；远端 PR/CI 平台数据应后续作为可选扩展接入

### TASK-004 - Add project-manager-gated team authorization

- status: `review`
- priority: `high`
- owner_role: `shared`
- claimed_by: `codex`
- spec_path: `docs/specs/FEAT-004-project-manager-gated-authorization.md`
- depends_on: `TASK-002, TASK-003`
- blocked_by: `none`
- related_issues: `none`
- scope_files: `SKILL.md, README.md, STATE-MODEL.md, CHANGELOG.md, scripts/check-assignment.py, scripts/init-state.sh, scripts/validate-state.py, templates/github-workflows/check-assignment.yml, templates/parallel/developer.yaml, templates/parallel/assignment.yaml, templates/docs/feature-spec-template.md, docs/specs/_feature-spec-template.md, .claw/current-status.md, .claw/goals.md, .claw/decisions.md, .claw/task-board.md, .claw/test-report.md, docs/specs/FEAT-004-project-manager-gated-authorization.md`
- branch: `n/a`
- pr_url: `n/a`
- assignment_path: `none`
- task_status_path: `none`
- parallel_group: `protocol-manager-gated-authorization`
- touch_policy: `shared`
- shared_contracts: `docs/specs/FEAT-004-project-manager-gated-authorization.md`
- merge_policy: `direct_workspace_update`
- integration_queue: `.claw/integration-queue.md`
- integration_owner: `codex`
- authorization_check: `scripts/check-assignment.py`

#### Done When

- 技能协议明确项目经理是团队成员和任务授权的唯一授权入口
- 默认推荐 Git 平台账号绑定加 SSH commit signing
- 默认一个 Git 平台账号只绑定一个 active 身份；同账号多身份必须使用不同 SSH signing key 并记录例外
- 模板记录项目经理、Git 平台账号、SSH 签名指纹、长期范围和单任务授权范围
- 新增 preflight 授权检查脚本，能阻止身份不符、分支不符和文件越界
- 新增 GitHub Actions PR gate 示例，展示如何传入 PR author、branch 和 changed files
- 当前仓库状态校验和脚本验证通过

#### Next Action

- 用户 review 项目经理门控授权协议、模板、`scripts/check-assignment.py` 行为和 GitHub Actions 示例

#### Handoff Note

- 本任务已实现协议、模板、preflight 脚本、GitHub Actions 示例和校验器支持；不要保存任何私钥、token、口令或 bearer secret，Git 级可信度由平台账号、SSH 签名、分支保护和 CI 共同实现

### TASK-005 - Add local SSH challenge-response developer login

- status: `review`
- priority: `high`
- owner_role: `shared`
- claimed_by: `codex`
- spec_path: `docs/specs/FEAT-005-local-identity-login.md`
- depends_on: `TASK-004`
- blocked_by: `none`
- related_issues: `none`
- scope_files: `SKILL.md, README.md, STATE-MODEL.md, CHANGELOG.md, scripts/dev-login.py, scripts/init-state.sh, templates/parallel/developer.yaml, templates/parallel/assignment.yaml, templates/docs/feature-spec-template.md, docs/specs/_feature-spec-template.md, .gitignore, .claw/current-status.md, .claw/decisions.md, .claw/task-board.md, .claw/test-report.md, docs/specs/FEAT-005-local-identity-login.md`
- branch: `n/a`
- pr_url: `n/a`
- assignment_path: `none`
- task_status_path: `none`
- parallel_group: `protocol-local-identity-login`
- touch_policy: `shared`
- shared_contracts: `docs/specs/FEAT-005-local-identity-login.md`
- merge_policy: `direct_workspace_update`
- integration_queue: `.claw/integration-queue.md`
- integration_owner: `codex`
- authorization_check: `scripts/dev-login.py, scripts/check-assignment.py`

#### Done When

- 本地开发前可用 `scripts/dev-login.py` 从私钥自动解析并报告 `developer_id`
- 脚本用一次性 challenge 验证当前用户确实持有登记 public key 对应的私钥
- 脚本可把私钥路径缓存到本机忽略文件，并在后续任务前重新验签
- 传入 `--task` 时会串联 assignment、branch 和 `scope_files` 检查
- 文档明确 `.claw-local/identity.json` / `.ai-dev-local/identity.json` 不是事实源，不能提交
- 当前仓库状态校验和脚本验证通过

#### Next Action

- 用户 review 3.7.0 本地登录式身份验证流程和 `scripts/dev-login.py` 行为

#### Handoff Note

- 本任务已实现登录式身份验证协议和脚本；后续如果要增强组织级强制力，优先接入平台 signed commit 验证、系统 Keychain 或企业 SSO，不要把私钥或 token 写入仓库

### TASK-006 - Harden local identity login as mandatory pre-edit gate

- status: `review`
- priority: `critical`
- owner_role: `shared`
- claimed_by: `codex`
- spec_path: `docs/specs/FEAT-006-hard-identity-gate.md`
- depends_on: `TASK-005`
- blocked_by: `none`
- related_issues: `none`
- scope_files: `SKILL.md, README.md, STATE-MODEL.md, CHANGELOG.md, templates/task-board.md, templates/parallel/assignment.yaml, templates/docs/feature-spec-template.md, docs/specs/_feature-spec-template.md, docs/specs/FEAT-005-local-identity-login.md, docs/specs/FEAT-006-hard-identity-gate.md, .claw/current-status.md, .claw/decisions.md, .claw/task-board.md, .claw/test-report.md, /Volumes/AISpace/AI/KB/wiki/cc-aidev-guidelines-common-usage-guide.md`
- branch: `n/a`
- pr_url: `n/a`
- assignment_path: `none`
- task_status_path: `none`
- parallel_group: `protocol-hard-identity-gate`
- touch_policy: `shared`
- shared_contracts: `docs/specs/FEAT-006-hard-identity-gate.md`
- merge_policy: `direct_workspace_update`
- integration_queue: `.claw/integration-queue.md`
- integration_owner: `codex`
- authorization_check: `scripts/dev-login.py hard gate`

#### Done When

- 协议明确身份/授权记录存在时自动启用硬身份门禁
- `scripts/dev-login.py` 返回 `allowed` 前不得修改源码、测试、配置、迁移、生成资产、feature spec 或任务状态
- 聊天声明、历史记忆、Git author/email、缓存路径和 `scripts/check-assignment.py` 都不能绕过本地登录
- 缺少私钥路径、任务、分支、文件范围或 assignment 时 agent 必须停止并要求补齐
- README、STATE-MODEL、模板和使用说明同步硬阻断规则
- 当前仓库状态校验通过

#### Next Action

- 用户 review 3.7.1 硬身份门禁规则

#### Handoff Note

- 本任务把 3.7.0 的身份验证能力升级为 3.7.1 的强制编辑前门禁；协议层已无后门，后续如需技术强制可接入 runtime hook 或 IDE/CI 策略。

### TASK-007 - Add task-bounded broad code authorization

- status: `review`
- priority: `critical`
- owner_role: `shared`
- claimed_by: `codex`
- spec_path: `docs/specs/FEAT-007-task-bounded-broad-code-authorization.md`
- depends_on: `TASK-006`
- blocked_by: `none`
- related_issues: `none`
- scope_mode: `task_bounded_broad_code`
- allowed_write_roots: `SKILL.md, README.md, STATE-MODEL.md, CHANGELOG.md, scripts/**, templates/**, docs/specs/**, .claw/**`
- scope_files: `docs/specs/FEAT-007-task-bounded-broad-code-authorization.md, .claw/current-status.md, .claw/decisions.md, .claw/task-board.md, .claw/test-report.md`
- protected_paths: `scripts/dev-login.py, scripts/check-assignment.py, scripts/validate-state.py`
- branch: `n/a`
- pr_url: `n/a`
- assignment_path: `none`
- task_status_path: `none`
- parallel_group: `protocol-task-bounded-broad-code`
- touch_policy: `shared`
- shared_contracts: `docs/specs/FEAT-007-task-bounded-broad-code-authorization.md`
- merge_policy: `direct_workspace_update`
- integration_queue: `.claw/integration-queue.md`
- integration_owner: `codex`
- authorization_check: `scripts/dev-login.py hard gate, scripts/check-assignment.py scope mode`

#### Done When

- 协议明确普通功能任务的门禁控制任务处理权限，而不是预判所有代码文件
- assignment 支持 `scope_mode: task_bounded_broad_code`、`allowed_write_roots` 和 `protected_paths`
- `scripts/check-assignment.py` 在宽代码模式下允许源码/测试根路径，阻止未精确授权的受保护路径
- 旧的 `scope_mode: exact_files` 行为保持兼容
- README、STATE-MODEL、模板、feature spec 和状态文件同步新授权模型
- 当前仓库状态校验和脚本验证通过

#### Next Action

- 用户 review 3.8.0 任务边界宽代码权限模型

#### Handoff Note

- 本任务把普通功能开发从精确文件授权改为任务边界宽代码授权；如果要进一步增强，应在 PR 模板或 CI 中检查 change manifest，而不是重新收窄所有源码路径。

### TASK-008 - Add Codeup change request submission flow

- status: `review`
- priority: `high`
- owner_role: `shared`
- claimed_by: `codex`
- spec_path: `docs/specs/FEAT-008-codeup-change-request-submission.md`
- depends_on: `TASK-007`
- blocked_by: `none`
- related_issues: `none`
- scope_mode: `task_bounded_broad_code`
- allowed_write_roots: `SKILL.md, README.md, STATE-MODEL.md, CHANGELOG.md, scripts/**, templates/**, docs/specs/**, .claw/**, .gitignore`
- scope_files: `docs/specs/FEAT-008-codeup-change-request-submission.md, .claw/current-status.md, .claw/decisions.md, .claw/task-board.md, .claw/test-report.md`
- protected_paths: `scripts/dev-login.py, scripts/check-assignment.py, scripts/validate-state.py`
- branch: `n/a`
- change_request_url: `n/a`
- pr_url: `n/a`
- assignment_path: `none`
- task_status_path: `none`
- parallel_group: `protocol-codeup-change-request`
- touch_policy: `shared`
- shared_contracts: `docs/specs/FEAT-008-codeup-change-request-submission.md`
- merge_policy: `direct_workspace_update`
- integration_queue: `.claw/integration-queue.md`
- integration_owner: `codex`
- authorization_check: `scripts/dev-login.py hard gate, scripts/check-assignment.py scope mode`

#### Done When

- Codeup is documented as the default review request platform flow
- Each developer can store a local `YUNXIAO_TOKEN` outside Git-tracked files
- Creating a Codeup change request checks for `YUNXIAO_TOKEN` before any OpenAPI call
- Missing token output links to the official Yunxiao personal access token documentation
- GitHub Actions guidance remains as an optional platform example
- Current repository validation and Python syntax checks pass

#### Next Action

- User review the Codeup script options and decide whether to wire repository-specific defaults into local `.claw-local/codeup.env`

#### Handoff Note

- Token material must stay local. Use `.claw-local/codeup.env` or process environment only; do not write tokens into `.claw/`, docs, specs, task status files, or logs.

## Completed Tasks

- 暂无已完成任务。

## 维护规则

- 这里只记录可执行任务，不记录完整 bug 细节或长篇设计。
- `owner_role` 是稳定责任角色，不依赖智能体自我身份。
- `claimed_by` 是可选运行时标签，环境知道就写，不知道可留空。
- 异步多开发者协作时，填写 `assignment_path`、`task_status_path`、`branch`、`scope_mode`、`allowed_write_roots`、`scope_files`、`protected_paths` 和 `touch_policy`。
- 普通功能开发推荐 `scope_mode: task_bounded_broad_code`，用 `allowed_write_roots` 放开源码和测试路径，用 `protected_paths` 保护治理、CI、迁移、密钥和门禁脚本。
- 精确文档、任务状态和受保护路径仍放入 `scope_files`；`scope_mode: exact_files` 只用于已知全部写入路径的窄任务。
- 非平凡功能任务应填写 `spec_path` 并指向 `docs/specs/` 下真实文件。
- Brownfield 接入任务可先指向 `docs/specs/PROJECT-BASELINE.md`，后续再拆成具体 feature spec。
- `Completed Tasks` 最多保留最近 20 条任务卡，超过后将最旧的 `done` 或 `canceled` 任务移动到 `task-archive.md`。
- 任务状态、依赖和交接说明变化时立即更新。
