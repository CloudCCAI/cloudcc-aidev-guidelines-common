---
kind: feature-spec
schema_version: 5
feature_id: FEAT-bimo-001
work_type: feature_iteration
title: 引导式项目初始化与运行期管理重设计
status: verified
init_status: complete
init_completed_at: 2026-07-18T02:05:46Z
init_confirmed_by: Bimo
owner_role: shared
owner_slug: bimo
created_at: 2026-07-18T01:47:58Z
created_by: Bimo
created_by_slug: bimo
created_by_source: git_config_user_name
created_by_developer_id: none
contributors: Bimo
task_ids: TASK-bimo-001, TASK-bimo-002, TASK-bimo-003, TASK-bimo-004, TASK-bimo-005
related_decisions: none
related_issues: none
policy_version: 2
updated_at: 2026-07-18T03:10:11Z
updated_by: Bimo
---

# FEAT-bimo-001 - 引导式项目初始化与运行期管理重设计

## 文档状态

- 本文汇总本轮讨论中已经确认的产品需求、协议规则和实现方向。
- 用户已于 `2026-07-18T02:05:46Z` 确认按本文开始实现。
- 当前为 `verified + complete`：设计基线已确认，v5 实现和回归验证已完成。
- `TASK-bimo-001` 至 `TASK-bimo-005` 均已完成，历史文件继续按兼容规则保留。

## 1. 背景与目标

当前 Skill 已经被多个项目安装并产生了大量旧格式状态文件，但现有初始化方式主要是一次性复制固定模板，存在以下问题：

- 无法可靠区分“Skill 已安装”和“项目已完成初始化”。
- 未区分绿地项目与历史旧项目，容易要求旧项目一次性回填大量历史。
- 核心文件缺少逐文件问答、暂停恢复和初始化完成状态。
- 项目状态、多人门禁、代码合并申请等能力耦合加载，无法按项目需要启停。
- 新会话缺少对本次工作意图的轻量确认，需求讨论、设计和任务拆分之间没有稳定门槛。
- `current-status.md` 假设只有一个活跃任务，不支持同一用户多聊天窗口或多人并行。
- FEAT 和 TASK 使用项目全局编号，无法从名称识别创建者或负责人。
- 新规则不能直接强制改写已经存在的旧文件，否则会给已安装项目带来破坏性迁移。

本次重设计的目标是：

1. 建立可检测、可恢复、可验证的项目初始化流程。
2. 用引导式问答生成真实的项目核心状态，不生成虚假占位事实。
3. 将项目状态、协作门禁和代码评审拆成可配置模块，并只加载启用模块。
4. 建立“讨论 → FEAT 设计 → 用户确认 → TASK 拆分 → 开发验证”的运行期流程。
5. 支持多用户、多窗口和多个并行任务，同时保持热状态紧凑。
6. 对历史项目保持向后兼容，对新创建文件执行新规则。

## 2. 设计原则

- **引导而非猜测**：先从仓库读取可验证事实，再针对不确定信息提问。
- **用户最终确认**：AI 可以推荐项目类型、默认模块和推断结果，但不能替用户确认关键事实。
- **单一事实源**：每类事实只有一个权威文件，热文件只做索引和摘要。
- **渐进式加载**：按热、温、冷和功能开关加载，不在会话开始时读取全部资料。
- **按需创建**：核心基线文件在初始化阶段创建；事件型文件在真实事件发生时创建。
- **允许未知**：无法确认的信息标记为 `pending verification`，不得用占位任务或伪造命令补齐。
- **可暂停恢复**：每个核心文件单独记录初始化状态，问答中断后从第一个未完成文件继续。
- **幂等和非破坏性**：重复运行不得覆盖用户已经填写的内容，也不得自动重命名历史文档。
- **配置驱动**：初始化器与校验器共享状态目录清单和模块配置，避免规则漂移。
- **作者标识不等于授权**：Git/系统用户名用于文档归属；启用门禁时仍必须使用已验证的开发者身份。

## 3. Skill 启动与项目预检

### 3.1 “第一次启动”的定义

Skill 平台没有可靠的安装后生命周期钩子，因此“第一次启动”定义为：

> Skill 安装后，AI Agent 第一次在目标项目中加载本 Skill 并准备处理项目请求的会话。

`SKILL.md` 保持为轻量预检和路由入口；项目根 `README.md`、`AGENTS.md` 中的受控声明块负责提醒后续 Agent 在工作前加载 Skill。

### 3.2 预检顺序

