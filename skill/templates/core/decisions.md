---
kind: decisions
schema_version: 5
version: 5
init_status: not_started
init_completed_at: none
init_confirmed_by: none
architecture_init_status: not_started
architecture_reviewed_at: none
architecture_confirmed_by: none
updated_at: {{TIMESTAMP}}
updated_by: onboarding
project_mode: {{PROJECT_MODE}}
---

<!-- cc-aidev:onboarding-incomplete -->

> 此标记表示必需答案尚未确认。填写真实项目答案并取得用户确认后，才能删除标记并将 `init_status` 设为 `complete`。

# 架构与技术决策

`decisions.md` 保存当前 `ARCHITECTURE` 快照和重要决策的历史原因。

## ARCHITECTURE

### 证据约定

- Greenfield 计划在实现并验证前使用 `planned`。
- Brownfield 事实使用 `verified`、`inferred` 或 `pending verification`。

### 系统类型与技术栈

- 等待用户确认。

### 架构风格与运行流程

- 等待用户确认。

### 组件与边界

- 等待用户确认。

### 数据存储、流转与一致性

- 等待用户确认。

### 外部系统与依赖

- 等待用户确认。

### 构建、部署与运行拓扑

- 等待用户确认。

### 非功能约束

- 性能：等待用户确认
- 安全：等待用户确认
- 可用性：等待用户确认
- 合规：等待用户确认

### 待验证事项

- 记录未知项、所需证据和下一项验证动作。

## ADR 索引

当前没有已接受的 ADR。

## ADR 规则

- 记录背景、备选方案、最终选择、选择原因、后果和验证方式。
- 不要为了完成初始化而创建占位 ADR。
- 使当前架构快照失效的 ADR 必须把 `architecture_init_status` 设为 `needs_review`。
