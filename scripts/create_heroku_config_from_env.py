#!/usr/bin/env python3
"""Create/Update Heroku app config vars from .env via Heroku Platform API.

Usage:
  # Run locally with HEROKU_API_KEY in env
  python scripts/create_heroku_config_from_env.py --app my-heroku-app

  # Or in GitHub Actions: set HEROKU_API_KEY secret and call the workflow.

The script reads .env and posts non-empty keys to PATCH /apps/{app}/config-vars
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Dict

import requests

HEROKU_API = "https://api.heroku.com"
HEADERS = {"Accept": "application/vnd.heroku+json; version=3"}


def load_env(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not os.path.exists(path):
        raise SystemExit(f".env file not found at {path}")
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v
    return env


def heroku_patch_config(app: str, token: str, kv: Dict[str, str]) -> bool:
    url = f"{HEROKU_API}/apps/{app}/config-vars"
    headers = dict(HEADERS)
    headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    resp = requests.patch(url, headers=headers, json=kv)
    if resp.status_code >= 200 and resp.status_code < 300:
        return True
    print(f"Failed to set config for {app}: {resp.status_code} {resp.text}")
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', required=True, help='Heroku app name')
    parser.add_argument('--mongo-uri', help='Optional override MONGODB_URL')
    args = parser.parse_args()

    token = os.environ.get('HEROKU_API_KEY')
    if not token:
        print('HEROKU_API_KEY environment variable is required')
        sys.exit(2)

    env = load_env(os.path.join(os.path.dirname(__file__), '..', '.env'))
    if args.mongo_uri:
        env['MONGODB_URL'] = args.mongo_uri

    # Filter out empty values
    kv = {k: v for k, v in env.items() if v != ''}
    if not kv:
        print('No non-empty env vars to set')
        return

    print(f"Patching {len(kv)} config vars on {args.app} (secret values hidden)")
    ok = heroku_patch_config(args.app, token, kv)
    if not ok:
        sys.exit(1)
    print('Done')


if __name__ == '__main__':
    main()
