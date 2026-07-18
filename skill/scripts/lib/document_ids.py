from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .atomic_io import atomic_write_text, exclusive_create_text, file_lock
from .state_io import read_front_matter, utc_now


LEGACY_TASK_ID_PATTERN = r"TASK-[0-9]+"
LEGACY_FEATURE_ID_PATTERN = r"FEAT-[0-9]+"
V5_SEQUENCE_PATTERN = r"(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})"
V5_TASK_ID_PATTERN = rf"TASK-[a-z0-9]+(?:-[a-z0-9]+)*-{V5_SEQUENCE_PATTERN}"
V5_FEATURE_ID_PATTERN = rf"FEAT-[a-z0-9]+(?:-[a-z0-9]+)*-{V5_SEQUENCE_PATTERN}"
TASK_ID_PATTERN = rf"(?:{LEGACY_TASK_ID_PATTERN}|{V5_TASK_ID_PATTERN})"
FEATURE_ID_PATTERN = rf"(?:{LEGACY_FEATURE_ID_PATTERN}|{V5_FEATURE_ID_PATTERN})"

LEGACY_TASK_ID_RE = re.compile(rf"^{LEGACY_TASK_ID_PATTERN}$")
LEGACY_FEATURE_ID_RE = re.compile(rf"^{LEGACY_FEATURE_ID_PATTERN}$")
V5_TASK_ID_RE = re.compile(rf"^{V5_TASK_ID_PATTERN}$")
V5_FEATURE_ID_RE = re.compile(rf"^{V5_FEATURE_ID_PATTERN}$")
TASK_ID_RE = re.compile(rf"^{TASK_ID_PATTERN}$")
FEATURE_ID_RE = re.compile(rf"^{FEATURE_ID_PATTERN}$")
TASK_ID_SEARCH_RE = re.compile(
    rf"(?<![A-Za-z0-9])(?:TASK-[a-z0-9]+(?:-[a-z0-9]+)*?-{V5_SEQUENCE_PATTERN}|TASK-[0-9]+(?!-[0-9]{{3}}(?![0-9])))(?![A-Za-z0-9])"
)
FEATURE_ID_SEARCH_RE = re.compile(
    rf"(?<![A-Za-z0-9])(?:FEAT-[a-z0-9]+(?:-[a-z0-9]+)*?-{V5_SEQUENCE_PATTERN}|FEAT-[0-9]+(?!-[0-9]{{3}}(?![0-9])))(?![A-Za-z0-9])"
)
TASK_BOARD_HEADER_RE = re.compile(rf"^###\s+({TASK_ID_PATTERN})\s+-\s+(.+?)\s*$")


@dataclass(frozen=True)
class DocumentAllocation:
    kind: str
    document_id: str
    owner_slug: str
    number: int
    path: Path


def normalize_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    normalized = re.sub(r"-+", "-", normalized)
    if not normalized:
        raise ValueError("value cannot be normalized to a safe lowercase slug")
    return normalized


def is_task_id(value: str) -> bool:
    return bool(TASK_ID_RE.fullmatch(value.strip()))


def is_feature_id(value: str) -> bool:
    return bool(FEATURE_ID_RE.fullmatch(value.strip()))


def is_legacy_id(value: str) -> bool:
    cleaned = value.strip()
    return bool(LEGACY_TASK_ID_RE.fullmatch(cleaned) or LEGACY_FEATURE_ID_RE.fullmatch(cleaned))


def is_v5_id(value: str) -> bool:
    cleaned = value.strip()
    return bool(V5_TASK_ID_RE.fullmatch(cleaned) or V5_FEATURE_ID_RE.fullmatch(cleaned))


def extract_task_ids(text: str) -> list[str]:
    return list(dict.fromkeys(match.group(0) for match in TASK_ID_SEARCH_RE.finditer(text)))


def extract_feature_ids(text: str) -> list[str]:
    return list(dict.fromkeys(match.group(0) for match in FEATURE_ID_SEARCH_RE.finditer(text)))


def document_id_from_path(path: Path, kind: str, metadata_id: str | None = None) -> str:
    """Resolve a canonical ID from front matter or a legacy/v5 document filename."""

    expected = TASK_ID_RE if kind == "task" else FEATURE_ID_RE
    if metadata_id:
        cleaned = metadata_id.strip()
        if not expected.fullmatch(cleaned):
            raise ValueError(f"invalid {kind} id: {metadata_id}")
        stem = Path(path).stem
        if stem != cleaned and not stem.startswith(f"{cleaned}-"):
            raise ValueError(f"filename `{stem}` does not start with canonical id `{cleaned}`")
        return cleaned

    matches = extract_task_ids(Path(path).stem) if kind == "task" else extract_feature_ids(Path(path).stem)
    if not matches:
        raise ValueError(f"cannot resolve {kind} id from filename: {path}")
    return matches[0]


