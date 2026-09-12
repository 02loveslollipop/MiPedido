"""Utilities for safe file path handling across deployment scripts."""
from __future__ import annotations

import os
import tempfile


def validate_safe_path(path: str, description: str = "File") -> str:
    """Validate that a path does not traverse directories and is contained within allowed roots.

    Returns the canonical absolute path if valid, or raises SystemExit otherwise.
    """
    if ".." in path:
        raise SystemExit(f"Invalid path: directory traversal not allowed in '{path}'.")

    abs_path = os.path.abspath(path)
    allowed_root = os.path.abspath(os.getcwd())
    temp_root = os.path.abspath(os.environ.get("RUNNER_TEMP", tempfile.gettempdir()))

    if not abs_path.startswith(allowed_root) and not abs_path.startswith(temp_root):
        raise SystemExit(
            f"Access denied: {description.lower()} '{path}' is outside allowed directories."
        )

    if not os.path.isfile(abs_path):
        raise SystemExit(f"{description} not found at {path}")

    return abs_path
