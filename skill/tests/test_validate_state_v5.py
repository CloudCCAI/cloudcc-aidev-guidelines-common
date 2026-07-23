from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate-state.py"
PREFLIGHT = SKILL_ROOT / "scripts" / "project-preflight.py"
CHECK_ASSIGNMENT = SKILL_ROOT / "scripts" / "check-assignment.py"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from lib.project_docs_html import project_root_for_document, write_companion  # noqa: E402

SKILL_REPO_URL = "https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common/tree/main/skill"
TIMESTAMP = "2026-07-18T03:00:00Z"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    project_root = project_root_for_document(path) if path.suffix == ".md" else None
    if project_root is not None:
        write_companion(path, project_root=project_root, generated_at=TIMESTAMP)


def add_guidance(project_root: Path) -> None:
    block = f"""
    <!-- cc-aidev-guidelines-common:begin -->
    This project uses cc-aidev-guidelines-common.
    Install from {SKILL_REPO_URL}.
    <!-- cc-aidev-guidelines-common:end -->
    """
    write(project_root / "README.md", block)
    write(project_root / "AGENTS.md", block)


def v5_catalog(path: Path) -> None:
    catalog = {
        "schema_version": 1,
        "artifacts": [
            {
                "id": "manifest",
                "kind": "manifest",
                "path": ".claw/manifest.yaml",
                "module": "control",
                "category": "core",
                "required_when": "always",
                "initialization_required": False,
            },
            {
                "id": "current-status",
                "kind": "current-status",
                "path": ".claw/current-status.md",
                "module": "project_state",
                "category": "core",
                "required_when": "project_state",
                "initialization_required": True,
                "required_fields": ["active_task_count", "active_tasks"],
            },
            {
                "id": "project-baseline",
                "kind": "project-baseline",
                "path": "docs/specs/PROJECT-BASELINE.md",
                "module": "project_state",
                "category": "core",
                "required_when": {"project_mode": "brownfield"},
                "initialization_required": True,
            },
            {
                "id": "task-board",
                "kind": "task-board",
                "path": ".claw/task-board.md",
                "module": "project_state",
                "category": "core",
                "required_when": "project_state",
                "initialization_required": True,
            },
            {
                "id": "collaboration-config",
                "kind": "collaboration-config",
                "path": ".claw/collaboration-config.yaml",
                "module": "collaboration_gate",
                "category": "module_config",
                "required_when": "collaboration_gate",
                "initialization_required": True,
            },
            {
                "id": "review-config",
                "kind": "change-review-config",
                "path": ".claw/review-config.yaml",
                "module": "change_review",
                "category": "module_config",
                "required_when": "change_review",
                "initialization_required": True,
            },
            {
                "id": "developer",
                "kind": "developer",
                "path_pattern": ".claw/developers/*.yaml",
                "module": "collaboration_gate",
                "category": "event",
                "required_when": "event",
                "initialization_required": False,
            },
            {
                "id": "task-status",
                "kind": "task-status",
                "path_pattern": ".claw/tasks/TASK-*.md",
                "module": "project_state",
                "category": "event",
                "required_when": "event",
            },
            {
                "id": "feature-spec",
                "kind": "feature-spec",
                "path_pattern": "docs/specs/FEAT-*.md",
                "module": "project_state",
                "category": "event",
                "required_when": "event",
            },
            {
                "id": "issue-list",
                "kind": "issue-list",
                "path": ".claw/issue-list.md",
                "module": "project_state",
                "category": "event",
                "required_when": "event",
            },
        ],
    }
    for entry in catalog["artifacts"]:
        entry["schema_version"] = 5
    path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")


