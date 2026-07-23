---
title: State Model Reference
version: 5.0.5
---

# State Model Reference

本文定义 `cc-aidev-guidelines-common` schema v5 的详细状态模型。`SKILL.md` 负责路由；本文负责字段语义、事实源、兼容和冲突规则。

## 目录

- 协议 profile、manifest、项目模式与模块
- 文件初始化状态、catalog、核心/事件文件
- FEAT/TASK 命名、个人序号与 legacy index
- 字段级事实源、热温冷和会话流程
- 协作门禁、change review、校验与原子恢复

## 1. 总体原则

1. 项目状态目录固定为 `.claw/`，本地私密配置固定为 `.claw-local/`。
2. `.claw/manifest.yaml` 是 v5 的机器控制面；内容事实仍由各自文件负责。
3. 每个事实只有一个权威来源，current status 和 team status 只做派生视图。
4. 核心文件在初始化时创建；事件文件只在真实事件发生时创建。
5. 所有推断与待验证内容必须显式标记，不得伪造测试、构建或部署事实。
6. 热、温、冷表示加载策略，不强制对应物理目录。
7. 旧文件不强制迁移；新文件必须遵守 policy 生效后的 v5 命名和字段规则。
8. Git/OS 用户名只用于文档归属，不构成多人门禁授权。
9. Skill 新写入的人类可读内容固定使用简体中文；manifest 的 `language` 保留为写入策略与历史兼容标记，机器字段、枚举、ID、路径、命令和原始证据保持协议原值。
10. `.claw/devops.md` 是运维事实源；根目录 `DevOps/` 是按客户环境拆分的可执行资产目录，两者必须引用一致。
11. `docs/help` 保存用户手册，`docs/design` 保存详细功能与流转设计；所有规范文档统一使用小写 `docs` 根目录。
12. `docs/design` 与 `docs/specs` 中每份 Markdown 都有同目录、同 basename HTML；Markdown 是唯一事实源，HTML 只是可重建的人类阅读派生视图。

## 2. 协议 profile

### `manifest_v5`

`.claw/manifest.yaml` 存在且 `schema_version: 5` 时启用。初始化器、路由器和校验器按 manifest、catalog、模块开关和事件触发动态工作。

### `legacy_v4`

`.claw/` 已存在但没有 manifest 时启用。继续读取和校验原有核心文件、旧 FEAT/TASK 和单活跃任务结构，不自动重命名、补字段或创建 manifest。

首次显式采用 v5 时，先生成 `.claw/legacy-document-index.yaml`，再写入 policy 生效时间。不得使用 Git 时间判断新旧。

## 3. manifest

manifest 至少表达以下逻辑字段：

```yaml
schema_version: 5
skill_version: 5.0.5
language: zh-CN
project_mode: pending | greenfield | brownfield | not_applicable
initialization:
  status: in_progress | ready | needs_review
  started_at: timestamp
  completed_at: timestamp | none
  confirmed_by: username | developer_id | none
modules:
  project_state: true | false
  collaboration_gate: true | false
  change_review: true | false
module_config:
  collaboration_gate: path | none
  change_review: path | none
compatibility:
  legacy_documents_allowed: true
  legacy_index_path: .claw/legacy-document-index.yaml | none
  new_document_policy_version: 3
  policy_effective_at: timestamp
```

实现可以使用受限 YAML 子集，但字段语义必须与 catalog 一致。

状态规则：

- `in_progress`：初始化已开始或正在恢复。
- `ready`：当前模式、已启用模块的核心文件均完成并通过校验，且用户已最终确认。
- `needs_review`：核心事实漂移、引用失效或校验失败。

manifest 的总体状态由文件状态聚合，不得反向覆盖文件状态。

Skill 5.0.3 起，新 manifest 固定使用 `language: zh-CN`，不再提供语言选择或重配置。缺少该字段的早期 v5 manifest 按历史 `en` 读取；5.0.1/5.0.2 的 `en`、`zh-CN` 和未完成初始化中的 `pending` 继续可读，`pending` 在下一次明确的初始化写操作中归一为 `zh-CN`。v4 文件不补字段，既有项目文档不自动翻译或覆盖；以后新增或明确重写的人类可读内容统一使用中文。

