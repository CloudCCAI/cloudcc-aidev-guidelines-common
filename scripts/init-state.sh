#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATES_DIR="${ROOT_DIR}/templates"
DOC_TEMPLATES_DIR="${TEMPLATES_DIR}/docs"

TARGET_DIR="${1:-.}"
STATE_DIR_NAME="${2:-.claw}"
STATE_DIR_PATH="${TARGET_DIR%/}/${STATE_DIR_NAME}"
DOCS_SPEC_DIR="${TARGET_DIR%/}/docs/specs"
TIMESTAMP="$(date -u "+%Y-%m-%dT%H:%M:%SZ")"
CALENDAR_DATE="$(date -u "+%Y-%m-%d")"

STATE_TEMPLATE_FILES=(
  "current-status.md"
  "goals.md"
  "decisions.md"
  "issue-list.md"
  "task-board.md"
  "test-report.md"
  "devops.md"
)

if [[ ! -d "${TEMPLATES_DIR}" ]]; then
  echo "Templates directory not found: ${TEMPLATES_DIR}" >&2
  exit 1
fi

render_template() {
  local source_path="$1"
  local destination_path="$2"

  sed \
    -e "s/YYYY-MM-DDTHH:MM:SSZ/${TIMESTAMP}/g" \
    -e "s/YYYY-MM-DD/${CALENDAR_DATE}/g" \
    "${source_path}" > "${destination_path}"
}

mkdir -p "${STATE_DIR_PATH}"
mkdir -p "${DOCS_SPEC_DIR}"

for filename in "${STATE_TEMPLATE_FILES[@]}"; do
  template="${TEMPLATES_DIR}/${filename}"
  destination="${STATE_DIR_PATH}/${filename}"

  if [[ ! -f "${template}" ]]; then
    echo "State template not found: ${template}" >&2
    exit 1
  fi

  if [[ -e "${destination}" ]]; then
    echo "Skip existing file: ${destination}"
    continue
  fi

  render_template "${template}" "${destination}"
  echo "Created: ${destination}"
done

SPEC_TEMPLATE_SOURCE="${DOC_TEMPLATES_DIR}/feature-spec-template.md"
SPEC_TEMPLATE_DESTINATION="${DOCS_SPEC_DIR}/_feature-spec-template.md"
BASELINE_TEMPLATE_SOURCE="${DOC_TEMPLATES_DIR}/project-baseline-template.md"
BASELINE_TEMPLATE_DESTINATION="${DOCS_SPEC_DIR}/_project-baseline-template.md"

if [[ ! -f "${SPEC_TEMPLATE_SOURCE}" ]]; then
  echo "Feature spec template not found: ${SPEC_TEMPLATE_SOURCE}" >&2
  exit 1
fi

if [[ ! -f "${BASELINE_TEMPLATE_SOURCE}" ]]; then
  echo "Project baseline template not found: ${BASELINE_TEMPLATE_SOURCE}" >&2
  exit 1
fi

if [[ -e "${SPEC_TEMPLATE_DESTINATION}" ]]; then
  echo "Skip existing file: ${SPEC_TEMPLATE_DESTINATION}"
else
  render_template "${SPEC_TEMPLATE_SOURCE}" "${SPEC_TEMPLATE_DESTINATION}"
  echo "Created: ${SPEC_TEMPLATE_DESTINATION}"
fi

if [[ -e "${BASELINE_TEMPLATE_DESTINATION}" ]]; then
  echo "Skip existing file: ${BASELINE_TEMPLATE_DESTINATION}"
else
  render_template "${BASELINE_TEMPLATE_SOURCE}" "${BASELINE_TEMPLATE_DESTINATION}"
  echo "Created: ${BASELINE_TEMPLATE_DESTINATION}"
fi

echo
echo "State directory initialized at: ${STATE_DIR_PATH}"
echo "Feature specs directory initialized at: ${DOCS_SPEC_DIR}"
echo "Next steps:"
echo "1. Fill ${STATE_DIR_NAME}/current-status.md"
echo "2. Fill ${STATE_DIR_NAME}/goals.md"
echo "3. Create or update ${STATE_DIR_NAME}/task-board.md"
echo "4. For existing projects, copy docs/specs/_project-baseline-template.md to docs/specs/PROJECT-BASELINE.md"
echo "5. For non-trivial work, copy docs/specs/_feature-spec-template.md to docs/specs/FEAT-xxx-feature-name.md"
echo "6. Run validation: python3 \"${ROOT_DIR}/scripts/validate-state.py\" \"${STATE_DIR_PATH}\""
