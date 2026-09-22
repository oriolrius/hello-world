"""Load the host/port/greeting contract inputs from config/settings.yaml.

A malformed YAML file (the deliberate S2 trap) raises clearly instead of
silently starting with wrong values.
"""
from __future__ import annotations

import os

import yaml

DEFAULTS: dict[str, object] = {"host": "0.0.0.0", "port": 8000, "greeting": "Hello, world!"}


def load_settings(path: str | None = None) -> dict:
    """Return {host, port, greeting}, merging the YAML file over the defaults."""
    path = path or os.environ.get("HELLO_WORLD_SETTINGS", "config/settings.yaml")
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: settings must be a YAML mapping, got {type(data).__name__}")
    settings = {**DEFAULTS, **data}
    try:
        settings["port"] = int(settings["port"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{path}: port must be an integer, got {settings['port']!r}") from exc
    return settings
