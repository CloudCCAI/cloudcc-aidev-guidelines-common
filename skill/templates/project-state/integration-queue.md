---
kind: integration-queue
schema_version: 5
updated_at: {{TIMESTAMP}}
updated_by: "{{UPDATED_BY}}"
queue_id: {{QUEUE_ID}}
status: collecting
integration_owner: {{INTEGRATION_OWNER}}
---

# Integration Queue

Create `integration-queue.md` when real branches or parallel tasks require coordinated integration.

## Active Integration Queues

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

#### Rollback Notes

- {{ROLLBACK_NOTES}}

## Completed Integration Queues

- None.
