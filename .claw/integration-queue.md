---
kind: integration-queue
version: 3
updated_at: 2026-05-01T11:44:25Z
updated_by: codex
queue_id: QUEUE-001
status: ready
integration_owner: codex
---

# 集成队列

`integration-queue.md` 用于异步多开发者并行开发的最终合并协调。简单单线项目可以保持空白或只保留模板。

推荐状态值：`not_started` / `collecting` / `merging` / `verifying` / `ready` / `blocked` / `completed`

## Active Integration Queues

### QUEUE-001 - Identity-based async parallel delivery protocol

- status: `ready`
- feature_id: `FEAT-002`
- integration_branch: `n/a`
- integration_owner: `codex`
- related_tasks: `TASK-002, TASK-003`
- related_prs: `none`
- merge_order: `TASK-002, TASK-003`
- validation_gates: `python3 scripts/validate-state.py .claw`
- blocked_by: `none`

#### Merge Notes

- 本仓库当前在单工作区直接更新协议文件；外部项目启用并行协作时应使用 integration 分支。
- `TASK-002` 已完成协议实现和本地验证，等待用户 review。
- `TASK-003` 补充团队状态派生汇总协议和标准汇总脚本。

#### Rollback Notes

- 如果状态校验失败，保持 `TASK-002` 为 `in_progress`，先修复协议、模板或校验器不一致之处。

## Completed Integration Queues

- 暂无已完成集成队列。

## 维护规则

- 只有存在多个开发者分支或多个并行任务需要合并时才维护本文件。
- 合并顺序、集成分支和验证门禁以本文件为准。
- 真实测试结果仍记录到 `.claw/test-report.md`。
