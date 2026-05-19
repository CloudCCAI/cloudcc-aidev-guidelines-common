---
kind: team-status
version: 3
updated_at: 2026-05-19T03:52:05Z
updated_by: summarize-team-status
status: derived
---

# 团队状态汇总

`team-status.md` 是管理者视图，由 `scripts/summarize-team-status.py` 根据项目状态文件生成。它不是事实源。

## 汇总规则

事实源优先级：

1. `.claw/developers/*.yaml`
2. `.claw/assignments/*.yaml`
3. `.claw/tasks/*.md`
4. `.claw/task-board.md`
5. `.claw/integration-queue.md`

如果本文件与事实源冲突，修复事实源后重新生成本文件。

## 团队概览

| 指标 | 数量 |
|------|------|
| 开发者 | 0 |
| 活跃开发者 | 0 |
| 授权任务 | 0 |
| 已开始任务 | 0 |
| 等待 review | 0 |
| 已集成任务 | 0 |
| 阻塞任务 | 0 |

## 成员状态

- 暂无开发者记录。

## 任务状态

- 暂无任务授权记录。


## 集成状态

- `TASK-002`: `ready`
- `TASK-003`: `ready`

## 维护规则

- 不手工维护本文件的事实内容。
- 管理者需要查看团队状态时，运行 `python3 scripts/summarize-team-status.py .claw --write`。
- 远端 PR/CI 数据只有在写入任务状态或由后续平台脚本接入后，才会进入本汇总。
