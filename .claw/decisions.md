---
kind: decisions
version: 4
architecture_init_status: complete
architecture_reviewed_at: 2026-07-18T02:36:33Z
architecture_confirmed_by: Bimo
updated_at: 2026-07-18T12:39:25Z
updated_by: Bimo
---

# 技术决策记录

`decisions.md` 是架构和技术选型的唯一事实源。

## ARCHITECTURE

### 系统类型与技术栈

- 状态：`verified`。
- 本项目是一个可独立发布的项目管理 Skill，不是常驻运行服务。
- 发布包位于 `skill/`，主要使用 Markdown、YAML、JSON、Python 标准库和 Shell；平台集成模板覆盖 Codeup 与 GitHub。

### 运行流程

1. `skill/SKILL.md` 先调用只读 preflight，以 `.claw/manifest.yaml` 或 legacy 状态选择 profile。
2. manifest 先用 `language` 选择人类可读模板，再根据 `project_state`、`collaboration_gate`、`change_review` 开关按需路由 reference 和核心文件。
3. Greenfield/Brownfield 引导由 catalog、模板和初始化脚本驱动，每个核心文件独立保存初始化状态。
4. 运行期按“讨论 → FEAT → 用户确认 → TASK → 实现 → 验证 → 评审”推进；热索引从字段级事实源生成。

### 模块与边界

- `skill/references/`：按初始化、模块和平台渐进加载的协议。
- `skill/state-catalog.json` 与 `skill/schemas/`：机器可读文件生命周期、条件和结构约束。
- `skill/scripts/`：预检、初始化、模块配置、个人编号、热状态聚合、身份门禁、评审与校验。
- `skill/templates/`：英文规范模板和 `locales/zh-CN/` 中文镜像，只在核心初始化或真实事件触发时渲染。
- `skill/tests/` 与 `skill/examples/`：Greenfield、Brownfield、legacy 和模块组合的回归证据。
- `.claw/` 与 `docs/specs/`：本仓库自身的项目事实和设计，不属于可发布 Skill 运行代码。

### 数据、依赖与发布

- 项目状态只写入 `.claw/`；本机私密配置只写入 Git 忽略的 `.claw-local/`。
- 状态文件是可审计文本，不依赖数据库；写入关键索引和个人编号时使用锁、排他创建与原子替换。
- 核心初始化和校验脚本只依赖 Python 标准库；Git、OpenSSH、Codeup/GitHub API 只在对应能力实际启用时需要。
- 发布单元是 `skill/` 目录，版本权威为 `skill/SKILL.md` 的 `metadata.skill_version`。

### 非功能约束

- 旧项目默认继续使用 legacy profile；未经明确请求不得改名、补字段或批量迁移。
- 禁用模块的资料不得加载；事件文件不得在初始化时伪造。
- 不记录 secret，不伪造测试或部署结果；所有 ready/complete 状态必须有确认与真实校验依据。
- 相关决策：ADR-001、ADR-002、ADR-003、ADR-010、ADR-011、ADR-012、ADR-013。

## 决策索引

| 编号 | 标题 | 状态 | 日期 | 替代/被替代 |
|------|------|------|------|-------------|
| ADR-001 | Use managed README/AGENTS declaration blocks | accepted | 2026-04-30 | - |
| ADR-002 | Use public identity records and signed task assignments for async parallel delivery | accepted | 2026-05-01 | - |
| ADR-003 | Treat team status as a generated manager view | accepted | 2026-05-01 | - |
| ADR-004 | Gate multi-developer work through project-manager assignments and SSH-signed Git identity | accepted | 2026-05-16 | - |
| ADR-005 | Verify local developer identity with SSH challenge-response login | accepted | 2026-05-17 | - |
| ADR-006 | Make local identity login a hard pre-edit gate | accepted | 2026-05-17 | - |
| ADR-007 | Use task-bounded broad code authorization for normal feature work | accepted | 2026-05-18 | - |
| ADR-008 | Use Codeup change requests as the default review platform flow | accepted | 2026-05-19 | - |
| ADR-009 | Use source-branch-wins conflict resolution for test-environment pushes | accepted | 2026-05-20 | - |
| ADR-010 | Keep state progressive with per-task status files | accepted | 2026-05-21 | - |
| ADR-011 | Keep the distributable skill in a dedicated directory | accepted | 2026-07-17 | - |
| ADR-012 | Use a manifest-driven modular v5 state lifecycle | accepted | 2026-07-18 | - |
| ADR-013 | Use manifest-selected language for human-readable project documents | accepted | 2026-07-18 | - |

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
- 备选方案：只更新 `skill/SKILL.md`；只要求人工编辑 `README.md` 和 `AGENTS.md`；增加受控声明块并配套脚本和校验器。
- 最终结论：使用带 marker 的受控声明块，由脚本幂等写入 `README.md` 和 `AGENTS.md`，并由校验器检查是否存在。
- 为什么这个方案胜出：它同时覆盖 greenfield 和 brownfield，自动化程度高，也能减少文档漂移。
- 后续影响：初始化流程和示例项目都要同步维护这两个文件；校验器会对未补齐声明块的项目给出失败结果。
- 验证方式：运行 `python3 skill/scripts/validate-state.py .claw`，并检查主仓库与示例项目的 `README.md`、`AGENTS.md`。

