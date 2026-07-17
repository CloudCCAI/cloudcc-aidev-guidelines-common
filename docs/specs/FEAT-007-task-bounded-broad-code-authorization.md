---
kind: feature-spec
feature_id: FEAT-007
title: Task-bounded broad code authorization
status: implemented
owner_role: shared
task_ids: TASK-007
related_decisions: ADR-007
related_issues: none
updated_at: 2026-05-27T08:16:30Z
updated_by: codex
---

# FEAT-007 - Task-bounded broad code authorization

## 背景与目标

- 3.7.1 的硬身份门禁可以阻止未登录或未授权开发，但 `scope_files` 过窄时会把开发者限制在任务标题相关模块内。
- 真实功能经常需要沿调用链修改多个模块，项目经理很难在任务开始前准确预判全部实现文件。
- 本次目标是把门禁重心从“预判每个代码文件”调整为“验证开发者是否有权处理当前任务”，同时保护治理、身份、CI、迁移和门禁脚本等高风险路径。

## 范围

### In Scope

- 新增 assignment `scope_mode` 概念。
- 支持普通功能任务使用 `scope_mode: task_bounded_broad_code`。
- 使用 `allowed_write_roots` 放开源码和测试等普通代码路径。
- 使用 `protected_paths` 保护敏感治理路径，除非 PM 在 `scope_files` 中精确授权。
- 保留 `scope_mode: exact_files` 兼容旧项目和窄任务。
- 更新协议、README、STATE-MODEL、模板、校验器和授权检查脚本。

### Out Of Scope

- 不移除身份登录门禁。
- 不允许开发者自我扩权、修改 assignment 或添加成员。
- 不把宽代码权限扩展到密钥、身份、CI、迁移或门禁脚本。
- 不实现自动 diff 语义审查；变更是否服务于任务仍由 PR review 和 change manifest 共同判断。

## 用户场景

- 开发者处理 OpenAPI/Dify parity 任务时，发现必须修改聊天编排或模型路由模块，才能在正确层解决问题。
- 旧模式会阻止该文件写入，诱导开发者把修复塞回 OpenAPI 层。
- 新模式允许开发者在 `src/**` 和 `tests/**` 内修改必要调用链，同时阻止其触碰 `.claw/assignments/**`、`.claw/developers/**`、CI、迁移和门禁脚本。
- 授权根路径应符合人的目录直觉：`frontend/src`、`frontend/src/` 和 `frontend/src/**` 都表示递归目录根，不应因为 PM 少写 `/**` 而阻止目标文件。

## 现状与约束

- 硬身份门禁仍然是前置条件：`skill/scripts/dev-login.py` 必须返回 `allowed`。
- `.claw/assignments/TASK-xxx.yaml` 仍是项目经理授权的事实源。
- 宽代码权限不能替代 feature spec、验收标准、PR review 和 CI。
- 现有项目如果不声明 `scope_mode`，默认按 `exact_files` 处理，保持兼容。

## 方案设计

- `scope_mode: exact_files`
  - 所有目标文件必须匹配 `scope_files`。
  - 适合文档修补、配置小改、安全敏感任务和已知全部写入路径的任务。
- `scope_mode: task_bounded_broad_code`
  - 普通源码和测试可匹配 `allowed_write_roots`。
  - `protected_paths` 命中时默认阻止，除非该具体路径同时匹配 `scope_files`。
  - `scope_files` 继续用于当前任务 spec、任务状态文件和受保护路径精确授权。
  - `allowed_write_roots`、`protected_paths` 和开发者 `allowed_scopes` 中的裸目录按递归目录根处理；`scope_files` 中的裸路径保持精确匹配，除非显式写 glob。
  - `task_boundary` 和 linked spec 的验收标准定义产品范围。
  - `change_manifest_required: true` 要求开发者解释跨模块变更原因。

## 身份与授权计划

- 是否启用异步多开发者协作：`yes`
- 项目管理者身份：`MANAGER-xxx`
- 开发者身份文件：`.claw/developers/DEV-xxx.yaml`
- 任务授权文件：`.claw/assignments/TASK-xxx.yaml`
- 单任务状态文件：`.claw/tasks/TASK-xxx.md`
- 项目经理门控授权：`yes`
- 默认身份绑定：Git 平台账号 + SSH commit signing
- 本地身份登录：`skill/scripts/dev-login.py` hard gate
- 开发前检查：`skill/scripts/check-assignment.py`

## 并行与集成计划

- 默认功能任务 assignment 推荐：
  - `scope_mode: task_bounded_broad_code`
  - `allowed_write_roots: src, tests`
  - `scope_files`: 当前 feature spec 和当前 task status
  - `protected_paths`: identity、assignment、CI、迁移、门禁脚本、infra 和 secret 路径
- 集成者和 reviewer 检查 change manifest 是否能解释每个跨模块修改。

## 接口与数据影响

- `skill/scripts/check-assignment.py` 新增对 `scope_mode`、`allowed_write_roots` 和 `protected_paths` 的检查。
- `skill/scripts/validate-state.py` 新增 assignment `scope_mode` 最低结构校验。
- assignment 模板新增宽代码授权字段。
- 旧 assignment 未声明 `scope_mode` 时按 `exact_files` 处理。

## 任务拆分

- `TASK-007`：实现任务边界宽代码权限协议、模板、脚本和文档。

## 验收标准

- `scope_mode: task_bounded_broad_code` 下，`src/**` 和 `tests/**` 内文件可通过授权检查。
- `allowed_write_roots: frontend/src` 下，`frontend/src/...` 目标文件可通过授权检查。
- 命中 `protected_paths` 的文件如果不在 `scope_files` 内会被阻止。
- `scope_mode: exact_files` 旧行为保持不变。
- 状态校验和 Python 语法检查通过。

## 风险与回滚

- 风险：宽代码权限可能让 PR diff 变大。
- 缓解：要求 task boundary、linked spec、change manifest、PR review 和 CI 共同约束。
- 回滚：将 assignment 改回 `scope_mode: exact_files`，只使用 `scope_files` 精确授权。

## 实现进展

- 当前状态：已实现。
- 已完成项：协议文本、README、STATE-MODEL、模板、脚本和校验器；裸目录写入根递归匹配。
- 未完成项：无。

## 交接说明

- 下一位接手者先看 `skill/scripts/check-assignment.py` 的 scope mode 分支，再看 assignment 模板。
- 若要进一步增强，可以在 PR 模板或 CI 中检查 change manifest 是否覆盖所有 changed files。
