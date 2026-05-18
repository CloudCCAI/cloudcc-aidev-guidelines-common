---
kind: task-board
version: 3
updated_at: YYYY-MM-DDTHH:MM:SSZ
updated_by: ai
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

### TASK-001 - Establish the first delivery slice

- status: `ready`
- priority: `high`
- owner_role: `shared`
- claimed_by: ``
- spec_path: ``
- depends_on: `none`
- blocked_by: `none`
- related_issues: `none`
- scope_mode: `exact_files`
- allowed_write_roots: `none`
- scope_files: `.claw/current-status.md, .claw/goals.md, .claw/task-board.md`
- protected_paths: `.claw/assignments/**, .claw/developers/**, scripts/dev-login.py, scripts/check-assignment.py`
- branch: `n/a`
- pr_url: `n/a`
- assignment_path: `none`
- task_status_path: `none`
- parallel_group: `none`
- touch_policy: `exclusive`
- shared_contracts: `none`
- merge_policy: `direct`
- integration_queue: `none`
- integration_owner: `unassigned`
- authorization_check: `scripts/check-assignment.py`

#### Done When

- 项目目标已经补齐
- 第一个活跃任务已经拆出
- 非平凡功能已建立 feature spec

#### Next Action

- 根据当前优先级创建真正的 `TASK-001`

#### Handoff Note

- 如果这是首轮初始化，下一位接手者应先补齐 `goals.md`，再决定是否新建 feature spec

## Completed Tasks

- 暂无已完成任务。

## 维护规则

- 这里只记录可执行任务，不记录完整 bug 细节或长篇设计。
- `owner_role` 是稳定责任角色，不依赖智能体自我身份。
- `claimed_by` 是可选运行时标签，环境知道就写，不知道可留空。
- 异步多开发者协作时，填写 `assignment_path`、`task_status_path`、`branch`、`scope_mode`、`allowed_write_roots`、`scope_files`、`protected_paths` 和 `touch_policy`。
- 普通功能开发推荐 `scope_mode: task_bounded_broad_code`，用 `allowed_write_roots` 放开源码和测试路径，用 `protected_paths` 保护治理、CI、迁移、密钥和门禁脚本。
- 精确文档、任务状态和受保护路径仍放入 `scope_files`；`scope_mode: exact_files` 只用于已知全部写入路径的窄任务。
- 项目经理门控授权或存在身份/授权记录时，开发前必须先运行 `scripts/dev-login.py`；`scripts/check-assignment.py` 只用于 CI 或 assignment-only 检查，不能替代本地 SSH challenge-response 登录。
- 非平凡功能任务应填写 `spec_path` 并指向 `docs/specs/` 下真实文件。
- Brownfield 接入任务可先指向 `docs/specs/PROJECT-BASELINE.md`，后续再拆成具体 feature spec。
- `Completed Tasks` 最多保留最近 20 条任务卡，超过后将最旧的 `done` 或 `canceled` 任务移动到 `task-archive.md`。
- 任务状态、依赖和交接说明变化时立即更新。
