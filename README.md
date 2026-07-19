# cc-aidev-guidelines-common

用于开发和发布 AI 软件项目初始化、状态管理、多人协作门禁与代码评审管理 Skill。

当前 Skill 版本：`5.0.3`。唯一权威版本位于 [skill/SKILL.md](skill/SKILL.md) 的 `metadata.skill_version`。

## 核心能力

- 以 `.claw/manifest.yaml` 判断项目未初始化、初始化中、已完成或 legacy 状态。
- 所有新写入的人类可读项目管理内容使用规范中文模板，并兼容读取历史语言标记。
- 基于仓库证据建议 Greenfield/Brownfield，并由用户确认。
- 逐文件问答初始化 goals、ARCHITECTURE、目录职责、DevOps、空 task board 和多任务 current status。
- 客户环境确认后，按环境初始化根目录 `DevOps/`；客户未定时可明确接受 `DEV/UAT/PROD` 三套预留文件。
- 初始化 `docs/help` 产品使用手册目录和 `docs/design` 功能/流转设计目录，并生成中文索引。
- 通过开关独立控制项目状态、多人协作门禁和代码合并申请。
- 新 FEAT/TASK 带用户名，并按用户分别从 `001` 递增。
- 同时管理多个用户、多个聊天窗口和多个活跃任务。
- grandfather 已存在的旧 FEAT/TASK，不强制批量迁移。
- 以热、温、冷和事件触发实现渐进加载。

项目状态目录只使用 `.claw/`；本地私密配置只使用 `.claw-local/`。

## 仓库结构

| 路径 | 用途 |
|---|---|
| `skill/SKILL.md` | 轻量预检、模块路由和硬门槛 |
| `skill/STATE-MODEL.md` | 字段、事实源、兼容和冲突规则 |
| `skill/state-catalog.json` | 初始化器与校验器共享的机器清单 |
| `skill/references/` | 按初始化、模块和平台加载的详细流程 |
| `skill/templates/core/` | 初始化核心模板 |
| `skill/templates/devops-assets/` | 每环境 Dockerfile、变量示例和 DevOps 目录说明模板 |
| `skill/templates/project-docs/` | 产品帮助和详细设计文档目录索引模板 |
| `skill/templates/project-state/` | FEAT、TASK 和事件模板 |
| `skill/templates/collaboration-gate/` | 身份、assignment 和门禁配置模板 |
| `skill/templates/change-review/` | 评审配置和平台资源 |
| `skill/scripts/` | 预检、初始化、编号、聚合、门禁和校验工具 |
| `skill/tests/` | v5 和 legacy 回归测试 |
| `skill/examples/` | Greenfield、Brownfield 和 legacy 示例 |
| `.claw/` | 本仓库自身的项目状态 |
| `docs/specs/` | 本仓库的设计规格 |

`skill/` 是独立可发布包；仓库根目录用于开发该 Skill。

## 首次接入项目

先确保目标项目根目录已经存在，再做只读预检：

```bash
mkdir -p /path/to/project
python3 /path/to/skill/scripts/project-preflight.py /path/to/project --json
```

未初始化时开始引导：

```bash
python3 /path/to/skill/scripts/project-onboarding.py start /path/to/project \
  --mode greenfield \
  --project-state on \
  --collaboration-gate off \
  --change-review off
```

恢复、查看和完成：

```bash
python3 /path/to/skill/scripts/project-onboarding.py resume /path/to/project --json
python3 /path/to/skill/scripts/project-onboarding.py status /path/to/project --json
python3 /path/to/skill/scripts/project-onboarding.py devops-assets /path/to/project --recommended-environments
python3 /path/to/skill/scripts/project-onboarding.py finalize /path/to/project --confirmed-by user
```

兼容入口：

```bash
bash /path/to/skill/scripts/init-state.sh /path/to/project
```

初始化器不会创建虚假首任务，也不会预建 issue、test、archive、integration、team 或空门禁目录。

## 三个模块开关

| 模块 | 默认 | 作用 |
|---|---:|---|
| `project_state` | 开 | 核心状态、会话意图、FEAT/TASK、热温冷加载 |
| `collaboration_gate` | 关 | manager/developer、assignment、SSH 登录和并行授权 |
| `change_review` | 关 | Codeup/GitHub change request 与合并检查 |

