## Plan: Migrate infra from Northflank → Heroku (eco) & MongoDB → Atlas 🚀

**TL;DR** — Move these services to Heroku (eco): **Backend API (Python FastAPI)**, **WebSocket Engine (Go)**, **redisIndexerCronJob** and **ratingCronJob** (Go cron jobs). Use **MongoDB Atlas** (you will create DB and user and provide the connection URI). Use an external Redis (you will provide host/creds). Use GitHub Actions to build Docker images and push to Heroku Container Registry.

---

## Important repo references (found)
- Backend DB usage: `backend/database/db.py` (reads `MONGODB_URL`, `DATABASE_NAME`)
- Backend env: `backend/utils/env.py` (defines `MONGODB_URL`, `DATABASE_NAME`, `REDIS_*`, `SECRET_KEY`, `ADMIN_*`, `BLOB_READ_WRITE_TOKEN`)
- Backend entrypoint: `backend/app.py` (uvicorn/fastapi app; production should use gunicorn + uvicorn worker)
- Backend requirements: `backend/requirements.txt`
- Cron jobs:
  - `redisIndexerCronJob/` (Dockerfile + `cmd/main/main.go`) — requires `MONGODB_URL`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
  - `ratingCronJob/` (Dockerfile + `cmd/main/main.go`) — requires `MONGODB_URL`
- WebSocket engine: `webSocketEngine/` (DockerFile + `cmd/main/main.go`) — binds to `PORT` and uses Mongo
- Seed script: `backend/scripts/fill_db.py` (uses `MONGODB_URL`)

---

## Deployment steps (high level)
1. Preparation (confirm choices)
   - You provide:
     - Atlas DB connection string (full `MONGODB_URL`) and DB name (or confirm default `mipedido`).
     - Redis credentials: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`.
     - Heroku app names (suggestions: `mipedido-backend`, `mipedido-ws`, `mipedido-redis-indexer`, `mipedido-rating-cron`) and owner account.
     - GitHub Actions secrets (`HEROKU_API_KEY`, `HEROKU_EMAIL`, app names as needed).
   - Decide IP access policy for Atlas (quick: allow `0.0.0.0/0` temporarily; recommended: VPC peering for production).

2. Repo changes (drafts to add)
   - Add `backend/Dockerfile` (multi-stage Python build) and `backend/Procfile` (e.g., `web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:$PORT`).
   - Add GitHub Actions workflows to build Docker images and push to Heroku Container Registry for each service.
   - Optionally add `Procfile` to direct processes in Heroku apps (for worker vs web types).

3. Heroku app creation
   - Create separate Heroku apps per service for isolation.
   - Add config vars:
     - `MONGODB_URL` — Atlas connection URI
     - `DATABASE_NAME` — optional (default `mipedido`)
     - `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` (or `REDIS_URL` parsed in code)
     - `SECRET_KEY`, `ADMIN_PRIVATE_KEY`, `ADMIN_PUBLIC_KEY`, `BLOB_READ_WRITE_TOKEN`, `LOG_LEVEL`, `SENTRY_DSN` (if any)
   - Optionally add logging or monitoring add-ons.

4. MongoDB Atlas
   - You create DB and user (readWrite on DB) and provide `MONGODB_URL` (include username/password and any options). Example: `mongodb+srv://user:pass@cluster0.xxxxxx.mongodb.net/mipedido?retryWrites=true&w=majority`.
   - Add Network Access entry: either allow `0.0.0.0/0` for quick rollout or plan a VPC peering for security.

5. Redis & Crons
   - Use provided Redis credentials and set Heroku config vars accordingly.
   - Cron jobs: use **Heroku Scheduler** to run the compiled binary or one-off commands (recommended), because current cron apps run, process once, and exit.
   - Alternative: deploy as `worker` process and implement internal scheduling.

6. CI/CD
   - Add GH Actions workflows to build, test, push, and release images to Heroku on pushes to `main`.
   - Add unit tests as part of CI (`pytest` for backend).

7. Data seeding & verification
   - Run `python backend/scripts/fill_db.py` (via `heroku run` or locally with `MONGODB_URL`) to seed the DB.
   - Run smoke tests: `GET /` (backend) and root for WebSocket Engine; run cron jobs and check Redis indices.

8. Frontend considerations
   - Frontends (`appAdmin`, `appCliente`, `appVendedor`) appear to be Flutter apps (Web builds). It is recommended to keep them on Vercel or similar; update their environment variables to point to the new Heroku host URLs and verify CORS.

9. Rollback & monitoring
   - Use Heroku release rollback or revert GH commit + re-deploy.
   - Add log drains or log add-ons to aggregate logs.

---

## Verification & testing checklist
- CI builds succeed and runs tests.
- Staging deployment: `heroku run python backend/scripts/fill_db.py` completes and DB accepts writes.
- Backend health endpoint responds, WebSocket Engine starts and binds to `PORT`, cron jobs run with expected logs.
- Redis indices created and keys exist after `redisIndexerCronJob` runs.
- Frontend can call the new Heroku endpoints (CORS already accepts `*` in FastAPI).

---

## Decisions & trade-offs
- Separate Heroku apps per service for isolation and easier scaling.
- Use Heroku Scheduler for cron jobs (simpler, fits current single-run cron jobs).
- Use external Redis (you provide credentials) rather than Heroku Redis add-on.

---

## Missing information I need from you
1. Atlas DB connection string (`MONGODB_URL`) including read/write user credentials.
2. Redis credentials: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`.
3. Heroku app names and which Heroku account should own them.
4. GitHub access to set `HEROKU_API_KEY` in repo secrets (or you'll set it).
5. Whether allowing Atlas IP `0.0.0.0/0` for rollout is acceptable or if you need VPC peering.
6. Any environment variables you prefer to rename or consolidate.

---

## Next steps (short)
1. You provide the missing items above.
2. I’ll draft the exact repo changes: `Dockerfile` for backend, `Procfile` examples, and GH Actions YAML templates.
3. After your review and approval, implement the changes and deploy to staging, run tests, then cut over to production.

---

> If you want, I can now create the template `Dockerfile` and GitHub Action workflow files as PR-ready drafts for your review. Would you like me to draft those files next? ✅
