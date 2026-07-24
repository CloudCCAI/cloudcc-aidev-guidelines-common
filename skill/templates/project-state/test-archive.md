---
kind: test-archive
schema_version: 5
version: 5
updated_at: {{TIMESTAMP}}
updated_by: "{{UPDATED_BY}}"
archive_status: active
---

# 测试报告归档

`test-archive.md` 保存从 `test-report.md` 移出的完整历史验证证据，仅在追溯时读取。

## 归档批次 {{TIMESTAMP}}

{{ARCHIVED_TEST_RECORDS}}

## 维护规则

- 保留原始命令、状态和证据，不得把未执行的验证改写为通过。
- 当前未解决状态的紧凑索引保留在 `test-report.md`。
