---
kind: test-report
version: 5
updated_at: 2026-07-23T09:05:16Z
updated_by: Bimo
last_run_at: 2026-07-23T09:05:16Z
last_run_status: passed
---

# Test Report

`test-report.md` records real verification evidence. Keep the latest useful result compact.

## Latest Run Summary

- 状态：`passed`
- 范围：`Skill 5.0.5 design/specs Markdown 配对 HTML`
- 命令：90 项 unittest；四个项目的 HTML 摘要检查；Greenfield/Brownfield v5、legacy v4 与本仓库状态校验；Python 编译、JSON、Shell、diff 和 Chrome 渲染检查
- 环境：`local workspace`

## Result Summary

| Type | Total | Passed | Failed | Skipped | Coverage |
|------|-------|--------|--------|---------|----------|
| Python unit tests | 90 | 90 | 0 | 0 | n/a |
| HTML pair freshness checks | 4 | 4 | 0 | 0 | n/a |
| Project state profiles | 4 | 4 | 0 | 0 | n/a |
| Syntax, JSON, Shell and diff checks | 6 | 6 | 0 | 0 | n/a |
| Browser rendering | 1 | 1 | 0 | 0 | n/a |
| Skill standard validation | 1 | 1 | 0 | 0 | n/a |
| Total | 106 | 106 | 0 | 0 | n/a |

## Failures

- None.

## Notes

- 单文件与项目批量模式均验证了同目录同 basename 输出、嵌套目录、中文、表格、任务项、代码块、链接和安全转义。
- 缺失 HTML、源摘要不一致和生成器版本不一致都会被检查命令与状态校验器识别。
- 初始化器、Brownfield baseline 和 FEAT 分配器的自动同步已覆盖；重复同步当前配对文件不会重写。
- Chrome 实际渲染确认了响应式双栏布局、关键元数据、本文目录和原生折叠章节。
- `skill-creator` 的 `quick_validate.py` 确认 Skill front matter、命名和目录结构有效。
- 上述验证命令不包含提交、推送、变更请求或部署；发布证据以 Git 历史和实际推送输出为准。

## Common Commands

- `python3 skill/scripts/validate-state.py .claw`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skill/tests -p 'test_*.py'`
- `python3 -c 'import ast, pathlib; ...'`
- `python3 skill/scripts/dev-login.py .claw --ssh-key ~/.ssh/id_ed25519_cc_dev --developer DEV-xxx --task TASK-xxx --files path/to/file`
- `python3 skill/scripts/check-assignment.py .claw --developer DEV-xxx --task TASK-xxx --files path/to/file`

## Maintenance Rules

- Update this file only after a real command runs.
- Keep only the latest useful evidence here.
- Move long historical testing narratives to release notes or dedicated audit artifacts when needed.
