---
name: cc-aidev-guidelines-common
description: 通过 `.claw` manifest、引导式 Greenfield/Brownfield 初始化、逐文件初始化状态、按用户递增的 FEAT/TASK、多个并行工作流、项目经理身份门禁和可选 Codeup/GitHub 评审，持久化并渐进加载 AI 软件项目状态。用于首次接入项目、恢复未完成初始化、开始新 AI 会话、讨论和设计开发工作、拆解任务、跨会话交接、多人并行授权、创建代码合并申请、验证或维护项目状态。
metadata:
  skill_version: "5.0.2"
---

# AI 项目初始化与交付路由

使用本技能让 AI Agent 在跨会话和多人协作中持续维护项目事实。详细规则按需加载，不要在会话开始时展开全部 reference。

## 1. 必须先执行预检

项目状态目录固定为 `.claw/`，本地私密配置固定为 `.claw-local/`。

在分析、规划、实现或维护前先运行只读预检：

```bash
python3 scripts/project-preflight.py /path/to/project --json
```

按结果路由：

- 没有 `.claw/`：读取 [references/onboarding.md](references/onboarding.md)，引导初始化。
- 有 `.claw/`、没有 manifest：按 legacy v4 读取，不自动迁移、改名或补字段。
- manifest 为 `in_progress`：读取 onboarding reference，从第一个未完成核心文件恢复。
- manifest 为 `needs_review`：先修复漂移或待确认项。
- manifest 为 `ready`：只加载启用模块。

如果用户已经明确本次目标，不要重复询问固定菜单。

## 2. 按模块加载

先读取 `.claw/manifest.yaml` 的模块开关；legacy 项目按已有文件触发。

| 条件 | 读取 |
|---|---|
| 初始化、恢复或 reconfigure | [references/onboarding.md](references/onboarding.md) |
| `project_state=true` | [references/modules/project-state.md](references/modules/project-state.md) |
| `collaboration_gate=true`，或 legacy identity/assignment 已存在 | [references/modules/collaboration-gate.md](references/modules/collaboration-gate.md) |
| `change_review=true` | [references/modules/change-review.md](references/modules/change-review.md) |
| review platform 为 Codeup | [references/platforms/codeup.md](references/platforms/codeup.md) |
| review platform 为 GitHub | [references/platforms/github.md](references/platforms/github.md) |
| 需要完整字段、枚举、兼容或冲突规则 | [STATE-MODEL.md](STATE-MODEL.md) |
| 需要可运行样例 | [examples/README.md](examples/README.md) |

禁用模块的 reference、模板说明和状态文件不得加载。`collaboration_gate=true` 要求 `project_state=true`；不能静默开启依赖模块。

## 3. 初始化门槛

初始化先由用户确认文档语言和三个模块开关。语言支持 `zh-CN` 和 `en`，控制新写入的人类可读项目管理内容；不得翻译机器字段、枚举、ID、路径、命令或原始验证输出。

三个模块开关：

- `project_state`：建议开。
- `collaboration_gate`：默认关。
- `change_review`：默认关。

`project_state=true` 时，AI 再根据代码、配置、入口、构建清单、Git 历史和兼容义务建议 `greenfield` 或 `brownfield`，用户最终确认；不得只凭文件数量决定。`project_state=false` 时使用 `project_mode: not_applicable`，跳过类型和项目状态基线问答。

每次只问 1～3 个关联问题，保存进度并支持恢复。核心文件使用：

- `not_started`
- `in_progress`
- `awaiting_confirmation`
- `complete`
- `needs_review`

未知信息标为 `pending verification`，不得伪造事实。所有必需核心文件完成、动态校验通过且用户最终确认后，manifest 才能变为 `ready`。

引导 `devops.md` 时先确认客户环境清单，再初始化根目录 `DevOps/`。每个环境分别拥有 `Dockerfile` 和 `.env.example`。客户尚未决定时，先建议 `DEV`、`UAT`、`PROD` 三套预留环境；只有客户明确接受后才创建，后续允许增补或调整。初始化器不得覆盖或删除已有 DevOps 资产，占位 Dockerfile 不得伪装成可运行配置。

文档语言和项目模式确认后，`project_state=true` 的新项目必须初始化 `docs/help/README.md` 和 `docs/design/README.md`。`help` 保存面向用户的产品帮助和使用手册；`design` 保存功能、交互、业务流转、状态变化和异常流程等设计。路径统一小写，与 `docs/specs` 保持同一根目录；初始化只补缺，不覆盖已有内容。

新初始化未确认语言时使用 `language: pending`，不得先生成默认英文核心文件。早期 v5 manifest 缺少语言字段时按 `en` 兼容读取；legacy 文件和既有内容不自动翻译。

初始化为空看板；不要制造 `TASK-001`。issue、test report、archive、integration queue、team status、FEAT 和 TASK 都按真实事件创建。

## 4. 新会话意图

仅在 `project_state=true` 或 legacy 项目已有该文件时，每个新 AI 会话先读 `.claw/current-status.md`；项目状态模块关闭时不得为此加载或创建该文件。