## ADR-002 - Use public identity records and signed task assignments for async parallel delivery

- 状态：`accepted`
- 日期：`2026-05-01`
- 背景：两个独立开发者可能在不同环境中并行开发，过程里无法依赖实时状态同步，最后合并时容易出现身份不清、写入范围冲突和热文件冲突。
- 备选方案：把管理者口令加密存入项目文档并下发开发者 token；只依赖聊天记录和 PR 描述；使用仓库内公钥身份记录、管理者签名授权、单任务状态文件和集成队列。
- 最终结论：采用公钥身份记录和任务授权协议。项目文档只保存公钥、开发者 ID、任务授权、状态分片和集成队列，不保存管理者口令、bearer token、私钥或可复用密钥。
- 为什么这个方案胜出：公钥和授权记录适合异步、多环境、可审计的协作模式；单任务状态文件能减少 `current-status.md` 合并冲突；集成队列能把最终合并顺序和验证门禁显性化。
- 后续影响：技能协议、模板、初始化脚本和校验器都要支持可选的 `.claw/developers/`、`.claw/assignments/`、`.claw/tasks/` 和 `.claw/integration-queue.md`。
- 验证方式：运行 `python3 skill/scripts/validate-state.py .claw`，并确认可选并行协作文件存在时能通过结构校验。

## ADR-003 - Treat team status as a generated manager view

- 状态：`accepted`
- 日期：`2026-05-01`
- 背景：管理者需要查看团队成员列表、任务分配、贡献状态和集成状态，但这些事实分散在 identity、assignment、task status、task-board 和 integration queue 中。
- 备选方案：让管理者手工维护 `.claw/team-status.md`；把所有贡献状态写回 `current-status.md`；把 `team-status.md` 定义为派生视图并用脚本生成。
- 最终结论：`team-status.md` 是派生管理视图，由 `skill/scripts/summarize-team-status.py` 按标准顺序生成，不作为事实源。
- 为什么这个方案胜出：它给管理者一个统一入口，同时避免多人频繁编辑热文件，也避免把汇总快照误当成真实授权或进度来源。
- 后续影响：`team-status.md` 只在管理者请求真实汇总时生成；ADR-012 已取消初始化阶段的预创建。当开发者、授权、任务状态或集成队列变化后，应重新生成团队状态。
- 验证方式：运行 `python3 skill/scripts/summarize-team-status.py .claw --write` 和 `python3 skill/scripts/validate-state.py .claw`。

## ADR-004 - Gate multi-developer work through project-manager assignments and SSH-signed Git identity

