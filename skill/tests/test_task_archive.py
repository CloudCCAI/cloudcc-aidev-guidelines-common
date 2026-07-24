from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
ARCHIVER = SCRIPTS_DIR / "archive-completed-tasks.py"
sys.path.insert(0, str(SCRIPTS_DIR))


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_state_for_task_archive",
        SCRIPTS_DIR / "validate-state.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = load_validator()


def task_card(number: int, *, status: str = "done") -> str:
    task_id = f"TASK-{number:03d}"
    return (
        f"### {task_id} - Task {number}\n\n"
        f"- status: `{status}`\n"
        "- priority: `medium`\n"
        "- owner_role: `shared`\n"
        f"- task_status_path: `.claw/tasks/{task_id}.md`\n"
        "- next_action: `none`\n"
    )


def task_board(count: int) -> str:
    cards = "\n".join(task_card(number) for number in range(count, 0, -1))
    return (
        "---\n"
        "kind: task-board\n"
        "schema_version: 5\n"
        "updated_at: 2026-07-24 01:00:00\n"
        "updated_by: test\n"
        "---\n\n"
        "# Task Board\n\n"
        "## Active Tasks\n\n"
        "## Completed Tasks\n\n"
        f"{cards}\n"
        "## Maintenance Rules\n"
    )


class TaskArchiveTests(unittest.TestCase):
    def make_state(self, count: int = 7) -> tuple[Path, bytes]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        state_dir = root / ".claw"
        tasks_dir = state_dir / "tasks"
        tasks_dir.mkdir(parents=True)
        board = state_dir / "task-board.md"
        board.write_text(task_board(count), encoding="utf-8")
        for number in range(count, 0, -1):
            task_path = tasks_dir / f"TASK-{number:03d}.md"
            task_path.write_text(f"task {number}\n", encoding="utf-8")
        return state_dir, board.read_bytes()

    def run_archiver(self, state_dir: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(ARCHIVER),
                str(state_dir),
                *arguments,
                "--now",
                "2026-07-24 02:00:00",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_dry_run_reports_overflow_without_writing(self) -> None:
        state_dir, original_board = self.make_state()

        completed = self.run_archiver(state_dir)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["moved"], ["TASK-002", "TASK-001"])
        self.assertEqual(payload["kept_count"], 5)
        self.assertEqual((state_dir / "task-board.md").read_bytes(), original_board)
        self.assertFalse((state_dir / "task-archive.md").exists())

    def test_write_moves_oldest_cards_and_preserves_task_facts(self) -> None:
        state_dir, _original_board = self.make_state()
        task_facts = {
            path.name: path.read_bytes()
            for path in (state_dir / "tasks").glob("TASK-*.md")
        }

        completed = self.run_archiver(state_dir, "--write")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        board = (state_dir / "task-board.md").read_text(encoding="utf-8")
        archive = (state_dir / "task-archive.md").read_text(encoding="utf-8")
        self.assertEqual(board.count("\n### TASK-"), 5)
        self.assertNotIn("### TASK-002", board)
        self.assertNotIn("### TASK-001", board)
        self.assertIn("### TASK-002", archive)
        self.assertIn("### TASK-001", archive)
        self.assertEqual(archive.count("- archived_at: `2026-07-24 02:00:00`"), 2)
        for name, content in task_facts.items():
            self.assertEqual((state_dir / "tasks" / name).read_bytes(), content)

        repeated = self.run_archiver(state_dir, "--write")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertFalse(json.loads(repeated.stdout)["changed"])
        self.assertEqual(
            (state_dir / "task-archive.md").read_text(encoding="utf-8").count("### TASK-"),
            2,
        )

    def test_validator_requires_archiving_after_five_completed_cards(self) -> None:
        state_dir, _original_board = self.make_state(6)
        board_path = state_dir / "task-board.md"
        text = board_path.read_text(encoding="utf-8")
        body = text.split("---", 2)[2]

        errors = validator.validate_task_board(board_path, body, state_dir.parent)

        self.assertTrue(any("at most 5 remain" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
