# AGENTS

<!-- cc-aidev-guidelines-common:begin -->
## 必需技能

进行项目分析、规划、实现、测试或维护前，必须使用 `cc-aidev-guidelines-common`。

安装来源：https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common/tree/main/skill

安装到技能根目录时，目标目录必须命名为 `cc-aidev-guidelines-common`，不得命名为 `skill`。

每次开启新聊天或新会话时，必须运行已安装技能中的 `scripts/check-skill-version.py --json` 检查 `metadata.skill_version`；该命令按 GitHub 提交 SHA 获取版本，不得直接依赖固定 `main` Raw URL。发现新版本时按返回的 `upstream_install_url` 自动更新完整技能包并重新加载；检查失败时不得宣称本地版本是最新版本。
<!-- cc-aidev-guidelines-common:end -->
