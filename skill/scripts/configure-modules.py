#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent


def load_onboarding_module() -> Any:
    module_path = SCRIPT_DIR / "project-onboarding.py"
    spec = importlib.util.spec_from_file_location("cc_project_onboarding", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ONBOARDING = load_onboarding_module()


def emit(result: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return
    print(f"status: {result.get('status')}")
    if result.get("message"):
        print(result["message"])


def normalize_switch(value: str | None, current: bool) -> bool:
    if value is None:
        return current
    return value == "on"


def command_status(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    project_root = ONBOARDING.ensure_project_root(args.project_root)
    manifest = ONBOARDING.load_manifest(project_root)
    return {
        "status": "ok",
        "project_root": str(project_root),
        "language": ONBOARDING.manifest_language(manifest),
        "modules": manifest.get("modules", {}),
        "module_config": manifest.get("module_config", {}),
    }, ONBOARDING.EXIT_OK


def command_set(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    project_root = ONBOARDING.ensure_project_root(args.project_root)
    timestamp = ONBOARDING.utc_now(args.now)
    with ONBOARDING.onboarding_lock(project_root):
        manifest = ONBOARDING.load_manifest(project_root)
        current = manifest.get("modules")
        if not isinstance(current, dict):
            current = {}
        modules = {
            "project_state": normalize_switch(args.project_state, bool(current.get("project_state", False))),
            "collaboration_gate": normalize_switch(
                args.collaboration_gate, bool(current.get("collaboration_gate", False))
            ),
            "change_review": normalize_switch(args.change_review, bool(current.get("change_review", False))),
        }
        ONBOARDING.validate_module_dependencies(modules)
        changed = modules != current
        manifest["modules"] = modules
        if not modules["project_state"]:
            manifest["project_mode"] = "not_applicable"
        elif not bool(current.get("project_state", False)):
            manifest["project_mode"] = "pending"

        module_config = manifest.setdefault("module_config", {})
        if not isinstance(module_config, dict):
            module_config = {}
            manifest["module_config"] = module_config
        module_config["collaboration_gate"] = (
            ".claw/collaboration-config.yaml" if modules["collaboration_gate"] else "none"
        )
        module_config["change_review"] = (
            ".claw/review-config.yaml" if modules["change_review"] else "none"
        )

        initialization = manifest.setdefault("initialization", {})
        if not isinstance(initialization, dict):
            initialization = {}
            manifest["initialization"] = initialization
        if changed and initialization.get("status") == "ready":
            initialization["status"] = "needs_review"
            initialization["completed_at"] = "none"
            initialization["confirmed_by"] = "none"

        ONBOARDING.validate_mode_for_modules(manifest, allow_pending=True)

        ONBOARDING.write_manifest(project_root, manifest)
        created = ONBOARDING.sync_files(project_root, manifest, timestamp)
        result = ONBOARDING.status_result(project_root, manifest)
        result["changed"] = changed
        result["created"] = created
        result["message"] = "configuration updated; existing documents were preserved"
        return result, ONBOARDING.EXIT_NEEDS_INPUT if result["next"] else ONBOARDING.EXIT_OK


def command_review(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    project_root = ONBOARDING.ensure_project_root(args.project_root)
    timestamp = ONBOARDING.utc_now(args.now)
    with ONBOARDING.onboarding_lock(project_root):
        manifest = ONBOARDING.load_manifest(project_root)
        modules = manifest.get("modules")
        if not isinstance(modules, dict) or not modules.get("change_review"):
            raise ONBOARDING.OnboardingError(
                "module_disabled",
                "change_review is disabled; enable it before configuring review policy",
                ONBOARDING.EXIT_INVALID_INPUT,
            )
        ONBOARDING.sync_files(project_root, manifest, timestamp)
        config_path = project_root / ".claw" / "review-config.yaml"
        reviewers = args.reviewers.strip() if args.reviewers else "none"
        checks = args.required_checks.strip() if args.required_checks else "none"
        ONBOARDING.update_top_level_fields(
            config_path,
            {
                "platform": args.platform,
                "target_branch": args.target_branch,
                "reviewers": reviewers,
                "required_checks": checks,
                "creation_policy": args.creation_policy,
                "token_storage": "local_only",
                "init_status": "complete",
                "init_completed_at": timestamp,
                "init_confirmed_by": args.confirmed_by,
                "updated_at": timestamp,
                "updated_by": args.confirmed_by,
            },
        )
        file_status = manifest.setdefault("file_status", {})
        if not isinstance(file_status, dict):
            file_status = {}
            manifest["file_status"] = file_status
        file_status["review_config"] = "complete"
        module_config = manifest.setdefault("module_config", {})
        if not isinstance(module_config, dict):
            module_config = {}
            manifest["module_config"] = module_config
        module_config["change_review"] = ".claw/review-config.yaml"
        ONBOARDING.write_manifest(project_root, manifest)
        result = ONBOARDING.status_result(project_root, manifest)
        result["configured"] = {
            "platform": args.platform,
            "target_branch": args.target_branch,
            "creation_policy": args.creation_policy,
        }
        return result, ONBOARDING.EXIT_NEEDS_INPUT if result["next"] else ONBOARDING.EXIT_OK


def add_common(parser: argparse.ArgumentParser, include_now: bool = False) -> None:
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    if include_now:
        parser.add_argument("--now", help="fixed UTC timestamp for deterministic automation")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Configure cc-aidev-guidelines-common feature modules")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status")
    add_common(status)

    set_parser = subparsers.add_parser("set")
    add_common(set_parser, include_now=True)
    set_parser.add_argument("--project-state", choices=("on", "off"))
    set_parser.add_argument("--collaboration-gate", choices=("on", "off"))
    set_parser.add_argument("--change-review", choices=("on", "off"))

    review = subparsers.add_parser("review")
    add_common(review, include_now=True)
    review.add_argument("--platform", required=True, choices=("codeup", "github"))
    review.add_argument("--target-branch", required=True)
    review.add_argument("--reviewers", default="none")
    review.add_argument("--required-checks", default="none")
    review.add_argument("--creation-policy", choices=("manual", "automatic"), default="manual")
    review.add_argument("--confirmed-by", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "status":
            result, exit_code = command_status(args)
        elif args.command == "set":
            result, exit_code = command_set(args)
        elif args.command == "review":
            result, exit_code = command_review(args)
        else:
            raise AssertionError(args.command)
    except ONBOARDING.OnboardingError as exc:
        result = {"status": "error", "error": exc.code, "message": str(exc)}
        exit_code = exc.exit_code
    except OSError as exc:
        result = {"status": "error", "error": "io_error", "message": str(exc)}
        exit_code = ONBOARDING.EXIT_IO_ERROR
    emit(result, args.json)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
