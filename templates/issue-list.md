---
kind: issue-list
version: 2
updated_at: YYYY-MM-DDTHH:MM:SSZ
updated_by: ai
---

# 问题追踪列表

`issue-list.md` 是 bug、阻塞、风险和待跟进事项的唯一事实源。

推荐严重级别：`critical` / `high` / `medium` / `low`  
推荐状态值：`open` / `in_progress` / `blocked` / `fixed` / `verified` / `closed`

## 活跃问题

### ISSUE-001 - [问题标题]

- severity: `high`
- status: `open`
- owner: `ai`
- created_at: `YYYY-MM-DD`
- related_files: [`path/to/file`]

#### Summary

[一句话描述问题]

#### Evidence

- [错误信息、复现现象、日志、截图说明]

#### Reproduction

1. [步骤 1]
2. [步骤 2]
3. [步骤 3]

#### Root Cause

- status: `verified` / `inferred` / `unknown`
- detail: [根因说明]

#### Next Action

- [下一步动作]

#### Timeline

- YYYY-MM-DD: [事件]
- YYYY-MM-DD: [事件]

## 已解决问题

### ISSUE-000 - [问题标题]

- severity: `medium`
- status: `closed`
- resolved_at: `YYYY-MM-DD`

#### Summary

[问题摘要]

#### Fix

- [修复措施]

#### Lessons

- [经验 1]
- [经验 2]

## 维护规则

- 发现新问题、风险或阻塞时新增条目。
- 只把真实存在的问题写进这里，不写猜测性的“也许有问题”。
- 根因必须区分 `verified` 和 `inferred`。
- `current-status.md` 只引用 issue ID，不重复完整内容。
