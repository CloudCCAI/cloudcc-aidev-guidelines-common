---
kind: feature-spec
feature_id: FEAT-002
title: Identity-based asynchronous parallel delivery
status: implemented
owner_role: shared
task_ids: TASK-002
related_decisions: ADR-002
related_issues: none
updated_at: 2026-05-01T11:44:25Z
updated_by: codex
---

# FEAT-002 - Identity-based asynchronous parallel delivery

## 背景与目标

- 两个或更多独立开发者可能在不同物理环境中从主版本拉分支并行开发，开发过程中不能依赖实时互相感知进度。
- 现有协议能记录任务、spec 和交接，但缺少开发者身份、任务授权、写入边界、分片状态和最终集成队列的标准结构。
- 本次目标是把异步并行开发流程纳入技能协议，降低最后合并时的身份不清、范围冲突、状态冲突和语义冲突风险。

## 范围

### In Scope

- 定义项目管理者、开发者、集成者的身份与职责边界。
- 推荐使用公私钥签名模型，避免把管理者口令或 bearer token 明文/密文提交到项目文档。
- 新增可选目录和文件模型：`.claw/developers/`、`.claw/assignments/`、`.claw/tasks/`、`.claw/integration-queue.md`。
- 将 `current-status.md` 定位为热索引，不作为多开发者频繁写入的进度正文。
- 更新任务卡、feature spec、状态模型、README 和模板中的并行协作字段。
- 扩展初始化脚本和校验器，对可选并行协作文件进行轻量校验。

### Out Of Scope

- 实现完整的密码学签名验签工具链。
- 替代 Git 平台权限、分支保护、CI 或代码审查。
- 为某个具体 Git 托管平台生成专用 PR 自动化。

## 用户场景

- 项目管理者初始化项目后，登记开发者公钥并分配 `TASK-xxx`。
- 开发者声明自己的 `developer_id`，只修改分配给自己的任务状态文件和授权范围内的代码。
- `current-status.md` 只索引活跃任务、分片状态路径和集成队列，减少多人合并冲突。
- 集成者按 `.claw/integration-queue.md` 的顺序合并分支，验证真实测试结果，再更新主看板和热状态。

## 现状与约束

- 当前状态文件以单线交接为主，`current-status.md` 和 `task-board.md` 容易成为多人并行写入热点。
- 仓库内文档不能安全保存管理者口令；应保存公钥和签名材料，私钥留在本地或安全凭据系统中。
- 校验器应保持轻量，不引入外部 YAML 或加密依赖。

## 方案设计

- 项目只提交身份公钥与任务授权记录，不提交管理者口令、开发者令牌明文或可直接冒用的长期密钥。
- `.claw/developers/DEV-xxx.yaml` 记录开发者身份、公钥、角色和状态。
- `.claw/assignments/TASK-xxx.yaml` 记录任务授权、负责人、分支、写入范围、共享契约和管理者签名。
- `.claw/tasks/TASK-xxx.md` 记录单任务进度、验证结果和交接说明，由对应开发者维护。
- `.claw/current-status.md` 只记录当前主线快照、任务状态索引和集成队列入口。
- `.claw/integration-queue.md` 记录并行组、合并顺序、集成分支、集成负责人和验证门禁。
- 校验器在不做真实验签的前提下，检查文件结构、必填字段、引用路径和任务状态路径是否存在。

## 接口与数据影响

- 技能版本从 `3.4.0` 升级为 `3.5.0`。
- 新初始化项目会创建并行协作目录和 `integration-queue.md`。
- 既有项目不强制马上补齐开发者和任务授权文件；这些结构在启用异步多开发者协作时触发。

## 任务拆分

- `TASK-002`：更新协议、模板、脚本、校验器和状态文件，加入身份化异步并行交付模型。

## 验收标准

- `SKILL.md` 明确说明异步多开发者协作模式和安全边界。
- README 和 STATE-MODEL 记录新目录、角色、文件职责和推荐流程。
- feature spec 模板包含身份授权与并行集成计划章节。
- task-board 模板包含任务授权、分片状态、分支、PR、写入策略和集成字段。
- 初始化脚本会创建并行协作目录和集成队列模板。
- `scripts/validate-state.py .claw` 在当前仓库通过，并能轻量校验可选并行协作文件。

## 风险与回滚

- 风险：协议复杂度增加，简单项目可能感觉负担变重。
- 缓解：并行身份协作层保持可选，只有异步多开发者交付时启用。
- 风险：签名字段被误解为完整安全实现。
- 缓解：明确 skill 只定义协议和校验结构，真实验签仍应由 Git 平台、CI 或专用工具完成。
- 回滚方式：保留 3.4.0 的单线状态文件模型，移除可选身份/集成队列扩展。

## 实现进展

- 已完成：需求和设计边界确认。
- 已完成：更新技能协议、README、STATE-MODEL、CHANGELOG 和 feature spec 模板。
- 已完成：新增 `integration-queue.md`、developer、assignment 和 task-status 模板。
- 已完成：初始化脚本会创建并行协作目录并生成 `.claw/integration-queue.md`。
- 已完成：校验器支持可选并行协作文件和 task card 引用路径校验。
- 已完成：当前仓库状态校验、校验器语法检查、临时项目初始化和临时项目校验。
- 未完成：真实双开发者项目中的流程验证。

## 交接说明

- 下一位接手者优先看本 spec，再看 `SKILL.md` 中的身份化异步并行交付章节。
- 如果要继续增强安全性，应新增独立签名/验签工具，不要把 bearer token 或管理者口令提交进仓库。
- 如果要补充示例，建议新增一个 `examples/async-parallel-project/`，展示两个开发者分支、两个 assignment 和一个 integration queue。
