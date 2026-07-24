#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from lib.atomic_io import atomic_write_text, file_lock
from lib.state_io import clean_value, utc_now


COMPLETED_TASK_LIMIT = 5
COMPLETED_SECTIONS = {"Completed Tasks", "已完成任务"}
ARCHIVED_SECTIONS = {"Archived Tasks", "已归档任务"}
TERMINAL_STATUSES = {"done", "canceled"}
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
TASK_RE = re.compile(r"^###\s+(TASK-[A-Za-z0-9-]+)\s+-\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^-\s+([a-z_]+):\s*(.+?)\s*$")
TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$")


@dataclass(frozen=True)
class TaskCard:
    task_id: str
    title: str
    lines: tuple[str, ...]

    def field(self, name: str) -> str:
        for line in self.lines[1:]:
            match = FIELD_RE.match(line)
            if match and match.group(1) == name:
                return clean_value(match.group(2))
        return ""

    def archived(self, timestamp: str) -> "TaskCard":
        if self.field("archived_at"):
            return self
        lines = list(self.lines)
        lines.append(f"- archived_at: `{timestamp}`")
        return TaskCard(self.task_id, self.title, tuple(lines))


def find_section(lines: list[str], names: set[str]) -> tuple[int, int]:
    for index, line in enumerate(lines):
        match = SECTION_RE.match(line)
        if not match or match.group(1) not in names:
            continue
        end = next(
            (
                candidate
                for candidate in range(index + 1, len(lines))
                if SECTION_RE.match(lines[candidate])
            ),
            len(lines),
        )
        return index, end
    expected = " or ".join(sorted(names))
    raise ValueError(f"missing section: {expected}")


def read_cards(lines: list[str], start: int, end: int) -> list[TaskCard]:
    headings = [
        index
        for index in range(start + 1, end)
        if TASK_RE.match(lines[index])
    ]
    cards: list[TaskCard] = []
    for offset, index in enumerate(headings):
        next_index = headings[offset + 1] if offset + 1 < len(headings) else end
        raw_lines = lines[index:next_index]
        while raw_lines and not raw_lines[-1].strip():
            raw_lines.pop()
        match = TASK_RE.match(raw_lines[0])
        assert match is not None
        cards.append(TaskCard(match.group(1), match.group(2), tuple(raw_lines)))
    return cards


def render_section(cards: list[TaskCard]) -> list[str]:
    rendered = [""]
    for card in cards:
        rendered.extend(card.lines)
        rendered.append("")
    return rendered


def replace_section(
    lines: list[str],
    start: int,
    end: int,
    cards: list[TaskCard],
) -> list[str]:
    return lines[: start + 1] + render_section(cards) + lines[end:]


