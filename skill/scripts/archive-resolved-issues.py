#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from lib.atomic_io import atomic_write_text, file_lock
from lib.state_io import clean_value, split_front_matter, utc_now


RECENT_CLOSED_LIMIT = 5
TERMINAL_STATUSES = {"verified", "closed"}
ISSUE_RE = re.compile(r"^###\s+(ISSUE-[A-Za-z0-9-]+)\s+[—-]\s+(.+?)\s*$")
STATUS_RE = re.compile(
    r"(?:状态：|status:\s*)`(open|in_progress|blocked|fixed|verified|closed)`",
    re.IGNORECASE,
)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$")
ACTIVE_SECTIONS = {"活跃问题", "Active Issues"}
RECENT_CLOSED_SECTIONS = {"最近关闭问题", "Recently Closed Issues"}
ARCHIVED_SECTIONS = {"已归档问题", "Archived Issues"}
MAINTENANCE_SECTIONS = {"维护规则", "Maintenance Rules"}


@dataclass(frozen=True)
class IssueCard:
    issue_id: str
    title: str
    lines: tuple[str, ...]

    @property
    def status(self) -> str:
        for line in self.lines[1:]:
            match = STATUS_RE.search(line)
            if match:
                return match.group(1).lower()
        return ""

    def archived(self, timestamp: str) -> "IssueCard":
        if any(line.startswith("- archived_at:") for line in self.lines):
            return self
        return IssueCard(
            self.issue_id,
            self.title,
            self.lines + (f"- archived_at: `{timestamp}`",),
        )


def issue_cards(lines: list[str]) -> list[IssueCard]:
    headings = [
        index
        for index, line in enumerate(lines)
        if ISSUE_RE.match(line)
    ]
    cards: list[IssueCard] = []
    for offset, index in enumerate(headings):
        next_issue = headings[offset + 1] if offset + 1 < len(headings) else len(lines)
        next_section = next(
            (
                candidate
                for candidate in range(index + 1, next_issue)
                if SECTION_RE.match(lines[candidate])
            ),
            next_issue,
        )
        raw_lines = lines[index:next_section]
        trailing_rules = next(
            (
                candidate
                for candidate, line in enumerate(raw_lines)
                if line.startswith("- 发现新问题") or line.startswith("- Record a new issue")
            ),
            len(raw_lines),
        )
        raw_lines = raw_lines[:trailing_rules]
        while raw_lines and not raw_lines[-1].strip():
            raw_lines.pop()
        match = ISSUE_RE.match(raw_lines[0])
        assert match is not None
        cards.append(IssueCard(match.group(1), match.group(2), tuple(raw_lines)))
    return cards


def section_body(lines: list[str], names: set[str]) -> list[str]:
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
        body = lines[index + 1 : end]
        first_issue = next(
            (candidate for candidate, value in enumerate(body) if ISSUE_RE.match(value)),
            len(body),
        )
        before_issue = body[:first_issue]
        trailing_rules = next(
            (
                candidate
                for candidate in range(first_issue, len(body))
                if body[candidate].startswith("- 发现新问题")
                or body[candidate].startswith("- Record a new issue")
            ),
            len(body),
        )
        after_issue = body[trailing_rules:]
        result = before_issue + after_issue
        while result and not result[0].strip():
            result.pop(0)
        while result and not result[-1].strip():
            result.pop()
        return result
    return []


def front_matter_value(fields: dict[str, object], name: str, default: str) -> str:
    value = clean_value(fields.get(name, ""))
    return value or default


def render_current(
    fields: dict[str, object],
    active_cards: list[IssueCard],
    archived_cards: list[IssueCard],
    *,
    timestamp: str,
    updated_by: str,
    maintenance_lines: list[str],
) -> str:
    lines = [
        "---",
        "kind: issue-list",
        "schema_version: 5",
        "version: 5",
        f"updated_at: {timestamp}",
        f"updated_by: {json.dumps(updated_by, ensure_ascii=False)}",
        "---",
        "",
        "# 问题追踪列表",
        "",
        "`issue-list.md` 保留未闭环问题和最近 5 条关闭索引；完整终态记录位于 `issue-archive.md`。",
        "",
        "推荐严重级别：`critical` / `high` / `medium` / `low`  ",
        "推荐状态值：`open` / `in_progress` / `blocked` / `fixed` / `verified` / `closed`",
        "",
        "## 活跃问题",
        "",
    ]
    for card in active_cards:
        lines.extend(card.lines)
        lines.append("")
    if not active_cards:
        lines.extend(["- 暂无。", ""])

    lines.extend(["## 最近关闭问题", ""])
    for card in archived_cards[:RECENT_CLOSED_LIMIT]:
        lines.append(
            f"- `{card.issue_id}` — {card.title}；状态：`{card.status}`；详情见 `issue-archive.md`。"
        )
    if not archived_cards:
        lines.append("- 暂无。")

    lines.extend(["", "## 维护规则", ""])
    lines.extend(
        maintenance_lines
        or [
            "- 现象、影响、根因状态和阻塞信息以本文件为准。",
            "- 只有 `verified` 或 `closed` 问题可以移入归档。",
            "- `fixed` 仍表示待验证，必须保留在活跃问题中。",
            "- 修复设计、变更范围、验收标准和回归策略写入关联 FEAT。",
        ]
    )
    lines.extend(
        [
            "- 问题进入终态后运行 `archive-resolved-issues.py .claw --write`。",
            "",
        ]
    )
    return "\n".join(lines)


