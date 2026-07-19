from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.document_ids import (  # noqa: E402
    document_id_from_path,
    extract_feature_ids,
    extract_task_ids,
    is_feature_id,
    is_legacy_id,
    is_task_id,
    is_v5_id,
    reserve_document,
)
from lib.state_io import read_front_matter  # noqa: E402


class DocumentIdTests(unittest.TestCase):
    def make_project(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / ".claw" / "tasks").mkdir(parents=True)
        (root / "docs" / "specs").mkdir(parents=True)
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        return root

    def test_old_and_new_ids_coexist(self) -> None:
        self.assertTrue(is_task_id("TASK-001"))
        self.assertTrue(is_task_id("TASK-bimo-001"))
        self.assertTrue(is_feature_id("FEAT-001"))
        self.assertTrue(is_feature_id("FEAT-bimo-001"))
        self.assertTrue(is_legacy_id("TASK-001"))
        self.assertTrue(is_v5_id("TASK-bimo-001"))
        self.assertFalse(is_task_id("TASK-bimo-000"))
        self.assertFalse(is_feature_id("FEAT-bimo-000"))
        self.assertFalse(is_task_id("TASK-123-000"))
        self.assertFalse(is_feature_id("FEAT-123-000"))
        self.assertEqual(extract_task_ids("TASK-bimo-000"), [])
        self.assertEqual(extract_feature_ids("FEAT-bimo-000"), [])
        self.assertEqual(
            extract_task_ids("TASK-001, feat/TASK-bimo-001-login and TASK-bimo-001 again"),
            ["TASK-001", "TASK-bimo-001"],
        )
        self.assertEqual(extract_feature_ids("docs/specs/FEAT-xu-hm-007-login.md"), ["FEAT-xu-hm-007"])
        self.assertEqual(extract_task_ids(".claw/tasks/TASK-123-001-numeric.md"), ["TASK-123-001"])
        self.assertEqual(extract_feature_ids("docs/specs/FEAT-123-001-numeric.md"), ["FEAT-123-001"])
        self.assertEqual(extract_task_ids("TASK-123-000-description"), [])
        self.assertEqual(extract_feature_ids("FEAT-123-000-description"), [])
        self.assertEqual(extract_task_ids("TASK-123-description"), ["TASK-123"])
        self.assertEqual(extract_feature_ids("FEAT-123-description"), ["FEAT-123"])

    def test_description_is_not_part_of_canonical_id(self) -> None:
        path = Path("TASK-bimo-001-implement-login-api.md")
        self.assertEqual(document_id_from_path(path, "task"), "TASK-bimo-001")
        self.assertEqual(document_id_from_path(path, "task", "TASK-bimo-001"), "TASK-bimo-001")
        self.assertEqual(document_id_from_path(Path("TASK-123-001-numeric.md"), "task"), "TASK-123-001")
        self.assertEqual(document_id_from_path(Path("FEAT-123-001-numeric.md"), "feature"), "FEAT-123-001")
        with self.assertRaises(ValueError):
            document_id_from_path(Path("TASK-123-000-description.md"), "task")
        with self.assertRaises(ValueError):
            document_id_from_path(Path("FEAT-123-000-description.md"), "feature")
        with self.assertRaises(ValueError):
            document_id_from_path(path, "task", "TASK-alice-001")

    def test_personal_counters_are_independent_and_not_reused(self) -> None:
        root = self.make_project()
        first = reserve_document(
            root,
            kind="task",
            owner="Alice Smith",
            description="first task",
            content="id: {{DOCUMENT_ID}}\n",
        )
        bob = reserve_document(
            root,
            kind="task",
            owner="Bob",
            description="first task",
            content="id: {{DOCUMENT_ID}}\n",
        )
        first.path.unlink()
        second = reserve_document(
            root,
            kind="task",
            owner="Alice Smith",
            description="second task",
            content="id: {{DOCUMENT_ID}}\n",
        )
        self.assertEqual(first.document_id, "TASK-alice-smith-001")
        self.assertEqual(bob.document_id, "TASK-bob-001")
        self.assertEqual(second.document_id, "TASK-alice-smith-002")

    def test_filename_reserves_id_when_custom_front_matter_is_richer(self) -> None:
        root = self.make_project()
        first = reserve_document(
            root,
            kind="task",
            owner="Alice",
            description="custom metadata",
            content="""---
task_id: {{DOCUMENT_ID}}
schema_version: 5
custom:
  nested: value
---
""",
        )
        (root / ".claw" / "document-id-registry.json").unlink()

        second = reserve_document(
            root,
            kind="task",
            owner="Alice",
            description="after registry recovery",
            content="task_id: {{DOCUMENT_ID}}\n",
        )

        self.assertEqual(first.document_id, "TASK-alice-001")
        self.assertEqual(second.document_id, "TASK-alice-002")

    def test_concurrent_cli_allocations_are_unique(self) -> None:
        root = self.make_project()
        script = SCRIPTS_DIR / "allocate-document-id.py"
        processes = [
            subprocess.Popen(
                [
                    sys.executable,
                    str(script),
                    "task",
                    "--project-root",
                    str(root),
                    "--owner",
                    "alice",
                    "--description",
                    f"parallel-{index}",
                    "--json",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for index in range(6)
        ]
        results: list[dict[str, object]] = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=20)
            self.assertEqual(process.returncode, 0, stderr)
            results.append(json.loads(stdout))

        ids = {str(result["document_id"]) for result in results}
        self.assertEqual(ids, {f"TASK-alice-{number:03d}" for number in range(1, 7)})
        registry = json.loads((root / ".claw" / "document-id-registry.json").read_text(encoding="utf-8"))
        self.assertEqual(len(registry["allocations"]), 6)

    def test_cli_default_documents_have_v5_creator_attribution(self) -> None:
        root = self.make_project()
        script = SCRIPTS_DIR / "allocate-document-id.py"
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "task",
                "--project-root",
                str(root),
                "--owner",
                "Alice Smith",
                "--created-by",
                "Alice",
                "--description",
                "v5 metadata",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        allocation = json.loads(result.stdout)
        fields, _body = read_front_matter(root / str(allocation["path"]))

        self.assertEqual(fields["schema_version"], "5")
        self.assertEqual(fields["policy_version"], "3")
        self.assertEqual(fields["owner_slug"], "alice-smith")
        self.assertEqual(fields["created_by"], "Alice")
        self.assertEqual(fields["created_by_slug"], "alice-smith")
        self.assertEqual(fields["created_by_source"], "user_confirmed")
        self.assertEqual(fields["created_by_developer_id"], "none")

        feature_result = subprocess.run(
            [
                sys.executable,
                str(script),
                "feature",
                "--project-root",
                str(root),
                "--owner",
                "Alice Smith",
                "--created-by",
                "Alice",
                "--description",
                "feature metadata",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(feature_result.returncode, 0, feature_result.stderr)
        feature_allocation = json.loads(feature_result.stdout)
        feature_fields, _body = read_front_matter(root / str(feature_allocation["path"]))
        self.assertEqual(feature_fields["schema_version"], "5")
        self.assertEqual(feature_fields["policy_version"], "3")
        self.assertEqual(feature_fields["created_by_slug"], "alice-smith")
        self.assertEqual(feature_fields["created_by_source"], "user_confirmed")
        self.assertEqual(feature_fields["created_by_developer_id"], "none")
        self.assertEqual(feature_fields["contributors"], ["Alice"])
        self.assertIn("related_decisions", feature_fields)
        self.assertIn("related_issues", feature_fields)
        feature_body = (root / str(feature_allocation["path"])).read_text(encoding="utf-8")
        self.assertIn("## Current and Target Behavior", feature_body)
        self.assertIn("## Risks and Rollback", feature_body)

    def test_cli_prefers_global_git_name_over_project_local_name(self) -> None:
        root = self.make_project()
        subprocess.run(["git", "init", str(root)], capture_output=True, text=True, check=True)
        subprocess.run(
            ["git", "-C", str(root), "config", "user.name", "Repository Local"],
            capture_output=True,
            text=True,
            check=True,
        )
        global_config = root / "global.gitconfig"
        global_config.write_text("[user]\n\tname = Global Alice\n", encoding="utf-8")
        env = os.environ.copy()
        env["GIT_CONFIG_GLOBAL"] = str(global_config)
        env["LOGNAME"] = "system-user"
        env["USER"] = "system-user"

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "allocate-document-id.py"),
                "task",
                "--project-root",
                str(root),
                "--description",
                "global identity",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        allocation = json.loads(result.stdout)
        self.assertEqual(allocation["document_id"], "TASK-global-alice-001")
        fields, _body = read_front_matter(root / str(allocation["path"]))
        self.assertEqual(fields["owner_slug"], "global-alice")
        self.assertEqual(fields["created_by_source"], "global_git_config_user_name")

    def test_cli_uses_project_local_git_name_when_global_name_is_missing(self) -> None:
        root = self.make_project()
        subprocess.run(["git", "init", str(root)], capture_output=True, text=True, check=True)
        subprocess.run(
            ["git", "-C", str(root), "config", "user.name", "Project Alice"],
            capture_output=True,
            text=True,
            check=True,
        )
        empty_global_config = root / "empty-global.gitconfig"
        empty_global_config.write_text("", encoding="utf-8")
        env = os.environ.copy()
        env["GIT_CONFIG_GLOBAL"] = str(empty_global_config)
        env["LOGNAME"] = "system-user"
        env["USER"] = "system-user"

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "allocate-document-id.py"),
                "task",
                "--project-root",
                str(root),
                "--description",
                "project identity",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        allocation = json.loads(result.stdout)
        self.assertEqual(allocation["document_id"], "TASK-project-alice-001")
        fields, _body = read_front_matter(root / str(allocation["path"]))
        self.assertEqual(fields["owner_slug"], "project-alice")
        self.assertEqual(fields["created_by_source"], "project_git_config_user_name")

    def test_cli_falls_back_to_os_user_when_global_git_name_is_missing(self) -> None:
        root = self.make_project()
        empty_global_config = root / "empty-global.gitconfig"
        empty_global_config.write_text("", encoding="utf-8")
        env = os.environ.copy()
        env["GIT_CONFIG_GLOBAL"] = str(empty_global_config)
        env["LOGNAME"] = "system-user"
        env["USER"] = "system-user"

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "allocate-document-id.py"),
                "feature",
                "--project-root",
                str(root),
                "--description",
                "os identity",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        allocation = json.loads(result.stdout)
        self.assertEqual(allocation["document_id"], "FEAT-system-user-001")
        fields, _body = read_front_matter(root / str(allocation["path"]))
        self.assertEqual(fields["owner_slug"], "system-user")
        self.assertEqual(fields["created_by_source"], "os_user")

    def test_cli_uses_manifest_language_for_new_documents(self) -> None:
        root = self.make_project()
        (root / ".claw" / "manifest.yaml").write_text(
            "schema_version: 5\nskill_version: 5.0.1\nlanguage: zh-CN\n",
            encoding="utf-8",
        )
        script = SCRIPTS_DIR / "allocate-document-id.py"
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "feature",
                "--project-root",
                str(root),
                "--owner",
                "Alice",
                "--description",
                "localized feature",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        allocation = json.loads(result.stdout)
        body = (root / str(allocation["path"])).read_text(encoding="utf-8")
        self.assertIn("## 当前行为与目标行为", body)
        self.assertNotIn("## Current and Target Behavior", body)

    def test_task_creation_requires_a_confirmed_referenced_feature(self) -> None:
        root = self.make_project()
        script = SCRIPTS_DIR / "allocate-document-id.py"
        feature_result = subprocess.run(
            [
                sys.executable,
                str(script),
                "feature",
                "--project-root",
                str(root),
                "--owner",
                "Alice",
                "--description",
                "confirmation gate",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(feature_result.returncode, 0, feature_result.stderr)
        feature = json.loads(feature_result.stdout)
        feature_path = root / str(feature["path"])

        blocked = subprocess.run(
            [
                sys.executable,
                str(script),
                "task",
                "--project-root",
                str(root),
                "--owner",
                "Alice",
                "--feature-id",
                str(feature["document_id"]),
                "--description",
                "blocked before confirmation",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("user-confirmed", blocked.stderr)

        content = feature_path.read_text(encoding="utf-8")
        content = content.replace("status: draft", "status: approved", 1)
        content = content.replace("init_status: awaiting_confirmation", "init_status: complete", 1)
        content = content.replace("init_completed_at: none", "init_completed_at: 2026-07-18T02:00:00Z", 1)
        content = content.replace("init_confirmed_by: none", "init_confirmed_by: Alice", 1)
        feature_path.write_text(content, encoding="utf-8")

        allowed = subprocess.run(
            [
                sys.executable,
                str(script),
                "task",
                "--project-root",
                str(root),
                "--owner",
                "Alice",
                "--feature-id",
                str(feature["document_id"]),
                "--description",
                "allowed after confirmation",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        task = json.loads(allowed.stdout)
        task_fields, _body = read_front_matter(root / str(task["path"]))
        self.assertIn("change_request_url", task_fields)
        self.assertIn("pr_url", task_fields)


if __name__ == "__main__":
    unittest.main()
