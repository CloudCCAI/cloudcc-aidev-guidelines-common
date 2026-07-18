---
kind: current-status
schema_version: 5
version: 5
init_status: not_started
init_completed_at: none
init_confirmed_by: none
updated_at: {{TIMESTAMP}}
updated_by: onboarding
phase: onboarding
active_task: "none"
active_task_count: 0
active_tasks: []
next_action: "完成引导式项目初始化"
read_next:
  goals: true
  decisions: true
  directory_map: true
  devops: true
  task_board: true
---

# 项目当前状态

`current-status.md` 是紧凑热索引，不保存任务进度或设计详情。

## 快照

- 项目模式：`{{PROJECT_MODE}}`
- 阶段：`onboarding`
- 活跃工作流：`0`
- 下一步：完成第一个尚未初始化的核心文件

## 活跃工作流

尚未创建活跃工作流。

## 按需读取

- 只读取 `project-onboarding.py resume` 返回的第一个未完成核心文件。
- 初始化完成后，仅在活跃工作流引用时加载任务和功能详情。

## 维护规则

- 本文件保持在 60 行以内。
- 初始化时不得创建占位任务。
- 根据权威任务和看板状态重新生成本索引。
