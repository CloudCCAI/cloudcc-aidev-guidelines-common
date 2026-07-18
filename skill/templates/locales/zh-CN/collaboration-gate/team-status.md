---
kind: team-status
schema_version: 5
updated_at: {{TIMESTAMP}}
updated_by: summarize-team-status
status: derived
---

# 团队状态汇总

`team-status.md` 是按需生成的管理者视图，不是事实源。

## 汇总规则

1. `.claw/developers/*.yaml`
2. `.claw/assignments/*.yaml`
3. `.claw/tasks/*.md`
4. `.claw/task-board.md`
5. `.claw/integration-queue.md`

## 团队概览

| 指标 | 数量 |
|---|---:|
| 开发者 | 0 |
| 活跃开发者 | 0 |
| 授权任务 | 0 |
| 阻塞任务 | 0 |

## 成员状态

- 运行 `python3 scripts/summarize-team-status.py .claw --write` 生成真实视图。
