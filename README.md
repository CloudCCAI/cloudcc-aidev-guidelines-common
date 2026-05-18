# AI Agent 项目状态与交付规范

**Bilingual project-state and delivery protocol for AI coding agents**

这个 skill 现在覆盖五件事：

1. 把项目状态外存到 `.claw/` 或 `.ai-dev/`
2. 用 `task-board.md` 管理任务、依赖和交接
3. 用 `docs/specs/` 强制功能级设计先落盘再开发，并支持老项目渐进接入
4. 用身份、公钥、任务授权、分片状态和集成队列支持异步多开发者并行交付
5. 用项目经理门控授权、SSH challenge-response 登录、Git 平台账号绑定、SSH commit signing 和 preflight 检查阻止越权开发

It now covers five layers:

1. durable project state in `.claw/` or `.ai-dev/`
2. executable task tracking and handoff in `task-board.md`
3. spec-driven delivery in `docs/specs/`, including brownfield adoption
4. identity-based async parallel delivery with assignments, status slices, and integration queues
5. project-manager-gated authorization with SSH challenge-response login, Git account binding, SSH commit signing, and preflight scope checks

## 一句话介绍 | One-Line Pitch

让 AI 在跨会话、跨智能体协作中，不只记住“现在做到哪”，还记住“为什么这样做、接下来该谁做、按什么设计继续做”。

## 版本标识 | Version Marker

当前 skill 版本：`3.8.0`

唯一权威版本标识位于 [SKILL.md](SKILL.md) front matter 中的 `skill_version` 字段。智能体需要判断当前安装的是哪个版本时，应优先读取这个字段，而不是以 README 或 CHANGELOG 为准。

## 仓库内容 | Repository Contents

| 路径 | 说明 |
|------|------|
| `SKILL.md` | 主 skill 协议 / main skill protocol |
| `STATE-MODEL.md` | 详细状态模型 / detailed state model |
| `templates/` | 核心状态与可选并行协作模板 / core state and optional parallel coordination templates |
| `scripts/ensure-agent-guidance.sh` | 项目级 README/AGENTS 声明写入器 / managed README/AGENTS declaration writer |
| `scripts/dev-login.py` | 开发前本地 SSH challenge-response 身份登录 / local SSH challenge-response identity login |
| `scripts/check-assignment.py` | 开发前身份、任务、分支、任务边界和受保护路径检查 / preflight identity, task, branch, task boundary, and protected-path check |
| `scripts/summarize-team-status.py` | 团队状态汇总器 / derived team status summarizer |
| `templates/github-workflows/check-assignment.yml` | GitHub Actions 授权检查示例 / GitHub Actions assignment gate example |
| `templates/team-status.md` | 管理者团队状态汇总模板 / manager team status view template |
| `templates/integration-queue.md` | 异步并行集成队列模板 / async parallel integration queue template |
| `templates/parallel/` | 开发者身份、任务授权、单任务状态模板 / identity, assignment, and task-status templates |
| `templates/docs/feature-spec-template.md` | 功能设计模板 / feature spec template |
| `templates/docs/project-baseline-template.md` | 老项目基线模板 / legacy baseline template |
| `scripts/` | 初始化与校验脚本 / init and validation scripts |
| `examples/` | 完整示例状态与 spec / sample state and feature spec |
| `CHANGELOG.md` | 版本变更记录 / version history |

## 设计原则 | Design Principles

- 默认最小读取，而不是默认全量读取
- 触发式更新，而不是机械回写全部文件
- 热状态、任务队列、长文档设计分层
- 活跃任务与历史任务分层保存
- 项目根目录必须有 README/AGENTS 双锚点声明技能要求
- 异步并行开发时，用公钥身份和任务授权记录替代仓库内口令或 bearer token
- 多人开发默认由项目经理门控授权，绑定 Git 平台账号和 SSH commit signing 指纹
- 使用身份或授权记录的项目会自动启用硬身份门禁，本地开发前必须用 SSH challenge-response 验证当前操作者确实持有登记身份对应的私钥
- 开发前必须通过身份、任务、分支和文件范围 preflight 检查；不通过或无法运行检查就停止开发
- 多开发者进度写入单任务状态文件，`current-status.md` 只做热索引和主线快照
- 最终合并走集成队列、集成分支和真实验证记录
- 摘要、任务、问题、设计各自有唯一事实源
- 已验证事实与推断结论分离
- 非平凡功能先写 spec，再进入主开发
- 老项目先建 baseline，再渐进纳入完整协议

