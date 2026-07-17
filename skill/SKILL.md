---
name: cc-aidev-guidelines-common
description: 将紧凑的项目状态持久化到 `.claw` 或 `.ai-dev`，通过索引化热状态、单任务状态文件、功能 spec、项目经理门控授权、Codeup 评审和测试环境推送，支持 AI 辅助软件交付、跨会话项目记忆、任务交接、ADR、问题跟踪、测试记录、多开发者协作、授权门禁和 Agent 编码规范。
metadata:
  skill_version: "4.1.3"
---

# AI Agent 项目状态与交付协议

使用本技能把项目状态保存为可读、可更新、可审计的持久化文件，使 AI Agent 能在跨会话和多人协作中继续交付。

## 1. 执行入口

### 核心原则

- 当前权威版本是 `metadata.skill_version: "4.1.3"`。其他文档与此冲突时，以该字段为准。
- 每个事实只能有一个事实源；其他文件只做摘要或引用。
- 必须区分已验证事实、推断和待确认项，不得伪造测试、构建、部署或问题状态。
- 默认最小读取、触发式更新；不得每次加载全部状态和 spec。
- 保留用户明确的目标和决策，不得用 AI 摘要静默覆盖用户意图。

### 递进阅读路径

按任务需要逐级阅读，不要一开始展开全部内容：

1. 先阅读“项目接入”，解析状态目录并判断 `Greenfield Mode` 或 `Brownfield Adoption Mode`。
2. 再阅读“最小状态读取”，只加载当前工作需要的事实源。
3. 开始实现、排期或交接前，阅读“单任务交付流程”和“写入与验证”。
4. 仅在身份门禁或多人并行条件出现时，继续阅读“多开发者协作与授权门禁”。
5. 仅在创建 Codeup change request、配置 GitHub 检查或推送测试环境时，阅读“平台评审与环境交付”。
6. 需要完整字段、枚举和冲突规则时，再打开 [STATE-MODEL.md](STATE-MODEL.md)；需要样例时打开 [examples/README.md](examples/README.md)。

## 2. 项目接入

### 状态目录解析

默认使用 `.claw/`；已有项目可使用 `.ai-dev/`。按以下顺序解析：

1. 存在 `.claw/` 时使用 `.claw/`。
2. 否则，存在 `.ai-dev/` 时使用 `.ai-dev/`。
3. 两者都不存在时，初始化 `.claw/` 和 `docs/specs/`。
4. 两者同时存在时，遵循项目声明；没有声明时优先 `.claw/`，检查 `.ai-dev/` 偏差并在 `current-status.md` 记录合并计划。

标准结构：

```text
.claw/
├── current-status.md
├── goals.md
├── decisions.md
├── issue-list.md
├── task-board.md
├── task-archive.md
├── test-report.md
├── devops.md
├── team-status.md
├── integration-queue.md
├── developers/DEV-xxx.yaml
├── assignments/TASK-xxx.yaml
└── tasks/TASK-xxx.md

docs/specs/
├── _feature-spec-template.md
├── _project-baseline-template.md
├── PROJECT-BASELINE.md
└── FEAT-xxx-feature-name.md
```

`tasks/` 由初始化脚本创建。`developers/` 和 `assignments/` 仅在启用多人身份与任务授权时按需创建；不要在普通项目中预建空目录，因为目录存在会触发硬身份门禁。

初始化项目：

```bash
bash scripts/init-state.sh /path/to/project
```

项目根目录的 `README.md` 和 `AGENTS.md` 必须保留受控声明块，说明：

- 项目遵循 `cc-aidev-guidelines-common`。
- 所有 AI Agent 在项目工作前必须加载本技能。
- 技能缺失时，从 `https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common/tree/main/skill` 安装。

使用 `scripts/ensure-agent-guidance.sh <project-root>` 创建或刷新声明块。

### 选择交付模式

#### `Greenfield Mode`

- 运行 `scripts/init-state.sh`，确认根 `README.md` 和 `AGENTS.md` 声明块。
- 先填写 `current-status.md`、`goals.md` 和第一个任务卡，再创建 `.claw/tasks/TASK-001.md`。
- 非平凡实现前创建 `docs/specs/FEAT-xxx-*.md`。

