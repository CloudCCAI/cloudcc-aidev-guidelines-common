from __future__ import annotations

import importlib.util
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


legacy_snapshot = load_script("snapshot_legacy_documents", "snapshot-legacy-documents.py")
state_validator = load_script("validate_state_for_snapshot", "validate-state.py")


class LegacySnapshotTests(unittest.TestCase):
    def make_project(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / ".claw" / "tasks").mkdir(parents=True)
        (root / "docs" / "specs").mkdir(parents=True)
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        return root

    def test_snapshot_is_idempotent_and_records_old_and_new_ids(self) -> None:
        root = self.make_project()
        (root / ".claw" / "current-status.md").write_text("legacy\n", encoding="utf-8")
        (root / ".claw" / "tasks" / "TASK-001.md").write_text("legacy task\n", encoding="utf-8")
        (root / "docs" / "specs" / "FEAT-bimo-001-guided.md").write_text("new style before policy\n", encoding="utf-8")

        path, created = legacy_snapshot.create_snapshot(root, created_by="test")
        original = path.read_text(encoding="utf-8")
        same_path, created_again = legacy_snapshot.create_snapshot(root, created_by="other")
        snapshot = legacy_snapshot.load_snapshot(path)

        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(path, same_path)
        self.assertEqual(original, path.read_text(encoding="utf-8"))
        self.assertIn("captured_at", snapshot)
        self.assertIn("policy_effective_at", snapshot)
        self.assertIn("\n  - {", original)
        self.assertNotIn("\n  - \"{", original)
        parsed, parse_errors = state_validator.read_yaml_document(path)
        validation_errors, _legacy_paths = state_validator.validate_legacy_index_data(path, parsed, root)
        self.assertEqual(parse_errors, [])
        self.assertEqual(validation_errors, [])
        self.assertIsInstance(parsed["documents"][0], dict)
        ids = {
            item_id
            for entry in snapshot["documents"]
            for item_id in entry.get("document_ids", [])
        }
        self.assertIn("TASK-001", ids)
        self.assertIn("FEAT-bimo-001", ids)

    def test_verify_reports_new_changed_and_missing_paths_without_rewriting(self) -> None:
        root = self.make_project()
        current = root / ".claw" / "current-status.md"
        removed = root / ".claw" / "goals.md"
        current.write_text("one\n", encoding="utf-8")
        removed.write_text("old\n", encoding="utf-8")
        path, _created = legacy_snapshot.create_snapshot(root, created_by="test")
        original = path.read_text(encoding="utf-8")

        current.write_text("two\n", encoding="utf-8")
        removed.unlink()
        new_path = root / ".claw" / "tasks" / "TASK-002.md"
        new_path.write_text("new\n", encoding="utf-8")
        result = legacy_snapshot.verify_snapshot(root)

        self.assertIn(".claw/current-status.md", result["changed_paths"])
        self.assertIn(".claw/goals.md", result["missing_paths"])
        self.assertIn(".claw/tasks/TASK-002.md", result["new_paths"])
        self.assertEqual(original, path.read_text(encoding="utf-8"))

    def test_missing_state_directory_is_rejected_without_creating_it(self) -> None:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))

        with self.assertRaisesRegex(ValueError, r"\.claw state directory does not exist"):
            legacy_snapshot.create_snapshot(root, created_by="test")

        self.assertFalse((root / ".claw").exists())

    def test_loader_accepts_conventional_block_mapping_documents(self) -> None:
        root = self.make_project()
        path = root / ".claw" / "legacy-document-index.yaml"
        path.write_text(
            """kind: legacy-document-index
schema_version: 1
captured_at: 2026-07-18T00:00:00Z
policy_effective_at: 2026-07-18T00:00:00Z
documents:
  - path: .claw/tasks/TASK-001.md
    kind: task-status
    id: TASK-001
    schema_version: 4
    document_ids:
      - TASK-001
""",
            encoding="utf-8",
        )

        snapshot = legacy_snapshot.load_snapshot(path)

        self.assertEqual(snapshot["documents"][0]["path"], ".claw/tasks/TASK-001.md")
        self.assertEqual(snapshot["documents"][0]["document_ids"], ["TASK-001"])

    def test_snapshot_excludes_v5_documents_but_keeps_mixed_legacy_documents(self) -> None:
        root = self.make_project()
        legacy_task = root / ".claw" / "tasks" / "TASK-001.md"
        legacy_task.write_text(
            "---\nkind: task-status\nschema_version: 4\ntask_id: TASK-001\n---\n",
            encoding="utf-8",
        )
        legacy_id_with_v5_schema = root / ".claw" / "tasks" / "TASK-002.md"
        legacy_id_with_v5_schema.write_text(
            "---\nkind: task-status\nschema_version: 5\ntask_id: TASK-002\n---\n",
            encoding="utf-8",
        )
        new_task = root / ".claw" / "tasks" / "TASK-alice-001-new.md"
        new_task.write_text(
            "---\nkind: task-status\nschema_version: 5\ntask_id: TASK-alice-001\n---\n",
            encoding="utf-8",
        )
        new_core = root / ".claw" / "current-status.md"
        new_core.write_text(
            "---\nkind: current-status\nschema_version: 5\n---\n",
            encoding="utf-8",
        )
        legacy_feature = root / "docs" / "specs" / "FEAT-old-001-before-policy.md"
        legacy_feature.write_text(
            "---\nkind: feature-spec\nschema_version: 4\nfeature_id: FEAT-old-001\n---\n",
            encoding="utf-8",
        )
        legacy_feature_id_with_v5_schema = root / "docs" / "specs" / "FEAT-001.md"
        legacy_feature_id_with_v5_schema.write_text(
            "---\nkind: feature-spec\nschema_version: 5\nfeature_id: FEAT-001\n---\n",
            encoding="utf-8",
        )
        new_feature = root / "docs" / "specs" / "FEAT-alice-001-mentions-TASK-001.md"
        new_feature.write_text(
            "---\nkind: feature-spec\nschema_version: 5\nfeature_id: FEAT-alice-001\n---\n",
            encoding="utf-8",
        )

        entries = legacy_snapshot.build_entries(root)
        indexed_paths = {str(entry["path"]) for entry in entries}

        self.assertIn(".claw/tasks/TASK-001.md", indexed_paths)
        self.assertIn(".claw/tasks/TASK-002.md", indexed_paths)
        self.assertIn("docs/specs/FEAT-old-001-before-policy.md", indexed_paths)
        self.assertIn("docs/specs/FEAT-001.md", indexed_paths)
        self.assertNotIn(".claw/tasks/TASK-alice-001-new.md", indexed_paths)
        self.assertNotIn(".claw/current-status.md", indexed_paths)
        self.assertNotIn("docs/specs/FEAT-alice-001-mentions-TASK-001.md", indexed_paths)

if __name__ == "__main__":
    unittest.main()
