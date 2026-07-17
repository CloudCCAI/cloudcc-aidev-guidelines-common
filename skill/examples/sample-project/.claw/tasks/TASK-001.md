---
kind: task-status
task_id: TASK-001
assignee: unassigned
owner_role: backend-agent
status: in_progress
branch: n/a
change_request_url: n/a
pr_url: n/a
updated_at: 2026-04-01T09:30:00Z
updated_by: ai
---

# TASK-001 - 稳定登录失败路径并补齐测试

## Current State

- Status: `in_progress`
- Next action: mock or reset rate-limit storage, then rerun integration tests
- Blocked: `ISSUE-002`
- Spec: `docs/specs/FEAT-001-login-reliability.md`
- Assignment: none

## Progress

- 登录成功路径已接入统一响应封装。
- 用户不存在场景已补充错误码。
- 登录失败路径的限流状态隔离仍在处理。

## Changed Files

- `src/api/login.ts`
- `src/api/login.test.ts`
- `src/lib/rate-limit.ts`
- `docs/specs/FEAT-001-login-reliability.md`

## Verification

- Status: `partial`
- Evidence: `npm run test:integration` passed 13 of 14 tests; see `.claw/test-report.md`

## Handoff

- 接手时先确认限流状态是否在测试间共享。
- 修复后重跑集成测试，再将任务推进到 `review`。