`project_mode: pending` 只允许在 `project_state=true` 且初始化尚未 ready 时作为可恢复检查点；`project_mode: not_applicable` 仅在 `project_state=false` 时合法，表示按用户选择跳过项目类型和项目状态基线问答。进入 ready 前，启用项目状态的模式必须由用户确认为 `greenfield` 或 `brownfield`。

## 4. 项目模式

### Greenfield

当前作用域没有必须兼容的既有用户行为、数据、API 或部署契约。引导用户确认目标、架构、目录、运行方式和第一项真实工作。没有工作时保持空 task board。

### Brownfield

必须理解并保护既有实现或契约。先读取代码、配置、入口和构建事实，再提问；创建 `docs/specs/PROJECT-BASELINE.md`，区分：

- `verified`
- `inferred`
- `pending verification`

不要求一次性回填全部历史。baseline 稳定后属于冷资料；当前架构、目录和 DevOps 事实仍由核心文件负责。

AI 只能建议模式，用户最终确认。

## 5. 模块

### `project_state`

管理核心状态、会话意图、FEAT、TASK、多任务热索引和事件文件。建议默认开启。

关闭时只保留 manifest 和合法启用的非状态模块配置，不创建或加载项目状态文件，也不强制 FEAT/TASK 流程。

### `collaboration_gate`

管理 manager/developer 身份、assignment、登录和并行授权。默认关闭，要求 `project_state=true`。启用模块本身不创建空 developers/assignments 目录。

启用后创建并引导确认 `.claw/collaboration-config.yaml`，只保存公开的身份绑定、管理者、assignment、登录和签名策略。developer 与 assignment 文件仍由真实登记和授权事件创建。

### `change_review`

管理 Codeup/GitHub change request 和评审配置。默认关闭，可以独立于 `project_state` 启用；与项目状态或门禁同时启用时增加对应追踪和授权检查。

关闭模块不删除历史资料，只停止后续加载和执行。

## 6. 文件初始化状态

所有 v5 核心内容文件包含：

```yaml
kind: goals
schema_version: 5
init_status: not_started | in_progress | awaiting_confirmation | complete | needs_review
init_completed_at: timestamp | none
init_confirmed_by: username | developer_id | none
updated_at: timestamp
updated_by: username | developer_id | ai
```

- `not_started`：骨架已存在，尚未开始问答。
- `in_progress`：已保存部分答案。
- `awaiting_confirmation`：草稿完整，等待用户确认。
- `complete`：首次基线已确认，文件仍可继续演进。
- `needs_review`：事实漂移、校验失败或关键未知项需要复核。

不存在的事件文件不计为未完成；关闭模块对应文件不计入 ready。

## 7. 状态 catalog

`state-catalog.json` 是初始化器和校验器共享的机器清单。每个条目至少定义：

- path 或 pattern
- kind 和 schema version
- module
- `core` / `event` / `derived`
- temperature
- create trigger
- init order 与依赖
- required fields 和状态枚举
- 是否计入 ready
- 可选的外部资产契约（根路径、环境字段、每环境必需文件和生效 Skill 版本）
- 可选的 `project_assets`（普通项目文档路径、规范中文模板、模块、模式和生效版本）
- v4/v5 compatibility profile

脚本不得再各自硬编码一套固定八文件清单。

## 8. 核心文件

### 项目文档资产

Skill 5.0.2 起，启用 `project_state` 且模式为 Greenfield/Brownfield 的新项目必须包含：

- `docs/help/README.md`：产品帮助、使用手册和常见问题的职责说明与索引。
- `docs/design/README.md`：功能、交互、业务流转、状态变化、异常路径、接口与数据设计的职责说明与索引。

两个文件依据规范中文模板生成，只在缺失时创建，已有内容不得覆盖。它们是普通项目资产，不使用状态文件 frontmatter，也不单独计入核心文件初始化问答；catalog 的 `project_assets` 声明生效版本、模块、模式、路径和模板。较早 v5 与 legacy 项目不强制回填。

FEAT 是范围、关键设计决策、任务和验收事实源；`docs/design/` 承载需要长期展开的详细设计并由 FEAT 引用。`docs/help/` 只描述面向用户的确认行为，不应成为内部需求或未验证实现的事实源。

