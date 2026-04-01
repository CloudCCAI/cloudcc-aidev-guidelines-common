# AI Agent 项目状态外存规范

**Bilingual project-state protocol for AI coding agents**

这个 skill 用来做两件事：

1. 把项目状态外存到 `.claw/` 或 `.ai-dev/`
2. 给 AI 编码过程加入明确的读写和验证规则

它不是普通文档模板集合，而是一个给 AI 使用的项目记忆协议。

This skill does two things:

1. Externalizes project state into `.claw/` or `.ai-dev/`
2. Enforces explicit read, write, and verification rules for AI-assisted development

It is not just a document template pack. It is a reusable project memory protocol for coding agents.

## 一句话介绍 | One-Line Pitch

让 AI 在跨会话开发中拥有稳定、可审计、可持续更新的项目记忆。

Give coding agents a durable, auditable, and structured project memory across sessions.

## 适用场景 | When To Use

- 你希望 AI 在多轮开发中持续理解项目状态
- 你希望把 goals、ADR、issues、tests、devops 知识外存到仓库
- 你希望 AI 遵守更明确的开发规范，而不是每次从零开始
- 你希望减少“上下文遗忘”“状态漂移”“重复提问”

- You want AI to retain project context across coding sessions
- You want goals, ADRs, issues, tests, and devops knowledge stored in the repo
- You want explicit coding-agent rules instead of ad-hoc behavior
- You want to reduce context loss, state drift, and repeated clarification

## 核心价值 | Value Proposition

- `状态外存`：把项目关键状态持久化到仓库，而不是依赖对话上下文
- `行为约束`：明确 AI 何时读取、何时更新、何时必须验证
- `唯一事实源`：避免同一事实在多个文件里漂移
- `可自动化`：可配合脚本、Hooks、CI 使用
- `可审计`：状态变化可追踪，可回看，可校验

- `Externalized state`: keep durable project memory in files, not only in chat context
- `Behavior constraints`: define when agents must read, update, and verify
- `Single source of truth`: reduce duplicated and conflicting state
- `Automation-ready`: works with scripts, hooks, and CI
- `Auditable`: state changes are visible, reviewable, and testable

## 仓库内容 | Repository Contents

| 路径 | 说明 |
|------|------|
| `SKILL.md` | 主 skill 协议 / main skill protocol |
| `STATE-MODEL.md` | 详细状态模型 / detailed state model |
| `templates/` | 6 个状态文件模板 / six state file templates |
| `scripts/` | 初始化与校验脚本 / init and validation scripts |
| `examples/` | 完整示例项目状态 / complete sample state set |
| `CHANGELOG.md` | 版本变更记录 / version history |

## 设计原则 | Design Principles

- 默认最小读取，而不是默认全量读取
- 触发式更新，而不是机械回写全部文件
- 热状态与冷状态分层
- 摘要与事实源分离
- 已验证事实与推断结论分离

- Read the minimum necessary state by default
- Use trigger-based updates instead of rewriting every file
- Separate hot state from cold state
- Separate summaries from authoritative records
- Separate verified facts from inferred conclusions

## 快速开始

### 1. 初始化状态目录

```bash
cd your-project
mkdir -p .claw
cp /path/to/this-skill/templates/*.md .claw/
```

或者直接使用初始化脚本：

```bash
bash /path/to/this-skill/scripts/init-state.sh /path/to/your-project
```

### 2. 先填最少内容

初始化时优先填写这三个文件：

- `current-status.md`
- `goals.md`
- `decisions.md`（如果已有明确技术选型）

其余文件在触发条件出现后再写。

### 3. 让 AI 按协议执行

每次会话：

- 先读 `current-status.md`
- 按需再读其他状态文件
- 结束时回写 `current-status.md`
- 只有触发条件满足时才更新其他文件

### 4. 运行校验

```bash
python3 /path/to/this-skill/scripts/validate-state.py /path/to/your-project/.claw
```

## 状态分层

| 层级 | 文件 | 默认动作 | 用途 |
|------|------|----------|------|
| Hot | `current-status.md` | 每次读，每次更新 | 当前快照、下一步、读取索引 |
| Warm | `issue-list.md` | 按需读写 | bug、阻塞、风险 |
| Warm | `test-report.md` | 按需读写 | 已验证的测试结果 |
| Cold | `goals.md` | 触发式读写 | 项目目标、范围、成功标准 |
| Cold | `decisions.md` | 触发式读写 | 架构与技术决策 |
| Cold | `devops.md` | 触发式读写 | 构建、部署、运维知识 |

