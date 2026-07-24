---
kind: task-board
schema_version: 5
version: 5
init_status: not_started
init_completed_at: none
init_confirmed_by: none
updated_at: {{TIMESTAMP}}
updated_by: onboarding
board_status: active
---

# 任务看板

`task-board.md` 是紧凑的协作索引，任务详情属于事件创建的 `.claw/tasks/TASK-*.md`。

## 活跃任务

当前没有活跃任务。

## 已完成任务

当前没有已完成任务。

## 维护规则

- 初始化时不得创建占位任务。
- 每张任务卡必须引用真实任务状态文件。
- 非平凡交付工作必须引用真实 FEAT。
- 不要在本索引保存长篇进度、验证、变更文件和交接记录。
- 已完成区只保留最新 5 张 `done` 或 `canceled` 卡片；任务进入终态后运行 `archive-completed-tasks.py .claw --write`。
