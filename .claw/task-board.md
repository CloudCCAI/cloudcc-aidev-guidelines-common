---
kind: task-board
version: 3
updated_at: 2026-04-30T01:31:01Z
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

## Completed Tasks

- 暂无已完成任务。

## 维护规则

- 这里只记录可执行任务，不记录完整 bug 细节或长篇设计。
- `owner_role` 是稳定责任角色，不依赖智能体自我身份。
- `claimed_by` 是可选运行时标签，环境知道就写，不知道可留空。
- 非平凡功能任务应填写 `spec_path` 并指向 `docs/specs/` 下真实文件。
- Brownfield 接入任务可先指向 `docs/specs/PROJECT-BASELINE.md`，后续再拆成具体 feature spec。
- `Completed Tasks` 最多保留最近 20 条任务卡，超过后将最旧的 `done` 或 `canceled` 任务移动到 `task-archive.md`。
- 任务状态、依赖和交接说明变化时立即更新。
