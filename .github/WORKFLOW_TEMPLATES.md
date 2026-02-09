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
- If your Docker context places files into `/app`, keep `PYTHONPATH=/app` or adjust imports accordingly.

## Cron jobs & Heroku Scheduler ⚙️
- For periodic or one-off tasks (cron jobs) we recommend using **Heroku Scheduler**. Typical patterns:
  - Compiled binaries (Go): build & release the image as a worker process (e.g. `rating-cron: ./rating-cron-binary`) and configure Heroku Scheduler to run a one-off command like:
    - `heroku run ./rating-cron-binary --app <HEROKU_APP>`
  - Python scripts: schedule a command such as `python backend/scripts/fill_db.py` via the Heroku Scheduler UI targeting your app.
- You can also release a `worker` process type and have it run continuously, but that will incur running dyno costs; for single-run cron jobs, Scheduler is simpler and cost-efficient.
- To test a worker after a deploy you can run:
  - `heroku run --app <HEROKU_APP> "<command>"` (one-off run)
  - or temporarily scale a worker: `heroku ps:scale worker=1` and inspect `heroku logs --tail --app <HEROKU_APP>`.
- Note: GitHub Actions cannot manage the Heroku Scheduler add-on directly; Scheduler must be configured through the Heroku Dashboard or API.

### Example Scheduler entries (your request)
- **rating-cron** — Daily at 02:00 UTC
  - Heroku Scheduler command: `heroku run --app <HEROKU_APP> ./rating-cron-binary`
  - Suggestion: ensure your binary accepts a `--once` or `--run-once` flag if needed, or use an entrypoint script that exits when done.
- **redisIndexerCronJob** — Every 3 hours
  - Heroku Scheduler command: `heroku run --app <HEROKU_APP> ./redis-indexer-binary`

If you want, I can add these example entries to the docs in a more structured table or add a sample Scheduler API call that configures them automatically (requires Heroku API key + permission).

If you want, I can: (A) open a PR with these files (draft), (B) make these files copy directly into the service directories and open a PR, or (C) add CI tests that validate the templates format. Which do you prefer?