from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "push-test-environment.py"


class PushTestEnvironmentTests(unittest.TestCase):
    def test_dry_run_never_claims_a_real_push(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.name", "Test User"], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.email", "test@example.com"], check=True)
            (project / "README.md").write_text("test\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(project), "add", "README.md"], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-qm", "initial"], check=True)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--no-fetch",
                    "--source-branch",
                    "feat/TASK-user-001-example",
                    "--target-branch",
                    "dev",
                    "--remote",
                    "origin",
                ],
                cwd=project,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Dry run complete; no branch was changed or pushed.", result.stdout)
            self.assertNotIn("Pushed dev to origin", result.stdout)


if __name__ == "__main__":
    unittest.main()
