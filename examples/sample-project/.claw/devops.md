---
kind: devops
version: 3
updated_at: 2026-03-29T11:00:00Z
updated_by: ai
verification_status: verified
---

# 项目部署运维手册

## 构建

### 命令

```bash
npm ci
npm run build
```

### 产物

- 输出目录：`dist/`
- 主产物：`dist/server.js`

### 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Node.js | 20.x | 运行时 |
| PostgreSQL | 15 | 主数据库 |
| Redis | 7 | 限流和缓存 |

## 启动

### 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `PORT` | 服务端口 | 3000 | 是 |
| `DB_URL` | 数据库连接 | - | 是 |
| `REDIS_URL` | Redis 连接 | - | 是 |
| `JWT_SECRET` | JWT 密钥 | - | 是 |

### 配置文件

- 主配置：`config/app.env`
- 日志配置：`config/logger.ts`

### 启动命令

```bash
npm run start
```

## 依赖服务

- 数据库：PostgreSQL `localhost:5432`
- 缓存：Redis `localhost:6379`
- 其他：无

## 部署与发布

1. 执行 `npm ci && npm run build`
2. 执行 `npm run test`
3. 将 `dist/` 与环境变量配置发布到目标环境
4. 发布后访问 `/health`
5. 若失败，回滚到上一个构建产物

## 排障

### 登录接口返回 429 过多

- 现象：测试环境或低流量环境也频繁触发限流
- 原因：`inferred` 测试环境共享 Redis key
- 处理：

```bash
redis-cli DEL rate_limit:login:test-user
```

## 健康检查

- 健康检查地址：`http://localhost:3000/health`
- 预期响应：`{"status":"ok"}`
- 日志位置：`logs/app.log`