每次会话先执行只读预检：

1. 检查项目唯一状态目录 `.claw/`。
2. 检查 `manifest.yaml` 是否存在及其 `initialization.status`。
3. 检查是否为尚未纳入新 manifest 的历史安装项目。
4. 检查启用的功能模块，只加载对应路由文档。
5. 检查核心文件的 `init_status`，发现未完成初始化时优先恢复。
6. 初始化完成后，才进入运行期会话意图确认。
7. 若身份硬门禁已启用，任何受保护写入前继续执行登录与 assignment 校验。

`.claw/` 是唯一项目状态目录，本文所有状态路径均以它为根目录；本地私密配置统一写入 `.claw-local/`。实现不再提供其他状态目录的探测、路由或兼容分支。

### 3.3 项目初始化判定

新版本以 `.claw/manifest.yaml` 为机器权威入口：

- 不存在状态目录：项目未初始化。
- 存在状态目录但不存在 manifest：视为历史安装项目，进入兼容预检，不自动重建或覆盖。
- manifest 为 `in_progress`：恢复未完成初始化。
- manifest 为 `ready`：初始化完成，进入运行期流程。
- manifest 为 `needs_review`：先处理失效、漂移或待确认项。

目录或某个旧文件单独存在，不能直接等价为“新协议初始化完成”。

## 4. Greenfield 与 Brownfield 判定

### 4.1 只读证据检查

AI 通过以下证据形成建议：

- 是否存在源代码、构建文件、依赖清单、数据库迁移、部署配置和测试。
- 是否存在有效 Git 历史、发布记录或长期维护文档。
- 是否已经有可运行入口、稳定目录结构、外部接口或生产配置。
- 仓库是否只有空目录、基础脚手架或尚未实现的占位内容。

### 4.2 确认规则

- AI 输出“建议判定 + 证据 + 不确定项”。
- 用户确认是 `greenfield` 或 `brownfield`，也可以纠正 AI 的建议。
- 判定结果写入 manifest；未经确认不得静默固化。

### 4.3 Greenfield 初始化

通过每次 1～3 个问题逐步收集：

- 项目目标、核心用户、成功标准、范围和约束。
- 计划使用的技术栈、总体架构、模块边界和数据方式。
- 主要目录、每个目录的职责、入口和禁止依赖。
- 构建、运行、测试、部署、环境变量和外部依赖。
- 是否已经有第一项工作；没有时保持空看板，不创建虚假的 `TASK-001`。

### 4.4 Brownfield 接管

- 先读取现有代码、配置、入口、构建和部署事实，再提问。
- 所有结论标为 `verified`、`inferred` 或 `pending verification`。
- 初始化时创建或完善 `docs/specs/PROJECT-BASELINE.md`，记录接管基线。
- 不要求一次性回填全部历史；只覆盖当前交付所需和影响较大的未知项。
- 基线稳定后转为冷资料；当前架构、目录和 DevOps 事实仍分别由核心状态文件维护，避免重复事实源。

## 5. 功能模块与开关

初始化时询问用户是否启用以下模块：

| 模块 | 开关 | 建议默认值 | 作用 | 关闭后的行为 |
|---|---|---:|---|---|
| 项目状态管理 | `project_state` | `on` | 项目初始化、会话意图、FEAT/TASK、状态和渐进加载 | 不创建、不加载项目状态文档，也不强制运行 FEAT/TASK 流程 |
| 多人协作门禁 | `collaboration_gate` | `off` | 管理者、开发者身份、assignment、并行开发授权和本地登录 | 不加载门禁文档，不创建 `developers/`、`assignments/` 或本地身份配置 |
| 代码合并申请 | `change_review` | `off` | Codeup/GitHub 等平台的 change request、评审规则和合并检查 | 不加载平台文档，不创建评审配置 |

通用规则：

- `manifest.yaml` 是始终存在的最小控制面，不属于可关闭的业务状态文件。
- 用户可在初始化后重新配置开关；关闭模块只停止后续加载和执行，不删除历史资料。
- 禁用模块的参考文档、模板、目录和脚本说明不得进入当前上下文。
- 启用 `change_review` 时继续询问平台、目标分支、评审人、必需检查和创建策略，只加载选中平台资料。
- 启用 `collaboration_gate` 时继续询问管理者、成员登记、授权范围和登录策略。
- `collaboration_gate` 的 assignment、登录和授权以 TASK 为边界，因此第一版要求 `project_state=on`。用户选择“门禁开、项目状态关”时，配置器必须说明依赖，并让用户选择开启项目状态或关闭门禁，不能静默修改开关。
- `change_review` 可以独立于项目状态工作；项目状态开启时增加 FEAT/TASK 追踪，门禁开启时再增加 identity/assignment 检查。
- `project_state=off` 时跳过 Greenfield/Brownfield 内容问答、核心状态文件和运行期 FEAT/TASK 流程，只初始化 manifest 以及合法启用的非状态模块配置。

