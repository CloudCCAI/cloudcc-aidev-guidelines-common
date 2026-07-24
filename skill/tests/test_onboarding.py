from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
PREFLIGHT = SCRIPTS_DIR / "project-preflight.py"
ONBOARDING = SCRIPTS_DIR / "project-onboarding.py"
CONFIGURE_MODULES = SCRIPTS_DIR / "configure-modules.py"
VALIDATE_STATE = SCRIPTS_DIR / "validate-state.py"
INIT_WRAPPER = SCRIPTS_DIR / "init-state.sh"
FIXED_NOW = "2026-07-18 02:00:00"
ONBOARDING_INCOMPLETE_SENTINEL = "<!-- cc-aidev:onboarding-incomplete -->"


class OnboardingCliTests(unittest.TestCase):
    def run_python(self, script: Path, *arguments: str) -> tuple[int, dict[str, object], str]:
        completed = subprocess.run(
            [sys.executable, str(script), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            self.fail(
                f"command did not emit JSON: {script.name} {' '.join(arguments)}\n"
                f"exit={completed.returncode}\nstdout={completed.stdout}\nstderr={completed.stderr}\nerror={exc}"
            )
        return completed.returncode, payload, completed.stderr

    def start(self, project: Path, *arguments: str) -> tuple[int, dict[str, object], str]:
        return self.run_python(
            ONBOARDING,
            "start",
            str(project),
            *arguments,
            "--now",
            FIXED_NOW,
            "--json",
        )

    def test_new_project_uses_chinese_without_a_language_question(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            code, payload, _ = self.start(project, "--mode", "greenfield")
            self.assertEqual(code, 2, payload)
            self.assertEqual(payload["language"], "zh-CN")
            self.assertEqual(payload["next"]["id"], "goals")
            self.assertNotEqual(payload["next"]["id"], "language")
            manifest = (project / ".claw" / "manifest.yaml").read_text(encoding="utf-8")
            self.assertIn('language: "zh-CN"', manifest)
            self.assertIn("# 项目目标", (project / ".claw" / "goals.md").read_text(encoding="utf-8"))
            self.assertIn("## AI 开发协议", (project / "README.md").read_text(encoding="utf-8"))
            agents = (project / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("metadata.skill_version", agents)
            self.assertIn("有新版本时自动更新后重新加载本技能", agents)
            self.assertIn(
                "# 产品帮助与使用手册",
                (project / "docs" / "help" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "# 产品与功能设计文档",
                (project / "docs" / "design" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertTrue((project / "docs" / "design" / "README.html").is_file())

            self.mark_all_required_complete(project)
            code, finalized, _ = self.run_python(
                ONBOARDING,
                "finalize",
                str(project),
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, finalized)
            self.assertEqual(finalized["status"], "ready")
            current_status = (project / ".claw" / "current-status.md").read_text(encoding="utf-8")
            self.assertIn("# 项目当前状态", current_status)
            self.assertIn("确认下一项项目工作", current_status)

    def write_example_answer_and_remove_sentinel(self, path: Path, file_id: str) -> None:
        content = path.read_text(encoding="utf-8")
        if ONBOARDING_INCOMPLETE_SENTINEL not in content:
            return
        content = content.replace(ONBOARDING_INCOMPLETE_SENTINEL, "", 1)
        content = content.rstrip() + (
            "\n\n## 已确认的初始化答案（测试夹具）\n\n"
            f"- `{file_id}` 已填写代表性的项目事实，并由 Bimo 确认。\n"
        )
        path.write_text(content, encoding="utf-8")
        self.assertNotIn(ONBOARDING_INCOMPLETE_SENTINEL, path.read_text(encoding="utf-8"))

    def mark_all_required_complete(self, project: Path) -> None:
        code, payload, _ = self.run_python(ONBOARDING, "status", str(project), "--json")
        self.assertIn(code, {0, 2})
        file_rows = payload["files"]
        self.assertIsInstance(file_rows, list)
        for row in file_rows:
            self.assertIsInstance(row, dict)
            file_id = str(row["id"])
            if file_id == "devops":
                code, assets, _ = self.run_python(
                    ONBOARDING,
                    "devops-assets",
                    str(project),
                    "--recommended-environments",
                    "--now",
                    FIXED_NOW,
                    "--json",
                )
                self.assertEqual(code, 2, assets)
                self.assertEqual(assets["environments"], ["DEV", "UAT", "PROD"])
            self.write_example_answer_and_remove_sentinel(project / str(row["path"]), file_id)
            code, marked, _ = self.run_python(
                ONBOARDING,
                "mark",
                str(project),
                file_id,
                "--status",
                "complete",
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertIn(code, {0, 2}, marked)

    def test_devops_assets_require_confirmation_and_recommend_three_reserved_environments(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            code, payload, _ = self.start(project, "--mode", "greenfield")
            self.assertEqual(code, 2, payload)
            code, validation, _ = self.run_python(
                VALIDATE_STATE,
                str(project / ".claw"),
                "--catalog",
                str(SKILL_ROOT / "state-catalog.json"),
                "--json",
            )
            self.assertEqual(code, 0, validation)

            code, needs_input, _ = self.run_python(
                ONBOARDING,
                "devops-assets",
                str(project),
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 2, needs_input)
            self.assertEqual(needs_input["error"], "environment_confirmation_required")
            self.assertFalse((project / "DevOps").exists())

            code, reserved, _ = self.run_python(
                ONBOARDING,
                "devops-assets",
                str(project),
                "--recommended-environments",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 2, reserved)
            self.assertEqual(reserved["environments"], ["DEV", "UAT", "PROD"])
            self.assertTrue(reserved["recommended_defaults_used"])
            self.assertIn("# DevOps 环境资产", (project / "DevOps" / "README.md").read_text(encoding="utf-8"))
            for environment in ("DEV", "UAT", "PROD"):
                dockerfile = project / "DevOps" / environment / "Dockerfile"
                self.assertTrue(dockerfile.is_file())
                self.assertNotIn("\nFROM ", "\n" + dockerfile.read_text(encoding="utf-8"))
                self.assertTrue((project / "DevOps" / environment / ".env.example").is_file())
            self.assertIn("DevOps/**/.env\n", (project / ".gitignore").read_text(encoding="utf-8"))
            devops = (project / ".claw" / "devops.md").read_text(encoding="utf-8")
            self.assertIn('environment_names: "DEV, UAT, PROD"', devops)
            self.assertIn("`DevOps/PROD/Dockerfile`", devops)

    def test_devops_assets_are_additive_and_do_not_overwrite_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.start(project, "--mode", "greenfield")
            code, first, _ = self.run_python(
                ONBOARDING,
                "devops-assets",
                str(project),
                "--environment",
                "QA",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 2, first)
            dockerfile = project / "DevOps" / "QA" / "Dockerfile"
            dockerfile.write_text("FROM scratch\n", encoding="utf-8")

            code, second, _ = self.run_python(
                ONBOARDING,
                "devops-assets",
                str(project),
                "--environment",
                "Production-CustomerA",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 2, second)
            self.assertEqual(second["environments"], ["QA", "Production-CustomerA"])
            self.assertEqual(dockerfile.read_text(encoding="utf-8"), "FROM scratch\n")
            self.assertTrue((project / "DevOps" / "Production-CustomerA" / "Dockerfile").is_file())

            devops_path = project / ".claw" / "devops.md"
            before_repeat = devops_path.read_bytes()
            code, repeated, _ = self.run_python(
                ONBOARDING,
                "devops-assets",
                str(project),
                "--environment",
                "Production-CustomerA",
                "--now",
                "2026-07-18 03:00:00",
                "--json",
            )
            self.assertEqual(code, 2, repeated)
            self.assertFalse(repeated["changed"])
            self.assertEqual(devops_path.read_bytes(), before_repeat)

    def test_devops_cannot_complete_without_confirmed_environment_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.start(project, "--mode", "greenfield")
            devops = project / ".claw" / "devops.md"
            self.write_example_answer_and_remove_sentinel(devops, "devops")
            code, rejected, _ = self.run_python(
                ONBOARDING,
                "mark",
                str(project),
                "devops",
                "--status",
                "complete",
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 2, rejected)
            self.assertEqual(rejected["error"], "devops_assets_incomplete")
            self.assertIn("environment_names", " ".join(rejected["repair"]["errors"]))

    def test_devops_assets_reject_unsafe_names_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.start(project, "--mode", "greenfield")
            code, rejected, _ = self.run_python(
                ONBOARDING,
                "devops-assets",
                str(project),
                "--environment",
                "../PROD",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 6, rejected)
            self.assertEqual(rejected["error"], "invalid_environment_name")
            self.assertFalse((project / "DevOps").exists())

    def test_read_only_preflight_recommends_greenfield_for_empty_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            code, payload, _ = self.run_python(PREFLIGHT, str(project), "--json")
            self.assertEqual(code, 0)
            self.assertEqual(payload["status"], "uninitialized")
            self.assertIn("confirm module switches", payload["next_action"])
            self.assertNotIn("language", payload["next_action"])
            recommendation = payload["mode_recommendation"]
            self.assertEqual(recommendation["candidate"], "greenfield")
            self.assertTrue(recommendation["requires_user_confirmation"])
            self.assertFalse((project / ".claw").exists())

    def test_greenfield_resume_mark_finalize_and_idempotent_restart(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            code, payload, _ = self.start(project, "--mode", "greenfield")
            self.assertEqual(code, 2)
            self.assertEqual(payload["status"], "needs_input")
            self.assertEqual(payload["next"]["id"], "goals")

            expected_core = {
                "manifest.yaml",
                "current-status.md",
                "goals.md",
                "decisions.md",
                "directory-map.md",
                "devops.md",
                "task-board.md",
            }
            actual_core = {path.name for path in (project / ".claw").iterdir() if path.is_file()}
            self.assertEqual(actual_core, expected_core)
            self.assertEqual(
                (project / ".gitignore").read_text(encoding="utf-8"),
                ".claw-local/\n.claw/.locks/\n",
            )
            self.assertFalse((project / "docs" / "specs" / "PROJECT-BASELINE.md").exists())
            help_index = project / "docs" / "help" / "README.md"
            design_index = project / "docs" / "design" / "README.md"
            self.assertIn("# 产品帮助与使用手册", help_index.read_text(encoding="utf-8"))
            self.assertIn("# 产品与功能设计文档", design_index.read_text(encoding="utf-8"))
            for event_path in (
                ".claw/issue-list.md",
                ".claw/issue-archive.md",
                ".claw/test-report.md",
                ".claw/test-archive.md",
                ".claw/task-archive.md",
                ".claw/integration-queue.md",
                ".claw/team-status.md",
                ".claw/tasks",
                ".claw/developers",
                ".claw/assignments",
            ):
                self.assertFalse((project / event_path).exists(), event_path)

            code, resumed, _ = self.run_python(ONBOARDING, "resume", str(project), "--json")
            self.assertEqual(code, 2)
            self.assertEqual(resumed["question_batch"][0]["id"], "goals")

            self.mark_all_required_complete(project)
            code, finalized, _ = self.run_python(
                ONBOARDING,
                "finalize",
                str(project),
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, finalized)
            self.assertEqual(finalized["status"], "ready")
            current_status = project / ".claw" / "current-status.md"
            finalized_current_status = current_status.read_text(encoding="utf-8")
            self.assertIn("phase: idle", finalized_current_status)
            self.assertIn('next_action: "确认下一项项目工作"', finalized_current_status)

            code, ready, _ = self.run_python(PREFLIGHT, str(project), "--require-ready", "--json")
            self.assertEqual(code, 0, ready)
            self.assertTrue(ready["ready"])
            self.assertEqual(ready["project_mode"], "greenfield")

            code, validation, _ = self.run_python(
                VALIDATE_STATE,
                str(project / ".claw"),
                "--catalog",
                str(SKILL_ROOT / "state-catalog.json"),
                "--json",
            )
            self.assertEqual(code, 0, validation)
            self.assertEqual(validation["status"], "passed")

            manifest_path = project / ".claw" / "manifest.yaml"
            manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            current_status_hash = hashlib.sha256(current_status.read_bytes()).hexdigest()
            code, repeated_finalize, _ = self.run_python(
                ONBOARDING,
                "finalize",
                str(project),
                "--confirmed-by",
                "Another User",
                "--now",
                "2026-07-19 02:00:00",
                "--json",
            )
            self.assertEqual(code, 0, repeated_finalize)
            self.assertFalse(repeated_finalize["changed"])
            self.assertEqual(hashlib.sha256(manifest_path.read_bytes()).hexdigest(), manifest_hash)
            self.assertEqual(hashlib.sha256(current_status.read_bytes()).hexdigest(), current_status_hash)

            help_index.write_text("# Customer-authored manual index\n", encoding="utf-8")
            design_index.unlink()
            code, missing_asset, _ = self.run_python(
                VALIDATE_STATE,
                str(project / ".claw"),
                "--catalog",
                str(SKILL_ROOT / "state-catalog.json"),
                "--json",
            )
            self.assertNotEqual(code, 0, missing_asset)
            self.assertIn("docs/design/README.md", " ".join(missing_asset["errors"]))

            before = current_status.read_text(encoding="utf-8")
            code, restarted, _ = self.start(project, "--mode", "greenfield")
            self.assertEqual(code, 0, restarted)
            self.assertEqual(restarted["created"], ["docs/design/README.md"])
            self.assertEqual(help_index.read_text(encoding="utf-8"), "# Customer-authored manual index\n")
            self.assertTrue(design_index.is_file())
            self.assertEqual(current_status.read_text(encoding="utf-8"), before)

            code, idempotent, _ = self.start(project, "--mode", "greenfield")
            self.assertEqual(code, 0, idempotent)
            self.assertEqual(idempotent["created"], [])

    def test_onboarding_sentinel_blocks_completion_until_answers_are_confirmed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            code, payload, _ = self.start(project, "--mode", "greenfield")
            self.assertEqual(code, 2, payload)

            protected_files = {
                "goals.md",
                "decisions.md",
                "directory-map.md",
                "devops.md",
            }
            for filename in protected_files:
                self.assertIn(
                    ONBOARDING_INCOMPLETE_SENTINEL,
                    (project / ".claw" / filename).read_text(encoding="utf-8"),
                )
            for filename in ("current-status.md", "task-board.md"):
                self.assertNotIn(
                    ONBOARDING_INCOMPLETE_SENTINEL,
                    (project / ".claw" / filename).read_text(encoding="utf-8"),
                )

            goals_path = project / ".claw" / "goals.md"
            original_goals = goals_path.read_text(encoding="utf-8")
            code, blocked_mark, _ = self.run_python(
                ONBOARDING,
                "mark",
                str(project),
                "goals",
                "--status",
                "complete",
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 2, blocked_mark)
            self.assertEqual(blocked_mark["status"], "needs_input")
            self.assertEqual(blocked_mark["error"], "onboarding_incomplete")
            self.assertEqual(goals_path.read_text(encoding="utf-8"), original_goals)
            self.assertIn("init_status: not_started", original_goals)

            self.mark_all_required_complete(project)
            answered_goals = goals_path.read_text(encoding="utf-8")
            self.assertIn("已确认的初始化答案（测试夹具）", answered_goals)
            self.assertNotIn(ONBOARDING_INCOMPLETE_SENTINEL, answered_goals)

            goals_path.write_text(
                answered_goals.replace(
                    "# 项目目标",
                    f"{ONBOARDING_INCOMPLETE_SENTINEL}\n\n# 项目目标",
                    1,
                ),
                encoding="utf-8",
            )
            code, rejected, _ = self.run_python(
                ONBOARDING,
                "finalize",
                str(project),
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 4, rejected)
            self.assertEqual(rejected["status"], "needs_review")
            self.assertIn("onboarding", json.dumps(rejected["validation"], ensure_ascii=False).lower())

            goals_path.write_text(
                goals_path.read_text(encoding="utf-8").replace(
                    ONBOARDING_INCOMPLETE_SENTINEL,
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            code, finalized, _ = self.run_python(
                ONBOARDING,
                "finalize",
                str(project),
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, finalized)
            self.assertEqual(finalized["status"], "ready")

    def test_brownfield_creates_baseline_but_not_event_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / "src").mkdir()
            (project / "src" / "app.py").write_text("print('app')\n", encoding="utf-8")
            (project / "src" / "service.py").write_text("VALUE = 1\n", encoding="utf-8")
            (project / "package.json").write_text("{}\n", encoding="utf-8")

            code, preflight, _ = self.run_python(PREFLIGHT, str(project), "--json")
            self.assertEqual(code, 0)
            self.assertEqual(preflight["mode_recommendation"]["candidate"], "brownfield")

            code, payload, _ = self.start(project, "--mode", "brownfield")
            self.assertEqual(code, 2, payload)
            self.assertEqual(payload["next"]["id"], "project_baseline")
            baseline = project / "docs" / "specs" / "PROJECT-BASELINE.md"
            self.assertTrue(baseline.is_file())
            baseline_text = baseline.read_text(encoding="utf-8")
            self.assertIn("init_status: not_started", baseline_text)
            self.assertIn("schema_version: 5", baseline_text)
            self.assertFalse((project / ".claw" / "tasks").exists())
            self.assertFalse((project / ".claw" / "issue-list.md").exists())
            self.assertFalse((project / ".claw" / "issue-archive.md").exists())

            self.mark_all_required_complete(project)
            code, finalized, _ = self.run_python(
                ONBOARDING,
                "finalize",
                str(project),
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, finalized)
            code, validation, _ = self.run_python(
                VALIDATE_STATE,
                str(project / ".claw"),
                "--catalog",
                str(SKILL_ROOT / "state-catalog.json"),
                "--json",
            )
            self.assertEqual(code, 0, validation)

    def test_start_without_mode_persists_checkpoint_then_resumes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            code, payload, _ = self.start(project)
            self.assertEqual(code, 2, payload)
            self.assertEqual(payload["next"]["id"], "project_mode")
            self.assertTrue((project / ".claw" / "manifest.yaml").is_file())
            self.assertFalse((project / ".claw" / "goals.md").exists())
            code, validation, _ = self.run_python(
                VALIDATE_STATE,
                str(project / ".claw"),
                "--catalog",
                str(SKILL_ROOT / "state-catalog.json"),
                "--json",
            )
            self.assertEqual(code, 0, validation)

            code, resumed, _ = self.run_python(ONBOARDING, "resume", str(project), "--json")
            self.assertEqual(code, 2)
            self.assertEqual(resumed["question_batch"][0]["id"], "project_mode")

            code, continued, _ = self.start(project, "--mode", "greenfield")
            self.assertEqual(code, 2, continued)
            self.assertEqual(continued["next"]["id"], "goals")
            self.assertTrue((project / ".claw" / "goals.md").is_file())

    def test_project_state_off_creates_only_control_plane(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            code, payload, _ = self.start(project, "--project-state", "off")
            self.assertEqual(code, 0, payload)
            self.assertTrue(payload["ready_to_finalize"])
            self.assertEqual(payload["project_mode"], "not_applicable")
            self.assertEqual(
                {path.name for path in (project / ".claw").iterdir()},
                {"manifest.yaml"},
            )
            self.assertFalse((project / "docs").exists())
            code, finalized, _ = self.run_python(
                ONBOARDING,
                "finalize",
                str(project),
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, finalized)
            code, ready, _ = self.run_python(PREFLIGHT, str(project), "--json")
            self.assertEqual(code, 0, ready)
            self.assertIn("project-state workflow is disabled", ready["next_action"])
            self.assertEqual(ready["mode_recommendation"]["candidate"], "not_applicable")
            self.assertFalse(ready["mode_recommendation"]["requires_user_confirmation"])

    def test_change_review_module_is_configured_without_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            code, payload, _ = self.start(
                project,
                "--project-state",
                "off",
                "--change-review",
                "on",
            )
            self.assertEqual(code, 2, payload)
            self.assertEqual(payload["next"]["id"], "review_config")
            config_path = project / ".claw" / "review-config.yaml"
            self.assertTrue(config_path.is_file())

            code, configured, _ = self.run_python(
                CONFIGURE_MODULES,
                "review",
                str(project),
                "--platform",
                "codeup",
                "--target-branch",
                "main",
                "--reviewers",
                "Bimo",
                "--required-checks",
                "state-validation",
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, configured)
            config_text = config_path.read_text(encoding="utf-8").lower()
            self.assertIn('platform: "codeup"', config_text)
            self.assertIn('token_storage: "local_only"', config_text)
            self.assertNotIn("bearer_token", config_text)
            self.assertNotIn("password", config_text)
            code, finalized, _ = self.run_python(
                ONBOARDING,
                "finalize",
                str(project),
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, finalized)
            code, ready, _ = self.run_python(PREFLIGHT, str(project), "--json")
            self.assertEqual(code, 0, ready)
            self.assertIn("load only enabled non-state module configuration", ready["next_action"])

    def test_collaboration_dependency_and_no_gate_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            invalid_project = Path(temporary) / "invalid"
            invalid_project.mkdir()
            code, payload, _ = self.start(
                invalid_project,
                "--project-state",
                "off",
                "--collaboration-gate",
                "on",
            )
            self.assertEqual(code, 6, payload)
            self.assertEqual(payload["error"], "module_dependency")
            self.assertFalse((invalid_project / ".claw").exists())

            valid_project = Path(temporary) / "valid"
            valid_project.mkdir()
            code, payload, _ = self.start(
                valid_project,
                "--mode",
                "greenfield",
                "--collaboration-gate",
                "on",
            )
            self.assertEqual(code, 2, payload)
            collaboration_config = valid_project / ".claw" / "collaboration-config.yaml"
            self.assertTrue(collaboration_config.is_file())
            self.assertIn("init_status:", collaboration_config.read_text(encoding="utf-8"))
            self.assertFalse((valid_project / ".claw" / "developers").exists())
            self.assertFalse((valid_project / ".claw" / "assignments").exists())
            self.assertFalse((valid_project / ".claw" / "integration-queue.md").exists())
            self.mark_all_required_complete(valid_project)
            code, finalized, _ = self.run_python(
                ONBOARDING,
                "finalize",
                str(valid_project),
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, finalized)

    def test_legacy_state_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / ".claw").mkdir()
            legacy_file = project / ".claw" / "current-status.md"
            legacy_file.write_text("legacy content\n", encoding="utf-8")
            code, preflight, _ = self.run_python(PREFLIGHT, str(project), "--json")
            self.assertEqual(code, 0, preflight)
            self.assertEqual(preflight["status"], "legacy")
            self.assertTrue(preflight["operational"])
            self.assertIn("continue with legacy v4 profile", preflight["next_action"])
            self.assertEqual(legacy_file.read_text(encoding="utf-8"), "legacy content\n")
            code, payload, _ = self.start(project, "--mode", "brownfield")
            self.assertEqual(code, 5, payload)
            self.assertEqual(payload["error"], "legacy_state")
            self.assertEqual(legacy_file.read_text(encoding="utf-8"), "legacy content\n")
            self.assertFalse((project / ".claw" / "manifest.yaml").exists())

    def test_explicit_adopt_snapshots_and_grandfathers_legacy_core(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / ".claw").mkdir()
            legacy_decisions = project / ".claw" / "decisions.md"
            legacy_decisions.write_text("# Historical decisions\n\nDo not rewrite me.\n", encoding="utf-8")
            original_hash = hashlib.sha256(legacy_decisions.read_bytes()).hexdigest()
            (project / "README.md").write_text("# Existing project\n\nKeep this text.\n", encoding="utf-8")

            code, preflight, _ = self.run_python(PREFLIGHT, str(project), "--json")
            self.assertEqual(code, 0)
            self.assertEqual(preflight["status"], "legacy")
            self.assertFalse((project / ".claw" / "legacy-document-index.yaml").exists())

            code, adopted, _ = self.run_python(
                ONBOARDING,
                "adopt",
                str(project),
                "--mode",
                "brownfield",
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 2, adopted)
            self.assertTrue(adopted["adopted"])
            self.assertEqual(adopted["grandfathered_files"]["decisions"], ".claw/decisions.md")
            self.assertEqual(hashlib.sha256(legacy_decisions.read_bytes()).hexdigest(), original_hash)
            self.assertTrue((project / ".claw" / "legacy-document-index.yaml").is_file())
            self.assertTrue((project / ".claw" / "goals.md").is_file())
            self.assertTrue((project / "docs" / "specs" / "PROJECT-BASELINE.md").is_file())
            readme_text = (project / "README.md").read_text(encoding="utf-8")
            self.assertIn("Keep this text.", readme_text)
            self.assertIn("<!-- cc-aidev-guidelines-common:begin -->", readme_text)
            self.assertTrue((project / "AGENTS.md").is_file())

            self.mark_all_required_complete(project)
            self.assertEqual(hashlib.sha256(legacy_decisions.read_bytes()).hexdigest(), original_hash)
            code, finalized, _ = self.run_python(
                ONBOARDING,
                "finalize",
                str(project),
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, finalized)

            code, repeated, _ = self.run_python(
                ONBOARDING,
                "adopt",
                str(project),
                "--mode",
                "brownfield",
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, repeated)
            self.assertEqual(repeated["created"], [])
            self.assertEqual(hashlib.sha256(legacy_decisions.read_bytes()).hexdigest(), original_hash)

    def test_explicit_adopt_accepts_existing_block_mapping_legacy_index(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            state_dir = project / ".claw"
            state_dir.mkdir()
            legacy_decisions = state_dir / "decisions.md"
            legacy_decisions.write_text("# Historical decisions\n", encoding="utf-8")
            original_hash = hashlib.sha256(legacy_decisions.read_bytes()).hexdigest()
            (state_dir / "legacy-document-index.yaml").write_text(
                "kind: legacy-document-index\n"
                "schema_version: 1\n"
                "captured_at: 2026-07-17T02:00:00Z\n"
                "policy_effective_at: 2026-07-17T02:00:00Z\n"
                "created_by: Bimo\n"
                "document_count: 1\n"
                "documents:\n"
                "  - path: .claw/decisions.md\n"
                "    kind: decisions\n"
                "    schema_version: 4\n",
                encoding="utf-8",
            )

            code, adopted, _ = self.run_python(
                ONBOARDING,
                "adopt",
                str(project),
                "--mode",
                "brownfield",
                "--confirmed-by",
                "Bimo",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 2, adopted)
            self.assertEqual(adopted["grandfathered_files"]["decisions"], ".claw/decisions.md")
            self.assertEqual(hashlib.sha256(legacy_decisions.read_bytes()).hexdigest(), original_hash)
            code, preflight, _ = self.run_python(PREFLIGHT, str(project), "--json")
            self.assertEqual(code, 0, preflight)
            decisions_row = next(
                row for row in preflight["file_statuses"] if row["id"] == "decisions"
            )
            self.assertEqual(decisions_row["init_status"], "complete")

    def test_catalog_covers_module_configs_and_event_artifacts(self) -> None:
        catalog = json.loads((SKILL_ROOT / "state-catalog.json").read_text(encoding="utf-8"))
        locales_root = SKILL_ROOT / "templates" / "locales"
        self.assertFalse(
            any(path.is_file() for path in locales_root.rglob("*")) if locales_root.exists() else False,
            "templates/locales must not contain language-specific template mirrors",
        )
        entries = {entry["id"]: entry for entry in catalog["files"]}
        for entry in entries.values():
            template = entry.get("template")
            if template:
                self.assertTrue((SKILL_ROOT / template).is_file(), template)
        self.assertEqual(entries["project_baseline"]["template"], "templates/project-state/project-baseline.md")
        self.assertTrue(entries["project_baseline"]["initialization_required"])
        self.assertEqual(entries["collaboration_config"]["path"], ".claw/collaboration-config.yaml")
        external_assets = entries["devops"]["external_assets"]
        for asset in external_assets["root_files"] + external_assets["per_environment_files"]:
            self.assertTrue((SKILL_ROOT / asset["template"]).is_file(), asset["template"])
        for entry_id in (
            "feature_spec",
            "task_status",
            "issue_list",
            "test_report",
            "test_archive",
            "task_archive",
            "developer",
            "assignment",
            "integration_queue",
            "team_status",
        ):
            entry = entries[entry_id]
            self.assertEqual(entry["schema_version"], 5)
            self.assertFalse(entry["initialization_required"])
            if entry.get("lifecycle") == "derived":
                self.assertFalse(entry.get("template"), entry_id)
            else:
                self.assertTrue(entry.get("template"), entry_id)

    def test_module_reconfiguration_preserves_disabled_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            code, payload, _ = self.start(project, "--project-state", "off")
            self.assertEqual(code, 0, payload)

            code, enabled, _ = self.run_python(
                CONFIGURE_MODULES,
                "set",
                str(project),
                "--change-review",
                "on",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 2, enabled)
            config_path = project / ".claw" / "review-config.yaml"
            self.assertTrue(config_path.exists())

            code, disabled, _ = self.run_python(
                CONFIGURE_MODULES,
                "set",
                str(project),
                "--change-review",
                "off",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, disabled)
            self.assertTrue(config_path.exists())
            self.assertFalse(disabled["modules"]["change_review"])

    def test_historical_language_markers_preserve_documents_and_pending_normalizes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            code, payload, _ = self.start(project, "--mode", "greenfield")
            self.assertEqual(code, 2, payload)
            goals_path = project / ".claw" / "goals.md"
            goals_path.write_text(
                goals_path.read_text(encoding="utf-8").replace(
                    "# 项目目标",
                    "# Existing English Project Goals",
                    1,
                ),
                encoding="utf-8",
            )
            original_hash = hashlib.sha256(goals_path.read_bytes()).hexdigest()
            manifest_path = project / ".claw" / "manifest.yaml"
            historical_manifest = manifest_path.read_text(encoding="utf-8").replace(
                'skill_version: "5.0.3"',
                'skill_version: "5.0.2"',
                1,
            ).replace(
                'language: "zh-CN"',
                'language: "en"',
                1,
            )
            manifest_path.write_text(historical_manifest, encoding="utf-8")
            design_index = project / "docs" / "design" / "README.md"
            design_index.unlink()

            code, compatible, _ = self.start(project, "--mode", "greenfield")
            self.assertEqual(code, 2, compatible)
            self.assertEqual(compatible["language"], "en")
            self.assertEqual(hashlib.sha256(goals_path.read_bytes()).hexdigest(), original_hash)
            self.assertIn("# 产品与功能设计文档", design_index.read_text(encoding="utf-8"))

            manifest_path.write_text(
                manifest_path.read_text(encoding="utf-8").replace(
                    'language: "en"',
                    'language: "pending"',
                    1,
                ),
                encoding="utf-8",
            )
            help_index = project / "docs" / "help" / "README.md"
            help_index.unlink()
            code, normalized, _ = self.start(project, "--mode", "greenfield")
            self.assertEqual(code, 2, normalized)
            self.assertEqual(normalized["language"], "zh-CN")
            self.assertIn('language: "zh-CN"', manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(hashlib.sha256(goals_path.read_bytes()).hexdigest(), original_hash)
            self.assertIn("# 产品帮助与使用手册", help_index.read_text(encoding="utf-8"))
            self.assertIn("## AI 开发协议", (project / "README.md").read_text(encoding="utf-8"))

    def test_project_state_reconfiguration_updates_project_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            code, payload, _ = self.start(project, "--mode", "greenfield")
            self.assertEqual(code, 2, payload)
            goals_path = project / ".claw" / "goals.md"
            self.assertTrue(goals_path.is_file())

            code, disabled, _ = self.run_python(
                CONFIGURE_MODULES,
                "set",
                str(project),
                "--project-state",
                "off",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 0, disabled)
            self.assertEqual(disabled["project_mode"], "not_applicable")
            self.assertTrue(goals_path.is_file())

            code, enabled, _ = self.run_python(
                CONFIGURE_MODULES,
                "set",
                str(project),
                "--project-state",
                "on",
                "--now",
                FIXED_NOW,
                "--json",
            )
            self.assertEqual(code, 2, enabled)
            self.assertEqual(enabled["project_mode"], "pending")
            self.assertEqual(enabled["next"]["id"], "project_mode")

    def test_shell_wrapper_rejects_non_claw_state_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            completed = subprocess.run(
                ["bash", str(INIT_WRAPPER), temporary, "custom-state", "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 6)
            self.assertIn("Only the fixed .claw state directory", completed.stderr)
            self.assertFalse((Path(temporary) / ".claw").exists())

    def test_onboarding_rejects_historical_timestamp_override(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            code, payload, _ = self.run_python(
                ONBOARDING,
                "start",
                temporary,
                "--mode",
                "greenfield",
                "--now",
                "2026-07-18T02:00:00Z",
                "--json",
            )

            self.assertEqual(code, 6)
            self.assertEqual(payload["error"], "invalid_timestamp")
            self.assertIn("YYYY-MM-DD HH:MM:SS", payload["message"])


if __name__ == "__main__":
    unittest.main()
