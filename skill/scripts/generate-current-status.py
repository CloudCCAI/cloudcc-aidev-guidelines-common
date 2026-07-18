#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from lib.atomic_io import atomic_write_text, file_lock
from lib.document_ids import TASK_BOARD_HEADER_RE, document_id_from_path, extract_feature_ids
from lib.language import choose, state_dir_language
from lib.state_io import clean_value, read_front_matter, utc_now


SECTION_HEADER_RE = re.compile(r"^##\s+(.+?)\s*$")
TASK_FIELD_RE = re.compile(r"^- ([a-z_]+):\s*(.+?)\s*$")
NEXT_ACTION_RE = re.compile(r"^-\s+Next action:\s*(.+?)\s*$", re.IGNORECASE)
TERMINAL_STATUSES = {"done", "canceled"}
ACTIVE_TASK_SECTIONS = {"Active Tasks", "活跃任务"}
EXECUTION_STATUS_GROUP = {
    "blocked": 0,
    "in_progress": 0,
    "ready": 1,
    "review": 1,
}
PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
INIT_DEFAULTS = {
    "init_status": "not_started",
    "init_completed_at": "none",
    "init_confirmed_by": "none",
}


@dataclass(frozen=True)
class Workflow:
    task_id: str
    title: str
    user: str
    feature_id: str
    work_type: str
    status: str
    branch: str
    next_action: str
    task_status_path: str
    priority: str = "medium"


def parse_task_board(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    cards: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    section = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        section_match = SECTION_HEADER_RE.match(line)
        if section_match:
            section = section_match.group(1).strip()
            continue
        header_match = TASK_BOARD_HEADER_RE.match(line)
        if header_match:
            current = {
                "task_id": header_match.group(1),
                "title": header_match.group(2).strip(),
                "section": section,
            }
            cards.append(current)
            continue
        if current is None:
            continue
        field_match = TASK_FIELD_RE.match(line.strip())
        if field_match:
            current[field_match.group(1)] = clean_value(field_match.group(2))
    return cards


def _safe_referenced_path(project_root: Path, raw_path: str) -> Path | None:
    if not raw_path or raw_path.lower() in {"none", "n/a"}:
        return None
    candidate = (project_root / raw_path).resolve()
    try:
        candidate.relative_to(project_root)
    except ValueError:
        return None
    return candidate


def resolve_task_status_path(project_root: Path, state_dir: Path, card: dict[str, str]) -> Path | None:
    referenced = _safe_referenced_path(project_root, card.get("task_status_path", ""))
    task_id = card["task_id"]
    if referenced and referenced.is_file():
        try:
            if document_id_from_path(referenced, "task") == task_id:
                return referenced
        except ValueError:
            pass
    matches: list[Path] = []
    for candidate in sorted((state_dir / "tasks").glob(f"{task_id}*.md")):
        try:
            if document_id_from_path(candidate, "task") == task_id:
                matches.append(candidate)
        except ValueError:
            continue
    return matches[0] if len(matches) == 1 else None


def _next_action(body: str, fallback: str) -> str:
    for raw_line in body.splitlines():
        match = NEXT_ACTION_RE.match(raw_line.strip())
        if match:
            return clean_value(match.group(1))
    return fallback or "none"


def collect_workflows(state_dir: Path) -> list[Workflow]:
    state_dir = Path(state_dir).resolve()
    if state_dir.name != ".claw":
        raise ValueError("current status generation only supports a .claw state directory")
    project_root = state_dir.parent
    workflows: list[Workflow] = []
    for card in parse_task_board(state_dir / "task-board.md"):
        if card.get("section") not in ACTIVE_TASK_SECTIONS or card.get("status", "").lower() in TERMINAL_STATUSES:
            continue
        task_path = resolve_task_status_path(project_root, state_dir, card)
        fields: dict[str, object] = {}
        body = ""
        if task_path:
            fields, body = read_front_matter(task_path)
            metadata_id = clean_value(fields.get("task_id"))
            if metadata_id:
                document_id_from_path(task_path, "task", metadata_id)

        spec_path = clean_value(card.get("spec_path", ""))
        feature_ids = extract_feature_ids(spec_path)
        feature_id = clean_value(fields.get("feature_id")) or (feature_ids[0] if feature_ids else "none")
        status = clean_value(fields.get("status")) or card.get("status", "unknown")
        if status.lower() in TERMINAL_STATUSES:
            continue
        user = (
            clean_value(fields.get("owner_slug"))
            or clean_value(fields.get("assignee"))
            or clean_value(card.get("claimed_by", ""))
            or clean_value(card.get("owner_role", "unassigned"))
        )
        workflows.append(
            Workflow(
                task_id=card["task_id"],
                title=card.get("title", card["task_id"]),
                user=user,
                feature_id=feature_id,
                work_type=clean_value(fields.get("task_type")) or clean_value(fields.get("work_type")) or "unknown",
                status=status,
                branch=clean_value(fields.get("branch")) or clean_value(card.get("branch", "n/a")),
                next_action=_next_action(body, clean_value(fields.get("next_action")) or card.get("next_action", "none")),
                task_status_path=task_path.relative_to(project_root).as_posix() if task_path else "missing",
                priority=clean_value(card.get("priority", "medium")).lower() or "medium",
            )
        )
    return order_workflows(workflows)


def order_workflows(workflows: list[Workflow]) -> list[Workflow]:
    """Prioritize active execution while preserving board order for ties."""

    return sorted(
        workflows,
        key=lambda item: (
            EXECUTION_STATUS_GROUP.get(item.status.lower(), 2),
            PRIORITY_RANK.get(item.priority.lower(), len(PRIORITY_RANK)),
        ),
    )


def _cell(value: str, *, limit: int = 72) -> str:
    cleaned = value.replace("|", "\\|").replace("\n", " ").strip()
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1] + "…"


