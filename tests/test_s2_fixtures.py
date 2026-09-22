"""S2 instructor fixtures (APP-03).

Proves the deliberate YAML fault fails to load (before the app could bind a
port) and that the repaired/valid settings load cleanly. The full HTTP contract
after repair is covered by test_contract.py.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from hello_world.config import load_settings

BROKEN = Path(__file__).resolve().parent.parent / "fixtures" / "s2" / "settings.broken.yaml"
REPAIRED = Path(__file__).resolve().parent.parent / "config" / "settings.yaml"


def test_broken_starter_settings_fail_to_load():
    with pytest.raises(Exception):  # noqa: B017 — YAML ScannerError or ValueError, both are "fails before binding"
        load_settings(str(BROKEN))


def test_repaired_settings_load_the_contract_inputs():
    s = load_settings(str(REPAIRED))
    assert s["host"] == "0.0.0.0"
    assert s["port"] == 8000
    assert isinstance(s["greeting"], str) and s["greeting"]
