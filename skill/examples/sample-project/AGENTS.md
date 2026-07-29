# AGENTS


<!-- cc-aidev-guidelines-common:begin -->
## Required Skill

- This project follows the `cc-aidev-guidelines-common` skill.
- Every AI agent must automatically load and use this skill before any project work.
- If the skill is not installed in the current environment, install it first from GitHub: https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common/tree/main/skill
- When installing under the skills root, name the destination directory `cc-aidev-guidelines-common`, not `skill`.
- After the skill is available, follow its greenfield or brownfield workflow to maintain `README.md`, `AGENTS.md`, `.claw/`, and `docs/specs/`.

## 必须遵守

- 本项目遵循 `cc-aidev-guidelines-common` 技能。
- 所有 AI 智能体在开始任何项目工作前，都必须自动加载并使用此技能。
- 如果当前环境尚未安装该技能，必须先从 GitHub 安装：https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common/tree/main/skill
- 安装到技能根目录时，目标目录必须命名为 `cc-aidev-guidelines-common`，不得命名为 `skill`。
- 技能可用后，必须按技能中的 Greenfield 或 Brownfield 流程维护 `README.md`、`AGENTS.md`、`.claw/` 以及 `docs/specs/`。
- 每次开启新聊天或新会话时，必须运行已安装技能中的 `scripts/check-skill-version.py --json` 检查 `metadata.skill_version`；该命令按 GitHub 提交 SHA 获取版本，不得直接依赖固定 `main` Raw URL。发现新版本时按返回的 `upstream_install_url` 自动更新完整技能包并重新加载；检查失败时不得宣称本地版本是最新版本。
<!-- cc-aidev-guidelines-common:end -->
