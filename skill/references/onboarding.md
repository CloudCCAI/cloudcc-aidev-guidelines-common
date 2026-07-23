# 项目初始化

仅在 `.claw/manifest.yaml` 不存在、初始化未完成或标记为 `needs_review` 时读取本文。

## 目录

- 预检与显式 legacy adoption
- 模块开关与项目模式
- 开始、恢复与模块重配置
- 核心文件问答与初始化状态
- 完成与校验

## 预检

先运行只读预检：

```bash
python3 scripts/project-preflight.py /path/to/project --json
```

目标项目根目录必须已经存在；全新项目先运行 `mkdir -p /path/to/project`，再执行预检和初始化。初始化器不会替用户猜测或创建项目根路径。

预检只读取目录、代码入口、构建清单、Git 历史和现有 `.claw/`，不得运行构建、安装、测试或部署命令。

判定规则：

- 没有 `.claw/`：未初始化。
- 有 `.claw/` 但没有 manifest：legacy v4 项目；保持原文件，不自动迁移。
- manifest 为 `in_progress`：恢复初始化。
- manifest 为 `ready`：进入运行期流程。
- manifest 为 `needs_review`：先处理漂移或待确认项。

legacy 项目可以无限期继续使用 v4 profile。只有用户明确要求采用 v5 时才执行：

```bash
python3 scripts/project-onboarding.py adopt /path/to/project \
  --mode brownfield \
  --project-state on \
  --collaboration-gate off \
  --change-review off \
  --confirmed-by bimo
```

`adopt` 先建立不可覆盖的 legacy index，再创建 manifest 和缺失的新核心文件；index 中的既有文件保持原样并按旧 schema 读取。不得用 `start` 代替显式采用。

## 确认模块

新建或明确重写的人类可读项目管理内容固定使用简体中文，不再询问语言。新 manifest 记录 `language: zh-CN`；机器字段、枚举、FEAT/TASK ID、路径、命令、代码标识符和原始验证输出保持协议值。早期 v5 缺少 language 或记录 `en` 时继续兼容读取；未完成初始化中的 `pending` 会在恢复写操作时归一为 `zh-CN`，既有文件不自动翻译。

询问三个开关：

- `project_state`：建议开启；管理核心状态、FEAT、TASK 和会话流程。
- `collaboration_gate`：默认关闭；管理身份、角色、assignment 和并行授权。
- `change_review`：默认关闭；管理 Codeup/GitHub change request。

`collaboration_gate=true` 要求 `project_state=true`。不要静默修改用户选择。`change_review` 可以独立启用。

先确认模块，再决定是否询问项目模式。`project_state=false` 时将 `project_mode` 设为 `not_applicable`，跳过 Greenfield/Brownfield 与项目状态核心文件问答。

## 确认项目模式

仅在 `project_state=true` 时执行。AI 根据证据给出建议，用户最终确认：

- `greenfield`：当前作用域没有必须保持兼容的既有行为、数据、API 或部署契约。
- `brownfield`：必须理解并保护既有实现或契约。

文件数量不是唯一依据。脚手架可能是 Greenfield；没有 Git 历史的运行系统也可能是 Brownfield。把证据区分为 `verified`、`inferred` 和 `pending verification`。

## 开始或恢复

使用初始化器创建 manifest、checkpoint 和已启用模块的核心骨架：

```bash
python3 scripts/project-onboarding.py start /path/to/project \
  --mode greenfield \
  --project-state on \
  --collaboration-gate off \
  --change-review off
```

恢复或查看下一批问题：

```bash
python3 scripts/project-onboarding.py resume /path/to/project --json
python3 scripts/project-onboarding.py status /path/to/project --json
```

旧入口 `scripts/init-state.sh` 只是该初始化器的 `.claw` 包装器。

初始化器还会通过中文受控声明块幂等创建项目根 `README.md`、`AGENTS.md`，让后续 Agent 在工作前加载本 Skill，并确保 `.gitignore` 包含 `.claw-local/`；历史项目已有的完整受控块和所有块外内容保持不变。

Greenfield/Brownfield 模式确认后，初始化器还会幂等创建：

```text
docs/
  specs/     # Brownfield baseline 或首次真实 FEAT 出现时创建
  help/      # 面向用户的产品帮助和使用手册
    README.md
  design/    # 功能、交互、业务流转、状态和异常流程设计
    README.md
```

初始化器创建 `docs/design/README.md` 或 Brownfield `docs/specs/PROJECT-BASELINE.md` 后，同时生成同目录、同 basename HTML。Markdown 是事实源，HTML 是人类阅读派生视图；以后修改 design/specs Markdown 时必须运行 `scripts/generate-project-docs-html.py <Markdown 路径> --write`。

`help` 与 `design` 使用小写路径，以避免 `Docs`/`docs` 在不同文件系统上的大小写冲突。README 是目录职责和索引，不代表已经存在经确认的产品文档。重复 start/adopt/sync 只恢复缺失文件，绝不覆盖用户已经编写的 README。