## 项目级技能声明 | Project-Level Skill Declaration

凡是采用此技能的项目，都必须在项目根目录的 `README.md` 和 `AGENTS.md` 中保留一个受控声明块，明确说明：

- 当前项目遵循 `cc-aidev-guidelines-common`
- 所有 AI 智能体必须自动使用此技能
- 如果当前环境尚未安装此技能，必须先从 GitHub 安装：`https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common`

推荐使用：

```bash
bash /path/to/this-skill/scripts/ensure-agent-guidance.sh /path/to/your-project
```

## 快速开始

### 1. 初始化状态与文档目录

推荐直接使用脚本：

```bash
bash /path/to/this-skill/scripts/init-state.sh /path/to/your-project
```

它会创建：

- 项目根目录中的 `README.md` 技能声明块
- 项目根目录中的 `AGENTS.md` 技能声明块
- `.claw/` 状态目录
- `docs/specs/` 文档目录
- `docs/specs/_feature-spec-template.md` 模板文件
- `docs/specs/_project-baseline-template.md` 老项目基线模板
- `.claw/task-archive.md` 任务归档文件
- `.claw/integration-queue.md` 异步并行集成队列
- `.claw/team-status.md` 管理者团队状态派生视图
- `.claw/developers/`、`.claw/assignments/`、`.claw/tasks/` 可选并行协作目录

### 2. 先判断项目类型

在第一次接入时，先区分当前项目属于哪一类：

- `新项目 / Greenfield`：项目刚启动，或某个新模块可以从零按协议落盘
- `老项目 / Brownfield`：项目已经存在一段时间，之前没有按这套协议维护状态和设计文档

如果判断标准不清晰，可以用这个经验法则：

- 需要先理解遗留实现、推断架构、补运行入口，通常是老项目
- 可以直接从当前需求开始拆任务和写 spec，通常是新项目

### 3. 先补最少内容

初始化后优先确认这些文件：

- `README.md`
- `AGENTS.md`
- `.claw/current-status.md`
- `.claw/goals.md`
- `.claw/task-board.md`

如果当前工作属于新功能、跨模块改动、接口/数据变更或非平凡重构，再创建：

- `docs/specs/FEAT-xxx-feature-name.md`

如果这是老项目首次接入，再先创建：

- `docs/specs/PROJECT-BASELINE.md`

如果这是两个或更多开发者异步并行开发，再启用：

- `.claw/developers/DEV-xxx.yaml`
- `.claw/assignments/TASK-xxx.yaml`
- `.claw/tasks/TASK-xxx.md`
- `.claw/integration-queue.md`
- `.claw/team-status.md`

### 4. 新项目如何使用 | Greenfield Workflow

推荐按这个顺序：

1. 运行初始化脚本
2. 确认 `README.md` 和 `AGENTS.md` 中的技能声明块已生成
3. 填写 `.claw/current-status.md`
4. 填写 `.claw/goals.md`
5. 在 `.claw/task-board.md` 中创建首批任务
6. 对非平凡功能创建 `docs/specs/FEAT-xxx-feature-name.md`
7. 开发过程中持续同步 `task-board.md`、feature spec、`current-status.md`
8. 会话结束时更新必要状态文件并运行校验

适用于：

- 从零开始的新仓库
- 新立项项目
- 在老仓库里独立启动的新模块或新子系统

### 5. 老项目如何使用 | Brownfield Workflow

推荐按这个顺序：

1. 运行初始化脚本
2. 检查并补齐 `README.md` 和 `AGENTS.md` 中的技能声明块
3. 先创建 `docs/specs/PROJECT-BASELINE.md`
4. 在 baseline 里记录当前已确认事实、推断事实、待验证项、关键入口和热点模块
5. 在 `.claw/task-board.md` 里创建“接管/接入”任务，必要时让任务先指向 `PROJECT-BASELINE.md`
6. 从当前正在推进的工作开始，逐步要求 `task-board + feature spec`
7. 只有当某个老模块真的被改动时，才为它补对应 `FEAT-xxx-*.md`
8. 每次确认了新的 legacy 理解，就回写 `PROJECT-BASELINE.md`

适用于：