- 状态：`accepted`
- 日期：`2026-05-16`
- 背景：用户要求每个项目有项目经理，只有项目经理能添加团队成员和规定负责功能范围；开发前必须识别开发者身份并阻止越权开发。
- 备选方案：只依赖聊天记录和人工约定；只绑定 Git author/email；使用 Git 平台账号绑定、SSH commit signing、项目经理任务授权和 preflight 脚本共同校验。
- 最终结论：采用项目经理门控授权模型。默认推荐 Git 平台账号绑定 + SSH commit signing；`.claw/developers/` 保存公开身份和签名指纹，`.claw/assignments/` 保存项目经理授权范围，`skill/scripts/check-assignment.py` 用于本地和 CI preflight 检查。
- 为什么这个方案胜出：Git author/email 可伪造，不能作为强身份依据；SSH signing 易于团队理解和平台验证，配合分支保护与 CI 能把授权规则变成可执行门禁。
- 后续影响：协议、模板、校验器和 README 都要明确项目经理是唯一授权入口；CI 接入时应把 PR author、branch 和 changed files 传给 preflight 脚本。
- 验证方式：运行 `python3 skill/scripts/check-assignment.py` 的通过和阻断用例、`python3 skill/scripts/validate-state.py .claw`、以及 Python 语法检查。
- 补充规则：默认一个 Git 平台账号只绑定一个 active 身份；如果同账号需要兼任多个身份，必须使用不同 SSH signing key fingerprint 并记录 `role_sharing_exception`；同账号同 key 不应同时代表项目经理和开发者。

## ADR-005 - Verify local developer identity with SSH challenge-response login

- 状态：`accepted`
- 日期：`2026-05-17`
- 背景：用户希望开发会话开始前先像登录一样报告并验证当前操作者身份，而不是只在 PR 或 assignment 检查里验证传入的 `developer_id`。
- 备选方案：继续要求用户手工声明身份；把私钥或 token 写入项目文件；使用本机私钥签名一次性 challenge，并用仓库登记的 public key 验签。
- 最终结论：新增 `skill/scripts/dev-login.py`，首次运行时由用户提供本机私钥路径，脚本自动推导 public key 和 fingerprint、匹配 `.claw/developers/*.yaml`、完成 challenge-response 验签，并可串联 `check-assignment.py`。
- 为什么这个方案胜出：它证明当前操作者持有登记身份对应的私钥，同时不把私钥、token 或密码写入仓库；本机缓存只保存私钥路径和公开身份元数据，每次开发仍重新验签。
- 后续影响：开发者记录必须保存 `public_key` 才能做登录式验签；采用此模式的项目应把 `.claw-local/` 加入 `.gitignore`。
- 验证方式：生成临时 SSH key 和临时 `.claw` 状态，运行 `skill/scripts/dev-login.py` 的通过、缓存复用、错误 key 和越界文件用例，并运行状态校验和 Python 语法检查。

## ADR-006 - Make local identity login a hard pre-edit gate

- 状态：`accepted`
- 日期：`2026-05-17`
- 背景：3.7.0 已提供 `skill/scripts/dev-login.py`，但协议仍有 `should run` 等软约束，真实项目中 agent 可能在已知身份但未完成 challenge-response 验证时直接修改代码。
- 备选方案：继续依赖 agent 自觉运行登录脚本；只在 PR/CI 阶段阻断；把本地 `dev-login.py` 升级为身份/授权记录存在时自动启用的硬性编辑前门禁。
- 最终结论：采用硬阻断门禁。只要项目存在 `.claw/developers/`、`.claw/assignments/`、`assignment_path` 或 `local_login_required: true`，agent 在修改源码、测试、运行配置、迁移、生成资产、feature spec 或任务状态前，必须先让 `skill/scripts/dev-login.py` 返回 `allowed`。
- 为什么这个方案胜出：它把“身份验证能力”变成“开发前必须满足的状态”，避免聊天声明、缓存路径、Git author/email 或记忆上下文被误当成身份验证。
- 后续影响：协议、README、状态模型、模板和使用说明都必须明确没有后门；`skill/scripts/check-assignment.py` 只用于 CI/assignment-only，不替代本地 SSH challenge-response 登录。
- 验证方式：运行文档/状态校验、Python 语法检查，并检查协议文本中不再把本地登录描述为可选建议。

## ADR-007 - Use task-bounded broad code authorization for normal feature work

