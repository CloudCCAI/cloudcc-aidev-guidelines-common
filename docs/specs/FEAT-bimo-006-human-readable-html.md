---
kind: feature-spec
schema_version: 5
feature_id: FEAT-bimo-006
work_type: new_feature
title: "设计与规格的人类可读 HTML"
status: verified
init_status: complete
init_completed_at: 2026-07-23T08:54:52Z
init_confirmed_by: "Bimo"
owner_role: shared
owner_slug: bimo
created_at: 2026-07-23T08:49:33Z
created_by: "Bimo"
created_by_slug: bimo
created_by_source: global_git_config_user_name
created_by_developer_id: none
contributors: ["Bimo"]
task_ids: ["TASK-bimo-010"]
related_decisions: none
related_issues: none
policy_version: 3
updated_at: 2026-07-23T09:05:16Z
updated_by: "Bimo"
---

# FEAT-bimo-006 - 设计与规格的人类可读 HTML

## 背景与目标

- `docs/design/` 和 `docs/specs/` 中的 Markdown 同时承载机器协议字段和详细设计，适合版本管理与 AI 读取，但人类需要逐文件查找、理解 front matter 和长篇章节，审阅成本较高。
- 在不改变 Markdown 事实源地位的前提下，为每份 Markdown 生成一份同目录、同 basename、离线可读的 HTML，降低产品、研发和评审人员的阅读成本。
- 创建或修改上述目录中的 Markdown 后，同一工作流必须刷新对应 HTML，避免阅读视图过期。

## 范围

### 范围内

- 在技能中提供确定性的 Markdown 到同名 HTML 生成脚本。
- 扫描 `docs/design/**/*.md` 和 `docs/specs/**/*.md`，确保范围内每份 Markdown 都有配对 HTML，包括 README 和以下划线开头的 Markdown 模板。
- 每个输入文件默认输出到相同目录并使用相同 basename，例如 `docs/specs/FEAT-x.md` 对应 `docs/specs/FEAT-x.html`；Markdown 继续作为唯一事实源，HTML 标记为派生阅读视图。
- 每份 HTML 提供本文目录、FEAT 状态标签、重要元数据摘要、章节折叠、源文件名和生成时间。
- HTML 自包含并可离线打开，不要求项目安装 Node.js、Pandoc 或第三方 Python 包。
- 在 `SKILL.md`、项目状态模块、模板、示例和测试中声明并验证同步规则：技能创建或修改 design/specs Markdown 后必须刷新 HTML。
- 保持 legacy v4 与 v5 项目兼容；目录不存在或没有可渲染文档时也能生成明确的空状态页面。
- 发布时将技能版本从 `5.0.4` 升级到下一版本。

### 范围外

- 不用 HTML 替代 Markdown，也不从 HTML 反向写回 Markdown。
- 不建立汇总门户、Web 服务、在线部署、实时文件监听或浏览器编辑能力。
- 不渲染 `.drawio`、图片源文件或 `docs/help/`。
- 不自动改写历史 Markdown 的内容和语言。
- 不引入通用静态站点生成器或新的包管理链路。

## 当前行为与目标行为

- 当前：技能创建 FEAT 和 design 文档后只保留 Markdown；仓库没有聚合阅读入口，也没有文档变更后的 HTML 同步动作。
- 目标：技能完成 design/specs Markdown 写入后运行生成器，原子更新该 Markdown 同目录下的同名 HTML；人类直接打开配对文件阅读对应设计或规格。

## 方案设计

- 新增 `skill/scripts/generate-project-docs-html.py`，既可接收单个 Markdown 路径并刷新其配对 HTML，也可接收项目根目录批量同步 design/specs；使用 `--write` 原子写入目标文件。
- 生成器只使用 Python 标准库：解析 YAML front matter 的常用标量与列表字段，并把受支持的 Markdown 标题、段落、列表、任务项、表格、引用、代码块和链接转换为经过转义的 HTML。
- 页面把 front matter 中的 `feature_id`、`title`、`status`、`owner_slug`、`updated_at` 等字段转换为紧凑摘要，完整原始元数据默认不展示。
- 页面按单个源文件生成本文目录和正文，并使用原生 `details` 元素实现章节折叠，不依赖客户端框架或网络。
- 输出包含生成器版本、生成时间、源文件名和源内容摘要，并明确声明 HTML 不是真实事实源。
- 批量模式按排序后的相对路径读取输入；所有写入使用同目录临时文件加原子替换。
- 技能规则要求任何 AI 工作流在创建或修改 design/specs Markdown 后刷新对应 HTML；校验器逐一检查配对 HTML 是否存在且源内容摘要匹配。

## 接口与数据影响

- 新命令：
  `python3 <skill>/scripts/generate-project-docs-html.py /path/to/project --write`；
  `python3 <skill>/scripts/generate-project-docs-html.py /path/to/document.md --write`。
- 新派生文件：每份 design/specs Markdown 对应的同目录同名 `.html`。
- `validate-state.py` 增加文档阅读视图的存在性和新鲜度检查；不修改既有 Markdown schema、FEAT/TASK ID 或事实源优先级。
- 示例项目和初始化模板增加 HTML 阅读视图说明；初始化仅补缺，不覆盖人工文件。

## 任务拆分

- 用户确认本 FEAT 后创建一个实现 TASK，完成生成器、协议说明、模板、示例、测试、版本升级和验证。

## 验收标准

- 给定 design/specs Markdown，命令能为每份输入生成无外部资源依赖的同目录同名 HTML。
- 页面能正确显示中文、标题、段落、列表、任务项、表格、代码块、引用、链接和关键 front matter。
- 页面能通过本文目录导航、识别 FEAT 状态，并显示源文件名。
- 输入顺序变化不会导致非确定性的文档排序；连续生成在忽略生成时间字段后内容稳定。
- Markdown 被创建或修改后，技能规则明确要求刷新对应 HTML；缺失或摘要不匹配时状态校验失败并给出修复命令。
- HTML 不参与 FEAT/TASK 事实解析，删除后可完全由 Markdown 重建。
- 现有自动化测试、示例验证和项目状态校验全部通过。

## 风险与回滚

- 风险：自实现 Markdown 子集与完整 Markdown 语法存在差异；通过明确支持范围和覆盖现有模板语法的测试控制。
- 风险：依赖 mtime 判断新鲜度会受复制文件或 Git checkout 影响；生成文件记录源内容摘要，校验直接比较摘要。
- 风险：同目录生成文件会增加文件数量；使用确定的同 basename 规则降低查找和清理成本。
- 回滚：删除生成脚本、同步规则和派生 HTML 即可恢复原行为，Markdown 事实源不受影响。

## 交接说明

- 事实源：本 FEAT、`skill/SKILL.md`、`skill/STATE-MODEL.md`、`skill/references/modules/project-state.md`、`skill/templates/`、`skill/scripts/` 和 `skill/examples/`。
- 用户已确认：每份 Markdown 对应一份同目录同 basename 的 HTML；Markdown 给 AI 读取，HTML 给人阅读。
