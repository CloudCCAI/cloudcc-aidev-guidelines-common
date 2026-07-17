---
kind: test-report
version: 3
updated_at: 2026-04-01T09:20:00Z
updated_by: ai
last_run_at: 2026-04-01T09:18:00Z
last_run_status: partial
---

# 测试报告

## 最新运行摘要

- 状态：`partial`
- 范围：integration
- 命令：`npm run test:integration`
- 环境：ci

## 结果汇总

| 类型 | 总数 | 通过 | 失败 | 跳过 | 覆盖率 |
|------|------|------|------|------|--------|
| 单元测试 | 48 | 48 | 0 | 0 | 86% |
| 集成测试 | 14 | 13 | 1 | 0 | 74% |
| E2E 测试 | 0 | 0 | 0 | 0 | - |
| 总计 | 62 | 61 | 1 | 0 | 82% |

## 失败项

### 登录失败路径偶发返回 429

- file: `src/api/login.test.ts`
- case: `should return 401 when password is invalid`
- severity: `high`

#### Error

```text
Expected status: 401
Received status: 429
```

#### Notes

- 与限流逻辑共享状态有关
- 关联 `ISSUE-002`

## 覆盖率趋势

| 日期 | 行覆盖率 | 分支覆盖率 | 函数覆盖率 |
|------|----------|------------|------------|
| 2026-03-25 | 78% | 69% | 81% |
| 2026-03-30 | 81% | 73% | 85% |
| 2026-04-01 | 82% | 74% | 86% |

## 常用测试命令

```bash
npm test
npm run test:unit
npm run test:integration
npm run test:coverage
```
