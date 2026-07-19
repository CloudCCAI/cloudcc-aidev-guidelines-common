from __future__ import annotations

import argparse
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "create-codeup-change-request.py"
SPEC = importlib.util.spec_from_file_location("create_codeup_change_request", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CodeupTaskIdTests(unittest.TestCase):
    def test_extracts_v5_and_legacy_task_ids(self) -> None:
        self.assertEqual(MODULE.extract_task_id("feat/TASK-alice-001-login"), "TASK-alice-001")
        self.assertEqual(MODULE.extract_task_id("feat/TASK-123-001-login"), "TASK-123-001")
        self.assertEqual(MODULE.extract_task_id("feat/TASK-123-login"), "TASK-123")

    def test_rejects_invalid_explicit_task_id(self) -> None:
        args = argparse.Namespace(
            source_branch="feat/work",
            task="TASK-ALICE-001",
            title=None,
            description=None,
            description_file=None,
            trigger_ai_review=False,
        )
        config = {
            "repository_id": "1",
            "source_project_id": "1",
            "target_project_id": "1",
            "target_branch": "main",
            "create_from": "COMMAND_LINE",
            "trigger_ai_review": "",
            "reviewer_user_ids": "",
            "work_item_ids": "",
        }
        with self.assertRaisesRegex(SystemExit, "invalid task id"):
            MODULE.build_payload(args, config)

    def test_rejects_zero_v5_sequence(self) -> None:
        self.assertEqual(MODULE.extract_task_id("feat/TASK-alice-000-login"), "")
        self.assertEqual(MODULE.extract_task_id("feat/TASK-123-000-login"), "")

    def test_default_change_request_description_is_chinese(self) -> None:
        args = argparse.Namespace(description_file=None, description=None)
        rendered = MODULE.read_description(args, "TASK-alice-001", "feat/login", "main")
        self.assertIn("任务：TASK-alice-001", rendered)
        self.assertIn("源分支：feat/login", rendered)
        self.assertIn("验证：", rendered)


if __name__ == "__main__":
    unittest.main()
