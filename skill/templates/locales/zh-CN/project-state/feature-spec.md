---
kind: feature-spec
schema_version: 5
feature_id: {{FEATURE_ID}}
work_type: {{WORK_TYPE}}
title: "{{TITLE}}"
status: draft
init_status: awaiting_confirmation
init_completed_at: none
init_confirmed_by: none
owner_role: shared
owner_slug: {{OWNER_SLUG}}
created_at: {{TIMESTAMP}}
created_by: "{{CREATED_BY}}"
created_by_slug: {{CREATED_BY_SLUG}}
created_by_source: {{CREATED_BY_SOURCE}}
created_by_developer_id: {{CREATED_BY_DEVELOPER_ID}}
contributors:
  - "{{CREATED_BY}}"
task_ids: none
related_decisions: none
related_issues: none
policy_version: 3
updated_at: {{TIMESTAMP}}
updated_by: "{{CREATED_BY}}"
---

# {{FEATURE_ID}} - {{TITLE}}

## 背景与目标

- 说明用户问题、项目现状和期望结果。

## 范围

### 范围内

- 列出本次必须完成的行为。

### 范围外

- 列出明确不在本次交付内的行为。

## 当前行为与目标行为

- 当前：记录已验证的当前行为。
- 目标：记录用户确认的目标行为。

## 方案设计

- 记录设计概览、关键流程和方案选择理由。

## 接口与数据影响

- 记录 API、事件、消息、数据结构、迁移和兼容影响。

## 任务拆分

- 用户确认本 FEAT 后再创建并链接真实 TASK，不预建占位任务。

## 验收标准

- 记录可验证的用户行为和技术条件。

## 风险与回滚

- 记录已知风险、监控点和失败后的回滚方案。

## 交接说明

- 记录下一位接手者需要先读的事实源和未决问题。
