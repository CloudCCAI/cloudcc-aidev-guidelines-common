#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from lib.atomic_io import exclusive_create_text, file_lock
from lib.document_ids import document_id_from_path, extract_feature_ids, extract_task_ids, is_legacy_id
from lib.state_io import clean_value, read_mapping_list_yaml, utc_now


INDEX_RELATIVE_PATH = Path(".claw/legacy-document-index.yaml")
ELIGIBLE_SUFFIXES = {".md", ".yaml", ".yml", ".json"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _kind_for(path: Path) -> str:
    name = path.name
    if name.startswith("FEAT-"):
        return "feature-spec"
    if name.startswith("TASK-"):
        return "task-status" if path.suffix == ".md" else "assignment"
    return path.stem


def _schema_version_for(path: Path) -> int | str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, dict):
            value = data.get("schema_version", data.get("version"))
            if isinstance(value, (int, str)):
                return value

    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        try:
            lines = lines[1 : lines.index("---", 1)]
        except ValueError:
            return None
    elif path.suffix.lower() == ".md":
        return None
    for raw_line in lines:
        if raw_line[:1].isspace():
            continue
        match = re.match(r"^(?:schema_version|version):\s*([^#]+?)\s*$", raw_line)
        if not match:
            continue
        value = match.group(1).strip().strip('"').strip("'")
        return int(value) if value.isdigit() else value or None
    return None


def _canonical_id_for(path: Path) -> str | None:
    kind = "task" if path.name.startswith("TASK-") else "feature" if path.name.startswith("FEAT-") else ""
    if not kind:
        return None
    try:
        return document_id_from_path(path, kind)
    except ValueError:
        return None


def _is_legacy_document(path: Path) -> bool:
    canonical_id = _canonical_id_for(path)
    return _schema_version_for(path) != 5 or bool(canonical_id and is_legacy_id(canonical_id))


def eligible_legacy_paths(project_root: Path) -> list[Path]:
    project_root = Path(project_root).resolve()
    state_dir = project_root / ".claw"
    if not state_dir.is_dir():
        raise ValueError(f".claw state directory does not exist: {state_dir}")

    paths: list[Path] = []
    for path in state_dir.rglob("*"):
        relative = path.relative_to(project_root)
        if path.is_symlink():
            raise ValueError(f"legacy snapshot refuses symlinks: {relative}")
        if not path.is_file() or path.suffix.lower() not in ELIGIBLE_SUFFIXES:
            continue
        if relative == INDEX_RELATIVE_PATH or ".locks" in relative.parts:
            continue
        if relative.name in {"manifest.yaml", "document-id-registry.json", "onboarding-checkpoint.json"}:
            continue
        if _is_legacy_document(path):
            paths.append(path)

    specs_dir = project_root / "docs" / "specs"
    if specs_dir.is_dir():
        for path in specs_dir.rglob("*.md"):
            relative = path.relative_to(project_root)
            if path.is_symlink():
                raise ValueError(f"legacy snapshot refuses symlinks: {relative}")
            if _is_legacy_document(path):
                paths.append(path)
    return sorted(set(paths), key=lambda item: item.relative_to(project_root).as_posix())


def build_entries(project_root: Path) -> list[dict[str, object]]:
    project_root = Path(project_root).resolve()
    entries: list[dict[str, object]] = []
    for path in eligible_legacy_paths(project_root):
        relative = path.relative_to(project_root).as_posix()
        canonical_id = _canonical_id_for(path)
        found_ids = extract_task_ids(relative) + extract_feature_ids(relative)
        ids = list(dict.fromkeys(([canonical_id] if canonical_id else []) + found_ids))
        schema_version = _schema_version_for(path)
        entries.append(
            {
                "path": relative,
                "kind": _kind_for(path),
                "id": canonical_id,
                "schema_version": schema_version,
                "document_ids": ids,
                "sha256": _sha256(path),
            }
        )
    return entries


def render_snapshot(entries: list[dict[str, object]], *, created_by: str) -> str:
    captured_at = utc_now()
    lines = [
        "kind: legacy-document-index",
        "schema_version: 1",
        f"captured_at: {captured_at}",
        f"policy_effective_at: {captured_at}",
        f"created_by: {json.dumps(created_by, ensure_ascii=False)}",
        f"document_count: {len(entries)}",
        "documents:" if entries else "documents: []",
    ]
    if entries:
        lines.extend(
            "  - " + json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            for entry in entries
        )
    return "\n".join(lines) + "\n"