Skill 5.0.5 起，初始化器创建 `docs/design/README.md` 后同步创建 `docs/design/README.html`。`docs/help/README.md` 不在本规则范围内。

### `.claw/current-status.md`

上下文热入口，是派生索引而非任务事实源。v5 frontmatter 至少包含：

```yaml
kind: current-status
schema_version: 5
active_task_count: 0
active_tasks: []
phase: bootstrap
next_action: confirm project baseline
updated_at: timestamp
updated_by: generate-current-status
```

正文用紧凑表格展示用户、FEAT、TASK、工作类型、执行状态、分支和下一步。保持少于 60 行，不记录会话日志、变更文件、长验证证据或完整问题详情。

### `.claw/goals.md`

目标、用户、In/Out Scope、成功标准、里程碑、约束和非目标的事实源。只在产品意图变化时更新。

### `.claw/decisions.md`

同时承载当前架构快照和 ADR 历史。

固定 `## ARCHITECTURE` 至少记录：系统类型、技术栈、架构风格、模块边界、数据、外部依赖、部署、非功能约束、事实置信状态和相关 ADR。

额外 frontmatter：

```yaml
architecture_init_status: not_started | in_progress | awaiting_confirmation | complete | needs_review
architecture_reviewed_at: timestamp | none
architecture_confirmed_by: username | developer_id | none
```

ARCHITECTURE 表示当前有效快照；ADR 表示为什么选择以及历史如何变化。ADR 记录 context、options、choice、why、consequences 和 verification。首次初始化不要求已有 ADR。

### `.claw/directory-map.md`

顶层和关键目录职责、入口、模块边界、允许依赖和禁止依赖的事实源。不要把目录职责重复写入 baseline 或 current status。

### `.claw/devops.md`

构建、运行、测试、部署、环境、依赖服务和运维知识的事实源。命令必须已验证，或明确标记 `pending verification`。

Skill 5.0.2 起增加：

```yaml
devops_assets_root: DevOps
environment_names: DEV, UAT, PROD
```

客户环境清单确认后、`devops` 首次完成前，初始化根目录 `DevOps/`。每个 `environment_names` 条目必须存在 `DevOps/<environment>/Dockerfile` 和 `DevOps/<environment>/.env.example`，并由 `DevOps/README.md` 说明密钥与维护边界。客户未决定时只能建议 `DEV`、`UAT`、`PROD`；用户接受后才预留。环境名称可由客户自定义，须为安全的单路径段并忽略大小写唯一。

环境资产初始化只增补缺失文件，不覆盖、不删除已有资产。占位 Dockerfile 必须明确不可运行且不得包含臆造的构建成功证据；`.env.example` 不得包含真实密钥。环境清单或资产变化会把已完成的 devops/总体初始化置为 `needs_review`，复核后才能恢复 complete/ready。legacy index 中的既有 devops 文件不被强制补齐。

### `.claw/task-board.md`

任务队列和协调索引的事实源。初始化为空，不制造 `TASK-001`。每张 active card 记录状态、优先级、owner role、依赖、spec/task/assignment 指针和 next action；单张卡片保持少于 20 行，看板整体按真实任务数量伸缩。

task board 可以短暂落后于单任务执行状态；管理者或集成负责人负责协调字段。

### `docs/specs/PROJECT-BASELINE.md`

仅 Brownfield 初始化要求。记录既有用途、verified/inferred/pending、风险热点、入口和接管边界。稳定后为冷资料。

## 9. 事件文件与派生文件

- `docs/specs/FEAT-*.md`：开发类讨论形成设计时创建。
- `docs/design/**/*.html`、`docs/specs/**/*.html`：对应 Markdown 创建或修改后生成；与源文件同目录、同 basename，通过源内容 SHA-256 判断是否过期，不参与事实解析。
- `.claw/tasks/TASK-*.md`：真实任务创建时创建。
- `.claw/issue-list.md`：首次 bug、风险或阻塞时创建。
- `.claw/test-report.md`：首次真实运行验证时创建。
- `.claw/task-archive.md`：首次归档时创建。
- `.claw/integration-queue.md`：出现真实并行分支时创建。
- `.claw/developers/*.yaml`：门禁启用后登记真实成员时创建。
- `.claw/assignments/*.yaml`：产生真实授权时创建。
- `.claw/team-status.md`：管理者查询时生成，不手工维护。
- `.claw-local/identity.json`：本地登录成功后创建，必须 Git ignore。

