---
kind: devops
version: 2
updated_at: YYYY-MM-DDTHH:MM:SSZ
updated_by: ai
verification_status: partial
---

# 项目部署运维手册

`devops.md` 是构建、运行、部署和运维知识的事实源。

## 构建

### 命令

```bash
# 安装依赖
[install command]

# 构建项目
[build command]
```

### 产物

- 输出目录：`[dist/build/target]`
- 主产物：`[artifact]`

### 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| [依赖] | [版本] | [说明] |

## 启动

### 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `PORT` | 服务端口 | 3000 | 是 |
| `DB_HOST` | 数据库地址 | localhost | 是 |

### 配置文件

- 主配置：`[path/to/config]`
- 日志配置：`[path/to/log-config]`

### 启动命令

```bash
# 开发环境
[dev command]

# 生产环境
[prod command]
```

## 依赖服务

- 数据库：[类型 + 地址]
- 缓存：[类型 + 地址]
- 消息队列：[类型 + 地址]
- 其他：[服务说明]

## 部署与发布

1. [部署步骤 1]
2. [部署步骤 2]
3. [回滚方式]

## 排障

### [问题标题]

- 现象：[现象]
- 原因：[仅写已验证或明确标注为推断]
- 处理：

```bash
[处理命令]
```

## 健康检查

- 健康检查地址：`[url]`
- 预期响应：[response]
- 日志位置：`[log path]`

## 维护规则

- 仅记录已验证可用的命令、步骤和配置。
- 若步骤未验证，必须显式标注 `pending verification`。
- 仅在构建、启动、部署或运维知识发生变化时更新。
