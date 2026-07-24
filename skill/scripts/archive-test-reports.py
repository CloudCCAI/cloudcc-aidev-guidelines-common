#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from lib.atomic_io import atomic_write_text, file_lock
from lib.state_io import clean_value, split_front_matter, utc_now


RECENT_REPORT_LIMIT = 5
RECENT_SECTIONS = {"Recent Test Records", "最近测试记录"}
PENDING_SECTIONS = {"Pending Verification", "待处理验证项"}
STRUCTURAL_SECTIONS = {
    "最新运行摘要",
    "Latest Run Summary",
    "结果汇总",
    "Result Summary",
    "失败项",
    "Failures",
    "维护规则",
    "Maintenance Rules",
    "历史摘要",
    "Historical Summary",
    "本次验证详情",
    "Current Verification Details",
    "历史验证详情",
    "Historical Verification Details",
    "常用测试命令",
    "Common Test Commands",
}
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
ENTRY_RE = re.compile(r"^###\s+(.+?)\s*$")
STATUS_RE = re.compile(r"(?<![A-Z_])(FAILED|FAIL|BLOCKED|PENDING|NOT_RUN)(?![A-Z_])", re.IGNORECASE)
TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$")
DIGEST_MARKER_RE = re.compile(r"<!-- test-report-entry-sha256:([0-9a-f]{64}) -->")


@dataclass(frozen=True)
class ReportEntry:
    title: str
    lines: tuple[str, ...]

    @property
    def digest(self) -> str:
        normalized = "\n".join(
            line
            for line in self.lines
            if not DIGEST_MARKER_RE.fullmatch(line.strip())
            and not line.startswith("- archived_at:")
        ).strip()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def archived_lines(self, timestamp: str) -> list[str]:
        lines = list(self.lines)
        lines.append(f"- archived_at: `{timestamp}`")
        lines.append(f"<!-- test-report-entry-sha256:{self.digest} -->")
        return lines


def find_section(lines: list[str], names: set[str]) -> tuple[int, int] | None:
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
    return None


def read_recent_entries(lines: list[str], start: int, end: int) -> list[ReportEntry]:
    headings = [
        index
        for index in range(start + 1, end)
        if ENTRY_RE.match(lines[index])
    ]
    entries: list[ReportEntry] = []
    for offset, index in enumerate(headings):
        next_index = headings[offset + 1] if offset + 1 < len(headings) else end
        raw_lines = lines[index:next_index]
        while raw_lines and not raw_lines[-1].strip():
            raw_lines.pop()
        match = ENTRY_RE.match(raw_lines[0])
        assert match is not None
        entries.append(ReportEntry(match.group(1), tuple(raw_lines)))
    return entries


def legacy_entries(lines: list[str]) -> list[tuple[int, int, ReportEntry]]:
    headings = [
        (index, match.group(1))
        for index, line in enumerate(lines)
        if (match := SECTION_RE.match(line)) and match.group(1) not in STRUCTURAL_SECTIONS
    ]
    entries: list[tuple[int, int, ReportEntry]] = []
    for offset, (index, title) in enumerate(headings):
        end = headings[offset + 1][0] if offset + 1 < len(headings) else len(lines)
        raw_lines = lines[index:end]
        while raw_lines and not raw_lines[-1].strip():
            raw_lines.pop()
        raw_lines[0] = f"### {title}"
        entries.append((index, end, ReportEntry(title, tuple(raw_lines))))
    return entries


