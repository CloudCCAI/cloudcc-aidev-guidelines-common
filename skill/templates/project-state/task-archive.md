---
kind: task-archive
schema_version: 5
updated_at: {{TIMESTAMP}}
updated_by: "{{UPDATED_BY}}"
archive_status: active
---

# Task Archive

Create `task-archive.md` when the first real task leaves the board for the archive.

## Archived Tasks

### {{TASK_ID}} - {{TITLE}}

- status: `{{FINAL_STATUS}}`
- owner_role: `{{OWNER_ROLE}}`
- related_issues: `{{RELATED_ISSUES}}`
- scope_files: `{{SCOPE_FILES}}`
- task_status_path: `{{TASK_STATUS_PATH}}`
- archived_at: `{{TIMESTAMP}}`
- completion_context: {{COMPLETION_CONTEXT}}

## Maintenance Rules

- Archive only `done` or `canceled` tasks.
- Archiving moves the index card from the task board and does not delete the task fact file.
