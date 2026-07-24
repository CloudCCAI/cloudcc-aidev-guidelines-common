#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from lib.devops_assets import (
    DevOpsAssetContract,
    contract_from_catalog,
    normalize_environment_names,
)
from lib.language import PENDING_LANGUAGE, PRIMARY_LANGUAGE, READABLE_LANGUAGES
from lib.project_docs_html import validate_project_documents


EXPECTED_KINDS = {
    "current-status.md": "current-status",
    "goals.md": "goals",
    "decisions.md": "decisions",
    "issue-list.md": "issue-list",
    "task-board.md": "task-board",
    "task-archive.md": "task-archive",
    "test-report.md": "test-report",
    "devops.md": "devops",
}
OPTIONAL_STATE_KINDS = {
    "integration-queue.md": "integration-queue",
    "issue-archive.md": "issue-archive",
    "team-status.md": "team-status",
    "test-archive.md": "test-archive",
    "test-report-archive.md": "test-report-archive",
}
STATE_KINDS = {**EXPECTED_KINDS, **OPTIONAL_STATE_KINDS}
SKILL_REPO_URL = "https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common/tree/main/skill"
GUIDANCE_MARKER_BEGIN = "<!-- cc-aidev-guidelines-common:begin -->"
GUIDANCE_MARKER_END = "<!-- cc-aidev-guidelines-common:end -->"
GUIDANCE_REQUIRED_FILES = ("README.md", "AGENTS.md")

REQUIRED_FRONTMATTER_FIELDS = {"kind", "version", "updated_at", "updated_by"}
CURRENT_STATUS_REQUIRED_FIELDS = {"phase", "active_task", "next_action"}
TASK_STATUSES = {
    "todo",
    "ready",
    "in_progress",
    "blocked",
    "review",
    "done",
    "canceled",
}
OWNER_ROLES = {
    "backend-agent",
    "frontend-agent",
    "fullstack-agent",
    "qa-agent",
    "release-agent",
    "project-manager",
    "integration-agent",
    "human",
    "shared",
    "unassigned",
}
TOUCH_POLICIES = {
    "exclusive",
    "shared",
    "read_only",
}
SCOPE_MODES = {
    "exact_files",
    "task_bounded_broad_code",
}
INTEGRATION_QUEUE_STATUSES = {
    "not_started",
    "collecting",
    "merging",
    "verifying",
    "ready",
    "blocked",
    "completed",
}
DEVELOPER_STATUSES = {
    "active",
    "suspended",
    "revoked",
    "expired",
}
ASSIGNMENT_STATUSES = {
    "active",
    "paused",
    "revoked",
    "expired",
    "completed",
}
FEATURE_SPEC_STATUSES = {
    "draft",
    "in_design",
    "approved",
    "in_implementation",
    "implemented",
    "verified",
    "archived",
}
CONFIRMED_FEATURE_STATUSES = {"approved", "in_implementation", "implemented", "verified"}
PROJECT_BASELINE_STATUSES = {
    "draft",
    "adopting",
    "active_reference",
    "verified",
    "archived",
}
TASK_BOARD_COMPLETED_LIMIT = 5
CURRENT_STATUS_LINE_LIMIT = 60
TASK_CARD_LINE_LIMIT = 20
TASK_STATUS_LINE_LIMIT = 120
TEST_REPORT_LINE_LIMIT = 150
TEST_REPORT_RECENT_LIMIT = 5
TEST_REPORT_RECENT_SECTIONS = {"Recent Test Records", "最近测试记录"}
ISSUE_TERMINAL_STATUSES = {"verified", "closed"}
ISSUE_RECENT_CLOSED_LIMIT = 5
ISSUE_RECENT_CLOSED_SECTIONS = {"Recently Closed Issues", "最近关闭问题"}
ISSUE_CARD_RE = re.compile(r"^###\s+(ISSUE-[A-Za-z0-9-]+)\s+[—-]\s+(.+?)\s*$")
ISSUE_STATUS_RE = re.compile(
    r"(?:状态：|status:\s*)`(open|in_progress|blocked|fixed|verified|closed)`",
    re.IGNORECASE,
)
FORBIDDEN_CURRENT_STATUS_HEADINGS = {
    "本次会话进展",
    "修改文件",
    "已验证事实",
    "相关状态文件",
    "相关设计文档",
    "Session History",
    "Changed Files",
    "Verified Facts",
}
ONBOARDING_INCOMPLETE_SENTINEL = "<!-- cc-aidev:onboarding-incomplete -->"
TIMESTAMP_RE = re.compile(
    r"^(?:[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"|[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z)$"
)
DOCUMENT_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LEGACY_TASK_ID_PATTERN = r"TASK-[0-9]+"
V5_TASK_ID_PATTERN = r"TASK-[a-z0-9]+(?:-[a-z0-9]+)*-(?!000)[0-9]{3}"
TASK_ID_PATTERN = rf"(?:{LEGACY_TASK_ID_PATTERN}|{V5_TASK_ID_PATTERN})"
LEGACY_FEATURE_ID_PATTERN = r"FEAT-[0-9]+"
V5_FEATURE_ID_PATTERN = r"FEAT-[a-z0-9]+(?:-[a-z0-9]+)*-(?!000)[0-9]{3}"
FEATURE_ID_PATTERN = rf"(?:{LEGACY_FEATURE_ID_PATTERN}|{V5_FEATURE_ID_PATTERN})"
TASK_ID_RE = re.compile(rf"^{TASK_ID_PATTERN}$")
LEGACY_TASK_ID_RE = re.compile(rf"^{LEGACY_TASK_ID_PATTERN}$")
V5_TASK_ID_RE = re.compile(rf"^{V5_TASK_ID_PATTERN}$")
FEATURE_ID_RE = re.compile(rf"^{FEATURE_ID_PATTERN}$")
LEGACY_FEATURE_ID_RE = re.compile(rf"^{LEGACY_FEATURE_ID_PATTERN}$")
V5_FEATURE_ID_RE = re.compile(rf"^{V5_FEATURE_ID_PATTERN}$")
TASK_HEADER_RE = re.compile(rf"^###\s+({TASK_ID_PATTERN})\s+-\s+(.+?)\s*$")
TASK_FIELD_RE = re.compile(r"^- ([a-z_]+):\s*(.+?)\s*$")
SECTION_HEADER_RE = re.compile(r"^##\s+(.+?)\s*$")
TEST_REPORT_STATUS_RE = re.compile(r"- (?:状态|Status)[：:]\s*`([^`]+)`", re.IGNORECASE)
SIMPLE_YAML_FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$")

V5_INIT_STATUSES = {
    "not_started",
    "in_progress",
    "awaiting_confirmation",
    "complete",
    "needs_review",
}
V5_INITIALIZATION_STATUSES = {"in_progress", "ready", "needs_review"}
V5_PROJECT_STATE_MODES = {"greenfield", "brownfield"}
V5_PROJECT_MODES = {*V5_PROJECT_STATE_MODES, "not_applicable", "pending"}
V5_MODULES = {"project_state", "collaboration_gate", "change_review"}
V5_LANGUAGES = set(READABLE_LANGUAGES)
ACTIVE_TASK_SECTIONS = {"Active Tasks", "活跃任务"}
COMPLETED_TASK_SECTIONS = {"Completed Tasks", "已完成任务"}
ARCHIVED_TASK_SECTIONS = {"Archived Tasks", "已归档任务"}
V5_COMMON_CORE_FIELDS = {
    "kind",
    "schema_version",
    "init_status",
    "init_completed_at",
    "init_confirmed_by",
    "updated_at",
    "updated_by",
}
DEFAULT_CATALOG_CANDIDATES = (
    "state-catalog.json",
    "schemas/state-catalog.json",
    "references/state-catalog.json",
)


@dataclass
class ValidationResult:
    state_dir: Path
    mode: str
    strict_v5: bool = False
    catalog_path: Path | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors

    def as_json(self) -> dict[str, object]:
        return {
            "status": "passed" if self.passed else "failed",
            "mode": self.mode,
            "strict_v5": self.strict_v5,
            "state_dir": str(self.state_dir),
            "catalog_path": str(self.catalog_path) if self.catalog_path else None,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
            },
        }


def clean_value(value: object) -> str:
    if value is None:
        return ""
    cleaned = str(value).strip().strip('"').strip("'")
    if cleaned.startswith("`") and cleaned.endswith("`") and len(cleaned) >= 2:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def is_placeholder_value(value: str) -> bool:
    cleaned = clean_value(value)
    if not cleaned:
        return True
    if "{{" in cleaned or "}}" in cleaned:
        return True
    if "YYYY-MM-DD" in cleaned or "HH:MM:SS" in cleaned:
        return True
    if "..." in cleaned:
        return True
    if cleaned.startswith("[") and cleaned.endswith("]"):
        return True
    return False


def is_empty_reference(value: str) -> bool:
    cleaned = clean_value(value).lower()
    return cleaned in {"", "none", "null", "n/a", "na", "not_applicable"}


def read_simple_yaml(path: Path) -> tuple[dict[str, object], list[str]]:
    parsed: dict[str, object] = {}
    errors: list[str] = []
    current_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if current_key and stripped.startswith("- "):
            current_value = parsed.setdefault(current_key, [])
            if isinstance(current_value, list):
                current_value.append(clean_value(stripped[2:]))
            continue

        match = SIMPLE_YAML_FIELD_RE.match(stripped)
        if not match:
            current_key = None
            continue
        key = match.group(1).strip()
        value = clean_value(match.group(2))
        if value == "":
            parsed[key] = []
            current_key = key
        else:
            parsed[key] = value
            current_key = None

    if not parsed:
        errors.append(f"{path}: no top-level YAML fields found")

    return parsed, errors


class SimpleYamlError(ValueError):
    pass


def strip_yaml_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if char == "\\" and quote == '"':
            escaped = True
            continue
        if char in {"'", '"'}:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
            continue
        if char == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.rstrip()


def split_inline_yaml(value: str) -> list[str]:
    items: list[str] = []
    quote: str | None = None
    depth = 0
    start = 0
    for index, char in enumerate(value):
        if char in {"'", '"'}:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
            continue
        if quote is not None:
            continue
        if char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
        elif char == "," and depth == 0:
            items.append(value[start:index].strip())
            start = index + 1
    items.append(value[start:].strip())
    return [item for item in items if item]


def parse_yaml_scalar(value: str) -> object:
    cleaned = strip_yaml_comment(value).strip()
    if not cleaned:
        return ""
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {"'", '"'}:
        if cleaned[0] == '"':
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass
        return cleaned[1:-1].replace("''", "'")
    lowered = cleaned.lower()
    if lowered in {"true", "yes", "on"}:
        return True
    if lowered in {"false", "no", "off"}:
        return False
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?[0-9]+", cleaned):
        try:
            return int(cleaned)
        except ValueError:
            pass
    if cleaned.startswith("[") and cleaned.endswith("]"):
        inner = cleaned[1:-1].strip()
        if not inner:
            return []
        return [parse_yaml_scalar(item) for item in split_inline_yaml(inner)]
    if cleaned.startswith("{") and cleaned.endswith("}"):
        inner = cleaned[1:-1].strip()
        result: dict[str, object] = {}
        if not inner:
            return result
        for item in split_inline_yaml(inner):
            if ":" not in item:
                raise SimpleYamlError(f"invalid inline mapping item `{item}`")
            key, item_value = item.split(":", 1)
            result[clean_value(key)] = parse_yaml_scalar(item_value)
        return result
    return cleaned


