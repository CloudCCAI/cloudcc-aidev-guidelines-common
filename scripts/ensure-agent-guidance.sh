#!/usr/bin/env bash

set -euo pipefail

TARGET_DIR="${1:-.}"
TARGET_DIR="${TARGET_DIR%/}"

README_PATH="${TARGET_DIR}/README.md"
AGENTS_PATH="${TARGET_DIR}/AGENTS.md"
MARKER_BEGIN="<!-- cc-aidev-guidelines-common:begin -->"
MARKER_END="<!-- cc-aidev-guidelines-common:end -->"
SKILL_REPO_URL="https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common"

README_BLOCK=$(cat <<EOF
${MARKER_BEGIN}
## AI Development Protocol

This project follows the \`cc-aidev-guidelines-common\` skill.

- All AI agents must automatically use this skill before project analysis, planning, implementation, testing, or maintenance.
- If the current agent does not have this skill installed, install it first from GitHub: ${SKILL_REPO_URL}
- When the environment supports \`AGENTS.md\`, treat both this README section and \`AGENTS.md\` as mandatory project instructions.

本项目遵循 \`cc-aidev-guidelines-common\` 技能规范。

- 所有 AI 智能体在进行项目分析、规划、编码、测试和维护前，必须自动使用此技能。
- 如果当前智能体尚未安装此技能，必须先从 GitHub 安装：${SKILL_REPO_URL}
- 如果当前环境支持 \`AGENTS.md\`，应将 README 中的本节和 \`AGENTS.md\` 同时视为必须遵守的项目级指令。
${MARKER_END}
EOF
)

AGENTS_BLOCK=$(cat <<EOF
${MARKER_BEGIN}
## Required Skill

- This project follows the \`cc-aidev-guidelines-common\` skill.
- Every AI agent must automatically load and use this skill before any project work.
- If the skill is not installed in the current environment, install it first from GitHub: ${SKILL_REPO_URL}
- After the skill is available, follow its greenfield or brownfield workflow to maintain \`README.md\`, \`AGENTS.md\`, \`.claw/\` or \`.ai-dev/\`, and \`docs/specs/\`.

## 必须遵守

- 本项目遵循 \`cc-aidev-guidelines-common\` 技能。
- 所有 AI 智能体在开始任何项目工作前，都必须自动加载并使用此技能。
- 如果当前环境尚未安装该技能，必须先从 GitHub 安装：${SKILL_REPO_URL}
- 技能可用后，必须按技能中的 Greenfield 或 Brownfield 流程维护 \`README.md\`、\`AGENTS.md\`、\`.claw/\` 或 \`.ai-dev/\` 以及 \`docs/specs/\`。
${MARKER_END}
EOF
)

strip_managed_block() {
  local path="$1"
  awk -v begin="${MARKER_BEGIN}" -v end="${MARKER_END}" '
    BEGIN { skip = 0 }
    index($0, begin) { skip = 1; next }
    index($0, end) { skip = 0; next }
    !skip { print }
  ' "${path}"
}

write_with_block() {
  local path="$1"
  local prelude="$2"
  local block="$3"
  local tmp_path
  tmp_path="$(mktemp)"

  if [[ -f "${path}" ]]; then
    strip_managed_block "${path}" > "${tmp_path}"
    if [[ -s "${tmp_path}" ]]; then
      printf "\n%s\n" "${block}" >> "${tmp_path}"
    else
      printf "%s\n" "${block}" > "${tmp_path}"
    fi
  else
    if [[ -n "${prelude}" ]]; then
      printf "%s\n\n%s\n" "${prelude}" "${block}" > "${tmp_path}"
    else
      printf "%s\n" "${block}" > "${tmp_path}"
    fi
  fi

  mv "${tmp_path}" "${path}"
  echo "Updated: ${path}"
}

mkdir -p "${TARGET_DIR}"

write_with_block "${README_PATH}" "# $(basename "${TARGET_DIR}")" "${README_BLOCK}"
write_with_block "${AGENTS_PATH}" "# AGENTS" "${AGENTS_BLOCK}"