def read_initialization_fields(path: Path) -> dict[str, str]:
    fields = dict(INIT_DEFAULTS)
    if not path.exists():
        return fields
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return fields
    for raw_line in lines[1:]:
        if raw_line.strip() == "---":
            break
        if raw_line[:1].isspace() or ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        if key in fields:
            fields[key] = clean_value(value) or fields[key]
    return fields


def render_current_status(
    workflows: list[Workflow],
    *,
    updated_by: str,
    limit: int = 10,
    initialization: dict[str, str] | None = None,
    language: str = "en",
) -> str:
    init_fields = dict(INIT_DEFAULTS)
    if initialization:
        init_fields.update({key: value for key, value in initialization.items() if key in init_fields})
    ordered_workflows = order_workflows(workflows)
    shown = ordered_workflows[: max(limit, 0)]
    truncated = len(shown) < len(workflows)
    next_action = shown[0].next_action if shown else choose(
        language,
        en="confirm the next project action",
        zh_cn="确认下一项项目工作",
    )
    lines = [
        "---",
        "kind: current-status",
        "schema_version: 5",
        f"init_status: {json.dumps(init_fields['init_status'], ensure_ascii=False)}",
        f"init_completed_at: {json.dumps(init_fields['init_completed_at'], ensure_ascii=False)}",
        f"init_confirmed_by: {json.dumps(init_fields['init_confirmed_by'], ensure_ascii=False)}",
        f"updated_at: {utc_now()}",
        f"updated_by: {json.dumps(updated_by, ensure_ascii=False)}",
        f"phase: {'active' if workflows else 'idle'}",
        f"active_task_count: {len(workflows)}",
        f"active_tasks_shown: {len(shown)}",
        f"active_tasks_truncated: {'true' if truncated else 'false'}",
        f"next_action: {json.dumps(_cell(next_action), ensure_ascii=False)}",
        "task_board: .claw/task-board.md",
    ]
    if shown:
        lines.append("active_tasks:")
        lines.extend(f"  - {workflow.task_id}" for workflow in shown)
    else:
        lines.append("active_tasks: []")
    lines.extend(
        [
            "---",
            "",
            choose(language, en="# Project Current Status", zh_cn="# 项目当前状态"),
            "",
            choose(
                language,
                en="`current-status.md` is a generated hot index. The linked source files remain authoritative.",
                zh_cn="`current-status.md` 是生成的热索引，所链接的事实源文件仍具有最终权威。",
            ),
            "",
            choose(language, en="## Active Workflows", zh_cn="## 活跃工作流"),
            "",
        ]
    )
    if shown:
        lines.extend(
            [
                choose(
                    language,
                    en="| User | Feature | Task | Type | Status | Branch | Next Action |",
                    zh_cn="| 用户 | 功能 | 任务 | 类型 | 状态 | 分支 | 下一步 |",
                ),
                "|---|---|---|---|---|---|---|",
            ]
        )
        for item in shown:
            lines.append(
                f"| {_cell(item.user)} | `{item.feature_id}` | `{item.task_id}` | `{item.work_type}` | `{item.status}` | `{item.branch}` | {_cell(item.next_action)} |"
            )
    else:
        lines.append(
            choose(
                language,
                en="- No active task. Do not create a placeholder task.",
                zh_cn="- 当前没有活跃任务，不要创建占位任务。",
            )
        )
    if truncated:
        remaining = len(workflows) - len(shown)
        lines.extend(
            [
                "",
                choose(
                    language,
                    en=f"- {remaining} more active task(s); read `.claw/task-board.md` for the full queue.",
                    zh_cn=f"- 另有 {remaining} 个活跃任务；读取 `.claw/task-board.md` 查看完整队列。",
                ),
            ]
        )
    lines.extend(
        [
            "",
            choose(language, en="## Read Next", zh_cn="## 按需读取"),
            "",
            choose(
                language,
                en="- `.claw/task-board.md` for queue membership, priority, dependencies, and references.",
                zh_cn="- 读取 `.claw/task-board.md` 获取队列归属、优先级、依赖和引用。",
            ),
            choose(
                language,
                en="- Only the selected task status and its referenced FEAT or issue.",
                zh_cn="- 只读取选中任务的状态，以及它引用的 FEAT 或问题。",
            ),
        ]
    )
    rendered = "\n".join(lines) + "\n"
    if len(rendered.splitlines()) > 60:
        raise ValueError("generated current-status.md exceeds the 60-line hot-file budget")
    return rendered


