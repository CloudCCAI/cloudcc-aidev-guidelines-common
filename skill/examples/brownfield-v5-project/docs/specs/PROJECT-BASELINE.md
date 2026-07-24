---
kind: project-baseline
schema_version: 5
title: Inventory service project baseline
status: verified
init_status: complete
init_completed_at: 2026-01-02 00:04:00
init_confirmed_by: sample-maintainer
owner_role: shared
updated_at: 2026-01-02 00:04:00
updated_by: sample-maintainer
project_mode: brownfield
---

# PROJECT-BASELINE

## 已验证事实

- `src/inventory.py` 将可用库存计算为现有库存减去预留库存，并保证结果非负。
- 既有调用方依赖函数名及其两个位置参数。

## 推断事实

- 单一模块表明可能存在库边界，但没有打包元数据。

## 待验证事项

- 此示例未体现生产调用方、支持的 Python 版本和部署归属。
- 修改行为前，向维护者索取调用方证据，并运行真实下游测试套件。

## 历史风险热点

- 可用量规则对兼容性敏感，因为调用方可能依赖将负值归零的行为。

## 接管计划

- 保留公开函数契约，只记录下一项真实变更所需的事实。
