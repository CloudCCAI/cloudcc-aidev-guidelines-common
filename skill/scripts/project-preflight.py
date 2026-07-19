#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from lib.language import PENDING_LANGUAGE, PRIMARY_LANGUAGE, manifest_language


EXIT_OK = 0
EXIT_REPAIR_REQUIRED = 4

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
CATALOG_PATH = SKILL_ROOT / "state-catalog.json"
STATE_DIR_NAME = ".claw"

IGNORED_DIRS = {
    ".git",
    ".claw",
    ".claw-local",
    ".idea",
    ".pytest_cache",
    ".venv",
    ".vscode",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
SOURCE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".kts",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}
BUILD_MANIFESTS = {
    "Cargo.toml",
    "Gemfile",
    "Makefile",
    "Package.swift",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
    "go.mod",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
    "settings.gradle",
}
DEPLOYMENT_NAMES = {
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "fly.toml",
    "helmfile.yaml",
    "serverless.yml",
}
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)


class ManifestError(ValueError):
    pass


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith('"') and value.endswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    return value


def load_simple_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ManifestError(f"missing file: {path}")

    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            raise ManifestError(f"{path}:{line_number}: tab indentation is not supported")
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if ":" not in stripped:
            raise ManifestError(f"{path}:{line_number}: expected key/value mapping")
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]+", key):
            raise ManifestError(f"{path}:{line_number}: unsupported key `{key}`")

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ManifestError(f"{path}:{line_number}: invalid indentation")
        parent = stack[-1][1]
        if raw_value.strip() == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = parse_scalar(raw_value)
    return root


def read_front_matter_status(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "needs_review"
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return "needs_review"
    for raw_line in match.group(1).splitlines():
        key, separator, raw_value = raw_line.partition(":")
        if separator and key.strip() == "init_status":
            return str(parse_scalar(raw_value))
    return "needs_review"


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def version_tuple(value: object) -> tuple[int, int, int]:
    cleaned = str(value).strip().strip('"\'')
    if not re.fullmatch(r"[0-9]\.[0-9]\.[0-9]", cleaned):
        return (0, 0, 0)
    return tuple(int(part) for part in cleaned.split("."))  # type: ignore[return-value]


def git_commit_count(project_root: Path) -> int | None:
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "--max-count=3", "HEAD"],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


def collect_mode_evidence(project_root: Path) -> dict[str, Any]:
    source_files = 0
    build_manifests: list[str] = []
    deployment_files: list[str] = []
    test_files = 0
    migration_files = 0
    scanned_files = 0
    scan_truncated = False

    for current_root, dir_names, file_names in os.walk(project_root, followlinks=False):
        current_path = Path(current_root)
        dir_names[:] = sorted(
            name
            for name in dir_names
            if name not in IGNORED_DIRS and not (current_path / name).is_symlink()
        )
        relative_root = current_path.relative_to(project_root)
        if len(relative_root.parts) >= 6:
            dir_names[:] = []

        for name in sorted(file_names):
            scanned_files += 1
            if scanned_files > 2500:
                scan_truncated = True
                dir_names[:] = []
                break
            path = current_path / name
            relative = path.relative_to(project_root).as_posix()
            if path.suffix.lower() in SOURCE_SUFFIXES:
                source_files += 1
            if name in BUILD_MANIFESTS:
                build_manifests.append(relative)
            if name in DEPLOYMENT_NAMES or ".github/workflows/" in relative:
                deployment_files.append(relative)
            lowered_parts = {part.lower() for part in path.parts}
            if "test" in lowered_parts or "tests" in lowered_parts or name.lower().startswith("test_"):
                test_files += 1
            if "migration" in lowered_parts or "migrations" in lowered_parts:
                migration_files += 1
        if scan_truncated:
            break

    commits = git_commit_count(project_root)
    evidence: list[str] = []
    if source_files:
        evidence.append(f"{source_files} source files detected")
    if build_manifests:
        evidence.append(f"build manifests: {', '.join(build_manifests[:5])}")
    if deployment_files:
        evidence.append(f"deployment or CI files: {', '.join(deployment_files[:5])}")
    if test_files:
        evidence.append(f"{test_files} test-related files detected")
    if migration_files:
        evidence.append(f"{migration_files} migration-related files detected")
    if commits is not None:
        evidence.append(f"git history contains at least {commits} commit(s) in the bounded scan")
    if scan_truncated:
        evidence.append("repository inventory was truncated at 2500 files")

    brownfield_signals = 0
    brownfield_signals += 2 if source_files >= 2 else 0
    brownfield_signals += 1 if build_manifests and source_files else 0
    brownfield_signals += 1 if deployment_files else 0
    brownfield_signals += 1 if test_files or migration_files else 0
    brownfield_signals += 1 if commits is not None and commits >= 2 else 0

    if brownfield_signals >= 2:
        candidate = "brownfield"
        confidence = "high" if brownfield_signals >= 4 else "medium"
    else:
        candidate = "greenfield"
        confidence = "medium" if evidence else "high"
    if not evidence:
        evidence.append("no substantive source, build, test, deployment, migration, or Git history evidence detected")

    return {
        "candidate": candidate,
        "confidence": confidence,
        "evidence": evidence,
        "requires_user_confirmation": True,
        "semantic_rule": (
            "Choose brownfield when existing behavior, data, users, APIs, or deployment contracts must be preserved; "
            "otherwise choose greenfield for the selected scope."
        ),
    }