def update_front_matter(text: str, *, timestamp: str, updated_by: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("state file is missing YAML front matter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("state file has unclosed YAML front matter") from exc

    replacements = {
        "updated_at": timestamp,
        "updated_by": json.dumps(updated_by, ensure_ascii=False),
    }
    found: set[str] = set()
    for index in range(1, end):
        if ":" not in lines[index] or lines[index][:1].isspace():
            continue
        key = lines[index].split(":", 1)[0].strip()
        if key in replacements:
            lines[index] = f"{key}: {replacements[key]}"
            found.add(key)
    for key in ("updated_at", "updated_by"):
        if key not in found:
            lines.insert(end, f"{key}: {replacements[key]}")
            end += 1
    return "\n".join(lines) + "\n"


def empty_archive(timestamp: str, updated_by: str) -> str:
    return (
        "---\n"
        "kind: task-archive\n"
        "schema_version: 5\n"
        f"updated_at: {timestamp}\n"
        f"updated_by: {json.dumps(updated_by, ensure_ascii=False)}\n"
        "archive_status: active\n"
        "---\n\n"
        "# 任务归档\n\n"
        "`task-archive.md` 保存从 `task-board.md` 中移出的已完成或已取消任务卡。\n\n"
        "## 已归档任务\n\n"
        "## 维护规则\n\n"
        "- 只归档 `done` 或 `canceled` 任务。\n"
        "- 归档是从 task board 移动索引卡，不删除任务事实文件。\n"
    )


def archive_completed_tasks(
    state_dir: Path,
    *,
    timestamp: str,
    updated_by: str,
    write: bool,
) -> dict[str, object]:
    state_dir = state_dir.resolve()
    if state_dir.name != ".claw":
        raise ValueError(f"state directory must be named .claw: {state_dir}")
    board_path = state_dir / "task-board.md"
    archive_path = state_dir / "task-archive.md"
    if not board_path.is_file():
        raise ValueError(f"missing task board: {board_path}")

    lock_path = state_dir / ".locks" / "task-archive.lock"
    with file_lock(lock_path):
        board_text = board_path.read_text(encoding="utf-8")
        board_lines = board_text.splitlines()
        completed_start, completed_end = find_section(board_lines, COMPLETED_SECTIONS)
        completed_cards = read_cards(board_lines, completed_start, completed_end)
        overflow = completed_cards[COMPLETED_TASK_LIMIT:]
        if not overflow:
            return {
                "changed": False,
                "completed_count": len(completed_cards),
                "kept_count": len(completed_cards),
                "moved": [],
            }

        for card in overflow:
            status = card.field("status")
            if status not in TERMINAL_STATUSES:
                raise ValueError(
                    f"cannot archive {card.task_id}: expected done or canceled, got {status or 'missing'}"
                )

        archive_text = (
            archive_path.read_text(encoding="utf-8")
            if archive_path.is_file()
            else empty_archive(timestamp, updated_by)
        )
        archive_lines = archive_text.splitlines()
        archived_start, archived_end = find_section(archive_lines, ARCHIVED_SECTIONS)
        archived_cards = read_cards(archive_lines, archived_start, archived_end)
        archived_ids = {card.task_id for card in archived_cards}
        new_cards = [
            card.archived(timestamp)
            for card in overflow
            if card.task_id not in archived_ids
        ]

        next_archive_lines = replace_section(
            archive_lines,
            archived_start,
            archived_end,
            new_cards + archived_cards,
        )
        next_archive = update_front_matter(
            "\n".join(next_archive_lines) + "\n",
            timestamp=timestamp,
            updated_by=updated_by,
        )
        next_board_lines = replace_section(
            board_lines,
            completed_start,
            completed_end,
            completed_cards[:COMPLETED_TASK_LIMIT],
        )
        next_board = update_front_matter(
            "\n".join(next_board_lines) + "\n",
            timestamp=timestamp,
            updated_by=updated_by,
        )

        if write:
            atomic_write_text(archive_path, next_archive)
            atomic_write_text(board_path, next_board)

        return {
            "changed": True,
            "completed_count": len(completed_cards),
            "kept_count": COMPLETED_TASK_LIMIT,
            "moved": [card.task_id for card in overflow],
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Move completed task-board cards beyond the newest five into task-archive.md."
    )
    parser.add_argument("state_dir", help="Path to the project .claw directory")
    parser.add_argument("--write", action="store_true", help="Persist the archive and task-board updates")
    parser.add_argument("--updated-by", default="archive-completed-tasks")
    parser.add_argument("--now", default="", help="Override time using YYYY-MM-DD HH:MM:SS")
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    timestamp = args.now or utc_now()
    if not TIMESTAMP_RE.fullmatch(timestamp):
        parser.error("--now must use YYYY-MM-DD HH:MM:SS")
    try:
        result = archive_completed_tasks(
            Path(args.state_dir),
            timestamp=timestamp,
            updated_by=args.updated_by,
            write=args.write,
        )
    except (OSError, ValueError, TimeoutError) as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        action = "Moved" if args.write else "Would move"
        print(f"{action} {len(result['moved'])} task(s); kept {result['kept_count']} completed task(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