- 用户目标清楚：复述理解并继续，不重复问。
- 用户目标不清楚：开放式询问，可以提示“新需求、老功能迭代、修改 bug”等例子。
- 这些例子不是封闭菜单；分析、文档、测试、重构、发布、部署、评审和项目管理都可直接路由。

保留用户原始 `session_intent`；`work_kind` 只是可扩展路由标签，不能覆盖用户意图。

## 5. 开发类交付流程

`project_state=true` 时，新功能、非平凡迭代、bug 修复、跨模块修改、API/数据结构变更和非平凡重构通常执行：

```text
讨论现状、目标、范围、验收、约束和风险
  → 创建 FEAT 草稿
  → 用户确认 FEAT
  → 拆分 TASK
  → 实现
  → 真实验证
  → 评审与关闭
```

FEAT 确认前可以只读分析，不得先实现后补设计。简单查询或小型独立维护可以不创建 FEAT。

已有活跃工作时，开始新工作前显示当前工作，让用户选择继续、并行、暂停或取消，不能静默覆盖。

## 6. 新文档命名

新 FEAT：

```text
docs/specs/FEAT-<author-slug>-<personal-sequence>-<description>.md
```

新 TASK：

```text
.claw/tasks/TASK-<owner-slug>-<personal-sequence>-<description>.md
```

规范 ID 不含 description，例如 `FEAT-bimo-001`、`TASK-bimo-001`。FEAT 和 TASK 分别按用户独立递增，从 `001` 开始且不复用。

自动作者固定按以下顺序解析：全局 Git 配置的 `user.name`、当前项目本地 Git 配置的 `user.name`、操作系统用户名。已登录 developer 的 `document_slug` 不参与自动文档命名；显式 `--owner` 作为用户确认的覆盖值。Git/OS 身份只用于署名，不能绕过授权门禁。

使用确定性分配器处理并发和持久计数，不手工猜下一个编号。

## 7. 最小状态读取

`project_state=true` 时按以下顺序：

1. manifest：只做路由，不展开全部内容。
2. current status：热索引，少于 60 行。
3. 实现、排期或交接时读取 task board。
4. 只读取选中任务的 task status。
5. 非平凡实现前读取关联 FEAT；Brownfield 广泛修改前读取 baseline。
6. 只在触发时读取 goals、ARCHITECTURE/ADR、directory map、issue、test、devops、identity、assignment、integration 或 review 配置。

字段事实源：

- task board：队列、优先级、依赖和协调指针。
- task status：执行进展、验证、变更、阻塞、下一步和交接。
- FEAT：需求、设计和验收。
- assignment：授权身份、分支和写入范围。
- current status、team status：派生视图，冲突时重新生成。

## 8. 多任务热索引

`.claw/current-status.md` 支持多个用户和多个聊天窗口的活跃 TASK。用生成器在锁内聚合并原子替换：

```bash
python3 scripts/generate-current-status.py /path/to/project/.claw --write
```

每个聊天只更新自己选中的 task status；热索引按字段事实源重建，不使用最后写入覆盖其他工作流。

## 9. 身份硬门禁

`collaboration_gate=true` 时，或 legacy 项目已有 developers/assignments/active assignment 时，任何源码、测试、运行配置、迁移、生成资产、FEAT 或 TASK 状态写入前必须运行 `scripts/dev-login.py`。

必须在当前会话返回 `allowed`。聊天声明、Git author、操作系统用户名、记忆、缓存或 `check-assignment.py` 都不能代替 SSH challenge-response。

只有项目经理能创建、撤销或扩大 developer/assignment。仓库不得保存 manager password、private key、token、secret 或 bearer token。

## 10. 写入与验证

- 时间使用 `YYYY-MM-DDTHH:MM:SSZ`。
- 只更新事实真正变化的文件；不要机械回写全部状态。
- 只有真实命令或检查运行后才能写 test report。
- 初始化、编号分配和热索引生成使用锁、临时文件和原子替换。
- 已存在且被用户修改的内容不得静默覆盖。
- 所有新建或明确重写的人类可读内容使用 manifest 的 `language`；机器协议值保持不变。
- README 和 AGENTS 保留受控 Skill 声明块；它们不是状态文件。
- `change_review=true` 且用户明确要求推送到测试环境时，按 change-review reference 使用 `push-test-environment.py`；source-branch-wins 只适用于测试环境。

校验：

```bash
python3 scripts/validate-state.py /path/to/project/.claw
```

无 manifest 时使用 legacy v4 profile；有 v5 manifest 时按 catalog、模式、模块和事件动态校验。失败时不得把 manifest 标记为 ready。

## 11. 禁止行为

- 使用其他项目状态目录或创建第二套状态树。
- 启动时读取全部状态、全部 spec 或禁用模块资料。
- 伪造测试、构建、部署、问题根因或完成状态。
- 初始化时创建虚假任务、空门禁目录或未触发事件文件。
- 自动重命名、批量改写或按 Git 时间推断 legacy 文件。
- 把 current status、task board 或 team status 写成长日志。
- 在多个文件独立维护同一事实。
- 用作者署名、聊天上下文或本地缓存绕过身份和 assignment。
