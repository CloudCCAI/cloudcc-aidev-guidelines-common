---
kind: test-report
version: 3
updated_at: 2026-05-18T00:00:00Z
updated_by: codex
last_run_at: 2026-05-18T00:00:00Z
last_run_status: passed
---

# 测试报告

`test-report.md` 只记录真实执行过的测试或验证结果，不记录猜测。

推荐状态值：`passed` / `failed` / `partial` / `not_run`

## 最新运行摘要

- 状态：`passed`
- 范围：`task-bounded broad code authorization, protected-path blocking, exact_files compatibility, state validation, Python syntax, installed skill sync`
- 命令：`tmpdir=$(mktemp -d /tmp/cc-aidev-scope.XXXXXX) ... python3 scripts/check-assignment.py ...`; `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/validate-state.py scripts/summarize-team-status.py scripts/check-assignment.py scripts/dev-login.py`; `python3 scripts/validate-state.py .claw`; `rg -n 'skill_version: 3\\.8\\.0|task_bounded_broad_code|allowed_write_roots|protected_paths|change_manifest_required' ...`; `rsync -a --delete --exclude=... ./ /Users/owenmacbook/.agents/skills/cloudcc-aidev-guidelines-common/`; `python3 /Users/owenmacbook/.agents/skills/cloudcc-aidev-guidelines-common/scripts/validate-state.py /Users/owenmacbook/.agents/skills/cloudcc-aidev-guidelines-common/.claw`
- 环境：`local workspace`

## 结果汇总

| 类型 | 总数 | 通过 | 失败 | 跳过 | 覆盖率 |
|------|------|------|------|------|--------|
| 单元测试 | 0 | 0 | 0 | 0 | 0% |
| 集成测试 | 0 | 0 | 0 | 0 | 0% |
| E2E 测试 | 0 | 0 | 0 | 0 | - |
| 总计 | 6 | 6 | 0 | 0 | n/a |

## 失败项

- 暂无失败项。
- 备注：`task_bounded_broad_code` 临时状态用例中，`src/chat/ChatOrchestratorService.ts` 和 `tests/chat/ChatOrchestratorService.test.ts` 通过授权检查。
- 备注：同一临时状态用例中，未列入 `scope_files` 的 `scripts/check-assignment.py` 命中 `protected_paths` 并被阻止。
- 备注：`scope_mode: exact_files` 兼容用例中，`src/chat/ChatOrchestratorService.ts` 在只授权 `src/openapi/**` 时被阻止。
- 备注：已同步安装路径 `/Users/owenmacbook/.agents/skills/cloudcc-aidev-guidelines-common`，并在安装路径运行状态校验通过。
- 备注：直接运行 `python3 -m py_compile scripts/validate-state.py` 时，macOS Python 试图写入 `/Users/owenspace/Library/Caches/...` 并被沙箱拒绝；改用 `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache` 后通过。
- 备注：首次阻断用例包装脚本使用 zsh 只读变量名 `status` 导致包装失败；更换为 `rc` 后，`scripts/check-assignment.py` 正确阻止越界文件并返回非 0。

## 覆盖率趋势

| 日期 | 行覆盖率 | 分支覆盖率 | 函数覆盖率 |
|------|----------|------------|------------|
| 2026-05-01 | n/a | n/a | n/a |
| 2026-05-09 | n/a | n/a | n/a |
| 2026-05-16 | n/a | n/a | n/a |
| 2026-05-17 | n/a | n/a | n/a |
| 2026-05-18 | n/a | n/a | n/a |

## 常用测试命令

- `python3 scripts/validate-state.py .claw`
- `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/validate-state.py scripts/summarize-team-status.py scripts/check-assignment.py scripts/dev-login.py`
- `python3 scripts/dev-login.py .claw --ssh-key ~/.ssh/id_ed25519_cc_dev --developer DEV-xxx --task TASK-xxx --files path/to/file`
- `python3 scripts/check-assignment.py .claw --developer DEV-xxx --task TASK-xxx --files path/to/file`
- `python3 scripts/check-assignment.py .claw --developer DEV-xxx --task TASK-xxx --branch branch-name --files src/module/file.ts tests/module/file.test.ts`
- `python3 scripts/summarize-team-status.py .claw --write`
- `python3 - <<'PY' ... templates/github-workflows/check-assignment.yml ... PY`
- 不要在这里保留通用占位命令或猜测性的命令。

## 维护规则

- 只有在实际运行命令后才更新这里。
- `current-status.md` 只应摘录一行测试摘要。
- 如果没有运行测试，明确写 `not_run`，不要留空也不要虚构结果。
