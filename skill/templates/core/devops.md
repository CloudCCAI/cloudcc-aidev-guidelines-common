---
kind: devops
schema_version: 5
version: 5
init_status: not_started
init_completed_at: none
init_confirmed_by: none
updated_at: {{TIMESTAMP}}
updated_by: onboarding
project_mode: {{PROJECT_MODE}}
verification_status: pending
devops_assets_root: DevOps
environment_names: none
---

<!-- cc-aidev:onboarding-incomplete -->

> 此标记表示必需答案尚未确认。填写真实项目答案并取得用户确认后，才能删除标记并将 `init_status` 设为 `complete`。

# 构建、运行、测试与运维

`devops.md` 保存已验证的操作入口和明确的待验证事项。

## 构建

- 命令：`pending verification`
- 证据：none

## 运行

- 命令：`pending verification`
- 入口：`pending verification`
- 证据：none

## 测试

- 命令：`pending verification`
- 证据：none

## 部署

- 目标：`pending verification`
- 流程：`pending verification`
- 证据：none

## 环境与外部服务

- 只记录环境变量名，绝不记录密钥值。
- 必需服务：`pending verification`
- 确认客户环境名称后，运行 `project-onboarding.py devops-assets`。
- 如果客户尚未决定，建议先预留 `DEV`、`UAT`、`PROD`，客户可稍后调整。
- 每个环境必须分别维护 `DevOps/<environment>/Dockerfile` 和 `DevOps/<environment>/.env.example`。

## 运维边界

- 健康检查：`pending verification`
- 日志与诊断：`pending verification`
- 回滚方式：`pending verification`

## 维护规则

- 命令只有在真实运行或权威证据确认后才能标记为已验证。
- 初始化可以保留明确的待验证项，但不得伪造成功证据。