def manifest_text(
    *,
    legacy: bool = False,
    project_state: bool = True,
    project_mode: str | None = None,
    initialization_status: str = "ready",
    skill_version: str = "5.0.0",
    language: str | None = None,
    policy_version: int = 2,
) -> str:
    legacy_path = ".claw/legacy-document-index.yaml" if legacy else "none"
    effective_mode = project_mode or ("greenfield" if project_state else "not_applicable")
    completed_at = TIMESTAMP if initialization_status == "ready" else "none"
    confirmed_by = "tester" if initialization_status == "ready" else "none"
    language_line = f"language: {language}" if language is not None else ""
    return f"""
    schema_version: 5
    skill_version: {skill_version}
    {language_line}
    project_mode: {effective_mode}
    initialization:
      status: {initialization_status}
      started_at: {TIMESTAMP}
      completed_at: {completed_at}
      confirmed_by: {confirmed_by}
    modules:
      project_state: {str(project_state).lower()}
      collaboration_gate: false
      change_review: false
    module_config:
      collaboration_gate: none
      change_review: none
    compatibility:
      legacy_documents_allowed: {str(legacy).lower()}
      legacy_index_path: {legacy_path}
      new_document_policy_version: {policy_version}
      policy_effective_at: {TIMESTAMP}
    """


def current_status_text(active_tasks: list[str], *, count: int | None = None, truncated: bool = False) -> str:
    task_count = len(active_tasks) if count is None else count
    tasks_yaml = "[]" if not active_tasks else "[" + ", ".join(active_tasks) + "]"
    return f"""
    ---
    kind: current-status
    schema_version: 5
    init_status: complete
    init_completed_at: {TIMESTAMP}
    init_confirmed_by: tester
    updated_at: {TIMESTAMP}
    updated_by: tester
    active_task_count: {task_count}
    active_tasks: {tasks_yaml}
    active_tasks_shown: {len(active_tasks)}
    active_tasks_truncated: {str(truncated).lower()}
    ---

    # Current Status

    No active work.
    """


def task_board_text() -> str:
    return f"""
    ---
    kind: task-board
    schema_version: 5
    init_status: complete
    init_completed_at: {TIMESTAMP}
    init_confirmed_by: tester
    updated_at: {TIMESTAMP}
    updated_by: tester
    ---

    # Task Board

    ## Active Tasks

    - None.
    """


def module_config_text(kind: str) -> str:
    lines = [
        f"kind: {kind}",
        "schema_version: 5",
        "init_status: complete",
        f"init_completed_at: {TIMESTAMP}",
        "init_confirmed_by: tester",
        f"updated_at: {TIMESTAMP}",
        "updated_by: tester",
    ]
    if kind in {"collaboration-config", "collaboration-gate-config"}:
        lines.extend(
            [
                "enabled: true",
                "identity_binding: ssh_public_key_and_git_platform_account",
                "commit_signing: ssh",
                "local_login_required: true",
                "assignment_required: true",
                "manager_required: true",
            ]
        )
    elif kind == "change-review-config":
        lines.extend(
            [
                "platform: codeup",
                "target_branch: main",
                "creation_policy: manual",
                "token_storage: local_only",
            ]
        )
    return "\n".join(lines) + "\n"


def developer_text(*, document_slug: str | None) -> str:
    slug_field = "" if document_slug is None else f"document_slug: {document_slug}"
    return f"""
    kind: developer
    schema_version: 5
    developer_id: DEV-alice
    display_name: Alice
    slug: alice
    {slug_field}
    role: frontend-agent
    public_key: "ssh-ed25519 AAAAB3NzaC1yc2EAAAADAQABAAACAQC tester"
    git_platform: github
    git_username: alice-dev
    ssh_signing_key_fingerprint: "SHA256:abc123"
    status: active
    managed_by: MANAGER-001
    """


def v5_task_text(task_id: str, *, feature_id: str = "none", status: str = "in_progress") -> str:
    return f"""
    ---
    kind: task-status
    schema_version: 5
    task_id: {task_id}
    task_type: feature
    feature_id: {feature_id}
    policy_version: 2
    created_at: {TIMESTAMP}
    created_by: Alice
    created_by_slug: alice
    created_by_source: user_confirmed
    created_by_developer_id: none
    owner_slug: alice
    assignee: alice
    owner_role: shared
    status: {status}
    stage: implementation
    branch: main
    assignment_path: none
    next_action: continue
    updated_at: {TIMESTAMP}
    updated_by: Alice
    ---

    # {task_id} - Test task
    """


