---
kind: directory-map
schema_version: 5
init_status: complete
init_completed_at: 2026-01-01T00:06:00Z
init_confirmed_by: sample-owner
updated_at: 2026-01-01T00:06:00Z
updated_by: sample-owner
project_mode: greenfield
---

# 目录地图

| 路径 | 职责 | 入口 | 证据 |
|---|---|---|---|
| `src/api/` | HTTP 传输和请求验证 | `src/api/main.py` | planned |
| `src/application/` | 用例和事务边界 | 服务模块 | planned |
| `src/persistence/` | PostgreSQL 适配器和迁移 | 仓储模块 | planned |
| `tests/` | 单元和 API 验证 | pytest | planned |
| `docs/help/` | 面向客户的产品帮助和使用手册 | `README.md` | verified |
| `docs/design/` | 详细功能和流程设计 | `README.md` | verified |

允许的依赖从 API 流向应用接口，并从适配器流向这些接口。应用代码不得导入 HTTP 框架或具体数据库适配器。
