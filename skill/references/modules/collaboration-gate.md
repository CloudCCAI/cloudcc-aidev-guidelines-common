# 多人协作门禁模块

仅在 manifest 的 `modules.collaboration_gate` 为 `true`，或 legacy 项目已经存在 `.claw/developers/`、`.claw/assignments/` 时读取本文。

## 依赖与事实源

- 本模块要求 `project_state=true`。
- `.claw/collaboration-config.yaml`：公开的身份绑定、管理者、assignment、登录和签名策略；启用模块时引导确认。
- `.claw/developers/*.yaml`：长期公开身份和角色。
- `.claw/assignments/*.yaml`：管理者授权的任务、分支和写入范围。
- `.claw/tasks/*.md`：开发者日常执行进展。
- `.claw/integration-queue.md`：真实并行分支的合并顺序。
- `.claw/team-status.md`：按需生成的管理者视图，不是事实源。

## 硬门禁

启用模块后，任何源码、测试、运行配置、迁移、生成资产、FEAT 或 TASK 状态写入前，必须在当前会话运行：

```bash
python3 scripts/dev-login.py .claw \
  --ssh-key /path/to/private-key \
  --task TASK-user-001 \
  --files path/to/intended-file
```

只有返回 `allowed` 才能继续。聊天声明、Git author、操作系统用户名、历史记忆、本地缓存和 `check-assignment.py` 都不能代替 SSH challenge-response 登录。

## 身份和授权

- 只有项目经理可以创建、暂停、撤销 developer 或扩大 assignment。
- developer 记录保存公开 SSH key、Git 平台账号、签名指纹、`document_slug` 和状态；不得保存私钥或 token。
- assignment 保存 assignee、manager、task、branch、scope mode、write roots、exact files、protected paths、touch policy 和验证引用。
- `exact_files` 用于窄文档或敏感文件。
- `task_bounded_broad_code` 用于正常代码链路；protected path 仍需 exact authorization。

CI/评审使用：

```bash
python3 scripts/check-assignment.py .claw \
  --developer DEV-user \
  --task TASK-user-001 \
  --branch feat/TASK-user-001-description \
  --files path/to/file
```

## 并行交付

1. 管理者登记身份并为每个任务创建 assignment。
2. 开发者在授权分支登录，只写自己的任务状态和授权文件。
3. CI 检查 review author、branch、changed files 和 assignment。
4. 集成负责人按 integration queue 合并并运行真实验证。
5. 需要团队摘要时运行 `summarize-team-status.py .claw --write`。

不要因为模块启用就创建空 developers/assignments 目录；只有真实成员或授权存在时才创建。
