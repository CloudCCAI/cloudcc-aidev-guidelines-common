---
kind: task-board
version: 3
updated_at: 2026-04-01T09:28:00Z
updated_by: ai
board_status: active
---

# 任务看板

## Active Tasks

### TASK-001 - 稳定登录失败路径并补齐测试

- status: `in_progress`
- priority: `high`
- owner_role: `backend-agent`
- claimed_by: `current-session`
- spec_path: `docs/specs/FEAT-001-login-reliability.md`
- depends_on: `none`
- blocked_by: `ISSUE-002`
- related_issues: `ISSUE-002`
- scope_files: `src/api/login.ts, src/api/login.test.ts, src/lib/rate-limit.ts`

#### Done When

- 登录失败路径不再偶发返回 429
- `npm run test:integration` 稳定通过
- `test-report.md` 更新为最新真实结果

#### Next Action

- 在测试环境中 mock 或重置限流存储，再重跑集成测试

#### Handoff Note

- 接手时先读 `docs/specs/FEAT-001-login-reliability.md` 和 `ISSUE-002`
- 如果集成测试通过，更新 `test-report.md`，再将任务推进到 `review`

## Completed Tasks

- 暂无已完成任务。