核心原则：不要把 6 个文件当作同一热度的文档。

## 每个文件负责什么

| 文件 | 唯一事实源 |
|------|------------|
| `current-status.md` | 当前任务、阶段、下一步 |
| `goals.md` | 目标、范围、成功标准 |
| `decisions.md` | 技术决策及其变更 |
| `issue-list.md` | 问题、风险、阻塞 |
| `test-report.md` | 真实测试结果 |
| `devops.md` | 已验证运维知识 |

不要在多个文件里独立维护同一事实。

## AI 执行规则

### 读取规则

- 默认只读 `current-status.md`
- 涉及目标或范围变化时读 `goals.md`
- 涉及技术选型或架构争议时读 `decisions.md`
- 涉及 bug、阻塞、风险时读 `issue-list.md`
- 运行测试或分析失败时读/写 `test-report.md`
- 涉及构建、环境、部署时读 `devops.md`

### 更新规则

- 每次会话结束更新 `current-status.md`
- 只有真实变化发生时才更新其他文件
- 没跑测试就不要写 `test-report.md`
- 没有形成非平凡技术决策就不要写 `decisions.md`

### 行为规则

- 只读取完成任务所需的最小状态
- 不伪造测试、构建、部署结果
- 区分 verified、inferred、needs-confirmation
- 不把临时思考写进长期状态文件
- 不覆盖用户明确写下的目标和决策

## 推荐工作流

### 新会话开始

1. 读取 `current-status.md`
2. 根据 `read_next` 或“相关状态文件”提示，决定是否读取别的文件
3. 执行任务

### 会话进行中

1. 只在事实发生变化时更新状态
2. 将问题写入 `issue-list.md`
3. 将真实测试结果写入 `test-report.md`
4. 将非平凡技术结论写入 `decisions.md`

### 会话结束

1. 更新 `current-status.md`
2. 如果有触发项，再更新对应文件
3. 保持摘要简洁，避免重复

## 模板说明

- `templates/current-status.md`：热状态入口
- `templates/goals.md`：项目目标和约束
- `templates/decisions.md`：ADR 模板
- `templates/issue-list.md`：问题和风险清单
- `templates/test-report.md`：真实测试结果
- `templates/devops.md`：构建和部署手册

模板统一使用 YAML front matter，便于 AI 稳定读写。

## 示例项目

仓库内提供了完整示例：

- `examples/README.md`
- `examples/sample-project/.claw/current-status.md`

这套示例展示了 6 个文件如何在同一个任务上下文里协同工作。

## 工具脚本

- `scripts/init-state.sh`：将模板初始化到目标项目
- `scripts/validate-state.py`：检查必需文件、front matter 和 `kind` 是否正确

## 参考文档

- [SKILL.md](SKILL.md) - 主协议
- [STATE-MODEL.md](STATE-MODEL.md) - 详细状态模型和枚举
- [CHANGELOG.md](CHANGELOG.md) - 版本变更记录
- [RELEASE_TEMPLATE.md](RELEASE_TEMPLATE.md) - 发布说明模板 / release note template
- [LICENSE](LICENSE) - MIT license

## 最佳实践

- 保持 `current-status.md` 足够短，确保 AI 每次都能快速读完
- 用 ID 和引用代替长段复制
- 将长历史归档到独立文件，不污染热状态
- 让 AI 记录“项目知识”，不要记录“思考过程”

## 避免

- 每次会话都读完整个状态目录
- 在多个文件里复制同一个事实
- 没有验证就写“测试通过”或“问题已解决”
- 把 `current-status.md` 写成流水账

## 发布检查

- `SKILL.md` 保持精简，主入口职责明确
- 所有模板都有统一 front matter
- 提供完整示例状态目录
- 提供初始化脚本和校验脚本
- `README.md` 能独立解释安装、使用和验证方式
- `CHANGELOG.md` 记录版本变化
- `LICENSE` 和 `RELEASE_TEMPLATE.md` 已补齐

---

*版本 2.0.0 | 面向 AI 项目状态外存与编码规范*