### 5.1 manifest 建议结构

```yaml
schema_version: 5
skill_version: 5.0.0
project_mode: greenfield | brownfield | not_applicable
initialization:
  status: in_progress | ready | needs_review
  started_at: timestamp
  completed_at: timestamp | none
  confirmed_by: user | none
modules:
  project_state: true
  collaboration_gate: false
  change_review: false
module_config:
  collaboration_gate: none | path
  change_review: none | path
compatibility:
  legacy_documents_allowed: true
  legacy_index_path: none | .claw/legacy-document-index.yaml
  new_document_policy_version: 2
  policy_effective_at: timestamp
```

`not_applicable` 只允许在 `project_state=false` 时使用，表示已经按用户选择跳过项目类型和项目状态基线问答；`project_state=true` 时仍必须是 `greenfield` 或 `brownfield`。实际实现由统一 schema/catalog 定义字段，示例不作为重复事实源。

## 6. 核心文件初始化

### 6.1 文件级初始化状态

每个由初始化流程创建的核心内容文件都包含：

```yaml
init_status: not_started | in_progress | awaiting_confirmation | complete | needs_review
init_completed_at: timestamp | none
init_confirmed_by: username | developer_id | none
```

状态含义：

- `not_started`：文件存在但尚未开始引导。
- `in_progress`：已回答一部分问题，可以继续恢复。
- `awaiting_confirmation`：AI 已形成完整草稿，等待用户确认。
- `complete`：初始化基线已确认；以后仍可正常演进，并不代表文件冻结。
- `needs_review`：仓库事实变化、校验失败或关键未知项导致内容需要复核。

文件状态是权威事实；manifest 中的总体初始化状态由这些文件和已启用模块聚合得出。尚未触发、因模块关闭而不存在的文件，不计为未完成。

### 6.2 核心文件、问题和时机

| 文件 | 温度 | 创建/完成时机 | 引导内容 |
|---|---|---|---|
| `.claw/manifest.yaml` | 机器热 | 第一个创建，最后置为 `ready` | 项目模式、模块开关、兼容策略、初始化聚合状态 |
| `.claw/current-status.md` | 热 | 启动时创建最小骨架，所有基线确认后生成正式索引 | 当前阶段、多个活跃工作流、下一步和按需读取指针 |
| `.claw/goals.md` | 温 | 确认项目模式后 | 目标、用户、范围、成功标准、约束和非目标 |
| `.claw/decisions.md` | 温 | goals 后 | 当前 `ARCHITECTURE` 模块和 ADR 决策历史 |
| `.claw/directory-map.md` | 温 | 架构初稿后 | 目录职责、入口、模块边界、允许/禁止依赖 |
| `.claw/devops.md` | 温 | 目录与运行方式清楚后 | 已验证的构建、启动、测试、部署、环境和依赖 |
| `.claw/collaboration-config.yaml` | 模块温 | 仅 `collaboration_gate=on` 时 | 公开的身份绑定、管理者、assignment、登录和签名策略，不存 secret |
| `.claw/review-config.yaml` | 模块温 | 仅 `change_review=on` 时 | 平台、目标分支、评审和检查规则，不存 token |
| `.claw/task-board.md` | 温 | 项目状态模块基线完成后 | 初始化为空的有效看板，不制造占位任务 |
| `docs/specs/PROJECT-BASELINE.md` | 冷 | 仅 Brownfield 初始化时 | 旧项目基线和 verified/inferred/pending 事实 |

多人门禁配置文件只在 `collaboration_gate=on` 后按真实成员和授权事件创建，不预建空 `developers/`、`assignments/` 目录。

项目根 `README.md`、`AGENTS.md` 中的受控声明块是 Agent 指令锚点，不是项目状态文件，不使用内容文件的 `init_status`，也不计入核心文件完成度。

### 6.3 `decisions.md` 中的 ARCHITECTURE 模块

不再新增独立 `ARCHITECTURE.md`。架构信息加入 `.claw/decisions.md` 的固定 `## ARCHITECTURE` 模块，内容至少包括：