def v5_feature_text(feature_id: str, task_id: str) -> str:
    return f"""
    ---
    kind: feature-spec
    schema_version: 5
    feature_id: {feature_id}
    work_type: new_feature
    title: Test feature
    status: approved
    init_status: complete
    init_completed_at: {TIMESTAMP}
    init_confirmed_by: tester
    owner_role: shared
    owner_slug: alice
    created_at: {TIMESTAMP}
    created_by: Alice
    created_by_slug: alice
    created_by_source: user_confirmed
    created_by_developer_id: none
    contributors: [Alice]
    task_ids: [{task_id}]
    related_decisions: none
    related_issues: none
    policy_version: 2
    updated_at: {TIMESTAMP}
    updated_by: Alice
    ---

    # {feature_id} - Test feature
    """


def legacy_task_text(task_id: str = "TASK-001") -> str:
    return f"""
    ---
    kind: task-status
    task_id: {task_id}
    assignee: unassigned
    owner_role: shared
    status: review
    updated_at: {TIMESTAMP}
    updated_by: tester
    ---

    # {task_id} - Legacy task
    """


class ValidateStateV5Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name) / "project"
        self.state_dir = self.project_root / ".claw"
        self.state_dir.mkdir(parents=True)
        add_guidance(self.project_root)
        self.catalog_path = Path(self.temp_dir.name) / "state-catalog.json"
        v5_catalog(self.catalog_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_validator(self, *extra: str) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(VALIDATOR),
            str(self.state_dir),
            "--catalog",
            str(self.catalog_path),
            *extra,
        ]
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def add_minimal_v5(self, active_tasks: list[str] | None = None, *, count: int | None = None) -> None:
        write(self.state_dir / "manifest.yaml", manifest_text())
        write(self.state_dir / "current-status.md", current_status_text(active_tasks or [], count=count))
        write(self.state_dir / "task-board.md", task_board_text())

    def test_manifest_v5_with_catalog_passes(self) -> None:
        self.add_minimal_v5()
        result = self.run_validator("--strict-v5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("(v5)", result.stdout)

    def test_v501_manifest_keeps_historical_language_compatibility(self) -> None:
        self.add_minimal_v5()
        write(
            self.state_dir / "manifest.yaml",
            manifest_text(skill_version="5.0.1", policy_version=3),
        )
        missing = self.run_validator("--strict-v5")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("missing manifest field `language`", missing.stdout)

        for language in ("en", "zh-CN"):
            with self.subTest(language=language):
                write(
                    self.state_dir / "manifest.yaml",
                    manifest_text(skill_version="5.0.1", language=language, policy_version=3),
                )
                confirmed = self.run_validator("--strict-v5")
                self.assertEqual(confirmed.returncode, 0, confirmed.stdout + confirmed.stderr)

        write(
            self.state_dir / "manifest.yaml",
            manifest_text(
                skill_version="5.0.1",
                language="pending",
                policy_version=3,
                initialization_status="in_progress",
            ),
        )
        pending = self.run_validator("--strict-v5")
        self.assertEqual(pending.returncode, 0, pending.stdout + pending.stderr)

        write(
            self.state_dir / "manifest.yaml",
            manifest_text(skill_version="5.0.1", language="pending", policy_version=3),
        )
        ready_pending = self.run_validator("--strict-v5")
        self.assertNotEqual(ready_pending.returncode, 0)
        self.assertIn("ready initialization cannot keep language pending", ready_pending.stdout)

        write(
            self.state_dir / "manifest.yaml",
            manifest_text(skill_version="5.0.1", language="zh-CN", policy_version=2),
        )
        old_policy = self.run_validator("--strict-v5")
        self.assertNotEqual(old_policy.returncode, 0)
        self.assertIn("requires compatibility.new_document_policy_version >= 3", old_policy.stdout)

    def test_v503_manifest_requires_zh_cn_language(self) -> None:
        self.add_minimal_v5()

        for language in (None, "en", "pending"):
            with self.subTest(language=language):
                write(
                    self.state_dir / "manifest.yaml",
                    manifest_text(skill_version="5.0.3", language=language, policy_version=3),
                )
                invalid = self.run_validator("--strict-v5")
                self.assertNotEqual(invalid.returncode, 0)
                self.assertIn(
                    "skill_version 5.0.3 or newer requires language `zh-CN`",
                    invalid.stdout,
                )
                if language is None:
                    self.assertIn("missing manifest field `language`", invalid.stdout)

        write(
            self.state_dir / "manifest.yaml",
            manifest_text(skill_version="5.0.3", language="zh-CN", policy_version=3),
        )
        valid = self.run_validator("--strict-v5")
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

    def test_preflight_routes_v503_english_manifest_to_review(self) -> None:
        self.add_minimal_v5()
        write(
            self.state_dir / "manifest.yaml",
            manifest_text(skill_version="5.0.3", language="en", policy_version=3),
        )

        result = subprocess.run(
            [sys.executable, str(PREFLIGHT), str(self.project_root), "--json"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "needs_review")
        self.assertFalse(payload["ready"])
        self.assertEqual(payload["language"], "en")
        self.assertIn("language: zh-CN", payload["finding"])
        self.assertEqual(payload["next_action"], "repair manifest language to zh-CN")

    def test_strict_v5_allows_prefinalize_manifest_when_core_is_complete(self) -> None:
        write(
            self.state_dir / "manifest.yaml",
            manifest_text(initialization_status="in_progress"),
        )
        write(self.state_dir / "current-status.md", current_status_text([]))
        write(self.state_dir / "task-board.md", task_board_text())
        result = self.run_validator("--strict-v5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        incomplete = current_status_text([]).replace("init_status: complete", "init_status: in_progress")
        write(self.state_dir / "current-status.md", incomplete)
        result = self.run_validator("--strict-v5")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires init_status=complete", result.stdout)

    def test_in_progress_manifest_accepts_null_unset_values(self) -> None:
        manifest = manifest_text(initialization_status="in_progress")
        manifest = manifest.replace("completed_at: none", "completed_at: null")
        manifest = manifest.replace("confirmed_by: none", "confirmed_by: null")
        manifest = manifest.replace("collaboration_gate: none", "collaboration_gate: null")
        manifest = manifest.replace("change_review: none", "change_review: null")
        write(self.state_dir / "manifest.yaml", manifest)
        write(self.state_dir / "current-status.md", current_status_text([]))
        write(self.state_dir / "task-board.md", task_board_text())
        result = self.run_validator("--strict-v5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_project_state_off_requires_not_applicable_mode(self) -> None:
        write(self.state_dir / "manifest.yaml", manifest_text(project_state=False))
        result = self.run_validator("--strict-v5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        write(
            self.state_dir / "manifest.yaml",
            manifest_text(project_state=False, project_mode="greenfield"),
        )
        result = self.run_validator("--strict-v5")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires project_mode not_applicable", result.stdout)

    def test_ready_manifest_rejects_pending_project_mode(self) -> None:
        self.add_minimal_v5()
        write(
            self.state_dir / "manifest.yaml",
            manifest_text(project_mode="pending", initialization_status="ready"),
        )
        result = self.run_validator("--strict-v5")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ready initialization cannot keep project_mode pending", result.stdout)

    def test_disabled_modules_do_not_load_retained_state(self) -> None:
        write(self.state_dir / "manifest.yaml", manifest_text(project_state=False))
        write(self.state_dir / "current-status.md", "not front matter\n")
        write(self.state_dir / "task-board.md", "not front matter\n")
        write(self.state_dir / "tasks" / "TASK-alice-001-invalid.md", "not front matter\n")
        write(
            self.project_root / "docs" / "specs" / "FEAT-alice-001-invalid.md",
            "not front matter\n",
        )
        write(self.state_dir / "collaboration-config.yaml", "not: valid-for-this-kind\n")
        write(self.state_dir / "review-config.yaml", "not: valid-for-this-kind\n")
        write(self.state_dir / "developers" / "retained.yaml", "not: a-developer\n")
        write(self.state_dir / "assignments" / "retained.yaml", "not: an-assignment\n")

        result = self.run_validator("--strict-v5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_enabled_module_config_uses_catalog_kind_and_completion_metadata(self) -> None:
        manifest = manifest_text()
        manifest = manifest.replace("collaboration_gate: false", "collaboration_gate: true")
        manifest = manifest.replace(
            "collaboration_gate: none",
            "collaboration_gate: .claw/collaboration-config.yaml",
        )
        write(self.state_dir / "manifest.yaml", manifest)
        write(self.state_dir / "current-status.md", current_status_text([]))
        write(self.state_dir / "task-board.md", task_board_text())
        write(
            self.state_dir / "collaboration-config.yaml",
            module_config_text("collaboration-config"),
        )

        valid = self.run_validator("--strict-v5")
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

        write(
            self.state_dir / "collaboration-config.yaml",
            module_config_text("collaboration-gate-config"),
        )
        wrong_kind = self.run_validator("--strict-v5")
        self.assertNotEqual(wrong_kind.returncode, 0)
        self.assertIn("expected kind `collaboration-config`", wrong_kind.stdout)

    def test_change_review_pending_config_cannot_finalize(self) -> None:
        manifest = manifest_text(project_state=False)
        manifest = manifest.replace("change_review: false", "change_review: true")
        manifest = manifest.replace(
            "change_review: none",
            "change_review: .claw/review-config.yaml",
        )
        write(self.state_dir / "manifest.yaml", manifest)
        pending = module_config_text("change-review-config").replace(
            "platform: codeup\ntarget_branch: main",
            "platform: pending\ntarget_branch: pending",
        )
        write(self.state_dir / "review-config.yaml", pending)

        invalid = self.run_validator("--strict-v5")
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("requires platform=codeup or github", invalid.stdout)
        self.assertIn("requires a non-pending target_branch", invalid.stdout)

        write(
            self.state_dir / "review-config.yaml",
            module_config_text("change-review-config"),
        )
        valid = self.run_validator("--strict-v5")
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

    def test_v5_developer_requires_document_slug_but_legacy_does_not(self) -> None:
        manifest = manifest_text()
        manifest = manifest.replace("collaboration_gate: false", "collaboration_gate: true")
        manifest = manifest.replace(
            "collaboration_gate: none",
            "collaboration_gate: .claw/collaboration-config.yaml",
        )
        write(self.state_dir / "manifest.yaml", manifest)
        write(self.state_dir / "current-status.md", current_status_text([]))
        write(self.state_dir / "task-board.md", task_board_text())
        write(
            self.state_dir / "collaboration-config.yaml",
            module_config_text("collaboration-config"),
        )
        developer_path = self.state_dir / "developers" / "alice.yaml"
        write(developer_path, developer_text(document_slug=None))

        missing = self.run_validator("--strict-v5")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("missing v5 developer field `document_slug`", missing.stdout)

        write(developer_path, developer_text(document_slug="Alice Smith"))
        invalid = self.run_validator("--strict-v5")
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("expected lowercase slug", invalid.stdout)

        write(developer_path, developer_text(document_slug="alice-smith"))
        valid = self.run_validator("--strict-v5")
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

    def test_registered_legacy_developer_does_not_require_document_slug(self) -> None:
        manifest = manifest_text(legacy=True)
        manifest = manifest.replace("collaboration_gate: false", "collaboration_gate: true")
        manifest = manifest.replace(
            "collaboration_gate: none",
            "collaboration_gate: .claw/collaboration-config.yaml",
        )
        write(self.state_dir / "manifest.yaml", manifest)
        write(self.state_dir / "current-status.md", current_status_text([]))
        write(self.state_dir / "task-board.md", task_board_text())
        write(
            self.state_dir / "collaboration-config.yaml",
            module_config_text("collaboration-config"),
        )
        developer_path = self.state_dir / "developers" / "alice.yaml"
        legacy_developer = developer_text(document_slug=None)
        legacy_developer = legacy_developer.replace("kind: developer\n", "")
        legacy_developer = legacy_developer.replace("schema_version: 5\n", "")
        write(developer_path, legacy_developer)
        write(
            self.state_dir / "legacy-document-index.yaml",
            f"""
            kind: legacy-document-index
            schema_version: 1
            captured_at: {TIMESTAMP}
            policy_effective_at: {TIMESTAMP}
            documents:
              - {{path: .claw/developers/alice.yaml, kind: developer, id: DEV-alice, schema_version: 4}}
            """,
        )

        result = self.run_validator("--strict-v5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_baseline_is_required_only_for_brownfield(self) -> None:
        self.add_minimal_v5()
        greenfield = self.run_validator("--strict-v5")
        self.assertEqual(greenfield.returncode, 0, greenfield.stdout + greenfield.stderr)

        write(
            self.state_dir / "manifest.yaml",
            manifest_text(project_mode="brownfield"),
        )
        brownfield_missing = self.run_validator("--strict-v5")
        self.assertNotEqual(brownfield_missing.returncode, 0)
        self.assertIn("missing required file", brownfield_missing.stdout)

        write(
            self.project_root / "docs" / "specs" / "PROJECT-BASELINE.md",
            f"""
            ---
            kind: project-baseline
            schema_version: 5
            title: Test baseline
            status: active_reference
            init_status: complete
            init_completed_at: {TIMESTAMP}
            init_confirmed_by: tester
            updated_at: {TIMESTAMP}
            updated_by: tester
            ---
            # Project Baseline
            """,
        )
        brownfield_present = self.run_validator("--strict-v5")
        self.assertEqual(
            brownfield_present.returncode,
            0,
            brownfield_present.stdout + brownfield_present.stderr,
        )

    def test_completed_core_file_cannot_keep_onboarding_sentinel(self) -> None:
        write(self.state_dir / "manifest.yaml", manifest_text(project_mode="brownfield"))
        write(self.state_dir / "current-status.md", current_status_text([]))
        write(self.state_dir / "task-board.md", task_board_text())
        write(
            self.project_root / "docs" / "specs" / "PROJECT-BASELINE.md",
            f"""
            ---
            kind: project-baseline
            schema_version: 5
            init_status: complete
            init_completed_at: {TIMESTAMP}
            init_confirmed_by: tester
            updated_at: {TIMESTAMP}
            updated_by: tester
            ---

            # Project Baseline

            <!-- cc-aidev:onboarding-incomplete -->

            ## Pending Verification

            - A real, bounded unknown remains valid here.
            """,
        )
        result = self.run_validator("--strict-v5")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "init_status=complete but onboarding sentinel remains",
            result.stdout,
        )

        baseline = self.project_root / "docs" / "specs" / "PROJECT-BASELINE.md"
        write(
            baseline,
            baseline.read_text(encoding="utf-8").replace(
                "<!-- cc-aidev:onboarding-incomplete -->\n",
                "",
            ),
        )
        valid = self.run_validator("--strict-v5")
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

    def test_multi_active_tasks_accepts_new_id(self) -> None:
        task_id = "TASK-alice-001"
        self.add_minimal_v5([task_id])
        write(self.state_dir / "tasks" / f"{task_id}-implementation.md", v5_task_text(task_id))
        result = self.run_validator("--strict-v5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_v5_zero_sequence_is_invalid_but_legacy_zero_can_be_grandfathered(self) -> None:
        invalid_id = "TASK-alice-000"
        self.add_minimal_v5([invalid_id])
        write(self.state_dir / "tasks" / f"{invalid_id}.md", v5_task_text(invalid_id))
        invalid = self.run_validator("--strict-v5")
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn(f"invalid active task id `{invalid_id}`", invalid.stdout)
        (self.state_dir / "tasks" / f"{invalid_id}.md").unlink()

        write(self.state_dir / "manifest.yaml", manifest_text(legacy=True))
        write(self.state_dir / "current-status.md", current_status_text(["TASK-0"]))
        write(self.state_dir / "tasks" / "TASK-0.md", legacy_task_text("TASK-0"))
        write(
            self.state_dir / "legacy-document-index.yaml",
            f"""
            kind: legacy-document-index
            schema_version: 1
            captured_at: {TIMESTAMP}
            policy_effective_at: {TIMESTAMP}
            documents:
              - {{path: .claw/tasks/TASK-0.md, kind: task-status, id: TASK-0, schema_version: 4}}
            """,
        )
        legacy = self.run_validator("--strict-v5")
        self.assertEqual(legacy.returncode, 0, legacy.stdout + legacy.stderr)

    def test_new_feature_and_task_cross_references_pass(self) -> None:
        feature_id = "FEAT-alice-001"
        task_id = "TASK-alice-001"
        self.add_minimal_v5([task_id])
        write(
            self.project_root / "docs" / "specs" / f"{feature_id}-test-feature.md",
            v5_feature_text(feature_id, task_id),
        )
        write(
            self.state_dir / "tasks" / f"{task_id}-implementation.md",
            v5_task_text(task_id, feature_id=feature_id),
        )
        result = self.run_validator("--strict-v5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_task_cannot_reference_an_unconfirmed_v5_feature(self) -> None:
        feature_id = "FEAT-alice-001"
        task_id = "TASK-alice-001"
        self.add_minimal_v5([task_id])
        feature = v5_feature_text(feature_id, task_id)
        feature = feature.replace("status: approved", "status: draft", 1)
        feature = feature.replace("init_status: complete", "init_status: awaiting_confirmation", 1)
        write(
            self.project_root / "docs" / "specs" / f"{feature_id}-test-feature.md",
            feature,
        )
        write(
            self.state_dir / "tasks" / f"{task_id}-implementation.md",
            v5_task_text(task_id, feature_id=feature_id),
        )
        result = self.run_validator("--strict-v5")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("is not user-confirmed", result.stdout)

    def test_truncated_multi_active_tasks_uses_total_count(self) -> None:
        task_id = "TASK-alice-001"
        write(self.state_dir / "manifest.yaml", manifest_text())
        write(self.state_dir / "current-status.md", current_status_text([task_id], count=3, truncated=True))
        write(self.state_dir / "task-board.md", task_board_text())
        write(self.state_dir / "tasks" / f"{task_id}-implementation.md", v5_task_text(task_id))
        result = self.run_validator("--strict-v5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_active_task_count_mismatch_fails(self) -> None:
        self.add_minimal_v5([], count=1)
        result = self.run_validator("--strict-v5")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match active_tasks length", result.stdout)

    def test_existing_event_artifact_must_declare_catalog_schema_version(self) -> None:
        self.add_minimal_v5()
        write(
            self.state_dir / "issue-list.md",
            f"""
            ---
            kind: issue-list
            updated_at: {TIMESTAMP}
            updated_by: tester
            ---

            # Issue List
            """,
        )
        missing_schema = self.run_validator("--strict-v5")
        self.assertNotEqual(missing_schema.returncode, 0)
        self.assertIn("schema_version must be `5` from the state catalog", missing_schema.stdout)

        content = (self.state_dir / "issue-list.md").read_text(encoding="utf-8")
        write(
            self.state_dir / "issue-list.md",
            content.replace("kind: issue-list", "kind: issue-list\nschema_version: 5"),
        )
        valid = self.run_validator("--strict-v5")
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

    def test_registered_legacy_task_is_allowed(self) -> None:
        write(self.state_dir / "manifest.yaml", manifest_text(legacy=True))
        write(self.state_dir / "current-status.md", current_status_text(["TASK-001"]))
        write(self.state_dir / "task-board.md", task_board_text())
        write(self.state_dir / "tasks" / "TASK-001.md", legacy_task_text())
        write(
            self.state_dir / "legacy-document-index.yaml",
            f"""
            kind: legacy-document-index
            schema_version: 1
            captured_at: {TIMESTAMP}
            policy_effective_at: {TIMESTAMP}
            documents:
              - path: .claw/tasks/TASK-001.md
                kind: task-status
                id: TASK-001
                schema_version: 4
            """,
        )
        result = self.run_validator("--strict-v5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_registered_v4_current_status_is_allowed_during_strict_adoption(self) -> None:
        write(self.state_dir / "manifest.yaml", manifest_text(legacy=True))
        write(
            self.state_dir / "current-status.md",
            f"""
            ---
            kind: current-status
            version: 4
            updated_at: {TIMESTAMP}
            updated_by: tester
            phase: implementation
            active_task: none
            next_action: continue
            read_next:
              task_board: .claw/task-board.md
            ---

            # Current Status

            No active work.
            """,
        )
        write(self.state_dir / "task-board.md", task_board_text())
        write(
            self.state_dir / "legacy-document-index.yaml",
            f"""
            kind: legacy-document-index
            schema_version: 1
            captured_at: {TIMESTAMP}
            policy_effective_at: {TIMESTAMP}
            documents:
              - {{path: .claw/current-status.md, kind: current-status, id: current-status, schema_version: 4}}
            """,
        )
        result = self.run_validator("--strict-v5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unregistered_legacy_task_fails(self) -> None:
        self.add_minimal_v5(["TASK-001"])
        write(self.state_dir / "tasks" / "TASK-001.md", legacy_task_text())
        result = self.run_validator("--strict-v5")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not registered in legacy-document-index", result.stdout)

    def test_json_output_is_structured(self) -> None:
        self.add_minimal_v5([], count=1)
        result = self.run_validator("--json", "--strict-v5")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(payload["mode"], "v5")
        self.assertGreater(payload["summary"]["error_count"], 0)

    def test_strict_v5_rejects_legacy_project(self) -> None:
        result = self.run_validator("--strict-v5")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires", result.stdout)

    def test_schema_files_are_valid_json(self) -> None:
        for filename in ("manifest.schema.json", "legacy-index.schema.json"):
            payload = json.loads((SKILL_ROOT / "schemas" / filename).read_text(encoding="utf-8"))
            self.assertEqual(payload["type"], "object")


class AssignmentTaskIdTests(unittest.TestCase):
    def test_assignment_gate_accepts_legacy_and_nonzero_v5_id_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_dir = Path(temp_dir) / ".claw"
            state_dir.mkdir()

            for task_id in ("TASK-0", "TASK-alice-001", "TASK-alice-999"):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(CHECK_ASSIGNMENT),
                        str(state_dir),
                        "--developer",
                        "DEV-alice",
                        "--task",
                        task_id,
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertNotIn("blocked_task_id_invalid", result.stdout, task_id)
                self.assertIn("blocked_identity_unknown", result.stdout, task_id)

            invalid = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_ASSIGNMENT),
                    str(state_dir),
                    "--developer",
                    "DEV-alice",
                    "--task",
                    "TASK-alice-000",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("blocked_task_id_invalid", invalid.stdout)


class ValidateStateV4FallbackTests(unittest.TestCase):
    def test_v4_without_manifest_still_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "project"
            state_dir = project_root / ".claw"
            state_dir.mkdir(parents=True)
            add_guidance(project_root)
            common = f"""
            ---
            kind: {{kind}}
            version: 4
            updated_at: {TIMESTAMP}
            updated_by: tester
            ---
            # {{title}}
            """
            write(
                state_dir / "current-status.md",
                f"""
                ---
                kind: current-status
                version: 4
                updated_at: {TIMESTAMP}
                updated_by: tester
                phase: idle
                active_task: none
                next_action: wait
                read_next:
                  task_board: true
                ---
                # Current Status
                """,
            )
            write(state_dir / "goals.md", common.format(kind="goals", title="Goals"))
            write(state_dir / "decisions.md", common.format(kind="decisions", title="Decisions"))
            write(state_dir / "issue-list.md", common.format(kind="issue-list", title="Issues"))
            write(state_dir / "task-board.md", common.format(kind="task-board", title="Task Board"))
            write(state_dir / "task-archive.md", common.format(kind="task-archive", title="Archive"))
            write(
                state_dir / "test-report.md",
                f"""
                ---
                kind: test-report
                version: 4
                updated_at: {TIMESTAMP}
                updated_by: tester
                last_run_status: not_run
                ---
                # Test Report
                - 状态：`not_run`
                """,
            )
            write(state_dir / "devops.md", common.format(kind="devops", title="DevOps"))
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), str(state_dir)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("(v4)", result.stdout)


if __name__ == "__main__":
    unittest.main()
