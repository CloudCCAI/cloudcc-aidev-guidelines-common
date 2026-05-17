---
kind: current-status
version: 3
updated_at: 2026-05-17T14:23:46Z
updated_by: codex
phase: review
active_task: "TASK-006 - Harden local identity login as mandatory pre-edit gate"
next_action: "Run final validation, sync installed skill, and commit 3.7.1 hard identity gate"
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

- 会话目标：把 3.7.0 的本地身份验证能力升级为 3.7.1 硬阻断编辑前门禁
- 当前关注点：`TASK-006` 已实现，进入 review，待最终验证和提交
- 活跃任务：见 `TASK-006`
- 阻塞状态：无

## 本次会话进展

### 已完成

- 仓库协议版本从 `3.7.0` 升级到 `3.7.1`
- 明确只要项目存在 `.claw/developers/`、`.claw/assignments/`、`assignment_path` 或 `local_login_required: true`，硬身份门禁就自动启用
- 将本地 `scripts/dev-login.py` 从推荐流程升级为修改源码、测试、配置、迁移、生成资产、feature spec 或任务状态前的强制门禁
- 明确聊天声明、历史记忆、Git author/email、缓存路径和 `scripts/check-assignment.py` 都不能绕过本地 SSH challenge-response 登录
- 明确缺少私钥路径、任务 ID、分支、文件范围或 assignment 时，agent 必须停止并要求补齐，不能先修改再补验证
- 更新 `SKILL.md`、`README.md`、`STATE-MODEL.md`、`CHANGELOG.md`、模板和 wiki 使用说明
- 新增 `docs/specs/FEAT-006-hard-identity-gate.md`
- 新增 `ADR-006`，记录采用硬身份门禁的决策
- 更新 `task-board.md`

### 进行中

- 最终验证、安装路径同步和 commit

### 下一步

- 运行最终状态校验和语法检查
- 同步本机安装路径 `/Users/owenmacbook/.agents/skills/cloudcc-aidev-guidelines-common`
- 提交 3.7.1 版本

## 修改文件

- `SKILL.md` - 主协议升级到 `3.7.1`，新增硬身份门禁规则
- `README.md` - 增加硬身份门禁说明
- `STATE-MODEL.md` - 增加 Hard Identity Gate 状态模型
- `CHANGELOG.md` - 增加 `3.7.1` 记录
- `templates/task-board.md` - 同步硬门禁维护规则
- `templates/parallel/assignment.yaml` - 增加 hard gate notes
- `templates/docs/feature-spec-template.md` - 标明 `dev-login.py hard gate`
- `docs/specs/_feature-spec-template.md` - 同步 feature spec 模板
- `docs/specs/FEAT-005-local-identity-login.md` - 增加 3.7.1 硬阻断补充
- `docs/specs/FEAT-006-hard-identity-gate.md` - 新增本次功能设计
- `.claw/decisions.md` - 新增 `ADR-006`
- `.claw/task-board.md` - 新增 `TASK-006`
- `/Volumes/AISpace/AI/KB/wiki/cc-aidev-guidelines-common-usage-guide.md` - 更新使用说明为 3.7.1 硬门禁

## 已验证事实

- Build: `not_run`
- Tests: `python3 scripts/validate-state.py .claw` passed
- Syntax: `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/validate-state.py scripts/summarize-team-status.py scripts/check-assignment.py scripts/dev-login.py` passed
- Soft gate wording check: `rg` found no remaining `should run` / `推荐先运行` / `dev-login.py should` style local-login guidance in protocol docs
- Hard gate wording check: `rg` confirmed `3.7.1`, hard identity gate, `dev-login.py must`, `必须先运行`, and no-bypass wording in protocol docs and wiki guide
- 依赖变更: `none`

## 待确认

- 是否需要后续接入 agent runtime 的编辑前 hook 或 IDE/CI 强制策略

## 相关状态文件

- `decisions.md` - `ADR-006` 记录硬身份门禁决策
- `task-board.md` - `TASK-006` 任务状态、范围和交接说明
- `test-report.md` - 本次真实验证命令待更新

## 相关设计文档

- `docs/specs/FEAT-006-hard-identity-gate.md` - 本次硬身份门禁协议设计
- `docs/specs/FEAT-005-local-identity-login.md` - 本地登录式身份验证协议设计
- `docs/specs/FEAT-004-project-manager-gated-authorization.md` - 项目经理门控授权协议设计

## 维护规则

- 保持简短，只记录当前快照。
- 当前会话的活跃任务 ID 应与 `task-board.md` 保持一致。
- 不复制完整 issue、ADR 或测试详情。
- 不在这里写长篇功能设计，功能设计写到 `docs/specs/`。
- 不在这里写多开发者的个人进度流水；个人任务进度写入 `.claw/tasks/TASK-xxx.md`。
- 如需历史归档，放到独立历史文件，不放在这里。
