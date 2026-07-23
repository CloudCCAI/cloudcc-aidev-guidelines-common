#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from lib.atomic_io import atomic_write_text
from lib.devops_assets import (
    DevOpsAssetContract,
    contract_from_catalog,
    normalize_environment_names,
)
from lib.language import (
    PENDING_LANGUAGE,
    PRIMARY_LANGUAGE,
    manifest_language,
)
from lib.project_docs_html import sync_project_documents
from lib.state_io import clean_value, read_mapping_list_yaml


EXIT_OK = 0
EXIT_NEEDS_INPUT = 2
EXIT_REPAIR_REQUIRED = 4
EXIT_CONFLICT = 5
EXIT_INVALID_INPUT = 6
EXIT_IO_ERROR = 7
EXIT_LOCKED = 8

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
CATALOG_PATH = SKILL_ROOT / "state-catalog.json"
STATE_DIR_NAME = ".claw"
MANIFEST_RELATIVE_PATH = Path(STATE_DIR_NAME) / "manifest.yaml"
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
ONBOARDING_INCOMPLETE_SENTINEL = "<!-- cc-aidev:onboarding-incomplete -->"
RECOMMENDED_ENVIRONMENTS = ("DEV", "UAT", "PROD")
DEVOPS_ASSETS_BEGIN = "<!-- cc-aidev:devops-assets:begin -->"
DEVOPS_ASSETS_END = "<!-- cc-aidev:devops-assets:end -->"


