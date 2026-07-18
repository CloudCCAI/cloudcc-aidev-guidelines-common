# Template profiles

v5 canonical templates are selected only through `state-catalog.json`:

- `core/` for manifest-driven initialization files
- `project-state/` for FEAT, TASK, Brownfield baseline, and event files
- `collaboration-gate/` for public identity, assignment, gate configuration, and derived team status
- `change-review/` for review configuration
- `locales/zh-CN/` mirrors every v5 human-readable Markdown template for projects whose manifest selects `language: zh-CN`; canonical template paths are English
- `platforms/` and `github-workflows/` for an explicitly enabled review platform

Root-level templates plus `docs/` and `parallel/` are retained only as v4 compatibility assets. The v5 initializer does not copy or load them, and new projects must not use them as a second state model.

Machine-readable YAML keys, enum values, IDs, paths, commands, and raw evidence are never localized. Existing project files are never translated automatically when the manifest language changes.
