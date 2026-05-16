#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


TASK_HEADER_RE = re.compile(r"^###\s+(TASK-[0-9]+)\s+-\s+(.+?)\s*$")
TASK_FIELD_RE = re.compile(r"^- ([a-z_]+):\s*(.+?)\s*$")
SECTION_HEADER_RE = re.compile(r"^##\s+(.+?)\s*$")
YAML_FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$")


def clean_value(value: str) -> str:
    cleaned = value.strip().strip('"').strip("'")
    if cleaned.startswith("`") and cleaned.endswith("`") and len(cleaned) >= 2:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def is_empty(value: str | None) -> bool:
    if value is None:
        return True
    return clean_value(value).lower() in {"", "none", "n/a", "na", "not_applicable"}


def read_simple_yaml(path: Path) -> dict[str, object]:
    parsed: dict[str, object] = {}
    current_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        stripped = raw_line.strip()
        if current_key and stripped.startswith("- "):
            current_value = parsed.setdefault(current_key, [])
            if isinstance(current_value, list):
                current_value.append(clean_value(stripped[2:]))
            continue

        match = YAML_FIELD_RE.match(stripped)
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

    return parsed


def read_front_matter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if len(lines) < 3 or lines[0].strip() != "---":
        return {}, text

    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, text

    front_matter: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        front_matter[key.strip()] = clean_value(value)

    return front_matter, "\n".join(lines[end + 1 :])


def parse_task_board(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}

    tasks: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    current_id = ""
    current_section = ""

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        section_match = SECTION_HEADER_RE.match(line)
        if section_match:
            current_section = section_match.group(1).strip()

        header_match = TASK_HEADER_RE.match(line)
        if header_match:
            current_id = header_match.group(1)
            current = {
                "task_id": current_id,
                "title": header_match.group(2).strip(),
                "section": current_section,
            }
            tasks[current_id] = current
            continue

        if current is None:
            continue

        field_match = TASK_FIELD_RE.match(line.strip())
        if field_match:
            current[field_match.group(1)] = clean_value(field_match.group(2))

    return tasks


def parse_integration_queue(path: Path) -> dict[str, str]:
    task_status: dict[str, str] = {}
    if not path.exists():
        return task_status

    current_status = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("- status:"):
            current_status = clean_value(stripped.split(":", 1)[1])
        if stripped.startswith("- related_tasks:") or stripped.startswith("- merge_order:"):
            raw_tasks = clean_value(stripped.split(":", 1)[1])
            for task_id in re.findall(r"TASK-[0-9]+", raw_tasks):
                if current_status:
                    task_status[task_id] = current_status

    return task_status


def list_yaml_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(path.glob("*.yaml")) + sorted(path.glob("*.yml"))


def load_developers(state_dir: Path) -> dict[str, dict[str, object]]:
    developers: dict[str, dict[str, object]] = {}
    for path in list_yaml_files(state_dir / "developers"):
        fields = read_simple_yaml(path)
        developer_id = str(fields.get("developer_id") or path.stem)
        fields["path"] = str(path)
        developers[developer_id] = fields
    return developers


def load_assignments(state_dir: Path) -> list[dict[str, object]]:
    assignments: list[dict[str, object]] = []
    for path in list_yaml_files(state_dir / "assignments"):
        fields = read_simple_yaml(path)
        fields["path"] = str(path)
        if "task_id" not in fields:
            fields["task_id"] = path.stem
        assignments.append(fields)
    return assignments


def load_task_statuses(state_dir: Path) -> dict[str, dict[str, str]]:
    statuses: dict[str, dict[str, str]] = {}
    tasks_dir = state_dir / "tasks"
    if not tasks_dir.exists():
        return statuses

    for path in sorted(tasks_dir.glob("*.md")):
        front_matter, body = read_front_matter(path)
        task_id = front_matter.get("task_id") or path.stem
        front_matter["path"] = str(path)
        front_matter["validation_status"] = extract_validation_status(body)
        statuses[task_id] = front_matter

    return statuses


def extract_validation_status(body: str) -> str:
    in_validation = False
    for raw_line in body.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("## "):
            in_validation = "验证" in stripped or "Validation" in stripped
            continue
        if not in_validation:
            continue
        if "状态" in stripped or "结果" in stripped or "status" in stripped.lower() or "result" in stripped.lower():
            lowered = stripped.lower()
            for status in ("passed", "failed", "partial", "not_run", "unknown"):
                if status in lowered:
                    return status
    return "unknown"