- 系统类型和主要技术栈。
- 总体架构风格和关键运行流程。
- 模块、服务、层次及其边界。
- 数据存储、数据流和一致性策略。
- 外部系统和第三方依赖。
- 构建、部署和运行拓扑的架构视角。
- 性能、安全、可用性、合规等非功能约束。
- `verified`、`inferred`、`pending verification` 标记。
- 相关 ADR 链接。

`ARCHITECTURE` 表示“当前有效的架构快照”；ADR 表示“为什么做出某项选择以及历史如何演进”。初次初始化可以在没有 ADR 的情况下完成，但不能把推断写成已验证事实。目录职责继续由 `directory-map.md` 维护。

由于 `decisions.md` 同时承载持续追加的 ADR 和可初始化的 ARCHITECTURE 模块，frontmatter 还应单独记录架构子模块状态，例如：

```yaml
architecture_init_status: awaiting_confirmation | complete | needs_review
architecture_reviewed_at: timestamp | none
architecture_confirmed_by: username | developer_id | none
```

文件级 `init_status` 表示该核心文件的首次建档是否完成；`architecture_init_status` 精确表示其中架构基线的完成度。新增 ADR 不会把已经确认的架构初始化状态重置为未开始，但推翻当前架构的 ADR 应将其标为 `needs_review`。

### 6.4 引导执行规则

- 每轮只问 1～3 个关联问题，避免一次抛出长问卷。
- 优先从仓库证据预填，并显示证据来源和置信状态。
- 每次回答后持久化进度和待确认项。
- 中断后从第一个非 `complete` 文件、该文件第一个未回答问题恢复。
- 重复运行只补充缺失字段，不覆盖用户已确认内容。
- “完成初始化”允许存在明确标记的待验证事实，但不允许未解释的模板占位符。
- 所有核心文件完成并通过校验后，先请求最终确认，再把 manifest 置为 `ready`。

### 6.5 推荐初始化顺序

```text
manifest(in_progress)
  → 询问模块开关并校验依赖
  ├─ project_state=on
  │    → 基于证据建议并由用户确认 Greenfield/Brownfield
  │    → Brownfield baseline（按需）
  │    → goals
  │    → decisions / ARCHITECTURE
  │    → directory-map
  │    → devops
  │    → 已启用模块配置
  │    → 空 task-board
  │    → 生成 current-status
  └─ project_state=off
       → 只生成合法启用的非状态模块配置
  → 动态校验
  → 用户最终确认
  → manifest(ready)
```

## 7. 热、温、冷与按需创建

温度是加载策略，不强制对应物理目录：

- **机器热**：`manifest.yaml`，用于路由和校验，不向模型展开全部内容。
- **上下文热**：`current-status.md`，每次会话先读，保持少于 60 行。
- **温**：task board、选中的任务状态、选中的 FEAT、相关 ARCHITECTURE/ADR、directory map、当前 issue/test/devops、已启用模块配置。
- **冷**：goals 的稳定部分、ADR 历史、Brownfield baseline、archive、已完成 FEAT/TASK。

以下文件不在项目初始化时创建，必须由真实事件触发：

| 文件 | 首次创建事件 |
|---|---|
| `docs/specs/FEAT-<user>-<seq>-<description>.md` | 开发类工作讨论完成，形成待确认设计 |
| `.claw/tasks/TASK-<user>-<seq>-<description>.md` | FEAT 已确认并开始任务拆分，或非 FEAT 工作需要持久任务 |
| `.claw/issue-list.md` | 首次发现 bug、风险或阻塞 |
| `.claw/test-report.md` | 首次真实执行验证 |
| `.claw/task-archive.md` | 首次归档完成/取消任务 |
| `.claw/integration-queue.md` | 首次出现真实并行分支和集成顺序 |
| `.claw/developers/*` | 门禁启用后登记真实成员 |
| `.claw/assignments/*` | 门禁启用后产生真实授权 |
| `.claw-local/identity.json` | 本地登录成功后缓存公开元数据和私钥路径 |

`team-status.md` 是管理者查询时生成的派生视图，不参与手工初始化。安装包内的 FEAT/baseline 模板由 Skill 直接渲染，不再复制 `_feature-spec-template.md`、`_project-baseline-template.md` 到目标项目。

## 8. 每个新 AI 会话的运行期流程

### 8.1 意图确认是建议性引导

每次打开新的 AI 聊天：

