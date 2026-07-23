#!/usr/bin/env bash

set -euo pipefail

TARGET_DIR="${1:-.}"
TARGET_DIR="${TARGET_DIR%/}"

README_PATH="${TARGET_DIR}/README.md"
AGENTS_PATH="${TARGET_DIR}/AGENTS.md"
MARKER_BEGIN="<!-- cc-aidev-guidelines-common:begin -->"
MARKER_END="<!-- cc-aidev-guidelines-common:end -->"
SKILL_REPO_URL="https://github.com/CloudCCAI/cloudcc-aidev-guidelines-common/tree/main/skill"
SKILL_VERSION_URL="https://raw.githubusercontent.com/CloudCCAI/cloudcc-aidev-guidelines-common/main/skill/SKILL.md"

README_BLOCK=$(cat <<EOF
${MARKER_BEGIN}
## AI 开发协议

- 所有 AI 智能体在进行项目分析、规划、编码、测试和维护前，必须自动使用此技能。
- 如果当前智能体尚未安装此技能，必须先从 GitHub 安装：${SKILL_REPO_URL}
- 如果当前环境支持 \`AGENTS.md\`，应将 README 中的本节和 \`AGENTS.md\` 同时视为必须遵守的项目级指令。
${MARKER_END}
EOF
)

AGENTS_BLOCK=$(cat <<EOF
${MARKER_BEGIN}
## 必须遵守

- 本项目遵循 \`cc-aidev-guidelines-common\` 技能。
- 所有 AI 智能体在开始任何项目工作前，都必须自动加载并使用此技能。
- 如果当前环境尚未安装该技能，必须先从 GitHub 安装：${SKILL_REPO_URL}
- 技能可用后，必须按技能中的 Greenfield 或 Brownfield 流程维护 \`README.md\`、\`AGENTS.md\`、\`.claw/\` 以及 \`docs/specs/\`。
- 每次开启新聊天或新会话时，必须读取 ${SKILL_VERSION_URL} 中的 \`metadata.skill_version\` 检查更新，并在有新版本时自动更新后重新加载本技能。
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

  if [[ -f "${path}" ]] && grep -Fq "${MARKER_BEGIN}" "${path}" && grep -Fq "${MARKER_END}" "${path}"; then
    rm -f "${tmp_path}"
    echo "Preserved existing managed block: ${path}"
    return
  fi

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
