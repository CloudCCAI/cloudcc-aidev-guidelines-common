#!/usr/bin/env python3

from __future__ import annotations

import argparse
import getpass
import os
import shlex
import stat
import sys
from pathlib import Path


DEFAULT_ENV_FILE = Path(".claw-local/codeup.env")
TOKEN_DOC_URL = "https://help.aliyun.com/zh/yunxiao/developer-reference/obtain-personal-access-token"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Store a local Yunxiao Codeup OpenAPI token outside Git-tracked project files."
    )
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Local env file to write. Defaults to .claw-local/codeup.env.",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read the token from stdin instead of prompting. Avoids putting tokens in shell history.",
    )
    return parser.parse_args()


def read_token(use_stdin: bool) -> str:
    if use_stdin:
        token = sys.stdin.read().strip()
    else:
        print(f"Create a Yunxiao personal access token first: {TOKEN_DOC_URL}")
        token = getpass.getpass("YUNXIAO_TOKEN: ").strip()

    if not token:
        raise SystemExit("YUNXIAO_TOKEN is empty; nothing was stored.")
    return token


def write_env_file(path: Path, token: str) -> None:
    parent_existed = path.parent.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not parent_existed:
        os.chmod(path.parent, stat.S_IRWXU)

    content = "\n".join(
        [
            "# Local Codeup OpenAPI token. Do not commit this file.",
            f"export YUNXIAO_TOKEN={shlex.quote(token)}",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def main() -> int:
    args = parse_args()
    token = read_token(args.stdin)
    env_file = Path(args.env_file)
    write_env_file(env_file, token)
    print(f"Stored YUNXIAO_TOKEN in {env_file}")
    print("Future scripts can load it automatically from this local env file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
