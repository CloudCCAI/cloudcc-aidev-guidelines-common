---
kind: task-status
schema_version: 5
task_id: {{TASK_ID}}
task_type: {{TASK_TYPE}}
feature_id: {{FEATURE_ID}}
policy_version: 3
created_at: {{TIMESTAMP}}
created_by: "{{CREATED_BY}}"
created_by_slug: {{CREATED_BY_SLUG}}
created_by_source: {{CREATED_BY_SOURCE}}
created_by_developer_id: {{CREATED_BY_DEVELOPER_ID}}
assignee: {{ASSIGNEE}}
owner_slug: {{OWNER_SLUG}}
owner_role: {{OWNER_ROLE}}
status: ready
stage: planning
branch: n/a
assignment_path: none
change_request_url: n/a
pr_url: n/a
next_action: "{{NEXT_ACTION}}"
updated_at: {{TIMESTAMP}}
updated_by: "{{CREATED_BY}}"
---

# {{TASK_ID}} - {{TITLE}}

## 当前状态

- 状态：`ready`
- 下一步：{{NEXT_ACTION}}
- 阻塞：none
- 功能：`{{FEATURE_ID}}`
- 授权：none

## 进度

- 尚未记录持久化进度。

## 变更文件

- None.

## 验证

- 状态：`not_run`
- 证据：none

## 交接

- 从上述下一步继续。
