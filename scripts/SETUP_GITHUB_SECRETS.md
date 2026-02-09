# Set GitHub Secrets for Heroku CI/CD

Follow these steps to configure GitHub Secrets required by the GitHub Actions workflow:

1. Install GitHub CLI (`gh`) and authenticate:
   - https://cli.github.com/
   - gh auth login

2. Prepare the required secrets in your shell environment (or enter interactively when running the script):
   - HEROKU_API_KEY — Your Heroku account API key
   - HEROKU_APP_BACKEND — Heroku app name for the backend (e.g., `mipedido-backend`)
   - HEROKU_APP_WS — Heroku app name for WebSocket Engine (e.g., `mipedido-ws`)
   - HEROKU_APP_REDIS_INDEXER — Heroku app name for Redis indexer (e.g., `mipedido-redis-indexer`)
   - HEROKU_APP_RATING_CRON — Heroku app name for rating cron (e.g., `mipedido-rating-cron`)

3. Run the script (bash):

   export HEROKU_API_KEY=...
   export HEROKU_APP_BACKEND=...
   export HEROKU_APP_WS=...
   export HEROKU_APP_REDIS_INDEXER=...
   export HEROKU_APP_RATING_CRON=...

   ./scripts/set_github_heroku_secrets.sh

   Or on Windows PowerShell:

   $env:HEROKU_API_KEY = '...'
   $env:HEROKU_APP_BACKEND = 'mipedido-backend'
   # etc.

   ./scripts/set_github_heroku_secrets.ps1

4. After running, check the repository Settings → Secrets → Actions to confirm the secrets were added.

Notes:
- The script uses the `gh` CLI which should be authenticated for the GitHub account that has write access to this repository.
- Use a GitHub token with repo permissions if running non-interactively.
