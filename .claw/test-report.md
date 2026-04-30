---
kind: test-report
version: 3
updated_at: 2026-04-30T01:31:01Z
updated_by: codex
last_run_at: 2026-04-30T01:31:01Z
last_run_status: passed
---

# 测试报告

`test-report.md` 只记录真实执行过的测试或验证结果，不记录猜测。

推荐状态值：`passed` / `failed` / `partial` / `not_run`

## 最新运行摘要

- 状态：`passed`
- 范围：`state validation`
- 命令：`python3 scripts/validate-state.py .claw`
- 环境：`local workspace`

## 结果汇总

| 类型 | 总数 | 通过 | 失败 | 跳过 | 覆盖率 |
|------|------|------|------|------|--------|
| 单元测试 | 0 | 0 | 0 | 0 | 0% |
| 集成测试 | 0 | 0 | 0 | 0 | 0% |
| E2E 测试 | 0 | 0 | 0 | 0 | - |
| 总计 | 1 | 1 | 0 | 0 | n/a |

## 失败项

- 暂无失败项。

## 覆盖率趋势

| 日期 | 行覆盖率 | 分支覆盖率 | 函数覆盖率 |
|------|----------|------------|------------|
| 2026-04-30 | n/a | n/a | n/a |

## 常用测试命令

- `python3 scripts/validate-state.py .claw`
- 不要在这里保留通用占位命令或猜测性的命令。

## 维护规则

- 只有在实际运行命令后才更新这里。
- `current-status.md` 只应摘录一行测试摘要。
- 如果没有运行测试，明确写 `not_run`，不要留空也不要虚构结果。
