---
kind: test-report
schema_version: 5
version: 5
updated_at: {{TIMESTAMP}}
updated_by: "{{UPDATED_BY}}"
last_run_at: {{TIMESTAMP}}
last_run_status: {{TEST_STATUS}}
---

# 测试报告

`test-report.md` 仅在真实命令、CI job 或等价验证运行后创建。

## 最新运行摘要

- 状态：`{{TEST_STATUS}}`
- 范围：{{TEST_SCOPE}}
- 命令：`{{TEST_COMMAND}}`
- 环境：{{TEST_ENVIRONMENT}}
- 证据：{{TEST_EVIDENCE}}

## 待处理验证项

- {{PENDING_VERIFICATION}}

## 最近测试记录

### {{TIMESTAMP}} - {{TEST_SCOPE}}

- 状态：`{{TEST_STATUS}}`
- 命令：`{{TEST_COMMAND}}`
- 环境：{{TEST_ENVIRONMENT}}
- 证据：{{TEST_EVIDENCE}}

## 维护规则

- 最近测试记录按从新到旧排列，最多保留 5 条。
- 新增第 6 条后运行 `archive-test-reports.py .claw --write`。
- 归档时保留 `FAILED`、`BLOCKED`、`PENDING` 和 `NOT_RUN` 的紧凑索引。
- 不得把未执行的验证写成通过。
- current status 只引用最新摘要，不复制完整证据。
