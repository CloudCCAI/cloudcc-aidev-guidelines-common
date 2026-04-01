---
kind: test-report
version: 2
updated_at: YYYY-MM-DDTHH:MM:SSZ
updated_by: ai
last_run_at: YYYY-MM-DDTHH:MM:SSZ
last_run_status: not_run
---

# 测试报告

`test-report.md` 只记录真实执行过的测试或验证结果，不记录猜测。

推荐状态值：`passed` / `failed` / `partial` / `not_run`

## 最新运行摘要

- 状态：`passed`
- 范围：[unit / integration / e2e / smoke / build verification]
- 命令：`[实际执行的命令]`
- 环境：[local / ci / staging]

## 结果汇总

| 类型 | 总数 | 通过 | 失败 | 跳过 | 覆盖率 |
|------|------|------|------|------|--------|
| 单元测试 | 0 | 0 | 0 | 0 | 0% |
| 集成测试 | 0 | 0 | 0 | 0 | 0% |
| E2E 测试 | 0 | 0 | 0 | 0 | - |
| 总计 | 0 | 0 | 0 | 0 | 0% |

## 失败项

### [失败项标题]

- file: `path/to/test-file`
- case: `[测试用例名称]`
- severity: `high`

#### Error

```text
[错误输出]
```

#### Notes

- [关键信息]
- [下一步排查或修复动作]

## 覆盖率趋势

| 日期 | 行覆盖率 | 分支覆盖率 | 函数覆盖率 |
|------|----------|------------|------------|
| YYYY-MM-DD | 0% | 0% | 0% |

## 常用测试命令

```bash
# 运行所有测试
npm test

# 运行单元测试
npm run test:unit

# 运行集成测试
npm run test:integration

# 生成覆盖率报告
npm run test:coverage
```

## 维护规则

- 只有在实际运行命令后才更新这里。
- `current-status.md` 只应摘录一行测试摘要。
- 如果没有运行测试，明确写 `not_run`，不要留空也不要虚构结果。
