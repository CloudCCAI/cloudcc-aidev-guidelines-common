---
kind: decisions
schema_version: 5
init_status: complete
init_completed_at: 2026-01-01 00:05:00
init_confirmed_by: sample-owner
architecture_init_status: complete
architecture_reviewed_at: 2026-01-01 00:05:00
architecture_confirmed_by: sample-owner
updated_at: 2026-01-01 00:05:00
updated_by: sample-owner
project_mode: greenfield
---

# 架构与技术决策

## ARCHITECTURE

- 证据状态：`planned`。
- 系统类型：一个 HTTP API 服务。
- 技术栈：Python、FastAPI、PostgreSQL 和 pytest。
- 边界：API 层调用应用服务；持久化适配器负责 SQL 访问。
- 数据：PostgreSQL 是事实源；笔记写入使用数据库事务。
- 外部系统：初始范围内没有外部系统。
- 部署：一个无状态服务加一个托管数据库。
- 非功能约束：身份验证访问、结构化日志和可恢复的数据库备份。

## ADR 索引

接受非平凡选择前，不需要 ADR。
