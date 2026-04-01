---
kind: current-status
version: 2
updated_at: YYYY-MM-DDTHH:MM:SSZ
updated_by: ai
phase: discovery
active_task: "[当前正在推进的单句任务]"
next_action: "[下一步动作]"
read_next:
  goals: false
  decisions: false
  issue_list: false
  test_report: false
  devops: false
---

# 项目当前状态

`current-status.md` 是唯一的热状态入口。每次会话先读它，再按需读取其他状态文件。

## 快照

- 会话目标：
- 当前关注点：
- 阻塞状态：无 / 见 `ISSUE-xxx`

## 本次会话进展

### 已完成
- [已完成事项]

### 进行中
- [进行中事项]

### 下一步
- [下一步 1]
- [下一步 2]

## 修改文件

- `path/to/file` - [修改原因]

## 已验证事实

- Build: [passed/failed/not-run]
- Tests: [passed/failed/partial/not-run]
- Lint: [passed/failed/not-run]
- 依赖变更: 无 / `[package]`

## 待确认

- [需要用户或后续会话确认的事项]

## 相关状态文件

- `goals.md` - [仅在目标或范围变化时填写]
- `decisions.md` - [仅在技术选型影响当前任务时填写]
- `issue-list.md` - [仅在存在活跃问题时填写]
- `test-report.md` - [仅在本次实际运行测试后填写]
- `devops.md` - [仅在涉及构建/部署/环境时填写]

## 维护规则

- 保持简短，只记录当前快照。
- 不复制完整 issue、ADR 或测试详情。
- 如需历史归档，放到独立历史文件，不放在这里。