安装包模板不复制为目标项目中的 `_feature-spec-template.md` 或 `_project-baseline-template.md`。

## 10. FEAT

新路径：

```text
docs/specs/FEAT-<author-slug>-<nnn>-<description>.md
```

规范 ID：`FEAT-<author-slug>-<nnn>`。

必需字段：

- `kind: feature-spec`
- `feature_id`
- `work_type`
- `title`
- `status`
- `init_status`
- created/updated attribution
- `contributors`
- `task_ids`
- related issue/decision IDs
- `policy_version: 3`

推荐状态：`draft`、`in_design`、`approved`、`in_implementation`、`implemented`、`verified`、`archived`。

文件名作者是原始创建者；多人贡献只更新 contributors，不重命名。

分配器创建 FEAT Markdown 后必须在返回成功前生成同目录配对 HTML。后续修改 FEAT 时，执行者必须刷新该 HTML。

## 11. TASK

新路径：

```text
.claw/tasks/TASK-<owner-slug>-<nnn>-<description>.md
```

规范 ID：`TASK-<owner-slug>-<nnn>`。

所有任务类型共享该用户的个人序列。必需字段至少包含 task ID/type、可选 feature ID、creator、assignee、owner role、status/stage、branch、assignment path、next action、updated attribution 和 policy version。

推荐 task type：`feature`、`iteration`、`bugfix`、`refactor`、`documentation`、`test`、`release`、`deployment`、`investigation`、`project_management`、`other`。

任务转交只更新 assignee，不改变 ID 或路径。

## 12. 作者与个人序号

自动作者 slug 解析顺序：

1. 全局 Git 配置的 `user.name`。
2. 当前项目本地 Git 配置的 `user.name`。
3. 操作系统用户名。

已验证 developer 的 `document_slug` 不参与自动文档命名。显式 `--owner` 是用户确认的覆盖值。自动来源分别记录为 `global_git_config_user_name`、`project_git_config_user_name` 和 `os_user`；历史 `git_config_user_name` 值继续兼容。

FEAT 和 TASK 分别维护每位用户的最高已分配序号。分配器必须：

- 在项目锁内运行。
- 同时扫描文件和持久计数登记。
- 使用排他创建或原子预留。
- 删除或归档文件后仍不复用编号。
- 不把旧全局编号归属给任何用户。

`.claw/document-id-registry.json` 是可提交的机器登记，用于防止删除或归档后的编号复用；`.claw/.locks/` 仅用于瞬时互斥，不提交版本库。

## 13. Legacy index

`.claw/legacy-document-index.yaml` 至少记录 captured/policy time，以及每个 grandfathered 路径、kind、ID 和原 schema version。

规则：

- index 中的旧文件按旧 schema 校验。
- policy 生效后的新文件按 v5 校验。
- policy 生效后新建旧式 ID 报错。
- 旧、新 FEAT/TASK 可以长期交叉引用。
- 没有 manifest 的项目保持 v4 profile，仅给迁移提示。

批量迁移必须由用户明确请求，并生成 path/ID mapping；默认不迁移。

## 14. 字段级事实源

| 事实 | 权威来源 |
|---|---|
| 项目模式、文档语言、模块开关、初始化聚合状态 | manifest |
| 用户目标、范围、成功标准 | goals |
| 当前架构 | decisions / ARCHITECTURE |
| 技术选择原因和历史 | decisions / ADR |
| 目录职责 | directory-map |
| 队列、优先级、依赖、协调指针 | task-board |
| 执行进展、验证、变更、阻塞、下一步、交接 | task status |
| 需求、设计、验收 | FEAT |
| bug/risk 根因和严重度 | issue-list |
| 真实测试证据 | test-report |
| 授权身份、分支和写入范围 | assignment |
| 开发者公开身份和状态 | developer record |
| 合并顺序和集成 gate | integration-queue |
| 热索引 | current-status（派生） |
| 团队摘要 | team-status（派生） |

冲突时按字段权威来源修复，不能让整个文件全局覆盖其他文件。current status 和 team status 与来源冲突时重新生成。

