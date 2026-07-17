#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import secrets
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


EMPTY_VALUES = {"", "none", "n/a", "na", "not_applicable"}
LOGIN_NAMESPACE = "cc-aidev-login"


def clean_value(value: object) -> str:
    cleaned = str(value).strip().strip('"').strip("'")
    if cleaned.startswith("`") and cleaned.endswith("`") and len(cleaned) >= 2:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def is_empty(value: object) -> bool:
    return clean_value(value).lower() in EMPTY_VALUES


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_command(args: list[str], input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def read_simple_yaml(path: Path) -> dict[str, object]:
    parsed: dict[str, object] = {}
    current_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if current_key and stripped.startswith("- "):
            current_value = parsed.setdefault(current_key, [])
            if isinstance(current_value, list):
                current_value.append(clean_value(stripped[2:]))
            continue

        if ":" not in stripped:
            current_key = None
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = clean_value(value)
        if value == "":
            parsed[key] = []
            current_key = key
        else:
            parsed[key] = value
            current_key = None

    return parsed


def public_key_identity(public_key: str) -> str:
    parts = clean_value(public_key).split()
    if len(parts) < 2:
        return ""
    return " ".join(parts[:2])


def load_developer_records(state_dir: Path) -> list[tuple[Path, dict[str, object]]]:
    developers_dir = state_dir / "developers"
    if not developers_dir.exists():
        return []
    records: list[tuple[Path, dict[str, object]]] = []
    for path in sorted(developers_dir.glob("*.y*ml")):
        records.append((path, read_simple_yaml(path)))
    return records


def active_identity_policy_findings(records: list[tuple[Path, dict[str, object]]]) -> list[str]:
    findings: list[str] = []
    by_username: dict[str, list[tuple[Path, dict[str, object]]]] = {}
    by_fingerprint: dict[str, list[tuple[Path, dict[str, object]]]] = {}
    by_public_key: dict[str, list[tuple[Path, dict[str, object]]]] = {}

    for path, fields in records:
        if clean_value(fields.get("status", "")) != "active":
            continue
        username = clean_value(fields.get("git_username", ""))
        fingerprint = clean_value(fields.get("ssh_signing_key_fingerprint", ""))
        public_identity = public_key_identity(clean_value(fields.get("public_key", "")))
        if username:
            by_username.setdefault(username, []).append((path, fields))
        if fingerprint:
            by_fingerprint.setdefault(fingerprint, []).append((path, fields))
        if public_identity:
            by_public_key.setdefault(public_identity, []).append((path, fields))

    for username, username_records in by_username.items():
        if len(username_records) <= 1:
            continue
        fingerprints = [
            clean_value(fields.get("ssh_signing_key_fingerprint", "")) for _path, fields in username_records
        ]
        ids = ", ".join(clean_value(fields.get("developer_id", path.stem)) for path, fields in username_records)
        if len(set(fingerprints)) != len(fingerprints) or any(not item for item in fingerprints):
            findings.append(
                f"blocked_duplicate_git_identity: git_username `{username}` is reused by active identities `{ids}` without distinct SSH signing key fingerprints"
            )
            continue
        missing_exceptions = [
            clean_value(fields.get("developer_id", path.stem))
            for path, fields in username_records
            if is_empty(fields.get("role_sharing_exception", ""))
        ]
        if missing_exceptions:
            findings.append(
                f"blocked_role_sharing_exception_missing: git_username `{username}` is reused but identities `{', '.join(missing_exceptions)}` do not record role_sharing_exception"
            )

    for fingerprint, fingerprint_records in by_fingerprint.items():
        if len(fingerprint_records) <= 1:
            continue
        ids = ", ".join(clean_value(fields.get("developer_id", path.stem)) for path, fields in fingerprint_records)
        findings.append(
            f"blocked_duplicate_ssh_identity: SSH signing key `{fingerprint}` is reused by active identities `{ids}`"
        )

    for public_identity, public_key_records in by_public_key.items():
        if len(public_key_records) <= 1:
            continue
        ids = ", ".join(clean_value(fields.get("developer_id", path.stem)) for path, fields in public_key_records)
        fingerprint = fingerprint_for_public_key(public_identity)
        findings.append(
            f"blocked_duplicate_public_key_identity: public key `{fingerprint}` is reused by active identities `{ids}`"
        )

    return findings


def resolve_cache_path(state_dir: Path, cache_path: str) -> Path:
    if cache_path:
        return Path(cache_path).expanduser()
    local_dir_name = ".ai-dev-local" if state_dir.name == ".ai-dev" else ".claw-local"
    return state_dir.parent / local_dir_name / "identity.json"


def load_cached_identity(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_cached_identity(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def derive_public_key(private_key_path: Path) -> str:
    result = run_command(["ssh-keygen", "-y", "-f", str(private_key_path)])
    if result.returncode != 0:
        raise RuntimeError(f"failed_to_derive_public_key: {result.stderr.strip()}")
    return result.stdout.strip()


def fingerprint_for_public_key(public_key: str) -> str:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        public_key_path = Path(handle.name)
        handle.write(public_key.strip() + "\n")
    try:
        result = run_command(["ssh-keygen", "-lf", str(public_key_path)])
    finally:
        public_key_path.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(f"failed_to_compute_fingerprint: {result.stderr.strip()}")
    parts = result.stdout.strip().split()
    if len(parts) < 2:
        raise RuntimeError("failed_to_parse_fingerprint")
    return parts[1]


def find_matching_identity(
    records: list[tuple[Path, dict[str, object]]],
    public_key: str,
    fingerprint: str,
    requested_developer: str,
) -> tuple[Path, dict[str, object], list[str]]:
    findings: list[str] = []
    public_identity = public_key_identity(public_key)
    matches: list[tuple[Path, dict[str, object]]] = []

    for path, fields in records:
        developer_id = clean_value(fields.get("developer_id", path.stem))
        if requested_developer and developer_id != requested_developer:
            continue
        record_public_key = public_key_identity(clean_value(fields.get("public_key", "")))
        record_fingerprint = clean_value(fields.get("ssh_signing_key_fingerprint", ""))
        if record_public_key and record_public_key == public_identity:
            matches.append((path, fields))
            continue
        if record_fingerprint and record_fingerprint == fingerprint:
            matches.append((path, fields))

    if not matches:
        if requested_developer:
            findings.append(f"blocked_identity_key_mismatch: key does not match `{requested_developer}`")
        else:
            findings.append("blocked_identity_unknown: no developer record matches this SSH key")
        raise PermissionError("\n".join(findings))

    unique_by_id: dict[str, tuple[Path, dict[str, object]]] = {}
    for path, fields in matches:
        unique_by_id[clean_value(fields.get("developer_id", path.stem))] = (path, fields)

    if len(unique_by_id) > 1:
        ids = ", ".join(sorted(unique_by_id))
        findings.append(f"blocked_identity_ambiguous: SSH key matches multiple identities `{ids}`")
        raise PermissionError("\n".join(findings))

    path, fields = next(iter(unique_by_id.values()))
    status = clean_value(fields.get("status", ""))
    if status != "active":
        developer_id = clean_value(fields.get("developer_id", path.stem))
        findings.append(f"blocked_member_inactive: developer `{developer_id}` status is `{status}`")
        raise PermissionError("\n".join(findings))

    return path, fields, findings


def verify_key_possession(private_key_path: Path, developer_id: str, public_key: str, fingerprint: str) -> str:
    if is_empty(public_key):
        raise PermissionError(f"blocked_public_key_missing: developer `{developer_id}` has no public_key")

    challenge = (
        f"cc-aidev-login\n"
        f"developer_id={developer_id}\n"
        f"fingerprint={fingerprint}\n"
        f"issued_at={utc_now()}\n"
        f"nonce={secrets.token_urlsafe(32)}\n"
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        challenge_path = temp_path / "challenge.txt"
        allowed_signers_path = temp_path / "allowed_signers"
        challenge_path.write_text(challenge, encoding="utf-8")
        allowed_signers_path.write_text(f"{developer_id} {public_key.strip()}\n", encoding="utf-8")

        sign_result = run_command(
            ["ssh-keygen", "-Y", "sign", "-f", str(private_key_path), "-n", LOGIN_NAMESPACE, str(challenge_path)]
        )
        if sign_result.returncode != 0:
            raise PermissionError(f"blocked_key_sign_failed: {sign_result.stderr.strip()}")

        signature_path = challenge_path.with_suffix(challenge_path.suffix + ".sig")
        verify_result = run_command(
            [
                "ssh-keygen",
                "-Y",
                "verify",
                "-f",
                str(allowed_signers_path),
                "-I",
                developer_id,
                "-n",
                LOGIN_NAMESPACE,
                "-s",
                str(signature_path),
            ],
            input_text=challenge,
        )
        if verify_result.returncode != 0:
            detail = verify_result.stderr.strip() or verify_result.stdout.strip()
            raise PermissionError(f"blocked_key_verify_failed: {detail}")

    return "verified"


def run_assignment_check(
    state_dir: Path,
    developer_id: str,
    task_id: str,
    branch: str,
    git_username: str,
    fingerprint: str,
    files: list[str],
) -> tuple[bool, str]:
    script_path = Path(__file__).resolve().with_name("check-assignment.py")
    command = [
        sys.executable,
        str(script_path),
        str(state_dir),
        "--developer",
        developer_id,
        "--task",
        task_id,
        "--ssh-signing-key-fingerprint",
        fingerprint,
    ]
    if branch:
        command.extend(["--branch", branch])
    if git_username:
        command.extend(["--git-username", git_username])
    if files:
        command.append("--files")
        command.extend(files)

    result = run_command(command)
    output = "\n".join(item for item in [result.stdout.strip(), result.stderr.strip()] if item)
    return result.returncode == 0, output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify the current local developer identity before development starts."
    )
    parser.add_argument("state_dir", help="Path to .claw or .ai-dev")
    parser.add_argument("--ssh-key", default="", help="Path to the local private SSH key used for login signing")
    parser.add_argument("--developer", default="", help="Optional expected developer id such as DEV-alice")
    parser.add_argument("--task", default="", help="Optional task id; when provided, assignment scope is checked")
    parser.add_argument("--branch", default="", help="Current branch or intended task branch")
    parser.add_argument("--git-username", default="", help="Optional Git platform username to check against the record")
    parser.add_argument("--files", nargs="*", default=[], help="Changed or intended file paths for assignment checks")
    parser.add_argument("--cache-path", default="", help="Optional local identity cache path")
    parser.add_argument("--no-cache", action="store_true", help="Do not read or write local identity cache")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    state_dir = Path(args.state_dir).expanduser()
    cache_path = resolve_cache_path(state_dir, args.cache_path)
    cache = {} if args.no_cache else load_cached_identity(cache_path)
    ssh_key_arg = args.ssh_key or clean_value(cache.get("ssh_key_path", ""))
    details: dict[str, object] = {
        "status": "blocked",
        "state_dir": str(state_dir),
        "cache_path": "" if args.no_cache else str(cache_path),
    }

    try:
        if not ssh_key_arg:
            raise PermissionError("blocked_login_required: provide --ssh-key for the first login")

        private_key_path = Path(ssh_key_arg).expanduser()
        if not private_key_path.exists():
            raise PermissionError(f"blocked_ssh_key_missing: `{private_key_path}` does not exist")

        derived_public_key = derive_public_key(private_key_path)
        derived_fingerprint = fingerprint_for_public_key(derived_public_key)
        records = load_developer_records(state_dir)
        identity_policy_findings = active_identity_policy_findings(records)
        if identity_policy_findings:
            raise PermissionError("\n".join(identity_policy_findings))
        developer_path, developer, _findings = find_matching_identity(
            records,
            derived_public_key,
            derived_fingerprint,
            args.developer,
        )

        developer_id = clean_value(developer.get("developer_id", developer_path.stem))
        record_public_key = clean_value(developer.get("public_key", ""))
        record_fingerprint = clean_value(developer.get("ssh_signing_key_fingerprint", ""))
        expected_git_username = clean_value(developer.get("git_username", ""))
        git_username = args.git_username or expected_git_username

        if record_fingerprint and record_fingerprint != derived_fingerprint:
            raise PermissionError("blocked_ssh_signing_key_mismatch: derived fingerprint does not match record")
        if args.git_username and expected_git_username and expected_git_username != args.git_username:
            raise PermissionError(
                f"blocked_git_username_mismatch: expected `{expected_git_username}`, got `{args.git_username}`"
            )

        verify_key_possession(private_key_path, developer_id, record_public_key, derived_fingerprint)

        assignment_output = ""
        if args.task:
            assignment_allowed, assignment_output = run_assignment_check(
                state_dir,
                developer_id,
                args.task,
                args.branch,
                git_username,
                derived_fingerprint,
                args.files,
            )
            if not assignment_allowed:
                raise PermissionError(assignment_output or "blocked_assignment_check_failed")

        details.update(
            {
                "status": "allowed",
                "developer_id": developer_id,
                "developer_record": str(developer_path),
                "git_username": git_username,
                "ssh_signing_key_fingerprint": derived_fingerprint,
                "task_id": args.task,
                "branch": args.branch,
                "files": args.files,
                "verified": [
                    "developer_record_active",
                    "ssh_key_fingerprint_matched",
                    "ssh_key_possession_verified",
                ]
                + (["assignment_scope_allowed"] if args.task else []),
            }
        )
        if assignment_output:
            details["assignment_check"] = assignment_output

        if not args.no_cache:
            save_cached_identity(
                cache_path,
                {
                    "developer_id": developer_id,
                    "ssh_key_path": str(private_key_path),
                    "ssh_signing_key_fingerprint": derived_fingerprint,
                    "git_username": git_username,
                    "updated_at": utc_now(),
                },
            )

    except (RuntimeError, PermissionError, json.JSONDecodeError) as exc:
        details["findings"] = [line for line in str(exc).splitlines() if line]
        if args.json:
            print(json.dumps(details, indent=2, sort_keys=True))
        else:
            for finding in details["findings"]:
                print(finding, file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(details, indent=2, sort_keys=True))
    else:
        print(f"allowed: developer `{details['developer_id']}` identity verified")
        if args.task:
            print(f"allowed: developer `{details['developer_id']}` may work on `{args.task}`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