def load_snapshot(path: Path) -> dict[str, object]:
    fields = read_mapping_list_yaml(path, list_key="documents")
    raw_documents = fields.get("documents", [])
    if not isinstance(raw_documents, list):
        raise ValueError(f"legacy snapshot documents must be a list: {path}")
    documents: list[dict[str, object]] = []
    for raw in raw_documents:
        if isinstance(raw, dict):
            entry = raw
        else:
            try:
                entry = json.loads(str(raw))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid legacy snapshot entry in {path}") from exc
        if not isinstance(entry, dict) or "path" not in entry:
            raise ValueError(f"invalid legacy snapshot entry in {path}: {entry}")
        documents.append(entry)
    fields["documents"] = documents
    required = {"kind", "schema_version", "captured_at", "policy_effective_at", "documents"}
    missing = sorted(required - fields.keys())
    if missing:
        raise ValueError(f"legacy snapshot is missing required fields in {path}: {', '.join(missing)}")
    if clean_value(fields.get("kind")) != "legacy-document-index":
        raise ValueError(f"invalid legacy snapshot kind in {path}")
    try:
        schema_version = int(clean_value(fields.get("schema_version")))
    except ValueError as exc:
        raise ValueError(f"invalid legacy snapshot schema_version in {path}") from exc
    if schema_version < 1:
        raise ValueError(f"invalid legacy snapshot schema_version in {path}")
    for field_name in ("captured_at", "policy_effective_at"):
        value = clean_value(fields.get(field_name))
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value):
            raise ValueError(f"invalid legacy snapshot {field_name} in {path}")
    seen_paths: set[str] = set()
    for entry in documents:
        entry_path = clean_value(entry.get("path"))
        if not entry_path or not clean_value(entry.get("kind")):
            raise ValueError(f"legacy snapshot entry is missing path or kind in {path}: {entry}")
        if entry_path in seen_paths:
            raise ValueError(f"legacy snapshot contains duplicate path in {path}: {entry_path}")
        seen_paths.add(entry_path)
    return fields


def create_snapshot(project_root: Path, *, created_by: str, lock_timeout: float = 10.0) -> tuple[Path, bool]:
    project_root = Path(project_root).resolve()
    state_dir = project_root / ".claw"
    if not state_dir.is_dir():
        raise ValueError(f".claw state directory does not exist: {state_dir}")
    destination = project_root / INDEX_RELATIVE_PATH
    lock_path = state_dir / ".locks" / "legacy-snapshot.lock"
    with file_lock(lock_path, timeout=lock_timeout):
        if destination.exists():
            load_snapshot(destination)
            return destination, False
        entries = build_entries(project_root)
        exclusive_create_text(destination, render_snapshot(entries, created_by=created_by))
    return destination, True


def verify_snapshot(project_root: Path, snapshot_path: Path | None = None) -> dict[str, list[str]]:
    project_root = Path(project_root).resolve()
    path = snapshot_path or project_root / INDEX_RELATIVE_PATH
    snapshot = load_snapshot(path)
    stored_entries = {str(entry["path"]): entry for entry in snapshot["documents"] if isinstance(entry, dict)}
    current_entries = {str(entry["path"]): entry for entry in build_entries(project_root)}
    stored_paths = set(stored_entries)
    current_paths = set(current_entries)
    changed = sorted(
        path_value
        for path_value in stored_paths & current_paths
        if stored_entries[path_value].get("sha256") != current_entries[path_value].get("sha256")
    )
    return {
        "missing_paths": sorted(stored_paths - current_paths),
        "new_paths": sorted(current_paths - stored_paths),
        "changed_paths": changed,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create or verify an immutable .claw legacy document boundary.")
    parser.add_argument("project_root", nargs="?", default=".", help="Project root containing .claw.")
    parser.add_argument("--created-by", default="snapshot-legacy-documents")
    parser.add_argument("--lock-timeout", type=float, default=10.0)
    parser.add_argument("--verify", action="store_true", help="Compare current paths with the existing snapshot.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    project_root = Path(args.project_root).resolve()
    if args.verify:
        result: dict[str, object] = verify_snapshot(project_root)
        changed = any(result.values())
        result["status"] = "drift" if changed else "unchanged"
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(result["status"])
            for key in ("missing_paths", "new_paths", "changed_paths"):
                for path in result[key]:  # type: ignore[index]
                    print(f"- {key}: {path}")
        return 1 if changed else 0

    destination, created = create_snapshot(
        project_root,
        created_by=args.created_by,
        lock_timeout=args.lock_timeout,
    )
    result = {
        "status": "created" if created else "unchanged",
        "path": destination.relative_to(project_root).as_posix(),
        "document_count": len(load_snapshot(destination)["documents"]),
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"{result['status']}: {result['path']} ({result['document_count']} documents)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
