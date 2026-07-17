---
kind: project-baseline
title: Skill repository baseline
status: active_reference
owner_role: shared
updated_at: 2026-04-30T01:31:01Z
updated_by: codex
---

# PROJECT-BASELINE

## 项目概览

- 当前项目是 `cc-aidev-guidelines-common` 技能仓库。
- 当前最活跃的交付方向是完善项目级技能声明，让采用该技能的新项目和老项目都能在 `README.md` 与 `AGENTS.md` 中明确要求自动使用此技能。
- 现在纳入这套协议，是为了让后续对技能本身的演进也具备可恢复的状态、任务和设计上下文。

## Verified Facts

- 仓库以 `skill/SKILL.md` 为技能协议主入口，以 `README.md` 和 `skill/STATE-MODEL.md` 作为对外说明。
- `skill/scripts/init-state.sh` 是项目初始化入口，`skill/scripts/validate-state.py` 是状态校验入口。
- 仓库已经提供 `.claw/`、`docs/specs/` 模板和 `skill/examples/sample-project/` 示例项目。
- 当前会话已新增 `skill/scripts/ensure-agent-guidance.sh`，用于幂等写入项目根目录的 `README.md` 与 `AGENTS.md` 声明块。

## Inferred Facts

- 后续版本迭代会继续围绕“协议约束 + 初始化脚本 + 校验器 + 示例项目”四个面同步演进。
- 示例项目会被当作技能预期输出的参考实现，因此 README/AGENTS 的声明结构应与主仓库保持一致。

## Pending Verification

- 尚未验证在更多真实外部仓库上运行 `skill/scripts/ensure-agent-guidance.sh` 的效果。
- 尚未建立对 README/AGENTS 声明块位置或格式的更细粒度定制规则。

## Legacy Hotspots

- `skill/scripts/validate-state.py` 的 front matter 解析逻辑较轻量，后续如果状态文件结构更复杂，需要评估是否升级解析方式。
- 文档、脚本、示例和模板之间存在跨文件一致性约束，版本升级时容易漏改。

## Key Entry Points

- 技能入口：`skill/SKILL.md`
- 项目说明：`README.md`
- 状态模型：`skill/STATE-MODEL.md`
- 初始化脚本：`skill/scripts/init-state.sh`
- 项目级声明写入器：`skill/scripts/ensure-agent-guidance.sh`
- 校验脚本：`skill/scripts/validate-state.py`

## Active Delivery Surface

- 当前任务：`TASK-001`
- 当前功能设计：`docs/specs/FEAT-001-project-skill-declaration.md`

## Adoption Plan

- 用本仓库自己的 `.claw/` 和 `docs/specs/` 跟踪技能演进。
- 把“README/AGENTS 技能声明”作为 greenfield 和 brownfield 的共同接入要求。
- 保持示例项目与主协议同步，避免文档和脚本行为分叉。

## Handoff Notes

- 新接手的智能体先读 `.claw/current-status.md`、`.claw/task-board.md`、本文件和 `docs/specs/FEAT-001-project-skill-declaration.md`。
- 如果继续演进初始化流程，优先检查 `skill/scripts/init-state.sh`、`skill/scripts/ensure-agent-guidance.sh` 和 `skill/scripts/validate-state.py` 三者的一致性。
