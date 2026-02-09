<#
Usage: Set required environment variables or run interactively.
Requires GitHub CLI (gh) and that you're in the repo folder.
#>

$Required = @(
  'HEROKU_API_KEY',
  'HEROKU_APP_BACKEND',
  'HEROKU_APP_WS',
  'HEROKU_APP_REDIS_INDEXER',
  'HEROKU_APP_RATING_CRON'
)

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  Write-Host "gh CLI not found. Install from https://cli.github.com/ and run 'gh auth login' first." -ForegroundColor Red
  exit 1
}

foreach ($s in $Required) {
  $val = (Get-Item -Path Env:\$s -ErrorAction SilentlyContinue).Value
  if (-not $val) {
    $val = Read-Host "Enter value for $s"
  }
  Write-Host "Setting GitHub secret $s..."
  # gh secret set supports --body flag, using Invoke-Expression to pass value
  gh secret set $s --body "$val"
}

Write-Host "All secrets set. Verify in GitHub -> Settings -> Secrets -> Actions." -ForegroundColor Green
