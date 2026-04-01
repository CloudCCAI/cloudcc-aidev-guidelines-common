#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATES_DIR="${ROOT_DIR}/templates"

TARGET_DIR="${1:-.}"
STATE_DIR_NAME="${2:-.claw}"
STATE_DIR_PATH="${TARGET_DIR%/}/${STATE_DIR_NAME}"

if [[ ! -d "${TEMPLATES_DIR}" ]]; then
  echo "Templates directory not found: ${TEMPLATES_DIR}" >&2
  exit 1
fi

mkdir -p "${STATE_DIR_PATH}"

for template in "${TEMPLATES_DIR}"/*.md; do
  filename="$(basename "${template}")"
  destination="${STATE_DIR_PATH}/${filename}"

  if [[ -e "${destination}" ]]; then
    echo "Skip existing file: ${destination}"
    continue
  fi

  cp "${template}" "${destination}"
  echo "Created: ${destination}"
done

echo
echo "State directory initialized at: ${STATE_DIR_PATH}"
echo "Next steps:"
echo "1. Fill ${STATE_DIR_NAME}/current-status.md"
echo "2. Fill ${STATE_DIR_NAME}/goals.md"
echo "3. Run validation: python3 \"${ROOT_DIR}/scripts/validate-state.py\" \"${STATE_DIR_PATH}\""
