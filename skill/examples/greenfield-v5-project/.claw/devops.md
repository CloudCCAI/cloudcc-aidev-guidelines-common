---
kind: devops
schema_version: 5
init_status: complete
init_completed_at: 2026-01-01T00:07:00Z
init_confirmed_by: sample-owner
updated_at: 2026-01-01T00:07:00Z
updated_by: sample-owner
project_mode: greenfield
verification_status: pending
devops_assets_root: DevOps
environment_names: "DEV, UAT, PROD"
---

# 构建、运行、测试与运维

- 构建：`pending verification`；应用骨架建立后再确认。
- 运行：`pending verification`；计划入口为 `src/api/main.py`。
- 测试：`pending verification`；计划使用 pytest 运行。
- 部署：容器化服务和托管 PostgreSQL，平台尚待选择。
- 环境：只记录变量名，绝不在本文件中写入密钥值。
- 下一项验证动作：第一个实现任务必须运行并记录实际命令。

<!-- cc-aidev:devops-assets:begin -->
## 环境资产清单

| 环境 | Dockerfile | 环境变量示例 |
| --- | --- | --- |
| `DEV` | `DevOps/DEV/Dockerfile` | `DevOps/DEV/.env.example` |
| `UAT` | `DevOps/UAT/Dockerfile` | `DevOps/UAT/.env.example` |
| `PROD` | `DevOps/PROD/Dockerfile` | `DevOps/PROD/.env.example` |
<!-- cc-aidev:devops-assets:end -->