- 之前没有任何项目状态外存的老仓库
- 有代码但缺少设计文档和任务交接材料的项目
- 需要多个智能体轮流接手的存量系统

老项目接入时要特别注意：

- 不要求一次性补齐全部历史
- 不要把历史猜测写成 verified 事实
- 不要一边大改 legacy，一边不更新 baseline
- 目标是先建立“可继续推进的共同基线”，不是补作文档库存

### 6. 异步多开发者并行开发 | Async Parallel Delivery

当两个独立开发者不在同一物理环境、只能通过 Git 远端和项目文件异步协作时，推荐使用这一层。

核心原则：

- 不把管理者口令、开发者 bearer token、私钥或可复用密钥写入仓库，即使加密后也不推荐。
- 仓库只记录公钥、开发者 ID、任务授权、任务边界、写入根路径、受保护路径、状态分片和集成队列。
- 真实身份强校验交给 Git signed commits、代码托管平台 verified identity、CI 或专用验签工具。
- 开发者只更新自己分配到的 `.claw/tasks/TASK-xxx.md` 和授权范围内的代码。
- `current-status.md` 只做主线热索引，由项目管理者或集成者在合并时刷新。

推荐流程：

1. 项目管理者登记自己的公钥或 Git verified identity。
2. 管理者在 `.claw/developers/DEV-xxx.yaml` 中登记开发者公钥、角色和状态。
3. 管理者为每个并行任务创建 task card 和 `.claw/assignments/TASK-xxx.yaml`。
4. 开发者从主分支创建授权分支，只处理被分配的任务；普通源码/测试可在 `allowed_write_roots` 内修改，受保护路径必须有精确授权。
5. 开发者把进度、验证和交接写入 `.claw/tasks/TASK-xxx.md`。
6. 集成者按 `.claw/integration-queue.md` 的顺序合并分支、解决冲突、运行真实验证。
7. 集成通过后再更新 `task-board.md`、`current-status.md` 和 `test-report.md`。

### 7. 项目经理门控授权 | Project-Manager-Gated Authorization

多人异步协作默认推荐启用这一层：每个项目指定一个或多个 `MANAGER-xxx`，只有项目经理能添加团队成员、暂停成员、分配任务、扩大范围或批准越界修改。

默认 Git 级身份方案：

1. 项目内身份 `developer_id` 绑定 GitHub/GitLab 等平台账号。
2. 开发者使用专门的 SSH commit signing key。
3. `.claw/developers/DEV-xxx.yaml` 只记录公开身份材料，例如 Git 平台账号、SSH public key 和 SSH signing key fingerprint。
4. `.claw/assignments/TASK-xxx.yaml` 记录项目经理授权的任务、分支、scope mode、写入根路径、受保护路径和签名验证引用。
5. 分支保护要求 signed commits 和 CI 检查通过。

本地开发前必须先运行登录式身份验证。只要项目存在 `.claw/developers/`、`.claw/assignments/`、`assignment_path` 或 `local_login_required: true`，这个硬身份门禁就自动启用：

```bash
python3 /path/to/this-skill/scripts/dev-login.py /path/to/your-project/.claw \
  --ssh-key ~/.ssh/id_ed25519_cc_dev \
  --developer DEV-alice \
  --task TASK-001 \
  --branch feat/TASK-001-feature-title \
  --files src/example/file.ts tests/example/test.ts
```

`dev-login.py` 会从本机私钥推导 public key 和 fingerprint，匹配 `.claw/developers/*.yaml`，生成一次性 challenge，用私钥签名，并用登记的 `public_key` 验签。通过后会把 `developer_id`、fingerprint 和私钥路径写入本机忽略文件 `.claw-local/identity.json` 或 `.ai-dev-local/identity.json`，后续可省略 `--ssh-key` 自动复用路径。缓存只保存路径和公开标识，不保存私钥内容；缓存存在不代表已登录，每次开发前仍必须重新验签。

硬身份门禁启用后，AI agent 或开发者在 `dev-login.py` 返回 `allowed` 之前，不得修改源码、测试、运行配置、迁移、生成的应用资产、feature spec 或任务状态文件。聊天里声明 `developer_id`、已知当前用户、Git author/email、历史记忆、缓存 key 路径都不能绕过此门禁。如果缺少私钥路径、任务 ID、分支、待修改文件列表或 assignment，必须先停下补齐验证输入或让 PM 更新授权。

PR CI 或只需要检查任务授权时运行：

