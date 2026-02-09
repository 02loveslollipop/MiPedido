# Workflow & Dockerfile templates (how to use)

This file explains what the template files do and how to use them.

Files added in this PR:

- `.github/workflows/deploy-to-heroku-template.yml` — A configurable workflow that builds and pushes per-service Docker images to Heroku Container Registry and releases them.
- `docker/backend.Dockerfile.template` — Multi-stage Python Dockerfile for the backend (FastAPI + gunicorn). Copy/rename and adapt it to `backend/Dockerfile`.
- `backend/Procfile.template` — Procfile template for Heroku process types (web).

How to use:
1. Copy `docker/backend.Dockerfile.template` → `backend/Dockerfile` and update packaging commands if you use Poetry/poetry-builds/etc.
2. Copy `backend/Procfile.template` → `backend/Procfile` (or to repo root if deploying monorepo) and confirm process names.
3. Copy `.github/workflows/deploy-to-heroku-template.yml` → `.github/workflows/deploy-to-heroku.yml` and update the matrix entries to match your services and contexts.
4. Add GitHub repository secrets: `HEROKU_API_KEY` and `HEROKU_APP_<SERVICE>` for each service, e.g. `HEROKU_APP_BACKEND`.

Notes & tips:
- The template's smoke check hits `/health`. Ensure your service exposes a health endpoint.
- For cron jobs, the workflow releases worker images and expects you to use Heroku Scheduler (or a worker process defined in a Procfile).
- If your Docker context places files into `/app`, keep `PYTHONPATH=/app` or adjust imports accordingly.

If you want, I can: (A) open a PR with these files (draft), (B) make these files copy directly into the service directories and open a PR, or (C) add CI tests that validate the templates format. Which do you prefer?