## 15. 热、温、冷

- 机器热：manifest。
- 上下文热：current status。
- 温：task board、选中 task、选中 FEAT、相关 architecture/ADR、directory map、当前 issue/test/devops、启用模块配置。
- 冷：稳定 goals、ADR 历史、baseline、archive、已完成 FEAT/TASK。

每次会话：manifest 路由 → current status → task board（实现/排期时）→ 选中 task → 关联 FEAT → 仅触发的其他文件。

## 16. 会话意图与交付门槛

用户目标清楚时不要重复问固定菜单。目标不清楚时开放式确认，可以提示新需求、迭代和 bug，但接受任何操作。

开发类工作通常执行：讨论 → FEAT 草稿 → 用户确认 → TASK 拆分 → 实现 → 真实验证 → 评审/关闭。简单查询和小型独立维护可以不创建 FEAT。

已有活跃工作时，开始新工作前显示当前工作并确认继续、并行、暂停或取消，不能静默覆盖。

## 17. 协作门禁

v5 中 `modules.collaboration_gate=true` 是主要触发条件；legacy 项目存在 developers/assignments 或 active assignment 也触发。

触发后，任何实现和交付状态写入前必须由 `dev-login.py` 完成 SSH challenge-response，并在有 task 时检查 assignment。缓存、聊天身份、Git author 和 `check-assignment.py` 不能替代登录。

repository 文件不得保存 private key、password、token、secret 或 bearer token。`.claw-local/identity.json` 只缓存私钥路径和公开身份，不能作为已登录证明。

## 18. Change review

`.claw/review-config.yaml` 保存 platform、target branch、reviewer 和 required checks，不保存 secret。只读取被选中的平台 reference。

Codeup token 保存于 `.claw-local/codeup.env`；GitHub secret 使用平台 secret store。评审描述关联完整 TASK ID，并记录 scope、verification、risk、rollback 和状态链接。

用户明确要求推送到测试环境时，`change_review` 模块路由到 `push-test-environment.py`。默认目标为 `dev`，冲突采用 source-branch-wins；该策略仅限测试环境，不能静默套用于生产发布。门禁同时启用时仍需登录和 assignment 授权。

## 19. 校验

无 manifest 时运行 legacy v4 校验。有 v5 manifest 时按 catalog 动态校验：

- 只要求当前模式、启用模块和已触发事件的文件。
- 核心文件 frontmatter、init status 和确认字段合法。
- `complete` 文件没有未解释占位符。
- current status 计数、引用和活跃 task 一致。
- 新式 ID、路径、作者和个人序号一致。
- legacy index 与 policy 边界一致。
- 禁用模块没有被初始化器意外创建或要求。
- 5.0.3 及后续 manifest 固定使用 `language: zh-CN`；历史 ready 状态仍不得保留 `language: pending`。
- repository 状态和 review config 不包含 secret。
- `docs/design/**/*.md`、`docs/specs/**/*.md` 都存在同目录同 basename HTML，且 HTML 内记录的源内容摘要与当前 Markdown 一致。

校验失败不得把 manifest 标为 ready。

## 20. 原子性与恢复

- 初始化、编号分配和 hot index 生成使用项目锁；`.claw/.locks/` 是 Git ignore 的瞬时协调目录。
- 写入使用同目录临时文件和原子替换。
- 配对 HTML 也使用同目录临时文件和原子替换；中断不能留下半写文件。
- 重复初始化相同内容为 no-op。
- 已被用户修改的文件不自动覆盖；报告冲突。
- 中断后从 checkpoint 和第一个未完成核心文件恢复。
- 并发 revision 冲突时停止并协调，不采用最后写入覆盖。

## 21. 项目指令锚点

项目根 README 和 AGENTS 必须保留受控声明块，要求所有 Agent 在项目工作前加载本 Skill，并给出安装来源。它们是指令锚点，不是状态文件，不计入 init completion。

新生成的 AGENTS 受控声明块还必须要求每个新聊天或新会话读取上游 `skill/SKILL.md` 的 `metadata.skill_version`；发现新版本时自动更新并重新加载本 Skill。已有完整受控块继续保持原样，不因初始化或同步被静默覆盖。
