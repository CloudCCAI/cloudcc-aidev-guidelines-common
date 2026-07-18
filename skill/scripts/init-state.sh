#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-.}"

if [[ $# -gt 0 ]]; then
  shift
fi

# Backward-compatible acceptance of the old explicit state-directory argument.
# Only `.claw` is supported by the new protocol.
if [[ $# -gt 0 && "${1}" != --* ]]; then
  if [[ "${1}" != ".claw" ]]; then
    echo "Only the fixed .claw state directory is supported; got: ${1}" >&2
    exit 6
  fi
  shift
fi

exec python3 "${SCRIPT_DIR}/project-onboarding.py" start "${TARGET_DIR}" "$@"
