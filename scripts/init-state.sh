#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATES_DIR="${ROOT_DIR}/templates"
DOC_TEMPLATES_DIR="${TEMPLATES_DIR}/docs"
INTEGRATION_QUEUE_TEMPLATE="${TEMPLATES_DIR}/integration-queue.md"
TEAM_STATUS_TEMPLATE="${TEMPLATES_DIR}/team-status.md"
GUIDANCE_SCRIPT="${ROOT_DIR}/scripts/ensure-agent-guidance.sh"

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
  "task-archive.md"
  "test-report.md"
  "devops.md"
)

if [[ ! -d "${TEMPLATES_DIR}" ]]; then
  echo "Templates directory not found: ${TEMPLATES_DIR}" >&2
  exit 1
fi

if [[ ! -f "${GUIDANCE_SCRIPT}" ]]; then
  echo "Agent guidance script not found: ${GUIDANCE_SCRIPT}" >&2
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
mkdir -p "${STATE_DIR_PATH}/developers"
mkdir -p "${STATE_DIR_PATH}/assignments"
mkdir -p "${STATE_DIR_PATH}/tasks"

bash "${GUIDANCE_SCRIPT}" "${TARGET_DIR}"

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
INTEGRATION_QUEUE_DESTINATION="${STATE_DIR_PATH}/integration-queue.md"
TEAM_STATUS_DESTINATION="${STATE_DIR_PATH}/team-status.md"

if [[ ! -f "${SPEC_TEMPLATE_SOURCE}" ]]; then
  echo "Feature spec template not found: ${SPEC_TEMPLATE_SOURCE}" >&2
  exit 1
fi

if [[ ! -f "${BASELINE_TEMPLATE_SOURCE}" ]]; then
  echo "Project baseline template not found: ${BASELINE_TEMPLATE_SOURCE}" >&2
  exit 1
fi

if [[ ! -f "${INTEGRATION_QUEUE_TEMPLATE}" ]]; then
  echo "Integration queue template not found: ${INTEGRATION_QUEUE_TEMPLATE}" >&2
  exit 1
fi

if [[ ! -f "${TEAM_STATUS_TEMPLATE}" ]]; then
  echo "Team status template not found: ${TEAM_STATUS_TEMPLATE}" >&2
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

if [[ -e "${INTEGRATION_QUEUE_DESTINATION}" ]]; then
  echo "Skip existing file: ${INTEGRATION_QUEUE_DESTINATION}"
else
  render_template "${INTEGRATION_QUEUE_TEMPLATE}" "${INTEGRATION_QUEUE_DESTINATION}"
  echo "Created: ${INTEGRATION_QUEUE_DESTINATION}"
fi

if [[ -e "${TEAM_STATUS_DESTINATION}" ]]; then
  echo "Skip existing file: ${TEAM_STATUS_DESTINATION}"
else
  render_template "${TEAM_STATUS_TEMPLATE}" "${TEAM_STATUS_DESTINATION}"
  echo "Created: ${TEAM_STATUS_DESTINATION}"
fi

echo
echo "State directory initialized at: ${STATE_DIR_PATH}"
echo "Feature specs directory initialized at: ${DOCS_SPEC_DIR}"
echo "Async parallel directories initialized at: ${STATE_DIR_PATH}/developers, ${STATE_DIR_PATH}/assignments, ${STATE_DIR_PATH}/tasks"
echo "Project guidance refreshed in: ${TARGET_DIR}/README.md and ${TARGET_DIR}/AGENTS.md"
echo "Next steps:"
echo "1. Review README.md and AGENTS.md to confirm the managed skill declaration still fits the project context"
echo "2. Fill ${STATE_DIR_NAME}/current-status.md"
echo "3. Fill ${STATE_DIR_NAME}/goals.md"
echo "4. Create or update ${STATE_DIR_NAME}/task-board.md"
echo "5. For existing projects, copy docs/specs/_project-baseline-template.md to docs/specs/PROJECT-BASELINE.md"
echo "6. For non-trivial work, copy docs/specs/_feature-spec-template.md to docs/specs/FEAT-xxx-feature-name.md"
echo "7. For async parallel work, create developer records, assignment files, and per-task status files from templates/parallel/"
echo "8. Before local async development, run: python3 \"${ROOT_DIR}/scripts/dev-login.py\" \"${STATE_DIR_PATH}\" --ssh-key ~/.ssh/id_ed25519_cc_dev --task TASK-xxx --files path/to/file"
echo "9. Before CI merge or assignment-only checks, run: python3 \"${ROOT_DIR}/scripts/check-assignment.py\" \"${STATE_DIR_PATH}\" --developer DEV-xxx --task TASK-xxx --files path/to/file"
echo "10. For a GitHub PR gate example, copy templates/github-workflows/check-assignment.yml into .github/workflows/"
echo "11. For manager team status, run: python3 \"${ROOT_DIR}/scripts/summarize-team-status.py\" \"${STATE_DIR_PATH}\" --write"
echo "12. Run validation: python3 \"${ROOT_DIR}/scripts/validate-state.py\" \"${STATE_DIR_PATH}\""
