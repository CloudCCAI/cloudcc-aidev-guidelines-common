---
kind: feature-spec
feature_id: FEAT-003
title: Standard team status aggregation
status: implemented
owner_role: shared
task_ids: TASK-003
related_decisions: ADR-002, ADR-003
related_issues: none
updated_at: 2026-05-01T11:44:25Z
updated_by: codex
---

# FEAT-003 - Standard team status aggregation

## 背景与目标

- 管理者需要查看当前项目开发者团队列表、任务分配、成员贡献状态和集成状态。
- `developers/`、`assignments/`、`tasks/` 和 `integration-queue.md` 已经分散保存事实源，但缺少统一的标准汇总方法。
- 本次目标是声明 `.claw/team-status.md` 为派生汇总视图，并提供可重复运行的汇总脚本。

## 范围

### In Scope

- 定义团队状态汇总的事实源优先级和字段映射。
- 新增 `.claw/team-status.md` 派生视图模板。
- 新增 `scripts/summarize-team-status.py`，支持打印汇总或写入 `.claw/team-status.md`。
- 更新协议、README、STATE-MODEL、初始化脚本和校验器。

### Out Of Scope

- 直接连接 GitHub/GitLab 等远端平台拉取 PR/CI 数据。
- 真实验签、权限控制或代码托管平台权限管理。
- 把 `team-status.md` 作为人工维护的事实源。

## 用户场景

- 管理者运行汇总脚本查看当前团队状态。
- 管理者在合并前检查哪些成员已经接手任务、哪些任务已有 PR、哪些任务处于 blocked/review/done。
- 集成者刷新 `.claw/team-status.md`，把当前团队协作状态作为只读快照提交到项目状态中。

## 现状与约束

- 团队状态必须避免成为多人频繁编辑的热文件。
- 当前脚本应保持轻量，只依赖 Python 标准库。
- 本地汇总只能基于仓库内已有状态文件，不应伪造远端 PR、CI 或 review 结果。

## 方案设计

- `.claw/team-status.md` 是 derived view，不是 source of truth。
- 标准汇总顺序：
  1. 读取 `.claw/developers/*.yaml` 获得团队成员和身份状态。
  2. 读取 `.claw/assignments/*.yaml` 获得任务授权、分支、PR、写入范围和 assignee。
  3. 读取 `.claw/tasks/*.md` 获得单任务进度、PR、验证摘要和阻塞状态。
  4. 读取 `.claw/task-board.md` 补充任务标题、优先级、owner role 和主看板状态。
  5. 读取 `.claw/integration-queue.md` 补充合并队列和 integration status。
  6. 生成团队维度和任务维度汇总。
- 汇总脚本默认打印到 stdout，传 `--write` 时刷新 `.claw/team-status.md`。

## 接口与数据影响

- 新增可选状态文件 `.claw/team-status.md`。
- 新增模板 `templates/team-status.md`。
- 新增脚本 `scripts/summarize-team-status.py`。
- 初始化脚本会创建初始团队状态模板。
- 校验器存在即校验 `team-status.md` front matter。

## 任务拆分

- `TASK-003`：实现团队状态汇总协议、模板、脚本、初始化和校验支持。

## 验收标准

- 协议明确 `team-status.md` 是派生视图，不是事实源。
- README 说明管理者如何运行标准汇总方法。
- 初始化脚本创建 `team-status.md`。
- 汇总脚本可在当前仓库运行并输出/写入团队状态。
- 校验器接受 `team-status.md` 并能通过当前仓库状态校验。

## 风险与回滚

- 风险：使用者误以为 `team-status.md` 可以手工长期维护。
- 缓解：文档和模板明确标注 derived view，事实源仍是分片文件和 Git/PR/CI 证据。
- 回滚方式：保留分片事实源，移除汇总脚本和 derived view。

## 实现进展

- 已完成：协议、README 和 STATE-MODEL 声明 `team-status.md` 为派生管理视图。
- 已完成：新增 `templates/team-status.md` 和 `scripts/summarize-team-status.py`。
- 已完成：初始化脚本创建 `.claw/team-status.md`。
- 已完成：校验器支持可选 `team-status.md`。
- 已完成：当前仓库生成 `.claw/team-status.md` 并通过状态校验。
- 未完成：远端 PR/CI 平台数据接入。

## 交接说明

- 后续如要接入 GitHub/GitLab，应作为额外数据源扩展汇总脚本，不应改变 `team-status.md` 的派生视图定位。
