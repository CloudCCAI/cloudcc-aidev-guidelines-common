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
    "task-archive.md": "task-archive",
    "test-report.md": "test-report",
    "devops.md": "devops",
}
OPTIONAL_STATE_KINDS = {
    "integration-queue.md": "integration-queue",
    "team-status.md": "team-status",
}
STATE_KINDS = {**EXPECTED_KINDS, **OPTIONAL_STATE_KINDS}
SKILL_REPO_URL = "https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common"
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
PROJECT_BASELINE_STATUSES = {
    "draft",
    "adopting",
    "active_reference",
    "verified",
    "archived",
}
TASK_BOARD_COMPLETED_LIMIT = 20
CURRENT_STATUS_LINE_LIMIT = 60
TASK_CARD_LINE_LIMIT = 20
TASK_STATUS_LINE_LIMIT = 120
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
TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
TASK_HEADER_RE = re.compile(r"^###\s+(TASK-[0-9]+)\s+-\s+(.+?)\s*$")
TASK_FIELD_RE = re.compile(r"^- ([a-z_]+):\s*(.+?)\s*$")
SECTION_HEADER_RE = re.compile(r"^##\s+(.+?)\s*$")
TEST_REPORT_STATUS_RE = re.compile(r"- 状态：`([^`]+)`")
SIMPLE_YAML_FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$")


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
    if "..." in cleaned:
        return True
    if cleaned.startswith("[") and cleaned.endswith("]"):
        return True
    return False


def is_empty_reference(value: str) -> bool:
    cleaned = clean_value(value).lower()
    return cleaned in {"", "none", "n/a", "na", "not_applicable"}


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

        if section == "Completed Tasks":
            completed_task_count += 1
            if status not in {"done", "canceled"}:
                errors.append(
                    f"{path.name}: task `{task_id}` is in `Completed Tasks` but has status `{status}`"
                )

        if section == "Active Tasks" and status in {"done", "canceled"}:
            errors.append(f"{path.name}: task `{task_id}` is in `Active Tasks` but has terminal status `{status}`")

        task_status_path = clean_value(str(fields.get("task_status_path", "")))
        if section == "Active Tasks":
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

        if section and section != "Archived Tasks":
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
    if task_id and not task_id.startswith("TASK-"):
        errors.append(f"{path}: task_id should start with `TASK-`")

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
    if task_id and not task_id.startswith("TASK-"):
        errors.append(f"{path}: task_id should start with `TASK-`")
    if task_id and path.stem != task_id:
        errors.append(f"{path}: filename should match task_id `{task_id}`")

    assignee = front_matter.get("assignee", "")
    if assignee and assignee not in {"unassigned", "shared", "n/a", "none"} and not assignee.startswith(("DEV-", "MANAGER-")):
        errors.append(f"{path}: assignee should reference `DEV-xxx`, `MANAGER-xxx`, or `unassigned`")

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

    for filename in OPTIONAL_STATE_KINDS:
        path = state_dir / filename
        if path.exists():
            errors.extend(validate_file(path, project_root))

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

    errors.extend(validate_project_guidance(project_root))

    if errors:
        print("State validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"State validation passed for: {state_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
