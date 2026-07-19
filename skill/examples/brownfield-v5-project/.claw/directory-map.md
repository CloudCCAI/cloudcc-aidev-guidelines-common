---
kind: directory-map
schema_version: 5
init_status: complete
init_completed_at: 2026-01-02T00:08:00Z
init_confirmed_by: sample-maintainer
updated_at: 2026-01-02T00:08:00Z
updated_by: sample-maintainer
project_mode: brownfield
---

# 目录地图

| 路径 | 职责 | 入口 | 证据 |
|---|---|---|---|
| `src/` | 既有库存领域行为 | `src/inventory.py` | verified |
| `.claw/` | 项目管理状态 | `manifest.yaml`、`current-status.md` | verified |
| `docs/specs/` | 基线和未来功能设计 | `PROJECT-BASELINE.md` | verified |
| `docs/help/` | 面向客户的产品帮助和使用手册 | `README.md` | verified |
| `docs/design/` | 详细功能和流程设计 | `README.md` | verified |

不要根据这个小型示例推断缺失的生产或部署目录。