- 状态：`accepted`
- 日期：`2026-05-18`
- 背景：精确 `scope_files` 能保护任务边界，但普通功能经常需要修改任务标题之外的关联模块。要求 PM 在任务开始前准确预判所有实现文件会造成频繁阻断，并诱导开发者把修复塞进错误层。
- 备选方案：继续把 `scope_files` 作为所有代码的硬边界；完全放开所有路径；采用任务边界宽代码权限，同时保护治理、身份、CI、迁移和门禁脚本等敏感路径。
- 最终结论：普通功能任务默认推荐 `scope_mode: task_bounded_broad_code`。开发者通过身份和任务授权后，可在 `allowed_write_roots` 内修改源码和测试；`protected_paths` 命中时必须由 PM 在 `scope_files` 中精确授权。
- 为什么这个方案胜出：它把门禁控制点放回“谁能处理哪个任务”，避免用过窄文件清单限制正确实现路径，同时保留对高风险路径的硬保护和审计。
- 后续影响：assignment 模板、`skill/scripts/check-assignment.py`、README、STATE-MODEL 和 feature spec 模板都要支持 scope mode、宽写入根路径、受保护路径和变更清单。
- 验证方式：运行 broad scope 通过/阻断用例、旧 exact scope 阻断用例、状态校验和 Python 语法检查。

## ADR-008 - Use Codeup change requests as the default review platform flow

- 状态：`accepted`
- 日期：`2026-05-19`
- 背景：用户的开发环境基于阿里云云效 Codeup，创建合并请求使用 Codeup OpenAPI，不能把 GitHub pull request 和 GitHub Actions 作为默认规范。
- 备选方案：继续以 GitHub PR 为默认流程；只写文档不提供脚本；将评审请求抽象为平台无关概念，并提供 Codeup 默认脚本和模板。
- 最终结论：以 Codeup change request 作为默认提交评审流程。每个开发者本地保存 `YUNXIAO_TOKEN`，创建前脚本先检查 token；缺失时提示官方个人访问令牌文档。GitHub Actions 示例保留为可选平台说明。
- 为什么这个方案胜出：它符合真实托管平台和密钥模型，同时仍保留跨平台扩展空间；token 保存在本地忽略目录，不进入仓库事实源。
- 后续影响：README、SKILL、STATE-MODEL、模板和初始化提示都要说明 Codeup 为默认方案；自动化创建合并请求时使用 `skill/scripts/create-codeup-change-request.py`。
- 验证方式：运行 Codeup 脚本缺 token 用例、Python 语法检查和 `.claw` 状态校验。

## ADR-009 - Use source-branch-wins conflict resolution for test-environment pushes

- 状态：`accepted`
- 日期：`2026-05-20`
- 背景：用户希望当他说“推送到测试环境”时，agent 自动把开发分支合并到 `dev`，如果有冲突则自动处理，并把 `dev` 推送到线上测试分支。
- 备选方案：遇到冲突就停止并要求人工处理；使用 `dev` 分支内容优先；使用开发分支内容优先；尝试语义级自动合并。
- 最终结论：测试环境推送采用开发分支优先策略。脚本先执行 `git merge -X theirs <source>`；如仍存在 unmerged paths，则逐个采用源开发分支版本并提交 merge，然后推送 `dev`。
- 为什么这个方案胜出：自动冲突处理必须有可预测规则。测试环境的目标是快速验证开发分支效果，使用源分支优先比静默保留 `dev` 更符合用户意图；同时文档明确该策略不适合生产发布默认流程。
- 后续影响：新增 `skill/scripts/push-test-environment.py`，并在 README、SKILL、STATE-MODEL 和初始化提示中声明“推送到测试环境”的默认行为。
- 验证方式：运行脚本帮助和 dry-run、临时 Git 仓库冲突合并用例、Python 语法检查和 `.claw` 状态校验。

## ADR-010 - Keep state progressive with per-task status files

- 状态：`accepted`
- 日期：`2026-05-21`
- 背景：用户指出项目增大后技能状态文件会越来越大，热文件不能积累历史内容，并明确要求按索引模式做渐进式追踪与披露，每个任务单独记录当前状态。
- 备选方案：继续在 `current-status.md` 和 `task-board.md` 中保留会话进展与任务详情；只增加归档规则；将热文件和看板都改成索引，并把任务状态拆到 `.claw/tasks/TASK-xxx.md`。
- 最终结论：采用渐进式状态披露。`current-status.md` 只做热索引，`task-board.md` 只做紧凑任务目录，每个活跃任务必须通过 `task_status_path` 指向独立小文件。
- 为什么这个方案胜出：它把启动时必读内容控制在最小集合，同时仍保留任务进度、验证和交接信息；大型项目可以按需继续展开 spec、issue、decision 和 test-report。
- 后续影响：模板、README、STATE-MODEL、SKILL、校验器和当前仓库状态文件都要迁移到索引模式。
- 验证方式：运行 `python3 skill/scripts/validate-state.py .claw` 和 `python3 -m py_compile skill/scripts/validate-state.py`。

