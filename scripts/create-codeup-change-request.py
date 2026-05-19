#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


DEFAULT_ENV_FILE = Path(".claw-local/codeup.env")
TOKEN_DOC_URL = "https://help.aliyun.com/zh/yunxiao/developer-reference/obtain-personal-access-token"
TASK_ID_RE = re.compile(r"\bTASK-\d+\b")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a Codeup change request with Yunxiao OpenAPI. Codeup is the default review platform."
    )
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), help="Local env file to read.")
    parser.add_argument("--domain", help="Yunxiao OpenAPI domain, for example https://openapi-rdc.aliyuncs.com.")
    parser.add_argument("--organization-id", help="Yunxiao organization id for center-version API endpoints.")
    parser.add_argument("--repository-id", help="Codeup repository id or URL-encoded full path.")
    parser.add_argument("--source-project-id", help="Source project id when Codeup requires it.")
    parser.add_argument("--target-project-id", help="Target project id when Codeup requires it.")
    parser.add_argument("--source-branch", help="Source branch. Defaults to the current Git branch.")
    parser.add_argument("--target-branch", help="Target branch. Defaults to CODEUP_TARGET_BRANCH or master.")
    parser.add_argument("--title", help="Change request title. Defaults to a title derived from TASK-xxx and branch.")
    parser.add_argument("--description", help="Change request description.")
    parser.add_argument("--description-file", help="Read the change request description from a file.")
    parser.add_argument("--reviewer-user-ids", help="Comma-separated Yunxiao reviewer user ids.")
    parser.add_argument("--work-item-ids", help="Comma-separated Yunxiao work item ids.")
    parser.add_argument("--task", help="Task id such as TASK-123. Defaults to extracting from branch/title/description.")
    parser.add_argument("--trigger-ai-review", action="store_true", help="Ask Codeup to trigger AI review if enabled.")
    parser.add_argument("--dry-run", action="store_true", help="Print the request without sending it.")
    return parser.parse_args()


def parse_env_file(path: Path) -> dict[str, str]:
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


def config_value(name: str, explicit: str | None, env_values: dict[str, str], default: str = "") -> str:
    if explicit:
        return explicit
    if os.environ.get(name):
        return os.environ[name]
    if env_values.get(name):
        return env_values[name]
    return default


def current_git_branch() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    branch = result.stdout.strip()
    if not branch or branch == "HEAD":
        raise SystemExit("Could not resolve the current Git branch; pass --source-branch explicitly.")
    return branch


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def extract_task_id(*values: str) -> str:
    for value in values:
        match = TASK_ID_RE.search(value or "")
        if match:
            return match.group(0)
    return ""


def read_description(args: argparse.Namespace, task_id: str, source_branch: str, target_branch: str) -> str:
    if args.description_file:
        return Path(args.description_file).read_text(encoding="utf-8")
    if args.description:
        return args.description

    lines = [
        f"Task: {task_id or 'n/a'}",
        f"Source branch: {source_branch}",
        f"Target branch: {target_branch}",
        "",
        "Verification:",
        "- not_run",
    ]
    return "\n".join(lines)


def normalize_domain(domain: str) -> str:
    if not domain:
        return ""
    cleaned = domain.strip().rstrip("/")
    if not cleaned.startswith(("http://", "https://")):
        cleaned = f"https://{cleaned}"
    return cleaned


def build_endpoint(domain: str, organization_id: str, repository_id: str) -> str:
    encoded_repo = quote(repository_id, safe="") if "/" in repository_id else repository_id
    if organization_id:
        return f"{domain}/oapi/v1/codeup/organizations/{organization_id}/repositories/{encoded_repo}/changeRequests"
    return f"{domain}/oapi/v1/codeup/repositories/{encoded_repo}/changeRequests"


def require_config(args: argparse.Namespace, env_values: dict[str, str]) -> dict[str, str]:
    token = config_value("YUNXIAO_TOKEN", None, env_values)
    if not token:
        print("YUNXIAO_TOKEN is not set, so the Codeup change request was not created.", file=sys.stderr)
        print(f"Create a Yunxiao personal access token: {TOKEN_DOC_URL}", file=sys.stderr)
        print("Then store it locally with:", file=sys.stderr)
        print("  python3 scripts/store-yunxiao-token.py", file=sys.stderr)
        print("or export it for the current shell:", file=sys.stderr)
        print("  export YUNXIAO_TOKEN='<your-token>'", file=sys.stderr)
        raise SystemExit(2)

    config = {
        "token": token,
        "domain": normalize_domain(config_value("YUNXIAO_DOMAIN", args.domain, env_values)),
        "organization_id": config_value("YUNXIAO_ORGANIZATION_ID", args.organization_id, env_values),
        "repository_id": config_value("CODEUP_REPOSITORY_ID", args.repository_id, env_values),
        "source_project_id": config_value("CODEUP_SOURCE_PROJECT_ID", args.source_project_id, env_values),
        "target_project_id": config_value("CODEUP_TARGET_PROJECT_ID", args.target_project_id, env_values),
        "target_branch": config_value("CODEUP_TARGET_BRANCH", args.target_branch, env_values, "master"),
    }

    missing = [key for key in ("domain", "repository_id") if not config[key]]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"Missing required Codeup config: {joined}. Pass CLI args or set local env values.")
    return config


def build_payload(args: argparse.Namespace, config: dict[str, str]) -> dict[str, Any]:
    source_branch = args.source_branch or current_git_branch()
    target_branch = config["target_branch"]
    task_id = args.task or extract_task_id(source_branch, args.title or "", args.description or "")
    if args.title:
        title = args.title
    elif task_id:
        title = f"[{task_id}] {source_branch}"
    else:
        title = f"Change request from {source_branch}"
    description = read_description(args, task_id, source_branch, target_branch)

    payload: dict[str, Any] = {
        "createFrom": "COMMAND_LINE",
        "sourceBranch": source_branch,
        "targetBranch": target_branch,
        "title": title,
        "description": description,
        "triggerAIReviewRun": bool(args.trigger_ai_review),
    }

    if config["source_project_id"]:
        payload["sourceProjectId"] = int(config["source_project_id"])
    if config["target_project_id"]:
        payload["targetProjectId"] = int(config["target_project_id"])
    if args.reviewer_user_ids:
        payload["reviewerUserIds"] = parse_csv(args.reviewer_user_ids)
    if args.work_item_ids:
        payload["workItemIds"] = args.work_item_ids

    return payload


def post_change_request(endpoint: str, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-yunxiao-token": token,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            raw_body = response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Codeup API returned HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise SystemExit(f"Could not reach Codeup API: {exc}") from exc

    try:
        return json.loads(raw_body)
    except json.JSONDecodeError:
        return {"raw": raw_body}


def main() -> int:
    args = parse_args()
    env_values = parse_env_file(Path(args.env_file))
    config = require_config(args, env_values)
    endpoint = build_endpoint(config["domain"], config["organization_id"], config["repository_id"])
    payload = build_payload(args, config)

    if args.dry_run:
        print(json.dumps({"endpoint": endpoint, "payload": payload}, ensure_ascii=False, indent=2))
        return 0

    result = post_change_request(endpoint, config["token"], payload)
    detail_url = result.get("detailUrl") or result.get("url") or result.get("webUrl") or ""
    local_id = result.get("localId") or result.get("local_id") or ""
    if detail_url:
        print(f"Created Codeup change request: {detail_url}")
    elif local_id:
        print(f"Created Codeup change request localId={local_id}")
    else:
        print("Created Codeup change request.")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
