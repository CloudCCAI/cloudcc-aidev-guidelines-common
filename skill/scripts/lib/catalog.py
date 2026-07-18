from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class CatalogEntry:
    kind: str
    path: str = ""
    path_pattern: str = ""
    module: str = "project_state"
    category: str = "event"
    temperature: str = "cold"
    template: str = ""
    required_when: Any = None
    required_fields: tuple[str, ...] = ()
    initialization_required: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


def default_catalog_path() -> Path:
    return Path(__file__).resolve().parents[2] / "state-catalog.json"


def _strings(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, Iterable) and not isinstance(value, (dict, bytes)):
        return tuple(str(item) for item in value)
    return (str(value),)


def _raw_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    entries = data.get("artifacts", data.get("files"))
    if isinstance(entries, list):
        return [dict(item) for item in entries if isinstance(item, dict)]
    if isinstance(entries, dict):
        normalized: list[dict[str, Any]] = []
        for kind, value in entries.items():
            if not isinstance(value, dict):
                continue
            item = dict(value)
            item.setdefault("kind", kind)
            normalized.append(item)
        return normalized

    normalized = []
    for kind, value in data.items():
        if kind == "schema_version" or not isinstance(value, dict):
            continue
        item = dict(value)
        item.setdefault("kind", kind)
        normalized.append(item)
    return normalized


def load_catalog(path: Path | None = None) -> list[CatalogEntry]:
    catalog_path = Path(path) if path else default_catalog_path()
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"state catalog does not exist: {catalog_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid state catalog JSON: {catalog_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"state catalog root must be an object: {catalog_path}")

    result: list[CatalogEntry] = []
    for raw in _raw_entries(data):
        kind = str(raw.get("kind", "")).strip()
        if not kind:
            raise ValueError(f"catalog entry is missing kind: {raw}")
        known = {
            "kind",
            "path",
            "path_pattern",
            "module",
            "category",
            "temperature",
            "template",
            "required_when",
            "required_fields",
            "initialization_required",
        }
        result.append(
            CatalogEntry(
                kind=kind,
                path=str(raw.get("path", "")),
                path_pattern=str(raw.get("path_pattern", raw.get("pattern", ""))),
                module=str(raw.get("module", "project_state")),
                category=str(raw.get("category", raw.get("type", "event"))),
                temperature=str(raw.get("temperature", raw.get("tier", "cold"))),
                template=str(raw.get("template", "")),
                required_when=raw.get("required_when"),
                required_fields=_strings(raw.get("required_fields")),
                initialization_required=bool(raw.get("initialization_required", False)),
                extra={key: value for key, value in raw.items() if key not in known},
            )
        )
    return result


def by_kind(entries: Iterable[CatalogEntry]) -> dict[str, CatalogEntry]:
    return {entry.kind: entry for entry in entries}