def yaml_mapping_pair(content: str, line_number: int) -> tuple[str, str]:
    quote: str | None = None
    for index, char in enumerate(content):
        if char in {"'", '"'}:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
            continue
        if char == ":" and quote is None:
            key = content[:index].strip()
            if not key:
                break
            return clean_value(key), content[index + 1 :].strip()
    raise SimpleYamlError(f"line {line_number}: expected `key: value`")


def parse_yaml_document(text: str) -> dict[str, object]:
    tokens: list[tuple[int, str, int]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            raise SimpleYamlError(f"line {line_number}: tabs are not supported for indentation")
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped == "---":
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        content = strip_yaml_comment(raw_line[indent:]).rstrip()
        if content:
            tokens.append((indent, content, line_number))

    if not tokens:
        return {}

    def parse_block(index: int, indent: int) -> tuple[object, int]:
        if index >= len(tokens):
            return {}, index
        is_list = tokens[index][1].startswith("- ") or tokens[index][1] == "-"
        container: object = [] if is_list else {}

        while index < len(tokens):
            current_indent, content, line_number = tokens[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise SimpleYamlError(f"line {line_number}: unexpected indentation")

            if is_list:
                if not (content.startswith("- ") or content == "-"):
                    break
                assert isinstance(container, list)
                item_text = content[1:].strip()
                index += 1
                if not item_text:
                    if index < len(tokens) and tokens[index][0] > indent:
                        item, index = parse_block(index, tokens[index][0])
                    else:
                        item = None
                    container.append(item)
                    continue

                if item_text.startswith("{") and item_text.endswith("}"):
                    container.append(parse_yaml_scalar(item_text))
                elif ":" in item_text:
                    key, raw_value = yaml_mapping_pair(item_text, line_number)
                    item_map: dict[str, object] = {}
                    if raw_value:
                        item_map[key] = parse_yaml_scalar(raw_value)
                    elif index < len(tokens) and tokens[index][0] > indent:
                        item_map[key], index = parse_block(index, tokens[index][0])
                    else:
                        item_map[key] = {}

                    while index < len(tokens) and tokens[index][0] > indent:
                        child_indent = tokens[index][0]
                        child, new_index = parse_block(index, child_indent)
                        if not isinstance(child, dict):
                            raise SimpleYamlError(
                                f"line {tokens[index][2]}: list mapping continuation must be a mapping"
                            )
                        item_map.update(child)
                        index = new_index
                    container.append(item_map)
                else:
                    container.append(parse_yaml_scalar(item_text))
                continue

            if content.startswith("- ") or content == "-":
                break
            assert isinstance(container, dict)
            key, raw_value = yaml_mapping_pair(content, line_number)
            index += 1
            if raw_value:
                container[key] = parse_yaml_scalar(raw_value)
            elif index < len(tokens) and tokens[index][0] > indent:
                container[key], index = parse_block(index, tokens[index][0])
            else:
                container[key] = {}

        return container, index

    parsed, end_index = parse_block(0, tokens[0][0])
    if end_index != len(tokens):
        _indent, _content, line_number = tokens[end_index]
        raise SimpleYamlError(f"line {line_number}: could not parse YAML content")
    if not isinstance(parsed, dict):
        raise SimpleYamlError("top-level YAML document must be a mapping")
    return parsed


def read_yaml_document(path: Path) -> tuple[dict[str, object], list[str]]:
    try:
        return parse_yaml_document(path.read_text(encoding="utf-8")), []
    except (OSError, UnicodeError, SimpleYamlError) as exc:
        return {}, [f"{path}: invalid YAML: {exc}"]


def read_front_matter_yaml(path: Path) -> tuple[dict[str, object], str, list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}, text, [f"{path}: missing YAML front matter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, text, [f"{path}: unclosed YAML front matter"]
    try:
        parsed = parse_yaml_document("\n".join(lines[1:end]))
    except SimpleYamlError as exc:
        return {}, text, [f"{path}: invalid YAML front matter: {exc}"]
    return parsed, "\n".join(lines[end + 1 :]), []


def read_front_matter(path: Path) -> tuple[dict[str, str], str, list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if len(lines) < 3 or lines[0].strip() != "---":
        return {}, text, [f"{path.name}: missing YAML front matter"]

    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, text, [f"{path.name}: unclosed YAML front matter"]

    raw_fields = lines[1:end]
    parsed: dict[str, str] = {}
    errors: list[str] = []

    for line in raw_fields:
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"{path.name}: invalid front matter line `{line}`")
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = clean_value(value)

    body = "\n".join(lines[end + 1 :])
    return parsed, body, errors


def validate_timestamp(path: Path, front_matter: dict[str, str], errors: list[str]) -> None:
    timestamp = front_matter.get("updated_at", "")
    if not TIMESTAMP_RE.match(timestamp):
        errors.append(f"{path.name}: invalid `updated_at` format `{timestamp}`")


def validate_common_front_matter(path: Path, front_matter: dict[str, str], errors: list[str]) -> None:
    missing = REQUIRED_FRONTMATTER_FIELDS - front_matter.keys()
    for field in sorted(missing):
        errors.append(f"{path.name}: missing front matter field `{field}`")

    for field in REQUIRED_FRONTMATTER_FIELDS & front_matter.keys():
        if is_placeholder_value(front_matter[field]):
            errors.append(f"{path.name}: unresolved placeholder in `{field}`")

    expected_kind = STATE_KINDS[path.name]
    actual_kind = front_matter.get("kind")
    if actual_kind and actual_kind != expected_kind:
        errors.append(f"{path.name}: expected kind `{expected_kind}`, got `{actual_kind}`")

    validate_timestamp(path, front_matter, errors)


def validate_current_status(path: Path, front_matter: dict[str, str], body: str, errors: list[str]) -> None:
    total_lines = len(path.read_text(encoding="utf-8").splitlines())
    if total_lines > CURRENT_STATUS_LINE_LIMIT:
        errors.append(
            f"{path.name}: has {total_lines} lines; keep the hot index under {CURRENT_STATUS_LINE_LIMIT} lines"
        )

    for raw_line in body.splitlines():
        stripped = raw_line.strip()
        if not stripped.startswith("## "):
            continue
        heading = stripped[3:].strip()
        if heading in FORBIDDEN_CURRENT_STATUS_HEADINGS:
            errors.append(
                f"{path.name}: forbidden hot-file history section `{heading}`; move details to task status, specs, or test-report"
            )

    for field in CURRENT_STATUS_REQUIRED_FIELDS:
        value = front_matter.get(field)
        if value is None:
            errors.append(f"{path.name}: missing front matter field `{field}`")
            continue
        if is_placeholder_value(value):
            errors.append(f"{path.name}: unresolved placeholder in `{field}`")

    if "task_board" not in front_matter:
        errors.append(f"{path.name}: missing `read_next.task_board` hint")


def parse_task_cards(body: str) -> list[dict[str, object]]:
    tasks: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    current_section = ""
    lines = body.splitlines()

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip()
        section_match = SECTION_HEADER_RE.match(line)
        if section_match:
            if current is not None:
                current["line_count"] = line_number - int(current["start_line"])
                tasks.append(current)
                current = None
            current_section = section_match.group(1).strip()

        header_match = TASK_HEADER_RE.match(line)
        if header_match:
            if current is not None:
                current["line_count"] = line_number - int(current["start_line"])
                tasks.append(current)
            current = {
                "id": header_match.group(1),
                "title": header_match.group(2).strip(),
                "section": current_section,
                "fields": {},
                "start_line": line_number,
                "line_count": 1,
            }
            continue

        if current is None:
            continue

        field_match = TASK_FIELD_RE.match(line.strip())
        if field_match:
            fields = current["fields"]
            assert isinstance(fields, dict)
            fields[field_match.group(1)] = clean_value(field_match.group(2))

    if current is not None:
        current["line_count"] = len(lines) - int(current["start_line"]) + 1
        tasks.append(current)

    return tasks


def validate_delivery_doc(path: Path) -> list[str]:
    errors: list[str] = []
    front_matter, _body, fm_errors = read_front_matter(path)
    errors.extend(fm_errors)

    if not front_matter:
        return errors

    kind = front_matter.get("kind", "")
    required_fields = {"kind", "title", "status", "updated_at", "updated_by"}
    if kind == "feature-spec":
        required_fields.add("feature_id")
    missing = required_fields - front_matter.keys()
    for field in sorted(missing):
        errors.append(f"{path}: missing front matter field `{field}`")

    if kind not in {"feature-spec", "project-baseline"}:
        errors.append(f"{path}: expected kind `feature-spec` or `project-baseline`, got `{kind}`")

    status = front_matter.get("status", "")
    if kind == "feature-spec" and status and status not in FEATURE_SPEC_STATUSES:
        errors.append(f"{path}: invalid feature spec status `{status}`")
    if kind == "project-baseline" and status and status not in PROJECT_BASELINE_STATUSES:
        errors.append(f"{path}: invalid project baseline status `{status}`")

    for field in ("title", "updated_by"):
        value = front_matter.get(field, "")
        if value and is_placeholder_value(value):
            errors.append(f"{path}: unresolved placeholder in `{field}`")

    if kind == "feature-spec":
        feature_id = front_matter.get("feature_id", "")
        if feature_id and is_placeholder_value(feature_id):
            errors.append(f"{path}: unresolved placeholder in `feature_id`")
        elif feature_id and not FEATURE_ID_RE.fullmatch(feature_id):
            errors.append(f"{path}: invalid feature_id `{feature_id}`")
        elif feature_id and V5_FEATURE_ID_RE.fullmatch(feature_id):
            if path.stem != feature_id and not path.stem.startswith(f"{feature_id}-"):
                errors.append(f"{path}: filename should start with feature_id `{feature_id}`")

    validate_timestamp(path, front_matter, errors)
    return errors


def validate_task_board(path: Path, body: str, project_root: Path) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    tasks = parse_task_cards(body)
    completed_task_count = 0

    for task in tasks:
        task_id = str(task["id"])
        title = str(task["title"]).strip()
        section = str(task.get("section", "")).strip()
        line_count = int(task.get("line_count", 0))
        fields = task["fields"]
        assert isinstance(fields, dict)

        if line_count > TASK_CARD_LINE_LIMIT:
            errors.append(
                f"{path.name}: task `{task_id}` has {line_count} lines; keep task-board cards under {TASK_CARD_LINE_LIMIT} lines and move details to `.claw/tasks/{task_id}.md`"
            )

        if task_id in seen_ids:
            errors.append(f"{path.name}: duplicate task id `{task_id}`")
        seen_ids.add(task_id)

        if not title:
            errors.append(f"{path.name}: task `{task_id}` is missing a title")

        status = clean_value(str(fields.get("status", "")))
        if not status:
            errors.append(f"{path.name}: task `{task_id}` is missing `status`")
        elif status not in TASK_STATUSES:
            errors.append(f"{path.name}: task `{task_id}` has invalid status `{status}`")

        if section in COMPLETED_TASK_SECTIONS:
            completed_task_count += 1
            if status not in {"done", "canceled"}:
                errors.append(
                    f"{path.name}: task `{task_id}` is in `Completed Tasks` but has status `{status}`"
                )

        if section in ACTIVE_TASK_SECTIONS and status in {"done", "canceled"}:
            errors.append(f"{path.name}: task `{task_id}` is in `Active Tasks` but has terminal status `{status}`")

        task_status_path = clean_value(str(fields.get("task_status_path", "")))
        if section in ACTIVE_TASK_SECTIONS:
            if is_empty_reference(task_status_path):
                errors.append(f"{path.name}: active task `{task_id}` must declare `task_status_path`")
            else:
                resolved_task_status_path = project_root / task_status_path
                if not resolved_task_status_path.exists():
                    errors.append(
                        f"{path.name}: task `{task_id}` references missing task_status_path `{task_status_path}`"
                    )

        owner_role = clean_value(str(fields.get("owner_role", "")))
        if owner_role and owner_role not in OWNER_ROLES:
            errors.append(f"{path.name}: task `{task_id}` has invalid owner_role `{owner_role}`")

        if status == "in_progress" and owner_role in {"", "unassigned"}:
            errors.append(f"{path.name}: task `{task_id}` is in_progress but has no concrete owner_role")

        if status == "blocked":
            blocked_by = clean_value(str(fields.get("blocked_by", ""))).lower()
            depends_on = clean_value(str(fields.get("depends_on", ""))).lower()
            if blocked_by in {"", "none"} and depends_on in {"", "none"}:
                errors.append(f"{path.name}: task `{task_id}` is blocked but has no blocker or dependency")

        spec_path = clean_value(str(fields.get("spec_path", "")))
        if spec_path and spec_path.lower() not in {"none", "n/a"}:
            resolved_spec_path = project_root / spec_path
            if not resolved_spec_path.exists():
                errors.append(f"{path.name}: task `{task_id}` references missing spec `{spec_path}`")
            else:
                errors.extend(validate_delivery_doc(resolved_spec_path))

        touch_policy = clean_value(str(fields.get("touch_policy", "")))
        if touch_policy and touch_policy.lower() not in {"none", "n/a"} and touch_policy not in TOUCH_POLICIES:
            errors.append(f"{path.name}: task `{task_id}` has invalid touch_policy `{touch_policy}`")

        for field_name in ("assignment_path", "integration_queue"):
            reference_path = clean_value(str(fields.get(field_name, "")))
            if is_empty_reference(reference_path):
                continue
            resolved_reference_path = project_root / reference_path
            if not resolved_reference_path.exists():
                errors.append(
                    f"{path.name}: task `{task_id}` references missing {field_name} `{reference_path}`"
                )

    if completed_task_count > TASK_BOARD_COMPLETED_LIMIT:
        errors.append(
            f"{path.name}: `Completed Tasks` has {completed_task_count} task cards; archive the oldest items to `task-archive.md` so at most {TASK_BOARD_COMPLETED_LIMIT} remain"
        )

    return errors


def validate_task_archive(path: Path, body: str) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    tasks = parse_task_cards(body)

    for task in tasks:
        task_id = str(task["id"])
        section = str(task.get("section", "")).strip()
        fields = task["fields"]
        assert isinstance(fields, dict)

        if task_id in seen_ids:
            errors.append(f"{path.name}: duplicate task id `{task_id}`")
        seen_ids.add(task_id)

        status = clean_value(str(fields.get("status", "")))
        if status not in {"done", "canceled"}:
            errors.append(f"{path.name}: archived task `{task_id}` must have status `done` or `canceled`")

        if section and section not in ARCHIVED_TASK_SECTIONS:
            errors.append(f"{path.name}: archived task `{task_id}` must be placed under `Archived Tasks`")

    return errors


def validate_test_report(path: Path, front_matter: dict[str, str], body: str, errors: list[str]) -> None:
    summary_match = TEST_REPORT_STATUS_RE.search(body)
    if not summary_match:
        errors.append(f"{path.name}: missing latest summary status line")
        return

    summary_status = summary_match.group(1)
    last_run_status = front_matter.get("last_run_status", "")
    if last_run_status and summary_status != last_run_status:
        errors.append(
            f"{path.name}: latest summary status `{summary_status}` does not match last_run_status `{last_run_status}`"
        )

    if front_matter.get("schema_version") != "5":
        return
    total_lines = len(path.read_text(encoding="utf-8").splitlines())
    if total_lines > TEST_REPORT_LINE_LIMIT:
        errors.append(
            f"{path.name}: has {total_lines} lines; keep the current report under {TEST_REPORT_LINE_LIMIT} lines and move older evidence to `test-archive.md`"
        )
    lines = body.splitlines()
    recent_count: int | None = None
    for index, line in enumerate(lines):
        if not line.startswith("## ") or line[3:].strip() not in TEST_REPORT_RECENT_SECTIONS:
            continue
        end = next(
            (candidate for candidate in range(index + 1, len(lines)) if lines[candidate].startswith("## ")),
            len(lines),
        )
        recent_count = sum(1 for candidate in lines[index + 1 : end] if candidate.startswith("### "))
        break
    if recent_count is None:
        errors.append(f"{path.name}: missing `最近测试记录` section")
    elif recent_count > TEST_REPORT_RECENT_LIMIT:
        errors.append(
            f"{path.name}: has {recent_count} recent test records; archive older evidence so at most {TEST_REPORT_RECENT_LIMIT} remain"
        )


def parsed_issue_cards(body: str) -> list[tuple[str, str]]:
    lines = body.splitlines()
    headings = [
        index
        for index, line in enumerate(lines)
        if ISSUE_CARD_RE.match(line)
    ]
    cards: list[tuple[str, str]] = []
    for offset, index in enumerate(headings):
        end = headings[offset + 1] if offset + 1 < len(headings) else len(lines)
        next_section = next(
            (
                candidate
                for candidate in range(index + 1, end)
                if lines[candidate].startswith("## ")
            ),
            end,
        )
        heading = ISSUE_CARD_RE.match(lines[index])
        assert heading is not None
        status = ""
        for line in lines[index + 1 : next_section]:
            match = ISSUE_STATUS_RE.search(line)
            if match:
                status = match.group(1).lower()
                break
        cards.append((heading.group(1), status))
    return cards


def validate_issue_list(
    path: Path,
    front_matter: dict[str, str],
    body: str,
    errors: list[str],
) -> None:
    if front_matter.get("schema_version") != "5":
        return
    for issue_id, status in parsed_issue_cards(body):
        if not status:
            errors.append(f"{path.name}: issue `{issue_id}` is missing a recognized status")
        elif status in ISSUE_TERMINAL_STATUSES:
            errors.append(
                f"{path.name}: terminal issue `{issue_id}` must be moved to `issue-archive.md`"
            )

    lines = body.splitlines()
    recent_count: int | None = None
    for index, line in enumerate(lines):
        if not line.startswith("## ") or line[3:].strip() not in ISSUE_RECENT_CLOSED_SECTIONS:
            continue
        end = next(
            (candidate for candidate in range(index + 1, len(lines)) if lines[candidate].startswith("## ")),
            len(lines),
        )
        recent_count = sum(
            1
            for candidate in lines[index + 1 : end]
            if re.match(r"^-\s+`ISSUE-[A-Za-z0-9-]+`", candidate)
        )
        break
    if recent_count is None:
        errors.append(f"{path.name}: missing `最近关闭问题` section")
    elif recent_count > ISSUE_RECENT_CLOSED_LIMIT:
        errors.append(
            f"{path.name}: has {recent_count} recently closed issue summaries; keep at most {ISSUE_RECENT_CLOSED_LIMIT}"
        )


def validate_issue_archive(path: Path, body: str) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for issue_id, status in parsed_issue_cards(body):
        if issue_id in seen_ids:
            errors.append(f"{path.name}: duplicate issue id `{issue_id}`")
        seen_ids.add(issue_id)
        if status not in ISSUE_TERMINAL_STATUSES:
            errors.append(
                f"{path.name}: archived issue `{issue_id}` must have status `verified` or `closed`"
            )
    return errors


def validate_integration_queue(path: Path, front_matter: dict[str, str], errors: list[str]) -> None:
    status = front_matter.get("status", "")
    if status and status not in INTEGRATION_QUEUE_STATUSES:
        errors.append(f"{path.name}: invalid integration queue status `{status}`")

    owner = front_matter.get("integration_owner", "")
    if owner and is_placeholder_value(owner):
        errors.append(f"{path.name}: unresolved placeholder in `integration_owner`")


def validate_developer_record(path: Path) -> list[str]:
    fields, errors = read_simple_yaml(path)
    required_fields = {
        "developer_id",
        "display_name",
        "role",
        "public_key",
        "git_platform",
        "git_username",
        "ssh_signing_key_fingerprint",
        "status",
        "managed_by",
    }

    for field in sorted(required_fields - fields.keys()):
        errors.append(f"{path}: missing developer field `{field}`")

    developer_id = str(fields.get("developer_id", ""))
    if developer_id and not developer_id.startswith(("DEV-", "MANAGER-")):
        errors.append(f"{path}: developer_id should start with `DEV-` or `MANAGER-`")

    role = str(fields.get("role", ""))
    if role and role not in OWNER_ROLES:
        errors.append(f"{path}: invalid role `{role}`")

    status = str(fields.get("status", ""))
    if status and status not in DEVELOPER_STATUSES:
        errors.append(f"{path}: invalid developer status `{status}`")

    public_key = str(fields.get("public_key", ""))
    if public_key and is_placeholder_value(public_key):
        errors.append(f"{path}: unresolved developer field `public_key`")

    managed_by = str(fields.get("managed_by", ""))
    if managed_by and not managed_by.startswith("MANAGER-"):
        errors.append(f"{path}: managed_by should reference `MANAGER-xxx`")

    git_username = str(fields.get("git_username", ""))
    if git_username and is_placeholder_value(git_username):
        errors.append(f"{path}: unresolved developer field `git_username`")

    ssh_fingerprint = str(fields.get("ssh_signing_key_fingerprint", ""))
    if ssh_fingerprint and is_placeholder_value(ssh_fingerprint):
        errors.append(f"{path}: unresolved developer field `ssh_signing_key_fingerprint`")

    for banned_field in ("private_key", "password", "token", "secret", "bearer_token"):
        if banned_field in fields:
            errors.append(f"{path}: must not store `{banned_field}` in repository identity records")

    return errors


def validate_developer_identity_policy(developer_records: list[tuple[Path, dict[str, object]]]) -> list[str]:
    errors: list[str] = []
    by_username: dict[str, list[tuple[Path, dict[str, object]]]] = {}
    by_username_and_key: dict[tuple[str, str], list[tuple[Path, dict[str, object]]]] = {}

    for path, fields in developer_records:
        status = str(fields.get("status", ""))
        if status != "active":
            continue
        username = str(fields.get("git_username", ""))
        fingerprint = str(fields.get("ssh_signing_key_fingerprint", ""))
        if not username:
            continue
        by_username.setdefault(username, []).append((path, fields))
        if fingerprint:
            by_username_and_key.setdefault((username, fingerprint), []).append((path, fields))

    for username, records in by_username.items():
        if len(records) <= 1:
            continue
        fingerprints = [str(fields.get("ssh_signing_key_fingerprint", "")) for _path, fields in records]
        ids = ", ".join(str(fields.get("developer_id", path.stem)) for path, fields in records)
        if len(set(fingerprints)) != len(fingerprints) or any(not item for item in fingerprints):
            errors.append(
                f"developers: git_username `{username}` is reused by active identities `{ids}` without distinct ssh_signing_key_fingerprint values"
            )
            continue
        missing_exceptions = [
            str(fields.get("developer_id", path.stem))
            for path, fields in records
            if is_empty_reference(str(fields.get("role_sharing_exception", "")))
        ]
        if missing_exceptions:
            errors.append(
                f"developers: git_username `{username}` is reused but identities `{', '.join(missing_exceptions)}` are missing role_sharing_exception"
            )

    for (username, fingerprint), records in by_username_and_key.items():
        if len(records) <= 1:
            continue
        has_manager = any(str(fields.get("developer_id", "")).startswith("MANAGER-") for _path, fields in records)
        has_developer = any(str(fields.get("developer_id", "")).startswith("DEV-") for _path, fields in records)
        if has_manager and has_developer:
            ids = ", ".join(str(fields.get("developer_id", path.stem)) for path, fields in records)
            errors.append(
                f"developers: git_username `{username}` and ssh_signing_key_fingerprint `{fingerprint}` are shared by manager/developer identities `{ids}`"
            )

    return errors


def validate_assignment_file(path: Path, project_root: Path) -> list[str]:
    fields, errors = read_simple_yaml(path)
    required_fields = {
        "task_id",
        "assignee",
        "assigned_by",
        "status",
        "spec_path",
        "task_status_path",
        "branch",
        "touch_policy",
        "signature",
    }

    for field in sorted(required_fields - fields.keys()):
        errors.append(f"{path}: missing assignment field `{field}`")

    task_id = str(fields.get("task_id", ""))
    if task_id and not TASK_ID_RE.fullmatch(task_id):
        errors.append(f"{path}: invalid task_id `{task_id}`")

    assignee = str(fields.get("assignee", ""))
    if assignee and not assignee.startswith(("DEV-", "MANAGER-")):
        errors.append(f"{path}: assignee should reference `DEV-xxx` or `MANAGER-xxx`")

    assigned_by = str(fields.get("assigned_by", ""))
    if assigned_by and not assigned_by.startswith("MANAGER-"):
        errors.append(f"{path}: assigned_by should reference `MANAGER-xxx`")

    status = str(fields.get("status", ""))
    if status and status not in ASSIGNMENT_STATUSES:
        errors.append(f"{path}: invalid assignment status `{status}`")

    touch_policy = str(fields.get("touch_policy", ""))
    if touch_policy and touch_policy not in TOUCH_POLICIES:
        errors.append(f"{path}: invalid touch_policy `{touch_policy}`")

    scope_mode = str(fields.get("scope_mode", "exact_files"))
    if scope_mode and scope_mode not in SCOPE_MODES:
        errors.append(f"{path}: invalid scope_mode `{scope_mode}`")

    scope_files = fields.get("scope_files", [])
    allowed_write_roots = fields.get("allowed_write_roots", [])
    if scope_mode == "exact_files" and not scope_files:
        errors.append(f"{path}: exact_files assignments must declare `scope_files`")
    if scope_mode == "task_bounded_broad_code" and not (scope_files or allowed_write_roots):
        errors.append(f"{path}: task_bounded_broad_code assignments must declare `allowed_write_roots` or `scope_files`")

    for field_name in ("spec_path", "task_status_path"):
        reference_path = str(fields.get(field_name, ""))
        if not reference_path or is_placeholder_value(reference_path):
            errors.append(f"{path}: unresolved assignment field `{field_name}`")
            continue
        resolved_reference_path = project_root / reference_path
        if not resolved_reference_path.exists():
            errors.append(f"{path}: references missing {field_name} `{reference_path}`")

    signature = str(fields.get("signature", ""))
    if signature and is_placeholder_value(signature):
        errors.append(f"{path}: unresolved assignment field `signature`")

    for banned_field in ("private_key", "password", "token", "secret", "bearer_token"):
        if banned_field in fields:
            errors.append(f"{path}: must not store `{banned_field}` in repository assignment records")

    return errors


def validate_task_status_file(path: Path) -> list[str]:
    errors: list[str] = []
    total_lines = len(path.read_text(encoding="utf-8").splitlines())
    if total_lines > TASK_STATUS_LINE_LIMIT:
        errors.append(
            f"{path}: has {total_lines} lines; keep per-task status files under {TASK_STATUS_LINE_LIMIT} lines and move long-lived design details to docs/specs/"
        )

    front_matter, _body, fm_errors = read_front_matter(path)
    errors.extend(fm_errors)

    if not front_matter:
        return errors

    required_fields = {"kind", "task_id", "assignee", "owner_role", "status", "updated_at", "updated_by"}
    for field in sorted(required_fields - front_matter.keys()):
        errors.append(f"{path}: missing task-status front matter field `{field}`")

    kind = front_matter.get("kind", "")
    if kind and kind != "task-status":
        errors.append(f"{path}: expected kind `task-status`, got `{kind}`")

    task_id = front_matter.get("task_id", "")
    if task_id and not TASK_ID_RE.fullmatch(task_id):
        errors.append(f"{path}: invalid task_id `{task_id}`")
    if task_id:
        filename_matches = path.stem == task_id
        if V5_TASK_ID_RE.fullmatch(task_id):
            filename_matches = filename_matches or path.stem.startswith(f"{task_id}-")
        if not filename_matches:
            errors.append(f"{path}: filename should match or start with task_id `{task_id}`")

    assignee = front_matter.get("assignee", "")
    assignee_is_slug = bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", assignee))
    allow_slug = bool(V5_TASK_ID_RE.fullmatch(task_id))
    if (
        assignee
        and assignee not in {"unassigned", "shared", "n/a", "none"}
        and not assignee.startswith(("DEV-", "MANAGER-"))
        and not (allow_slug and assignee_is_slug)
    ):
        errors.append(
            f"{path}: assignee should reference a developer id, a v5 username slug, or `unassigned`"
        )

    owner_role = front_matter.get("owner_role", "")
    if owner_role and owner_role not in OWNER_ROLES:
        errors.append(f"{path}: invalid owner_role `{owner_role}`")

    status = front_matter.get("status", "")
    if status and status not in TASK_STATUSES:
        errors.append(f"{path}: invalid task-status status `{status}`")

    validate_timestamp(path, front_matter, errors)
    return errors


def validate_file(path: Path, project_root: Path) -> list[str]:
    errors: list[str] = []
    front_matter, body, fm_errors = read_front_matter(path)
    errors.extend(fm_errors)

    if not front_matter:
        return errors

    validate_common_front_matter(path, front_matter, errors)

    if path.name == "current-status.md":
        validate_current_status(path, front_matter, body, errors)
    elif path.name == "task-board.md":
        errors.extend(validate_task_board(path, body, project_root))
    elif path.name == "task-archive.md":
        errors.extend(validate_task_archive(path, body))
    elif path.name == "issue-list.md":
        validate_issue_list(path, front_matter, body, errors)
    elif path.name == "issue-archive.md":
        errors.extend(validate_issue_archive(path, body))
    elif path.name == "test-report.md":
        validate_test_report(path, front_matter, body, errors)
    elif path.name == "integration-queue.md":
        validate_integration_queue(path, front_matter, errors)

    return errors


def validate_project_guidance(project_root: Path) -> list[str]:
    errors: list[str] = []

    for filename in GUIDANCE_REQUIRED_FILES:
        path = project_root / filename
        if not path.exists():
            errors.append(
                f"missing required project guidance file: {path}. Run scripts/ensure-agent-guidance.sh to create or update it"
            )
            continue

        text = path.read_text(encoding="utf-8")
        if GUIDANCE_MARKER_BEGIN not in text or GUIDANCE_MARKER_END not in text:
            errors.append(f"{filename}: missing managed `cc-aidev-guidelines-common` guidance block")
        if "cc-aidev-guidelines-common" not in text:
            errors.append(f"{filename}: missing skill name `cc-aidev-guidelines-common`")
        if SKILL_REPO_URL not in text:
            errors.append(f"{filename}: missing GitHub install source `{SKILL_REPO_URL}`")

    return errors


def nested_value(mapping: dict[str, object], dotted_path: str, default: object = None) -> object:
    current: object = mapping
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def normalized_project_path(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def resolve_project_path(raw_path: str, state_dir: Path, project_root: Path) -> Path:
    cleaned = clean_value(raw_path).replace("\\", "/")
    if cleaned.startswith(".claw/") or cleaned in {".claw", "docs", "README.md", "AGENTS.md"}:
        return project_root / cleaned
    if cleaned.startswith("docs/") or cleaned.startswith(".github/"):
        return project_root / cleaned
    return state_dir / cleaned


def scalar_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [clean_value(item) for item in value if not is_empty_reference(clean_value(item))]
    cleaned = clean_value(value)
    if is_empty_reference(cleaned):
        return []
    return [item.strip() for item in cleaned.split(",") if item.strip()]


def version_tuple(value: object) -> tuple[int, int, int]:
    cleaned = clean_value(value)
    if not re.fullmatch(r"[0-9]\.[0-9]\.[0-9]", cleaned):
        return (0, 0, 0)
    return tuple(int(part) for part in cleaned.split("."))


def validate_project_assets(
    project_root: Path,
    manifest: dict[str, object],
    catalog: dict[str, object],
) -> list[str]:
    errors: list[str] = []
    raw_assets = catalog.get("project_assets", [])
    if not isinstance(raw_assets, list):
        return ["state catalog: project_assets must be a list"]
    manifest_version = version_tuple(manifest.get("skill_version"))
    modules = manifest.get("modules") if isinstance(manifest.get("modules"), dict) else {}
    project_mode = clean_value(manifest.get("project_mode", ""))
    for index, asset in enumerate(raw_assets):
        if not isinstance(asset, dict):
            errors.append(f"state catalog: project_assets[{index}] must be an object")
            continue
        since_version = version_tuple(asset.get("since_skill_version"))
        if manifest_version < since_version:
            continue
        module = clean_value(asset.get("module", "control_plane"))
        if module != "control_plane" and modules.get(module) is not True:
            continue
        modes = asset.get("project_modes")
        if isinstance(modes, list) and project_mode not in {clean_value(mode) for mode in modes}:
            continue
        raw_path = clean_value(asset.get("path", ""))
        relative_path = Path(raw_path)
        if not raw_path or relative_path.is_absolute() or ".." in relative_path.parts:
            errors.append(f"state catalog: invalid project asset path `{raw_path}`")
            continue
        asset_path = project_root / relative_path
        if not asset_path.is_file():
            errors.append(f"manifest: missing required project asset `{relative_path.as_posix()}`")
    return errors


def validate_devops_environment_assets(
    project_root: Path,
    devops_path: Path,
    contract: DevOpsAssetContract,
) -> list[str]:
    errors: list[str] = []
    data, _body, front_matter_errors = read_front_matter_yaml(devops_path)
    errors.extend(front_matter_errors)
    if not data:
        return errors

    assets_root = clean_value(data.get(contract.root_field, ""))
    expected_root = contract.root_path.as_posix()
    if assets_root != expected_root:
        errors.append(f"{devops_path}: {contract.root_field} must be `{expected_root}`")

    environments = scalar_list(data.get(contract.environments_field))
    if not environments:
        errors.append(
            f"{devops_path}: {contract.environments_field} must contain at least one confirmed environment"
        )
        return errors

    try:
        environments = normalize_environment_names(environments)
    except ValueError as exc:
        errors.append(f"{devops_path}: {exc}")
        return errors

    assets_dir = project_root / contract.root_path
    for asset in contract.root_files:
        asset_path = assets_dir / asset.path
        if not asset_path.is_file():
            errors.append(f"{devops_path}: missing {(contract.root_path / asset.path).as_posix()}")
    for environment in environments:
        for asset in contract.per_environment_files:
            asset_path = assets_dir / environment / asset.path
            if not asset_path.is_file():
                errors.append(
                    f"{devops_path}: missing DevOps environment asset "
                    f"`{asset_path.relative_to(project_root).as_posix()}`"
                )
    return errors


def valid_timestamp_or_none(value: object) -> bool:
    if value is None:
        return True
    cleaned = clean_value(value)
    return cleaned.lower() in {"none", "n/a", "null"} or bool(TIMESTAMP_RE.fullmatch(cleaned))


def validate_manifest_data(path: Path, manifest: dict[str, object]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "skill_version",
        "project_mode",
        "initialization",
        "modules",
        "module_config",
        "compatibility",
    }
    for field_name in sorted(required - manifest.keys()):
        errors.append(f"{path}: missing manifest field `{field_name}`")

    if manifest.get("schema_version") != 5:
        errors.append(f"{path}: schema_version must be integer `5`")

    skill_version = clean_value(manifest.get("skill_version", ""))
    if not re.fullmatch(r"[0-9]\.[0-9]\.[0-9]", skill_version):
        errors.append(f"{path}: invalid skill_version `{skill_version}`; expected x.y.z with single digits")

    version_parts = (
        tuple(int(part) for part in skill_version.split("."))
        if re.fullmatch(r"[0-9]\.[0-9]\.[0-9]", skill_version)
        else (0, 0, 0)
    )
    if "language" not in manifest:
        if version_parts >= (5, 0, 1):
            errors.append(f"{path}: missing manifest field `language`")
        language = "en"
    else:
        language = clean_value(manifest.get("language", ""))
        if language not in V5_LANGUAGES:
            errors.append(f"{path}: invalid language `{language}`; expected pending, en, or zh-CN")
    if version_parts >= (5, 0, 3) and language != PRIMARY_LANGUAGE:
        errors.append(f"{path}: skill_version 5.0.3 or newer requires language `{PRIMARY_LANGUAGE}`")

    project_mode = clean_value(manifest.get("project_mode", ""))
    if project_mode not in V5_PROJECT_MODES:
        errors.append(f"{path}: invalid project_mode `{project_mode}`")

    initialization_status = ""
    initialization = manifest.get("initialization")
    if not isinstance(initialization, dict):
        errors.append(f"{path}: `initialization` must be a mapping")
    else:
        init_required = {"status", "started_at", "completed_at", "confirmed_by"}
        for field_name in sorted(init_required - initialization.keys()):
            errors.append(f"{path}: missing initialization field `{field_name}`")
        initialization_status = clean_value(initialization.get("status", ""))
        if initialization_status not in V5_INITIALIZATION_STATUSES:
            errors.append(f"{path}: invalid initialization.status `{initialization_status}`")
        if not valid_timestamp_or_none(initialization.get("started_at", "")):
            errors.append(f"{path}: invalid initialization.started_at")
        if not valid_timestamp_or_none(initialization.get("completed_at", "")):
            errors.append(f"{path}: invalid initialization.completed_at")
        if initialization_status == "ready":
            if is_empty_reference(clean_value(initialization.get("completed_at", ""))):
                errors.append(f"{path}: ready initialization requires completed_at")
            if is_empty_reference(clean_value(initialization.get("confirmed_by", ""))):
                errors.append(f"{path}: ready initialization requires confirmed_by")
            if language == PENDING_LANGUAGE:
                errors.append(f"{path}: ready initialization cannot keep language pending")

    modules = manifest.get("modules")
    if not isinstance(modules, dict):
        errors.append(f"{path}: `modules` must be a mapping")
        modules = {}
    for module_name in sorted(V5_MODULES):
        if module_name not in modules:
            errors.append(f"{path}: missing modules.{module_name}")
        elif not isinstance(modules[module_name], bool):
            errors.append(f"{path}: modules.{module_name} must be boolean")
    if modules.get("collaboration_gate") is True and modules.get("project_state") is not True:
        errors.append(f"{path}: collaboration_gate requires project_state=true")
    if modules.get("project_state") is True and project_mode not in {*V5_PROJECT_STATE_MODES, "pending"}:
        errors.append(
            f"{path}: project_state=true requires project_mode pending, greenfield, or brownfield"
        )
    if initialization_status == "ready" and project_mode == "pending":
        errors.append(f"{path}: ready initialization cannot keep project_mode pending")
    if modules.get("project_state") is False and project_mode != "not_applicable":
        errors.append(f"{path}: project_state=false requires project_mode not_applicable")

    module_config = manifest.get("module_config")
    if not isinstance(module_config, dict):
        errors.append(f"{path}: `module_config` must be a mapping")
    else:
        for module_name in ("collaboration_gate", "change_review"):
            if module_name not in module_config:
                errors.append(f"{path}: missing module_config.{module_name}")
            elif modules.get(module_name) is True and is_empty_reference(
                clean_value(module_config.get(module_name, ""))
            ):
                errors.append(f"{path}: enabled module `{module_name}` requires a module_config path")

    compatibility = manifest.get("compatibility")
    if not isinstance(compatibility, dict):
        errors.append(f"{path}: `compatibility` must be a mapping")
    else:
        compat_required = {
            "legacy_documents_allowed",
            "legacy_index_path",
            "new_document_policy_version",
            "policy_effective_at",
        }
        for field_name in sorted(compat_required - compatibility.keys()):
            errors.append(f"{path}: missing compatibility field `{field_name}`")
        if "legacy_documents_allowed" in compatibility and not isinstance(
            compatibility["legacy_documents_allowed"], bool
        ):
            errors.append(f"{path}: compatibility.legacy_documents_allowed must be boolean")
        policy_version = compatibility.get("new_document_policy_version")
        if not isinstance(policy_version, int) or policy_version < 1:
            errors.append(f"{path}: compatibility.new_document_policy_version must be a positive integer")
        elif version_parts >= (5, 0, 1) and policy_version < 3:
            errors.append(
                f"{path}: skill_version {skill_version} requires compatibility.new_document_policy_version >= 3"
            )
        if not valid_timestamp_or_none(compatibility.get("policy_effective_at", "")):
            errors.append(f"{path}: invalid compatibility.policy_effective_at")

    return errors


def validate_legacy_index_data(path: Path, data: dict[str, object], project_root: Path) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    legacy_paths: set[str] = set()
    required = {"kind", "schema_version", "captured_at", "policy_effective_at", "documents"}
    for field_name in sorted(required - data.keys()):
        errors.append(f"{path}: missing legacy index field `{field_name}`")
    if clean_value(data.get("kind", "")) != "legacy-document-index":
        errors.append(f"{path}: kind must be `legacy-document-index`")
    if not isinstance(data.get("schema_version"), int):
        errors.append(f"{path}: schema_version must be an integer")
    for field_name in ("captured_at", "policy_effective_at"):
        if not TIMESTAMP_RE.fullmatch(clean_value(data.get(field_name, ""))):
            errors.append(f"{path}: invalid `{field_name}`")

    documents = data.get("documents")
    if not isinstance(documents, list):
        errors.append(f"{path}: documents must be a list")
        return errors, legacy_paths

    for index, item in enumerate(documents):
        label = f"{path}: documents[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be a mapping")
            continue
        for field_name in ("path", "kind"):
            if not clean_value(item.get(field_name, "")):
                errors.append(f"{label} missing `{field_name}`")
        raw_document_path = clean_value(item.get("path", ""))
        if not raw_document_path:
            continue
        resolved = resolve_project_path(raw_document_path, project_root / ".claw", project_root)
        try:
            resolved.resolve().relative_to(project_root.resolve())
        except ValueError:
            errors.append(f"{label} path escapes the project root: `{raw_document_path}`")
            continue
        normalized = normalized_project_path(resolved, project_root)
        if normalized in legacy_paths:
            errors.append(f"{label} duplicates legacy path `{normalized}`")
        legacy_paths.add(normalized)
        if not resolved.exists():
            errors.append(f"{label} references missing path `{raw_document_path}`")

    return errors, legacy_paths


def resolve_catalog_path(explicit_path: str) -> Path | None:
    if explicit_path:
        return Path(explicit_path).expanduser()
    skill_root = Path(__file__).resolve().parent.parent
    for candidate in DEFAULT_CATALOG_CANDIDATES:
        path = skill_root / candidate
        if path.exists():
            return path
    return None


def load_catalog(path: Path) -> tuple[dict[str, object], list[dict[str, object]], list[str]]:
    errors: list[str] = []
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {}, [], [f"{path}: invalid state catalog: {exc}"]
    if not isinstance(catalog, dict):
        return {}, [], [f"{path}: state catalog must be a JSON object"]

    raw_entries: object = None
    for key in ("artifacts", "files", "entries", "documents", "state_files"):
        if key in catalog:
            raw_entries = catalog[key]
            break
    if raw_entries is None:
        candidate_entries = {
            key: value
            for key, value in catalog.items()
            if isinstance(value, dict) and ("kind" in value or "path" in value or "path_pattern" in value)
        }
        raw_entries = candidate_entries

    entries: list[dict[str, object]] = []
    if isinstance(raw_entries, list):
        for index, entry in enumerate(raw_entries):
            if not isinstance(entry, dict):
                errors.append(f"{path}: catalog entry {index} must be an object")
                continue
            normalized = dict(entry)
            normalized.setdefault("id", f"entry-{index}")
            entries.append(normalized)
    elif isinstance(raw_entries, dict):
        for entry_id, entry in raw_entries.items():
            if not isinstance(entry, dict):
                errors.append(f"{path}: catalog entry `{entry_id}` must be an object")
                continue
            normalized = dict(entry)
            normalized.setdefault("id", str(entry_id))
            entries.append(normalized)
    else:
        errors.append(f"{path}: catalog must contain `artifacts` or `files`")

    if not entries:
        errors.append(f"{path}: state catalog contains no artifacts")
    return catalog, entries, errors


def module_is_enabled(module: str, manifest: dict[str, object]) -> bool:
    normalized = module.replace("-", "_")
    if normalized in {"", "control", "core", "always"}:
        return True
    modules = manifest.get("modules", {})
    if isinstance(modules, dict) and normalized in modules:
        return modules.get(normalized) is True
    return True


def required_condition_matches(condition: object, manifest: dict[str, object], entry: dict[str, object]) -> bool:
    if condition is None:
        return False
    if isinstance(condition, bool):
        return condition
    if isinstance(condition, list):
        return all(required_condition_matches(item, manifest, entry) for item in condition)
    if isinstance(condition, dict):
        if "all" in condition:
            values = condition["all"]
            return isinstance(values, list) and all(required_condition_matches(item, manifest, entry) for item in values)
        if "any" in condition:
            values = condition["any"]
            return isinstance(values, list) and any(required_condition_matches(item, manifest, entry) for item in values)
        if "always" in condition:
            return bool(condition["always"])
        module = clean_value(condition.get("module_enabled", condition.get("module", "")))
        if module and not module_is_enabled(module, manifest):
            return False
        project_mode = clean_value(condition.get("project_mode", ""))
        if project_mode and clean_value(manifest.get("project_mode", "")) != project_mode:
            return False
        path = clean_value(condition.get("path", condition.get("manifest_path", "")))
        if path:
            actual = nested_value(manifest, path, object())
            if "equals" in condition and actual != condition["equals"]:
                return False
        return True
    if isinstance(condition, str):
        normalized = condition.strip().lower().replace("-", "_")
        if normalized in {"always", "true", "required"}:
            return True
        if normalized in {"never", "false", "event", "derived"}:
            return False
        if normalized in V5_MODULES:
            return module_is_enabled(normalized, manifest)
        if normalized in V5_PROJECT_MODES:
            return clean_value(manifest.get("project_mode", "")) == normalized
        if normalized.startswith("module:"):
            return module_is_enabled(normalized.split(":", 1)[1].strip(), manifest)
        if normalized.startswith("project_mode:"):
            return clean_value(manifest.get("project_mode", "")) == normalized.split(":", 1)[1].strip()
        missing = object()
        actual = nested_value(manifest, normalized, missing)
        if actual is not missing:
            return bool(actual)
    return False


def catalog_entry_paths(entry: dict[str, object], state_dir: Path, project_root: Path) -> list[Path]:
    raw_path = clean_value(entry.get("path", ""))
    pattern = clean_value(entry.get("path_pattern", entry.get("pattern", entry.get("glob", ""))))
    if raw_path and any(char in raw_path for char in "*?["):
        pattern = raw_path
        raw_path = ""
    if raw_path:
        return [resolve_project_path(raw_path, state_dir, project_root)]
    if not pattern:
        return []
    cleaned = pattern.replace("\\", "/")
    cleaned = re.sub(r"<[^>]+>", "*", cleaned)
    if cleaned.startswith(".claw/") or cleaned.startswith("docs/") or cleaned.startswith(".github/"):
        return sorted(project_root.glob(cleaned))
    return sorted(state_dir.glob(cleaned))


def validate_v5_front_matter_file(
    path: Path,
    entry: dict[str, object],
    *,
    require_initialization: bool,
) -> tuple[dict[str, object], list[str]]:
    data, body, errors = read_front_matter_yaml(path)
    if not data:
        return data, errors
    expected_kind = clean_value(entry.get("kind", ""))
    if expected_kind and clean_value(data.get("kind", "")) != expected_kind:
        errors.append(f"{path}: expected kind `{expected_kind}`, got `{clean_value(data.get('kind', ''))}`")
    required_fields = entry.get("required_fields", [])
    if not isinstance(required_fields, list):
        errors.append(f"catalog entry `{entry.get('id', 'unknown')}`: required_fields must be a list")
        required_fields = []
    effective_required = {clean_value(item) for item in required_fields if clean_value(item)}
    if require_initialization:
        effective_required.update(V5_COMMON_CORE_FIELDS)
    for field_name in sorted(effective_required - data.keys()):
        errors.append(f"{path}: missing v5 field `{field_name}`")
    expected_schema = entry.get("schema_version")
    if expected_schema is not None and data.get("schema_version") != expected_schema:
        errors.append(f"{path}: schema_version must be `{expected_schema}` from the state catalog")
    elif expected_schema is None and "schema_version" in data and data.get("schema_version") != 5:
        errors.append(f"{path}: schema_version must be integer `5`")
    if require_initialization:
        init_status = clean_value(data.get("init_status", ""))
        if init_status and init_status not in V5_INIT_STATUSES:
            errors.append(f"{path}: invalid init_status `{init_status}`")
        if "init_completed_at" in data and not valid_timestamp_or_none(data.get("init_completed_at")):
            errors.append(f"{path}: invalid init_completed_at")
        if "updated_at" in data and not valid_timestamp_or_none(data.get("updated_at")):
            errors.append(f"{path}: invalid updated_at")
        if init_status == "complete":
            if ONBOARDING_INCOMPLETE_SENTINEL in body:
                errors.append(
                    f"{path}: init_status=complete but onboarding sentinel remains "
                    f"`{ONBOARDING_INCOMPLETE_SENTINEL}`"
                )
            if is_empty_reference(clean_value(data.get("init_completed_at", ""))):
                errors.append(f"{path}: complete init_status requires init_completed_at")
            if is_empty_reference(clean_value(data.get("init_confirmed_by", ""))):
                errors.append(f"{path}: complete init_status requires init_confirmed_by")
            for field_name, value in data.items():
                if isinstance(value, str) and is_placeholder_value(value):
                    errors.append(f"{path}: complete file has unresolved placeholder in `{field_name}`")
    return data, errors


def find_task_status_path(state_dir: Path, task_id: str) -> Path | None:
    tasks_dir = state_dir / "tasks"
    exact = tasks_dir / f"{task_id}.md"
    candidates = ([exact] if exact.exists() else []) + sorted(tasks_dir.glob(f"{task_id}-*.md"))
    return candidates[0] if len(candidates) == 1 else None


def find_feature_path(project_root: Path, feature_id: str) -> Path | None:
    specs_dir = project_root / "docs" / "specs"
    exact = specs_dir / f"{feature_id}.md"
    candidates = ([exact] if exact.exists() else []) + sorted(specs_dir.glob(f"{feature_id}-*.md"))
    return candidates[0] if len(candidates) == 1 else None


def validate_v5_current_status(
    path: Path,
    state_dir: Path,
    legacy_paths: set[str],
    project_root: Path,
    *,
    require_current_user: bool = False,
) -> list[str]:
    data, body, errors = read_front_matter_yaml(path)
    if not data:
        return errors
    total_lines = len(path.read_text(encoding="utf-8").splitlines())
    if total_lines > CURRENT_STATUS_LINE_LIMIT:
        errors.append(f"{path}: has {total_lines} lines; keep the hot index under {CURRENT_STATUS_LINE_LIMIT} lines")
    for heading in FORBIDDEN_CURRENT_STATUS_HEADINGS:
        if re.search(rf"^##\s+{re.escape(heading)}\s*$", body, flags=re.MULTILINE):
            errors.append(f"{path}: forbidden hot-file history section `{heading}`")

    relative_path = normalized_project_path(path, project_root)
    is_registered_legacy = relative_path in legacy_paths
    if require_current_user and not is_registered_legacy:
        current_user = clean_value(data.get("current_user", ""))
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", current_user):
            errors.append(f"{path}: current_user must be a non-empty lowercase user slug")
    active_tasks_value = data.get("active_tasks")
    if active_tasks_value is None:
        if not is_registered_legacy:
            errors.append(f"{path}: v5 current status must declare `active_tasks`")
        legacy_active = clean_value(data.get("active_task", ""))
        active_tasks = [] if is_empty_reference(legacy_active) else [legacy_active]
    elif not isinstance(active_tasks_value, list):
        errors.append(f"{path}: active_tasks must be a list")
        active_tasks = []
    else:
        active_tasks = [clean_value(item) for item in active_tasks_value]

    if len(active_tasks) != len(set(active_tasks)):
        errors.append(f"{path}: active_tasks contains duplicate IDs")
    for task_id in active_tasks:
        if not TASK_ID_RE.fullmatch(task_id):
            errors.append(f"{path}: invalid active task id `{task_id}`")
            continue
        task_path = find_task_status_path(state_dir, task_id)
        if task_path is None:
            errors.append(f"{path}: active task `{task_id}` has no unique task status file")
            continue
        task_data, _task_body, task_errors = read_front_matter_yaml(task_path)
        errors.extend(task_errors)
        task_status = clean_value(task_data.get("status", ""))
        if task_status in {"done", "canceled"}:
            errors.append(f"{path}: active task `{task_id}` has terminal status `{task_status}`")

    # Explicitly indexed legacy hot state keeps the v4 single-active-task wire
    # format. Adoption must not mutate that grandfathered document merely to
    # satisfy v5 multi-task bookkeeping fields.
    if is_registered_legacy:
        return errors

    count = data.get("active_task_count")
    if not isinstance(count, int) or count < 0:
        errors.append(f"{path}: active_task_count must be a non-negative integer")
    else:
        truncated = data.get("active_tasks_truncated", False)
        shown = data.get("active_tasks_shown", len(active_tasks))
        if not isinstance(truncated, bool):
            errors.append(f"{path}: active_tasks_truncated must be boolean")
        elif truncated:
            if count < len(active_tasks):
                errors.append(f"{path}: truncated active_task_count cannot be smaller than active_tasks length")
            if shown != len(active_tasks):
                errors.append(f"{path}: active_tasks_shown must equal active_tasks length when truncated")
        elif count != len(active_tasks):
            errors.append(f"{path}: active_task_count `{count}` does not match active_tasks length `{len(active_tasks)}`")
    return errors


def validate_current_status_git_ignore(project_root: Path) -> list[str]:
    path = project_root / ".gitignore"
    if not path.is_file():
        return [f"{path}: missing `.claw/current-status.md` ignore rule for the local personal status"]
    entries = {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if not ({".claw/current-status.md", "/.claw/current-status.md"} & entries):
        return [f"{path}: missing `.claw/current-status.md` ignore rule for the local personal status"]
    return []


def validate_v5_task_document(path: Path, data: dict[str, object], legacy_paths: set[str], project_root: Path) -> list[str]:
    errors: list[str] = []
    task_id = clean_value(data.get("task_id", ""))
    relative_path = normalized_project_path(path, project_root)
    if not TASK_ID_RE.fullmatch(task_id):
        errors.append(f"{path}: invalid task_id `{task_id}`")
        return errors
    if LEGACY_TASK_ID_RE.fullmatch(task_id):
        if relative_path not in legacy_paths:
            errors.append(f"{path}: legacy task `{task_id}` is not registered in legacy-document-index")
        return errors
    if path.stem != task_id and not path.stem.startswith(f"{task_id}-"):
        errors.append(f"{path}: filename must start with task_id `{task_id}`")
    required = {
        "kind",
        "schema_version",
        "task_id",
        "task_type",
        "feature_id",
        "created_at",
        "created_by",
        "created_by_slug",
        "created_by_source",
        "created_by_developer_id",
        "owner_slug",
        "assignee",
        "owner_role",
        "status",
        "policy_version",
        "updated_at",
        "updated_by",
    }
    for field_name in sorted(required - data.keys()):
        errors.append(f"{path}: missing new task field `{field_name}`")
    if data.get("schema_version") != 5:
        errors.append(f"{path}: schema_version must be integer `5`")
    if data.get("policy_version") not in {2, 3}:
        errors.append(f"{path}: policy_version must be integer `2` or `3`")
    slug_match = re.fullmatch(r"TASK-(.+)-[0-9]{3}", task_id)
    if slug_match and clean_value(data.get("owner_slug", "")) != slug_match.group(1):
        errors.append(f"{path}: owner_slug must match task_id namespace `{slug_match.group(1)}`")
    feature_id = clean_value(data.get("feature_id", ""))
    if not is_empty_reference(feature_id):
        if not FEATURE_ID_RE.fullmatch(feature_id):
            errors.append(f"{path}: invalid feature_id `{feature_id}`")
        elif find_feature_path(project_root, feature_id) is None:
            errors.append(f"{path}: references missing feature `{feature_id}`")
        elif V5_FEATURE_ID_RE.fullmatch(feature_id):
            feature_path = find_feature_path(project_root, feature_id)
            assert feature_path is not None
            feature_data, _feature_body, _feature_errors = read_front_matter_yaml(feature_path)
            feature_init_status = clean_value(feature_data.get("init_status", ""))
            feature_status = clean_value(feature_data.get("status", ""))
            if (
                feature_init_status != "complete"
                or feature_status not in CONFIRMED_FEATURE_STATUSES
            ):
                errors.append(
                    f"{path}: referenced feature `{feature_id}` is not user-confirmed "
                    f"(init_status={feature_init_status or 'missing'}, status={feature_status or 'missing'})"
                )
    return errors


def validate_v5_feature_document(path: Path, data: dict[str, object], legacy_paths: set[str], project_root: Path, state_dir: Path) -> list[str]:
    errors: list[str] = []
    feature_id = clean_value(data.get("feature_id", ""))
    relative_path = normalized_project_path(path, project_root)
    if not FEATURE_ID_RE.fullmatch(feature_id):
        errors.append(f"{path}: invalid feature_id `{feature_id}`")
        return errors
    if LEGACY_FEATURE_ID_RE.fullmatch(feature_id):
        if relative_path not in legacy_paths:
            errors.append(f"{path}: legacy feature `{feature_id}` is not registered in legacy-document-index")
        return errors
    if path.stem != feature_id and not path.stem.startswith(f"{feature_id}-"):
        errors.append(f"{path}: filename must start with feature_id `{feature_id}`")
    required = {
        "kind",
        "schema_version",
        "feature_id",
        "work_type",
        "title",
        "status",
        "init_status",
        "init_completed_at",
        "init_confirmed_by",
        "created_at",
        "created_by",
        "created_by_slug",
        "created_by_source",
        "created_by_developer_id",
        "owner_slug",
        "contributors",
        "task_ids",
        "related_decisions",
        "related_issues",
        "policy_version",
        "updated_at",
        "updated_by",
    }
    for field_name in sorted(required - data.keys()):
        errors.append(f"{path}: missing new feature field `{field_name}`")
    if data.get("schema_version") != 5:
        errors.append(f"{path}: schema_version must be integer `5`")
    if data.get("policy_version") not in {2, 3}:
        errors.append(f"{path}: policy_version must be integer `2` or `3`")
    slug_match = re.fullmatch(r"FEAT-(.+)-[0-9]{3}", feature_id)
    if slug_match and clean_value(data.get("created_by_slug", "")) != slug_match.group(1):
        errors.append(f"{path}: created_by_slug must match feature_id namespace `{slug_match.group(1)}`")
    if slug_match and clean_value(data.get("owner_slug", "")) != slug_match.group(1):
        errors.append(f"{path}: owner_slug must match feature_id namespace `{slug_match.group(1)}`")
    for task_id in scalar_list(data.get("task_ids")):
        if not TASK_ID_RE.fullmatch(task_id):
            errors.append(f"{path}: invalid task_ids entry `{task_id}`")
        elif find_task_status_path(state_dir, task_id) is None:
            errors.append(f"{path}: references missing task `{task_id}`")
    return errors


def load_v5_legacy_paths(
    manifest: dict[str, object], state_dir: Path, project_root: Path
) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    compatibility = manifest.get("compatibility", {})
    if not isinstance(compatibility, dict):
        return set(), errors
    allowed = compatibility.get("legacy_documents_allowed") is True
    index_reference = clean_value(compatibility.get("legacy_index_path", ""))
    if not allowed:
        if not is_empty_reference(index_reference):
            errors.append("manifest: legacy_index_path must be none when legacy_documents_allowed=false")
        return set(), errors
    if is_empty_reference(index_reference):
        return set(), errors
    index_path = resolve_project_path(index_reference, state_dir, project_root)
    if not index_path.exists():
        return set(), [f"manifest: legacy_index_path does not exist: `{index_reference}`"]
    index_data, read_errors = read_yaml_document(index_path)
    errors.extend(read_errors)
    if not index_data:
        return set(), errors
    index_errors, legacy_paths = validate_legacy_index_data(index_path, index_data, project_root)
    errors.extend(index_errors)
    return legacy_paths, errors


def validate_module_config_file(path: Path, module_name: str, *, require_complete: bool) -> list[str]:
    data, errors = read_yaml_document(path)
    if not data:
        return errors
    expected_kind = "collaboration-config" if module_name == "collaboration_gate" else "change-review-config"
    if clean_value(data.get("kind", "")) != expected_kind:
        errors.append(f"{path}: expected kind `{expected_kind}`")
    for field_name in sorted(V5_COMMON_CORE_FIELDS - data.keys()):
        errors.append(f"{path}: missing required module config field `{field_name}`")
    if data.get("schema_version") != 5:
        errors.append(f"{path}: schema_version must be integer `5`")
    init_status = clean_value(data.get("init_status", ""))
    if init_status not in V5_INIT_STATUSES:
        errors.append(f"{path}: invalid init_status `{init_status}`")
    if "init_completed_at" in data and not valid_timestamp_or_none(data.get("init_completed_at")):
        errors.append(f"{path}: invalid init_completed_at")
    if "updated_at" in data and not valid_timestamp_or_none(data.get("updated_at")):
        errors.append(f"{path}: invalid updated_at")
    if init_status == "complete":
        if is_empty_reference(data.get("init_completed_at", "")):
            errors.append(f"{path}: complete init_status requires init_completed_at")
        if is_empty_reference(data.get("init_confirmed_by", "")):
            errors.append(f"{path}: complete init_status requires init_confirmed_by")
        for field_name, value in data.items():
            if isinstance(value, str) and is_placeholder_value(value):
                errors.append(f"{path}: complete module config has unresolved placeholder in `{field_name}`")
    if require_complete or init_status == "complete":
        if module_name == "collaboration_gate":
            if data.get("enabled") is not True:
                errors.append(f"{path}: completed collaboration config requires enabled=true")
            for field_name in ("identity_binding", "commit_signing"):
                value = clean_value(data.get(field_name, ""))
                if is_empty_reference(value) or is_placeholder_value(value) or value.lower() == "pending":
                    errors.append(
                        f"{path}: completed collaboration config requires non-placeholder `{field_name}`"
                    )
            for field_name in ("local_login_required", "assignment_required", "manager_required"):
                if data.get(field_name) is not True:
                    errors.append(f"{path}: completed collaboration config requires {field_name}=true")
        else:
            platform = clean_value(data.get("platform", ""))
            if platform not in {"codeup", "github"}:
                errors.append(f"{path}: completed change-review config requires platform=codeup or github")
            target_branch = clean_value(data.get("target_branch", ""))
            if is_empty_reference(target_branch) or target_branch.lower() == "pending" or is_placeholder_value(target_branch):
                errors.append(f"{path}: completed change-review config requires a non-pending target_branch")
            creation_policy = clean_value(data.get("creation_policy", ""))
            if creation_policy not in {"manual", "automatic"}:
                errors.append(
                    f"{path}: completed change-review config requires creation_policy=manual or automatic"
                )
            if clean_value(data.get("token_storage", "")) != "local_only":
                errors.append(f"{path}: completed change-review config requires token_storage=local_only")
    if require_complete and init_status != "complete":
        errors.append(f"{path}: strict/finalized validation requires module config init_status=complete")
    return errors


def validate_v5_developer_record(path: Path, legacy_paths: set[str], project_root: Path) -> list[str]:
    errors = validate_developer_record(path)
    if normalized_project_path(path, project_root) in legacy_paths:
        return errors
    fields, read_errors = read_simple_yaml(path)
    errors.extend(read_errors)
    document_slug = clean_value(fields.get("document_slug", ""))
    if not document_slug:
        errors.append(f"{path}: missing v5 developer field `document_slug`")
    elif not DOCUMENT_SLUG_RE.fullmatch(document_slug):
        errors.append(f"{path}: invalid document_slug `{document_slug}`; expected lowercase slug")
    return errors


def validate_catalog_artifacts(
    entries: list[dict[str, object]],
    manifest: dict[str, object],
    state_dir: Path,
    project_root: Path,
    legacy_paths: set[str],
    *,
    strict_v5: bool,
) -> list[str]:
    errors: list[str] = []
    initialization = manifest.get("initialization", {})
    manifest_ready = isinstance(initialization, dict) and clean_value(initialization.get("status", "")) == "ready"

    for entry in entries:
        entry_id = clean_value(entry.get("id", "unknown"))
        module = clean_value(entry.get("module", "control"))
        enabled = module_is_enabled(module, manifest)
        if not enabled:
            continue
        required = enabled and required_condition_matches(entry.get("required_when"), manifest, entry)
        paths = catalog_entry_paths(entry, state_dir, project_root)
        has_pattern = bool(clean_value(entry.get("path_pattern", entry.get("pattern", entry.get("glob", "")))))

        if required and not paths:
            errors.append(f"catalog `{entry_id}`: required artifact has no path or matching files")
            continue
        if required and not has_pattern and paths and not paths[0].exists():
            errors.append(f"catalog `{entry_id}`: missing required file `{paths[0]}`")
            continue

        existing_paths = [path for path in paths if path.exists()]
        for path in existing_paths:
            relative_path = normalized_project_path(path, project_root)
            if relative_path in legacy_paths:
                continue
            if path.name == "manifest.yaml":
                continue
            if path.suffix.lower() not in {".md", ".markdown"}:
                data, read_errors = read_yaml_document(path)
                errors.extend(read_errors)
                if data:
                    expected_kind = clean_value(entry.get("kind", ""))
                    if expected_kind and clean_value(data.get("kind", "")) != expected_kind:
                        errors.append(f"{path}: expected kind `{expected_kind}`")
                    required_fields = entry.get("required_fields", [])
                    if not isinstance(required_fields, list):
                        errors.append(f"catalog entry `{entry_id}`: required_fields must be a list")
                        required_fields = []
                    effective_required = {
                        clean_value(item) for item in required_fields if clean_value(item)
                    }
                    require_initialization = entry.get("initialization_required") is True
                    if require_initialization:
                        effective_required.update(V5_COMMON_CORE_FIELDS)
                    for field_name in sorted(effective_required - data.keys()):
                        errors.append(f"{path}: missing v5 field `{field_name}`")
                    expected_schema = entry.get("schema_version")
                    if expected_schema is not None and data.get("schema_version") != expected_schema:
                        errors.append(
                            f"{path}: schema_version must be `{expected_schema}` from the state catalog"
                        )
                    elif expected_schema is None and "schema_version" in data and data.get("schema_version") != 5:
                        errors.append(f"{path}: schema_version must be integer `5`")
                    if require_initialization:
                        init_status = clean_value(data.get("init_status", ""))
                        if init_status and init_status not in V5_INIT_STATUSES:
                            errors.append(f"{path}: invalid init_status `{init_status}`")
                        if (manifest_ready or strict_v5) and init_status != "complete":
                            errors.append(f"{path}: strict/finalized validation requires init_status=complete")
                continue

            require_initialization = entry.get("initialization_required") is True
            data, file_errors = validate_v5_front_matter_file(
                path,
                entry,
                require_initialization=require_initialization,
            )
            errors.extend(file_errors)
            if (
                (manifest_ready or strict_v5)
                and require_initialization
                and clean_value(data.get("init_status", "")) != "complete"
            ):
                errors.append(f"{path}: strict/finalized validation requires init_status=complete")

    return errors


def validate_v4_state(state_dir: Path) -> list[str]:
    project_root = state_dir.resolve().parent
    errors: list[str] = []

    for filename in EXPECTED_KINDS:
        path = state_dir / filename
        if not path.exists():
            errors.append(f"missing required file: {path}")
            continue
        errors.extend(validate_file(path, project_root))

    for filename in OPTIONAL_STATE_KINDS:
        path = state_dir / filename
        if path.exists():
            errors.extend(validate_file(path, project_root))
    if (state_dir / "test-archive.md").exists() and (state_dir / "test-report-archive.md").exists():
        errors.append(
            "both test-archive.md and legacy test-report-archive.md exist; keep only test-archive.md"
        )

    developers_dir = state_dir / "developers"
    if developers_dir.exists():
        developer_records: list[tuple[Path, dict[str, object]]] = []
        for path in sorted(developers_dir.glob("*.yaml")) + sorted(developers_dir.glob("*.yml")):
            errors.extend(validate_developer_record(path))
            fields, _field_errors = read_simple_yaml(path)
            developer_records.append((path, fields))
        errors.extend(validate_developer_identity_policy(developer_records))

    assignments_dir = state_dir / "assignments"
    if assignments_dir.exists():
        for path in sorted(assignments_dir.glob("*.yaml")) + sorted(assignments_dir.glob("*.yml")):
            errors.extend(validate_assignment_file(path, project_root))

    tasks_dir = state_dir / "tasks"
    if tasks_dir.exists():
        for path in sorted(tasks_dir.glob("*.md")):
            errors.extend(validate_task_status_file(path))

    errors.extend(validate_project_documents(project_root))
    errors.extend(validate_project_guidance(project_root))
    return errors


def validate_v5_state(state_dir: Path, catalog_path: Path, *, strict_v5: bool = False) -> list[str]:
    project_root = state_dir.resolve().parent
    errors: list[str] = []
    manifest_path = state_dir / "manifest.yaml"
    manifest, read_errors = read_yaml_document(manifest_path)
    errors.extend(read_errors)
    if not manifest:
        return errors
    errors.extend(validate_manifest_data(manifest_path, manifest))

    modules = manifest.get("modules", {})
    module_config = manifest.get("module_config", {})
    initialization = manifest.get("initialization", {})
    manifest_ready = isinstance(initialization, dict) and clean_value(initialization.get("status", "")) == "ready"
    if isinstance(modules, dict) and isinstance(module_config, dict):
        for module_name in ("collaboration_gate", "change_review"):
            config_reference = clean_value(module_config.get(module_name, ""))
            if modules.get(module_name) is True and not is_empty_reference(config_reference):
                config_path = resolve_project_path(config_reference, state_dir, project_root)
                if not config_path.exists():
                    errors.append(
                        f"manifest: enabled module `{module_name}` references missing config `{config_reference}`"
                    )
                else:
                    errors.extend(
                        validate_module_config_file(
                            config_path,
                            module_name,
                            require_complete=manifest_ready or strict_v5,
                        )
                    )

    catalog, entries, catalog_errors = load_catalog(catalog_path)
    errors.extend(catalog_errors)
    legacy_paths, legacy_errors = load_v5_legacy_paths(manifest, state_dir, project_root)
    errors.extend(legacy_errors)
    if entries:
        errors.extend(
            validate_catalog_artifacts(
                entries,
                manifest,
                state_dir,
                project_root,
                legacy_paths,
                strict_v5=strict_v5,
            )
        )
    legacy_test_archive = state_dir / "test-report-archive.md"
    canonical_test_archive = state_dir / "test-archive.md"
    if legacy_test_archive.exists():
        errors.extend(validate_file(legacy_test_archive, project_root))
        if canonical_test_archive.exists():
            errors.append(
                "both test-archive.md and legacy test-report-archive.md exist; keep only test-archive.md"
            )
    if catalog:
        errors.extend(validate_project_assets(project_root, manifest, catalog))

    devops_contract: DevOpsAssetContract | None = None
    has_devops_contract = any(
        isinstance(entry, dict) and entry.get("id") == "devops" and "external_assets" in entry
        for entry in entries
    )
    if catalog and has_devops_contract:
        try:
            devops_contract = contract_from_catalog(catalog)
        except ValueError as exc:
            errors.append(f"state catalog: {exc}")

    project_state_enabled = isinstance(modules, dict) and modules.get("project_state") is True
    devops_path = project_root / devops_contract.state_path if devops_contract else state_dir / "devops.md"
    devops_assets_configured = False
    if devops_contract and devops_path.is_file():
        devops_data, _devops_body, _devops_errors = read_front_matter_yaml(devops_path)
        devops_assets_configured = bool(
            scalar_list(devops_data.get(devops_contract.environments_field))
        )
    if (
        devops_contract is not None
        and project_state_enabled
        and version_tuple(manifest.get("skill_version")) >= devops_contract.since_skill_version
        and devops_contract.state_path.as_posix() not in legacy_paths
        and devops_path.is_file()
        and (manifest_ready or strict_v5 or devops_assets_configured)
    ):
        errors.extend(validate_devops_environment_assets(project_root, devops_path, devops_contract))

    current_status = state_dir / "current-status.md"
    if project_state_enabled and current_status.exists():
        personal_status_required = version_tuple(manifest.get("skill_version")) >= (5, 1, 2)
        errors.extend(
            validate_v5_current_status(
                current_status,
                state_dir,
                legacy_paths,
                project_root,
                require_current_user=personal_status_required,
            )
        )
        if personal_status_required:
            errors.extend(validate_current_status_git_ignore(project_root))

    tasks_dir = state_dir / "tasks"
    if project_state_enabled and tasks_dir.exists():
        for path in sorted(tasks_dir.glob("TASK-*.md")):
            data, _body, file_errors = read_front_matter_yaml(path)
            errors.extend(file_errors)
            if data:
                errors.extend(validate_v5_task_document(path, data, legacy_paths, project_root))

    specs_dir = project_root / "docs" / "specs"
    if project_state_enabled and specs_dir.exists():
        for path in sorted(specs_dir.glob("FEAT-*.md")):
            data, _body, file_errors = read_front_matter_yaml(path)
            errors.extend(file_errors)
            if data:
                errors.extend(validate_v5_feature_document(path, data, legacy_paths, project_root, state_dir))

    if project_state_enabled:
        errors.extend(validate_project_documents(project_root))

    collaboration_gate_enabled = isinstance(modules, dict) and modules.get("collaboration_gate") is True
    developers_dir = state_dir / "developers"
    if collaboration_gate_enabled and developers_dir.exists():
        developer_records: list[tuple[Path, dict[str, object]]] = []
        for path in sorted(developers_dir.glob("*.yaml")) + sorted(developers_dir.glob("*.yml")):
            errors.extend(validate_v5_developer_record(path, legacy_paths, project_root))
            fields, _field_errors = read_simple_yaml(path)
            developer_records.append((path, fields))
        errors.extend(validate_developer_identity_policy(developer_records))

    assignments_dir = state_dir / "assignments"
    if collaboration_gate_enabled and assignments_dir.exists():
        for path in sorted(assignments_dir.glob("*.yaml")) + sorted(assignments_dir.glob("*.yml")):
            errors.extend(validate_assignment_file(path, project_root))

    errors.extend(validate_project_guidance(project_root))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate legacy v4 or manifest/catalog-driven v5 project state in .claw."
    )
    parser.add_argument("state_dir", nargs="?", default=".claw", help="Path to the project's .claw directory")
    parser.add_argument("--catalog", default="", help="Override the v5 state-catalog.json path")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    parser.add_argument(
        "--strict-v5",
        action="store_true",
        help="Require manifest v5 instead of falling back to legacy v4 validation",
    )
    return parser


def run_validation(state_dir: Path, *, catalog_override: str = "", strict_v5: bool = False) -> ValidationResult:
    manifest_path = state_dir / "manifest.yaml"
    mode = "v5" if manifest_path.exists() else "v4"
    result = ValidationResult(state_dir=state_dir, mode=mode, strict_v5=strict_v5)

    if state_dir.name != ".claw":
        result.errors.append(f"state directory must be named `.claw`, got `{state_dir.name}`")
    if not state_dir.exists():
        result.errors.append(f"State directory does not exist: {state_dir}")
        return result
    if not state_dir.is_dir():
        result.errors.append(f"State path is not a directory: {state_dir}")
        return result

    if not manifest_path.exists():
        if strict_v5:
            result.errors.append(f"strict v5 validation requires `{manifest_path}`")
        else:
            result.errors.extend(validate_v4_state(state_dir))
        return result

    catalog_path = resolve_catalog_path(catalog_override)
    result.catalog_path = catalog_path
    if catalog_path is None:
        result.errors.append(
            "v5 validation requires state-catalog.json; pass --catalog or install it in the skill root"
        )
        return result
    if not catalog_path.exists():
        result.errors.append(f"state catalog does not exist: {catalog_path}")
        return result
    result.errors.extend(validate_v5_state(state_dir, catalog_path, strict_v5=strict_v5))
    return result


def print_result(result: ValidationResult, *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(result.as_json(), ensure_ascii=False, indent=2, sort_keys=True))
        return
    if result.errors:
        print("State validation failed:")
        for error in result.errors:
            print(f"- {error}")
        for warning in result.warnings:
            print(f"- warning: {warning}")
        return
    print(f"State validation passed for: {result.state_dir} ({result.mode})")
    for warning in result.warnings:
        print(f"warning: {warning}")


def main() -> int:
    args = build_parser().parse_args()
    result = run_validation(
        Path(args.state_dir).expanduser(),
        catalog_override=args.catalog,
        strict_v5=args.strict_v5,
    )
    print_result(result, json_output=args.json)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
