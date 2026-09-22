"""Local commit-message guardrail fixture (APP-04).

Proves the locked Commitizen contract used by .githooks/commit-msg rejects a
non-conventional message and accepts the course Conventional Commit types plus
the generated-merge-prefix policy. This is the LOCAL check; the server-side
event-range check (student-authored CI) is independently required.
"""
from __future__ import annotations

import shutil
import subprocess

import pytest

pytestmark = pytest.mark.skipif(shutil.which("cz") is None, reason="commitizen not installed")


def _check(message: str) -> int:
    return subprocess.run(
        ["cz", "check", "--message", message],
        capture_output=True,
        text=True,
    ).returncode


@pytest.mark.parametrize(
    "message",
    [
        "feat: add /health endpoint",
        "fix(app): return 405 for POST /",
        "docs: document the HTTP contract",
        "test: add contract checks",
        "refactor(config): validate port",
        "chore(release): v1.0.0",
        "Merge pull request #1 from oriolrius/dbai24",  # generated-merge prefix allowed
    ],
)
def test_accepts_conventional_and_generated_merge(message):
    assert _check(message) == 0, f"should accept: {message!r}"


@pytest.mark.parametrize(
    "message",
    [
        "added a thing",
        "WIP",
        "update stuff",
        "Fixed the bug",  # not a lowercase conventional type
    ],
)
def test_rejects_non_conventional(message):
    assert _check(message) != 0, f"should reject: {message!r}"
