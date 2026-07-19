#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from lib.codeup_config import (
    DEFAULT_DOMAIN,
    DEFAULT_ENV_FILE,
    TOKEN_DOC_URL,
    config_value,
    normalize_domain,
    parse_env_file,
    write_env_file,
)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Configure local Codeup change request defaults in .claw-local/codeup.env."
    )
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), help="Local env file to read and write.")
    parser.add_argument("--remote", default="origin", help="Git remote to inspect. Defaults to origin.")
    parser.add_argument("--domain", help=f"Yunxiao OpenAPI domain. Defaults to {DEFAULT_DOMAIN}.")
    parser.add_argument("--organization-id", help="Yunxiao organization id. Defaults to the Codeup remote namespace.")
    parser.add_argument("--repository-id", help="Numeric Codeup repository id. If omitted, resolve it from Codeup.")
    parser.add_argument("--source-project-id", help="Numeric source project id. Defaults to repository id.")
    parser.add_argument("--target-project-id", help="Numeric target project id. Defaults to repository id.")
    parser.add_argument("--target-branch", help="Target branch for change requests. Defaults to remote HEAD or main.")
    parser.add_argument(
        "--create-from",
        choices=("WEB", "COMMAND_LINE"),
        default="COMMAND_LINE",
        help="Create source sent to Codeup. Defaults to COMMAND_LINE.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print resolved config without writing the env file.")
    return parser.parse_args()


def run_git(args: list[str], *, required: bool = True) -> str:
    result = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        if required:
            raise SystemExit(result.stderr.strip() or f"git {' '.join(args)} failed")
        return ""
    return result.stdout.strip()


def parse_codeup_remote(remote_url: str) -> tuple[str, str, str]:
    cleaned = remote_url.strip()
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]

    match = re.match(r"git@codeup\.aliyun\.com:(?P<path>.+)$", cleaned)
    if not match:
        match = re.match(r"https://codeup\.aliyun\.com/(?P<path>.+)$", cleaned)
    if not match:
        raise SystemExit(f"Remote URL is not a Codeup URL: {remote_url}")

    path = match.group("path").strip("/")
    parts = path.split("/")
    if len(parts) < 2:
        raise SystemExit(f"Could not infer organization and repository from remote URL: {remote_url}")

    organization_id = parts[0]
    repository_name = parts[-1]
    return organization_id, path, repository_name


def remote_head_branch(remote: str) -> str:
    symbolic = run_git(["symbolic-ref", "-q", "--short", f"refs/remotes/{remote}/HEAD"], required=False)
    if symbolic.startswith(f"{remote}/"):
        return symbolic.split("/", 1)[1]

    current = run_git(["rev-parse", "--abbrev-ref", "HEAD"], required=False)
    if current in {"main", "master"}:
        return current
    return "main"


def repository_matches(item: dict[str, object], remote_url: str, namespace_path: str, repository_name: str) -> bool:
    remote_clean = remote_url.removesuffix(".git")
    candidates = [
        str(item.get("sshUrlToRepo") or "").removesuffix(".git"),
        str(item.get("httpUrlToRepo") or "").removesuffix(".git"),
        str(item.get("webUrl") or "").removesuffix(".git"),
    ]
    if remote_clean in candidates:
        return True

    path_with_namespace = str(item.get("pathWithNamespace") or "").strip("/")
    if path_with_namespace == namespace_path:
        return True

    return str(item.get("name") or "") == repository_name


def resolve_repository_id(
    *,
    domain: str,
    token: str,
    organization_id: str,
    remote_url: str,
    namespace_path: str,
    repository_name: str,
) -> str:
    params = urlencode({"page": 1, "perPage": 100, "search": repository_name, "archived": "false"})
    endpoint = f"{domain}/oapi/v1/codeup/organizations/{organization_id}/repositories?{params}"
    request = Request(
        endpoint,
        headers={"Content-Type": "application/json", "x-yunxiao-token": token},
    )
    try:
        with urlopen(request, timeout=30) as response:
            repositories = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Codeup repository lookup failed with HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise SystemExit(f"Could not reach Codeup API: {exc}") from exc

    matches = [
        item
        for item in repositories
        if isinstance(item, dict) and repository_matches(item, remote_url, namespace_path, repository_name)
    ]
    if not matches:
        raise SystemExit(f"Could not resolve Codeup repository id for {namespace_path}.")
    if len(matches) > 1:
        ids = ", ".join(str(item.get("id")) for item in matches)
        raise SystemExit(f"Repository lookup was ambiguous for {repository_name}: {ids}")

    repository_id = str(matches[0].get("id") or "")
    if not re.fullmatch(r"\d+", repository_id):
        raise SystemExit(f"Resolved repository id is not numeric: {repository_id}")
    return repository_id


def main() -> int:
    args = parse_args()
    env_file = Path(args.env_file)
    env_values = parse_env_file(env_file)

    remote_url = run_git(["remote", "get-url", args.remote])
    remote_org, namespace_path, repository_name = parse_codeup_remote(remote_url)
    domain = normalize_domain(config_value("YUNXIAO_DOMAIN", args.domain, env_values, DEFAULT_DOMAIN))
    organization_id = config_value("YUNXIAO_ORGANIZATION_ID", args.organization_id, env_values, remote_org)
    token = config_value("YUNXIAO_TOKEN", None, env_values)
    repository_id = config_value("CODEUP_REPOSITORY_ID", args.repository_id, env_values)

    if repository_id and not re.fullmatch(r"\d+", repository_id):
        raise SystemExit(f"CODEUP_REPOSITORY_ID must be numeric for generated defaults, got: {repository_id}")
    if not repository_id:
        if not token:
            print("YUNXIAO_TOKEN is required to resolve the Codeup repository id.", file=sys.stderr)
            print(f"Create a Yunxiao personal access token: {TOKEN_DOC_URL}", file=sys.stderr)
            print("Then run scripts/store-yunxiao-token.py before configuring Codeup defaults.", file=sys.stderr)
            raise SystemExit(2)
        repository_id = resolve_repository_id(
            domain=domain,
            token=token,
            organization_id=organization_id,
            remote_url=remote_url,
            namespace_path=namespace_path,
            repository_name=repository_name,
        )

    values = {
        **env_values,
        "YUNXIAO_DOMAIN": domain,
        "YUNXIAO_ORGANIZATION_ID": organization_id,
        "CODEUP_REPOSITORY_ID": repository_id,
        "CODEUP_SOURCE_PROJECT_ID": config_value("CODEUP_SOURCE_PROJECT_ID", args.source_project_id, env_values, repository_id),
        "CODEUP_TARGET_PROJECT_ID": config_value("CODEUP_TARGET_PROJECT_ID", args.target_project_id, env_values, repository_id),
        "CODEUP_TARGET_BRANCH": config_value(
            "CODEUP_TARGET_BRANCH",
            args.target_branch,
            env_values,
            remote_head_branch(args.remote),
        ),
        "CODEUP_CREATE_FROM": config_value("CODEUP_CREATE_FROM", args.create_from, env_values, "COMMAND_LINE"),
    }
    if token:
        values["YUNXIAO_TOKEN"] = token

    if args.dry_run:
        preview = {key: ("<set>" if key == "YUNXIAO_TOKEN" else value) for key, value in values.items()}
        print(json.dumps(preview, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    write_env_file(env_file, values)
    print(f"Stored Codeup change request defaults in {env_file}")
    print(f"CODEUP_REPOSITORY_ID={repository_id}")
    print(f"CODEUP_TARGET_BRANCH={values['CODEUP_TARGET_BRANCH']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
