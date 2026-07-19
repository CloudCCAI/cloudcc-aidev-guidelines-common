---
kind: test-report
schema_version: 5
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

## 结果汇总

- 通过：{{PASSED_COUNT}}
- 失败：{{FAILED_COUNT}}
- 跳过：{{SKIPPED_COUNT}}

## 失败项

- {{FAILURE_SUMMARY}}

## 维护规则

- 不得把未执行的验证写成通过。
- current status 只引用最新摘要，不复制完整证据。