def enabled_file_statuses(project_root: Path, manifest: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    project_mode = manifest.get("project_mode")
    modules = manifest.get("modules") if isinstance(manifest.get("modules"), dict) else {}
    file_index = manifest.get("file_status") if isinstance(manifest.get("file_status"), dict) else {}
    grandfathered = (
        manifest.get("grandfathered_files")
        if isinstance(manifest.get("grandfathered_files"), dict)
        else {}
    )
    results: list[dict[str, Any]] = []

    for descriptor in catalog.get("files", []):
        if descriptor.get("lifecycle") not in {"core", "module_config"}:
            continue
        file_id = descriptor["id"]
        module = descriptor.get("module")
        if module not in {"control_plane", None} and not bool(modules.get(module, False)):
            continue
        modes = descriptor.get("project_modes")
        if modes and project_mode not in modes:
            continue
        relative_path = descriptor.get("path")
        if not relative_path:
            continue
        path = project_root / relative_path
        if file_id in grandfathered and path.is_file():
            actual_status = "complete"
        elif path.suffix in {".yaml", ".yml"}:
            try:
                yaml_data = load_simple_yaml(path)
                actual_status = yaml_data.get("init_status")
            except ManifestError:
                actual_status = "needs_review" if path.exists() else None
        else:
            actual_status = read_front_matter_status(path)
        results.append(
            {
                "id": file_id,
                "path": relative_path,
                "init_status": actual_status or file_index.get(file_id) or "missing",
                "counts_toward_ready": bool(descriptor.get("counts_toward_ready", False)),
            }
        )
    return results


def inspect_project(project_root: Path) -> dict[str, Any]:
    catalog = load_catalog()
    state_dir = project_root / STATE_DIR_NAME
    manifest_path = state_dir / "manifest.yaml"
    mode_evidence = collect_mode_evidence(project_root)

    base: dict[str, Any] = {
        "project_root": str(project_root),
        "state_dir": STATE_DIR_NAME,
        "mode_recommendation": mode_evidence,
    }

    if not state_dir.exists():
        return {
            **base,
            "status": "uninitialized",
            "ready": False,
            "next_action": "confirm module switches; if project_state is enabled, confirm greenfield/brownfield",
        }

    if not state_dir.is_dir():
        return {
            **base,
            "status": "needs_review",
            "ready": False,
            "finding": "`.claw` exists but is not a directory.",
            "next_action": "repair the .claw path conflict",
        }

    if not manifest_path.is_file():
        return {
            **base,
            "status": "legacy",
            "ready": False,
            "operational": True,
            "finding": "`.claw` exists without the new manifest; existing content will not be overwritten.",
            "next_action": "continue with legacy v4 profile; offer explicit v5 adoption only if requested",
        }

    try:
        manifest = load_simple_yaml(manifest_path)
    except ManifestError as exc:
        return {
            **base,
            "status": "needs_review",
            "ready": False,
            "finding": str(exc),
            "next_action": "repair manifest.yaml",
        }

    initialization = manifest.get("initialization")
    if not isinstance(initialization, dict):
        initialization = {}
    initialization_status = initialization.get("status", "needs_review")
    if initialization_status not in set(catalog.get("initialization_statuses", [])):
        initialization_status = "needs_review"
    file_statuses = enabled_file_statuses(project_root, manifest, catalog)
    try:
        language = manifest_language(manifest)
    except ValueError as exc:
        return {
            **base,
            "status": "needs_review",
            "ready": False,
            "finding": str(exc),
            "next_action": "repair manifest language",
        }
    if version_tuple(manifest.get("skill_version")) >= (5, 0, 3) and language != PRIMARY_LANGUAGE:
        return {
            **base,
            "status": "needs_review",
            "ready": False,
            "language": language,
            "finding": "Skill 5.0.3 及后续版本的 manifest 必须使用 `language: zh-CN`。",
            "next_action": "repair manifest language to zh-CN",
        }
    ready = initialization_status == "ready" and language != PENDING_LANGUAGE
    reported_status = (
        "needs_review"
        if initialization_status == "ready" and language == PENDING_LANGUAGE
        else initialization_status
    )
    modules = manifest.get("modules", {})
    if language == PENDING_LANGUAGE:
        next_action = "resume guided onboarding to normalize the legacy language marker to zh-CN"
    elif ready and isinstance(modules, dict) and modules.get("project_state") is True:
        next_action = "load current-status.md"
    elif ready and isinstance(modules, dict) and modules.get("change_review") is True:
        next_action = "load only enabled non-state module configuration; continue without project-state workflow"
    elif ready:
        next_action = "continue with the requested operation; project-state workflow is disabled"
    else:
        next_action = "resume guided onboarding"
    if isinstance(modules, dict) and modules.get("project_state") is False:
        mode_evidence = {
            "candidate": "not_applicable",
            "confidence": "confirmed",
            "evidence": ["project_state is disabled in manifest modules"],
            "requires_user_confirmation": False,
            "semantic_rule": "Greenfield/Brownfield classification is skipped when project_state is disabled.",
        }
    return {
        **base,
        "mode_recommendation": mode_evidence,
        "status": reported_status,
        "ready": ready,
        "language": language,
        "project_mode": manifest.get("project_mode"),
        "modules": modules,
        "file_statuses": file_statuses,
        "next_action": next_action,
    }


def emit(result: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return
    print(f"status: {result['status']}")
    print(f"project_root: {result['project_root']}")
    print(f"state_dir: {result['state_dir']}")
    if result.get("finding"):
        print(f"finding: {result['finding']}")
    print(f"next_action: {result['next_action']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only project initialization preflight for .claw")
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return exit code 4 unless initialization.status is ready",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        result = {
            "status": "needs_review",
            "ready": False,
            "project_root": str(project_root),
            "state_dir": STATE_DIR_NAME,
            "finding": "project root does not exist or is not a directory",
            "next_action": "provide an existing project root",
        }
        emit(result, args.json)
        return EXIT_REPAIR_REQUIRED

    result = inspect_project(project_root)
    emit(result, args.json)
    if args.require_ready and not result.get("ready", False):
        return EXIT_REPAIR_REQUIRED
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
