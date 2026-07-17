#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge a development branch into dev and push dev for test-environment deployment."
    )
    parser.add_argument("--source-branch", help="Development branch to merge. Defaults to the current branch.")
    parser.add_argument("--target-branch", default="dev", help="Test-environment branch. Defaults to dev.")
    parser.add_argument("--remote", default="origin", help="Git remote to fetch from and push to. Defaults to origin.")
    parser.add_argument("--no-fetch", action="store_true", help="Skip git fetch before merging.")
    parser.add_argument(
        "--no-restore",
        action="store_true",
        help="Stay on the target branch after pushing instead of returning to the original branch.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned commands without changing the repo.")
    return parser.parse_args()


def run(args: list[str], *, check: bool = True, capture: bool = False, dry_run: bool = False) -> subprocess.CompletedProcess[str]:
    if dry_run:
        print("+ " + " ".join(args))
        return subprocess.CompletedProcess(args, 0, "", "")

    return subprocess.run(
        args,
        check=check,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True,
    )


def git_output(*args: str) -> str:
    result = run(["git", *args], capture=True)
    return result.stdout.strip()


def current_branch() -> str:
    branch = git_output("rev-parse", "--abbrev-ref", "HEAD")
    if not branch or branch == "HEAD":
        raise SystemExit("Could not resolve the current Git branch; pass --source-branch explicitly.")
    return branch


def require_clean_worktree() -> None:
    status = git_output("status", "--porcelain")
    if status:
        raise SystemExit("Working tree is not clean. Commit, stash, or discard local changes before pushing to test.")


def ref_exists(ref: str) -> bool:
    result = subprocess.run(["git", "show-ref", "--verify", "--quiet", ref])
    return result.returncode == 0


def source_ref(source_branch: str, remote: str) -> str:
    local_ref = f"refs/heads/{source_branch}"
    remote_ref = f"refs/remotes/{remote}/{source_branch}"
    if ref_exists(local_ref):
        return source_branch
    if ref_exists(remote_ref):
        return f"{remote}/{source_branch}"
    raise SystemExit(f"Source branch not found locally or on {remote}: {source_branch}")


def checkout_target_branch(target_branch: str, remote: str, dry_run: bool) -> None:
    if dry_run:
        run(["git", "checkout", target_branch], dry_run=True)
        return

    if ref_exists(f"refs/heads/{target_branch}"):
        run(["git", "checkout", target_branch], dry_run=dry_run)
        return

    remote_ref = f"refs/remotes/{remote}/{target_branch}"
    if ref_exists(remote_ref):
        run(["git", "checkout", "-B", target_branch, f"{remote}/{target_branch}"], dry_run=dry_run)
        return

    raise SystemExit(f"Target branch not found locally or on {remote}: {target_branch}")


def unmerged_paths() -> list[str]:
    raw = git_output("diff", "--name-only", "--diff-filter=U", "-z")
    return [item for item in raw.split("\0") if item]


def has_stage(path: str, stage: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "-u", "--", path],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return any(line.split()[2] == stage for line in result.stdout.splitlines() if line.split())


def resolve_conflicts_with_source_branch(paths: list[str]) -> None:
    for path in paths:
        if has_stage(path, "3"):
            run(["git", "checkout", "--theirs", "--", path])
        else:
            run(["git", "rm", "-f", "--", path])
    run(["git", "add", "-A"])


def merge_in_progress() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "-q", "--verify", "MERGE_HEAD"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def merge_source(source: str, dry_run: bool) -> None:
    result = run(["git", "merge", "--no-edit", "-X", "theirs", source], check=False, dry_run=dry_run)
    if result.returncode == 0:
        return

    paths = unmerged_paths()
    if not paths:
        raise SystemExit(f"Merge failed and no conflicted paths were available to auto-resolve from source branch: {source}")

    print("Auto-resolving merge conflicts by taking the development branch version:")
    for path in paths:
        print(f"- {path}")
    resolve_conflicts_with_source_branch(paths)
    run(["git", "commit", "--no-edit"])


def main() -> int:
    args = parse_args()
    original_branch = current_branch()
    source_branch = args.source_branch or original_branch
    target_branch = args.target_branch

    if source_branch == target_branch:
        raise SystemExit("Source branch and target branch are the same; nothing to merge.")

    if not args.dry_run:
        require_clean_worktree()

    if args.dry_run:
        print(f"Plan: merge {source_branch} into {target_branch}, auto-resolve conflicts from {source_branch}, push {args.remote}/{target_branch}.")

    try:
        if not args.no_fetch:
            run(["git", "fetch", args.remote, "--prune"], dry_run=args.dry_run)

        source = source_ref(source_branch, args.remote) if not args.dry_run else source_branch
        checkout_target_branch(target_branch, args.remote, args.dry_run)
        run(["git", "pull", "--ff-only", args.remote, target_branch], dry_run=args.dry_run)
        merge_source(source, args.dry_run)
        run(["git", "push", args.remote, target_branch], dry_run=args.dry_run)

        if not args.no_restore and original_branch != target_branch:
            run(["git", "checkout", original_branch], dry_run=args.dry_run)
    except BaseException:
        if not args.dry_run:
            if merge_in_progress():
                subprocess.run(["git", "merge", "--abort"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if not args.no_restore and original_branch != current_branch():
                subprocess.run(["git", "checkout", original_branch], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        raise

    print(f"Pushed {target_branch} to {args.remote} for test-environment deployment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
