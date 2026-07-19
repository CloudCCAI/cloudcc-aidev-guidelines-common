# 示例项目

这里提供三个兼容 profile，用于理解路由并做回归验证。

| 示例 | Profile | 语言 | 重点 |
|---|---|---|---|
| `examples/greenfield-v5-project/` | manifest v5 / Greenfield | `zh-CN` | 已完成的核心基线、空看板、没有预建事件文件 |
| `examples/brownfield-v5-project/` | manifest v5 / Brownfield | `zh-CN` | verified/inferred/pending baseline、兼容边界、空看板 |
| `examples/sample-project/` | legacy v4 | legacy 默认 `en` | 没有 manifest 的既有文件、旧全局 FEAT/TASK ID 和旧单任务热状态 |

## 推荐阅读顺序

对 v5 示例：

1. `.claw/manifest.yaml`
2. `.claw/current-status.md`
3. `.claw/task-board.md`
4. `.claw/goals.md`
5. `.claw/decisions.md` 的 `ARCHITECTURE`
6. `.claw/directory-map.md`
7. `.claw/devops.md`
8. `DevOps/` 中按环境拆分的 Dockerfile 和 `.env.example`
9. `docs/help/README.md` 与 `docs/design/README.md`
10. Brownfield 再读 `docs/specs/PROJECT-BASELINE.md`

两个 v5 示例都故意没有 issue、test report、archive、integration queue、team status、developer、assignment、FEAT 或 TASK；这些文件只在真实事件发生时创建。

Skill 5.0.3 起，规范模板固定为中文，直接位于 `templates/` 的各模块目录；测试会通过真实初始化和文档分配流程验证中文输出。

两个 v5 示例都接受了推荐的 `DEV`、`UAT`、`PROD` 预留结构。各 Dockerfile 仍是不可运行的待确认占位文件，用来证明“目录已初始化”不等于“打包或部署已验证”。

两个 v5 示例也包含 `docs/help` 和 `docs/design` 的中文索引；它们声明目录职责，不伪造示例产品尚未确认的手册或详细设计。

新 FEAT/TASK 未显式指定 `--owner` 时，示例遵循全局 Git `user.name`、当前项目本地 Git `user.name`、操作系统用户名的自动解析顺序，不读取 developer `document_slug`。

legacy 示例用于证明旧文件不被强制改名或补字段。新版本读取它时继续使用 v4 profile；只有用户显式采用 v5 时才建立历史边界。

## 校验

从仓库根目录运行：

```bash
python3 skill/scripts/validate-state.py skill/examples/greenfield-v5-project/.claw --strict-v5
python3 skill/scripts/validate-state.py skill/examples/brownfield-v5-project/.claw --strict-v5
python3 skill/scripts/validate-state.py skill/examples/sample-project/.claw
```
