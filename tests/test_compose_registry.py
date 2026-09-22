"""Registry Compose fixture (APP-10).

Proves the committed compose.yml deploys an explicit immutable GHCR release tag —
rejecting a missing/empty tag and never falling back to `latest` or a local
build — and that run and rollback both resolve to the intended image.
"""
from __future__ import annotations

import os
import shutil
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
COMPOSE = os.path.join(ROOT, "compose.yml")


def _has_compose() -> bool:
    if shutil.which("docker") is None:
        return False
    return subprocess.run(["docker", "compose", "version"], capture_output=True).returncode == 0


pytestmark = pytest.mark.skipif(not _has_compose(), reason="docker compose required")


def _config(**env):
    e = {**os.environ, "GHCR_NAMESPACE": "student", **env}
    return subprocess.run(
        ["docker", "compose", "-f", COMPOSE, "config"],
        capture_output=True, text=True, env=e,
    )


def test_missing_tag_rejected():
    r = _config()
    assert r.returncode != 0 and "HELLO_IMAGE_TAG" in r.stderr


def test_empty_tag_rejected():
    r = _config(HELLO_IMAGE_TAG="")
    assert r.returncode != 0


def test_release_tag_resolves_exactly():
    r = _config(HELLO_IMAGE_TAG="v1.1.0")
    assert r.returncode == 0
    assert "ghcr.io/student/hello-world:v1.1.0" in r.stdout
    assert "build:" not in r.stdout and ":latest" not in r.stdout


def test_rollback_to_prior_tag():
    r = _config(HELLO_IMAGE_TAG="v1.0.0")
    assert "ghcr.io/student/hello-world:v1.0.0" in r.stdout
