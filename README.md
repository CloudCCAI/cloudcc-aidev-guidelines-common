# AI Agent 项目状态与交付规范

**Bilingual project-state and delivery protocol for AI coding agents**

这个 skill 现在覆盖三件事：

1. 把项目状态外存到 `.claw/` 或 `.ai-dev/`
2. 用 `task-board.md` 管理任务、依赖和交接
3. 用 `docs/specs/` 强制功能级设计先落盘再开发

It now covers three layers:

1. durable project state in `.claw/` or `.ai-dev/`
2. executable task tracking and handoff in `task-board.md`
3. spec-driven delivery in `docs/specs/`

## 一句话介绍 | One-Line Pitch

让 AI 在跨会话、跨智能体协作中，不只记住“现在做到哪”，还记住“为什么这样做、接下来该谁做、按什么设计继续做”。

## 版本标识 | Version Marker

当前 skill 版本：`3.1.0`

唯一权威版本标识位于 [SKILL.md](SKILL.md) front matter 中的 `skill_version` 字段。智能体需要判断当前安装的是哪个版本时，应优先读取这个字段，而不是以 README 或 CHANGELOG 为准。

## 仓库内容 | Repository Contents

| 路径 | 说明 |
|------|------|
| `SKILL.md` | 主 skill 协议 / main skill protocol |
| `STATE-MODEL.md` | 详细状态模型 / detailed state model |
| `templates/` | 7 个状态文件模板 / seven state file templates |
| `templates/docs/feature-spec-template.md` | 功能设计模板 / feature spec template |
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

### 2. 先补最少内容

初始化后优先确认这些文件：

- `.claw/current-status.md`
- `.claw/goals.md`
- `.claw/task-board.md`

如果当前工作属于新功能、跨模块改动、接口/数据变更或非平凡重构，再创建：

- `docs/specs/FEAT-xxx-feature-name.md`

### 3. 让 AI 按协议执行

每次会话：

- 先读 `current-status.md`
- 做实现或交接时再读 `task-board.md`
- 任务有 `spec_path` 时先读对应 spec
- 结束时至少回写 `current-status.md`

### 4. 运行校验

```bash
python3 /path/to/this-skill/scripts/validate-state.py /path/to/your-project/.claw
```

校验器会检查：

- 必需状态文件是否存在
- front matter 是否完整且时间戳有效
- `task-board.md` 里的任务卡是否有效
- `spec_path` 引用的 feature spec 是否真实存在且 front matter 合法

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
| External | `docs/specs/*.md` | 非平凡功能必读必写 | 需求、设计、任务拆分、验收、交接 |

## 每个文件负责什么 | Source Of Truth

| 文件 | 唯一事实源 |
|------|------------|
| `current-status.md` | 当前会话、阶段、下一步 |
| `task-board.md` | 执行队列、`owner_role`、依赖、交接说明 |
| `goals.md` | 项目目标、范围、成功标准 |
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
├── _feature-spec-template.md
├── FEAT-001-login-reliability.md
└── FEAT-002-user-invite.md
```

## 最佳实践 | Best Practices

- 保持 `current-status.md` 足够短，确保 AI 每次都能快速读完
- 用 ID 和引用代替长段复制
- 把交接信息放到 `task-board.md` 或 feature spec，而不是聊天记录
- 功能实现偏离原设计时，先更新 spec 再继续写代码
- 让 AI 记录项目知识，不记录临时思考过程

## 避免 | Anti-Patterns

- 每次会话都读完整个状态目录和所有 spec
- 在多个文件里复制同一个事实
- 把 `task-board.md` 当成 bug 列表或设计文档
- 没有验证就写“测试通过”或“问题已解决”
- 先写大量代码，再补 feature spec
- 把 `current-status.md` 写成流水账

## 参考文档 | References

- [SKILL.md](SKILL.md)
- [STATE-MODEL.md](STATE-MODEL.md)
- [examples/README.md](examples/README.md)
- [CHANGELOG.md](CHANGELOG.md)

---

*版本 3.1.0 | 面向 AI 多智能体协作的项目状态与交付规范*