## ADR-011 - Keep the distributable skill in a dedicated directory

- 状态：`accepted`
- 日期：`2026-07-17`
- 背景：项目开发文档和可发布技能文件混在根目录，边界不清晰。
- 备选方案：继续保持扁平根目录；仅移动 `skill/SKILL.md`；将完整可发布技能包移入 `skill/`。
- 最终结论：根目录保留项目管理文档和状态，`skill/` 包含 `skill/SKILL.md`、状态模型、脚本、模板和示例。
- 为什么这个方案胜出：它建立了明确的发布边界，同时保留技能内部的相对路径关系。
- 后续影响：根 `README.md`、`AGENTS.md`、当前项目状态和发布模板需改用 `skill/` 路径；发布时以 `skill/` 作为技能包根目录。
- 验证方式：运行状态校验、Python/Shell 语法检查和全新项目初始化冒烟测试。

## ADR-012 - Use a manifest-driven modular v5 state lifecycle

- 状态：`accepted`
- 日期：`2026-07-18`
- 背景：固定复制一组状态文件无法判断初始化是否完成，也无法按项目需要关闭项目状态、多人门禁或代码评审；单值热状态和全局编号也不支持多人、多窗口并行。
- 备选方案：继续扩充固定 v4 模板；强制所有历史项目一次性迁移；增加 manifest、catalog、模块开关、逐文件初始化状态和显式 legacy 边界。
- 最终结论：采用 v5 manifest 控制面和共享 catalog。Greenfield/Brownfield 由证据建议、用户确认；项目状态、协作门禁和代码评审独立开关；新 FEAT/TASK 使用带用户名的个人序列；current status 由多个任务事实源生成；旧文件只在用户显式采用时登记边界，不自动改写。
- 为什么这个方案胜出：它能可靠恢复初始化、只加载启用能力、避免虚假占位文件，同时为新项目建立一致规则并保留历史项目的非破坏性运行路径。
- 后续影响：`SKILL.md` 成为轻量路由器，详细流程进入 references；初始化器、模板、校验器、示例和本仓库状态必须共享同一 catalog 契约。
- 验证方式：运行全部单元测试、Greenfield/Brownfield/legacy 严格校验、模块组合与显式 adoption 冒烟测试、Skill 标准校验和 diff 检查。

## ADR-013 - Use manifest-selected language for human-readable project documents

- 状态：`accepted`
- 日期：`2026-07-18`
- 背景：v5 的核心模板、事件模板和派生视图存在英文或中英混合内容，项目无法声明统一的文档语言，初始化会看似默认英文。
- 备选方案：继续使用固定英文；根据会话语言临时翻译但不保存配置；在 manifest 中保存语言并提供确定性本地化模板与生成器。
- 最终结论：manifest 增加 `language: pending | en | zh-CN`。新初始化必须先确认语言，再生成依赖语言的人类可读文件；机器字段、枚举、ID、路径、命令和原始证据不翻译。该兼容性新增能力按补丁位从 `5.0.0` 递增为 `5.0.1`。
- 为什么这个方案胜出：manifest 是所有会话共享的控制面，能让初始化、FEAT/TASK 分配和派生视图使用同一个稳定事实源；确定性模板避免不同 Agent 临时翻译造成结构漂移。
- 后续影响：规范英文模板与 `templates/locales/zh-CN/` 必须镜像维护；解析器接受关键中英文 section；早期 v5 缺字段按英文兼容，已有文件不自动翻译。
- 验证方式：运行 72 项单元测试、严格 v5 示例校验，并实际创建 pending、`zh-CN`、`en` 三种前向项目验证模板、FEAT 和派生视图。

## 维护规则

- 只记录非平凡技术决策。
- 决策变更时，不删除历史，新增或更新状态。
- 必须写清楚为什么选它，而不只是选了什么。
