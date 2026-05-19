---
kind: current-status
version: 3
updated_at: 2026-05-19T00:00:00Z
updated_by: codex
phase: review
active_task: "TASK-008 - Add Codeup change request submission flow"
next_action: "User review Codeup script options and configure local YUNXIAO_TOKEN when ready"
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

- 会话目标：在拉取 GitHub `3.8.0` 最新基线后，保留本地 Codeup 合并请求提交方案，并升级为 `3.9.0`
- 当前关注点：`TASK-008` 已实现，进入 review，等待用户确认 Codeup OpenAPI 脚本、`YUNXIAO_TOKEN` 本地存储方式和平台模板
- 活跃任务：见 `TASK-008`
- 阻塞状态：无

## 本次会话进展

### 已完成

- 从 GitHub remote 拉取并合并 `github/main`，保留 GitHub `3.8.0` 的硬身份门禁和任务边界宽代码权限模型
- 新增 `FEAT-008`，定义 Codeup 合并请求提交流程
- 仓库协议版本从 `3.8.0` 升级到 `3.9.0`
- 新增 `scripts/store-yunxiao-token.py`，将每个开发者的 `YUNXIAO_TOKEN` 保存到本地忽略目录 `.claw-local/codeup.env`
- 新增 `scripts/create-codeup-change-request.py`，通过 Codeup `CreateChangeRequest` OpenAPI 创建合并请求
- 创建合并请求前会检查 `YUNXIAO_TOKEN`；缺失时停止并输出云效个人访问令牌官方文档链接
- 更新 `.gitignore`，忽略 `.claw-local/`、`.ai-dev-local/` 和本地 env 文件
- 新增 `templates/platforms/codeup/`，把 Codeup 作为默认平台模板
- 保留 `templates/github-workflows/check-assignment.yml` 作为 GitHub 可选平台示例
- 新增 `ADR-008`，记录 Codeup-first 平台决策
- 仓库协议版本从 `3.7.1` 升级到 `3.8.0`
- 新增 `scope_mode: task_bounded_broad_code`，把普通功能开发授权从精确代码文件清单调整为任务边界 + 宽源码/测试写入根路径
- 保留 `scope_mode: exact_files` 作为旧项目和窄任务的兼容默认行为
- 新增 `allowed_write_roots`、`protected_paths`、`task_boundary` 和 `change_manifest_required` 模型
- 更新 `scripts/check-assignment.py`，在宽代码模式下允许普通源码/测试根路径，同时阻止未精确授权的受保护路径
- 更新 `scripts/validate-state.py`、`SKILL.md`、`README.md`、`STATE-MODEL.md`、`CHANGELOG.md` 和模板
- 新增 `docs/specs/FEAT-007-task-bounded-broad-code-authorization.md`
- 新增 `ADR-007`，记录采用任务边界宽代码权限的决策

### 进行中

- 用户 review 本次 GitHub 同步后的 `3.9.0` Codeup 合并请求默认方案

### 下一步

- 根据用户提供的 Codeup `domain`、`repositoryId`、reviewer ids 和 `YUNXIAO_TOKEN` 配置本地 `.claw-local/codeup.env`
- 如需团队级落地，可后续补云效 Flow/Webhook 适配脚本来调用 `scripts/check-assignment.py`
- 如果要强化身份验证，优先做 Codeup 保护分支、Flow 检测和外部验签工具，而不是把 token 写入仓库

## 修改文件

- `SKILL.md` - 主协议升级到 `3.9.0`，在 `3.8.0` 基线上将 Codeup 合并请求作为默认平台流程
- `README.md` - 增加 Codeup 合并请求、`YUNXIAO_TOKEN` 和 GitHub 可选示例说明
- `STATE-MODEL.md` - 增加 Codeup 脚本和平台模板语义
- `CHANGELOG.md` - 增加 `3.9.0` 记录
- `scripts/create-codeup-change-request.py` - 新增 Codeup 合并请求创建脚本
- `scripts/store-yunxiao-token.py` - 新增本地 token 存储脚本
- `scripts/init-state.sh` - 初始化后提示 Codeup 默认流程
- `templates/platforms/codeup/` - 新增 Codeup 默认平台模板
- `templates/parallel/assignment.yaml` - 增加 `change_request_url`
- `templates/parallel/task-status.md` - 增加 `change_request_url`
- `templates/task-board.md` - 增加 `change_request_url`
- `.gitignore` - 忽略本地密钥文件
- `docs/specs/FEAT-008-codeup-change-request-submission.md` - 新增本次功能设计
- `.claw/decisions.md` - 新增 `ADR-008`
- `.claw/task-board.md` - 新增 `TASK-008`
- `.claw/test-report.md` - 记录真实验证结果

## 已验证事实

- Build: `not_run`
- GitHub sync: `git fetch github` and `git merge --allow-unrelated-histories -X theirs github/main` completed; local Codeup changes were restored and re-applied on top of GitHub `3.8.0`
- Codeup token guard: `env -u YUNXIAO_TOKEN python3 scripts/create-codeup-change-request.py --dry-run ...` returned non-zero before any API call and printed the Yunxiao token document link
- Codeup dry-run payload: `YUNXIAO_TOKEN=dummy-token python3 scripts/create-codeup-change-request.py --dry-run ...` printed endpoint and payload without exposing the token
- Local token storage: `python3 scripts/store-yunxiao-token.py --stdin --env-file /private/tmp/cc-aidev-codeup-test.env` wrote a `-rw-------` env file, then the temp file was removed
- Syntax: `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/create-codeup-change-request.py scripts/store-yunxiao-token.py scripts/check-assignment.py scripts/validate-state.py scripts/summarize-team-status.py scripts/dev-login.py` passed
- Tests: `python3 scripts/validate-state.py .claw` passed
- 依赖变更: `none`

## 待确认

- Codeup `domain`、`repositoryId`、reviewer ids 是否需要写入各开发者本地 `.claw-local/codeup.env`
- 是否需要增加云效 Flow/Webhook 适配脚本来自动调用 `scripts/check-assignment.py`

## 相关状态文件

- `decisions.md` - `ADR-008` 记录 Codeup-first 平台决策
- `task-board.md` - `TASK-008` 任务状态、范围和交接说明
- `test-report.md` - 本次真实验证命令

## 相关设计文档

- `docs/specs/FEAT-008-codeup-change-request-submission.md` - 本次 Codeup 合并请求协议设计
- `docs/specs/FEAT-007-task-bounded-broad-code-authorization.md` - 任务边界宽代码权限协议设计
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
