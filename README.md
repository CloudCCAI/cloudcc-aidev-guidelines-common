# AI Agent 项目状态与交付规范

**Bilingual project-state and delivery protocol for AI coding agents**

这个 skill 现在覆盖三件事：

1. 把项目状态外存到 `.claw/` 或 `.ai-dev/`
2. 用 `task-board.md` 管理任务、依赖和交接
3. 用 `docs/specs/` 强制功能级设计先落盘再开发，并支持老项目渐进接入

It now covers three layers:

1. durable project state in `.claw/` or `.ai-dev/`
2. executable task tracking and handoff in `task-board.md`
3. spec-driven delivery in `docs/specs/`, including brownfield adoption

## 一句话介绍 | One-Line Pitch

让 AI 在跨会话、跨智能体协作中，不只记住“现在做到哪”，还记住“为什么这样做、接下来该谁做、按什么设计继续做”。

## 版本标识 | Version Marker

当前 skill 版本：`3.2.0`

唯一权威版本标识位于 [SKILL.md](SKILL.md) front matter 中的 `skill_version` 字段。智能体需要判断当前安装的是哪个版本时，应优先读取这个字段，而不是以 README 或 CHANGELOG 为准。

## 仓库内容 | Repository Contents

| 路径 | 说明 |
|------|------|
| `SKILL.md` | 主 skill 协议 / main skill protocol |
| `STATE-MODEL.md` | 详细状态模型 / detailed state model |
| `templates/` | 7 个状态文件模板 / seven state file templates |
| `templates/docs/feature-spec-template.md` | 功能设计模板 / feature spec template |
| `templates/docs/project-baseline-template.md` | 老项目基线模板 / legacy baseline template |
| `scripts/` | 初始化与校验脚本 / init and validation scripts |
| `examples/` | 完整示例状态与 spec / sample state and feature spec |
| `CHANGELOG.md` | 版本变更记录 / version history |

## 设计原则 | Design Principles

- 默认最小读取，而不是默认全量读取
- 触发式更新，而不是机械回写全部文件
- 热状态、任务队列、长文档设计分层
- 摘要、任务、问题、设计各自有唯一事实源
- 已验证事实与推断结论分离
- 非平凡功能先写 spec，再进入主开发
- 老项目先建 baseline，再渐进纳入完整协议

## 快速开始

### 1. 初始化状态与文档目录

推荐直接使用脚本：

```bash
bash /path/to/this-skill/scripts/init-state.sh /path/to/your-project
```

它会创建：

- `.claw/` 状态目录
- `docs/specs/` 文档目录
- `docs/specs/_feature-spec-template.md` 模板文件
- `docs/specs/_project-baseline-template.md` 老项目基线模板

### 2. 先判断项目类型

在第一次接入时，先区分当前项目属于哪一类：

- `新项目 / Greenfield`：项目刚启动，或某个新模块可以从零按协议落盘
- `老项目 / Brownfield`：项目已经存在一段时间，之前没有按这套协议维护状态和设计文档

如果判断标准不清晰，可以用这个经验法则：

- 需要先理解遗留实现、推断架构、补运行入口，通常是老项目
- 可以直接从当前需求开始拆任务和写 spec，通常是新项目

### 3. 先补最少内容

初始化后优先确认这些文件：

- `.claw/current-status.md`
- `.claw/goals.md`
- `.claw/task-board.md`

如果当前工作属于新功能、跨模块改动、接口/数据变更或非平凡重构，再创建：

- `docs/specs/FEAT-xxx-feature-name.md`

如果这是老项目首次接入，再先创建：

- `docs/specs/PROJECT-BASELINE.md`

### 4. 新项目如何使用 | Greenfield Workflow

推荐按这个顺序：

1. 运行初始化脚本
2. 填写 `.claw/current-status.md`
3. 填写 `.claw/goals.md`
4. 在 `.claw/task-board.md` 中创建首批任务
5. 对非平凡功能创建 `docs/specs/FEAT-xxx-feature-name.md`
6. 开发过程中持续同步 `task-board.md`、feature spec、`current-status.md`
7. 会话结束时更新必要状态文件并运行校验

适用于：

- 从零开始的新仓库
- 新立项项目
- 在老仓库里独立启动的新模块或新子系统

### 5. 老项目如何使用 | Brownfield Workflow

推荐按这个顺序：

1. 运行初始化脚本
2. 先创建 `docs/specs/PROJECT-BASELINE.md`
3. 在 baseline 里记录当前已确认事实、推断事实、待验证项、关键入口和热点模块
4. 在 `.claw/task-board.md` 里创建“接管/接入”任务，必要时让任务先指向 `PROJECT-BASELINE.md`
5. 从当前正在推进的工作开始，逐步要求 `task-board + feature spec`
6. 只有当某个老模块真的被改动时，才为它补对应 `FEAT-xxx-*.md`
7. 每次确认了新的 legacy 理解，就回写 `PROJECT-BASELINE.md`

适用于：

- 之前没有任何项目状态外存的老仓库
- 有代码但缺少设计文档和任务交接材料的项目
- 需要多个智能体轮流接手的存量系统

老项目接入时要特别注意：

- 不要求一次性补齐全部历史
- 不要把历史猜测写成 verified 事实
- 不要一边大改 legacy，一边不更新 baseline
- 目标是先建立“可继续推进的共同基线”，不是补作文档库存

### 6. 让 AI 按协议执行

每次会话：

- 先读 `current-status.md`
- 做实现或交接时再读 `task-board.md`
- 任务有 `spec_path` 时先读对应 spec
- 结束时至少回写 `current-status.md`

### 7. 运行校验

