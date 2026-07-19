# Codeup

仅在 `change_review=true` 且 platform 为 `codeup` 时读取本文。

1. 用 `store-yunxiao-token.py` 把个人 token 保存到本地 `.claw-local/codeup.env`。
2. 用 `configure-codeup-change-request.py` 解析 repository/project/target branch 默认值。
3. 用 `create-codeup-change-request.py` 创建 change request。
4. 将 URL 写回对应 TASK 状态。

缺少 `YUNXIAO_TOKEN` 时必须在 API 调用前停止。token 不得写入 `.claw/`、源码、spec、日志或 Git 历史。

三个脚本共享同一套 `.claw-local/codeup.env` 解析、优先级和原子写入逻辑。命令行显式值优先于进程环境变量，进程环境变量优先于本地文件；轮换 token 必须合并保留已有 repository、project 和 target branch 配置。文件权限固定为仅当前用户可读写的 `0600`。

分支、标题和描述使用完整新旧兼容 TASK ID，例如 `TASK-bimo-001` 或 legacy `TASK-001`。描述至少包含 scope、verification、risk、rollback 和状态文件路径。

`repositoryId` 是 API 路径参数；数字 `sourceProjectId`、`targetProjectId` 放在请求体。同仓请求可从数字 repository id 推导两个 project id，full-path repository id 必须显式提供 project ids。