def derive_contribution_status(assignment: dict[str, object], task_status: dict[str, str] | None) -> str:
    if not task_status:
        return "assigned"

    status = clean_value(task_status.get("status", ""))
    pr_url = task_status.get("pr_url") or str(assignment.get("pr_url", ""))

    if status in {"todo", "ready"}:
        return "claimed"
    if status == "in_progress":
        return "code_submitted" if not is_empty(pr_url) else "in_progress"
    if status == "review":
        return "review_requested"
    if status == "done":
        return "merged"
    if status == "blocked":
        return "blocked"
    if status == "canceled":
        return "canceled"
    return status or "not_started"


def derive_integration_status(task_id: str, contribution_status: str, integration_statuses: dict[str, str]) -> str:
    queue_status = integration_statuses.get(task_id, "")
    if queue_status in {"merging", "verifying"}:
        return "merging"
    if queue_status in {"ready", "collecting"}:
        return "ready_to_merge"
    if queue_status == "completed":
        return "integrated"
    if queue_status == "blocked" or contribution_status == "blocked":
        return "blocked"
    if contribution_status in {"review_requested", "code_submitted"}:
        return "waiting_review"
    if contribution_status == "merged":
        return "integrated"
    return "not_ready"


def csv_join(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def render_team_status(state_dir: Path) -> str:
    developers = load_developers(state_dir)
    assignments = load_assignments(state_dir)
    task_statuses = load_task_statuses(state_dir)
    task_board = parse_task_board(state_dir / "task-board.md")
    integration_statuses = parse_integration_queue(state_dir / "integration-queue.md")

    assignments_by_developer: dict[str, list[dict[str, object]]] = defaultdict(list)
    for assignment in assignments:
        assignee = str(assignment.get("assignee", "unassigned"))
        assignments_by_developer[assignee].append(assignment)
        if assignee not in developers and assignee != "unassigned":
            developers[assignee] = {
                "developer_id": assignee,
                "display_name": assignee,
                "role": "unassigned",
                "status": "unknown",
                "path": "not_found",
            }

    task_rows: list[dict[str, str]] = []
    for assignment in assignments:
        task_id = str(assignment.get("task_id", "unknown"))
        assignee = str(assignment.get("assignee", "unassigned"))
        task_status = task_statuses.get(task_id)
        contribution_status = derive_contribution_status(assignment, task_status)
        validation_status = task_status.get("validation_status", "unknown") if task_status else "unknown"
        integration_status = derive_integration_status(task_id, contribution_status, integration_statuses)
        board = task_board.get(task_id, {})

        task_rows.append(
            {
                "task_id": task_id,
                "title": board.get("title", "unknown"),
                "assignee": assignee,
                "board_status": board.get("status", "unknown"),
                "contribution_status": contribution_status,
                "validation_status": validation_status,
                "integration_status": integration_status,
                "branch": str(task_status.get("branch") if task_status else assignment.get("branch", "n/a")),
                "pr_url": str(task_status.get("pr_url") if task_status else assignment.get("pr_url", "n/a")),
            }
        )

    active_developers = [d for d in developers.values() if str(d.get("status", "")).lower() == "active"]
    started_tasks = [row for row in task_rows if row["contribution_status"] not in {"assigned", "not_started", "claimed"}]
    review_tasks = [row for row in task_rows if row["contribution_status"] == "review_requested"]
    integrated_tasks = [row for row in task_rows if row["integration_status"] == "integrated"]
    blocked_tasks = [row for row in task_rows if row["contribution_status"] == "blocked" or row["integration_status"] == "blocked"]

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "---",
        "kind: team-status",
        "version: 3",
        f"updated_at: {timestamp}",
        "updated_by: summarize-team-status",
        "status: derived",
        "---",
        "",
        "# 团队状态汇总",
        "",
        "`team-status.md` 是管理者视图，由 `scripts/summarize-team-status.py` 根据项目状态文件生成。它不是事实源。",
        "",
        "## 汇总规则",
        "",
        "事实源优先级：",
        "",
        "1. `.claw/developers/*.yaml`",
        "2. `.claw/assignments/*.yaml`",
        "3. `.claw/tasks/*.md`",
        "4. `.claw/task-board.md`",
        "5. `.claw/integration-queue.md`",
        "",
        "如果本文件与事实源冲突，修复事实源后重新生成本文件。",
        "",
        "## 团队概览",
        "",
        "| 指标 | 数量 |",
        "|------|------|",
        f"| 开发者 | {len(developers)} |",
        f"| 活跃开发者 | {len(active_developers)} |",
        f"| 授权任务 | {len(assignments)} |",
        f"| 已开始任务 | {len(started_tasks)} |",
        f"| 等待 review | {len(review_tasks)} |",
        f"| 已集成任务 | {len(integrated_tasks)} |",
        f"| 阻塞任务 | {len(blocked_tasks)} |",
        "",
        "## 成员状态",
        "",
    ]

    if not developers:
        lines.append("- 暂无开发者记录。")
        lines.append("")
    else:
        for developer_id in sorted(developers):
            developer = developers[developer_id]
            assigned = assignments_by_developer.get(developer_id, [])
            assigned_task_ids = [str(item.get("task_id", "unknown")) for item in assigned]
            active_task_ids = [
                row["task_id"]
                for row in task_rows
                if row["assignee"] == developer_id and row["contribution_status"] not in {"assigned", "not_started", "merged", "canceled"}
            ]
            latest_prs = [row["pr_url"] for row in task_rows if row["assignee"] == developer_id and not is_empty(row["pr_url"])]
            contribution_states = sorted({row["contribution_status"] for row in task_rows if row["assignee"] == developer_id})
            validation_states = sorted({row["validation_status"] for row in task_rows if row["assignee"] == developer_id})
            integration_states = sorted({row["integration_status"] for row in task_rows if row["assignee"] == developer_id})

            lines.extend(
                [
                    f"### {developer_id}",
                    "",
                    f"- display_name: `{developer.get('display_name', developer_id)}`",
                    f"- role: `{developer.get('role', 'unknown')}`",
                    f"- identity_status: `{developer.get('status', 'unknown')}`",
                    f"- assigned_tasks: `{csv_join(assigned_task_ids)}`",
                    f"- active_tasks: `{csv_join(active_task_ids)}`",
                    f"- latest_pr: `{latest_prs[-1] if latest_prs else 'none'}`",
                    f"- contribution_status: `{csv_join(contribution_states)}`",
                    f"- validation_status: `{csv_join(validation_states)}`",
                    f"- integration_status: `{csv_join(integration_states)}`",
                    "",
                ]
            )

    lines.extend(["## 任务状态", ""])

    if not task_rows:
        lines.append("- 暂无任务授权记录。")
        lines.append("")
    else:
        lines.extend(
            [
                "| Task | Title | Assignee | Board | Contribution | Validation | Integration | Branch | PR |",
                "|------|-------|----------|-------|--------------|------------|-------------|--------|----|",
            ]
        )
        for row in sorted(task_rows, key=lambda item: item["task_id"]):
            lines.append(
                f"| `{row['task_id']}` | {row['title']} | `{row['assignee']}` | `{row['board_status']}` | `{row['contribution_status']}` | `{row['validation_status']}` | `{row['integration_status']}` | `{row['branch']}` | `{row['pr_url']}` |"
            )

    lines.extend(["", "## 集成状态", ""])
    if not integration_statuses:
        lines.append("- 暂无集成队列记录。")
    else:
        for task_id in sorted(integration_statuses):
            lines.append(f"- `{task_id}`: `{integration_statuses[task_id]}`")

    lines.extend(
        [
            "",
            "## 维护规则",
            "",
            "- 不手工维护本文件的事实内容。",
            "- 管理者需要查看团队状态时，运行 `python3 scripts/summarize-team-status.py .claw --write`。",
            "- 远端 PR/CI 数据只有在写入任务状态或由后续平台脚本接入后，才会进入本汇总。",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the derived team-status manager view.")
    parser.add_argument("state_dir", nargs="?", default=".claw", help="Path to .claw or .ai-dev state directory")
    parser.add_argument("--write", action="store_true", help="Write the generated view to team-status.md")
    args = parser.parse_args()

    state_dir = Path(args.state_dir)
    if not state_dir.exists():
        parser.error(f"state directory does not exist: {state_dir}")

    rendered = render_team_status(state_dir)
    if args.write:
        destination = state_dir / "team-status.md"
        destination.write_text(rendered, encoding="utf-8")
        print(f"Updated: {destination}")
    else:
        print(rendered, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