- 如果用户已经清楚说明要做什么，直接复述理解并继续，不重复问固定问题。
- 如果目标不清楚，用开放式问题确认本次工作；可以提示“新需求开发、老功能迭代、修改 bug”等常见例子。
- 这些例子不是封闭菜单，也不是强制分类。用户可以进行分析、状态查询、重构、文档、测试、发布、部署、评审、项目管理或其他操作。

建议记录：

```yaml
session_intent: 用户原始目标的稳定摘要
work_kind: new_feature | feature_iteration | bugfix | refactor | docs | test | release | deploy | review | investigation | project_management | custom
requires_feat: true | false
```

`session_intent` 保留用户原意；`work_kind` 仅用于路由，允许扩展，不能反向覆盖用户目标。

### 8.2 哪些工作需要 FEAT

通常需要 FEAT：

- 新需求或新功能。
- 既有功能的非平凡迭代。
- bug 修复设计及其回归范围。
- 跨模块修改、API/数据结构变更、非平凡重构。
- 预计跨会话、跨 Agent 或需要长期交接的实现。

简单查询、只读分析、小型独立维护等可以不创建 FEAT；由路由规则结合风险和用户意图判断。

### 8.3 开发类工作门槛

```text
确认本次意图
  → 与用户讨论现状、目标和约束
  → 讨论完整性检查
  → 创建 FEAT 设计草稿
  → 用户确认 FEAT
  → 创建并拆分 TASK
  → 开发
  → 真实验证
  → 评审/合并/关闭
```

“讨论完成”至少意味着已经明确：

- 工作类型和用户真正目标。
- 当前行为与目标行为。
- In Scope 与 Out Of Scope。
- 验收标准。
- 技术、时间、兼容和安全约束。
- 已知风险、未决问题以及用户对方案的确认。

在 FEAT 确认前可以进行只读分析和方案探索；需要 FEAT 的工作不得先实现后补设计。若用户要开始一项新工作而已有活跃工作，应显示现有工作，并让用户选择继续、并行、暂停或取消，不能静默覆盖。

### 8.4 Bug 信息的事实源

- `issue-list.md` 保存现象、严重级别、影响、根因状态和阻塞信息。
- FEAT 保存修复方案、变更范围、验收标准和回归策略。
- 两者通过 ID 互相引用，不重复维护同一事实。

## 9. FEAT 文件命名、作者和个人编号

### 9.1 新文件格式

```text
FEAT-<username>-<personal-feature-number>-<short-description>.md
```

例如：

```text
FEAT-xuhm-001-user-login.md
FEAT-lisi-001-order-export.md
```

字段含义：

1. `FEAT`：Feature，表示功能/设计规格文档。
2. `username`：创建者的稳定文件名 slug。
3. `personal-feature-number`：该用户自己的三位递增编号，从 `001` 开始。
4. `short-description`：简短、稳定、可读的功能描述。

规范 ID 为 `FEAT-<username>-<number>`，description 只属于文件路径，不属于稳定 ID。

### 9.2 用户名解析顺序

1. 门禁启用时，使用已登录开发者的稳定 slug，并在 frontmatter 记录 `developer_id`。
2. 否则使用 `git config user.name`。
3. Git name 不可用时使用操作系统用户名。
4. 仍不可用或归一化存在歧义时，让用户确认。

显示名与文件名 slug 分开保存。slug 使用小写字母、数字和连字符等安全字符；Git/系统用户名只负责归属，不构成门禁授权。

### 9.3 个人递增与并发

- 每个用户独立拥有 `001`、`002`……序列，不使用项目全局序号。
- 同一用户的所有新式 FEAT 文件参与该用户序列；旧式 `FEAT-001` 不参与。
- 编号一旦分配不得复用，即使文件归档或取消。
- 分配脚本必须在锁内扫描、计算并以排他方式创建，防止同一用户的多个聊天窗口取得相同编号。
- 多位贡献者写入 `contributors`；文件名保留原创建者，不因转交而重命名。

### 9.4 建议 frontmatter

```yaml
kind: feature-spec
feature_id: FEAT-xuhm-001
work_type: new_feature | feature_iteration | bugfix | custom
title: 用户登录
status: draft
init_status: awaiting_confirmation
created_by: XuHM
created_by_slug: xuhm
created_by_source: developer_identity | git_config_user_name | os_user | user_confirmed
created_by_developer_id: DEV-001 | none
contributors: XuHM
task_ids: none
```

## 10. TASK 文件命名和归属

