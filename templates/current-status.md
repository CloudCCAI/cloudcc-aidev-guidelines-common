---
kind: current-status
version: 3
updated_at: YYYY-MM-DDTHH:MM:SSZ
updated_by: ai
phase: bootstrap
active_task: "Capture project goals and create the first task card"
next_action: "Fill goals.md, update task-board.md, and create the first feature spec when required"
read_next:
  goals: true
  decisions: false
  issue_list: false
  task_board: true
  test_report: false
  devops: false
---

# 项目当前状态

`current-status.md` 是唯一的热状态入口。每次会话先读它，再按需读取其他状态文件。

## 快照

- 会话目标：建立可持续推进和可交接的项目状态
- 当前关注点：补齐 goals、task board 和首个 feature spec
- 活跃任务：见 `TASK-001`；如果还没有任务卡，先在 `task-board.md` 中创建
- 阻塞状态：无 / 见 `ISSUE-xxx`

## 本次会话进展

### 已完成
- 初始化状态目录和交付文档目录

### 进行中
- 梳理项目目标、任务拆分和首个功能设计

### 下一步
- 补齐 `goals.md`
- 创建或更新 `task-board.md` 中的活跃任务
- 当任务为非平凡功能时，创建 `docs/specs/FEAT-xxx-*.md`

## 修改文件

- `.claw/current-status.md` - 会话快照与下一步
- `.claw/task-board.md` - 任务拆分与交接
- `docs/specs/FEAT-xxx-*.md` - 功能级设计与落地记录

## 已验证事实

- Build: `not_run`
- Tests: `not_run`
- Lint: `not_run`
- 依赖变更: `none`

## 待确认

- 项目目标、范围和优先级是否已经固化
- 当前要推进的第一个非平凡功能是否需要单独 spec

## 相关状态文件

- `goals.md` - 项目目标、范围和成功标准
- `task-board.md` - 任务、依赖、责任角色和交接说明
- `decisions.md` - 技术选型影响当前任务时再细读
- `issue-list.md` - 存在活跃问题时再细读
- `test-report.md` - 本次实际运行测试后再更新
- `devops.md` - 涉及构建、部署或环境时再更新

## 相关设计文档

- `docs/specs/FEAT-xxx-*.md` - 当前任务涉及非平凡功能时填写真实路径

## 异步并行索引

- 集成队列：`.claw/integration-queue.md`（启用异步多开发者协作时维护）
- 团队状态：`.claw/team-status.md`（管理者查看团队状态时由脚本生成）
- 单任务状态：`.claw/tasks/TASK-xxx.md`（开发者只更新自己分配的任务状态）
- 任务授权：`.claw/assignments/TASK-xxx.yaml`（由项目管理者维护）
- 开发者身份：`.claw/developers/DEV-xxx.yaml`（只记录公钥或外部验证身份，不记录私钥或 token）

## 维护规则

- 保持简短，只记录当前快照。
- 当前会话的活跃任务 ID 应与 `task-board.md` 保持一致。
- 不复制完整 issue、ADR 或测试详情。
- 不在这里写长篇功能设计，功能设计写到 `docs/specs/`。
- 不在这里写多开发者的个人进度流水；个人任务进度写入 `.claw/tasks/TASK-xxx.md`。
- 如需历史归档，放到独立历史文件，不放在这里。
