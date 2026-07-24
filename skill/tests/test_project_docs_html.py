from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
GENERATOR = SCRIPTS_DIR / "generate-project-docs-html.py"
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.project_docs_html import (  # noqa: E402
    GENERATOR_VERSION,
    GENERATOR_VERSION_META,
    SOURCE_DIGEST_META,
    companion_path,
    inspect_pair,
    render_document,
    validate_project_documents,
)


SAMPLE_MARKDOWN = """---
kind: feature-spec
schema_version: 5
feature_id: FEAT-alice-001
title: "登录体验"
status: approved
owner_slug: alice
updated_at: 2026-07-23 01:02:03
updated_by: "Alice"
---

# FEAT-alice-001 - 登录体验

## 背景与目标

让用户更快完成登录，并显示 `trace_id`。

- 支持中文
- [x] 已确认范围

## 验收标准

| 场景 | 结果 |
|---|---|
| 正常登录 | 成功 |

```python
print("<safe>")
```

<script>alert("must be escaped")</script>
"""


class ProjectDocsHtmlTests(unittest.TestCase):
    def make_project(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "docs" / "design").mkdir(parents=True)
        (root / "docs" / "specs").mkdir(parents=True)
        return root

    def run_generator(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(GENERATOR), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_rendered_html_is_self_contained_readable_and_escaped(self) -> None:
        root = self.make_project()
        source = root / "docs" / "specs" / "FEAT-alice-001-login.md"
        source.write_text(SAMPLE_MARKDOWN, encoding="utf-8")

        rendered = render_document(
            source,
            project_root=root,
            generated_at="2026-07-23 02:00:00",
        )

        self.assertIn("<!doctype html>", rendered)
        self.assertIn(f'<meta name="{SOURCE_DIGEST_META}"', rendered)
        self.assertIn(f'<meta name="{GENERATOR_VERSION_META}"', rendered)
        self.assertIn("<title>登录体验</title>", rendered)
        self.assertIn("FEAT-alice-001", rendered)
        self.assertIn('<details class="document-section" open', rendered)
        self.assertIn("<table>", rendered)
        self.assertIn('type="checkbox" disabled checked', rendered)
        self.assertIn('class="language-python"', rendered)
        self.assertIn("&lt;script&gt;alert", rendered)
        self.assertNotIn("<script>alert", rendered)
        self.assertNotIn("kind: feature-spec", rendered)
        self.assertNotIn("https://", rendered)
        self.assertEqual(rendered.count("FEAT-alice-001 - 登录体验"), 0)

    def test_batch_write_check_and_stale_detection(self) -> None:
        root = self.make_project()
        spec = root / "docs" / "specs" / "feature.md"
        design = root / "docs" / "design" / "nested" / "flow.md"
        design.parent.mkdir()
        spec.write_text("# Feature\n\n## Goal\n\nText.\n", encoding="utf-8")
        design.write_text("# Flow\n\n## Main\n\nText.\n", encoding="utf-8")

        written = self.run_generator(
            str(root),
            "--write",
            "--now",
            "2026-07-23 02:00:00",
            "--json",
        )
        self.assertEqual(written.returncode, 0, written.stderr)
        payload = json.loads(written.stdout)
        self.assertEqual(payload["source_count"], 2)
        self.assertEqual(
            payload["written"],
            ["docs/design/nested/flow.html", "docs/specs/feature.html"],
        )
        self.assertTrue(companion_path(spec).is_file())
        self.assertTrue(companion_path(design).is_file())
        self.assertEqual(companion_path(spec).stat().st_mode & 0o777, 0o644)
        self.assertEqual(validate_project_documents(root), [])

        current = self.run_generator(str(root), "--json")
        self.assertEqual(current.returncode, 0, current.stdout)
        self.assertEqual(json.loads(current.stdout)["stale"], [])

        spec_html = companion_path(spec)
        spec_html.write_text(
            spec_html.read_text(encoding="utf-8").replace(
                f'<meta name="{GENERATOR_VERSION_META}" content="{GENERATOR_VERSION}">',
                f'<meta name="{GENERATOR_VERSION_META}" content="old">',
                1,
            ),
            encoding="utf-8",
        )
        self.assertEqual(inspect_pair(spec).reason, "generator version mismatch")
        refreshed = self.run_generator(str(spec), "--write")
        self.assertEqual(refreshed.returncode, 0, refreshed.stderr)

        spec.write_text("# Feature\n\nChanged.\n", encoding="utf-8")
        stale = self.run_generator(str(root), "--json")
        self.assertEqual(stale.returncode, 1)
        self.assertEqual(json.loads(stale.stdout)["stale"][0]["reason"], "source digest mismatch")
        self.assertIn("source digest mismatch", validate_project_documents(root)[0])

    def test_single_file_write_refreshes_only_its_companion(self) -> None:
        root = self.make_project()
        first = root / "docs" / "specs" / "first.md"
        second = root / "docs" / "specs" / "second.md"
        first.write_text("# First\n", encoding="utf-8")
        second.write_text("# Second\n", encoding="utf-8")

        result = self.run_generator(
            str(first),
            "--write",
            "--now",
            "2026-07-23 02:00:00",
            "--json",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(companion_path(first).is_file())
        self.assertFalse(companion_path(second).exists())
        self.assertTrue(inspect_pair(first).current)
        self.assertEqual(inspect_pair(second).reason, "missing")

    def test_target_outside_design_and_specs_is_rejected(self) -> None:
        root = self.make_project()
        source = root / "README.md"
        source.write_text("# Root\n", encoding="utf-8")

        result = self.run_generator(str(source), "--write")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("docs/design or docs/specs", result.stderr)

    def test_cli_rejects_historical_timestamp_override(self) -> None:
        root = self.make_project()

        result = self.run_generator(
            str(root),
            "--write",
            "--now",
            "2026-07-23T02:00:00Z",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--now must use YYYY-MM-DD HH:MM:SS", result.stderr)


if __name__ == "__main__":
    unittest.main()