所有新任务，无论来自 FEAT 还是其他工作，都使用：

```text
TASK-<username>-<personal-task-number>-<short-description>.md
```

示例：

```text
TASK-xuhm-001-implement-login-api.md
TASK-lisi-001-fix-order-timeout.md
```

规则：

- 规范 ID 为 `TASK-<username>-<number>`。
- 每位用户的所有任务类型共享一个个人 TASK 序列，编号不得复用。
- `task_type` 可为 feature、iteration、bugfix、refactor、documentation、test、release、deployment、investigation、project_management 或 other。
- FEAT 派生任务记录 `feature_id`；非 FEAT 任务明确记录 `feature_id: none`。
- username 建议表示初始负责人命名空间；`created_by` 单独记录实际创建者。
- 管理者为李四创建任务时可使用 `TASK-lisi-003`，同时记录 `created_by: manager`、`assignee: lisi`。
- 后续转交只更新 `assignee` 和历史，不重命名文件或 ID。
- task board、current status、assignment 和 FEAT 必须引用完整新 ID。
- ID 分配同样使用锁和排他创建，支持多个聊天窗口并发。

## 11. 多活跃任务与多聊天窗口

`current-status.md` 必须从单任务模型升级为多工作流热索引：

```yaml
active_task_count: 2
active_tasks:
  - TASK-xuhm-001
  - TASK-lisi-001
```

正文使用紧凑表格展示：用户、FEAT、TASK、工作类型、状态、分支和下一步。规则如下：

- `.claw/tasks/TASK-*.md` 对执行进展、实际工作状态、变更文件、验证证据、阻塞、下一步和交接负责。
- `.claw/task-board.md` 对任务是否进入队列、优先级、依赖、协调状态以及 spec/task/assignment 指针负责。
- assignment 对授权人、被授权人、分支和可写范围负责；FEAT 对需求、设计和验收标准负责。
- `current-status.md` 是从上述事实源生成的热索引，本身不拥有这些事实。冲突时按字段归属修复，而不是让任一文件全局覆盖其他文件。
- task board 的协调状态可以暂时落后于任务文件的执行状态；热索引中的执行状态取任务文件，排队和依赖信息取 task board。
- current status 只保留活跃状态并继续少于 60 行；完整协调列表保留在 task board。
- 每个聊天只更新自己选中的任务文件；随后通过锁和原子替换重新生成 current status。
- 新会话先读 current status，再只加载选中用户/任务关联的 FEAT、issue、decision、assignment，不展开其他任务详情。
- 平台提供可靠 conversation/workstream ID 时可作为辅助字段，但协议不能依赖该 ID 才能工作。
- 项目可以保留总体 phase；每条工作流另外拥有自己的 stage。

## 12. 历史项目与旧文件兼容

### 12.1 基本策略

- 已经存在的 `FEAT-001-*`、`TASK-001` 和旧版核心文件全部 grandfather，不强制重命名、补字段或改引用。
- 新版本生效后创建的文件必须使用带用户名的新格式。
- 旧格式和新格式可以长期共存，读取器和交叉引用必须同时支持。
- 现有 `current-status.md` 可以继续保持旧结构；只有用户选择升级或需要多任务能力时，才进行显式、非破坏性升级。
- 兼容读取器必须同时解析旧版单值 `active_task` 和新版 `active_tasks` 列表，并统一投影为内部工作流集合。
- 不使用 Git 文件时间或 commit 时间判断文件属于新旧协议。

### 12.2 新旧边界登记

历史项目第一次使用新版本时，创建非破坏性的 `.claw/legacy-document-index.yaml`，登记当时已存在的旧路径和 ID，并在 manifest 记录：

```yaml
legacy_documents_allowed: true
legacy_index_path: .claw/legacy-document-index.yaml
new_document_policy_version: 2
policy_effective_at: timestamp
```

校验规则：

- legacy index 中登记的文件按旧 schema 校验。
- 新格式文件按新 schema 校验。
- policy 生效后新建的旧格式文件报错。
- 尚未建立新 manifest 的项目继续使用旧校验模式，并可输出迁移建议，不能直接失败。
- FEAT/TASK 交叉引用同时接受旧 ID 和新 ID。
- 新用户个人序列从 `001` 开始，历史全局编号不能推断为任何用户所有。

### 12.3 可选迁移

历史文件批量改名、补字段和更新引用只允许在用户明确选择迁移后执行；迁移必须生成 ID/path 映射、先校验后提交，并支持回滚。默认路径永远是兼容读取而不是自动重写。