#### `Brownfield Adoption Mode`

- 先创建最小状态骨架，不要一次性回填全部历史。
- 广泛修改 legacy 实现前，从模板创建 `docs/specs/PROJECT-BASELINE.md`。
- baseline 必须将内容标记为 `verified`、`inferred` 或 `pending verification`。
- 从当前活跃工作开始执行 `task-board + task status + spec`，只在旧模块被修改或缺失上下文形成阻塞时回填。

## 3. 最小状态读取

### 事实源

| 事实 | 事实源 |
|---|---|
| 当前阶段、活跃任务、下一步 | `current-status.md` |
| 任务队列、优先级、依赖、看板状态和状态文件指针 | `task-board.md` |
| 单任务进展、变更文件、验证、阻塞和交接 | `.claw/tasks/TASK-xxx.md` |
| 产品范围、成功标准和约束 | `goals.md` |
| 技术决策与撤销 | `decisions.md` |
| 问题、阻塞和风险 | `issue-list.md` |
| 已验证测试结果 | `test-report.md` |
| 构建、运行、部署和运维 | `devops.md` |
| 老项目基线、架构推断和未知项 | `docs/specs/PROJECT-BASELINE.md` |
| 需求、设计、验收标准和持久交接 | `docs/specs/FEAT-xxx-*.md` |
| 超出看板保留窗口的已完成或已取消任务 | `task-archive.md` |
| 开发者身份、Git 账号、SSH 指纹和长期范围 | `.claw/developers/DEV-xxx.yaml` |
| 授权人、被授权人、分支、任务范围和受保护路径 | `.claw/assignments/TASK-xxx.yaml` |
| 集成分支、合并顺序和验证门禁 | `integration-queue.md` |
| 团队成员与贡献摘要 | `team-status.md`（派生视图） |

冲突时保留事实源，修复摘要文件。`team-status.md` 与其他来源冲突时必须重新生成，不得反向修改事实源以匹配它。

异步并行时，`.claw/tasks/TASK-xxx.md` 是开发者日常进展的事实源，`task-board.md` 是项目经理/集成负责人维护的协调索引。除非 assignment 在 `scope_files` 中明确授权，开发者不得仅为记录开工而修改 `task-board.md`；看板暂时为 `ready` 而任务状态为 `in_progress` 是可接受的。

### 渐进式披露

1. 每次会话先读 `current-status.md`。
2. 实现、优先级或交接工作再读 `task-board.md`。
3. 只展开活跃任务指向的 `.claw/tasks/TASK-xxx.md`。
4. 任务有 `spec_path` 时，非平凡实现前读对应 spec 或 baseline。
5. 仅在任务触发时读取 issue、decision、test、devops、identity、assignment 或 integration 文件。

保持热文件紧凑：

- `current-status.md` 少于 60 行，只保留热索引和最新快照。
- `task-board.md` 每个任务卡少于 20 行，不放验证日志、变更列表或长交接。
- `.claw/tasks/TASK-xxx.md` 少于 120 行且只记录一个任务的当前状态；长期设计和历史转移到 spec、archive 或 test report。
- `Completed Tasks` 最多保留 20 张任务卡，更旧卡片移入 `task-archive.md`。

## 4. 单任务交付流程

### 判断是否需要 Spec

工作属于新功能、跨模块修改、API 或数据结构变更、非平凡重构、或可能跨 Agent/会话交接时，必须在主实现前创建或更新一份主 spec。小型独立修复可只使用紧凑任务卡和单任务状态文件。

### 会话开始

1. 解析状态目录并先读 `current-status.md`。
2. 实现、排期或交接时，读 `task-board.md` 和活跃任务状态文件。
3. 任务有 `spec_path` 时，主实现前读 spec；Brownfield 项目的广泛 legacy 修改前读 baseline。
4. 检查是否触发硬身份门禁；触发时，在任何文件修改前完成“多开发者协作与授权门禁”中的登录与授权检查。
5. 多开发者工作仅读当前任务引用的 developer、assignment、task status 和 integration queue。
6. 项目经理查询团队状态时，先使用 `scripts/summarize-team-status.py` 生成或读取 `team-status.md`。

