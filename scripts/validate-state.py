#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


EXPECTED_KINDS = {
    "current-status.md": "current-status",
    "goals.md": "goals",
    "decisions.md": "decisions",
    "issue-list.md": "issue-list",
    "task-board.md": "task-board",
    "test-report.md": "test-report",
    "devops.md": "devops",
}

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
    "human",
    "shared",
    "unassigned",
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
PROJECT_BASELINE_STATUSES = {
    "draft",
    "adopting",
    "active_reference",
    "verified",
    "archived",
}
TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
TASK_HEADER_RE = re.compile(r"^###\s+(TASK-[0-9]+)\s+-\s+(.+?)\s*$")
TASK_FIELD_RE = re.compile(r"^- ([a-z_]+):\s*(.+?)\s*$")
TEST_REPORT_STATUS_RE = re.compile(r"- 状态：`([^`]+)`")


def clean_value(value: str) -> str:
    cleaned = value.strip().strip('"').strip("'")
    if cleaned.startswith("`") and cleaned.endswith("`") and len(cleaned) >= 2:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def is_placeholder_value(value: str) -> bool:
    cleaned = clean_value(value)
    if not cleaned:
        return True
    if "YYYY-MM-DD" in cleaned or "HH:MM:SS" in cleaned:
        return True
    if cleaned.startswith("[") and cleaned.endswith("]"):
        return True
    return False


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

    expected_kind = EXPECTED_KINDS[path.name]
    actual_kind = front_matter.get("kind")
    if actual_kind and actual_kind != expected_kind:
        errors.append(f"{path.name}: expected kind `{expected_kind}`, got `{actual_kind}`")

    validate_timestamp(path, front_matter, errors)


def validate_current_status(path: Path, front_matter: dict[str, str], errors: list[str]) -> None:
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

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        header_match = TASK_HEADER_RE.match(line)
        if header_match:
            if current is not None:
                tasks.append(current)
            current = {
                "id": header_match.group(1),
                "title": header_match.group(2).strip(),
                "fields": {},
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

    validate_timestamp(path, front_matter, errors)
    return errors


def validate_task_board(path: Path, body: str, project_root: Path) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    tasks = parse_task_cards(body)

    for task in tasks:
        task_id = str(task["id"])
        title = str(task["title"]).strip()
        fields = task["fields"]
        assert isinstance(fields, dict)

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


def validate_file(path: Path, project_root: Path) -> list[str]:
    errors: list[str] = []
    front_matter, body, fm_errors = read_front_matter(path)
    errors.extend(fm_errors)

    if not front_matter:
        return errors

    validate_common_front_matter(path, front_matter, errors)

    if path.name == "current-status.md":
        validate_current_status(path, front_matter, errors)
    elif path.name == "task-board.md":
        errors.extend(validate_task_board(path, body, project_root))
    elif path.name == "test-report.md":
        validate_test_report(path, front_matter, body, errors)

    return errors


def main() -> int:
    state_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".claw")

    if not state_dir.exists():
        print(f"State directory does not exist: {state_dir}", file=sys.stderr)
        return 1

    project_root = state_dir.resolve().parent
    errors: list[str] = []

    for filename in EXPECTED_KINDS:
        path = state_dir / filename
        if not path.exists():
            errors.append(f"missing required file: {path}")
            continue
        errors.extend(validate_file(path, project_root))

    if errors:
        print("State validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"State validation passed for: {state_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
