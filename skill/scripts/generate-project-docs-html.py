#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from lib.project_docs_html import (
    discover_documents,
    inspect_pair,
    is_project_document,
    project_root_for_document,
    sync_project_documents,
    write_companion,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate or check one paired human-readable HTML file for each Markdown file "
            "under docs/design and docs/specs."
        )
    )
    parser.add_argument("target", help="Project root or one Markdown file under docs/design or docs/specs")
    parser.add_argument("--write", action="store_true", help="Atomically create or refresh paired HTML files")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    parser.add_argument("--now", default="", help="Override generated time using YYYY-MM-DDTHH:MM:SSZ")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target = Path(args.target).expanduser().resolve()
    generated_at = args.now or None

    if target.is_file():
        project_root = project_root_for_document(target)
        if target.suffix.lower() != ".md" or project_root is None or not is_project_document(target, project_root):
            raise SystemExit("target Markdown must be under docs/design or docs/specs")
        sources = [target]
    elif target.is_dir():
        project_root = target
        sources = discover_documents(project_root)
    else:
        raise SystemExit(f"target does not exist: {target}")

    if args.write:
        outputs = (
            sync_project_documents(project_root, generated_at=generated_at)
            if target.is_dir()
            else (
                []
                if inspect_pair(target).current
                else [write_companion(target, project_root=project_root, generated_at=generated_at)]
            )
        )
        statuses = [inspect_pair(source) for source in sources]
    else:
        outputs = []
        statuses = [inspect_pair(source) for source in sources]

    stale = [status for status in statuses if not status.current]
    payload = {
        "mode": "write" if args.write else "check",
        "project_root": str(project_root),
        "source_count": len(sources),
        "written": [str(path.relative_to(project_root)) for path in outputs],
        "stale": [
            {
                "source": str(status.source.relative_to(project_root)),
                "output": str(status.output.relative_to(project_root)),
                "reason": status.reason,
            }
            for status in stale
        ],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    elif stale:
        for status in stale:
            print(f"stale: {status.source} -> {status.output} ({status.reason})")
    elif args.write:
        print(f"Updated {len(outputs)} paired HTML file(s).")
    else:
        print(f"All {len(sources)} paired HTML file(s) are current.")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