初始化相关 CLI 使用以下退出约定：`0` 表示当前步骤完成且无需继续输入，`2` 表示本次创建/更新已经成功但仍需继续问答，`4` 表示需要修复后再完成，`5` 表示内容冲突，`6` 表示参数或模块组合非法。自动化脚本不得把 `2` 当成写入失败。

## 初始化后调整模块

模块开关变化必须显式执行，不删除已有资料：

```bash
python3 scripts/configure-modules.py set /path/to/project \
  --project-state on \
  --collaboration-gate off \
  --change-review on
```

启用模块会创建缺失的模块配置并把已 ready 的 manifest 置为 `needs_review`，从该配置继续问答；关闭模块只停止加载和执行。语言不可通过模块配置修改。配置代码评审平台时使用：

```bash
python3 scripts/configure-modules.py review /path/to/project \
  --platform codeup \
  --target-branch main \
  --confirmed-by bimo
```

## 核心文件问答

每轮只问 1～3 个问题。先从仓库证据预填，再让用户确认：

1. `goals.md`：目标用户、范围、非目标、成功标准、约束。
2. Brownfield baseline：现状、兼容义务、风险热点、未知项。
3. `decisions.md` 的 `ARCHITECTURE`：系统类型、技术栈、边界、数据、外部依赖、部署和非功能约束。
4. `directory-map.md`：目录职责、入口、允许依赖和禁止依赖。
5. `devops.md`：已验证或待验证的构建、运行、测试、部署和环境要求。
6. 已启用模块配置。
7. 空 `task-board.md` 和多任务 `current-status.md`。

详细功能设计需要长期独立维护时写入 `docs/design/`，并由 FEAT 引用；FEAT 仍负责范围、关键决策、任务拆分和验收，不在两处重复维护同一事实。功能经过验证并需要用户说明时更新 `docs/help/`，不得在实现前臆造产品行为。

事件文件不在初始化时创建：issue、test report、archive、integration queue、team status、FEAT 和 TASK 都由真实事件触发。

### DevOps 环境资产

`DevOps/` 不随 `start` 空骨架提前创建。完成 `devops.md` 问答时，先确认客户实际环境名称；每个环境使用不同的 `Dockerfile`，并配套只含变量名或非密钥示例值的 `.env.example`：

```text
DevOps/
  README.md
  <environment>/
    Dockerfile
    .env.example
```

客户暂未确定时，建议预留 `DEV`、`UAT`、`PROD`。只有用户接受建议后才执行：

```bash
python3 scripts/project-onboarding.py devops-assets /path/to/project \
  --recommended-environments
```

客户已确认自定义环境时，重复传入 `--environment`：

```bash
python3 scripts/project-onboarding.py devops-assets /path/to/project \
  --environment DEV \
  --environment Customer-UAT \
  --environment PROD
```

命令幂等且只做增量创建：已有 `Dockerfile`、`.env.example` 和 README 保持原样，不自动删除已记录环境；环境清单变化后由用户复核 `.claw/devops.md`。生成的 Dockerfile 是明确不可运行的占位文件，确认基础镜像、构建阶段、制品、端口、健康检查和启动命令后才可使用。`.gitignore` 必须忽略 `DevOps/**/.env`，但不得忽略 `.env.example`。

从 Skill 5.0.2 起，非 legacy 的 v5 项目必须具备已确认的 `environment_names` 及对应资产，才能把 `devops` 标为 `complete` 并最终进入 ready。

## 文件初始化状态

核心内容文件使用：

- `not_started`
- `in_progress`
- `awaiting_confirmation`
- `complete`
- `needs_review`

同时记录 `init_completed_at` 和 `init_confirmed_by`。`complete` 只表示首次基线已确认，不表示文件冻结。未知信息可以明确写为 `pending verification`，但不能保留未解释模板占位符。

用初始化器更新状态，避免手工破坏 frontmatter：

```bash
python3 scripts/project-onboarding.py mark /path/to/project goals \
  --status complete --confirmed-by bimo
```

`goals`、`decisions`、`directory-map`、`devops` 和 Brownfield baseline 的模板包含 `<!-- cc-aidev:onboarding-incomplete -->`。真实答案写入并经用户确认前不得删除；标记仍存在时，`mark --status complete` 会以退出码 `2` fail-fast 且不改状态。

## 完成

所有当前模式和已启用模块要求的核心文件均为 `complete` 后：

```bash
python3 scripts/project-onboarding.py finalize /path/to/project --confirmed-by bimo
python3 scripts/validate-state.py /path/to/project/.claw --strict-v5
```

finalize 必须幂等；存在冲突、缺失输入或校验失败时保持 `in_progress`/`needs_review`，不得覆盖用户内容或伪造 ready。