### 执行中

- 只在可复用事实变化时更新状态，使用紧凑增量，不记录思维过程或逐行日记。
- 将任务进展、变更文件、验证、阻塞和交接写入 `.claw/tasks/TASK-xxx.md`。
- 仅在状态、优先级、依赖、阻塞、分支、评审链接、spec/assignment/task-status 指针或下一步变化时更新任务卡。
- 实现偏离 spec 时，在代码修改前或同时更新 spec。
- 只有真实命令或检查已运行时才能更新 `test-report.md`。
- 授权或身份检查失败时立即停止，请项目经理或用户修正记录。

### 会话结束

- 将 `current-status.md` 重写为最新紧凑快照，不追加会话历史。
- 更新已触发的任务状态、spec、baseline、issue、decision、test 或 devops 文件，不得机械回写全部文件。
- 异步开发者只更新自己的任务状态；项目经理或集成负责人在协调状态变化时刷新 `task-board.md`、`current-status.md` 和 `integration-queue.md`。
- 管理者视图来源变化时重新生成 `team-status.md`。

### 按触发条件读取或更新

| 文件 | 读取或更新触发 |
|---|---|
| `goals.md` | 范围、优先级、里程碑、成功标准或约束变化 |
| `decisions.md` | 做出、替换或质疑非平凡技术决策 |
| `issue-list.md` | 发现或解决 bug、阻塞、回归或风险 |
| `task-board.md` | 实现、排期、交接、依赖、阻塞或看板协调字段变化 |
| `.claw/tasks/TASK-xxx.md` | 任务进展、变更文件、验证、阻塞或交接变化 |
| `task-archive.md` | 查询已归档历史，或 `Completed Tasks` 超过 20 张卡 |
| `test-report.md` | 已真实运行测试、构建或质量门禁 |
| `devops.md` | 构建、启动、环境变量、部署、运维或事故处理 |
| `PROJECT-BASELINE.md` | Brownfield 接管，或 legacy 理解被验证、修正或形成阻塞 |
| `FEAT-xxx-*.md` | 非平凡需求、设计、验收标准、实现进度或交接变化 |
| `developers/*.yaml` | 添加、暂停、撤销或轮换开发者身份 |
| `assignments/*.yaml` | 项目经理分配、撤销、延期或调整授权范围 |
| `integration-queue.md` | 集成分支、合并顺序、验证门禁或集成负责人变化 |
| `team-status.md` | 管理者查询团队状态，或派生视图的事实源变化 |

## 5. 写入与验证

- 状态文件使用 YAML front matter，时间使用 `YYYY-MM-DDTHH:MM:SSZ`，ID 使用 `TASK-xxx`、`ISSUE-xxx`、`ADR-xxx`、`FEAT-xxx`、`MANAGER-xxx` 和 `DEV-xxx`。
- 任务状态使用 `todo`、`ready`、`in_progress`、`blocked`、`review`、`done` 或 `canceled`。`in_progress` 任务必须有非空 `owner_role`。
- 活跃任务必须通过 `task_status_path` 引用真实的 `.claw/tasks/TASK-xxx.md`；`spec_path` 必须引用真实 spec 或 baseline。
- `current-status.md` 不得包含 `本次会话进展`、`修改文件`、`已验证事实` 等会话日志章节。
- `issue-list.md` 中的根因必须标明为 verified 或 inferred；`decisions.md` 必须记录方案胜出原因；`devops.md` 只能放已验证命令或明确标记的待验证步骤。
- assignment 不得包含 `private_key`、`password`、`token`、`secret` 或 `bearer_token`。
- 合并前运行 `scripts/check-assignment.py`；广范围代码授权不能绕过产品边界，change manifest 必须能解释每个变更模块为何属于授权任务。

校验项目状态：

```bash
python3 scripts/validate-state.py /path/to/project/.claw
```

## 6. 多开发者协作与授权门禁（按需）

