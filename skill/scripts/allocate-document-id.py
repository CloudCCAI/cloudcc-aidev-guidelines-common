#!/usr/bin/env python3

from __future__ import annotations

import argparse
import getpass
import json
import re
import subprocess
from pathlib import Path

from lib.document_ids import document_id_from_path, is_feature_id, is_legacy_id, reserve_document
from lib.state_io import clean_value, read_front_matter, utc_now


SKILL_ROOT = Path(__file__).resolve().parent.parent
CONFIRMED_FEATURE_STATUSES = {"approved", "in_implementation", "implemented", "verified"}


def global_git_user_name() -> str:
    result = subprocess.run(
        ["git", "config", "--global", "--get", "user.name"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def project_git_user_name(project_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(project_root), "config", "--local", "--get", "user.name"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def default_content(
    args: argparse.Namespace,
    owner: str,
    created_by: str,
    created_by_source: str,
) -> str:
    timestamp = utc_now()
    title = args.title or args.description.replace("-", " ").strip().title()
    template_name = "feature-spec.md" if args.kind == "feature" else "task-status.md"
    template_path = SKILL_ROOT / "templates" / "project-state" / template_name
    content = template_path.read_text(encoding="utf-8")

    def quoted_inner(value: str) -> str:
        return json.dumps(value.replace("\r", " ").replace("\n", " "), ensure_ascii=False)[1:-1]

    replacements = {
        "FEATURE_ID": "{{DOCUMENT_ID}}" if args.kind == "feature" else (args.feature_id or "none"),
        "TASK_ID": "{{DOCUMENT_ID}}",
        "WORK_TYPE": args.work_type,
        "TASK_TYPE": args.task_type,
        "TITLE": quoted_inner(title),
        "TIMESTAMP": timestamp,
        "CREATED_BY": quoted_inner(created_by),
        "CREATED_BY_SLUG": "{{OWNER_SLUG}}",
        "CREATED_BY_SOURCE": created_by_source,
        "CREATED_BY_DEVELOPER_ID": "none",
        "ASSIGNEE": "{{OWNER_SLUG}}",
        "OWNER_ROLE": "shared",
        "NEXT_ACTION": quoted_inner(args.next_action),
    }
    for key, value in replacements.items():
        content = content.replace("{{" + key + "}}", value)
    unresolved = {
        match
        for match in re.findall(r"\{\{([A-Z0-9_]+)\}\}", content)
        if match not in {"DOCUMENT_ID", "OWNER_SLUG", "DESCRIPTION_SLUG"}
    }
    if unresolved:
        raise SystemExit(f"default template has unresolved values: {', '.join(sorted(unresolved))}")
    return content


def require_confirmed_feature(project_root: Path, feature_id: str) -> Path:
    if not is_feature_id(feature_id):
        raise SystemExit(f"invalid feature id: {feature_id}")
    candidates: list[Path] = []
    for path in sorted((project_root / "docs" / "specs").glob(f"{feature_id}*.md")):
        try:
            fields, _body = read_front_matter(path)
            metadata_id = clean_value(fields.get("feature_id"))
            if document_id_from_path(path, "feature", metadata_id or None) == feature_id:
                candidates.append(path)
        except (OSError, ValueError):
            continue
    if len(candidates) != 1:
        raise SystemExit(f"feature id must resolve to one existing spec before task creation: {feature_id}")
    feature_path = candidates[0]
    if not is_legacy_id(feature_id):
        fields, _body = read_front_matter(feature_path)
        init_status = clean_value(fields.get("init_status"))
        status = clean_value(fields.get("status"))
        if init_status != "complete" or status not in CONFIRMED_FEATURE_STATUSES:
            raise SystemExit(
                f"feature must be user-confirmed before task creation: {feature_id} "
                f"(init_status={init_status or 'missing'}, status={status or 'missing'})"
            )
    return feature_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Allocate and exclusively create a v5 FEAT or TASK document under one .claw project."
    )
    parser.add_argument("kind", choices=("feature", "task"))
    parser.add_argument("--project-root", default=".", help="Project root containing .claw. Defaults to cwd.")
    parser.add_argument(
        "--owner",
        help=(
            "Explicit stable owner namespace. Defaults to global Git user.name, "
            "then project-local Git user.name, then the OS user."
        ),
    )
    parser.add_argument("--description", required=True, help="Short description used in the filename.")
    parser.add_argument("--title", help="Human-readable document title.")
    parser.add_argument("--created-by", help="Display name for document attribution.")
    parser.add_argument("--content-file", help="Optional UTF-8 template containing {{DOCUMENT_ID}} placeholders.")
    parser.add_argument("--work-type", default="new_feature", help="Feature work_type value.")
    parser.add_argument("--task-type", default="feature", help="Task task_type value.")
    parser.add_argument("--feature-id", help="Canonical FEAT id for a task, or omit for none.")
    parser.add_argument("--next-action", default="定义下一项可执行步骤")
    parser.add_argument("--lock-timeout", type=float, default=10.0)
    parser.add_argument("--json", action="store_true", help="Print the allocation as JSON.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    project_root = Path(args.project_root).resolve()
    global_git_owner = global_git_user_name() if not args.owner else ""
    project_git_owner = project_git_user_name(project_root) if not args.owner and not global_git_owner else ""
    if args.owner:
        owner = args.owner
        created_by_source = "user_confirmed"
    elif global_git_owner:
        owner = global_git_owner
        created_by_source = "global_git_config_user_name"
    elif project_git_owner:
        owner = project_git_owner
        created_by_source = "project_git_config_user_name"
    else:
        owner = getpass.getuser()
        created_by_source = "os_user"
    created_by = args.created_by or owner
    if args.kind == "task" and args.feature_id:
        require_confirmed_feature(project_root, args.feature_id)
    if args.content_file:
        content = Path(args.content_file).read_text(encoding="utf-8")
    else:
        content = default_content(args, owner, created_by, created_by_source)

    allocation = reserve_document(
        project_root,
        kind=args.kind,
        owner=owner,
        description=args.description,
        content=content,
        lock_timeout=args.lock_timeout,
    )
    result = {
        "kind": allocation.kind,
        "document_id": allocation.document_id,
        "owner_slug": allocation.owner_slug,
        "number": allocation.number,
        "path": allocation.path.relative_to(project_root).as_posix(),
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"Allocated {allocation.document_id}: {result['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
