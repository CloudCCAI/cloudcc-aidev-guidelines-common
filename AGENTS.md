# AGENTS

本项目用于开发和维护 `cc-aidev-guidelines-common` 项目开发管理技能。

<!-- cc-aidev-guidelines-common:begin -->
## 必须遵守

- 本仓库用于开发和维护 `cc-aidev-guidelines-common` 技能。
- 所有 AI 智能体在进行项目分析、规划、编码、测试或维护前，必须先读取并遵守本仓库的 `skill/SKILL.md`。
- 修改协议时，必须检查 `skill/SKILL.md`、`skill/STATE-MODEL.md`、`skill/templates/`、`skill/scripts/`、`skill/examples/` 和项目状态之间的一致性。
- 优先直接使用本仓库的 `skill/SKILL.md`；如果当前环境无法从本仓库加载该技能，再从 GitHub 安装：https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common/tree/main/skill
- 安装到技能根目录时，目标目录必须命名为 `cc-aidev-guidelines-common`，不得命名为 `skill`。
- 每次开启新聊天或新会话时，必须运行已安装技能中的 `scripts/check-skill-version.py --json` 检查 `metadata.skill_version`；该命令按 GitHub 提交 SHA 获取版本，不得直接依赖固定 `main` Raw URL。发现新版本时按返回的 `upstream_install_url` 自动更新完整技能包并重新加载；检查失败时不得宣称本地版本是最新版本。
<!-- cc-aidev-guidelines-common:end -->

## 技能发布版本管理

- 技能版本号采用三段式 `x.y.z`，`x`、`y`、`z` 均为 `0` 到 `9` 的单位数字。
- 版本号递增时逢 `9` 向前一位进位，例如 `1.2.9` 的下一版为 `1.3.0`，`1.9.9` 的下一版为 `2.0.0`。
- 每次发布时必须升级 `skill/SKILL.md` front matter 中的 `metadata.skill_version`：

```yaml
metadata:
  skill_version: "x.y.z"
```
