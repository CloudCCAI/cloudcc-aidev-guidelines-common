---
kind: devops
version: 4
updated_at: 2026-07-19T13:01:40Z
updated_by: Bimo
verification_status: verified
---

# 项目部署运维手册

`devops.md` 是构建、运行、部署和运维知识的事实源。

## 构建与静态检查

- 本项目无独立编译产物；Skill 发布单元为 `skill/`。
- Python 语法：`PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-final-pycache python3 -m compileall -q skill/scripts skill/tests`（已验证）。
- Shell 语法：`bash -n skill/scripts/init-state.sh skill/scripts/ensure-agent-guidance.sh`（已验证）。

## 运行与测试

- 单元测试：`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skill/tests -p 'test_*.py'`（86 项通过）。
- 本仓库状态：`python3 skill/scripts/validate-state.py .claw`（legacy v4 通过）。
- v5 fixtures：对 Greenfield/Brownfield 示例运行 `validate-state.py --strict-v5`（均通过）。
- legacy fixture：对 `skill/examples/sample-project/.claw` 运行普通校验（通过）。

## 依赖服务

- 核心初始化、编号、聚合与校验只依赖 Python 标准库。
- Git/SSH、Codeup/GitHub 仅在对应能力实际启用时需要。
- 系统 `quick_validate.py` 依赖可选 PyYAML；当前环境缺少该包，因此使用同等 frontmatter 规则的 Ruby YAML 检查完成验证。

## 部署与发布

- 版本权威：`skill/SKILL.md` 的 `metadata.skill_version`，当前为 `5.0.3`。
- `5.0.3` 发布状态以 Codeup `origin/main` 的 Git 历史和实际 `git push` 输出为准。

## 排障

- 暂无已验证排障条目。
- 补充时区分已验证处理和待确认假设。

## 健康检查

- 健康检查地址：`pending verification`
- 预期响应：`pending verification`
- 日志位置：`pending verification`

## 维护规则

- 仅记录已验证可用的命令、步骤和配置。
- 若步骤未验证，必须显式标注 `pending verification`。
- 仅在构建、启动、部署或运维知识发生变化时更新。
