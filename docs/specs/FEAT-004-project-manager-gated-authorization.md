---
kind: feature-spec
feature_id: FEAT-004
title: Project-manager-gated team authorization
status: implemented
owner_role: shared
task_ids: TASK-004
related_decisions: ADR-004
related_issues: none
updated_at: 2026-05-16T02:21:56Z
updated_by: codex
---

# FEAT-004 - Project-manager-gated team authorization

## 背景与目标

- 用户希望多人协作方案中有一个明确的项目经理角色，只有项目经理能添加团队成员并规定每个成员的负责功能范围。
- 开发前必须识别当前开发者身份，并判断开发范围是否与项目经理授权相符。
- 如果身份未知、成员未激活、任务未授权或文件范围越界，AI agent 和 CI 检查都应阻止开发。

## 范围

### In Scope

- 明确项目经理是团队成员和任务授权的唯一授权入口。
- 默认推荐 Git 平台账号绑定 + SSH commit signing。
- 扩展开发者身份模板，记录 Git 平台账号、SSH 签名公钥指纹、长期功能范围和授权管理者。
- 扩展任务授权模板，记录授权状态、授权分支、授权范围、签名验证引用和越界审批要求。
- 增加开发前 preflight 授权检查脚本，校验开发者、任务、分支和文件范围。
- 更新 `SKILL.md`、`README.md`、`STATE-MODEL.md`、模板、校验器和状态文件。

### Out Of Scope

- 不实现完整密码学验签库。
- 不保存私钥、token、密码或 bearer secret。
- 不直接配置 GitHub/GitLab 分支保护规则。
- 不接入远端 PR API；CI 可把 PR author、branch 和 changed files 作为脚本参数传入。

## 用户场景

- 项目经理添加 `DEV-alice`，绑定 GitHub/GitLab 账号和 SSH signing key fingerprint，并指定长期负责范围。
- 项目经理创建 `TASK-004` 授权，只允许 `DEV-alice` 在指定分支修改 `scope_files`。
- 开发者或 AI agent 开始开发前运行 preflight 检查；通过后才能继续。
- PR CI 收集变更文件并运行同一脚本；越界时失败，提示需要项目经理更新授权。

## 现状与约束

- `3.5.0` 已有 `.claw/developers/`、`.claw/assignments/`、`.claw/tasks/` 和 `.claw/integration-queue.md`。
- 现有协议强调不保存私钥、token 和口令，但尚未明确项目经理唯一授权入口。
- Git author/email 不可信，只能作为辅助信息；可信绑定应优先使用 Git 平台账号和 SSH commit signing 指纹。
- 默认一个 Git 平台账号只绑定一个 active 身份；同账号多身份必须使用不同 SSH signing key fingerprint，并显式记录例外原因。
- 仓库文件是协作与审计协议，不是完整权限系统；真正强制执行需要分支保护和 CI 门禁。

## 方案设计

- 在协议层新增 `Project-Manager-Gated Authorization Mode`，作为异步并行交付的默认授权模型。
- 开发者身份文件记录：
  - `developer_id`
  - `role`
  - `status`
  - `managed_by`
  - `git_platform`
  - `git_username`
  - `ssh_signing_key_fingerprint`
  - `allowed_scopes`
- 任务授权文件记录：
  - `assigned_by` 必须是 `MANAGER-xxx`
  - `status` 必须为 `active` 才能开发
  - `branch`、`scope_files` 和 `touch_policy` 是开发前硬边界
  - `signature` 记录项目经理签名提交、PR approval 或外部验证引用
- 新增 `scripts/check-assignment.py`，用于本地和 CI：
  - 校验开发者身份存在且 active
  - 校验开发者记录绑定的 Git 平台账号和 SSH 签名指纹
  - 校验任务授权存在、active、assignee 匹配、assigned_by 是项目经理
  - 校验可选 branch 参数与授权分支匹配
  - 校验传入文件路径都落在 assignment `scope_files` 内
  - 校验 active 身份记录中同一 Git username 的重复绑定是否符合不同 SSH signing key 和例外说明规则
  - 对越界、未授权、身份未知等情况返回非 0 退出码

