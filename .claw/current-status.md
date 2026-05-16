---
kind: current-status
version: 3
updated_at: 2026-05-16T02:21:56Z
updated_by: codex
phase: review
active_task: "Review project-manager-gated team authorization protocol and installed 3.6.0 skill"
next_action: "User review FEAT-004, identity binding policy, GitHub Actions example, and local installed skill sync"
read_next:
  goals: false
  decisions: true
  issue_list: false
  task_board: true
  test_report: true
  devops: false
---

# 项目当前状态

`current-status.md` 是唯一的热状态入口。每次会话先读它，再按需读取其他状态文件。

## 快照

- 会话目标：把“项目经理唯一授权入口 + Git 平台账号绑定 + SSH commit signing + 开发前范围校验”纳入多人协作协议
- 当前关注点：`TASK-004` 已进入 review，等待用户确认协议、模板、preflight 脚本和 CI 示例是否符合预期
- 活跃任务：见 `TASK-004`
- 阻塞状态：无

## 本次会话进展

### 已完成

- 新增 `FEAT-004`，定义项目经理门控团队授权模型
- 仓库协议版本从 `3.5.0` 升级到 `3.6.0`
- 明确默认推荐 Git 平台账号绑定 + SSH commit signing，不依赖 Git author name/email 作为强身份依据
- 在 `SKILL.md`、`README.md`、`STATE-MODEL.md` 中加入项目经理唯一授权、preflight 检查和阻断规则
- 更新开发者和 assignment 模板，增加 Git username、SSH signing fingerprint、`managed_by`、`allowed_scopes`、assignment `status` 和 preflight policy
- 新增 `scripts/check-assignment.py`，支持本地/CI 校验开发者身份、任务授权、分支和文件范围
- 扩展 `scripts/validate-state.py`，校验 3.6 授权字段、项目经理授权和 assignment 状态
- 新增 `ADR-004`，记录采用项目经理门控授权与 SSH signing 默认方案
- 更新 `scripts/init-state.sh`，在初始化后提示运行 preflight 授权检查
- 新增 `templates/github-workflows/check-assignment.yml`，提供 GitHub Actions PR gate 示例
- 明确默认一个 Git 平台账号只绑定一个 active 身份；同账号多身份必须使用不同 SSH signing key fingerprint 并记录 `role_sharing_exception`
- 扩展 `scripts/check-assignment.py` 和 `scripts/validate-state.py`，阻断同账号同 key 同时代表项目经理和开发者
- 更新 `team-status.md` 派生视图
- 已将仓库 `3.6.0` 同步到本机安装路径 `/Users/owenmacbook/.agents/skills/cloudcc-aidev-guidelines-common`
- 发现仓库存在未跟踪 `.DS_Store`，发布前应清理或补 `.gitignore`

### 进行中

- 用户 review 本次 3.6.0 协议升级、CI 示例和本地安装同步结果

### 下一步

- 根据用户反馈决定是否新增完整 `examples/async-parallel-project/`
- 如需接入真实远端贡献证据，可后续扩展脚本读取 GitHub/GitLab PR、commit signer 和 CI 状态
- 如果要强化身份验证，优先做 CI 门禁或外部验签工具，而不是把 token 写入仓库

## 修改文件

- `SKILL.md` - 主协议升级到 `3.6.0`
- `README.md` - 增加项目经理门控授权和 preflight 说明
- `STATE-MODEL.md` - 增加 manager-gated authorization 和 check-assignment 语义
- `CHANGELOG.md` - 增加 `3.6.0` 记录
- `scripts/init-state.sh` - 初始化后提示运行授权检查
- `scripts/validate-state.py` - 校验可选并行协作文件、团队状态文件和 3.6 授权字段
- `scripts/check-assignment.py` - 新增开发前/CI 授权检查脚本
- `templates/github-workflows/check-assignment.yml` - 新增 GitHub Actions PR gate 示例
- `templates/task-board.md` - 增加授权检查字段提示
- `templates/docs/feature-spec-template.md` - 增加项目经理门控授权字段
- `templates/parallel/developer.yaml` - 增加 Git 平台账号、SSH 签名指纹、管理者和长期范围
- `templates/parallel/assignment.yaml` - 增加 assignment 状态、preflight policy 和签名引用说明
- `.claw/goals.md` - 增加门控授权目标和成功标准
- `.claw/decisions.md` - 新增 `ADR-004`
- `.claw/task-board.md` - 新增并更新 `TASK-004`
- `.claw/test-report.md` - 记录真实验证结果
- `.claw/team-status.md` - 重新生成团队状态派生视图
- `docs/specs/_feature-spec-template.md` - 同步 feature spec 模板
- `docs/specs/FEAT-004-project-manager-gated-authorization.md` - 新增本次功能设计

## 已验证事实

- Build: `not_run`
- Tests: `python3 scripts/validate-state.py .claw` passed
- Syntax: `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/validate-state.py scripts/summarize-team-status.py scripts/check-assignment.py` passed
- Auth preflight allowed case: `python3 scripts/check-assignment.py <temp> --developer DEV-alice --task TASK-001 --branch feat/TASK-001-feature-title --git-username alice-dev --ssh-signing-key-fingerprint SHA256:abc123 --files src/example/file.ts tests/example/test.ts` passed
- Auth preflight blocked case: same command with `--files src/other/file.ts` returned non-zero and reported `blocked_scope_violation`
- Duplicate identity blocked case: same Git username and same SSH signing key for `MANAGER-001` and `DEV-alice` returned non-zero and reported `blocked_manager_developer_key_reuse`
- Duplicate identity role-key exception case: same Git username with distinct SSH signing keys and `role_sharing_exception` passed
- Workflow example syntax smoke: `python3` parsed `templates/github-workflows/check-assignment.yml` for required CI trigger, PR context variables, and `scripts/check-assignment.py` invocation
- Team summary: `python3 scripts/summarize-team-status.py .claw --write` passed
- Installed skill sync: `rsync` to `/Users/owenmacbook/.agents/skills/cloudcc-aidev-guidelines-common` completed and installed `SKILL.md` reports `skill_version: 3.6.0`
- 依赖变更: `none`

## 待确认

- 是否需要新增完整的异步并行示例项目
- 是否需要在后续版本接入 GitHub/GitLab PR 和 CI 数据源
- 是否需要新增完整异步并行示例项目

## 相关状态文件

- `goals.md` - 项目目标、范围和成功标准
- `decisions.md` - `ADR-004` 记录项目经理门控授权与 SSH signing 默认方案
- `task-board.md` - `TASK-004` 任务状态、范围和交接说明
- `test-report.md` - 本次真实验证命令
- `team-status.md` - 管理者团队状态派生视图

## 相关设计文档

- `docs/specs/FEAT-004-project-manager-gated-authorization.md` - 本次项目经理门控授权协议设计
- `docs/specs/FEAT-002-identity-parallel-delivery.md` - 身份化异步并行交付协议设计
- `docs/specs/FEAT-003-team-status-aggregation.md` - 团队状态汇总协议设计
- `docs/specs/PROJECT-BASELINE.md` - 仓库基线与接管说明

## 维护规则

- 保持简短，只记录当前快照。
- 当前会话的活跃任务 ID 应与 `task-board.md` 保持一致。
- 不复制完整 issue、ADR 或测试详情。
- 不在这里写长篇功能设计，功能设计写到 `docs/specs/`。
- 不在这里写多开发者的个人进度流水；个人任务进度写入 `.claw/tasks/TASK-xxx.md`。
- 如需历史归档，放到独立历史文件，不放在这里。