仅在身份目录、任务授权或多人并行协作出现时阅读并执行本节。

### 触发硬身份门禁

出现以下任一条件时自动启用硬身份门禁：

- `.claw/developers/` 或 `.ai-dev/developers/`
- `.claw/assignments/` 或 `.ai-dev/assignments/`
- 活跃任务包含 `assignment_path`
- assignment 包含 `local_login_required: true`

### 身份与秘密

- 异步并行以 Git 分支和平台评审为交付介质，仓库文件只作持久协调层，不替代 CI、分支保护和 code review。
- 仓库只保存公开身份材料、授权和状态，不得保存管理者口令、bearer token、私钥或可复用 secret，即使加密也不可。
- 默认绑定 Git 平台账号、`public_key` 和 SSH commit signing 指纹。一个 Git 账号默认只对应一个 active `developer_id`。
- 新团队默认使用 SSH commit signing；已有 GPG 管理体系的团队可继续使用 GPG，Sigstore/gitsign 只作 CI、制品签名和供应链审计的高级选项。
- 同账号多身份时，每个身份必须使用不同 SSH signing key fingerprint 并记录 `role_sharing_exception`。同账号与同指纹不得同时表示 `MANAGER-xxx` 和 `DEV-xxx`。
- `.claw-local/identity.json` 或 `.ai-dev-local/identity.json` 只能缓存私钥路径和公开身份元数据，必须被 Git 忽略，不能作为已登录证明。

### 执行本地身份检查

门禁启用后：

1. 修改源码、测试、运行配置、迁移、生成资产、feature spec、任务状态或其他实现文件前，必须让 `scripts/dev-login.py` 在当前会话针对目标任务和文件返回 `allowed`。
2. `dev-login.py` 必须从本地私钥推导 public key 和 fingerprint，匹配 active developer 记录，对一次性 challenge 签名并使用登记公钥验签，再检查可选 assignment 范围。
3. 聊天声明、历史记忆、Git author/email、已知用户名、项目角色和缓存私钥路径都不是身份证明，不存在绕过方式。
4. `dev-login.py` 缺失、无法运行、缺私钥路径、缺任务/分支/目标文件，或返回任何 `blocked_*` 时，必须在编辑前停止。
5. `scripts/check-assignment.py` 只用于 CI 或 assignment-only 检查，不能代替本地 SSH challenge-response 登录。

### 执行项目经理授权

- 必须先登记至少一个 `MANAGER-xxx`。只有项目经理可新建、暂停、撤销或轮换 developer 记录，以及新建、撤销、延期或扩大 assignment 范围。
- assignment 必须包含 `assigned_by: MANAGER-xxx`、`assignee: DEV-xxx`、`branch`、`touch_policy`、`status` 和 `signature` 或外部验证引用。
- 编辑前必须检查：identity active、assignment active、assignee 匹配、branch 匹配（已知时）、任务边界与目标文件授权通过。

`scope_mode` 规则：

- `exact_files`：用于文档、配置或敏感的窄范围任务；所有变更必须匹配 `scope_files`。
- `task_bounded_broad_code`：用于常规功能实现；源码和测试可在 `allowed_write_roots` 内修改，命中 `protected_paths` 时必须由项目经理在 `scope_files` 精确授权，任务 spec 和验收标准仍是业务边界。
- 启用 `task_bounded_broad_code` 时应设置 `change_manifest_required`，变更清单必须解释每个模块与授权任务的关系。
- `allowed_write_roots`、`protected_paths` 和 developer `allowed_scopes` 中的裸目录按递归根解析；`scope_files` 的裸路径保持精确匹配，除非显式写入 glob。

### 完成异步并行交付

1. 项目经理登记自己和开发者的公开身份。
2. 项目经理为每个并行任务创建任务卡和 assignment。
3. 开发者在授权分支内运行 `scripts/dev-login.py`，仅处理授权任务并更新自己的 `.claw/tasks/TASK-xxx.md`。
4. CI 或平台自动化使用 `scripts/check-assignment.py` 检查 review author、branch 和 changed files；分支保护必须要求检查通过。
5. 集成负责人按 `integration-queue.md` 合并、执行真实验证、更新 `test-report.md` 和热状态。

