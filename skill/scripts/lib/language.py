from __future__ import annotations

import re
from pathlib import Path
from typing import Mapping

from .state_io import clean_value


SUPPORTED_LANGUAGES = ("en", "zh-CN")
PENDING_LANGUAGE = "pending"
LEGACY_DEFAULT_LANGUAGE = "en"
LANGUAGE_ALIASES = {
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "zh": "zh-CN",
    "zh-cn": "zh-CN",
    "zh-hans": "zh-CN",
    "pending": PENDING_LANGUAGE,
}
LANGUAGE_FIELD_RE = re.compile(r"^language:\s*(.*?)\s*$", re.MULTILINE)


def normalize_language(value: object, *, allow_pending: bool = True) -> str:
    cleaned = clean_value(value)
    if not cleaned:
        return LEGACY_DEFAULT_LANGUAGE
    normalized = LANGUAGE_ALIASES.get(cleaned.lower())
    if normalized is None or (normalized == PENDING_LANGUAGE and not allow_pending):
        choices = ", ".join(SUPPORTED_LANGUAGES)
        raise ValueError(f"unsupported language `{cleaned}`; expected one of: {choices}")
    return normalized


def manifest_language(manifest: Mapping[str, object], *, allow_pending: bool = True) -> str:
    return normalize_language(manifest.get("language"), allow_pending=allow_pending)


def state_dir_language(state_dir: Path, *, allow_pending: bool = False) -> str:
    manifest_path = Path(state_dir) / "manifest.yaml"
    if not manifest_path.is_file():
        return LEGACY_DEFAULT_LANGUAGE
    match = LANGUAGE_FIELD_RE.search(manifest_path.read_text(encoding="utf-8"))
    value = match.group(1) if match else ""
    return normalize_language(value, allow_pending=allow_pending)


def project_language(project_root: Path, *, allow_pending: bool = False) -> str:
    return state_dir_language(Path(project_root) / ".claw", allow_pending=allow_pending)


def localized_template_path(skill_root: Path, template_path: Path, language: str) -> Path:
    normalized = normalize_language(language, allow_pending=False)
    template_path = Path(template_path)
    if normalized == "en":
        return template_path
    templates_root = Path(skill_root) / "templates"
    relative = template_path.relative_to(templates_root)
    localized = templates_root / "locales" / normalized / relative
    if not localized.is_file():
        raise FileNotFoundError(f"missing {normalized} template for {relative.as_posix()}")
    return localized


def choose(language: str, *, en: str, zh_cn: str) -> str:
    return zh_cn if normalize_language(language, allow_pending=False) == "zh-CN" else en