```bash
python3 /path/to/this-skill/scripts/check-assignment.py /path/to/your-project/.claw \
  --developer DEV-alice \
  --task TASK-001 \
  --branch feat/TASK-001-feature-title \
  --git-username alice-dev \
  --ssh-signing-key-fingerprint SHA256:abc123 \
  --files src/example/file.ts tests/example/test.ts
```

检查通过会输出 `allowed`；如果身份未知、成员未激活、私钥验签失败、任务未分配给当前开发者、分支不匹配、文件不在允许写入根路径内，或触碰受保护路径但未精确授权，会返回非 0 并输出阻止原因。

推荐的任务授权模型：

```yaml
scope_mode: task_bounded_broad_code
allowed_write_roots:
  - src/**
  - tests/**
scope_files:
  - docs/specs/FEAT-036-openapi-dify-parity.md
  - .claw/tasks/TASK-112.md
protected_paths:
  - .claw/assignments/**
  - .claw/developers/**
  - scripts/dev-login.py
  - scripts/check-assignment.py
  - .github/workflows/**
  - migrations/**
task_boundary:
  - "所有代码修改必须服务于 TASK-112 和 FEAT-036 的验收标准。"
change_manifest_required: true
```

`scope_mode: task_bounded_broad_code` 表示门禁控制的是开发者是否有权处理当前任务，而不是让 PM 预判每一个实现文件。开发者可以在允许的源码和测试根路径内修改必要调用链，但不能修改治理文件、身份授权、CI、迁移、门禁脚本等受保护路径，除非这些路径被 PM 精确列入 `scope_files`。窄任务仍可使用 `scope_mode: exact_files`，此时 `scope_files` 是硬边界。

注意：Git author name 和 email 不能作为强身份依据。它们可以作为辅助信息，但真正可信的门禁应结合 Git 平台账号、SSH commit signing、分支保护和 CI。

默认身份绑定规则：

- 一个 Git 平台账号默认只能绑定一个 active `developer_id`
- 如果同一个 Git 账号必须同时承担项目经理和开发者等多个身份，必须为每个身份使用不同 SSH signing key fingerprint，并在身份记录里显式说明
- 默认不允许同一个 Git 账号 + 同一个 SSH signing key 同时代表 `MANAGER-xxx` 和 `DEV-xxx`
- 同一个 Git 账号兼任多个角色时，`dev-login.py` 通过不同私钥的 challenge-response 结果自动解析当前使用的是哪个 `developer_id`
- `scripts/check-assignment.py` 不能替代本地 `dev-login.py`；它用于 CI、PR 和 assignment-only 检查

GitHub Actions 示例：

```bash
mkdir -p .github/workflows
cp /path/to/this-skill/templates/github-workflows/check-assignment.yml .github/workflows/check-assignment.yml
```

这个 workflow 会从 PR 分支名、标题或正文解析 `TASK-xxx`，用 PR author 匹配 `.claw/developers/*.yaml` 里的 `git_username`，收集 changed files，然后调用 `scripts/check-assignment.py`。项目启用后应在分支保护里要求这个 check 通过。

### 8. 管理者团队状态汇总 | Manager Team Status

当管理者需要查看团队成员列表、任务分配、贡献状态和集成状态时，使用标准汇总方法生成派生视图。

推荐命令：

```bash
python3 /path/to/this-skill/scripts/summarize-team-status.py /path/to/your-project/.claw
```

写入 `.claw/team-status.md`：

```bash
python3 /path/to/this-skill/scripts/summarize-team-status.py /path/to/your-project/.claw --write
```

标准汇总顺序：

1. 读取 `.claw/developers/*.yaml` 获取团队成员、角色、公钥身份和身份状态。
2. 读取 `.claw/assignments/*.yaml` 获取授权任务、负责人、分支、PR、写入范围和共享契约。
3. 读取 `.claw/tasks/*.md` 获取单任务进度、验证状态、阻塞点和交接说明。
4. 读取 `.claw/task-board.md` 补充任务标题、优先级、owner role 和主看板状态。
5. 读取 `.claw/integration-queue.md` 补充合并顺序、集成负责人和 integration status。
6. 生成每个开发者的 `assigned_tasks`、`active_tasks`、`contribution_status`、`validation_status` 和 `integration_status`。

