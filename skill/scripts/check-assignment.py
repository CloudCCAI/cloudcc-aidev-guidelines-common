#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import PurePosixPath, Path

from lib.document_ids import TASK_ID_RE


EMPTY_VALUES = {"", "none", "n/a", "na", "not_applicable"}
ACTIVE_STATUSES = {"active"}
MANAGER_PREFIX = "MANAGER-"
DEVELOPER_PREFIXES = ("DEV-", MANAGER_PREFIX)
SCOPE_MODE_EXACT = "exact_files"
SCOPE_MODE_BROAD = "task_bounded_broad_code"
SCOPE_MODES = {SCOPE_MODE_EXACT, SCOPE_MODE_BROAD}
GLOB_CHARS = set("*?[")


def clean_value(value: object) -> str:
    cleaned = str(value).strip().strip('"').strip("'")
    if cleaned.startswith("`") and cleaned.endswith("`") and len(cleaned) >= 2:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def is_empty(value: object) -> bool:
    return clean_value(value).lower() in EMPTY_VALUES


def read_simple_yaml(path: Path) -> dict[str, object]:
    parsed: dict[str, object] = {}
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

        if ":" not in stripped:
            current_key = None
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = clean_value(value)
        if value == "":
            parsed[key] = []
            current_key = key
        else:
            parsed[key] = value
            current_key = None

    return parsed


def value_list(fields: dict[str, object], key: str) -> list[str]:
    value = fields.get(key, [])
    if isinstance(value, list):
        return [clean_value(item) for item in value if not is_empty(item)]
    if is_empty(value):
        return []
    return [item.strip() for item in clean_value(value).split(",") if item.strip()]


def normalize_path(path: str) -> str:
    cleaned = path.replace("\\", "/").strip()
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return str(PurePosixPath(cleaned))


def has_glob(pattern: str) -> bool:
    return any(char in pattern for char in GLOB_CHARS)


def path_matches(path: str, pattern: str, *, plain_directory: bool = False) -> bool:
    normalized_path = normalize_path(path)
    normalized_pattern = normalize_path(pattern)
    if normalized_pattern in {"*", "**"}:
        return True
    if fnmatch.fnmatchcase(normalized_path, normalized_pattern):
        return True
    if normalized_pattern.endswith("/**"):
        prefix = normalized_pattern[:-3].rstrip("/")
        return normalized_path == prefix or normalized_path.startswith(f"{prefix}/")
    if normalized_pattern.endswith("/"):
        prefix = normalized_pattern.rstrip("/")
        return normalized_path == prefix or normalized_path.startswith(f"{prefix}/")
    if plain_directory and not has_glob(normalized_pattern):
        return normalized_path == normalized_pattern or normalized_path.startswith(f"{normalized_pattern}/")
    return False


def path_allowed(path: str, patterns: list[str], *, plain_directories: bool = False) -> bool:
    return any(path_matches(path, pattern, plain_directory=plain_directories) for pattern in patterns)


def scope_mode(assignment: dict[str, object]) -> str:
    value = clean_value(assignment.get("scope_mode", SCOPE_MODE_EXACT))
    return value or SCOPE_MODE_EXACT


def assignment_write_patterns(assignment: dict[str, object]) -> list[str]:
    mode = scope_mode(assignment)
    if mode == SCOPE_MODE_BROAD:
        return value_list(assignment, "allowed_write_roots") + value_list(assignment, "scope_files")
    return value_list(assignment, "scope_files")