## 13. Skill 包的实现分层

### 13.1 轻量路由层

`skill/SKILL.md` 只保留：

- 项目预检入口。
- 初始化恢复优先级。
- 会话意图确认规则。
- 模块路由和必须遵守的安全门槛。
- 何时读取对应 reference、运行脚本或渲染模板。

详细 schema、问卷、平台差异和示例移到按需资源，避免每次加载全部协议。

### 13.2 建议 references

```text
references/
├── onboarding.md
├── state-model.md
├── modules/
│   ├── project-state.md
│   ├── collaboration-gate.md
│   └── change-review.md
└── platforms/
    ├── codeup.md
    └── github.md
```

### 13.3 建议模板

```text
templates/
├── core/
│   ├── manifest.yaml
│   ├── current-status.md
│   ├── goals.md
│   ├── decisions.md
│   ├── directory-map.md
│   ├── devops.md
│   └── task-board.md
├── project-state/
│   ├── feature-spec.md
│   ├── task-status.md
│   ├── issue-list.md
│   ├── test-report.md
│   └── task-archive.md
├── collaboration-gate/
└── change-review/
```

模板保留在 Skill 包内，事件发生时直接渲染到项目，避免目标项目中长期存在未使用模板。

### 13.4 建议确定性脚本

- `project-preflight`：状态目录、manifest、legacy、项目模式证据和门禁预检。
- `project-onboarding`：问答 checkpoint、逐文件生成、恢复和最终确认。
- `configure-modules`：模块开关、平台配置和重新配置。
- `allocate-document-id`：解析作者、锁定并分配 FEAT/TASK 个人编号。
- `generate-current-status`：从活跃任务原子生成多任务热索引。
- `snapshot-legacy-documents`：登记新规则生效前的历史文件。
- `validate-state`：根据 manifest、状态 catalog、模块开关和 legacy index 动态校验。

现有 `init-state.sh` 可先保留为兼容包装器并给出弃用提示，不能继续作为新协议唯一事实源。

本版提供的是显式 `adopt` 与不可覆盖的 legacy boundary，不提供批量改名迁移命令。未来若用户明确要求批量迁移，必须另行设计 path/ID mapping 和回滚机制。

### 13.5 状态 catalog

新增统一的机器可读 catalog/schema，至少描述：

- 文件路径或路径模式。
- 所属模块。
- core/event/derived 类型。
- 初始化顺序和前置依赖。
- 温度和加载触发条件。
- 必需字段、状态枚举和兼容版本。
- 是否计入总体初始化完成度。

初始化器、路由器和校验器共同读取 catalog，避免脚本固定要求八个文件、模板却演进为另一套规则。

## 14. 校验、失败处理与安全

### 14.1 动态校验

校验器必须验证：

- manifest 与启用模块配置一致。
- 只要求当前项目模式、启用模块和已触发事件对应的文件。
- 每个核心文件的初始化状态、时间和确认人合法。
- `complete` 文件不存在未解释占位符。
- current status 中的任务都存在，计数和状态一致。
- 新式 FEAT/TASK 文件名、ID、作者和个人序号一致。
- policy 生效后的旧式新文件被拒绝，登记 legacy 文件继续通过。
- 禁用模块没有被初始化器或路由器加载。
- review 配置不包含 token；assignment 和仓库状态不包含 secret。

### 14.2 失败和恢复

- 写入使用临时文件 + 原子替换；编号分配和 current status 聚合使用项目内锁。
- 单个文件生成失败时保持 manifest 为 `in_progress`，保存 checkpoint，不把半成品标记为 complete。
- 校验失败时把受影响文件或 manifest 标为 `needs_review`，给出精确修复项。
- 重试必须幂等，不删除用户内容。
- 并发写冲突时停止自动覆盖，展示两边差异并请求协调。

### 14.3 身份与平台秘密

- Git/OS 用户名只用于署名和命名空间。
- 门禁启用时，源码、spec、任务等受保护写入仍必须通过 SSH challenge-response 和 assignment。
- Codeup/GitHub token 只保存在本地忽略文件或环境变量，不进入 manifest、review config、日志或设计文档。

## 15. 测试场景

实现后至少覆盖：

