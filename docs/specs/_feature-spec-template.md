---
kind: feature-spec
feature_id: FEAT-001
title: Feature title
status: draft
owner_role: shared
task_ids: TASK-001
related_decisions: none
related_issues: none
updated_at: 2026-04-30T01:23:08Z
updated_by: ai
---

# FEAT-001 - Feature title

## 背景与目标

- 为什么要做这项功能
- 期望解决的用户问题或业务问题
- 本次交付完成后应达到的结果

## 范围

### In Scope

- 本次必须完成的内容

### Out Of Scope

- 明确不在本次实现的内容

## 用户场景

- 核心用户是谁
- 他们会如何使用这项能力
- 失败路径或边界情况有哪些

## 现状与约束

- 当前实现现状
- 相关技术约束、时间约束、合规约束
- 对已有模块、接口、数据模型的限制

## 方案设计

- 设计概览
- 关键流程
- 为什么采用这个方案

## 身份与授权计划

- 是否启用异步多开发者协作：`no`
- 项目管理者身份：`MANAGER-xxx` / `n/a`
- 开发者身份文件：`.claw/developers/DEV-xxx.yaml` / `n/a`
- 任务授权文件：`.claw/assignments/TASK-xxx.yaml` / `n/a`
- 单任务状态文件：`.claw/tasks/TASK-xxx.md` / `n/a`
- 团队状态汇总：`.claw/team-status.md` / `n/a`
- 项目经理门控授权：`yes` / `no`
- 默认身份绑定：Git 平台账号 + SSH commit signing
- 本地身份登录：`scripts/dev-login.py` hard gate / `n/a`
- 开发前检查：`scripts/check-assignment.py` / `n/a`
- 不允许提交管理者口令、开发者 token、私钥或可复用密钥

## 并行与集成计划

- 可并行任务组
- 每个任务的 `scope_mode`、`allowed_write_roots`、`scope_files`、`protected_paths` 和 `touch_policy`
- 普通功能开发优先使用任务边界宽代码权限，避免把必要调用链修改硬塞进错误模块
- 共享接口、数据结构、配置 key 或迁移顺序
- 集成分支和合并顺序
- 集成负责人和验证门禁

## 接口与数据影响

- API、事件、消息、数据库或配置层面的变更
- 向后兼容、迁移和回滚考虑

## 任务拆分

- 对应 `task-board.md` 中的任务 ID
- 任务依赖关系
- 推荐责任角色
- 异步并行任务应列出 `assignment_path`、`task_status_path` 和 `integration_queue`

## 验收标准

- 用户可见行为
- 技术验收条件
- 需要验证的命令、测试或检查项

## 风险与回滚

- 已知风险
- 监控点
- 失败后的回滚或降级方式

## 实现进展

- 当前状态
- 已完成项
- 未完成项

## 交接说明

- 下一位接手者先看什么
- 当前阻塞点是什么
- 继续推进前需要确认什么