def find_developer_record(state_dir: Path, developer_id: str) -> Path | None:
    developers_dir = state_dir / "developers"
    candidates = [
        developers_dir / f"{developer_id}.yaml",
        developers_dir / f"{developer_id}.yml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    if not developers_dir.exists():
        return None

    for path in sorted(developers_dir.glob("*.y*ml")):
        fields = read_simple_yaml(path)
        if clean_value(fields.get("developer_id", "")) == developer_id:
            return path
    return None


def find_assignment_file(state_dir: Path, task_id: str) -> Path | None:
    assignments_dir = state_dir / "assignments"
    candidates = [
        assignments_dir / f"{task_id}.yaml",
        assignments_dir / f"{task_id}.yml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    if not assignments_dir.exists():
        return None

    for path in sorted(assignments_dir.glob("*.y*ml")):
        fields = read_simple_yaml(path)
        if clean_value(fields.get("task_id", "")) == task_id:
            return path
    return None


def load_active_developers(state_dir: Path) -> list[tuple[Path, dict[str, object]]]:
    developers_dir = state_dir / "developers"
    if not developers_dir.exists():
        return []

    records: list[tuple[Path, dict[str, object]]] = []
    for path in sorted(developers_dir.glob("*.y*ml")):
        fields = read_simple_yaml(path)
        if clean_value(fields.get("status", "")) == "active":
            records.append((path, fields))
    return records


def check_duplicate_identity_policy(state_dir: Path) -> list[str]:
    findings: list[str] = []
    by_username: dict[str, list[tuple[Path, dict[str, object]]]] = {}
    by_username_and_key: dict[tuple[str, str], list[tuple[Path, dict[str, object]]]] = {}

    for path, fields in load_active_developers(state_dir):
        username = clean_value(fields.get("git_username", ""))
        fingerprint = clean_value(fields.get("ssh_signing_key_fingerprint", ""))
        if not username:
            continue
        by_username.setdefault(username, []).append((path, fields))
        if fingerprint:
            by_username_and_key.setdefault((username, fingerprint), []).append((path, fields))

    for username, records in by_username.items():
        if len(records) <= 1:
            continue
        fingerprints = [clean_value(fields.get("ssh_signing_key_fingerprint", "")) for _path, fields in records]
        if len(set(fingerprints)) != len(fingerprints) or any(not item for item in fingerprints):
            ids = ", ".join(clean_value(fields.get("developer_id", path.stem)) for path, fields in records)
            findings.append(
                f"blocked_duplicate_git_identity: git_username `{username}` is reused by active identities `{ids}` without distinct SSH signing key fingerprints"
            )
            continue
        missing_exceptions = [
            clean_value(fields.get("developer_id", path.stem))
            for path, fields in records
            if is_empty(fields.get("role_sharing_exception", ""))
        ]
        if missing_exceptions:
            findings.append(
                f"blocked_role_sharing_exception_missing: git_username `{username}` is reused but identities `{', '.join(missing_exceptions)}` do not record role_sharing_exception"
            )

    for (username, fingerprint), records in by_username_and_key.items():
        if len(records) <= 1:
            continue
        has_manager = any(clean_value(fields.get("developer_id", "")).startswith(MANAGER_PREFIX) for _path, fields in records)
        has_developer = any(clean_value(fields.get("developer_id", "")).startswith("DEV-") for _path, fields in records)
        if has_manager and has_developer:
            ids = ", ".join(clean_value(fields.get("developer_id", path.stem)) for path, fields in records)
            findings.append(
                f"blocked_manager_developer_key_reuse: git_username `{username}` and SSH signing key `{fingerprint}` are shared by manager/developer identities `{ids}`"
            )

    return findings


def check_authorization(args: argparse.Namespace) -> tuple[bool, list[str], dict[str, object]]:
    state_dir = Path(args.state_dir)
    findings: list[str] = []
    details: dict[str, object] = {
        "developer_id": args.developer,
        "task_id": args.task,
        "branch": args.branch or "",
        "files": args.files,
    }

    if not TASK_ID_RE.fullmatch(args.task):
        findings.append(
            "blocked_task_id_invalid: expected legacy TASK-<number> or v5 TASK-<user-slug>-<nnn>"
        )
        return False, findings, details

    findings.extend(check_duplicate_identity_policy(state_dir))

    developer_path = find_developer_record(state_dir, args.developer)
    if developer_path is None:
        findings.append(f"blocked_identity_unknown: developer `{args.developer}` is not registered")
        return False, findings, details

    developer = read_simple_yaml(developer_path)
    details["developer_record"] = str(developer_path)

    developer_id = clean_value(developer.get("developer_id", ""))
    if developer_id != args.developer:
        findings.append(
            f"blocked_identity_mismatch: developer record id `{developer_id}` does not match `{args.developer}`"
        )

    developer_status = clean_value(developer.get("status", ""))
    if developer_status not in ACTIVE_STATUSES:
        findings.append(f"blocked_member_inactive: developer `{args.developer}` status is `{developer_status}`")

    if args.git_username:
        expected_username = clean_value(developer.get("git_username", ""))
        if not expected_username:
            findings.append(f"blocked_identity_unbound: developer `{args.developer}` has no git_username")
        elif expected_username != args.git_username:
            findings.append(
                f"blocked_git_username_mismatch: expected `{expected_username}`, got `{args.git_username}`"
            )

    if args.ssh_signing_key_fingerprint:
        expected_fingerprint = clean_value(developer.get("ssh_signing_key_fingerprint", ""))
        if not expected_fingerprint:
            findings.append(
                f"blocked_identity_unbound: developer `{args.developer}` has no ssh_signing_key_fingerprint"
            )
        elif expected_fingerprint != args.ssh_signing_key_fingerprint:
            findings.append("blocked_ssh_signing_key_mismatch: provided SSH signing key fingerprint does not match")

    assignment_path = find_assignment_file(state_dir, args.task)
    if assignment_path is None:
        findings.append(f"blocked_assignment_missing: assignment for `{args.task}` does not exist")
        return False, findings, details

    assignment = read_simple_yaml(assignment_path)
    details["assignment_file"] = str(assignment_path)

    task_id = clean_value(assignment.get("task_id", ""))
    if task_id != args.task:
        findings.append(f"blocked_assignment_mismatch: assignment task_id `{task_id}` does not match `{args.task}`")

    assignment_status = clean_value(assignment.get("status", "active"))
    if assignment_status not in ACTIVE_STATUSES:
        findings.append(f"blocked_assignment_inactive: assignment `{args.task}` status is `{assignment_status}`")

    assignee = clean_value(assignment.get("assignee", ""))
    if assignee != args.developer:
        findings.append(f"blocked_not_assignee: assignment assignee `{assignee}` does not match `{args.developer}`")

    assigned_by = clean_value(assignment.get("assigned_by", ""))
    if not assigned_by.startswith(MANAGER_PREFIX):
        findings.append(f"blocked_manager_required: assigned_by `{assigned_by}` must reference `MANAGER-xxx`")

    if args.branch:
        expected_branch = clean_value(assignment.get("branch", ""))
        if not is_empty(expected_branch) and expected_branch != args.branch:
            findings.append(f"blocked_branch_mismatch: expected `{expected_branch}`, got `{args.branch}`")

    mode = scope_mode(assignment)
    details["scope_mode"] = mode
    if mode not in SCOPE_MODES:
        findings.append(f"blocked_scope_mode_invalid: assignment `{args.task}` has invalid scope_mode `{mode}`")

    assignment_scopes = value_list(assignment, "scope_files")
    allowed_write_roots = value_list(assignment, "allowed_write_roots")
    protected_paths = value_list(assignment, "protected_paths")
    write_patterns = assignment_write_patterns(assignment)

    if mode == SCOPE_MODE_EXACT and not assignment_scopes:
        findings.append(f"blocked_scope_missing: assignment `{args.task}` has no scope_files")
    if mode == SCOPE_MODE_BROAD and not write_patterns:
        findings.append(f"blocked_allowed_write_roots_missing: assignment `{args.task}` has no allowed_write_roots or scope_files")

    developer_scopes = value_list(developer, "allowed_scopes")
    if developer_scopes:
        for scope in write_patterns:
            scope_probe = scope.rstrip("/").replace("/**", "/placeholder")
            if not path_allowed(scope_probe, developer_scopes, plain_directories=True):
                findings.append(
                    f"blocked_assignment_scope_violation: assignment scope `{scope}` is outside developer allowed_scopes"
                )
    elif args.require_developer_scopes:
        findings.append(f"blocked_developer_scope_missing: developer `{args.developer}` has no allowed_scopes")

    for changed_file in args.files:
        if mode == SCOPE_MODE_BROAD and path_allowed(changed_file, protected_paths, plain_directories=True):
            if not path_allowed(changed_file, assignment_scopes):
                findings.append(
                    f"blocked_protected_path: `{changed_file}` matches protected_paths and is not explicitly listed in scope_files"
                )
                continue

        if mode == SCOPE_MODE_BROAD:
            is_allowed = path_allowed(changed_file, allowed_write_roots, plain_directories=True) or path_allowed(
                changed_file, assignment_scopes
            )
        else:
            is_allowed = path_allowed(changed_file, assignment_scopes)

        if not is_allowed:
            if mode == SCOPE_MODE_BROAD:
                findings.append(f"blocked_write_root_violation: `{changed_file}` is outside allowed_write_roots")
            else:
                findings.append(f"blocked_scope_violation: `{changed_file}` is outside assignment scope_files")

    return not findings, findings, details


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check manager-gated task authorization before development or CI merge."
    )
    parser.add_argument("state_dir", help="Path to the project's .claw directory")
    parser.add_argument("--developer", required=True, help="Developer id such as DEV-alice")
    parser.add_argument("--task", required=True, help="Task id such as TASK-001 or TASK-alice-001")
    parser.add_argument("--branch", default="", help="Current branch or PR head branch")
    parser.add_argument("--git-username", default="", help="Git platform username to match developer record")
    parser.add_argument(
        "--ssh-signing-key-fingerprint",
        default="",
        help="SSH commit signing key fingerprint to match developer record",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=[],
        help="Changed or intended file paths checked against scope_mode, allowed_write_roots, scope_files, and protected_paths",
    )
    parser.add_argument(
        "--require-developer-scopes",
        action="store_true",
        help="Block if the developer record does not declare allowed_scopes",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if Path(args.state_dir).name != ".claw":
        if args.json:
            print(
                json.dumps(
                    {
                        "status": "blocked",
                        "findings": ["blocked_state_directory: expected a .claw directory"],
                        "state_dir": args.state_dir,
                    },
                    indent=2,
                )
            )
        else:
            print("blocked:\n- blocked_state_directory: expected a .claw directory")
        return 1

    allowed, findings, details = check_authorization(args)

    if args.json:
        print(json.dumps({"status": "allowed" if allowed else "blocked", "findings": findings, **details}, indent=2))
    elif allowed:
        print(f"allowed: developer `{args.developer}` may work on `{args.task}`")
    else:
        print("blocked:")
        for finding in findings:
            print(f"- {finding}")

    return 0 if allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