def _registry_path(project_root: Path) -> Path:
    return project_root / ".claw" / "document-id-registry.json"


def _load_registry(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"schema_version": 1, "allocations": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid document id registry: {path}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError(f"unsupported document id registry: {path}")
    allocations = data.setdefault("allocations", [])
    if not isinstance(allocations, list):
        raise ValueError(f"invalid allocations in document id registry: {path}")
    return data


def _scan_max_number(project_root: Path, kind: str, owner_slug: str) -> int:
    if kind == "feature":
        paths = (project_root / "docs" / "specs").glob("FEAT-*.md")
        id_key = "feature_id"
        matcher = V5_FEATURE_ID_RE
    else:
        paths = (project_root / ".claw" / "tasks").glob("TASK-*.md")
        id_key = "task_id"
        matcher = V5_TASK_ID_RE

    highest = 0
    prefix = f"{'FEAT' if kind == 'feature' else 'TASK'}-{owner_slug}-"
    for path in paths:
        document_id = ""
        try:
            fields, _body = read_front_matter(path)
            raw_id = fields.get(id_key)
            document_id = document_id_from_path(path, kind, str(raw_id) if raw_id else None)
        except (OSError, ValueError):
            # A custom document may use richer YAML than the dependency-free
            # reader supports. Its canonical filename still reserves the ID.
            try:
                document_id = document_id_from_path(path, kind)
            except ValueError:
                continue
        if not matcher.fullmatch(document_id) or not document_id.startswith(prefix):
            continue
        highest = max(highest, int(document_id.rsplit("-", 1)[1]))
    return highest


def _registry_max_number(registry: dict[str, object], kind: str, owner_slug: str) -> int:
    highest = 0
    for raw_entry in registry.get("allocations", []):
        if not isinstance(raw_entry, dict):
            continue
        if raw_entry.get("kind") != kind or raw_entry.get("owner_slug") != owner_slug:
            continue
        try:
            highest = max(highest, int(raw_entry.get("number", 0)))
        except (TypeError, ValueError):
            continue
    return highest


def reserve_document(
    project_root: Path,
    *,
    kind: str,
    owner: str,
    description: str,
    content: str,
    lock_timeout: float = 10.0,
) -> DocumentAllocation:
    """Allocate a personal, monotonic ID and exclusively create its document."""

    if kind not in {"feature", "task"}:
        raise ValueError("kind must be `feature` or `task`")
    project_root = Path(project_root).resolve()
    state_dir = project_root / ".claw"
    if not state_dir.is_dir():
        raise ValueError(f".claw state directory does not exist: {state_dir}")
    owner_slug = normalize_slug(owner)
    description_slug = normalize_slug(description)
    registry_path = _registry_path(project_root)
    lock_path = state_dir / ".locks" / "document-id.lock"

    with file_lock(lock_path, timeout=lock_timeout):
        registry = _load_registry(registry_path)
        highest = max(
            _scan_max_number(project_root, kind, owner_slug),
            _registry_max_number(registry, kind, owner_slug),
        )
        number = highest + 1
        if number > 999:
            raise ValueError(f"personal {kind} sequence exhausted for `{owner_slug}`")
        prefix = "FEAT" if kind == "feature" else "TASK"
        document_id = f"{prefix}-{owner_slug}-{number:03d}"
        directory = project_root / "docs" / "specs" if kind == "feature" else state_dir / "tasks"
        path = directory / f"{document_id}-{description_slug}.md"

        rendered = content.replace("{{DOCUMENT_ID}}", document_id)
        rendered = rendered.replace("{{OWNER_SLUG}}", owner_slug)
        rendered = rendered.replace("{{DESCRIPTION_SLUG}}", description_slug)
        exclusive_create_text(path, rendered)

        allocations = registry["allocations"]
        assert isinstance(allocations, list)
        allocations.append(
            {
                "kind": kind,
                "document_id": document_id,
                "owner_slug": owner_slug,
                "number": number,
                "path": path.relative_to(project_root).as_posix(),
                "allocated_at": utc_now(),
            }
        )
        atomic_write_text(registry_path, json.dumps(registry, ensure_ascii=False, indent=2) + "\n")

    return DocumentAllocation(kind, document_id, owner_slug, number, path)
