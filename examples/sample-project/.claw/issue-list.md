---
kind: issue-list
version: 3
updated_at: 2026-04-01T09:25:00Z
updated_by: ai
---

# 问题追踪列表

## 活跃问题

### ISSUE-002 - 登录失败路径集成测试不稳定

- severity: `high`
- status: `in_progress`
- owner: `ai`
- created_at: `2026-03-31`
- related_files: [`src/api/login.test.ts`, `src/lib/rate-limit.ts`]
- related_tasks: [`TASK-001`]

#### Summary

登录失败路径在 CI 中偶发返回 429，导致测试结果不稳定。

#### Evidence

- CI 集成测试偶发失败
- 失败时响应码为 429，而预期为 401

#### Reproduction

1. 执行 `npm run test:integration`
2. 连续运行 3 次
3. 第 2 或第 3 次偶发失败

#### Root Cause

- status: `inferred`
- detail: 测试环境下限流计数器未在用例间重置

#### Next Action

- 在测试环境中 mock 或重置限流存储

#### Timeline

- 2026-03-31: CI 发现偶发失败
- 2026-04-01: 定位到限流逻辑相关

## 已解决问题

### ISSUE-001 - 登录成功响应缺少统一错误码字段

- severity: `medium`
- status: `closed`
- resolved_at: `2026-03-30`

#### Summary

登录接口成功响应结构和通用 API 规范不一致。

#### Fix

- 统一返回结构为 `{ code, message, data }`

#### Lessons

- API 协议应在功能开发早期统一
- 集成测试要覆盖响应结构而不是只校验状态码
