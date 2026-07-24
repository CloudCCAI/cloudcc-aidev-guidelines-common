from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from urllib.request import Request


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "check-skill-version.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_skill_version_for_tests", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_module()


class FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        return False

    def read(self) -> bytes:
        return self.payload


class SkillVersionCheckTests(unittest.TestCase):
    def test_git_ref_lookup_and_pinned_raw_fetch_bypass_branch_cache(self) -> None:
        commit = "a" * 40
        requests: list[Request] = []
        git_calls: list[list[str]] = []

        def opener(request: Request, *, timeout: float):
            self.assertEqual(timeout, 3.0)
            requests.append(request)
            return FakeResponse(b'---\nmetadata:\n  skill_version: "5.1.1"\n---\n')

        def git_runner(command: list[str], **kwargs):
            self.assertEqual(kwargs["timeout"], 3.0)
            git_calls.append(command)
            return SimpleNamespace(returncode=0, stdout=f"{commit}\trefs/heads/main\n", stderr="")

        upstream = checker.fetch_upstream(
            repository="CloudCCAI/cloudcc-aidev-guidelines-common",
            branch="main",
            skill_path="skill/SKILL.md",
            timeout=3.0,
            opener=opener,
            git_runner=git_runner,
            nonce_factory=lambda: "nonce-raw",
        )

        self.assertEqual(upstream["upstream_commit"], commit)
        self.assertEqual(upstream["upstream_version"], "5.1.1")
        self.assertEqual(upstream["commit_source"], "git_ls_remote")
        self.assertEqual(
            upstream["upstream_install_url"],
            f"https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common/tree/{commit}/skill",
        )
        self.assertEqual(
            git_calls,
            [[
                "git",
                "ls-remote",
                "--exit-code",
                "https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common.git",
                "refs/heads/main",
            ]],
        )
        self.assertIn(f"/{commit}/skill/SKILL.md?cache_bust=nonce-raw", requests[0].full_url)
        for request in requests:
            self.assertEqual(request.get_header("Cache-control"), "no-cache, no-store, max-age=0")
            self.assertEqual(request.get_header("Pragma"), "no-cache")

    def test_api_fallback_uses_no_cache_request(self) -> None:
        commit = "c" * 40
        requests: list[Request] = []
        payloads = iter(
            [
                json.dumps({"object": {"sha": commit}}).encode(),
                b'---\nmetadata:\n  skill_version: "5.1.1"\n---\n',
            ]
        )

        def opener(request: Request, *, timeout: float):
            self.assertEqual(timeout, 3.0)
            requests.append(request)
            return FakeResponse(next(payloads))

        def unavailable_git(_command: list[str], **_kwargs):
            raise FileNotFoundError("git unavailable")

        upstream = checker.fetch_upstream(
            repository="CloudCCAI/cloudcc-aidev-guidelines-common",
            branch="main",
            skill_path="skill/SKILL.md",
            timeout=3.0,
            opener=opener,
            git_runner=unavailable_git,
            nonce_factory=iter(["nonce-ref", "nonce-raw"]).__next__,
        )

        self.assertEqual(upstream["commit_source"], "github_api_no_cache")
        self.assertIn("/git/ref/heads/main?cache_bust=nonce-ref", requests[0].full_url)
        self.assertIn(f"/{commit}/skill/SKILL.md?cache_bust=nonce-raw", requests[1].full_url)

    def test_check_reports_update_available(self) -> None:
        commit = "b" * 40

        def opener(_request: Request, *, timeout: float):
            self.assertEqual(timeout, 2.0)
            return FakeResponse(b'---\nmetadata:\n  skill_version: "5.1.1"\n---\n')

        def git_runner(_command: list[str], **_kwargs):
            return SimpleNamespace(returncode=0, stdout=f"{commit}\trefs/heads/main\n", stderr="")

        with tempfile.TemporaryDirectory() as temporary:
            local_skill = Path(temporary) / "SKILL.md"
            local_skill.write_text(
                '---\nmetadata:\n  skill_version: "5.1.0"\n---\n',
                encoding="utf-8",
            )
            result = checker.check_version(
                local_skill,
                repository="CloudCCAI/cloudcc-aidev-guidelines-common",
                branch="main",
                skill_path="skill/SKILL.md",
                timeout=2.0,
                opener=opener,
                git_runner=git_runner,
                nonce_factory=lambda: "one",
            )

        self.assertTrue(result["update_available"])
        self.assertEqual(result["relation"], "update_available")
        self.assertEqual(result["strategy"], "git_ls_remote_or_no_cache_api_then_commit_pinned_raw")

    def test_invalid_ref_sha_fails_closed_before_raw_fetch(self) -> None:
        calls = 0

        def opener(_request: Request, *, timeout: float):
            nonlocal calls
            calls += 1
            self.assertEqual(timeout, 1.0)
            return FakeResponse(b'{"object":{"sha":"stale-or-invalid"}}')

        def unavailable_git(_command: list[str], **_kwargs):
            raise FileNotFoundError("git unavailable")

        with self.assertRaisesRegex(ValueError, "valid 40-character commit SHA"):
            checker.fetch_upstream(
                repository="CloudCCAI/cloudcc-aidev-guidelines-common",
                branch="main",
                skill_path="skill/SKILL.md",
                timeout=1.0,
                opener=opener,
                git_runner=unavailable_git,
                nonce_factory=lambda: "nonce",
            )
        self.assertEqual(calls, 1)

    def test_version_parser_requires_single_digit_semver(self) -> None:
        self.assertEqual(
            checker.parse_skill_version('metadata:\n  skill_version: "5.1.1"\n'),
            "5.1.1",
        )
        with self.assertRaises(ValueError):
            checker.parse_skill_version('metadata:\n  skill_version: "5.10.0"\n')


if __name__ == "__main__":
    unittest.main()