def load_preflight_module() -> Any:
    module_path = SCRIPT_DIR / "project-preflight.py"
    spec = importlib.util.spec_from_file_location("cc_project_preflight", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PREFLIGHT = load_preflight_module()


class OnboardingError(RuntimeError):
    def __init__(self, code: str, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code


def utc_now(explicit: str | None = None) -> str:
    if explicit:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", explicit):
            raise OnboardingError("invalid_timestamp", "--now must use YYYY-MM-DDTHH:MM:SSZ", EXIT_INVALID_INPUT)
        return explicit
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def calendar_date(timestamp: str) -> str:
    return timestamp[:10]


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def devops_contract() -> DevOpsAssetContract:
    try:
        return contract_from_catalog(load_catalog())
    except ValueError as exc:
        raise OnboardingError("invalid_catalog", str(exc), EXIT_REPAIR_REQUIRED) from exc


def read_skill_version() -> str:
    skill_path = SKILL_ROOT / "SKILL.md"
    if not skill_path.is_file():
        return "unknown"
    match = re.search(r'^\s*skill_version:\s*["\']?([^"\'\s]+)', skill_path.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else "unknown"


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def dump_simple_yaml(data: dict[str, Any], indent: int = 0) -> str:
    lines: list[str] = []
    prefix = " " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.extend(dump_simple_yaml(value, indent + 2).rstrip("\n").splitlines())
        else:
            lines.append(f"{prefix}{key}: {yaml_scalar(value)}")
    return "\n".join(lines) + "\n"


def atomic_write(path: Path, content: str) -> None:
    atomic_write_text(path, content)


@contextmanager
def onboarding_lock(project_root: Path) -> Iterator[None]:
    lock_path = project_root / ".claw-onboarding.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise OnboardingError(
            "onboarding_locked",
            f"another onboarding operation holds {lock_path}",
            EXIT_LOCKED,
        ) from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode("utf-8"))
        os.close(descriptor)
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def bool_flag(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value == "on"


def render(template_path: Path, values: dict[str, str]) -> str:
    content = template_path.read_text(encoding="utf-8")
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", value)
    unresolved = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", content)))
    if unresolved:
        raise OnboardingError(
            "template_error",
            f"unresolved template values in {template_path}: {', '.join(unresolved)}",
            EXIT_REPAIR_REQUIRED,
        )
    return content


def render_values(
    manifest: dict[str, Any],
    timestamp: str,
    project_root: Path | None = None,
) -> dict[str, str]:
    project_mode = str(manifest.get("project_mode", "pending"))
    modules = manifest.get("modules") if isinstance(manifest.get("modules"), dict) else {}
    return {
        "TIMESTAMP": timestamp,
        "CALENDAR_DATE": calendar_date(timestamp),
        "SKILL_VERSION": read_skill_version(),
        "PROJECT_MODE": project_mode,
        "PROJECT_STATE": str(bool(modules.get("project_state", False))).lower(),
        "COLLABORATION_GATE": str(bool(modules.get("collaboration_gate", False))).lower(),
        "CHANGE_REVIEW": str(bool(modules.get("change_review", False))).lower(),
        "EVIDENCE_STATUS": "planned" if project_mode == "greenfield" else "pending verification",
        "PROJECT_NAME": project_root.name if project_root is not None else "project",
        "UPDATED_BY": "onboarding",
    }


def load_manifest(project_root: Path) -> dict[str, Any]:
    path = project_root / MANIFEST_RELATIVE_PATH
    try:
        return PREFLIGHT.load_simple_yaml(path)
    except Exception as exc:
        raise OnboardingError("invalid_manifest", str(exc), EXIT_REPAIR_REQUIRED) from exc


def write_manifest(project_root: Path, manifest: dict[str, Any]) -> None:
    atomic_write(project_root / MANIFEST_RELATIVE_PATH, dump_simple_yaml(manifest))


def version_at_least(raw_version: object, expected: tuple[int, int, int]) -> bool:
    cleaned = str(raw_version).strip().strip('"\'')
    if not re.fullmatch(r"[0-9]\.[0-9]\.[0-9]", cleaned):
        return False
    return tuple(int(part) for part in cleaned.split(".")) >= expected


def read_top_level_fields(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(content)
    if not match:
        raise OnboardingError(
            "invalid_front_matter",
            f"{path} is missing YAML front matter",
            EXIT_REPAIR_REQUIRED,
        )
    fields: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        fields[key.strip()] = PREFLIGHT.parse_scalar(raw_value)
    return fields


def scalar_items(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        candidates = [str(item).strip() for item in value if str(item).strip()]
    else:
        candidates = [item.strip() for item in str(value).split(",") if item.strip()]
    return [item for item in candidates if item.casefold() not in {"none", "n/a", "null", "pending"}]


def validate_environment_names(names: list[str]) -> list[str]:
    try:
        return normalize_environment_names(names)
    except ValueError as exc:
        code = "duplicate_environment_name" if "unique" in str(exc) else "invalid_environment_name"
        raise OnboardingError(code, str(exc), EXIT_INVALID_INPUT) from exc


def devops_asset_errors(project_root: Path, devops_path: Path) -> list[str]:
    contract = devops_contract()
    if not devops_path.is_file():
        return [f"missing initialization file: {devops_path}"]
    fields = read_top_level_fields(devops_path)
    assets_root = str(fields.get(contract.root_field, "")).strip()
    environments = scalar_items(fields.get(contract.environments_field))
    errors: list[str] = []
    expected_root = contract.root_path.as_posix()
    if assets_root != expected_root:
        errors.append(f"{contract.root_field} must be `{expected_root}`")
    if not environments:
        errors.append(f"{contract.environments_field} must contain at least one confirmed environment")
        return errors
    try:
        environments = validate_environment_names(environments)
    except OnboardingError as exc:
        errors.append(str(exc))
        return errors
    root = project_root / contract.root_path
    for asset in contract.root_files:
        if not (root / asset.path).is_file():
            errors.append(f"missing `{(contract.root_path / asset.path).as_posix()}`")
    for environment in environments:
        for asset in contract.per_environment_files:
            relative_path = contract.root_path / environment / asset.path
            if not (project_root / relative_path).is_file():
                errors.append(f"missing `{relative_path.as_posix()}`")
    return errors


def update_controlled_block(path: Path, begin: str, end: str, body: str) -> None:
    content = path.read_text(encoding="utf-8")
    block = f"{begin}\n{body.rstrip()}\n{end}"
    if begin in content or end in content:
        if content.count(begin) != 1 or content.count(end) != 1 or content.index(begin) > content.index(end):
            raise OnboardingError(
                "invalid_controlled_block",
                f"{path} contains malformed DevOps asset inventory markers",
                EXIT_REPAIR_REQUIRED,
            )
        content = content[: content.index(begin)] + block + content[content.index(end) + len(end) :]
    else:
        separator = "\n" if content.endswith("\n") else "\n\n"
        content = content + separator + block + "\n"
    atomic_write(path, content)


def grandfathered_files(manifest: dict[str, Any]) -> dict[str, str]:
    values = manifest.get("grandfathered_files")
    if not isinstance(values, dict):
        return {}
    return {str(key): str(value) for key, value in values.items()}


def descriptor_enabled(descriptor: dict[str, Any], manifest: dict[str, Any]) -> bool:
    module = descriptor.get("module")
    modules = manifest.get("modules") if isinstance(manifest.get("modules"), dict) else {}
    if module not in {None, "control_plane"} and not bool(modules.get(module, False)):
        return False
    if module == "project_state" and manifest.get("project_mode") not in {"greenfield", "brownfield"}:
        return False
    modes = descriptor.get("project_modes")
    if modes and manifest.get("project_mode") not in modes:
        return False
    return descriptor.get("lifecycle") in {"core", "module_config"}


def required_descriptors(manifest: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    descriptors = [
        descriptor
        for descriptor in catalog.get("files", [])
        if descriptor_enabled(descriptor, manifest) and descriptor.get("id") != "manifest"
    ]
    return sorted(descriptors, key=lambda item: (int(item.get("init_order", 999)), item["id"]))


def read_init_status(path: Path) -> str:
    if not path.is_file():
        return "missing"
    if path.suffix in {".yaml", ".yml"}:
        try:
            parsed = PREFLIGHT.load_simple_yaml(path)
        except Exception:
            return "needs_review"
        return str(parsed.get("init_status", "needs_review"))
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "needs_review"
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return "needs_review"
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip() == "init_status":
            return str(PREFLIGHT.parse_scalar(value))
    return "needs_review"


def ensure_rendered_init_fields(content: str, *, markdown: bool) -> str:
    if markdown:
        match = FRONT_MATTER_RE.match(content)
        if not match:
            raise OnboardingError(
                "template_error",
                "initialized Markdown template is missing YAML front matter",
                EXIT_REPAIR_REQUIRED,
            )
        header = match.group(1)
        body = content[match.end() :]
    else:
        header = content.rstrip("\n")
        body = ""

    lines = header.splitlines()
    top_level_keys = {
        line.split(":", 1)[0].strip()
        for line in lines
        if line and not line.startswith((" ", "\t")) and ":" in line
    }
    defaults: list[tuple[str, Any]] = [
        ("schema_version", 5),
        ("init_status", "not_started"),
        ("init_completed_at", "none"),
        ("init_confirmed_by", "none"),
    ]
    insertion_index = 1 if lines and lines[0].startswith("kind:") else 0
    for key, value in reversed(defaults):
        if key not in top_level_keys:
            lines.insert(insertion_index, f"{key}: {yaml_scalar(value)}")
    rendered_header = "\n".join(lines) + "\n"
    if markdown:
        return "---\n" + rendered_header + "---\n" + body
    return rendered_header


def create_descriptor_file(
    project_root: Path,
    descriptor: dict[str, Any],
    manifest: dict[str, Any],
    timestamp: str,
) -> None:
    relative_path = Path(descriptor["path"])
    destination = project_root / relative_path
    if destination.exists():
        return
    template_path = SKILL_ROOT / descriptor["template"]
    content = render(template_path, render_values(manifest, timestamp, project_root))
    content = ensure_rendered_init_fields(content, markdown=destination.suffix.lower() == ".md")
    atomic_write(destination, content)


def enabled_project_assets(manifest: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    raw_assets = catalog.get("project_assets", [])
    if not isinstance(raw_assets, list):
        raise OnboardingError(
            "invalid_catalog",
            "state catalog project_assets must be a list",
            EXIT_REPAIR_REQUIRED,
        )
    modules = manifest.get("modules") if isinstance(manifest.get("modules"), dict) else {}
    enabled: list[dict[str, Any]] = []
    for index, asset in enumerate(raw_assets):
        if not isinstance(asset, dict):
            raise OnboardingError(
                "invalid_catalog",
                f"state catalog project_assets[{index}] must be an object",
                EXIT_REPAIR_REQUIRED,
            )
        module = str(asset.get("module", "control_plane"))
        if module != "control_plane" and not bool(modules.get(module, False)):
            continue
        modes = asset.get("project_modes")
        if isinstance(modes, list) and manifest.get("project_mode") not in modes:
            continue
        since_version = str(asset.get("since_skill_version", "0.0.0"))
        if not re.fullmatch(r"[0-9]\.[0-9]\.[0-9]", since_version):
            raise OnboardingError(
                "invalid_catalog",
                f"invalid project asset since_skill_version: {since_version}",
                EXIT_REPAIR_REQUIRED,
            )
        expected = tuple(int(part) for part in since_version.split("."))
        if not version_at_least(manifest.get("skill_version"), expected):
            continue
        enabled.append(asset)
    return enabled


def sync_project_assets(
    project_root: Path,
    manifest: dict[str, Any],
    catalog: dict[str, Any],
    timestamp: str,
) -> list[str]:
    created: list[str] = []
    for asset in enabled_project_assets(manifest, catalog):
        relative_path = Path(str(asset.get("path", "")))
        if not relative_path.parts or relative_path.is_absolute() or ".." in relative_path.parts:
            raise OnboardingError(
                "invalid_catalog",
                f"invalid project asset path: {relative_path}",
                EXIT_REPAIR_REQUIRED,
            )
        destination = project_root / relative_path
        if destination.exists():
            if not destination.is_file():
                raise OnboardingError(
                    "asset_path_conflict",
                    f"project asset path exists but is not a file: {destination}",
                    EXIT_CONFLICT,
                )
            continue
        template_path = SKILL_ROOT / str(asset.get("template", ""))
        atomic_write(destination, render(template_path, render_values(manifest, timestamp, project_root)))
        created.append(relative_path.as_posix())
    return created


def sync_files(project_root: Path, manifest: dict[str, Any], timestamp: str) -> list[str]:
    if manifest_language(manifest) == PENDING_LANGUAGE:
        manifest["language"] = PRIMARY_LANGUAGE
    catalog = load_catalog()
    created: list[str] = []
    file_status = manifest.setdefault("file_status", {})
    if not isinstance(file_status, dict):
        file_status = {}
        manifest["file_status"] = file_status

    for descriptor in required_descriptors(manifest, catalog):
        destination = project_root / descriptor["path"]
        existed = destination.exists()
        create_descriptor_file(project_root, descriptor, manifest, timestamp)
        if not existed and destination.exists():
            created.append(descriptor["path"])
        if descriptor["id"] in grandfathered_files(manifest) and destination.exists():
            file_status[descriptor["id"]] = "complete"
        else:
            file_status[descriptor["id"]] = read_init_status(destination)
    created.extend(sync_project_assets(project_root, manifest, catalog, timestamp))
    sync_project_documents(project_root, generated_at=timestamp)
    write_manifest(project_root, manifest)
    return created


def update_top_level_fields(path: Path, updates: dict[str, Any]) -> None:
    content = path.read_text(encoding="utf-8")
    is_markdown = path.suffix.lower() == ".md"
    if is_markdown:
        match = FRONT_MATTER_RE.match(content)
        if not match:
            raise OnboardingError(
                "invalid_front_matter",
                f"{path} is missing YAML front matter",
                EXIT_REPAIR_REQUIRED,
            )
        header = match.group(1)
        body = content[match.end() :]
    else:
        header = content.rstrip("\n")
        body = ""

    lines = header.splitlines()
    remaining = dict(updates)
    for index, line in enumerate(lines):
        if line.startswith(" ") or line.startswith("\t") or ":" not in line:
            continue
        key = line.split(":", 1)[0].strip()
        if key in remaining:
            lines[index] = f"{key}: {yaml_scalar(remaining.pop(key))}"
    for key, value in remaining.items():
        lines.append(f"{key}: {yaml_scalar(value)}")

    rendered_header = "\n".join(lines) + "\n"
    if is_markdown:
        atomic_write(path, "---\n" + rendered_header + "---\n" + body)
    else:
        atomic_write(path, rendered_header)


def file_rows(project_root: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    legacy_files = grandfathered_files(manifest)
    for descriptor in required_descriptors(manifest, load_catalog()):
        path = project_root / descriptor["path"]
        is_grandfathered = descriptor["id"] in legacy_files and path.exists()
        rows.append(
            {
                "id": descriptor["id"],
                "path": descriptor["path"],
                "init_status": "complete" if is_grandfathered else read_init_status(path),
                "prompt": descriptor.get("prompt") or "完成该文件并请求确认。",
                "counts_toward_ready": bool(descriptor.get("counts_toward_ready", False)),
                "legacy": is_grandfathered,
            }
        )
    return rows


def status_result(project_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    initialization = manifest.get("initialization")
    if not isinstance(initialization, dict):
        initialization = {}
    rows = file_rows(project_root, manifest)
    pending = [
        row
        for row in rows
        if row["counts_toward_ready"] and row["init_status"] != "complete"
    ]
    language = manifest_language(manifest)
    if manifest.get("modules", {}).get("project_state") and manifest.get("project_mode") not in {
        "greenfield",
        "brownfield",
    }:
        next_item: dict[str, Any] | None = {
            "id": "project_mode",
            "path": ".claw/manifest.yaml",
            "init_status": "not_started",
            "prompt": "Confirm greenfield or brownfield using the preflight evidence.",
        }
    else:
        next_item = pending[0] if pending else None
    return {
        "status": initialization.get("status", "needs_review"),
        "project_root": str(project_root),
        "state_dir": STATE_DIR_NAME,
        "language": language,
        "project_mode": manifest.get("project_mode"),
        "modules": manifest.get("modules", {}),
        "files": rows,
        "pending_count": len(pending)
        + (1 if next_item and next_item.get("id") == "project_mode" else 0),
        "next": next_item,
        "ready_to_finalize": next_item is None,
    }


def emit(result: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return
    print(f"status: {result.get('status')}")
    if result.get("message"):
        print(result["message"])
    if result.get("next"):
        print(f"next: {result['next']['id']} - {result['next']['prompt']}")


def validate_module_dependencies(modules: dict[str, bool]) -> None:
    if modules.get("collaboration_gate") and not modules.get("project_state"):
        raise OnboardingError(
            "module_dependency",
            "collaboration_gate requires project_state; enable project_state or disable collaboration_gate",
            EXIT_INVALID_INPUT,
        )


def validate_mode_for_modules(manifest: dict[str, Any], *, allow_pending: bool) -> None:
    modules = manifest.get("modules")
    if not isinstance(modules, dict):
        raise OnboardingError("invalid_modules", "manifest modules must be a mapping", EXIT_INVALID_INPUT)
    project_mode = manifest.get("project_mode")
    if modules.get("project_state"):
        allowed = {"greenfield", "brownfield"}
        if allow_pending:
            allowed.add("pending")
        if project_mode not in allowed:
            raise OnboardingError(
                "invalid_project_mode",
                "project_state requires a confirmed greenfield/brownfield mode before finalization",
                EXIT_INVALID_INPUT,
            )
    elif project_mode != "not_applicable":
        raise OnboardingError(
            "invalid_project_mode",
            "project_state=false requires project_mode=not_applicable",
            EXIT_INVALID_INPUT,
        )


def validate_manifest_language(manifest: dict[str, Any], *, allow_pending: bool) -> str:
    try:
        language = manifest_language(manifest, allow_pending=allow_pending)
    except ValueError as exc:
        raise OnboardingError("invalid_language", str(exc), EXIT_INVALID_INPUT) from exc
    if not allow_pending and language == PENDING_LANGUAGE:
        raise OnboardingError(
            "language_not_confirmed",
            "resume onboarding once to normalize the legacy pending language marker to zh-CN",
            EXIT_NEEDS_INPUT,
        )
    return language


def ensure_project_root(path: str) -> Path:
    project_root = Path(path).resolve()
    if not project_root.is_dir():
        raise OnboardingError(
            "invalid_project_root",
            f"project root does not exist or is not a directory: {project_root}",
            EXIT_INVALID_INPUT,
        )
    return project_root


def ensure_guidance(project_root: Path) -> None:
    script = SCRIPT_DIR / "ensure-agent-guidance.sh"
    result = subprocess.run(
        ["bash", str(script), str(project_root)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise OnboardingError(
            "guidance_failed",
            result.stderr.strip() or "failed to update README.md and AGENTS.md guidance",
            EXIT_IO_ERROR,
        )


def ensure_local_ignore(project_root: Path) -> None:
    path = project_root / ".gitignore"
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    entries = {line.strip() for line in existing.splitlines()}
    required_entries = [
        entry
        for entry in (".claw-local/", ".claw/.locks/")
        if entry not in entries and entry.rstrip("/") not in entries
    ]
    if not required_entries:
        return
    separator = "" if not existing or existing.endswith("\n") else "\n"
    atomic_write(path, existing + separator + "".join(f"{entry}\n" for entry in required_entries))


def ensure_devops_ignore(project_root: Path, contract: DevOpsAssetContract) -> bool:
    path = project_root / ".gitignore"
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    entry = f"{contract.root_path.as_posix()}/**/.env"
    if entry in {line.strip() for line in existing.splitlines()}:
        return False
    separator = "" if not existing or existing.endswith("\n") else "\n"
    atomic_write(path, existing + separator + entry + "\n")
    return True


def create_manifest_data(
    project_mode: str,
    modules: dict[str, bool],
    timestamp: str,
) -> dict[str, Any]:
    template_path = SKILL_ROOT / "templates/core/manifest.yaml"
    draft = {
        "project_mode": project_mode,
        "modules": modules,
        "language": PRIMARY_LANGUAGE,
    }
    rendered = render(template_path, render_values(draft, timestamp))
    temporary_dir = Path(tempfile.mkdtemp(prefix="cc-onboarding-manifest-"))
    temporary_path = temporary_dir / "manifest.yaml"
    try:
        temporary_path.write_text(rendered, encoding="utf-8")
        manifest = PREFLIGHT.load_simple_yaml(temporary_path)
        module_config = manifest.setdefault("module_config", {})
        module_config["collaboration_gate"] = (
            ".claw/collaboration-config.yaml" if modules["collaboration_gate"] else "none"
        )
        module_config["change_review"] = (
            ".claw/review-config.yaml" if modules["change_review"] else "none"
        )
        return manifest
    finally:
        try:
            temporary_path.unlink()
            temporary_dir.rmdir()
        except OSError:
            pass


def read_legacy_boundary(index_path: Path) -> tuple[set[str], str]:
    try:
        fields = read_mapping_list_yaml(index_path, list_key="documents")
    except (OSError, ValueError) as exc:
        raise OnboardingError(
            "invalid_legacy_index",
            f"invalid legacy index in {index_path}: {exc}",
            EXIT_REPAIR_REQUIRED,
        ) from exc

    raw_documents = fields.get("documents", [])
    if not isinstance(raw_documents, list):
        raise OnboardingError(
            "invalid_legacy_index",
            f"legacy index documents must be a list: {index_path}",
            EXIT_REPAIR_REQUIRED,
        )
    paths: set[str] = set()
    for item in raw_documents:
        if not isinstance(item, dict):
            raise OnboardingError(
                "invalid_legacy_index",
                f"legacy index entry must be a mapping: {index_path}",
                EXIT_REPAIR_REQUIRED,
            )
        item_path = clean_value(item.get("path"))
        if not item_path:
            raise OnboardingError(
                "invalid_legacy_index",
                f"legacy index entry lacks path: {index_path}",
                EXIT_REPAIR_REQUIRED,
            )
        paths.add(item_path)

    policy_effective_at = clean_value(fields.get("policy_effective_at"))
    if not policy_effective_at:
        raise OnboardingError(
            "invalid_legacy_index",
            f"legacy index lacks policy_effective_at: {index_path}",
            EXIT_REPAIR_REQUIRED,
        )
    return paths, policy_effective_at


def command_adopt(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    project_root = ensure_project_root(args.project_root)
    timestamp = utc_now(args.now)
    catalog = load_catalog()
    defaults = {name: bool(config.get("default", False)) for name, config in catalog["modules"].items()}
    requested_modules = {
        "project_state": bool_flag(args.project_state, defaults["project_state"]),
        "collaboration_gate": bool_flag(args.collaboration_gate, defaults["collaboration_gate"]),
        "change_review": bool_flag(args.change_review, defaults["change_review"]),
    }
    validate_module_dependencies(requested_modules)
    if not requested_modules["project_state"] and args.mode:
        raise OnboardingError(
            "project_mode_not_applicable",
            "--mode is not used when project_state is off",
            EXIT_INVALID_INPUT,
        )
    requested_mode = args.mode or "pending" if requested_modules["project_state"] else "not_applicable"

    with onboarding_lock(project_root):
        state_dir = project_root / STATE_DIR_NAME
        manifest_path = project_root / MANIFEST_RELATIVE_PATH
        if not state_dir.is_dir():
            raise OnboardingError(
                "legacy_state_missing",
                "explicit adoption requires an existing .claw directory",
                EXIT_INVALID_INPUT,
            )
        if manifest_path.exists():
            manifest = load_manifest(project_root)
            compatibility = manifest.get("compatibility")
            if isinstance(compatibility, dict) and compatibility.get("legacy_index_path") not in {
                None,
                "none",
            }:
                existing_language = manifest_language(manifest)
                if existing_language == PENDING_LANGUAGE:
                    manifest["language"] = PRIMARY_LANGUAGE
                    write_manifest(project_root, manifest)
                validate_manifest_language(manifest, allow_pending=False)
                ensure_guidance(project_root)
                ensure_local_ignore(project_root)
                created_files = sync_files(project_root, manifest, timestamp)
                result = status_result(project_root, manifest)
                result["adopted"] = True
                result["created"] = created_files
                return result, EXIT_NEEDS_INPUT if result["next"] else EXIT_OK
            raise OnboardingError(
                "manifest_conflict",
                "manifest.yaml already exists and is not an explicit legacy adoption manifest",
                EXIT_CONFLICT,
            )

        snapshot_process = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "snapshot-legacy-documents.py"),
                str(project_root),
                "--created-by",
                args.confirmed_by,
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if snapshot_process.returncode != 0:
            raise OnboardingError(
                "legacy_snapshot_failed",
                snapshot_process.stderr.strip() or snapshot_process.stdout.strip() or "legacy snapshot failed",
                EXIT_REPAIR_REQUIRED,
            )
        try:
            snapshot_payload = json.loads(snapshot_process.stdout)
        except json.JSONDecodeError as exc:
            raise OnboardingError(
                "legacy_snapshot_failed",
                "legacy snapshot did not emit JSON",
                EXIT_REPAIR_REQUIRED,
            ) from exc

        index_path = project_root / ".claw" / "legacy-document-index.yaml"
        legacy_paths, policy_effective_at = read_legacy_boundary(index_path)
        manifest = create_manifest_data(requested_mode, requested_modules, timestamp)
        compatibility = manifest.setdefault("compatibility", {})
        compatibility["legacy_documents_allowed"] = True
        compatibility["legacy_index_path"] = ".claw/legacy-document-index.yaml"
        compatibility["policy_effective_at"] = policy_effective_at

        legacy_files: dict[str, str] = {}
        file_status = manifest.setdefault("file_status", {})
        adoption_candidates = [
            descriptor
            for descriptor in catalog.get("files", [])
            if descriptor.get("lifecycle") == "core"
            or (
                descriptor.get("lifecycle") == "module_config"
                and descriptor_enabled(descriptor, manifest)
            )
        ]
        for descriptor in adoption_candidates:
            relative_path = descriptor.get("path")
            if not relative_path:
                continue
            if relative_path in legacy_paths and (project_root / relative_path).exists():
                legacy_files[descriptor["id"]] = relative_path
                file_status[descriptor["id"]] = "complete"
        manifest["grandfathered_files"] = legacy_files
        write_manifest(project_root, manifest)

        ensure_guidance(project_root)
        ensure_local_ignore(project_root)
        created_files = sync_files(project_root, manifest, timestamp)
        result = status_result(project_root, manifest)
        result["adopted"] = True
        result["legacy_snapshot"] = snapshot_payload
        result["grandfathered_files"] = legacy_files
        result["created"] = [str(MANIFEST_RELATIVE_PATH)] + created_files
        if result["next"] is not None:
            result["status"] = "needs_input"
            return result, EXIT_NEEDS_INPUT
        return result, EXIT_OK


def command_start(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    project_root = ensure_project_root(args.project_root)
    timestamp = utc_now(args.now)
    catalog = load_catalog()
    defaults = {name: bool(config.get("default", False)) for name, config in catalog["modules"].items()}
    requested_modules = {
        "project_state": bool_flag(args.project_state, defaults["project_state"]),
        "collaboration_gate": bool_flag(args.collaboration_gate, defaults["collaboration_gate"]),
        "change_review": bool_flag(args.change_review, defaults["change_review"]),
    }
    validate_module_dependencies(requested_modules)
    if not requested_modules["project_state"] and args.mode:
        raise OnboardingError(
            "project_mode_not_applicable",
            "--mode is not used when project_state is off",
            EXIT_INVALID_INPUT,
        )
    requested_mode = (
        args.mode or "pending" if requested_modules["project_state"] else "not_applicable"
    )
    with onboarding_lock(project_root):
        state_dir = project_root / STATE_DIR_NAME
        manifest_path = project_root / MANIFEST_RELATIVE_PATH
        if state_dir.exists() and not state_dir.is_dir():
            raise OnboardingError("state_path_conflict", ".claw exists but is not a directory", EXIT_CONFLICT)
        if state_dir.exists() and not manifest_path.exists():
            raise OnboardingError(
                "legacy_state",
                ".claw exists without manifest.yaml; refusing to overwrite a historical installation",
                EXIT_CONFLICT,
            )

        created_manifest = False
        if manifest_path.exists():
            manifest = load_manifest(project_root)
            if manifest_language(manifest) == PENDING_LANGUAGE:
                manifest["language"] = PRIMARY_LANGUAGE
            existing_mode = manifest.get("project_mode")
            if existing_mode == "pending" and args.mode:
                manifest["project_mode"] = args.mode
            elif args.mode and existing_mode not in {args.mode, "not_applicable"}:
                raise OnboardingError(
                    "project_mode_conflict",
                    f"manifest project_mode is {existing_mode}; refusing to replace it with {args.mode}",
                    EXIT_CONFLICT,
                )
        else:
            state_dir.mkdir(parents=False, exist_ok=False)
            manifest = create_manifest_data(requested_mode, requested_modules, timestamp)
            write_manifest(project_root, manifest)
            created_manifest = True

        validate_manifest_language(manifest, allow_pending=False)
        ensure_guidance(project_root)
        ensure_local_ignore(project_root)
        created_files = sync_files(project_root, manifest, timestamp)
        result = status_result(project_root, manifest)
        result["created"] = [str(MANIFEST_RELATIVE_PATH)] + created_files if created_manifest else created_files
        result["mode_recommendation"] = PREFLIGHT.collect_mode_evidence(project_root)
        if result["next"] is not None:
            result["status"] = "needs_input"
            return result, EXIT_NEEDS_INPUT
        return result, EXIT_OK


def command_status(args: argparse.Namespace, resume: bool = False) -> tuple[dict[str, Any], int]:
    project_root = ensure_project_root(args.project_root)
    manifest = load_manifest(project_root)
    result = status_result(project_root, manifest)
    if resume:
        result["question_batch"] = [result["next"]] if result["next"] else []
    return result, EXIT_NEEDS_INPUT if result["next"] else EXIT_OK


def find_descriptor(file_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
    for descriptor in required_descriptors(manifest, load_catalog()):
        if descriptor["id"] == file_id:
            return descriptor
    raise OnboardingError(
        "unknown_or_disabled_file",
        f"`{file_id}` is not an enabled initialization file",
        EXIT_INVALID_INPUT,
    )


def render_devops_inventory(environments: list[str], contract: DevOpsAssetContract) -> str:
    asset_labels = [asset.path.as_posix() for asset in contract.per_environment_files]
    lines = [
        "## 环境资产清单",
        "",
        f"此清单由 `{contract.initialization_command}` 维护。调整客户环境时再次运行该命令；已有文件不会被覆盖或删除。",
        "",
        "| " + " | ".join(["环境", *asset_labels]) + " |",
        "| " + " | ".join(["---"] * (len(asset_labels) + 1)) + " |",
    ]
    for environment in environments:
        asset_paths = [
            f"`{(contract.root_path / environment / asset.path).as_posix()}`"
            for asset in contract.per_environment_files
        ]
        lines.append("| " + " | ".join([f"`{environment}`", *asset_paths]) + " |")
    return "\n".join(lines)


def command_devops_assets(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    project_root = ensure_project_root(args.project_root)
    timestamp = utc_now(args.now)
    contract = devops_contract()
    requested = list(RECOMMENDED_ENVIRONMENTS) if args.recommended_environments else list(args.environment or [])
    if not requested:
        raise OnboardingError(
            "environment_confirmation_required",
            (
                "confirm one or more customer environments with --environment, or accept the "
                "recommended reserved environments with --recommended-environments (DEV, UAT, PROD)"
            ),
            EXIT_NEEDS_INPUT,
        )
    requested = validate_environment_names(requested)

    with onboarding_lock(project_root):
        manifest = load_manifest(project_root)
        validate_manifest_language(manifest, allow_pending=False)
        descriptor = find_descriptor("devops", manifest)
        devops_path = project_root / descriptor["path"]
        if not devops_path.is_file():
            raise OnboardingError(
                "missing_file",
                f"missing initialization file: {devops_path}; run the onboarding sync command first",
                EXIT_REPAIR_REQUIRED,
            )

        fields = read_top_level_fields(devops_path)
        existing_environments = validate_environment_names(
            scalar_items(fields.get(contract.environments_field))
        )
        environments = list(existing_environments)
        known = {name.casefold() for name in environments}
        environment_added = False
        for environment in requested:
            if environment.casefold() not in known:
                environments.append(environment)
                known.add(environment.casefold())
                environment_added = True

        created: list[str] = []
        preserved: list[str] = []
        values = render_values(manifest, timestamp, project_root)
        values["DEVOPS_ASSETS_ROOT"] = contract.root_path.as_posix()

        asset_templates = {
            contract.root_path / asset.path: SKILL_ROOT / asset.template
            for asset in contract.root_files
        }
        for environment in environments:
            for asset in contract.per_environment_files:
                asset_templates[contract.root_path / environment / asset.path] = SKILL_ROOT / asset.template

        for relative_path, template_path in asset_templates.items():
            destination = project_root / relative_path
            if destination.exists():
                if not destination.is_file():
                    raise OnboardingError(
                        "asset_path_conflict",
                        f"DevOps asset path exists but is not a file: {destination}",
                        EXIT_CONFLICT,
                    )
                preserved.append(relative_path.as_posix())
                continue
            template_values = dict(values)
            template_values["ENVIRONMENT"] = relative_path.parent.name
            atomic_write(destination, render(template_path, template_values))
            created.append(relative_path.as_posix())

        ignore_entry = f"{contract.root_path.as_posix()}/**/.env"
        if ensure_devops_ignore(project_root, contract):
            created.append(f".gitignore entry: {ignore_entry}")
        else:
            preserved.append(f".gitignore entry: {ignore_entry}")

        previous_status = str(fields.get("init_status", "not_started"))
        next_status = "needs_review" if previous_status == "complete" else "in_progress"
        inventory = render_devops_inventory(environments, contract)
        devops_text = devops_path.read_text(encoding="utf-8")
        metadata_changed = (
            str(fields.get(contract.root_field, "")).strip() != contract.root_path.as_posix()
            or existing_environments != environments
        )
        inventory_changed = inventory not in devops_text
        state_changed = bool(created) or environment_added or metadata_changed or inventory_changed
        if state_changed:
            update_top_level_fields(
                devops_path,
                {
                    contract.root_field: contract.root_path.as_posix(),
                    contract.environments_field: ", ".join(environments),
                    "init_status": next_status,
                    "init_completed_at": "none",
                    "init_confirmed_by": "none",
                    "updated_at": timestamp,
                    "updated_by": "onboarding",
                },
            )
            update_controlled_block(
                devops_path,
                DEVOPS_ASSETS_BEGIN,
                DEVOPS_ASSETS_END,
                inventory,
            )

            file_status = manifest.setdefault("file_status", {})
            if not isinstance(file_status, dict):
                file_status = {}
                manifest["file_status"] = file_status
            file_status["devops"] = next_status
            initialization = manifest.setdefault("initialization", {})
            if not isinstance(initialization, dict):
                initialization = {}
                manifest["initialization"] = initialization
            if initialization.get("status") == "ready":
                initialization["status"] = "needs_review"
                initialization["completed_at"] = "none"
                initialization["confirmed_by"] = "none"
            write_manifest(project_root, manifest)

        result = status_result(project_root, manifest)
        result.update(
            {
                "status": "needs_input",
                "devops_assets_root": contract.root_path.as_posix(),
                "environments": environments,
                "recommended_defaults_used": bool(args.recommended_environments),
                "created": created,
                "preserved": preserved,
                "changed": state_changed,
                "message": (
                    "DevOps environment assets are reserved; review and customize each environment before completing devops onboarding."
                    if state_changed
                    else "DevOps environment assets are unchanged."
                ),
            }
        )
        return result, EXIT_NEEDS_INPUT


def command_mark(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    project_root = ensure_project_root(args.project_root)
    timestamp = utc_now(args.now)
    with onboarding_lock(project_root):
        manifest = load_manifest(project_root)
        descriptor = find_descriptor(args.file_id, manifest)
        if descriptor["id"] in grandfathered_files(manifest):
            result = status_result(project_root, manifest)
            result["marked"] = {
                "id": descriptor["id"],
                "init_status": "complete",
                "legacy": True,
                "changed": False,
            }
            return result, EXIT_NEEDS_INPUT if result["next"] else EXIT_OK
        path = project_root / descriptor["path"]
        if not path.is_file():
            raise OnboardingError("missing_file", f"missing initialization file: {path}", EXIT_REPAIR_REQUIRED)
        if args.status == "complete" and not args.confirmed_by:
            raise OnboardingError(
                "confirmation_required",
                "--confirmed-by is required when marking a file complete",
                EXIT_NEEDS_INPUT,
            )
        if args.status == "complete" and path.suffix.lower() == ".md":
            content = path.read_text(encoding="utf-8")
            if ONBOARDING_INCOMPLETE_SENTINEL in content:
                result = status_result(project_root, manifest)
                result["status"] = "needs_input"
                result["error"] = "onboarding_incomplete"
                result["message"] = (
                    f"{descriptor['path']} still contains the onboarding-incomplete marker; "
                    "write and confirm the required answers, then remove the marker before "
                    "marking the file complete"
                )
                result["repair"] = {
                    "file_id": descriptor["id"],
                    "path": descriptor["path"],
                    "sentinel": ONBOARDING_INCOMPLETE_SENTINEL,
                }
                return result, EXIT_NEEDS_INPUT
        if (
            args.status == "complete"
            and descriptor["id"] == "devops"
            and version_at_least(manifest.get("skill_version"), devops_contract().since_skill_version)
        ):
            asset_errors = devops_asset_errors(project_root, path)
            if asset_errors:
                result = status_result(project_root, manifest)
                result["status"] = "needs_input"
                result["error"] = "devops_assets_incomplete"
                result["message"] = "DevOps environment assets are incomplete"
                result["repair"] = {
                    "command": devops_contract().initialization_command,
                    "errors": asset_errors,
                    "recommendation": "Use --recommended-environments to reserve DEV, UAT, and PROD when the customer has not decided.",
                }
                return result, EXIT_NEEDS_INPUT

        updates: dict[str, Any] = {
            "init_status": args.status,
            "updated_at": timestamp,
            "updated_by": args.confirmed_by or "onboarding",
        }
        if args.status == "complete":
            updates["init_completed_at"] = timestamp
            updates["init_confirmed_by"] = args.confirmed_by
        else:
            updates["init_completed_at"] = "none"
            updates["init_confirmed_by"] = "none"
        if descriptor["id"] == "decisions":
            updates["architecture_init_status"] = args.status
            updates["architecture_reviewed_at"] = timestamp if args.status == "complete" else "none"
            updates["architecture_confirmed_by"] = args.confirmed_by if args.status == "complete" else "none"
        update_top_level_fields(path, updates)
        sync_project_documents(project_root, generated_at=timestamp)

        file_status = manifest.setdefault("file_status", {})
        if not isinstance(file_status, dict):
            file_status = {}
            manifest["file_status"] = file_status
        file_status[descriptor["id"]] = args.status
        initialization = manifest.setdefault("initialization", {})
        if not isinstance(initialization, dict):
            initialization = {}
            manifest["initialization"] = initialization
        if initialization.get("status") == "ready" and args.status != "complete":
            initialization["status"] = "needs_review"
        write_manifest(project_root, manifest)
        result = status_result(project_root, manifest)
        result["marked"] = {"id": descriptor["id"], "init_status": args.status}
        return result, EXIT_NEEDS_INPUT if result["next"] else EXIT_OK


def command_sync(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    project_root = ensure_project_root(args.project_root)
    timestamp = utc_now(args.now)
    with onboarding_lock(project_root):
        manifest = load_manifest(project_root)
        validate_module_dependencies(manifest.get("modules", {}))
        created = sync_files(project_root, manifest, timestamp)
        result = status_result(project_root, manifest)
        result["created"] = created
        return result, EXIT_NEEDS_INPUT if result["next"] else EXIT_OK


def command_finalize(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    project_root = ensure_project_root(args.project_root)
    timestamp = utc_now(args.now)
    if not args.confirmed_by:
        raise OnboardingError(
            "confirmation_required",
            "--confirmed-by is required for finalization",
            EXIT_NEEDS_INPUT,
        )
    with onboarding_lock(project_root):
        manifest = load_manifest(project_root)
        validate_manifest_language(manifest, allow_pending=False)
        validate_module_dependencies(manifest.get("modules", {}))
        validate_mode_for_modules(manifest, allow_pending=False)
        result = status_result(project_root, manifest)
        if result["next"] is not None:
            result["status"] = "in_progress"
            result["message"] = "initialization cannot be finalized while required files are incomplete"
            return result, EXIT_REPAIR_REQUIRED

        decisions_path = project_root / STATE_DIR_NAME / "decisions.md"
        legacy_decisions = "decisions" in grandfathered_files(manifest)
        if (
            manifest.get("modules", {}).get("project_state")
            and decisions_path.exists()
            and not legacy_decisions
        ):
            try:
                decisions_text = decisions_path.read_text(encoding="utf-8")
            except OSError as exc:
                raise OnboardingError("io_error", str(exc), EXIT_IO_ERROR) from exc
            if "## ARCHITECTURE" not in decisions_text:
                raise OnboardingError(
                    "architecture_missing",
                    "decisions.md must contain the `## ARCHITECTURE` section",
                    EXIT_REPAIR_REQUIRED,
                )

        initialization = manifest.get("initialization")
        already_ready = isinstance(initialization, dict) and initialization.get("status") == "ready"
        legacy_current_status = "current_status" in grandfathered_files(manifest)
        if (
            not already_ready
            and manifest.get("modules", {}).get("project_state")
            and not legacy_current_status
        ):
            generation_process = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "generate-current-status.py"),
                    str(project_root / STATE_DIR_NAME),
                    "--write",
                    "--updated-by",
                    args.confirmed_by,
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if generation_process.returncode != 0:
                raise OnboardingError(
                    "current_status_generation_failed",
                    generation_process.stderr.strip()
                    or generation_process.stdout.strip()
                    or "failed to generate current-status.md",
                    EXIT_REPAIR_REQUIRED,
                )

        sync_project_documents(project_root, generated_at=timestamp)
        validation_command = [
            sys.executable,
            str(SCRIPT_DIR / "validate-state.py"),
            str(project_root / STATE_DIR_NAME),
            "--catalog",
            str(CATALOG_PATH),
            "--strict-v5",
            "--json",
        ]
        validation_process = subprocess.run(
            validation_command,
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            validation_payload = json.loads(validation_process.stdout)
        except json.JSONDecodeError:
            validation_payload = {
                "status": "failed",
                "errors": [validation_process.stderr.strip() or "validator did not emit JSON"],
            }
        if validation_process.returncode != 0:
            initialization = manifest.setdefault("initialization", {})
            if not isinstance(initialization, dict):
                initialization = {}
                manifest["initialization"] = initialization
            initialization["status"] = "needs_review"
            initialization["completed_at"] = "none"
            initialization["confirmed_by"] = "none"
            write_manifest(project_root, manifest)
            failed = status_result(project_root, manifest)
            failed["status"] = "needs_review"
            failed["message"] = "strict v5 validation failed; initialization remains non-ready"
            failed["validation"] = validation_payload
            return failed, EXIT_REPAIR_REQUIRED

        initialization = manifest.setdefault("initialization", {})
        if not isinstance(initialization, dict):
            initialization = {}
            manifest["initialization"] = initialization
        if initialization.get("status") == "ready":
            unchanged = status_result(project_root, manifest)
            unchanged["status"] = "ready"
            unchanged["message"] = "guided project initialization is already ready"
            unchanged["validation"] = validation_payload
            unchanged["changed"] = False
            return unchanged, EXIT_OK
        initialization["status"] = "ready"
        initialization["completed_at"] = timestamp
        initialization["confirmed_by"] = args.confirmed_by
        write_manifest(project_root, manifest)
        finalized = status_result(project_root, manifest)
        finalized["status"] = "ready"
        finalized["message"] = "guided project initialization is ready"
        finalized["validation"] = validation_payload
        finalized["changed"] = True
        return finalized, EXIT_OK


def add_common(parser: argparse.ArgumentParser, include_now: bool = False) -> None:
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    if include_now:
        parser.add_argument("--now", help="fixed UTC timestamp for deterministic automation")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guided, resumable .claw project onboarding")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="start or idempotently continue onboarding")
    add_common(start, include_now=True)
    start.add_argument("--mode", choices=("greenfield", "brownfield"))
    start.add_argument("--project-state", choices=("on", "off"))
    start.add_argument("--collaboration-gate", choices=("on", "off"))
    start.add_argument("--change-review", choices=("on", "off"))

    adopt = subparsers.add_parser("adopt", help="explicitly adopt an existing legacy .claw project")
    add_common(adopt, include_now=True)
    adopt.add_argument("--mode", choices=("greenfield", "brownfield"))
    adopt.add_argument("--project-state", choices=("on", "off"))
    adopt.add_argument("--collaboration-gate", choices=("on", "off"))
    adopt.add_argument("--change-review", choices=("on", "off"))
    adopt.add_argument("--confirmed-by", required=True)

    status = subparsers.add_parser("status", help="show aggregate and per-file initialization status")
    add_common(status)

    resume = subparsers.add_parser("resume", help="return the first unfinished file and its question")
    add_common(resume)

    devops_assets = subparsers.add_parser(
        "devops-assets",
        help="reserve per-environment Dockerfile and environment-variable example assets",
    )
    add_common(devops_assets, include_now=True)
    environment_group = devops_assets.add_mutually_exclusive_group(required=False)
    environment_group.add_argument(
        "--environment",
        action="append",
        help="confirmed customer environment name; repeat for multiple environments",
    )
    environment_group.add_argument(
        "--recommended-environments",
        action="store_true",
        help="reserve the recommended DEV, UAT, and PROD environments",
    )

    mark = subparsers.add_parser("mark", help="update one enabled file's init_status")
    add_common(mark, include_now=True)
    mark.add_argument("file_id")
    mark.add_argument(
        "--status",
        required=True,
        choices=("not_started", "in_progress", "awaiting_confirmation", "complete", "needs_review"),
    )
    mark.add_argument("--confirmed-by")

    sync = subparsers.add_parser("sync", help="create missing files for newly enabled modules")
    add_common(sync, include_now=True)

    finalize = subparsers.add_parser("finalize", help="mark aggregate initialization ready")
    add_common(finalize, include_now=True)
    finalize.add_argument("--confirmed-by", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "start":
            result, exit_code = command_start(args)
        elif args.command == "adopt":
            result, exit_code = command_adopt(args)
        elif args.command == "status":
            result, exit_code = command_status(args)
        elif args.command == "resume":
            result, exit_code = command_status(args, resume=True)
        elif args.command == "devops-assets":
            result, exit_code = command_devops_assets(args)
        elif args.command == "mark":
            result, exit_code = command_mark(args)
        elif args.command == "sync":
            result, exit_code = command_sync(args)
        elif args.command == "finalize":
            result, exit_code = command_finalize(args)
        else:
            raise AssertionError(args.command)
    except OnboardingError as exc:
        result = {
            "status": "error",
            "error": exc.code,
            "message": str(exc),
        }
        exit_code = exc.exit_code
    except OSError as exc:
        result = {
            "status": "error",
            "error": "io_error",
            "message": str(exc),
        }
        exit_code = EXIT_IO_ERROR
    emit(result, getattr(args, "json", False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
