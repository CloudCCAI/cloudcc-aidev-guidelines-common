---
kind: feature-spec
feature_id: FEAT-001
title: Project-root skill declaration and automation
status: implemented
owner_role: shared
task_ids: TASK-001
related_decisions: ADR-001
related_issues: none
updated_at: 2026-04-30T01:31:01Z
updated_by: codex
---

# FEAT-001 - Project-root skill declaration and automation

## 背景与目标

- 让采用 `cc-aidev-guidelines-common` 的项目在仓库级显式声明必须自动使用该技能。
- 让没有安装该技能的智能体，能从项目文档中直接看到 GitHub 安装来源。
- 让新项目初始化和老项目接入都能自动或半自动补齐 `README.md` 与 `AGENTS.md`。

## 范围

### In Scope

- 在技能协议中新增项目级 README/AGENTS 声明要求。
- 为项目根目录 `README.md` 和 `AGENTS.md` 提供幂等写入脚本。
- 在初始化脚本中自动调用声明写入器。
- 在校验脚本中校验声明块、技能名和 GitHub 来源。
- 更新示例项目和仓库自身文档以反映新约束。

### Out Of Scope

- 通用的 GitHub 克隆或技能安装器实现。
- 针对不同代理平台的安装命令适配。
- 自定义 README/AGENTS 插入位置策略。

## 用户场景

- 新项目初始化时，智能体运行 `init-state.sh` 后，项目根目录自动出现 README/AGENTS 声明块。
- 老项目首次接入时，智能体通过脚本或按技能协议补齐 README/AGENTS 声明，再继续后续维护。
- 后续新会话中的智能体，即使未读聊天记录，也能从仓库文件判断需要自动使用该技能。

## 现状与约束

- 现有技能只约束 `.claw/` 和 `docs/specs/`，没有项目根级别的技能声明锚点。
- README 和 AGENTS 需要支持增量补写，不能粗暴覆盖已有项目文档。
- 校验器需要保持轻量，不引入复杂依赖。

## 方案设计

- 新增 `scripts/ensure-agent-guidance.sh`，用受控 marker 包裹声明块，并以幂等方式写入 `README.md` 和 `AGENTS.md`。
- `scripts/init-state.sh` 在创建状态目录前后自动调用该脚本，保证 greenfield 和 brownfield 都能补齐声明。
- `scripts/validate-state.py` 增加项目根 README/AGENTS 检查，至少验证文件存在、受控 marker 存在、技能名存在、GitHub 来源存在。
- 更新 `SKILL.md`、`README.md`、`STATE-MODEL.md`、示例项目和仓库自身 `AGENTS.md`，让规则、脚本和示例一致。

## 接口与数据影响

- 无外部 API 变更。
- 项目初始化会新增或修改项目根目录 `README.md` 和 `AGENTS.md`。
- 技能版本从 `3.3.0` 升级为 `3.4.0`。

## 任务拆分

- `TASK-001`：实现项目级技能声明、初始化自动化、校验器检查和文档更新。

## 验收标准

- 项目根目录 `README.md` 和 `AGENTS.md` 都包含受控声明块。
- 声明块明确包含技能名、自动使用要求和 GitHub 安装来源。
- `scripts/init-state.sh` 会自动刷新 README/AGENTS 声明块。
- `python3 scripts/validate-state.py .claw` 在当前仓库通过。

## 风险与回滚

- 风险：项目已有 README/AGENTS 的布局可能与自动追加策略不完全契合。
- 风险：校验规则如果过严，可能影响尚未补齐声明的老项目接入节奏。
- 回滚方式：移除新增脚本和校验规则，恢复 README/AGENTS 的手工维护模式。

## 实现进展

- 已完成：声明写入脚本、初始化自动调用、校验器检查、技能文档更新、示例补齐。
- 已完成：主仓库自身 `README.md` 和 `AGENTS.md` 声明块刷新。
- 未完成：跨更多真实仓库的兼容性验证。

## 交接说明

- 下一位接手者如需增强声明块策略，优先保持 marker 和校验规则兼容。
- 如需支持更多平台安装方式，可在不破坏 GitHub 来源要求的前提下补充平台特定说明。
