from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


ENVIRONMENT_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")


@dataclass(frozen=True)
class AssetTemplate:
    path: Path
    template: Path


@dataclass(frozen=True)
class DevOpsAssetContract:
    state_path: Path
    since_skill_version: tuple[int, int, int]
    root_field: str
    root_path: Path
    environments_field: str
    root_files: tuple[AssetTemplate, ...]
    per_environment_files: tuple[AssetTemplate, ...]
    initialization_command: str


def _version_tuple(value: object) -> tuple[int, int, int]:
    cleaned = str(value).strip().strip('"\'')
    if not re.fullmatch(r"[0-9]\.[0-9]\.[0-9]", cleaned):
        raise ValueError(f"invalid DevOps asset since_skill_version: {value}")
    return tuple(int(part) for part in cleaned.split("."))  # type: ignore[return-value]


def _relative_path(value: object, label: str) -> Path:
    path = Path(str(value).strip())
    if not path.parts or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"invalid DevOps asset {label}: {value}")
    return path


def _asset_templates(value: object, label: str) -> tuple[AssetTemplate, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"DevOps asset {label} must be a non-empty list")
    assets: list[AssetTemplate] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"DevOps asset {label}[{index}] must be an object")
        assets.append(
            AssetTemplate(
                path=_relative_path(item.get("path"), f"{label}[{index}].path"),
                template=_relative_path(item.get("template"), f"{label}[{index}].template"),
            )
        )
    return tuple(assets)


def contract_from_catalog(catalog: Mapping[str, object]) -> DevOpsAssetContract:
    entries = catalog.get("files")
    if not isinstance(entries, list):
        raise ValueError("state catalog files must be a list")
    descriptors = [item for item in entries if isinstance(item, Mapping) and item.get("id") == "devops"]
    if len(descriptors) != 1:
        raise ValueError("state catalog must contain exactly one devops descriptor")
    descriptor = descriptors[0]
    raw_contract = descriptor.get("external_assets")
    if not isinstance(raw_contract, Mapping):
        raise ValueError("state catalog devops descriptor must define external_assets")

    root_field = str(raw_contract.get("root_field", "")).strip()
    environments_field = str(raw_contract.get("environments_field", "")).strip()
    initialization_command = str(raw_contract.get("initialization_command", "")).strip()
    if not root_field or not environments_field or not initialization_command:
        raise ValueError("DevOps asset fields and initialization_command must be non-empty")

    return DevOpsAssetContract(
        state_path=_relative_path(descriptor.get("path"), "state path"),
        since_skill_version=_version_tuple(raw_contract.get("since_skill_version")),
        root_field=root_field,
        root_path=_relative_path(raw_contract.get("root_path"), "root_path"),
        environments_field=environments_field,
        root_files=_asset_templates(raw_contract.get("root_files"), "root_files"),
        per_environment_files=_asset_templates(
            raw_contract.get("per_environment_files"),
            "per_environment_files",
        ),
        initialization_command=initialization_command,
    )


def normalize_environment_names(names: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw_name in names:
        name = raw_name.strip()
        if not ENVIRONMENT_NAME_RE.fullmatch(name):
            raise ValueError(
                f"invalid environment name `{raw_name}`; use 1-64 letters, numbers, dots, "
                "underscores, or hyphens, beginning with a letter or number"
            )
        folded = name.casefold()
        if folded in seen:
            raise ValueError(f"environment names must be unique ignoring case: `{name}`")
        seen.add(folded)
        normalized.append(name)
    return normalized
