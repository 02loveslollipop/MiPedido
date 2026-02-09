#!/usr/bin/env python3
"""Create Heroku Scheduler add-on and (if possible) create scheduled jobs.

This helper attempts to:
  - Ensure the Scheduler add-on (scheduler:standard) is provisioned for the app.
  - If the add-on exposes an API endpoint (some add-ons provide a private API URL via config vars), attempt to POST job definitions to it.
  - Otherwise, print a clear set of `heroku` CLI commands and dashboard URLs to add the jobs manually.

Security: This script requires `HEROKU_API_KEY` in the environment and the app name passed via `--app`.

Usage:
  export HEROKU_API_KEY=<key>
  python scripts/create_heroku_scheduler_jobs.py --app mipedido-rating-cron --jobs-file scheduler-jobs.yml

The jobs file is a YAML list of jobs, for example:

- command: "./rating-cron-binary"
  frequency: daily
  at: "02:00"
- command: "./redis-indexer-binary"
  frequency: hourly
  every: 3

Notes:
- Heroku Scheduler UI supports frequencies: "every 10 minutes", "hourly", "daily". For multi-hour jobs you should use hourly and set the desired times, or schedule multiple entries.
- Programmatic creation of Scheduler entries depends on the add-on provider. If your add-on provides an API URL via its config vars (see the script output), this tool will attempt to POST jobs there.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any, Dict, List, Optional

import requests
import yaml

HEROKU_API = "https://api.heroku.com"
HEADERS = {"Accept": "application/vnd.heroku+json; version=3"}


def heroku_request(method: str, path: str, token: str, **kwargs) -> requests.Response:
    headers = kwargs.pop("headers", {})
    headers.update(HEADERS)
    headers.update({"Authorization": f"Bearer {token}"})
    return requests.request(method, HEROKU_API + path, headers=headers, **kwargs)


def ensure_scheduler_addon(app: str, token: str) -> Dict[str, Any]:
    """Ensure scheduler add-on exists; returns the add-on resource dict."""
    # List addons
    resp = heroku_request("GET", f"/apps/{app}/addons", token)
    resp.raise_for_status()
    addons = resp.json()
    for a in addons:
        if a.get("addon_service", {}).get("name") == "scheduler":
            print(f"Scheduler add-on already provisioned: {a.get('id')}")
            return a

    print("Provisioning Heroku Scheduler add-on (scheduler:standard)...")
    body = {"plan": "scheduler:standard"}
    resp = heroku_request("POST", f"/apps/{app}/addons", token, json=body)
    resp.raise_for_status()
    new = resp.json()
    print("Provisioned:", new.get("id"))
    # Wait a moment for config vars to populate
    time.sleep(2)
    return new


def find_scheduler_api_url(app: str, addon: Dict[str, Any], token: str) -> Optional[str]:
    """Try to discover an API endpoint for the scheduler add-on via config vars or addon info."""
    # Fetch addon info
    addon_id = addon.get("id")
    resp = heroku_request("GET", f"/apps/{app}/addons/{addon_id}", token)
    resp.raise_for_status()
    info = resp.json()

    # Some add-ons expose a "web_url" or other fields.
    if info.get("web_url"):
        print("Found addon web URL:", info.get("web_url"))

    # Check the addon's config vars on the app for any scheduler URLs.
    resp = heroku_request("GET", f"/apps/{app}/config-vars", token)
    resp.raise_for_status()
    cfg = resp.json()

    # heuristics: look for keys with SCHEDULER or SCHEDULER_API
    for k, v in cfg.items():
        if "SCHEDULER" in k.upper() and (v.startswith("http://") or v.startswith("https://")):
            print(f"Discovered possible scheduler API URL in config var {k}")
            return v

    return None


def post_job_to_scheduler_api(scheduler_api_url: str, job: Dict[str, Any]) -> bool:
    """Attempt to POST a job to a scheduler API endpoint. This format is provider-specific.
    Returns True if the request succeeded (2xx), False otherwise.
    """
    try:
        print(f"Posting job to {scheduler_api_url}: {job}")
        resp = requests.post(scheduler_api_url.rstrip("/") + "/jobs", json=job)
        if resp.status_code >= 200 and resp.status_code < 300:
            print("Job created ok")
            return True
        print("Failed to create job, status:", resp.status_code, resp.text)
        return False
    except Exception as exc:
        print("Error contacting scheduler api:", exc)
        return False


def load_jobs_file(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise SystemExit("Jobs file must be a YAML list of job objects")
    return data


def print_manual_instructions(app: str, jobs: List[Dict[str, Any]]):
    print("\nNo scheduler API discovered. Create the jobs manually using Heroku Scheduler UI or the CLI. Examples:")
    print(f"  heroku addons:create scheduler:standard --app {app}  # if not already provisioned")
    print(f"  heroku addons:open scheduler --app {app}  # open the GUI")
    print("Or run a one-off to test commands manually:")
    for j in jobs:
        cmd = j.get("command")
        example = f"  heroku run --app {app} \"{cmd}\""
        print(example)
    print("\nTo schedule the job use the Scheduler dashboard: Add Job → set command and frequency (every 10 minutes / hourly / daily)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", required=True, help="Heroku app name (e.g., mipedido-rating-cron)")
    parser.add_argument("--jobs-file", required=True, help="YAML file listing jobs to add")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done and exit")
    args = parser.parse_args()

    token = os.environ.get("HEROKU_API_KEY")
    if not token:
        print("HEROKU_API_KEY is required in env")
        sys.exit(2)

    jobs = load_jobs_file(args.jobs_file)

    addon = ensure_scheduler_addon(args.app, token)
    api_url = find_scheduler_api_url(args.app, addon, token)

    if not api_url:
        print("No scheduler add-on API endpoint discovered (this is common). Falling back to CLI / manual instructions.")
        print_manual_instructions(args.app, jobs)
        return

    # if we do have an api_url, try to POST jobs in a provider-agnostic JSON shape.
    for j in jobs:
        job_payload = {
            "command": j.get("command"),
            "frequency": j.get("frequency"),
            # provider-specific fields may include `at`, `every`, `timezone` etc.
            **{k: v for k, v in j.items() if k not in ("command", "frequency")},
        }
        if args.dry_run:
            print("DRY RUN: Would POST:", job_payload)
            continue
        ok = post_job_to_scheduler_api(api_url, job_payload)
        if not ok:
            print("Failed to create job programmatically for command:", job_payload["command"])
            print_manual_instructions(args.app, [j])


if __name__ == "__main__":
    main()