def write_current_status(state_dir: Path, rendered: str, *, lock_timeout: float = 10.0) -> Path:
    state_dir = Path(state_dir).resolve()
    if state_dir.name != ".claw":
        raise ValueError("current status generation only supports a .claw state directory")
    destination = state_dir / "current-status.md"
    with file_lock(state_dir / ".locks" / "current-status.lock", timeout=lock_timeout):
        atomic_write_text(destination, rendered)
    return destination


def generate_and_write_current_status(
    state_dir: Path,
    *,
    updated_by: str,
    limit: int = 10,
    lock_timeout: float = 10.0,
) -> tuple[Path, str]:
    """Collect, render, and replace the hot index under one project lock."""

    state_dir = Path(state_dir).resolve()
    if state_dir.name != ".claw":
        raise ValueError("current status generation only supports a .claw state directory")
    destination = state_dir / "current-status.md"
    with file_lock(state_dir / ".locks" / "current-status.lock", timeout=lock_timeout):
        workflows = collect_workflows(state_dir)
        initialization = read_initialization_fields(destination)
        rendered = render_current_status(
            workflows,
            updated_by=updated_by,
            limit=limit,
            initialization=initialization,
            language=state_dir_language(state_dir),
        )
        atomic_write_text(destination, rendered)
    return destination, rendered


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the .claw/current-status.md hot index from task sources.")
    parser.add_argument("state_dir", nargs="?", default=".claw", help="Path to the .claw state directory.")
    parser.add_argument("--updated-by", default="generate-current-status")
    parser.add_argument("--limit", type=int, default=10, help="Maximum active workflows to show. Defaults to 10.")
    parser.add_argument("--lock-timeout", type=float, default=10.0)
    parser.add_argument("--write", action="store_true", help="Atomically write .claw/current-status.md.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    state_dir = Path(args.state_dir)
    if not state_dir.is_dir():
        raise SystemExit(f"state directory does not exist: {state_dir}")
    if args.write:
        destination, _rendered = generate_and_write_current_status(
            state_dir,
            updated_by=args.updated_by,
            limit=args.limit,
            lock_timeout=args.lock_timeout,
        )
        print(f"Updated: {destination}")
    else:
        workflows = collect_workflows(state_dir)
        initialization = read_initialization_fields(state_dir / "current-status.md")
        rendered = render_current_status(
            workflows,
            updated_by=args.updated_by,
            limit=args.limit,
            initialization=initialization,
            language=state_dir_language(state_dir),
        )
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
