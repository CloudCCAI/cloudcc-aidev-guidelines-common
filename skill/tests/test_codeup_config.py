from __future__ import annotations

import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.codeup_config import config_value, merge_env_file, parse_env_file, write_env_file


class CodeupConfigTests(unittest.TestCase):
    def test_parser_accepts_export_and_shell_quoted_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "codeup.env"
            path.write_text(
                "# ignored\nexport CODEUP_TARGET_BRANCH='release branch'\nYUNXIAO_TOKEN=token-1\n",
                encoding="utf-8",
            )
            self.assertEqual(
                parse_env_file(path),
                {"CODEUP_TARGET_BRANCH": "release branch", "YUNXIAO_TOKEN": "token-1"},
            )

    def test_explicit_then_process_then_file_then_default_precedence(self) -> None:
        values = {"SETTING": "file"}
        with patch.dict(os.environ, {"SETTING": "process"}, clear=False):
            self.assertEqual(config_value("SETTING", "explicit", values, "default"), "explicit")
            self.assertEqual(config_value("SETTING", None, values, "default"), "process")
        self.assertEqual(config_value("SETTING", None, values, "default"), "file")
        self.assertEqual(config_value("MISSING", None, values, "default"), "default")

    def test_token_rotation_preserves_existing_codeup_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".claw-local" / "codeup.env"
            write_env_file(
                path,
                {
                    "CODEUP_REPOSITORY_ID": "42",
                    "CODEUP_TARGET_BRANCH": "main",
                    "YUNXIAO_TOKEN": "old-token",
                },
            )
            merge_env_file(path, {"YUNXIAO_TOKEN": "new-token"})
            self.assertEqual(
                parse_env_file(path),
                {
                    "CODEUP_REPOSITORY_ID": "42",
                    "CODEUP_TARGET_BRANCH": "main",
                    "YUNXIAO_TOKEN": "new-token",
                },
            )

    def test_writer_uses_owner_only_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".claw-local" / "codeup.env"
            write_env_file(path, {"YUNXIAO_TOKEN": "secret"})
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)


if __name__ == "__main__":
    unittest.main()