`team-status.md` 不是事实源。它只是一份可重新生成的管理者快照。如果它和 `developers/`、`assignments/`、`tasks/`、`task-board.md` 或 `integration-queue.md` 冲突，应修复事实源后重新生成。

### 9. 让 AI 按协议执行

每次会话：

- 先确认当前环境已经安装 `cc-aidev-guidelines-common`；如果没有，先从 `https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common` 安装
- 先看项目根目录 `README.md` 和 `AGENTS.md` 中的技能声明块
- 先读 `current-status.md`
- 做实现或交接时再读 `task-board.md`
- 任务有 `spec_path` 时先读对应 spec
- 任务有 `assignment_path` 或 `task_status_path` 时，只读取对应授权和单任务状态
- 异步多人开发时，先识别 `developer_id`，再用 `scripts/check-assignment.py` 或等价逻辑检查 assignment、branch、scope mode、写入根路径和受保护路径
- 如果 preflight 不通过，停止开发并要求项目经理更新授权
- 管理者询问团队状态时，用标准汇总脚本生成或读取 `.claw/team-status.md`
- 结束时至少回写 `current-status.md`

### 10. 运行校验

```bash
python3 /path/to/this-skill/scripts/validate-state.py /path/to/your-project/.claw
```

校验器会检查：

- 必需状态文件是否存在
- 项目根目录 `README.md` 和 `AGENTS.md` 是否存在技能声明块
- front matter 是否完整且时间戳有效
- `task-board.md` 里的任务卡是否有效
- `spec_path` 引用的 feature spec 或 baseline 文档是否真实存在且 front matter 合法
- 可选的 `team-status.md`、`integration-queue.md`、`developers/*.yaml`、`assignments/*.yaml` 和 `tasks/*.md` 是否具备最低结构

## 状态分层 | State Layers

| 层级 | 文件 | 默认动作 | 用途 |
|------|------|----------|------|
| Hot | `current-status.md` | 每次读，每次更新 | 当前快照、下一步、读取索引 |
| Warm | `task-board.md` | 实现/交接时读写 | 任务、依赖、责任角色、交接 |
| Warm | `integration-queue.md` | 异步并行集成时读写 | 集成分支、合并顺序、验证门禁 |
| Warm | `team-status.md` | 管理者查看团队状态时生成/读取 | 团队成员、任务分配、贡献状态、集成状态的派生视图 |
| Warm | `developers/*.yaml` | 身份/授权相关时读写 | 开发者 ID、Git 平台账号、SSH 签名指纹、角色、状态 |
| Warm | `assignments/*.yaml` | 分配任务时读写 | 项目经理、任务负责人、分支、scope mode、写入根路径、受保护路径、签名授权 |
| Warm | `tasks/*.md` | 单任务推进时读写 | 开发者进度、验证证据、交接说明 |
| Cold | `task-archive.md` | 仅在看历史任务时读写 | 超出保留窗口的已完成/已取消任务 |
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
| `.claw/developers/*.yaml` | 开发者身份、Git 平台账号、SSH 签名指纹、角色状态、长期范围 |
| `.claw/assignments/*.yaml` | 项目经理任务授权、分支、任务边界、写入根路径、受保护路径、管理者签名 |
| `.claw/tasks/*.md` | 单个任务的开发者进度、验证证据、交接说明 |
| `.claw/integration-queue.md` | 集成分支、合并顺序、集成门禁 |
| `.claw/team-status.md` | 派生团队状态汇总；不作为事实源 |
| `task-archive.md` | 超出保留窗口的已完成/已取消任务历史 |
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
- `scope_mode`
- `allowed_write_roots`
- `scope_files`
- `protected_paths`
- `branch`
- `pr_url`
- `assignment_path`
- `task_status_path`
- `parallel_group`
- `touch_policy`
- `shared_contracts`
- `merge_policy`
- `integration_queue`
- `integration_owner`
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
- `project-manager`
- `integration-agent`
- `human`
- `shared`
- `unassigned`

说明：

- `owner_role` 是稳定责任角色，不依赖智能体自我身份
- `claimed_by` 是可选运行时标签，环境知道就写，不知道就留空
- `assignment_path` 和 `task_status_path` 只在异步多开发者协作中必须填写
- `scope_mode: task_bounded_broad_code` 适合普通功能开发，`allowed_write_roots` 放开源码和测试，`protected_paths` 保护治理、CI、迁移和门禁脚本
- `scope_mode: exact_files` 适合文档修补、配置小改或安全敏感任务，`scope_files` 是硬边界
- 开发者应在任务状态或 PR 中维护变更清单，说明跨模块修改为什么服务于当前任务

