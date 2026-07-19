# DevOps Environment Assets

This directory stores customer-environment-specific build and configuration examples.

Each environment directory owns its own `Dockerfile` and `.env.example`. The generated files are reservations only: customize and verify them against the application before using them to build or deploy.

Rules:

- Never commit real secret values. Copy `.env.example` to an ignored `.env` only in an appropriate local or deployment system.
- Keep one independently reviewed `Dockerfile` per customer environment.
- Add new environments with `project-onboarding.py devops-assets`; existing files are preserved.
- Do not treat a generated placeholder as evidence of a successful build or deployment.
