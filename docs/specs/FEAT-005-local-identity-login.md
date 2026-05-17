---
kind: feature-spec
feature_id: FEAT-005
title: Local SSH challenge-response identity login
status: implemented
owner_role: shared
task_ids: TASK-005
related_decisions: ADR-005
related_issues: none
updated_at: 2026-05-17T00:00:00Z
updated_by: codex
---

# FEAT-005 - Local SSH Challenge-Response Identity Login

## 背景与目标

- 用户希望在项目开始开发前，像登录一样先报告并验证当前正在修改代码的用户身份。
- 3.6.0 已有 `check-assignment.py`，但它验证的是传入的身份和任务授权，不证明本地操作者真的持有该身份对应的私钥。
- 目标是在本地开发会话开始时，先用 SSH 私钥完成 challenge-response 验证，再进入任务授权检查。

## 范围

### In Scope

- 新增 `scripts/dev-login.py`。
- 支持首次传入本机私钥路径，并从私钥推导 public key 和 fingerprint。
- 根据 `.claw/developers/*.yaml` 自动匹配 `developer_id`。
- 用一次性 challenge 签名和登记的 `public_key` 验签，证明私钥持有。
- 验证通过后可把私钥路径和公开身份元数据写入本机忽略缓存。
- 当传入 `--task` 时，串联 `scripts/check-assignment.py` 做 assignment、branch 和 `scope_files` 检查。
- 更新协议、README、状态模型、模板和验证记录。

### Out Of Scope

- 不保存私钥内容、密码、token 或 bearer secret。
- 不实现跨机器共享登录态。
- 不替代 Git 平台 signed commits、分支保护和 CI。
- 不接入系统 Keychain 或企业 SSO；后续可作为可选增强。

## 用户场景

- 开发者首次开始开发时运行 `scripts/dev-login.py .claw --ssh-key ~/.ssh/id_ed25519_cc_dev --task TASK-001 --files src/example/file.ts`。
- 脚本自动解析该 key 对应的 `DEV-xxx`，报告身份和 fingerprint。
- 后续同一机器上可省略 `--ssh-key`，脚本从 `.claw-local/identity.json` 读取私钥路径后重新签名验签。
- 如果私钥不存在、身份已被暂停、public key 不匹配、验签失败或任务越界，脚本返回非 0 并阻止开发。

## 方案设计

- `.claw/developers/DEV-xxx.yaml` 中的 `public_key` 是登录式验签的公开材料，`ssh_signing_key_fingerprint` 是该 key 的短标识。
- `scripts/dev-login.py` 执行：
  - `ssh-keygen -y -f <private-key>` 推导 public key。
  - `ssh-keygen -lf <public-key>` 计算 fingerprint。
  - 扫描 `.claw/developers/*.yaml`，按 public key 或 fingerprint 匹配 active 身份。
  - 生成 nonce challenge。
  - `ssh-keygen -Y sign` 用本机私钥签名 challenge。
  - `ssh-keygen -Y verify` 用登记 public key 验签。
  - 可选调用 `scripts/check-assignment.py` 验证任务授权。
- 本地缓存文件只保存：
  - `developer_id`
  - `ssh_key_path`
  - `ssh_signing_key_fingerprint`
  - `git_username`
  - `updated_at`

## 身份与授权计划

- 启用异步多开发者协作：`yes`
- 项目管理者身份：`MANAGER-001`
- 开发者身份文件：`.claw/developers/DEV-xxx.yaml`
- 本地身份缓存：`.claw-local/identity.json` 或 `.ai-dev-local/identity.json`
- 本地身份登录：`scripts/dev-login.py`
- 开发前任务检查：`scripts/check-assignment.py`
- 默认身份绑定：SSH challenge-response + Git 平台账号 + SSH commit signing
- 不允许提交管理者口令、开发者 token、私钥或可复用密钥

## 接口与数据影响

- 新增脚本入口：`scripts/dev-login.py`
- 新增本地忽略路径：`.claw-local/`、`.ai-dev-local/`
- 开发者模板说明 `public_key` 用于 challenge-response 验证。
- assignment 模板增加 `local_login_required` 和新的 `identity_policy` 示例。

## 任务拆分

- `TASK-005`：实现本地登录式身份验证协议、脚本、模板和文档。

## 验收标准

- `scripts/dev-login.py` 能用临时 SSH key 完成身份匹配、challenge 签名、验签和 assignment 检查。
- `scripts/dev-login.py` 能用本机缓存自动复用私钥路径并重新验签。
- 错误 key 或越界文件会返回非 0。
- `scripts/validate-state.py .claw` 通过。
- Python 脚本语法检查通过。

## 风险与回滚

- 风险：用户误以为本地缓存等于登录凭证。
- 降低方式：文档明确缓存只保存路径，每次开发仍要重新 challenge-response 验证。
- 回滚：保留 `check-assignment.py` 和 3.6.0 授权模型，移除 `dev-login.py` 及本地缓存说明。

## 实现进展

- 当前状态：`implemented`
- 已完成项：脚本、协议文档、README、状态模型、模板、任务状态和验证记录
- 未完成项：后续可选接入系统 Keychain、GitHub/GitLab signer API 或企业 SSO

## 交接说明

- 下一位接手者先看 `scripts/dev-login.py` 和本 spec；如果要增强强制力，应优先接入平台 signed commit 验证或系统密钥管理，而不是把任何私钥或 token 写入仓库。

## 3.7.1 硬阻断补充

- 当项目存在 `.claw/developers/`、`.claw/assignments/`、`assignment_path` 或 `local_login_required: true` 时，本地身份门禁自动启用。
- AI agent 或开发者必须在任何源码、测试、运行配置、迁移、生成资产、feature spec 或任务状态修改前运行 `scripts/dev-login.py`。
- 只有 `scripts/dev-login.py` 当前会话返回 `allowed` 才能进入开发；聊天中明确身份、Git author/email、历史记忆、本地缓存路径或 `scripts/check-assignment.py` 都不能替代本地 challenge-response 登录。
- 如果缺少私钥路径、任务 ID、分支、待修改文件列表或 assignment，agent 必须停止并要求补齐验证输入或 PM 授权。
- 唯一允许的登录前仓库修改是 PM 明确要求的身份/assignment 初始化或修复；这些修改不得触碰应用源码、测试、运行配置、迁移或生成资产。
