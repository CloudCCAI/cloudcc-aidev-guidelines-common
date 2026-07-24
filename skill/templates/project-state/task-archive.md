---
kind: task-archive
schema_version: 5
updated_at: {{TIMESTAMP}}
updated_by: "{{UPDATED_BY}}"
archive_status: active
---

# 任务归档

`task-archive.md` 在第一个真实任务从看板归档时创建。

## 已归档任务

### {{TASK_ID}} - {{TITLE}}

- status: `{{FINAL_STATUS}}`
- owner_role: `{{OWNER_ROLE}}`
- related_issues: `{{RELATED_ISSUES}}`
- scope_files: `{{SCOPE_FILES}}`
- task_status_path: `{{TASK_STATUS_PATH}}`
- archived_at: `{{TIMESTAMP}}`
- completion_context: {{COMPLETION_CONTEXT}}

## 维护规则

- 只归档 `done` 或 `canceled` 任务。
- `task-board.md` 已完成区只保留最新 5 张卡片，第 6 张及更旧卡片由 `archive-completed-tasks.py` 移入本文件。
- 归档是从 task board 移动索引卡，不删除任务事实文件。
