---
kind: integration-queue
schema_version: 5
updated_at: {{TIMESTAMP}}
updated_by: "{{UPDATED_BY}}"
queue_id: {{QUEUE_ID}}
status: collecting
integration_owner: {{INTEGRATION_OWNER}}
---

# 集成队列

`integration-queue.md` 在多个真实分支或并行任务需要协调合并时创建。

## 活跃集成队列

### {{QUEUE_ID}} - {{TITLE}}

- status: `collecting`
- feature_id: `{{FEATURE_ID}}`
- integration_branch: `{{INTEGRATION_BRANCH}}`
- integration_owner: `{{INTEGRATION_OWNER}}`
- related_tasks: `{{RELATED_TASKS}}`
- related_prs: `{{RELATED_PRS}}`
- merge_order: `{{MERGE_ORDER}}`
- validation_gates: `{{VALIDATION_GATES}}`
- blocked_by: `none`

### 回滚说明

- {{ROLLBACK_NOTES}}

## 已完成集成队列

- 暂无。