## `task-board.md` 更新与归档机制

`task-board.md` 需要始终保持“当前最新状态”，但不会在任务完成后直接删除任务卡。

推荐机制：

- 活跃任务保留在 `Active Tasks`
- 已完成或已取消任务先进入 `Completed Tasks`
- `Completed Tasks` 最多保留最近 20 条任务卡
- 超过 20 条后，把最旧的 completed/canceled 任务卡移动到 `.claw/task-archive.md`

这意味着：

- 完成任务不会自动清空
- 任务历史不会丢失
- `task-board.md` 会维持较短、适合日常协作的窗口
- 更老的完成记录统一进入 `task-archive.md`

## `docs/specs/` 规则 | Spec-Driven Delivery

以下情况默认必须先建 spec：

- 新功能
- 跨模块改动
- API 或数据结构变更
- 非平凡重构
- 预计会跨会话或跨智能体交接的工作
- 预计会由两个或更多开发者并行推进并最终合并的工作

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

## 身份与授权文件 | Identity And Assignment Files

`.claw/developers/DEV-xxx.yaml` 推荐记录：

- `developer_id`
- `display_name`
- `role`
- `public_key`
- `git_platform`
- `git_username`
- `ssh_signing_key_fingerprint`
- `status`
- `managed_by`
- `allowed_scopes`
- `role_sharing_exception`
- `allowed_until`

`.claw/assignments/TASK-xxx.yaml` 推荐记录：

- `task_id`
- `assignee`
- `assigned_by`
- `status`
- `branch`
- `scope_mode`
- `allowed_write_roots`
- `scope_files`
- `protected_paths`
- `touch_policy`
- `shared_contracts`
- `task_boundary`
- `change_manifest_required`
- `signature`

约束：

- `assigned_by` 应指向 `MANAGER-xxx`
- 普通功能开发推荐 `scope_mode: task_bounded_broad_code`，精确文件范围只用于任务文档、任务状态和受保护路径
- 若使用 `scope_mode: exact_files`，所有目标文件都必须落在 `scope_files` 内
- 默认签名方案是 SSH commit signing
- Git author name/email 只可作为辅助信息，不能单独作为强身份依据
- 默认一个 Git 平台账号只绑定一个 active 身份；同账号多身份必须使用不同 SSH signing key fingerprint
- PR CI 或 assignment-only 检查必须运行 `scripts/check-assignment.py`；本地开发必须先运行 `scripts/dev-login.py`
- 本地开发前必须运行 `scripts/dev-login.py`，用 `public_key` 验证当前用户确实持有对应私钥
- `.claw-local/identity.json` 和 `.ai-dev-local/identity.json` 是本机缓存，不是事实源，必须加入 `.gitignore`

`.claw/tasks/TASK-xxx.md` 推荐记录：

- 当前状态
- 已完成内容
- 修改范围
- 已运行验证
- 阻塞点
- 交接说明

这些文件是协作协议，不是完整权限系统。真正的权限、分支保护、签名验签和 CI 门禁仍应由 Git 平台或外部工具执行。

## 团队状态汇总 | Team Status Aggregation

`team-status.md` 是管理者视图，用来快速查看团队成员和贡献状态。它应由脚本生成，不应手工长期维护。

推荐状态枚举：

- `contribution_status`: `not_started` / `assigned` / `claimed` / `in_progress` / `code_submitted` / `review_requested` / `merged` / `blocked` / `canceled`
- `validation_status`: `not_run` / `partial` / `passed` / `failed` / `unknown`
- `integration_status`: `not_ready` / `waiting_review` / `ready_to_merge` / `merging` / `integrated` / `blocked`

事实源优先级：

1. `.claw/developers/*.yaml`
2. `.claw/assignments/*.yaml`
3. `.claw/tasks/*.md`
4. `.claw/task-board.md`
5. `.claw/integration-queue.md`
6. Git/PR/CI 外部证据（如已写入 task status 或由后续脚本接入）

## 最佳实践 | Best Practices

