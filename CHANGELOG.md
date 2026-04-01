# Changelog

## 2.0.0 - 2026-04-01

- Refactored the skill into a layered project state protocol.
- Added explicit read and update triggers for all six state files.
- Added source-of-truth rules to prevent duplicated facts.
- Added `STATE-MODEL.md` as a detailed reference document.
- Reworked all templates with YAML front matter and machine-stable fields.
- Added `scripts/init-state.sh` for quick project bootstrapping.
- Added `scripts/validate-state.py` for basic state structure validation.
- Added `examples/sample-project/.claw/` with a complete sample state set.
- Updated `README.md` for installation, validation, and publishing readiness.
