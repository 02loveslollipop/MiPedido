#!/usr/bin/env python3
"""Create/Update Heroku app config vars from .env via Heroku Platform API.

Usage:
  # Run locally with HEROKU_API_KEY in env
  python scripts/create_heroku_config_from_env.py --app my-heroku-app --env-file .env

  # Dry-run locally without modifying Heroku config:
  python scripts/create_heroku_config_from_env.py --app my-heroku-app --env-file .env --dry-run

  # In GitHub Actions: set HEROKU_API_KEY secret and call the workflow.

The script reads an env file and posts non-empty keys to PATCH /apps/{app}/config-vars
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Dict

import requests

try:
    from scripts.path_utils import validate_safe_path
except ImportError:
    from path_utils import validate_safe_path

HEROKU_API = "https://api.heroku.com"
HEADERS = {"Accept": "application/vnd.heroku+json; version=3"}


def load_env(path: str) -> Dict[str, str]:
    abs_path = validate_safe_path(path, description="Env file")

    env: Dict[str, str] = {}
    with open(abs_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if len(v) >= 2 and (
                (v.startswith('"') and v.endswith('"'))
                or (v.startswith("'") and v.endswith("'"))
            ):
                v = v[1:-1]
            env[k] = v
    return env


def heroku_patch_config(app: str, token: str, kv: Dict[str, str]) -> bool:
    url = f"{HEROKU_API}/apps/{app}/config-vars"
    headers = dict(HEADERS)
    headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    try:
        resp = requests.patch(url, headers=headers, json=kv, timeout=30)
    except requests.RequestException as exc:
        print(f"Failed to communicate with Heroku API for {app}: {exc}", file=sys.stderr)
        return False

    if 200 <= resp.status_code < 300:
        return True
    print(f"Failed to set config for {app}: {resp.status_code} {resp.text}", file=sys.stderr)
    return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create/Update Heroku app config vars from env file via Heroku Platform API."
    )
    parser.add_argument("--app", required=True, help="Heroku app name")
    parser.add_argument("--mongo-uri", help="Optional override MONGODB_URL")
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to env file (default: .env)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print config vars to set without making API calls",
    )
    args = parser.parse_args()

    token = os.environ.get("HEROKU_API_KEY")
    if not token and not args.dry_run:
        print("HEROKU_API_KEY environment variable is required", file=sys.stderr)
        sys.exit(2)

    env: Dict[str, str] = {}
    if os.path.exists(args.env_file):
        env = load_env(args.env_file)
    elif args.mongo_uri and args.mongo_uri.strip():
        # Env file absent but mongo-uri override specified
        pass
    else:
        print(f"Env file not found at {args.env_file}", file=sys.stderr)
        sys.exit(1)

    if args.mongo_uri and args.mongo_uri.strip():
        env["MONGODB_URL"] = args.mongo_uri.strip()

    # Filter out empty values
    kv = {k: v for k, v in env.items() if v != ""}
    if not kv:
        print("No non-empty env vars to set")
        return

    print(f"Patching {len(kv)} config vars on {args.app} (secret values hidden)")
    if args.dry_run:
        sorted_keys = sorted(kv.keys())
        print(f"[dry-run] Would set keys on {args.app}: {', '.join(sorted_keys)}")
        print("Done (dry-run)")
        return

    ok = heroku_patch_config(args.app, token, kv)
    if not ok:
        sys.exit(1)
    print("Done")


if __name__ == "__main__":
    main()
