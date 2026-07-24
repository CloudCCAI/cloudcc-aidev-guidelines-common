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
ARCHIVER = SCRIPTS_DIR / "archive-test-reports.py"
sys.path.insert(0, str(SCRIPTS_DIR))


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_state_for_test_archive",
        SCRIPTS_DIR / "validate-state.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = load_validator()


def normalized_report(count: int) -> str:
    entries = []
    for number in range(count, 0, -1):
        status = "PENDING" if number <= 2 else "PASS"
        entries.append(
            f"### Run {number}\n\n"
            f"- 状态：`{status}`\n"
            f"- 证据：evidence-{number}\n"
        )
    return (
        "---\n"
        "kind: test-report\n"
        "schema_version: 5\n"
        "updated_at: 2026-07-24 01:00:00\n"
        "updated_by: test\n"
        "last_run_at: 2026-07-24 01:00:00\n"
        "last_run_status: partial\n"
        "---\n\n"
        "# 测试报告\n\n"
        "## 最新运行摘要\n\n"
        "- 状态：`partial`\n"
        "- 范围：Run\n\n"
        "## 待处理验证项\n\n"
        "- existing pending index\n\n"
        "## 最近测试记录\n\n"
        + "\n".join(entries)
        + "\n## 维护规则\n"
    )


def legacy_report(count: int) -> str:
    entries = []
    for number in range(count, 0, -1):
        status = "BLOCKED" if number == 1 else "PASS"
        entries.append(
            f"## Legacy Run {number} (2026-07-{number:02d})\n\n"
            "| Check | Result | Notes |\n"
            "| --- | --- | --- |\n"
            f"| command-{number} | {status} | evidence-{number} |\n"
        )
    return (
        "---\n"
        "kind: test-report\n"
        "version: 83\n"
        "updated_at: 2026-07-24T01:00:00Z\n"
        "updated_by: test\n"
        "last_run_at: 2026-07-24T01:00:00Z\n"
        "last_run_status: partial\n"
        "---\n\n"
        + "\n".join(entries)
    )


class TestArchiveTests(unittest.TestCase):
    def make_state(self, report: str) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        state_dir = Path(temporary.name) / ".claw"
        state_dir.mkdir()
        (state_dir / "test-report.md").write_text(report, encoding="utf-8")
        return state_dir

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

    def test_normalized_report_keeps_five_and_archives_overflow(self) -> None:
        state_dir = self.make_state(normalized_report(7))

        completed = self.run_archiver(state_dir, "--write")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["moved_count"], 2)
        report = (state_dir / "test-report.md").read_text(encoding="utf-8")
        archive = (state_dir / "test-archive.md").read_text(encoding="utf-8")
        self.assertEqual(report.count("\n### Run "), 5)
        self.assertNotIn("### Run 2", report)
        self.assertNotIn("### Run 1", report)
        self.assertIn("### Run 2", archive)
        self.assertIn("### Run 1", archive)
        self.assertIn("kind: test-archive", archive)
        self.assertIn("PENDING 2", report)

        repeated = self.run_archiver(state_dir, "--write")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertFalse(json.loads(repeated.stdout)["changed"])
        self.assertEqual(
            (state_dir / "test-archive.md").read_text(encoding="utf-8").count("### Run "),
            2,
        )

    def test_legacy_report_migration_preserves_older_evidence(self) -> None:
        state_dir = self.make_state(legacy_report(7))

        completed = self.run_archiver(state_dir, "--write")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "legacy_migration")
        self.assertEqual(payload["moved_count"], 2)
        report_path = state_dir / "test-report.md"
        report = report_path.read_text(encoding="utf-8")
        archive = (state_dir / "test-archive.md").read_text(encoding="utf-8")
        self.assertIn("schema_version: 5", report)
        self.assertEqual(report.count("\n### Legacy Run "), 5)
        self.assertIn("| command-2 | PASS | evidence-2 |", archive)
        self.assertIn("| command-1 | BLOCKED | evidence-1 |", archive)
        self.assertIn("BLOCKED 1", report)
        self.assertLessEqual(len(report.splitlines()), 150)
        self.assertEqual(validator.validate_file(report_path, state_dir.parent), [])

    def test_dry_run_does_not_create_archive_or_rewrite_report(self) -> None:
        state_dir = self.make_state(normalized_report(6))
        report_path = state_dir / "test-report.md"
        original = report_path.read_bytes()

        completed = self.run_archiver(state_dir)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["changed"])
        self.assertEqual(report_path.read_bytes(), original)
        self.assertFalse((state_dir / "test-archive.md").exists())

    def test_validator_rejects_more_than_five_recent_records(self) -> None:
        state_dir = self.make_state(normalized_report(6))
        report_path = state_dir / "test-report.md"

        errors = validator.validate_file(report_path, state_dir.parent)

        self.assertTrue(any("at most 5 remain" in error for error in errors), errors)

    def test_legacy_archive_name_is_readable_but_not_used_for_new_writes(self) -> None:
        state_dir = self.make_state(normalized_report(6))
        legacy_archive = state_dir / "test-report-archive.md"
        legacy_archive.write_text(
            "---\n"
            "kind: test-report-archive\n"
            "version: 5\n"
            "updated_at: 2026-07-24 01:00:00\n"
            "updated_by: test\n"
            "---\n\n"
            "# Legacy test archive\n",
            encoding="utf-8",
        )

        self.assertEqual(validator.validate_file(legacy_archive, state_dir.parent), [])
        completed = self.run_archiver(state_dir, "--write")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("rename it to test-archive.md", completed.stderr)
        self.assertFalse((state_dir / "test-archive.md").exists())


if __name__ == "__main__":
    unittest.main()
