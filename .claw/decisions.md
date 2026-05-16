---
kind: decisions
version: 3
updated_at: 2026-05-16T02:21:56Z
updated_by: codex
---

# 技术决策记录

`decisions.md` 是架构和技术选型的唯一事实源。

## 决策索引

| 编号 | 标题 | 状态 | 日期 | 替代/被替代 |
|------|------|------|------|-------------|
| ADR-001 | Use managed README/AGENTS declaration blocks | accepted | 2026-04-30 | - |
| ADR-002 | Use public identity records and signed task assignments for async parallel delivery | accepted | 2026-05-01 | - |
| ADR-003 | Treat team status as a generated manager view | accepted | 2026-05-01 | - |
| ADR-004 | Gate multi-developer work through project-manager assignments and SSH-signed Git identity | accepted | 2026-05-16 | - |

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

## ADR-002 - Use public identity records and signed task assignments for async parallel delivery

- 状态：`accepted`
- 日期：`2026-05-01`
- 背景：两个独立开发者可能在不同环境中并行开发，过程里无法依赖实时状态同步，最后合并时容易出现身份不清、写入范围冲突和热文件冲突。
- 备选方案：把管理者口令加密存入项目文档并下发开发者 token；只依赖聊天记录和 PR 描述；使用仓库内公钥身份记录、管理者签名授权、单任务状态文件和集成队列。
- 最终结论：采用公钥身份记录和任务授权协议。项目文档只保存公钥、开发者 ID、任务授权、状态分片和集成队列，不保存管理者口令、bearer token、私钥或可复用密钥。
- 为什么这个方案胜出：公钥和授权记录适合异步、多环境、可审计的协作模式；单任务状态文件能减少 `current-status.md` 合并冲突；集成队列能把最终合并顺序和验证门禁显性化。
- 后续影响：技能协议、模板、初始化脚本和校验器都要支持可选的 `.claw/developers/`、`.claw/assignments/`、`.claw/tasks/` 和 `.claw/integration-queue.md`。
- 验证方式：运行 `python3 scripts/validate-state.py .claw`，并确认可选并行协作文件存在时能通过结构校验。

## ADR-003 - Treat team status as a generated manager view

- 状态：`accepted`
- 日期：`2026-05-01`
- 背景：管理者需要查看团队成员列表、任务分配、贡献状态和集成状态，但这些事实分散在 identity、assignment、task status、task-board 和 integration queue 中。
- 备选方案：让管理者手工维护 `.claw/team-status.md`；把所有贡献状态写回 `current-status.md`；把 `team-status.md` 定义为派生视图并用脚本生成。
- 最终结论：`team-status.md` 是派生管理视图，由 `scripts/summarize-team-status.py` 按标准顺序生成，不作为事实源。
- 为什么这个方案胜出：它给管理者一个统一入口，同时避免多人频繁编辑热文件，也避免把汇总快照误当成真实授权或进度来源。
- 后续影响：初始化流程会创建团队状态模板；校验器会校验其 front matter；当开发者、授权、任务状态或集成队列变化后，应重新生成团队状态。
- 验证方式：运行 `python3 scripts/summarize-team-status.py .claw --write` 和 `python3 scripts/validate-state.py .claw`。

## ADR-004 - Gate multi-developer work through project-manager assignments and SSH-signed Git identity

- 状态：`accepted`
- 日期：`2026-05-16`
- 背景：用户要求每个项目有项目经理，只有项目经理能添加团队成员和规定负责功能范围；开发前必须识别开发者身份并阻止越权开发。
- 备选方案：只依赖聊天记录和人工约定；只绑定 Git author/email；使用 Git 平台账号绑定、SSH commit signing、项目经理任务授权和 preflight 脚本共同校验。
- 最终结论：采用项目经理门控授权模型。默认推荐 Git 平台账号绑定 + SSH commit signing；`.claw/developers/` 保存公开身份和签名指纹，`.claw/assignments/` 保存项目经理授权范围，`scripts/check-assignment.py` 用于本地和 CI preflight 检查。
- 为什么这个方案胜出：Git author/email 可伪造，不能作为强身份依据；SSH signing 易于团队理解和平台验证，配合分支保护与 CI 能把授权规则变成可执行门禁。
- 后续影响：协议、模板、校验器和 README 都要明确项目经理是唯一授权入口；CI 接入时应把 PR author、branch 和 changed files 传给 preflight 脚本。
- 验证方式：运行 `python3 scripts/check-assignment.py` 的通过和阻断用例、`python3 scripts/validate-state.py .claw`、以及 Python 语法检查。
- 补充规则：默认一个 Git 平台账号只绑定一个 active 身份；如果同账号需要兼任多个身份，必须使用不同 SSH signing key fingerprint 并记录 `role_sharing_exception`；同账号同 key 不应同时代表项目经理和开发者。

## 维护规则

- 只记录非平凡技术决策。
- 决策变更时，不删除历史，新增或更新状态。
- 必须写清楚为什么选它，而不只是选了什么。
