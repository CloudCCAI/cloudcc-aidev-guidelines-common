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
    "test-report.md": "test-report",
    "devops.md": "devops",
}

REQUIRED_FRONTMATTER_FIELDS = {"kind", "version", "updated_at", "updated_by"}


def read_front_matter(path: Path) -> tuple[dict[str, str], list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if len(lines) < 3 or lines[0].strip() != "---":
        return {}, [f"{path.name}: missing YAML front matter"]

    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, [f"{path.name}: unclosed YAML front matter"]

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
        parsed[key.strip()] = value.strip().strip('"').strip("'")

    return parsed, errors


def validate_timestamp(path: Path, front_matter: dict[str, str], errors: list[str]) -> None:
    timestamp = front_matter.get("updated_at", "")
    pattern = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$|^YYYY-MM-DDTHH:MM:SSZ$"
    if not re.match(pattern, timestamp):
        errors.append(f"{path.name}: invalid `updated_at` format `{timestamp}`")


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    front_matter, fm_errors = read_front_matter(path)
    errors.extend(fm_errors)

    if not front_matter:
        return errors

    missing = REQUIRED_FRONTMATTER_FIELDS - front_matter.keys()
    for field in sorted(missing):
        errors.append(f"{path.name}: missing front matter field `{field}`")

    expected_kind = EXPECTED_KINDS[path.name]
    actual_kind = front_matter.get("kind")
    if actual_kind and actual_kind != expected_kind:
        errors.append(
            f"{path.name}: expected kind `{expected_kind}`, got `{actual_kind}`"
        )

    validate_timestamp(path, front_matter, errors)
    return errors


def main() -> int:
    state_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".claw")

    if not state_dir.exists():
        print(f"State directory does not exist: {state_dir}", file=sys.stderr)
        return 1

    errors: list[str] = []

    for filename in EXPECTED_KINDS:
        path = state_dir / filename
        if not path.exists():
            errors.append(f"missing required file: {path}")
            continue
        errors.extend(validate_file(path))

    if errors:
        print("State validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"State validation passed for: {state_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
