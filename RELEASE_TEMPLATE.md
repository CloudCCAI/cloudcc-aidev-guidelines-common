# Release Template

Use this template when publishing a new version of the skill.

发布新版本时可直接使用这个模板。

---

## Title

`vX.Y.Z` - Short release title

`vX.Y.Z` - 发布标题

## Summary | 概要

### English

Briefly describe what changed in this release and why it matters.

### 中文

简要说明这一版做了什么改动，以及这些改动为什么重要。

## Highlights | 主要变化

### English

- Added:
- Changed:
- Fixed:
- Removed:

### 中文

- 新增：
- 调整：
- 修复：
- 移除：

## State Model Impact | 状态模型影响

### English

- Does this release change file roles?
- Does it change read or update triggers?
- Does it change front matter or enums?

### 中文

- 这一版是否调整了文件职责？
- 是否改变了读取或更新触发规则？
- 是否修改了 front matter 或枚举值？

## Migration Notes | 升级说明

### English

- Required actions for existing users:
- Optional improvements:
- Breaking changes:

### 中文

- 旧版本用户需要执行的操作：
- 可选升级项：
- 不兼容变更：

## Validation | 验证方式

### English

- Ran `scripts/init-state.sh`
- Ran `scripts/validate-state.py`
- Validated example state files
- Checked docs and templates

### 中文

- 已执行 `scripts/init-state.sh`
- 已执行 `scripts/validate-state.py`
- 已校验示例状态文件
- 已检查文档与模板

## Files Of Interest | 重点文件

- `SKILL.md`
- `STATE-MODEL.md`
- `README.md`
- `templates/`
- `scripts/`
- `examples/`

## Suggested Release Body | 推荐发布正文

### English

```markdown
## Summary

- [Key change 1]
- [Key change 2]
- [Key change 3]

## Migration Notes

- [Migration step]

## Validation

- [Validation item]
```

### 中文

```markdown
## 概要

- [关键改动 1]
- [关键改动 2]
- [关键改动 3]

## 升级说明

- [升级步骤]

## 验证

- [验证项]
```
