from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class SimpleYamlError(ValueError):
    """Raised when input exceeds the deliberately small YAML subset."""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def clean_value(value: object) -> str:
    if value is None:
        return ""
    cleaned = str(value).strip().strip('"').strip("'")
    if cleaned.startswith("`") and cleaned.endswith("`") and len(cleaned) >= 2:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def _strip_inline_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if char == "\\" and quote == '"':
            escaped = True
            continue
        if char in {'"', "'"}:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
            continue
        if char == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.rstrip()


def parse_scalar(raw_value: str) -> object:
    value = _strip_inline_comment(raw_value.strip())
    if not value:
        return ""
    if value.startswith(("[", "{")) and value.endswith(("]", "}")):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise SimpleYamlError(f"invalid JSON-compatible flow value: {value}") from exc
        if not isinstance(parsed, (list, dict)):
            raise SimpleYamlError(f"flow value must be a list or mapping: {value}")
        return parsed
    if value[0:1] == value[-1:] and value.startswith(('"', "'")):
        if value.startswith('"'):
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise SimpleYamlError(f"invalid quoted scalar: {value}") from exc
        return value[1:-1].replace("''", "'")
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    return value


def parse_simple_yaml(text: str) -> dict[str, object]:
    """Parse top-level scalars and scalar lists only.

    The project-state format intentionally avoids anchors, tags, block mappings,
    and multiline scalars. JSON-compatible flow lists/mappings are supported so
    machine-written indexes can remain ordinary YAML without third-party code.
    """

    parsed: dict[str, object] = {}
    current_list: str | None = None
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        stripped = raw_line.strip()
        if stripped.startswith("- "):
            if current_list is None:
                raise SimpleYamlError(f"line {line_number}: list item has no top-level key")
            value = parse_scalar(stripped[2:])
            current_value = parsed[current_list]
            if not isinstance(current_value, list):
                raise SimpleYamlError(f"line {line_number}: `{current_list}` is not a list")
            current_value.append(value)
            continue

        if raw_line[:1].isspace():
            raise SimpleYamlError(f"line {line_number}: nested mappings are not supported")
        if ":" not in stripped:
            raise SimpleYamlError(f"line {line_number}: expected `key: value`")

        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        if not key or any(char.isspace() for char in key):
            raise SimpleYamlError(f"line {line_number}: invalid key `{key}`")
        if key in parsed:
            raise SimpleYamlError(f"line {line_number}: duplicate key `{key}`")

        if raw_value.strip() == "":
            parsed[key] = []
            current_list = key
        else:
            parsed[key] = parse_scalar(raw_value)
            current_list = None
    return parsed


def parse_mapping_list_yaml(text: str, *, list_key: str) -> dict[str, object]:
    """Parse top-level fields plus one list of flat mappings.

    Machine-generated flow mappings and conventional YAML block mappings are
    both accepted. Nested scalar lists inside each mapping are also supported.
    """

    try:
        return parse_simple_yaml(text)
    except SimpleYamlError:
        pass

    fields: dict[str, object] = {}
    items: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    current_list_key: str | None = None
    in_items = False
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0:
            if ":" not in stripped:
                raise SimpleYamlError(f"line {line_number}: expected top-level key")
            key, raw_value = stripped.split(":", 1)
            key = key.strip()
            in_items = key == list_key
            current = None
            current_list_key = None
            if in_items:
                if raw_value.strip() not in {"", "[]"}:
                    raise SimpleYamlError(f"line {line_number}: `{list_key}` must be a list")
                fields[list_key] = items
            else:
                fields[key] = parse_scalar(raw_value)
            continue
        if not in_items:
            raise SimpleYamlError(f"line {line_number}: unexpected nested value")
        if indent == 2 and stripped.startswith("- "):
            item_text = stripped[2:].strip()
            current_list_key = None
            if item_text.startswith("{"):
                parsed = parse_scalar(item_text)
                if not isinstance(parsed, dict):
                    raise SimpleYamlError(f"line {line_number}: list entry must be a mapping")
                current = parsed
            else:
                if ":" not in item_text:
                    raise SimpleYamlError(f"line {line_number}: list entry must start with key: value")
                key, raw_value = item_text.split(":", 1)
                current = {key.strip(): parse_scalar(raw_value)}
            items.append(current)
            continue
        if current is None:
            raise SimpleYamlError(f"line {line_number}: mapping field has no list item")
        if indent == 4 and ":" in stripped:
            key, raw_value = stripped.split(":", 1)
            key = key.strip()
            if raw_value.strip():
                current[key] = parse_scalar(raw_value)
                current_list_key = None
            else:
                current[key] = []
                current_list_key = key
            continue
        if indent == 6 and stripped.startswith("- ") and current_list_key:
            raw_list = current[current_list_key]
            assert isinstance(raw_list, list)
            raw_list.append(parse_scalar(stripped[2:]))
            continue
        raise SimpleYamlError(f"line {line_number}: unsupported mapping-list structure")
    fields.setdefault(list_key, items)
    return fields


def read_mapping_list_yaml(path: Path, *, list_key: str) -> dict[str, object]:
    return parse_mapping_list_yaml(Path(path).read_text(encoding="utf-8"), list_key=list_key)


def split_front_matter(text: str) -> tuple[dict[str, object], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise SimpleYamlError("unclosed YAML front matter") from exc
    fields = parse_simple_yaml("\n".join(lines[1:end]))
    body = "\n".join(lines[end + 1 :])
    if text.endswith("\n"):
        body += "\n"
    return fields, body


def read_front_matter(path: Path) -> tuple[dict[str, object], str]:
    return split_front_matter(Path(path).read_text(encoding="utf-8"))
