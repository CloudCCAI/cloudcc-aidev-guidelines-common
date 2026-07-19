---
kind: task-status
schema_version: 5
task_id: TASK-bimo-009
task_type: feature
feature_id: FEAT-bimo-005
policy_version: 3
created_at: 2026-07-19T01:37:00Z
created_by: "Bimo"
created_by_slug: bimo
created_by_source: global_git_config_user_name
created_by_developer_id: none
assignee: bimo
owner_slug: bimo
owner_role: shared
status: done
stage: completed
branch: main
assignment_path: none
change_request_url: n/a
pr_url: n/a
next_action: "none"
updated_at: 2026-07-19T13:01:40Z
updated_by: "Bimo"
---

# TASK-bimo-009 - 中文模板清理

## 当前状态

- 状态：`done`
- 下一步：无；进入后续维护
- 阻塞：无
- 功能：`FEAT-bimo-005`
- 授权：无

## 进展

- 第一轮将中文模板提升为唯一规范来源，删除 locale 镜像、旧版模板和无运行入口的平台模板。
- 保留旧 manifest 的英文与 pending 只读兼容，新项目固定使用 `zh-CN`。
- 合并 Codeup 配置、DevOps 资产 catalog 和原子写入逻辑，删除无调用辅助函数与派生模板。
- 第二轮重新扫描死引用、精确重复、英文模板、空目录和生成缓存，并清理剩余安全项。
- 完成独立 Greenfield 前向初始化测试并修复目标目录前置条件、文档目录说明和 DevOps 幂等时间戳。
- 最终状态回写与独立差异审查补充修复了 legacy 热索引兼容、TASK 默认下一步中文化和公开命令残留参数。

## 变更文件

- `skill/SKILL.md`、`skill/STATE-MODEL.md`、references、catalog、schema、scripts、templates、examples 与 tests。
- `README.md`、`CHANGELOG.md`、ADR-017 及本次 FEAT/TASK 状态。

## 验证

- 状态：`passed`
- 证据：86 项单元测试全部通过；Python AST、Shell、JSON 与 diff 检查通过。
- 证据：Greenfield/Brownfield v5 严格校验、legacy v4 和本仓库状态校验通过。
- 证据：Skill 标准快速校验和独立 Greenfield 前向测试通过。

## 交接

- 本任务已完成；`5.0.3` 发布状态以 `main` 分支 Git 历史和实际推送结果为准。