## 身份与授权计划

- 启用异步多开发者协作：`yes`
- 项目管理者身份：`MANAGER-001`
- 开发者身份文件：`.claw/developers/DEV-xxx.yaml`
- 任务授权文件：`.claw/assignments/TASK-xxx.yaml`
- 单任务状态文件：`.claw/tasks/TASK-xxx.md`
- 团队状态汇总：`.claw/team-status.md`
- 默认签名方式：SSH commit signing
- 默认账号策略：一个 Git 平台账号绑定一个 active 身份
- 角色兼任例外：同账号多身份必须使用不同 SSH signing key fingerprint，并记录 `role_sharing_exception`
- 允许兼容：GPG signing
- 高级增强：Sigstore/gitsign 用于 CI、制品签名和供应链审计
- 不允许提交管理者口令、开发者 token、私钥或可复用密钥

## 并行与集成计划

- 本次是协议和工具升级，不拆多个并行开发任务。
- `scope_files` 见 `TASK-004`。
- 集成策略：直接更新当前工作树，验证通过后进入 review。
- 后续 CI 接入可调用同一 preflight 脚本。

## 接口与数据影响

- 新增脚本入口：`scripts/check-assignment.py`
- 新增 GitHub Actions 示例：`templates/github-workflows/check-assignment.yml`
- 开发者模板新增 Git 平台账号、SSH 签名指纹、长期范围字段。
- 任务授权模板新增 `status` 和项目经理授权要求。
- 校验器新增对项目经理授权、签名身份字段和授权状态的最低结构校验。

## 任务拆分

- `TASK-004`：实现项目经理门控授权协议、模板、脚本和校验器支持。

## 验收标准

- `SKILL.md`、`README.md`、`STATE-MODEL.md` 明确项目经理唯一授权入口和 SSH signing 默认推荐。
- 模板能指导项目经理添加成员、绑定 Git 账号/SSH 签名指纹、分配任务范围。
- `scripts/check-assignment.py` 能在授权通过、身份不符、分支不符和文件越界时给出明确结果。
- `scripts/validate-state.py .claw` 通过。
- Python 脚本语法检查通过。

## 风险与回滚

- 风险：用户误以为仓库 YAML 本身就是强权限系统。
- 降低方式：文档明确真正强制执行依赖 Git 平台分支保护、required signed commits 和 CI。
- 回滚：保留 3.5 的身份/授权结构，移除 3.6 新增强制字段或把 preflight 脚本标记为可选。

## 实现进展

- 当前状态：`implemented`
- 已完成项：协议、README、状态模型、模板、校验器、preflight 脚本、GitHub Actions 示例、身份重复绑定规则、ADR、任务状态和验证记录
- 未完成项：用户 review 后决定是否接入 GitHub/GitLab PR API 或提供完整异步并行示例项目

## 交接说明

- 下一位接手者先看本文件，再检查 `SKILL.md` 的授权流程、`templates/parallel/*.yaml` 和 `scripts/check-assignment.py` 是否一致；如果要做更强门禁，优先新增 CI workflow 示例而不是把任何 token 写入仓库。

## 3.8.0 任务边界宽代码权限补充

- `scope_files` 作为所有代码文件硬边界的设计已保留为 `scope_mode: exact_files`，用于窄任务和敏感任务。
- 普通功能开发推荐使用 `scope_mode: task_bounded_broad_code`，由 `allowed_write_roots` 授权源码和测试根路径，由 `protected_paths` 保护治理、CI、迁移和门禁脚本。
- 项目经理门控的核心仍是“谁可以处理哪个任务”；代码审查和 change manifest 判断跨模块修改是否服务于当前任务。
