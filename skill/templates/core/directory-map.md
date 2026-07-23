---
kind: directory-map
schema_version: 5
version: 5
init_status: not_started
init_completed_at: none
init_confirmed_by: none
updated_at: {{TIMESTAMP}}
updated_by: onboarding
project_mode: {{PROJECT_MODE}}
---

<!-- cc-aidev:onboarding-incomplete -->

> 此标记表示必需答案尚未确认。填写真实项目答案并取得用户确认后，才能删除标记并将 `init_status` 设为 `complete`。

# 目录地图

`directory-map.md` 是仓库目录职责和依赖边界的事实源。

## 目录职责

| 路径 | 职责 | 入口 | 证据状态 |
|---|---|---|---|
| `.` | 等待用户确认 | 等待用户确认 | `{{EVIDENCE_STATUS}}` |
| `docs/help/` | 面向用户的产品帮助和使用手册 | `README.md` | 已初始化 |
| `docs/design/` | 功能、交互、业务流转、状态和异常路径等详细设计；每份 Markdown 配对同名 HTML | `README.md`、`README.html` | 已初始化 |

## 允许的依赖

- 等待用户确认。

## 禁止的依赖

- 等待用户确认。

## 生成内容与外部内容

- 记录智能体不应编辑的生成目录、依赖副本、缓存、构建产物和外部管理路径。

## 待验证事项

- 记录职责不明确的目录，以及确认它所需的最小动作。

## 维护规则

- 描述有意义的项目目录，不要罗列每个生成子目录。
- 没有证据时，不要把 Brownfield 推断标记为已验证。