项目经理需要团队摘要时，运行：

```bash
python3 scripts/summarize-team-status.py /path/to/project/.claw --write
```

## 7. 平台评审与环境交付（按需）

### 创建 Codeup 评审

Codeup change request 是默认评审流程。

1. 使用 `scripts/store-yunxiao-token.py` 将 `YUNXIAO_TOKEN` 保存到本地 `.claw-local/codeup.env`，不得写入 Git 跟踪文件或日志。
2. 在每个 Codeup 项目中运行 `scripts/configure-codeup-change-request.py`，解析并保存 `CODEUP_REPOSITORY_ID`、`CODEUP_SOURCE_PROJECT_ID`、`CODEUP_TARGET_PROJECT_ID`、`CODEUP_TARGET_BRANCH` 和 `CODEUP_CREATE_FROM`。
3. 使用 `scripts/create-codeup-change-request.py` 创建 change request。缺失 `YUNXIAO_TOKEN` 时必须在 API 调用前停止并显示云效 token 文档链接。
4. `repositoryId` 是请求路径参数；数字 `sourceProjectId` 和 `targetProjectId` 放入 JSON body。同仓 change request 可默认使用数字 `repositoryId`；`repositoryId` 是完整路径时必须显式提供两个 project id。

平台约定见 `templates/platforms/codeup/`。GitHub 只作可选示例；需要时将 `templates/github-workflows/check-assignment.yml` 复制到采用项目的 `.github/workflows/check-assignment.yml`。

### 推送到测试环境

用户说“推送到测试环境”或“push to the test environment”时，默认运行 `scripts/push-test-environment.py`。

- 工作树必须干净。
- 默认以当前分支为开发分支，以 `dev` 为测试环境分支。
- 脚本执行 fetch，切换并 fast-forward `dev`，合并开发分支并推送 `dev`。
- 冲突使用 source-branch-wins，即采用开发分支版本。
- 成功后恢复原分支；使用 `--no-restore` 时除外。

## 8. 资源导航

| 路径 | 用途 |
|---|---|
| `templates/*.md` | 核心状态模板 |
| `templates/parallel/` | developer、assignment 和 task status 模板 |
| `templates/docs/` | feature spec 和 project baseline 模板 |
| `templates/platforms/codeup/` | Codeup change request 约定 |
| `scripts/init-state.sh` | 项目状态初始化 |
| `scripts/ensure-agent-guidance.sh` | 项目根声明块维护 |
| `scripts/dev-login.py` | 本地 SSH challenge-response 身份门禁 |
| `scripts/check-assignment.py` | CI/assignment-only 授权检查 |
| `scripts/store-yunxiao-token.py` | 本地云效 token 保存 |
| `scripts/configure-codeup-change-request.py` | Codeup 项目默认参数配置 |
| `scripts/create-codeup-change-request.py` | Codeup change request 创建 |
| `scripts/push-test-environment.py` | 测试环境分支推送 |
| `scripts/summarize-team-status.py` | 团队状态派生视图 |
| `scripts/validate-state.py` | 状态结构和引用校验 |

完整文件语义、字段、枚举、读写策略和冲突优先级见 [STATE-MODEL.md](STATE-MODEL.md)。完整示例见 [examples/README.md](examples/README.md)。

## 9. 禁止行为

- 启动时读取全部状态或全部 spec。
- 在多个文件独立维护同一事实，或把 `current-status.md`、`task-board.md` 写成日志。
- 未运行真实验证就写入通过结果，或将推断当作 verified 事实。
- 非平凡实现先写代码再补 spec，或要求 Brownfield 项目一次性回填全部历史。
- 手工维护 `team-status.md` 并将它当作事实源。
- 使用 Git author/email、聊天上下文、记忆、缓存或 `scripts/check-assignment.py` 绕过 `scripts/dev-login.py`。
- 开发者自行添加成员、扩大 assignment、越过任务边界或未授权修改 `protected_paths`。
