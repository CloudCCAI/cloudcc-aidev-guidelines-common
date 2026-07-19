from __future__ import annotations

from typing import Mapping

from .state_io import clean_value


PRIMARY_LANGUAGE = "zh-CN"
PENDING_LANGUAGE = "pending"
LEGACY_DEFAULT_LANGUAGE = "en"
READABLE_LANGUAGES = (PENDING_LANGUAGE, LEGACY_DEFAULT_LANGUAGE, PRIMARY_LANGUAGE)
LANGUAGE_ALIASES = {
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "zh": "zh-CN",
    "zh-cn": "zh-CN",
    "zh-hans": "zh-CN",
    "pending": PENDING_LANGUAGE,
}


def normalize_language(value: object, *, allow_pending: bool = True) -> str:
    cleaned = clean_value(value)
    if not cleaned:
        return LEGACY_DEFAULT_LANGUAGE
    normalized = LANGUAGE_ALIASES.get(cleaned.lower())
    if normalized is None or (normalized == PENDING_LANGUAGE and not allow_pending):
        choices = ", ".join(READABLE_LANGUAGES)
        raise ValueError(f"unsupported legacy language marker `{cleaned}`; expected one of: {choices}")
    return normalized


def manifest_language(manifest: Mapping[str, object], *, allow_pending: bool = True) -> str:
    return normalize_language(manifest.get("language"), allow_pending=allow_pending)