def empty_archive(timestamp: str, updated_by: str) -> str:
    return (
        "---\n"
        "kind: issue-archive\n"
        "schema_version: 5\n"
        "version: 5\n"
        f"updated_at: {timestamp}\n"
        f"updated_by: {json.dumps(updated_by, ensure_ascii=False)}\n"
        "archive_status: active\n"
        "---\n\n"
        "# 问题归档\n\n"
        "`issue-archive.md` 保存从 `issue-list.md` 移出的完整 `verified` 或 `closed` 问题记录，仅在追溯时读取。\n\n"
        "## 已归档问题\n\n"
        "## 维护规则\n\n"
        "- 只归档状态为 `verified` 或 `closed` 的问题。\n"
        "- 归档保留原始证据、根因、修复和验证信息。\n"
    )


def update_front_matter(text: str, *, timestamp: str, updated_by: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("issue-archive.md is missing YAML front matter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("issue-archive.md has unclosed YAML front matter") from exc
    replacements = {
        "updated_at": timestamp,
        "updated_by": json.dumps(updated_by, ensure_ascii=False),
    }
    for key, value in replacements.items():
        for index in range(1, end):
            if lines[index].startswith(f"{key}:"):
                lines[index] = f"{key}: {value}"
                break
        else:
            lines.insert(end, f"{key}: {value}")
            end += 1
    return "\n".join(lines) + "\n"


def render_archive(
    archive_text: str,
    cards: list[IssueCard],
    *,
    timestamp: str,
    updated_by: str,
) -> str:
    lines = archive_text.splitlines()
    section_start = next(
        (
            index
            for index, line in enumerate(lines)
            if (match := SECTION_RE.match(line)) and match.group(1) in ARCHIVED_SECTIONS
        ),
        -1,
    )
    if section_start < 0:
        raise ValueError("issue-archive.md is missing `已归档问题` section")
    section_end = next(
        (
            index
            for index in range(section_start + 1, len(lines))
            if SECTION_RE.match(lines[index])
        ),
        len(lines),
    )
    rendered = [""]
    for card in cards:
        rendered.extend(card.lines)
        rendered.append("")
    next_text = "\n".join(lines[: section_start + 1] + rendered + lines[section_end:]) + "\n"
    return update_front_matter(next_text, timestamp=timestamp, updated_by=updated_by)


def archive_resolved_issues(
    state_dir: Path,
    *,
    timestamp: str,
    updated_by: str,
    write: bool,
) -> dict[str, object]:
    state_dir = state_dir.resolve()
    if state_dir.name != ".claw":
        raise ValueError(f"state directory must be named .claw: {state_dir}")
    issue_path = state_dir / "issue-list.md"
    archive_path = state_dir / "issue-archive.md"
    if not issue_path.is_file():
        raise ValueError(f"missing issue list: {issue_path}")

    with file_lock(state_dir / ".locks" / "issue-archive.lock"):
        issue_text = issue_path.read_text(encoding="utf-8")
        fields, _body = split_front_matter(issue_text)
        cards = issue_cards(issue_text.splitlines())
        missing_status = [card.issue_id for card in cards if not card.status]
        if missing_status:
            raise ValueError(f"issues missing a recognized status: {', '.join(missing_status)}")

        terminal_cards = [card for card in cards if card.status in TERMINAL_STATUSES]
        normalized = (
            front_matter_value(fields, "schema_version", "") == "5"
            and "## 最近关闭问题" in issue_text
        )
        if not terminal_cards and not archive_path.is_file():
            return {
                "changed": False,
                "active_count": len(cards),
                "archived_count": 0,
                "moved": [],
            }
        if not terminal_cards and normalized:
            archive_cards = (
                issue_cards(archive_path.read_text(encoding="utf-8").splitlines())
                if archive_path.is_file()
                else []
            )
            return {
                "changed": False,
                "active_count": len(cards),
                "archived_count": len(archive_cards),
                "moved": [],
            }

        archive_text = (
            archive_path.read_text(encoding="utf-8")
            if archive_path.is_file()
            else empty_archive(timestamp, updated_by)
        )
        existing_archive_cards = issue_cards(archive_text.splitlines())
        existing_ids = {card.issue_id for card in existing_archive_cards}
        new_archive_cards = [
            card.archived(timestamp)
            for card in terminal_cards
            if card.issue_id not in existing_ids
        ]
        all_archive_cards = new_archive_cards + existing_archive_cards
        active_cards = [card for card in cards if card.status not in TERMINAL_STATUSES]
        maintenance_lines = section_body(issue_text.splitlines(), MAINTENANCE_SECTIONS)

        next_issue = render_current(
            fields,
            active_cards,
            all_archive_cards,
            timestamp=timestamp,
            updated_by=updated_by,
            maintenance_lines=maintenance_lines,
        )
        next_archive = render_archive(
            archive_text,
            all_archive_cards,
            timestamp=timestamp,
            updated_by=updated_by,
        )
        if write:
            atomic_write_text(archive_path, next_archive)
            atomic_write_text(issue_path, next_issue)
        return {
            "changed": True,
            "active_count": len(active_cards),
            "archived_count": len(all_archive_cards),
            "moved": [card.issue_id for card in terminal_cards],
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Move verified or closed issues into issue-archive.md."
    )
    parser.add_argument("state_dir", help="Path to the project .claw directory")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--updated-by", default="archive-resolved-issues")
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
        result = archive_resolved_issues(
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
        print(f"{action} {len(result['moved'])} issue(s); {result['active_count']} remain active.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
