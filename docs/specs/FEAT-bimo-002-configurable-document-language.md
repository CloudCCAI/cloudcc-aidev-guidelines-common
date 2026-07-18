---
kind: feature-spec
schema_version: 5
feature_id: FEAT-bimo-002
work_type: enhancement
title: "Configurable document language"
status: verified
init_status: complete
init_completed_at: 2026-07-18T12:16:16Z
init_confirmed_by: Bimo
owner_role: shared
owner_slug: bimo
created_at: 2026-07-18T12:16:09Z
created_by: "Bimo"
created_by_slug: bimo
created_by_source: user_confirmed
created_by_developer_id: none
contributors:
  - "Bimo"
task_ids:
  - TASK-bimo-006
related_decisions: none
related_issues: none
policy_version: 3
updated_at: 2026-07-18T12:39:25Z
updated_by: "Bimo"
---

# FEAT-bimo-002 - Configurable document language

## 背景与目标

- 当前 v5 初始化模板和生成器中的人类可读内容以英文或中英混合形式输出，项目不能声明统一的文档语言。
- 在 `.claw/manifest.yaml` 增加语言配置，让初始化问答、核心文件、FEAT、TASK 和派生视图按同一语言生成。
- 新项目必须明确选择语言，不再静默采用英文。

## 范围

### In Scope

- manifest 增加顶层 `language`，新建项目支持 `zh-CN`、`en` 和初始化中间值 `pending`。
- 初始化和显式 legacy adoption 支持 `--language`；未提供时先保存 manifest，再把语言作为第一个待确认问题。
- 为中文和英文提供确定性的核心、FEAT/TASK、事件及派生视图文案。
- 所有脚本读取同一个语言事实源；校验器、schema、catalog、示例、README 和协议文档保持一致。
- 已安装旧项目保持兼容：v4 不新增字段，缺少 `language` 的早期 v5 按 `en` 读取。
- 语言变化只影响随后新建或明确重写的人类可读内容，不自动批量翻译历史文件。

### Out Of Scope

- 自动翻译历史文档或用户代码、代码注释、第三方内容。
- 翻译机器字段名、状态枚举、文档 ID、路径、命令、API 名称和原始验证输出。
- 本版本不内置 `zh-CN`、`en` 之外的确定性模板资源。

## 当前行为与目标行为

- Current：manifest 没有语言字段；核心模板多为英文，事件模板和派生视图中英混合。
- Target：新初始化先确认语言，所有新生成的人类可读项目管理内容统一使用该语言，机器协议保持稳定。

## 方案设计

- manifest 使用单一标量：`language: pending | zh-CN | en`。
- `pending` 只允许出现在非 ready 初始化；语言未确认时不得生成依赖语言的核心文件。
- 英文模板保留在 catalog 的规范路径；中文模板放在 `templates/locales/zh-CN/`，脚本通过共享语言解析器选择资源。
- `generate-current-status.py` 和 `summarize-team-status.py` 使用同一语言解析器和本地化文案表。
- status/preflight 输出返回 `language`，让 Agent 在任何写入前完成路由。
- 现有 manifest 缺字段时解析为 legacy 默认 `en`；新 skill 版本生成的 manifest 必须显式包含该字段。

## 接口与数据影响

- `project-onboarding.py start|adopt` 新增 `--language {zh-CN,en}`。
- `configure-modules.py set` 新增可选 `--language`，用于显式更新未来写入语言；不会重写既有文件。
- `manifest.schema.json`、`state-catalog.json` 和运行时 validator 增加语言规则。
- `skill_version` 从 `5.0.0` 递增补丁位为 `5.0.1`，新文档策略升级为 `policy_version: 3`。

## 任务拆分

- `TASK-bimo-006`：实现语言配置、双语模板路由、生成器本地化、兼容校验和测试。

## 验收标准

- 不传 `--language` 启动新项目时，只建立可恢复控制面，并把语言作为第一个问题。
- 使用 `--language zh-CN` 时，核心文件、FEAT/TASK 和派生视图的人类可读标题与说明为中文。
- 使用 `--language en` 时，对应内容为英文。
- ready manifest 不允许 `language: pending`；新版本 manifest 缺少 language 校验失败。
- 早期 v5 manifest 缺少 language 和所有无 manifest 的 v4 项目继续通过兼容校验。
- 现有项目文件不会因配置变化被静默翻译或覆盖。

## 风险与回滚

- 风险：本地化标题会影响依赖固定英文 section 的解析器；必须为关键 section 增加中英文别名测试。
- 风险：复制模板会产生漂移；测试必须验证每个 catalog 模板都有受支持语言资源。
- 回滚：保留英文规范模板和旧 manifest 的英文兼容行为，可撤回 `5.0.1` 脚本而不修改既有文档。

## 交接说明

- 先读 manifest schema、onboarding reference、模板解析器和本 FEAT；不要把语言配置扩展成代码本地化或历史文档迁移。
