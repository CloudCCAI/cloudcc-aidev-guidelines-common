#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import secrets
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


DEFAULT_REPOSITORY = "CloudCCAI/cloudcc-aidev-guidelines-common"
DEFAULT_BRANCH = "main"
DEFAULT_SKILL_PATH = "skill/SKILL.md"
API_BASE = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"
VERSION_RE = re.compile(r'^\s*skill_version:\s*["\']?([0-9]\.[0-9]\.[0-9])["\']?\s*$', re.MULTILINE)
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
NO_CACHE_HEADERS = {
    "Accept": "application/vnd.github+json",
    "Cache-Control": "no-cache, no-store, max-age=0",
    "Pragma": "no-cache",
    "User-Agent": "cc-aidev-guidelines-common-version-check",
}


def cache_busted_url(url: str, nonce: str) -> str:
    parsed = urlsplit(url)
    query = parsed.query
    cache_query = urlencode({"cache_bust": nonce})
    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            f"{query}&{cache_query}" if query else cache_query,
            parsed.fragment,
        )
    )


def parse_skill_version(text: str) -> str:
    match = VERSION_RE.search(text)
    if not match:
        raise ValueError("SKILL.md is missing a valid single-digit metadata.skill_version")
    return match.group(1)


def version_tuple(version: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"[0-9]\.[0-9]\.[0-9]", version):
        raise ValueError(f"invalid skill version: {version}")
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


def request_bytes(
    url: str,
    *,
    timeout: float,
    nonce: str,
    opener: Callable[..., Any] = urlopen,
) -> bytes:
    request = Request(cache_busted_url(url, nonce), headers=NO_CACHE_HEADERS)
    with opener(request, timeout=timeout) as response:
        return response.read()


def resolve_commit_via_git(
    *,
    repository: str,
    branch: str,
    timeout: float,
    runner: Callable[..., Any] = subprocess.run,
) -> str:
    remote_url = f"https://github.com/{repository}.git"
    completed = runner(
        ["git", "ls-remote", "--exit-code", remote_url, f"refs/heads/{branch}"],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"exit {completed.returncode}"
        raise ValueError(f"git ls-remote failed: {detail}")
    first_line = completed.stdout.splitlines()[0] if completed.stdout.splitlines() else ""
    commit = first_line.split(maxsplit=1)[0].lower() if first_line else ""
    if not COMMIT_RE.fullmatch(commit):
        raise ValueError("git ls-remote did not return a valid 40-character commit SHA")
    return commit


def resolve_commit_via_api(
    *,
    repository: str,
    branch: str,
    timeout: float,
    nonce: str,
    opener: Callable[..., Any] = urlopen,
) -> str:
    encoded_repository = quote(repository, safe="/")
    encoded_branch = quote(branch, safe="")
    ref_url = f"{API_BASE}/repos/{encoded_repository}/git/ref/heads/{encoded_branch}"
    ref_payload = json.loads(
        request_bytes(
            ref_url,
            timeout=timeout,
            nonce=nonce,
            opener=opener,
        ).decode("utf-8")
    )
    commit = str(ref_payload.get("object", {}).get("sha", "")).lower()
    if not COMMIT_RE.fullmatch(commit):
        raise ValueError("GitHub ref response is missing a valid 40-character commit SHA")
    return commit


def fetch_upstream(
    *,
    repository: str,
    branch: str,
    skill_path: str,
    timeout: float,
    opener: Callable[..., Any] = urlopen,
    git_runner: Callable[..., Any] = subprocess.run,
    nonce_factory: Callable[[], str] | None = None,
) -> dict[str, str]:
    if not REPOSITORY_RE.fullmatch(repository):
        raise ValueError("repository must use owner/name")
    make_nonce = nonce_factory or (lambda: secrets.token_hex(12))
    try:
        commit = resolve_commit_via_git(
            repository=repository,
            branch=branch,
            timeout=timeout,
            runner=git_runner,
        )
        commit_source = "git_ls_remote"
    except (OSError, subprocess.TimeoutExpired, ValueError):
        commit = resolve_commit_via_api(
            repository=repository,
            branch=branch,
            timeout=timeout,
            nonce=make_nonce(),
            opener=opener,
        )
        commit_source = "github_api_no_cache"

    encoded_repository = quote(repository, safe="/")
    encoded_path = quote(skill_path.strip("/"), safe="/")
    pinned_url = f"{RAW_BASE}/{encoded_repository}/{commit}/{encoded_path}"
    skill_text = request_bytes(
        pinned_url,
        timeout=timeout,
        nonce=make_nonce(),
        opener=opener,
    ).decode("utf-8")
    return {
        "commit_source": commit_source,
        "upstream_commit": commit,
        "upstream_install_url": f"https://github.com/{repository}/tree/{commit}/skill",
        "upstream_version": parse_skill_version(skill_text),
        "upstream_skill_url": pinned_url,
    }


def check_version(
    local_skill: Path,
    *,
    repository: str,
    branch: str,
    skill_path: str,
    timeout: float,
    opener: Callable[..., Any] = urlopen,
    git_runner: Callable[..., Any] = subprocess.run,
    nonce_factory: Callable[[], str] | None = None,
) -> dict[str, object]:
    local_version = parse_skill_version(local_skill.read_text(encoding="utf-8"))
    upstream = fetch_upstream(
        repository=repository,
        branch=branch,
        skill_path=skill_path,
        timeout=timeout,
        opener=opener,
        git_runner=git_runner,
        nonce_factory=nonce_factory,
    )
    local_parts = version_tuple(local_version)
    upstream_parts = version_tuple(upstream["upstream_version"])
    relation = "update_available" if upstream_parts > local_parts else "current"
    if upstream_parts < local_parts:
        relation = "local_ahead"
    return {
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "strategy": "git_ls_remote_or_no_cache_api_then_commit_pinned_raw",
        "local_version": local_version,
        **upstream,
        "relation": relation,
        "update_available": upstream_parts > local_parts,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check the latest skill version without trusting a cached branch-level raw URL."
    )
    parser.add_argument(
        "--local-skill",
        default=str(Path(__file__).resolve().parents[1] / "SKILL.md"),
        help="Local SKILL.md path. Defaults to the SKILL.md beside this script package.",
    )
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--skill-path", default=DEFAULT_SKILL_PATH)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    try:
        result = check_version(
            Path(args.local_skill),
            repository=args.repository,
            branch=args.branch,
            skill_path=args.skill_path,
            timeout=args.timeout,
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, HTTPError, URLError) as exc:
        print(f"Could not verify the upstream skill version: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            f"local={result['local_version']} upstream={result['upstream_version']} "
            f"commit={result['upstream_commit']} relation={result['relation']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