- 保持 `current-status.md` 足够短，确保 AI 每次都能快速读完
- 把项目遵循此技能的要求同时落在 `README.md` 和 `AGENTS.md`
- 用 ID 和引用代替长段复制
- 把交接信息放到 `task-board.md` 或 feature spec，而不是聊天记录
- 异步多开发者协作时，把单人进度放到 `.claw/tasks/TASK-xxx.md`，让 `current-status.md` 保持短小
- 管理者查看团队状态时，使用 `scripts/summarize-team-status.py` 生成 `.claw/team-status.md`
- 异步多人开发时，使用项目经理授权、SSH commit signing 和 `scripts/check-assignment.py` 做开发前门禁
- 普通功能任务放开源码/测试写入根路径，用任务 spec、验收标准和变更清单约束工作边界
- 本地开发会话开始时，先用 `scripts/dev-login.py` 报告并验证当前身份，再让 AI 或开发者修改代码
- 如果 `dev-login.py` 未运行、运行失败或缺少 task/branch/files 等必要输入，AI agent 必须停止，不得先修改再补验证
- 同一 Git 账号兼任多个身份时，用不同 SSH signing key 区分项目经理身份和开发者身份
- 共享接口、数据结构、配置 key 和迁移顺序先写进 spec，再让下游任务并行
- 功能实现偏离原设计时，先更新 spec 再继续写代码
- 老项目先更新 `PROJECT-BASELINE.md`，再做大范围 legacy 改动
- 当 `Completed Tasks` 超过 20 条时，及时归档最旧任务到 `task-archive.md`
- 让 AI 记录项目知识，不记录临时思考过程

## 避免 | Anti-Patterns

- 每次会话都读完整个状态目录和所有 spec
- 在多个文件里复制同一个事实
- 把 `task-board.md` 当成 bug 列表或设计文档
- 项目已经接入此协议，但 `README.md` 或 `AGENTS.md` 没有明确声明必须自动使用该技能
- 任务完成后直接删除任务卡，导致交接和审计历史丢失
- 没有验证就写“测试通过”或“问题已解决”
- 先写大量代码，再补 feature spec
- 要求老项目一次性补齐全部历史文档
- 把 `current-status.md` 写成流水账
- 把管理者口令、开发者 token、私钥或可复用密钥提交到仓库
- 多个开发者频繁改同一个 `current-status.md` 来记录个人进度
- 手工维护 `team-status.md` 并把它当成事实源
- 没有任务授权、任务边界和受保护路径规则就让两个分支同时修改高风险共享文件
- 用过窄的 `scope_files` 逼开发者把必要调用链修复塞进错误模块
- 只依赖 Git author name/email 判断开发者身份
- 只记住私钥路径但不重新做 challenge-response 验证
- 在 `scripts/dev-login.py` 返回 `allowed` 前修改源码、测试、配置、迁移、feature spec 或任务状态
- 把聊天声明、历史记忆、缓存路径或 `scripts/check-assignment.py` 当成本地身份登录替代品
- 让开发者自行扩大自己的授权范围或添加团队成员
- 同一个 Git 账号和同一把 SSH signing key 同时代表项目经理和开发者

## 参考文档 | References

- [SKILL.md](SKILL.md)
- [STATE-MODEL.md](STATE-MODEL.md)
- [examples/README.md](examples/README.md)
- [CHANGELOG.md](CHANGELOG.md)

---

*版本 3.8.0 | 面向 AI 多智能体协作、老项目渐进接入、项目级技能声明、任务归档、身份化异步并行交付、硬阻断登录式身份验证、任务边界宽代码权限和项目经理门控授权的项目状态与交付规范*

<!-- cc-aidev-guidelines-common:begin -->
## AI Development Protocol

This project follows the `cc-aidev-guidelines-common` skill.

- All AI agents must automatically use this skill before project analysis, planning, implementation, testing, or maintenance.
- If the current agent does not have this skill installed, install it first from GitHub: https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common
- When the environment supports `AGENTS.md`, treat both this README section and `AGENTS.md` as mandatory project instructions.

本项目遵循 `cc-aidev-guidelines-common` 技能规范。

- 所有 AI 智能体在进行项目分析、规划、编码、测试和维护前，必须自动使用此技能。
- 如果当前智能体尚未安装此技能，必须先从 GitHub 安装：https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common
- 如果当前环境支持 `AGENTS.md`，应将 README 中的本节和 `AGENTS.md` 同时视为必须遵守的项目级指令。
<!-- cc-aidev-guidelines-common:end -->
