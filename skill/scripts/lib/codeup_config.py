from __future__ import annotations

import os
import shlex
import stat
from pathlib import Path

from .atomic_io import atomic_write_text


DEFAULT_DOMAIN = "https://openapi-rdc.aliyuncs.com"
DEFAULT_ENV_FILE = Path(".claw-local/codeup.env")
TOKEN_DOC_URL = "https://help.aliyun.com/zh/yunxiao/developer-reference/obtain-personal-access-token"
ORDERED_KEYS = (
    "YUNXIAO_DOMAIN",
    "YUNXIAO_ORGANIZATION_ID",
    "CODEUP_REPOSITORY_ID",
    "CODEUP_SOURCE_PROJECT_ID",
    "CODEUP_TARGET_PROJECT_ID",
    "CODEUP_TARGET_BRANCH",
    "CODEUP_CREATE_FROM",
    "CODEUP_REVIEWER_USER_IDS",
    "CODEUP_WORK_ITEM_IDS",
    "CODEUP_TRIGGER_AI_REVIEW",
    "YUNXIAO_TOKEN",
)


def parse_env_file(path: Path) -> dict[str, str]:
    path = Path(path)
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        try:
            parts = shlex.split(raw_value, posix=True)
        except ValueError:
            parts = [raw_value.strip().strip('"').strip("'")]
        if key:
            values[key] = parts[0] if parts else ""
    return values


def config_value(
    name: str,
    explicit: str | None,
    env_values: dict[str, str],
    default: str = "",
) -> str:
    if explicit:
        return explicit
    if os.environ.get(name):
        return os.environ[name]
    if env_values.get(name):
        return env_values[name]
    return default


def normalize_domain(domain: str) -> str:
    if not domain:
        return ""
    cleaned = domain.strip().rstrip("/")
    if not cleaned.startswith(("http://", "https://")):
        cleaned = f"https://{cleaned}"
    return cleaned


def write_env_file(path: Path, values: dict[str, str]) -> None:
    path = Path(path)
    parent_existed = path.parent.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not parent_existed:
        os.chmod(path.parent, stat.S_IRWXU)

    lines = ["# 本地 Codeup OpenAPI 配置，请勿提交此文件。"]
    for key in ORDERED_KEYS:
        if values.get(key):
            lines.append(f"export {key}={shlex.quote(values[key])}")
    lines.append("")
    atomic_write_text(path, "\n".join(lines), mode=0o600)


def merge_env_file(path: Path, updates: dict[str, str]) -> dict[str, str]:
    values = parse_env_file(path)
    values.update({key: value for key, value in updates.items() if value})
    write_env_file(path, values)
    return values
