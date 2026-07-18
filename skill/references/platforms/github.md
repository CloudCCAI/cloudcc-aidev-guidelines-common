# GitHub

仅在 `change_review=true` 且 platform 为 `github` 时读取本文。

- 从 `templates/github-workflows/check-assignment.yml` 安装可选 assignment 检查。
- 分支、PR 标题或正文必须包含完整 TASK ID；解析器同时支持 `TASK-001` 和 `TASK-bimo-001`。
- 启用 branch protection，要求 review 和必要检查通过。
- 门禁启用时，把 PR author 映射到 active developer，并检查 assignment、branch、changed files 和 protected paths。
- 将 PR URL、review 状态和真实 CI 证据写回对应 TASK 状态。

GitHub token 和其他 secret 只能使用平台 secret store 或本地忽略配置，不能进入 `.claw/`。