`collaboration_gate` 要求 `project_state`。关闭模块只停止加载和执行，不删除历史资料。

初始化后可显式调整开关；启用模块会进入待确认状态并创建缺失配置：

```bash
python3 /path/to/skill/scripts/configure-modules.py set /path/to/project \
  --project-state on \
  --collaboration-gate off \
  --change-review on
```

## 运行期流程

新会话中，如果用户目标不清楚，AI 会用开放式问题确认本次操作；新需求、老功能迭代和 bug 只是建议例子，不限制其他任务。

开发类工作通常遵循：

```text
讨论 → FEAT 草稿 → 用户确认 → TASK 拆分 → 实现 → 真实验证 → 评审
```

新文档格式：

```text
FEAT-<username>-<personal-sequence>-<description>.md
TASK-<username>-<personal-sequence>-<description>.md
```

使用脚本分配个人编号，避免并发聊天重复：

```bash
python3 /path/to/skill/scripts/allocate-document-id.py feature \
  --project-root /path/to/project \
  --description user-login
```

未显式传入 `--owner` 时，命名空间依次使用全局 Git 配置的 `user.name`、当前项目本地 Git 配置的 `user.name`、操作系统用户名。

聚合多个活跃任务：

```bash
python3 /path/to/skill/scripts/generate-current-status.py /path/to/project/.claw --write
```

## Legacy 项目

已有 `.claw/` 但没有 manifest 的项目继续按 v4 profile 读取和校验，不自动改名或补字段。

显式采用 v5 时先登记历史边界：

```bash
python3 /path/to/skill/scripts/project-onboarding.py adopt /path/to/project \
  --mode brownfield \
  --confirmed-by user
```

该命令内部先调用 legacy snapshot；也可用 `snapshot-legacy-documents.py` 单独创建边界或用 `--verify` 检查漂移。旧 `FEAT-001`/`TASK-001` 与新 `FEAT-bimo-001`/`TASK-bimo-001` 可以共存。policy 生效后，新文件必须使用带用户名的格式。

## 多人协作门禁

启用门禁后，任何实现或交付状态写入前必须完成本地 SSH challenge-response：

```bash
python3 /path/to/skill/scripts/dev-login.py .claw \
  --ssh-key /path/to/key \
  --task TASK-bimo-001 \
  --files path/to/file
```

CI/评审使用 `check-assignment.py`。聊天身份、Git author、本地缓存和 assignment-only 检查都不能代替登录。

## 测试环境推送

启用 `change_review` 后，用户明确要求“推送到测试环境”时使用：

```bash
python3 /path/to/skill/scripts/push-test-environment.py \
  --source-branch feat/TASK-bimo-001-description \
  --target-branch dev \
  --remote origin
```

测试环境冲突按 source-branch-wins 自动处理；此规则不适用于生产发布。门禁同时启用时仍需先完成登录和 assignment 检查。

## 校验与开发

```bash
python3 skill/scripts/validate-state.py .claw
python3 -m unittest discover -s skill/tests -p 'test_*.py' -v
bash -n skill/scripts/init-state.sh skill/scripts/ensure-agent-guidance.sh
git diff --check
```

发布前还应运行 Skill 标准校验，并验证 Greenfield、Brownfield、legacy、模块开关、个人编号并发和多任务聚合 fixture。

## 项目级指令锚点

采用项目必须在根 `README.md` 和 `AGENTS.md` 保留受控声明块：

```bash
bash /path/to/skill/scripts/ensure-agent-guidance.sh /path/to/project
```

该声明要求所有 AI Agent 在项目工作前加载本 Skill；README/AGENTS 是指令锚点，不是项目状态文件。

<!-- cc-aidev-guidelines-common:begin -->
## AI 开发协议

本项目遵循 `cc-aidev-guidelines-common` 技能规范。

- 所有 AI 智能体在进行项目分析、规划、编码、测试和维护前，必须自动使用此技能。
- 如果当前智能体尚未安装此技能，必须先从 GitHub 安装：https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common/tree/main/skill
- 如果当前环境支持 `AGENTS.md`，应将 README 中的本节和 `AGENTS.md` 同时视为必须遵守的项目级指令。
<!-- cc-aidev-guidelines-common:end -->
