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
- scope_files: `.claw/current-status.md, .claw/goals.md, .claw/task-board.md`

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
- 非平凡功能任务应填写 `spec_path` 并指向 `docs/specs/` 下真实文件。
- Brownfield 接入任务可先指向 `docs/specs/PROJECT-BASELINE.md`，后续再拆成具体 feature spec。
- 任务状态、依赖和交接说明变化时立即更新。
