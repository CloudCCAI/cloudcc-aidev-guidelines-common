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
ARCHIVER = SCRIPTS_DIR / "archive-resolved-issues.py"
sys.path.insert(0, str(SCRIPTS_DIR))


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_state_for_issue_archive",
        SCRIPTS_DIR / "validate-state.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = load_validator()


def issue_list() -> str:
    return """---
kind: issue-list
schema_version: 5
version: 5
updated_at: 2026-07-24 01:00:00
updated_by: test
---

# 问题追踪列表

## 活跃问题

### ISSUE-003 — Still open

- severity: `high`
- status: `open`
- evidence: open evidence

### ISSUE-002 — Fixed but pending verification

- severity: `medium`
- status: `fixed`
- evidence: pending evidence

### ISSUE-001 — Fully verified

- severity: `low`
- status: `verified`
- evidence: verified evidence

## 最近关闭问题

- 暂无。

## 维护规则

- Keep facts.
"""


class IssueArchiveTests(unittest.TestCase):
    def make_state(self) -> tuple[Path, bytes]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        state_dir = Path(temporary.name) / ".claw"
        state_dir.mkdir()
        issue_path = state_dir / "issue-list.md"
        issue_path.write_text(issue_list(), encoding="utf-8")
        return state_dir, issue_path.read_bytes()

    def run_archiver(self, state_dir: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(ARCHIVER),
                str(state_dir),
                *arguments,
                "--now",
                "2026-07-24 02:00:00",
                "--updated-by",
                "tester",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_moves_only_verified_or_closed_and_is_idempotent(self) -> None:
        state_dir, _original = self.make_state()

        completed = self.run_archiver(state_dir, "--write")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["moved"], ["ISSUE-001"])
        current = (state_dir / "issue-list.md").read_text(encoding="utf-8")
        archive = (state_dir / "issue-archive.md").read_text(encoding="utf-8")
        self.assertIn("### ISSUE-003", current)
        self.assertIn("### ISSUE-002", current)
        self.assertNotIn("### ISSUE-001", current)
        self.assertIn("`ISSUE-001` — Fully verified", current)
        self.assertIn("### ISSUE-001", archive)
        self.assertIn("verified evidence", archive)

        repeated = self.run_archiver(state_dir, "--write")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertFalse(json.loads(repeated.stdout)["changed"])
        self.assertEqual(
            (state_dir / "issue-archive.md").read_text(encoding="utf-8").count("### ISSUE-001"),
            1,
        )

    def test_dry_run_does_not_write(self) -> None:
        state_dir, original = self.make_state()

        completed = self.run_archiver(state_dir)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["changed"])
        self.assertEqual((state_dir / "issue-list.md").read_bytes(), original)
        self.assertFalse((state_dir / "issue-archive.md").exists())

    def test_write_without_terminal_issue_does_not_create_archive(self) -> None:
        state_dir, _original = self.make_state()
        issue_path = state_dir / "issue-list.md"
        text = issue_path.read_text(encoding="utf-8").replace(
            "- status: `verified`",
            "- status: `fixed`",
        )
        issue_path.write_text(text, encoding="utf-8")
        original = issue_path.read_bytes()

        completed = self.run_archiver(state_dir, "--write")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertFalse(json.loads(completed.stdout)["changed"])
        self.assertEqual(issue_path.read_bytes(), original)
        self.assertFalse((state_dir / "issue-archive.md").exists())

    def test_validator_rejects_terminal_card_in_current_list(self) -> None:
        state_dir, _original = self.make_state()
        issue_path = state_dir / "issue-list.md"

        errors = validator.validate_file(issue_path, state_dir.parent)

        self.assertTrue(any("ISSUE-001" in error and "issue-archive.md" in error for error in errors), errors)

    def test_validator_accepts_migrated_files(self) -> None:
        state_dir, _original = self.make_state()

        completed = self.run_archiver(state_dir, "--write")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(validator.validate_file(state_dir / "issue-list.md", state_dir.parent), [])
        self.assertEqual(validator.validate_file(state_dir / "issue-archive.md", state_dir.parent), [])

    def test_legacy_issue_under_maintenance_moves_to_active_and_keeps_rules(self) -> None:
        state_dir, _original = self.make_state()
        issue_path = state_dir / "issue-list.md"
        text = issue_path.read_text(encoding="utf-8").replace(
            "## 维护规则\n\n- Keep facts.",
            "## 维护规则\n\n"
            "### ISSUE-004 - Misplaced active issue\n\n"
            "- Severity: `high`; Status: `in_progress`.\n"
            "- Pending: runtime verification.\n\n"
            "- 发现新问题时新增条目。\n"
            "- 保留所有维护规则。",
        )
        issue_path.write_text(text, encoding="utf-8")

        completed = self.run_archiver(state_dir, "--write")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        current = issue_path.read_text(encoding="utf-8")
        self.assertLess(current.index("### ISSUE-004"), current.index("## 最近关闭问题"))
        self.assertIn("- 发现新问题时新增条目。", current)
        self.assertIn("- 保留所有维护规则。", current)


if __name__ == "__main__":
    unittest.main()
