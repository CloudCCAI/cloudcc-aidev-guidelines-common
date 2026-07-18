# 项目状态模块

仅在 manifest 的 `modules.project_state` 为 `true` 时读取本文。

## 会话入口

每个新 AI 会话先读 `.claw/current-status.md`。如果用户已经清楚说明目标，直接继续；如果目标不清楚，用开放式问题确认本次要做什么。

同时读取 manifest 的 `language`。新建或明确重写的 FEAT、TASK、核心状态和事件文件，其标题、说明和用户可读内容必须使用该语言；frontmatter 字段、枚举、ID、路径、命令和原始验证输出保持机器协议原值。选择模板时，`en` 使用 catalog 的规范路径，`zh-CN` 使用 `templates/locales/zh-CN/` 下的镜像路径。

可以提示“新需求、老功能迭代、修改 bug”等常见例子，但它们不是封闭菜单。分析、文档、测试、重构、发布、部署、评审和项目管理等意图同样有效。

保留两个概念：

- `session_intent`：用户目标的稳定摘要，不得被分类覆盖。
- `work_kind`：可扩展的路由提示。

## 开发类流程

新功能、非平凡迭代、bug 修复、跨模块修改、API/数据变更和非平凡重构通常执行：

```text
讨论现状、目标和约束
  → 确认范围与验收标准
  → 创建 FEAT 草稿
  → 用户确认 FEAT
  → 拆分 TASK
  → 实现
  → 真实验证
  → 评审与关闭
```

讨论完成至少要明确当前/目标行为、In/Out Scope、验收、约束、风险和未决项。确认 FEAT 前可以只读分析，不得先实现后补设计。

## FEAT 命名

新文件使用：

```text
FEAT-<author-slug>-<personal-sequence>-<description>.md
```

规范 ID 是 `FEAT-<author-slug>-<personal-sequence>`。序号按作者独立递增，从 `001` 开始且不复用。description 只属于路径。

作者解析顺序：已登录 developer 的 `document_slug`、Git `user.name`、操作系统用户名、用户确认。Git/OS 身份只用于署名，不构成授权。

## TASK 命名

所有新任务使用：

```text
TASK-<owner-slug>-<personal-sequence>-<description>.md
```

规范 ID 是 `TASK-<owner-slug>-<personal-sequence>`。同一用户的所有任务类型共享序列。转交只更新 `assignee`，不重命名文件。

使用确定性分配器，避免多个聊天窗口重复编号：

```bash
python3 scripts/allocate-document-id.py feature \
  --project-root /path/to/project \
  --description user-login
```

## 多任务热状态

`.claw/current-status.md` 可以同时索引多个活跃任务。生成器按字段事实源聚合：

- task board：队列、优先级、依赖、协调状态和引用。
- task status：执行状态、进展、验证、阻塞、下一步和交接。
- assignment：授权身份、分支和可写范围。
- FEAT：需求、设计和验收。

```bash
python3 scripts/generate-current-status.py /path/to/project/.claw --write
```

生成器使用锁和原子替换，保持热文件少于 60 行。新会话只展开所选任务及其关联 FEAT/issue/decision/assignment。

## 事件文件

- 首次 bug、风险或阻塞：创建 `issue-list.md`。
- 首次真实验证：创建 `test-report.md`。
- 首次归档：创建 `task-archive.md`。
- 首次真实并行集成：创建 `integration-queue.md`。
- 管理者查询团队状态：生成 `team-status.md`，不要手工维护。

## Legacy 兼容

已有 `FEAT-001-*`、`TASK-001` 和旧核心文件不强制改名或补字段。首次采用 v5 时用 legacy index 固化边界；边界之后的新文件必须使用带用户名的格式。读取器和交叉引用长期同时接受两种 ID。
