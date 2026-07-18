from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


current_status = load_script("generate_current_status", "generate-current-status.py")
team_status = load_script("summarize_team_status", "summarize-team-status.py")


class CurrentStatusTests(unittest.TestCase):
    def make_project(self) -> tuple[Path, Path]:
        root = Path(tempfile.mkdtemp())
        state_dir = root / ".claw"
        (state_dir / "tasks").mkdir(parents=True)
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        return root, state_dir

    def write_fixture(self, root: Path, state_dir: Path) -> None:
        (state_dir / "task-board.md").write_text(
            """---
kind: task-board
version: 5
updated_at: 2026-07-18T00:00:00Z
updated_by: test
---

# Task Board

## Active Tasks

### TASK-001 - Legacy task

- status: `in_progress`
- priority: `high`
- owner_role: `shared`
- spec_path: `docs/specs/FEAT-001-legacy.md`
- task_status_path: `.claw/tasks/TASK-001.md`
- next_action: `board legacy action`

### TASK-bimo-001 - New task

- status: `ready`
- priority: `high`
- owner_role: `shared`
- spec_path: `docs/specs/FEAT-bimo-001-guided.md`
- task_status_path: `.claw/tasks/TASK-bimo-001-new-task.md`
- next_action: `board new action`

## Completed Tasks
""",
            encoding="utf-8",
        )
        (state_dir / "tasks" / "TASK-001.md").write_text(
            """---
kind: task-status
task_id: TASK-001
assignee: legacy-user
owner_role: shared
status: in_progress
branch: legacy
updated_at: 2026-07-18T00:00:00Z
updated_by: test
---

## Current State
- Next action: finish legacy work
""",
            encoding="utf-8",
        )
        (state_dir / "tasks" / "TASK-bimo-001-new-task.md").write_text(
            """---
kind: task-status
task_id: TASK-bimo-001
task_type: feature
feature_id: FEAT-bimo-001
assignee: bimo
owner_slug: bimo
owner_role: shared
status: in_progress
branch: feat/TASK-bimo-001-new-task
next_action: implement the parser
updated_at: 2026-07-18T00:00:00Z
updated_by: test
---

## Current State
- Next action: implement the parser
""",
            encoding="utf-8",
        )

    def test_field_level_aggregation_and_dual_ids(self) -> None:
        root, state_dir = self.make_project()
        self.write_fixture(root, state_dir)
        workflows = current_status.collect_workflows(state_dir)
        self.assertEqual([item.task_id for item in workflows], ["TASK-001", "TASK-bimo-001"])
        new = workflows[1]
        self.assertEqual(new.status, "in_progress")
        self.assertEqual(new.feature_id, "FEAT-bimo-001")
        self.assertEqual(new.user, "bimo")
        rendered = current_status.render_current_status(workflows, updated_by="test", limit=10)
        self.assertIn("active_task_count: 2", rendered)
        self.assertIn("TASK-bimo-001", rendered)
        self.assertLessEqual(len(rendered.splitlines()), 60)

    def test_empty_board_does_not_create_placeholder_task(self) -> None:
        _root, state_dir = self.make_project()
        (state_dir / "task-board.md").write_text("# Task Board\n\n## Active Tasks\n", encoding="utf-8")
        workflows = current_status.collect_workflows(state_dir)
        rendered = current_status.render_current_status(workflows, updated_by="test")
        self.assertEqual(workflows, [])
        self.assertIn("schema_version: 5", rendered)
        self.assertIn("active_task_count: 0", rendered)
        self.assertIn("active_tasks: []", rendered)
        self.assertIn("No active task", rendered)
        self.assertNotIn("TASK-001", rendered)

    def test_chinese_task_board_and_generated_hot_index_are_supported(self) -> None:
        _root, state_dir = self.make_project()
        (state_dir / "manifest.yaml").write_text(
            "schema_version: 5\nskill_version: 5.0.1\nlanguage: zh-CN\n",
            encoding="utf-8",
        )
        (state_dir / "task-board.md").write_text(
            "# 任务看板\n\n## 活跃任务\n\n### TASK-user-001 - 中文任务\n\n"
            "- status: `ready`\n- owner_role: `shared`\n"
            "- task_status_path: `.claw/tasks/TASK-user-001-localized.md`\n",
            encoding="utf-8",
        )
        (state_dir / "tasks" / "TASK-user-001-localized.md").write_text(
            "---\ntask_id: TASK-user-001\nstatus: ready\nowner_slug: user\n---\n",
            encoding="utf-8",
        )
        workflows = current_status.collect_workflows(state_dir)
        self.assertEqual([item.task_id for item in workflows], ["TASK-user-001"])
        rendered = current_status.render_current_status(
            workflows,
            updated_by="test",
            language="zh-CN",
        )
        self.assertIn("# 项目当前状态", rendered)
        self.assertIn("## 活跃工作流", rendered)
        self.assertNotIn("# Project Current Status", rendered)

    def test_terminal_task_status_overrides_a_stale_active_board_card(self) -> None:
        _root, state_dir = self.make_project()
        (state_dir / "task-board.md").write_text(
            """# Task Board

## Active Tasks

### TASK-user-001 - Stale card

- status: `ready`
- task_status_path: `.claw/tasks/TASK-user-001-stale.md`
""",
            encoding="utf-8",
        )
        (state_dir / "tasks" / "TASK-user-001-stale.md").write_text(
            """---
kind: task-status
task_id: TASK-user-001
status: done
---
""",
            encoding="utf-8",
        )

        self.assertEqual(current_status.collect_workflows(state_dir), [])

    def test_truncation_preserves_hot_file_budget(self) -> None:
        workflows = [
            current_status.Workflow(
                task_id=f"TASK-user-{number:03d}",
                title=f"Task {number}",
                user="user",
                feature_id="none",
                work_type="test",
                status="ready",
                branch="n/a",
                next_action="continue",
                task_status_path="missing",
            )
            for number in range(1, 31)
        ]
        rendered = current_status.render_current_status(workflows, updated_by="test", limit=8)
        self.assertIn("active_task_count: 30", rendered)
        self.assertIn("active_tasks_truncated: true", rendered)
        self.assertLessEqual(len(rendered.splitlines()), 60)

    def test_active_execution_is_not_hidden_by_older_review_cards(self) -> None:
        workflows = [
            current_status.Workflow(
                task_id=f"TASK-user-{number:03d}",
                title=f"Review {number}",
                user="user",
                feature_id="none",
                work_type="test",
                status="review",
                branch="n/a",
                next_action="wait for review",
                task_status_path="missing",
                priority="medium",
            )
            for number in range(1, 11)
        ]
        workflows.append(
            current_status.Workflow(
                task_id="TASK-user-011",
                title="New execution",
                user="user",
                feature_id="none",
                work_type="feature",
                status="in_progress",
                branch="work",
                next_action="continue implementation",
                task_status_path="missing",
                priority="high",
            )
        )

        rendered = current_status.render_current_status(workflows, updated_by="test", limit=10)

        self.assertIn("  - TASK-user-011", rendered)
        self.assertNotIn("  - TASK-user-010", rendered)
        self.assertIn('next_action: "continue implementation"', rendered)

    def test_team_status_parser_recognizes_new_ids_and_description_filename(self) -> None:
        root, state_dir = self.make_project()
        self.write_fixture(root, state_dir)
        board = team_status.parse_task_board(state_dir / "task-board.md")
        statuses = team_status.load_task_statuses(state_dir)
        self.assertIn("TASK-001", board)
        self.assertIn("TASK-bimo-001", board)
        self.assertIn("TASK-bimo-001", statuses)

        queue = state_dir / "integration-queue.md"
        queue.write_text(
            "- status: `ready`\n- related_tasks: `TASK-001, TASK-bimo-001`\n",
            encoding="utf-8",
        )
        self.assertEqual(
            team_status.parse_integration_queue(queue),
            {"TASK-001": "ready", "TASK-bimo-001": "ready"},
        )

    def test_team_status_cli_rejects_a_non_claw_state_directory(self) -> None:
        root = Path(tempfile.mkdtemp())
        state_dir = root / "state"
        state_dir.mkdir()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))

        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "summarize-team-status.py"), str(state_dir)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only the .claw state directory is supported", result.stderr)

    def test_description_lookup_does_not_match_a_longer_legacy_id(self) -> None:
        root, state_dir = self.make_project()
        candidate = state_dir / "tasks" / "TASK-0010-other-task.md"
        candidate.write_text("---\ntask_id: TASK-0010\n---\n", encoding="utf-8")
        card = {
            "task_id": "TASK-001",
            "task_status_path": ".claw/tasks/TASK-0010-other-task.md",
        }

        self.assertIsNone(current_status.resolve_task_status_path(root, state_dir, card))

    def test_locked_generation_preserves_initialization_fields(self) -> None:
        root, state_dir = self.make_project()
        self.write_fixture(root, state_dir)
        (state_dir / "current-status.md").write_text(
            """---
kind: current-status
schema_version: 5
init_status: complete
init_completed_at: 2026-07-18T00:00:00Z
init_confirmed_by: user
---
""",
            encoding="utf-8",
        )

        destination, rendered = current_status.generate_and_write_current_status(
            state_dir,
            updated_by="test",
        )

        self.assertEqual(destination, (state_dir / "current-status.md").resolve())
        self.assertEqual(destination.read_text(encoding="utf-8"), rendered)
        self.assertIn('init_status: "complete"', rendered)
        self.assertIn('init_confirmed_by: "user"', rendered)
        self.assertTrue((state_dir / ".locks" / "current-status.lock").is_file())


if __name__ == "__main__":
    unittest.main()
