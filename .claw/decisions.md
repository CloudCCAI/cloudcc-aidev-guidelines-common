---
kind: decisions
version: 3
updated_at: 2026-04-30T01:31:01Z
updated_by: codex
---

# 技术决策记录

`decisions.md` 是架构和技术选型的唯一事实源。

## 决策索引

| 编号 | 标题 | 状态 | 日期 | 替代/被替代 |
|------|------|------|------|-------------|
| ADR-001 | Use managed README/AGENTS declaration blocks | accepted | 2026-04-30 | - |

推荐状态值：`proposed` / `accepted` / `rejected` / `superseded`

## 新增决策时记录

每条 ADR 至少记录以下信息：

- 编号，如 `ADR-001`
- 状态
- 日期
- 背景
- 备选方案
- 最终结论
- 为什么这个方案胜出
- 后续影响
- 验证方式
- 参考资料

## ADR-001 - Use managed README/AGENTS declaration blocks

- 状态：`accepted`
- 日期：`2026-04-30`
- 背景：技能此前只约束 `.claw/` 和 `docs/specs/`，无法确保新接手智能体在仓库根目录就看到“必须自动使用此技能”的要求。
- 备选方案：只更新 `SKILL.md`；只要求人工编辑 `README.md` 和 `AGENTS.md`；增加受控声明块并配套脚本和校验器。
- 最终结论：使用带 marker 的受控声明块，由脚本幂等写入 `README.md` 和 `AGENTS.md`，并由校验器检查是否存在。
- 为什么这个方案胜出：它同时覆盖 greenfield 和 brownfield，自动化程度高，也能减少文档漂移。
- 后续影响：初始化流程和示例项目都要同步维护这两个文件；校验器会对未补齐声明块的项目给出失败结果。
- 验证方式：运行 `python3 scripts/validate-state.py .claw`，并检查主仓库与示例项目的 `README.md`、`AGENTS.md`。

## 维护规则

- 只记录非平凡技术决策。
- 决策变更时，不删除历史，新增或更新状态。
- 必须写清楚为什么选它，而不只是选了什么。
