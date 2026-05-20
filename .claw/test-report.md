---
kind: test-report
version: 3
updated_at: 2026-05-20T00:00:00Z
updated_by: codex
last_run_at: 2026-05-20T00:00:00Z
last_run_status: passed
---

# 测试报告

`test-report.md` 只记录真实执行过的测试或验证结果，不记录猜测。

推荐状态值：`passed` / `failed` / `partial` / `not_run`

## 最新运行摘要

- 状态：`passed`
- 范围：`test environment push help, dry-run, content conflict merge, modify/delete conflict merge, Python syntax, state validation, diff whitespace`
- 命令：`python3 scripts/push-test-environment.py --help`; `python3 scripts/push-test-environment.py --dry-run --source-branch feature/example --target-branch dev --remote origin`; temporary Git repo content-conflict push test; temporary Git repo modify/delete conflict push test; `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/push-test-environment.py scripts/create-codeup-change-request.py scripts/store-yunxiao-token.py scripts/check-assignment.py scripts/validate-state.py scripts/summarize-team-status.py scripts/dev-login.py`; `python3 scripts/validate-state.py .claw`; `git diff --check`
- 环境：`local workspace`

## 结果汇总

| 类型 | 总数 | 通过 | 失败 | 跳过 | 覆盖率 |
|------|------|------|------|------|--------|
| 单元测试 | 0 | 0 | 0 | 0 | 0% |
| 集成测试 | 0 | 0 | 0 | 0 | 0% |
| E2E 测试 | 0 | 0 | 0 | 0 | - |
| 总计 | 7 | 7 | 0 | 0 | n/a |

## 失败项

- 暂无失败项。
- 备注：`python3 scripts/push-test-environment.py --help` 通过。
- 备注：dry-run 输出 fetch、checkout `dev`、pull、merge、push 和切回原分支的计划，不要求真实 `dev` 分支存在，也不修改工作区。
- 备注：临时 Git 仓库内容冲突用例中，`feat/test` 合并到 `dev` 后，`origin/dev:app.txt` 为开发分支内容 `feature`，脚本切回 `feat/test`。
- 备注：临时 Git 仓库 modify/delete 冲突用例中，开发分支删除 `app.txt`，`dev` 修改 `app.txt`，脚本自动采用开发分支删除结果，推送后 `origin/dev:app.txt` 不存在，脚本切回 `feat/delete`。
- 备注：`PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/push-test-environment.py scripts/create-codeup-change-request.py scripts/store-yunxiao-token.py scripts/check-assignment.py scripts/validate-state.py scripts/summarize-team-status.py scripts/dev-login.py` 通过。
- 备注：`github/main` 与本地 `main` 没有共同 merge-base，合并时使用 `--allow-unrelated-histories`，共同文件以 GitHub `3.8.0` 为基线，再重新套回本地 Codeup 方案。
- 备注：缺少 `YUNXIAO_TOKEN` 时，Codeup 创建脚本返回非 0，未发起 OpenAPI 请求，并输出云效个人访问令牌文档链接。
- 备注：dry-run 输出 endpoint 和 payload，没有输出 token。
- 备注：本地 token 存储测试写入 `/private/tmp/cc-aidev-codeup-test.env`，权限为 `-rw-------`，测试后已删除。
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
| 2026-05-19 | n/a | n/a | n/a |
| 2026-05-20 | n/a | n/a | n/a |

## 常用测试命令

- `python3 scripts/validate-state.py .claw`
- `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/validate-state.py scripts/summarize-team-status.py scripts/check-assignment.py scripts/dev-login.py`
- `python3 scripts/dev-login.py .claw --ssh-key ~/.ssh/id_ed25519_cc_dev --developer DEV-xxx --task TASK-xxx --files path/to/file`
- `python3 scripts/check-assignment.py .claw --developer DEV-xxx --task TASK-xxx --files path/to/file`
- `python3 scripts/check-assignment.py .claw --developer DEV-xxx --task TASK-xxx --branch branch-name --files src/module/file.ts tests/module/file.test.ts`
- `python3 scripts/summarize-team-status.py .claw --write`
- `python3 - <<'PY' ... templates/github-workflows/check-assignment.yml ... PY`
- `python3 scripts/create-codeup-change-request.py --dry-run --domain https://example.com --repository-id 123 --source-branch feat/TASK-xxx`
- `python3 scripts/store-yunxiao-token.py`
- `python3 scripts/push-test-environment.py --source-branch feat/TASK-xxx --target-branch dev --remote origin`
- 不要在这里保留通用占位命令或猜测性的命令。

## 维护规则

- 只有在实际运行命令后才更新这里。
- `current-status.md` 只应摘录一行测试摘要。
- 如果没有运行测试，明确写 `not_run`，不要留空也不要虚构结果。
