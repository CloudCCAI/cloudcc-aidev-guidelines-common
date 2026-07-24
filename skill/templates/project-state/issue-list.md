---
kind: issue-list
schema_version: 5
updated_at: {{TIMESTAMP}}
updated_by: "{{UPDATED_BY}}"
---

# 问题追踪列表

`issue-list.md` 在第一个真实 bug、风险或阻塞出现时创建，只保留未闭环问题和最近 5 条关闭索引。

## 活跃问题

### {{ISSUE_ID}} - {{TITLE}}

- severity: `{{SEVERITY}}`
- status: `open`
- owner: `{{OWNER}}`
- evidence: {{EVIDENCE}}
- root_cause_status: `unknown`
- related_tasks: `{{RELATED_TASKS}}`
- next_action: {{NEXT_ACTION}}

## 最近关闭问题

- 暂无。

## 维护规则

- 现象、影响、根因状态和阻塞信息以本文件为准。
- 只有 `verified` 或 `closed` 问题可以移入 `issue-archive.md`。
- `fixed` 仍表示待验证，必须保留在活跃问题中。
- 问题进入终态后运行 `archive-resolved-issues.py .claw --write`。
- 修复设计、变更范围、验收标准和回归策略写入关联 FEAT。
