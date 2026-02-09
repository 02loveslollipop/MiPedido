#!/usr/bin/env bash
set -euo pipefail

# Usage: export HEROKU_API_KEY=... HEROKU_APP_BACKEND=... && ./scripts/set_github_heroku_secrets.sh
# This script requires GitHub CLI (gh) authenticated and run from the repository root.

REQUIRED_SECRETS=(
  HEROKU_API_KEY
  HEROKU_APP_BACKEND
  HEROKU_APP_WS
  HEROKU_APP_REDIS_INDEXER
  HEROKU_APP_RATING_CRON
)

# Check gh
if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install from https://cli.github.com/ and run 'gh auth login' first."
  exit 1
fi

# Ensure we're in a git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Run this script from the repository root."
  exit 1
fi

# Loop through required secrets and set them (read from env or ask)
for s in "${REQUIRED_SECRETS[@]}"; do
  val=""
  if [ -n "${!s-}" ]; then
    val="${!s}"
  else
    read -r -p "Enter value for $s: " val
  fi

  echo "Setting GitHub secret $s..."
  # Use gh to set secret for the current repo
  echo -n "$val" | gh secret set "$s" --body - || { echo "Failed to set $s"; exit 1; }
  echo "Set $s"
done

echo "All secrets set. Verify in GitHub under Settings -> Secrets -> Actions."