1. 空仓库 Greenfield 初始化、逐文件问答和最终确认。
2. 有代码的 Brownfield 证据分析、用户纠正和最小 baseline。
3. 初始化中断后从正确问题恢复。
4. 重复初始化不覆盖已确认事实。
5. 三个模块的所有开关组合及禁用文档不加载。
6. change review 分别选择 Codeup 和 GitHub 时只加载对应平台资料。
7. collaboration gate 关闭时不创建空门禁目录，开启时执行登录与授权。
8. 没有首个任务时生成空看板，不出现虚假 TASK。
9. 两位用户分别取得自己命名空间中的 `FEAT-<user>-001` / `TASK-<user>-001`。
10. 同一用户两个窗口并发分配 ID，不产生重复编号。
11. 多用户、多窗口、多活跃任务正确聚合 current status。
12. task board、单任务事实与热索引冲突时按字段事实源重建。
13. legacy v4 项目不迁移也能继续读取和校验。
14. legacy 与新式 FEAT/TASK 交叉引用共存。
15. policy 生效后创建旧格式文件被拒绝。
16. 显式 adoption 建立 immutable legacy index，且既有文件哈希保持不变。
17. manifest/catalog 驱动的动态校验不会再次固定要求未触发文件。
18. 未执行真实测试时不会生成通过记录。

## 16. 验收标准

- 首次加载 Skill 能可靠判断未初始化、初始化中、已完成或历史安装状态。
- AI 能基于证据建议 Greenfield/Brownfield，并由用户确认。
- 用户可以独立启停项目状态、协作门禁和代码合并申请模块。
- 未启用模块的文档、模板说明和配置不被加载或创建。
- 每个核心文件通过小批量问答完成，具有可恢复的初始化状态。
- `decisions.md` 包含当前 ARCHITECTURE 快照和 ADR 历史，二者职责清楚。
- 新会话的三类常见工作只是建议示例，不限制其他操作。
- 开发类工作遵循讨论、FEAT 确认、TASK 拆分后再实现的门槛。
- 新 FEAT 和所有新 TASK 都带用户名，并按用户分别递增。
- current status 可以同时索引多个用户和多个聊天窗口的活跃任务。
- 旧项目和旧文件无需强制迁移；新文件严格遵守新规则。
- 热/温/冷加载、事件创建和单一事实源规则可由脚本与校验器验证。
- 初始化和运行期写入在中断、重试和并发条件下保持幂等、可审计、非破坏性。

## 17. 范围外

- 本规格不自动迁移或重命名任何现有 FEAT、TASK、current status 或看板记录。
- 本规格不选择唯一的远程代码托管平台；平台由模块配置决定。
- 本规格不把聊天平台的 conversation ID 作为唯一并发标识。

## 18. 任务拆分策略（确认后执行）

已创建以下正式任务：

1. `TASK-bimo-001`：manifest、状态 catalog、项目预检、模块开关、可恢复初始化和核心模板。
2. `TASK-bimo-002`：作者解析、FEAT/TASK 个人编号、事件模板和 legacy snapshot。
3. `TASK-bimo-003`：多任务 current status 聚合与相关消费者兼容。
4. `TASK-bimo-004`：v4/v5 双栈解析、动态校验、legacy policy 和安全检查。
5. `TASK-bimo-005`：Skill 路由、状态模型、references、示例、回归验证和版本发布准备。

## 19. 发布与兼容建议

该设计会改变新项目的初始化模型、文件清单、命名方式和会话流程，已将 `skill/SKILL.md` 的 `metadata.skill_version` 升级为 `5.0.0`。旧项目继续使用 legacy profile，只有显式 adoption 才建立 v5 边界。

## 20. 确认记录

- `2026-07-18T02:05:46Z`：用户确认“按照这个设计开始实现”。
- 确认人：`Bimo`。
- `2026-07-18T03:10:11Z`：五个实现任务和发布前验证完成。
- 当前阶段：`verified`，等待用户决定是否提交或发布。

## 21. 实现与验证结果

- v5 路由、manifest/catalog、模块开关、逐文件初始化、Greenfield/Brownfield、ARCHITECTURE、个人编号、多任务热索引、显式 legacy adoption 和双栈校验已实现。
- 三个独立前向测试分别覆盖 Greenfield 全流程、block-mapping legacy adoption、模块组合与禁用资源不加载；报告的问题已全部修复并回归通过。
- 自动化回归：`67` 项单元测试全部通过。
- 状态 fixture：本仓库 legacy v4、Greenfield v5、Brownfield v5、sample legacy v4 全部通过对应校验。
- 发布质量：Python 编译、Shell 语法、GitHub workflow YAML/Shell、Skill frontmatter、JSON、旧目录残留和 `git diff --check` 均通过。
