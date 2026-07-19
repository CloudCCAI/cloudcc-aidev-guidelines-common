---
kind: feature-spec
schema_version: 5
feature_id: FEAT-bimo-005
work_type: new_feature
title: "Chinese Template Cleanup"
status: verified
init_status: complete
init_completed_at: 2026-07-19T01:34:46Z
init_confirmed_by: user
owner_role: shared
owner_slug: bimo
created_at: 2026-07-19T01:34:46Z
created_by: "Bimo"
created_by_slug: bimo
created_by_source: global_git_config_user_name
created_by_developer_id: none
contributors: "Bimo"
task_ids: TASK-bimo-009
related_decisions: none
related_issues: none
policy_version: 3
updated_at: 2026-07-19T02:06:38Z
updated_by: "Bimo"
---

# FEAT-bimo-005 - Chinese Template Cleanup

## Background and Goal

- The distributable Skill carries parallel v4, English v5, and Chinese v5 human-readable templates, plus language-selection branches throughout the protocol and scripts.
- Retain one canonical Chinese template set, reduce dead compatibility assets and duplicate helpers, then perform a second independent cleanup scan.

## Scope

### In Scope

- Make canonical v5 human-readable templates Chinese and remove `templates/locales/zh-CN/`.
- New projects use fixed `zh-CN` output without a language-selection onboarding question.
- Continue reading older manifests containing `language: en` or `language: pending`; never rewrite existing historical documents automatically.
- Remove v4 template copies and platform templates that have no runtime consumer.
- Replace inline bilingual derived-view output with Chinese-only output.
- Consolidate safe duplicated catalog, atomic-write, state parsing, version and Codeup helpers where feasible.
- Convert v5 examples and tests to the Chinese-only contract.
- Run a second dead-reference, duplicate-content and generated-artifact scan after the first cleanup, then clean remaining safe findings.

### Out Of Scope

- Translating existing customer project files in place.
- Removing legacy v4 or early-v5 state readers and validators.
- Translating machine keys, enum values, IDs, paths, commands or raw evidence.
- Changing feature behavior unrelated to language/template/runtime cleanup.

## Current and Target Behavior

- Current: 60 tracked templates include approximately 710 lines each of v4 legacy, canonical English v5, and Chinese mirror content; new onboarding supports `pending`, `en`, and `zh-CN`.
- Target: one canonical Chinese v5 template set, no locale mirror, no new English output path, and explicit read compatibility for historical manifests.

## Design

- Move the Chinese mirror content into the existing catalog canonical paths so catalog paths remain stable.
- Keep a compatibility language reader for historical manifests, but make all renderers resolve to Chinese and make new manifests record `language: zh-CN` deterministically.
- Remove the language selection and reconfiguration interface; an early manifest checkpoint with `pending` is normalized to `zh-CN` when onboarding resumes.
- Gate the new fixed-language validation contract at Skill `5.0.3`; earlier v5 manifests retain read compatibility.
- Use Git history, not shipped inactive templates, as the archive for old v4 template sources.
- Prefer existing `scripts/lib/` utilities and catalog facts over repeated script-local implementations.

## Interface and Data Impact

- `project-onboarding.py start/adopt` no longer offer a meaningful language choice; `configure-modules.py` no longer changes document language.
- New `5.0.3` manifests use fixed `language: zh-CN`; validator accepts historical `en`/`pending` only for earlier versions.
- Template paths in `state-catalog.json` remain unchanged; their content becomes Chinese.
- `templates/locales/zh-CN/`, inactive root/docs/parallel templates, and unused platform templates are removed.
- Existing English project documents remain untouched and readable.

## Task Breakdown

- `TASK-bimo-009`: perform two cleanup passes, compatibility updates and full verification.

## Acceptance Criteria

- A fresh project initializes directly in Chinese without asking for language.
- All catalog-managed Markdown and generated current/team status content is Chinese.
- No `templates/locales` directory or canonical English human-readable template remains.
- Historical `language: en` and legacy v4 fixtures still validate and remain unmodified.
- No runtime reference points to deleted templates or removed language branches.
- Duplicate/dead-code scan is executed twice, with the second pass recorded.
- Full tests, compile/syntax checks, strict v5 examples, legacy fixture and repository-state validation pass.

## Risks and Rollback

- Risk: deleting templates claimed as v4 compatibility could break an undocumented consumer. Mitigation: prove no runtime references and preserve history in Git.
- Risk: fixed Chinese output could invalidate early-v5 manifests. Mitigation: version-gated validation and read-only compatibility for old `en`/`pending` values.
- Risk: broad helper consolidation could change parser behavior. Mitigation: make only test-covered equivalence refactors and defer uncertain consolidation.
- Rollback: restore deleted templates and language routing from the previous commit; do not rewrite generated customer documents.

## Handoff

- Read `scripts/lib/language.py`, manifest schema/catalog, canonical templates, onboarding/preflight/configure/validator scripts, derived-view generators and their tests.
- User-confirmed direction: keep only Chinese templates, clean once, rescan, and clean a second time.
- Verified outcome: both cleanup passes completed; all acceptance checks passed for Skill `5.0.3`.
