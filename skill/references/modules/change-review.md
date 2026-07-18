# 代码评审与合并申请模块

仅在 manifest 的 `modules.change_review` 为 `true` 时读取本文。

初始化时确认：

- platform：`codeup` 或 `github`。
- target branch。
- reviewer 规则。
- 必需 CI/质量检查。
- 自动创建还是仅生成描述草稿。

配置写入 `.claw/review-config.yaml`。该文件只能保存公开项目规则，不得保存 token、password、private key 或 bearer secret。

只加载所选 platform 的平台 reference：

- Codeup：`references/platforms/codeup.md`
- GitHub：`references/platforms/github.md`

项目状态模块开启时，change request 必须关联完整 FEAT/TASK ID；项目状态关闭时不得为了评审而创建 FEAT/TASK。协作门禁开启时，还必须通过 identity/assignment 检查。关闭本模块不会删除历史 review URL 或平台记录。

评审描述至少包含范围、真实验证、风险、回滚和状态链接。合并成功后更新 TASK 的 review URL、执行状态和真实验证证据；不要把远端成功状态写成未经验证的本地事实。

## 推送到测试环境

当本模块已启用且用户明确要求“推送到测试环境”时，使用既有确定性入口：

```bash
python3 scripts/push-test-environment.py \
  --source-branch feat/TASK-user-001-description \
  --target-branch dev \
  --remote origin
```

- 执行前要求干净工作区，并确认 source、target 和 remote。
- 测试环境冲突采用已确认的 source-branch-wins 规则：先 `git merge -X theirs`，仍冲突时逐文件采用源开发分支版本。
- 该自动冲突策略只适用于测试环境，不是生产发布默认策略。
- collaboration gate 同时启用时，推送前仍必须通过当前 TASK 的登录和 assignment 检查。
- 只有真实 merge/push 成功后才能更新 TASK、review 或测试证据；dry-run 不算成功部署。