```bash
python3 /path/to/this-skill/scripts/validate-state.py /path/to/your-project/.claw
```

校验器会检查：

- 必需状态文件是否存在
- front matter 是否完整且时间戳有效
- `task-board.md` 里的任务卡是否有效
- `spec_path` 引用的 feature spec 或 baseline 文档是否真实存在且 front matter 合法

## 状态分层 | State Layers

| 层级 | 文件 | 默认动作 | 用途 |
|------|------|----------|------|
| Hot | `current-status.md` | 每次读，每次更新 | 当前快照、下一步、读取索引 |
| Warm | `task-board.md` | 实现/交接时读写 | 任务、依赖、责任角色、交接 |
| Warm | `issue-list.md` | 按需读写 | bug、阻塞、风险 |
| Warm | `test-report.md` | 按需读写 | 已验证的测试结果 |
| Cold | `goals.md` | 触发式读写 | 项目目标、范围、成功标准 |
| Cold | `decisions.md` | 触发式读写 | 架构与技术决策 |
| Cold | `devops.md` | 触发式读写 | 构建、部署、运维知识 |
| External | `docs/specs/PROJECT-BASELINE.md` | 老项目接入时必读必写 | 旧系统基线、未知项、接管边界 |
| External | `docs/specs/*.md` | 非平凡功能必读必写 | 需求、设计、任务拆分、验收、交接 |

## 每个文件负责什么 | Source Of Truth

| 文件 | 唯一事实源 |
|------|------------|
| `current-status.md` | 当前会话、阶段、下一步 |
| `task-board.md` | 执行队列、`owner_role`、依赖、交接说明 |
| `goals.md` | 项目目标、范围、成功标准 |
| `docs/specs/PROJECT-BASELINE.md` | 老项目当前基线、推断架构、未知项和接管说明 |
| `docs/specs/*.md` | 单个功能的完整设计与落地过程 |
| `decisions.md` | 技术决策及其变更 |
| `issue-list.md` | 问题、风险、阻塞 |
| `test-report.md` | 真实测试结果 |
| `devops.md` | 已验证运维知识 |

不要在多个文件里独立维护同一事实。

## `task-board.md` 设计建议

推荐字段：

- `TASK-xxx`
- `status`
- `priority`
- `owner_role`
- `claimed_by`（可选）
- `spec_path`
- `depends_on`
- `blocked_by`
- `related_issues`
- `scope_files`
- `next_action`
- `handoff_note`

推荐状态：

- `todo`
- `ready`
- `in_progress`
- `blocked`
- `review`
- `done`
- `canceled`

推荐 `owner_role`：

- `backend-agent`
- `frontend-agent`
- `fullstack-agent`
- `qa-agent`
- `release-agent`
- `human`
- `shared`
- `unassigned`

说明：

- `owner_role` 是稳定责任角色，不依赖智能体自我身份
- `claimed_by` 是可选运行时标签，环境知道就写，不知道就留空

## `docs/specs/` 规则 | Spec-Driven Delivery

以下情况默认必须先建 spec：

- 新功能
- 跨模块改动
- API 或数据结构变更
- 非平凡重构
- 预计会跨会话或跨智能体交接的工作

以下情况可以只用任务卡：

- 小型 bugfix
- 文案或样式微调
- 局部配置修改
- 不需要长期保留设计上下文的简单改动

推荐采用“一功能一主文档”：

```text
docs/specs/
├── _project-baseline-template.md
├── PROJECT-BASELINE.md
├── _feature-spec-template.md
├── FEAT-001-login-reliability.md
└── FEAT-002-user-invite.md
```

## 老项目接入 | Brownfield Adoption

老项目不需要先补齐所有历史才能使用这个 skill，更推荐按下面的顺序渐进接入：

1. 创建 `.claw/current-status.md`、`.claw/task-board.md`
2. 创建 `docs/specs/PROJECT-BASELINE.md`
3. 只记录当前可确认的系统现状、推断架构、活跃未知项和当前交付边界
4. 从当前正在推进的任务开始要求 `task-board + spec`
5. 只在真正修改某个老模块时，再补它对应的 feature spec

`PROJECT-BASELINE.md` 至少应包含：

- 当前项目目标和活跃交付面
- verified facts
- inferred facts
- pending verification
- 关键入口、关键依赖、热点模块
- 当前接手者最先该看的文件和命令

这样做的目标不是“补历史”，而是“建立可继续推进的共同基线”。

## 最佳实践 | Best Practices

- 保持 `current-status.md` 足够短，确保 AI 每次都能快速读完
- 用 ID 和引用代替长段复制
- 把交接信息放到 `task-board.md` 或 feature spec，而不是聊天记录
- 功能实现偏离原设计时，先更新 spec 再继续写代码
- 老项目先更新 `PROJECT-BASELINE.md`，再做大范围 legacy 改动
- 让 AI 记录项目知识，不记录临时思考过程

## 避免 | Anti-Patterns

- 每次会话都读完整个状态目录和所有 spec
- 在多个文件里复制同一个事实
- 把 `task-board.md` 当成 bug 列表或设计文档
- 没有验证就写“测试通过”或“问题已解决”
- 先写大量代码，再补 feature spec
- 要求老项目一次性补齐全部历史文档
- 把 `current-status.md` 写成流水账

## 参考文档 | References

- [SKILL.md](SKILL.md)
- [STATE-MODEL.md](STATE-MODEL.md)
- [examples/README.md](examples/README.md)
- [CHANGELOG.md](CHANGELOG.md)

---

*版本 3.2.0 | 面向 AI 多智能体协作与老项目渐进接入的项目状态与交付规范*