def unresolved_counts(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for match in STATUS_RE.finditer(text):
        status = match.group(1).upper()
        counts["FAILED" if status == "FAIL" else status] += 1
    return counts


def unresolved_summary(counts: Counter[str], timestamp: str) -> str:
    ordered = [
        f"{status} {counts[status]}"
        for status in ("FAILED", "BLOCKED", "PENDING", "NOT_RUN")
        if counts[status]
    ]
    if not ordered:
        return f"- {timestamp} 归档批次未提取到未解决状态；任务和 issue 事实源保持权威。"
    return (
        f"- {timestamp} 归档批次包含：{' / '.join(ordered)}；"
        "详情见 `test-archive.md`，任务和 issue 事实源保持权威。"
    )


def front_matter_value(fields: dict[str, object], name: str, default: str) -> str:
    value = clean_value(fields.get(name, ""))
    return value or default


def normalized_utc_timestamp(value: str, default: str) -> str:
    if TIMESTAMP_RE.fullmatch(value):
        return value
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return default
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def render_current_report(
    fields: dict[str, object],
    entries: list[ReportEntry],
    *,
    timestamp: str,
    updated_by: str,
    pending_lines: list[str],
) -> str:
    last_run_at = normalized_utc_timestamp(
        front_matter_value(fields, "last_run_at", timestamp),
        timestamp,
    )
    last_run_status = front_matter_value(fields, "last_run_status", "partial")
    scope = entries[0].title if entries else "none"
    lines = [
        "---",
        "kind: test-report",
        "schema_version: 5",
        "version: 5",
        f"updated_at: {timestamp}",
        f"updated_by: {json.dumps(updated_by, ensure_ascii=False)}",
        f"last_run_at: {last_run_at}",
        f"last_run_status: {last_run_status}",
        "---",
        "",
        "# 测试报告",
        "",
        "`test-report.md` 保留最新摘要、待处理验证索引和最近 5 条详细记录；更早证据位于 `test-archive.md`。",
        "",
        "## 最新运行摘要",
        "",
        f"- 状态：`{last_run_status}`",
        f"- 范围：{scope}",
        f"- 最近运行：`{last_run_at}`",
        "",
        "## 待处理验证项",
        "",
    ]
    lines.extend(pending_lines or ["- 当前没有从归档批次提取出的未解决状态；任务和 issue 事实源保持权威。"])
    lines.extend(["", "## 最近测试记录", ""])
    for entry in entries:
        lines.extend(entry.lines)
        lines.append("")
    lines.extend(
        [
            "## 维护规则",
            "",
            "- 只记录真实执行过的命令、CI job 或等价验证。",
            "- 最近测试记录按从新到旧排列，最多保留 5 条。",
            "- 新增第 6 条后运行 `archive-test-reports.py .claw --write`。",
            "- `FAILED`、`BLOCKED`、`PENDING` 和 `NOT_RUN` 在归档时保留紧凑索引。",
            "- 不得把未执行的验证写成通过。",
            "",
        ]
    )
    return "\n".join(lines)


def empty_archive(timestamp: str, updated_by: str) -> str:
    return (
        "---\n"
        "kind: test-archive\n"
        "schema_version: 5\n"
        "version: 5\n"
        f"updated_at: {timestamp}\n"
        f"updated_by: {json.dumps(updated_by, ensure_ascii=False)}\n"
        "archive_status: active\n"
        "---\n\n"
        "# 测试报告归档\n\n"
        "`test-archive.md` 保存从 `test-report.md` 移出的完整历史验证证据，仅在追溯时读取。\n"
    )


def update_archive_front_matter(text: str, *, timestamp: str, updated_by: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("test-archive.md is missing YAML front matter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("test-archive.md has unclosed YAML front matter") from exc
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


def append_archive_batch(
    archive_text: str,
    *,
    timestamp: str,
    entries: list[ReportEntry] | None = None,
    legacy_text: str = "",
) -> str:
    existing_digests = set(DIGEST_MARKER_RE.findall(archive_text))
    batch_lines: list[str] = ["", f"## 归档批次 {timestamp}", ""]
    if legacy_text:
        digest = hashlib.sha256(legacy_text.encode("utf-8")).hexdigest()
        if digest in existing_digests:
            return archive_text
        batch_lines.extend(
            [
                "<!-- 以下内容按迁移前原顺序保存。 -->",
                legacy_text.rstrip(),
                f"<!-- test-report-entry-sha256:{digest} -->",
                "",
            ]
        )
    else:
        for entry in entries or []:
            if entry.digest in existing_digests:
                continue
            batch_lines.extend(entry.archived_lines(timestamp))
            batch_lines.append("")
    if len(batch_lines) == 3:
        return archive_text
    return archive_text.rstrip() + "\n" + "\n".join(batch_lines)


def pending_lines_from_normalized(body_lines: list[str]) -> list[str]:
    section = find_section(body_lines, PENDING_SECTIONS)
    if section is None:
        return []
    pending_start, pending_end = section
    return [
        line
        for line in body_lines[pending_start + 1 : pending_end]
        if line.strip().startswith("- ")
    ]


def archive_test_reports(
    state_dir: Path,
    *,
    timestamp: str,
    updated_by: str,
    write: bool,
) -> dict[str, object]:
    state_dir = state_dir.resolve()
    if state_dir.name != ".claw":
        raise ValueError(f"state directory must be named .claw: {state_dir}")
    report_path = state_dir / "test-report.md"
    archive_path = state_dir / "test-archive.md"
    legacy_archive_path = state_dir / "test-report-archive.md"
    if not report_path.is_file():
        raise ValueError(f"missing test report: {report_path}")
    if legacy_archive_path.exists():
        if archive_path.exists():
            raise ValueError(
                "both test-archive.md and legacy test-report-archive.md exist; keep only the canonical archive"
            )
        raise ValueError(
            "legacy test-report-archive.md exists; rename it to test-archive.md before writing"
        )

    lock_path = state_dir / ".locks" / "test-archive.lock"
    with file_lock(lock_path):
        report_text = report_path.read_text(encoding="utf-8")
        fields, body = split_front_matter(report_text)
        body_lines = body.splitlines()
        recent_section = find_section(body_lines, RECENT_SECTIONS)
        archive_text = (
            archive_path.read_text(encoding="utf-8")
            if archive_path.is_file()
            else empty_archive(timestamp, updated_by)
        )

        if recent_section is None:
            entries_with_ranges = legacy_entries(body_lines)
            if len(entries_with_ranges) <= RECENT_REPORT_LIMIT:
                return {
                    "changed": False,
                    "mode": "legacy",
                    "recent_count": len(entries_with_ranges),
                    "moved_count": 0,
                }
            recent_entries = [
                entry
                for _start, _end, entry in entries_with_ranges[:RECENT_REPORT_LIMIT]
            ]
            archive_start = entries_with_ranges[RECENT_REPORT_LIMIT][0]
            legacy_text = "\n".join(body_lines[archive_start:]).rstrip() + "\n"
            counts = unresolved_counts(legacy_text)
            pending_lines = [unresolved_summary(counts, timestamp)]
            next_report = render_current_report(
                fields,
                recent_entries,
                timestamp=timestamp,
                updated_by=updated_by,
                pending_lines=pending_lines,
            )
            next_archive = append_archive_batch(
                archive_text,
                timestamp=timestamp,
                legacy_text=legacy_text,
            )
            moved_count = len(entries_with_ranges) - RECENT_REPORT_LIMIT
            mode = "legacy_migration"
        else:
            recent_start, recent_end = recent_section
            entries = read_recent_entries(body_lines, recent_start, recent_end)
            overflow = entries[RECENT_REPORT_LIMIT:]
            if not overflow:
                return {
                    "changed": False,
                    "mode": "normalized",
                    "recent_count": len(entries),
                    "moved_count": 0,
                }
            pending_lines = pending_lines_from_normalized(body_lines)
            pending_lines.append(
                unresolved_summary(
                    unresolved_counts("\n".join(line for entry in overflow for line in entry.lines)),
                    timestamp,
                )
            )
            next_report = render_current_report(
                fields,
                entries[:RECENT_REPORT_LIMIT],
                timestamp=timestamp,
                updated_by=updated_by,
                pending_lines=pending_lines,
            )
            next_archive = append_archive_batch(
                archive_text,
                timestamp=timestamp,
                entries=overflow,
            )
            moved_count = len(overflow)
            mode = "normalized"

        next_archive = update_archive_front_matter(
            next_archive,
            timestamp=timestamp,
            updated_by=updated_by,
        )
        if write:
            atomic_write_text(archive_path, next_archive)
            atomic_write_text(report_path, next_report)
        return {
            "changed": True,
            "mode": mode,
            "recent_count": RECENT_REPORT_LIMIT,
            "moved_count": moved_count,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Keep five recent detailed test records and archive older verification evidence."
    )
    parser.add_argument("state_dir", help="Path to the project .claw directory")
    parser.add_argument("--write", action="store_true", help="Persist report and archive updates")
    parser.add_argument("--updated-by", default="archive-test-reports")
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
        result = archive_test_reports(
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
        action = "Archived" if args.write else "Would archive"
        print(f"{action} {result['moved_count']} test record(s); kept {result['recent_count']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
