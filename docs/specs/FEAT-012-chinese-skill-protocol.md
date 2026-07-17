---
kind: feature-spec
feature_id: FEAT-012
title: Chinese skill protocol and content consolidation
status: implemented
owner_role: shared
task_ids: TASK-012
related_decisions: none
related_issues: none
updated_at: 2026-07-17T07:13:02Z
updated_by: codex
---

# FEAT-012 - 中文技能协议与内容去重

## 需求

将 `skill/SKILL.md` 的说明性内容全部改为中文，保留技术关键字、字段名、状态枚举、变量、命令和路径原文，并合并重复规则。

## 设计

- 保持 `name`、`metadata.skill_version`、字段名、枚举值、脚本名、路径和命令不变。
- 将 `description` 和正文说明翻译为中文。
- 将目录解析、事实源、会话工作流、身份授权、平台操作和验证规则分别集中到单一章节。
- 将完整字段语义、枚举和冲突优先级留在 `STATE-MODEL.md`，`SKILL.md` 只保留执行所需的核心规则和引用入口。
- 不改变硬身份门禁、授权范围、Codeup、测试环境推送和状态更新行为。

## 验收标准

- `skill/SKILL.md` 的说明性英文内容已改为中文。
- 技术标识和命令保持不变。
- 重复规则显著减少，全文少于 400 行。
- 标准 Skill 校验、项目状态校验和关键协议检查通过。

## 验证

- 标准 `quick_validate.py`
- `python3 skill/scripts/validate-state.py .claw`
- 关键字段、脚本、状态和门禁文本检查
- `git diff --check`
