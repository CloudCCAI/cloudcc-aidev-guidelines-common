---
kind: current-status
version: 3
updated_at: 2026-05-18T00:00:00Z
updated_by: codex
phase: review
active_task: "TASK-007 - Add task-bounded broad code authorization"
next_action: "Run final validation, sync installed skill, and commit 3.8.0 task-bounded broad code authorization"
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

- 会话目标：把 3.7.1 的硬身份门禁升级为 3.8.0 任务边界宽代码权限模型
- 当前关注点：`TASK-007` 已实现，进入 review，待最终验证和提交
- 活跃任务：见 `TASK-007`
- 阻塞状态：无

## 本次会话进展

### 已完成

- 仓库协议版本从 `3.7.1` 升级到 `3.8.0`
- 新增 `scope_mode: task_bounded_broad_code`，把普通功能开发授权从精确代码文件清单调整为任务边界 + 宽源码/测试写入根路径
- 保留 `scope_mode: exact_files` 作为旧项目和窄任务的兼容默认行为
- 新增 `allowed_write_roots`、`protected_paths`、`task_boundary` 和 `change_manifest_required` 模型
- 更新 `scripts/check-assignment.py`，在宽代码模式下允许普通源码/测试根路径，同时阻止未精确授权的受保护路径
- 更新 `scripts/validate-state.py`、`SKILL.md`、`README.md`、`STATE-MODEL.md`、`CHANGELOG.md` 和模板
- 新增 `docs/specs/FEAT-007-task-bounded-broad-code-authorization.md`
- 新增 `ADR-007`，记录采用任务边界宽代码权限的决策

### 进行中

- 最终验证、安装路径同步和 commit

### 下一步

- 已运行最终状态校验、语法检查和 scope mode 授权用例
- 已同步本机安装路径 `/Users/owenmacbook/.agents/skills/cloudcc-aidev-guidelines-common`
- 提交 3.8.0 版本

## 修改文件

- `SKILL.md` - 主协议升级到 `3.8.0`，新增任务边界宽代码权限规则
- `README.md` - 增加 `scope_mode`、宽代码根路径、受保护路径和 change manifest 说明
- `STATE-MODEL.md` - 增加 Task-Bounded Broad Code Authorization 状态模型
- `CHANGELOG.md` - 增加 `3.8.0` 记录
- `scripts/check-assignment.py` - 新增 `scope_mode`、`allowed_write_roots` 和 `protected_paths` 检查
- `scripts/validate-state.py` - 新增 assignment scope mode 校验
- `templates/task-board.md` - 同步 scope mode 维护规则
- `templates/parallel/assignment.yaml` - 改为宽代码授权示例
- `templates/parallel/task-status.md` - 增加变更清单提示
- `templates/docs/feature-spec-template.md` - 同步并行授权计划字段
- `docs/specs/_feature-spec-template.md` - 同步 feature spec 模板
- `docs/specs/FEAT-007-task-bounded-broad-code-authorization.md` - 新增本次功能设计
- `.claw/decisions.md` - 新增 `ADR-007`
- `.claw/task-board.md` - 新增 `TASK-007`

## 已验证事实

- Build: `not_run`
- Tests: `python3 scripts/validate-state.py .claw` passed
- Syntax: `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/validate-state.py scripts/summarize-team-status.py scripts/check-assignment.py scripts/dev-login.py` passed
- Scope mode checks: broad code write allowed, protected path blocked, exact_files compatibility blocked out-of-scope path
- Protocol wording check: `rg` confirmed `3.8.0`, `task_bounded_broad_code`, `allowed_write_roots`, `protected_paths`, and `change_manifest_required`
- Installed skill sync: `rsync` to `/Users/owenmacbook/.agents/skills/cloudcc-aidev-guidelines-common` completed and installed `SKILL.md` reports `skill_version: 3.8.0`
- 依赖变更: `none`

## 待确认

- 是否需要后续在 PR 模板或 CI 中强制检查 change manifest 覆盖所有 changed files

## 相关状态文件

- `decisions.md` - `ADR-007` 记录任务边界宽代码权限决策
- `task-board.md` - `TASK-007` 任务状态、范围和交接说明
- `test-report.md` - 本次真实验证命令待更新

## 相关设计文档

- `docs/specs/FEAT-007-task-bounded-broad-code-authorization.md` - 本次任务边界宽代码权限协议设计
- `docs/specs/FEAT-006-hard-identity-gate.md` - 硬身份门禁协议设计
- `docs/specs/FEAT-005-local-identity-login.md` - 本地登录式身份验证协议设计
- `docs/specs/FEAT-004-project-manager-gated-authorization.md` - 项目经理门控授权协议设计

## 维护规则

- 保持简短，只记录当前快照。
- 当前会话的活跃任务 ID 应与 `task-board.md` 保持一致。
- 不复制完整 issue、ADR 或测试详情。
- 不在这里写长篇功能设计，功能设计写到 `docs/specs/`。
- 不在这里写多开发者的个人进度流水；个人任务进度写入 `.claw/tasks/TASK-xxx.md`。
- 如需历史归档，放到独立历史文件，不放在这里。
