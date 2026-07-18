---
kind: feature-spec
feature_id: FEAT-006
title: Hard pre-edit identity gate
status: implemented
owner_role: shared
task_ids: TASK-006
related_decisions: ADR-006
related_issues: none
updated_at: 2026-05-17T00:00:00Z
updated_by: codex
---

# FEAT-006 - Hard Pre-Edit Identity Gate

## 背景与目标

- 3.7.0 增加了 `skill/scripts/dev-login.py`，但实际项目中仍可能出现 agent 在“明确身份”但未完成 SSH challenge-response 验证时直接修改代码。
- 用户要求：只要使用此技能，就必须自动触发硬阻断规则，不能通过聊天声明、缓存、Git metadata 或其他路径绕过。
- 目标是把本地身份验证从推荐流程升级为使用身份/授权记录项目中的强制编辑前门禁。

## 范围

### In Scope

- 明确硬身份门禁自动启用条件。
- 明确 `skill/scripts/dev-login.py` 是本地编辑前唯一有效身份验证入口。
- 明确 `skill/scripts/check-assignment.py` 不能替代本地 challenge-response 登录。
- 明确未验证、验证失败、缺少私钥路径、缺少任务/分支/文件范围或缺少 assignment 时必须停止。
- 更新 `skill/SKILL.md`、`README.md`、`skill/STATE-MODEL.md`、模板、ADR、任务状态和使用说明。

### Out Of Scope

- 不拦截底层编辑器或操作系统文件写入。
- 不保存私钥、token、密码或 bearer secret。
- 不改变 CI 侧 `check-assignment.py` 的职责。

## 硬阻断规则

当项目存在任一条件时，硬身份门禁自动启用：

- `.claw/developers/`
- `.claw/assignments/`
- 任务卡包含 `assignment_path`
- assignment 包含 `local_login_required: true`
- task/spec 指定 `skill/scripts/dev-login.py` 为本地身份检查

门禁启用后，AI agent 或开发者在修改以下文件前必须先让 `skill/scripts/dev-login.py` 返回 `allowed`：

- 源码
- 测试
- 运行配置
- 数据库迁移
- 生成的应用资产
- feature spec
- `.claw/tasks/TASK-xxx.md`
- 任何会改变项目行为或交付状态的文件

不能作为绕过依据：

- 聊天里声明的 `developer_id`
- 已知用户名或 Git author/email
- 历史会话记忆
- `.claw-local/identity.json` 的存在
- `skill/scripts/check-assignment.py` 通过

## 允许的登录前修改

唯一允许的登录前仓库修改是 PM 明确要求的身份或 assignment 初始化/修复，例如：

- 创建第一个 `MANAGER-xxx`
- 添加或修复 `.claw/developers/DEV-xxx.yaml`
- 添加或修复 `.claw/assignments/TASK-xxx.yaml`
- 补 `.gitignore` 忽略本地身份缓存

这些修改不得触碰应用源码、测试、运行配置、迁移或生成资产。

## 验收标准

- `skill/SKILL.md` 使用 `must` 描述本地 `dev-login.py` 硬门禁。
- README 和 STATE-MODEL 明确聊天声明、缓存、Git metadata 和 `check-assignment.py` 不能绕过本地登录。
- 模板引导新项目启用 hard gate。
- 状态校验和 Python 语法检查通过。

## 实现进展

- 当前状态：`implemented`
- 已完成项：协议、README、状态模型、模板、ADR、任务状态、使用说明和验证记录

## 交接说明

- 后续如果要进一步增强“无后门”，应接入 agent runtime 的编辑前 hook 或 IDE/CI 强制策略；协议层已经要求 agent 在本地编辑前必须执行 `dev-login.py`。
