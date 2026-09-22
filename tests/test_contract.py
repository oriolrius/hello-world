"""Executable HTTP-contract checks (APP-02).

Proves GET / -> 200 JSON with the server hostname, /health -> 200, /boom -> 500,
an unknown path -> 404 and POST / -> 405. Runs the real server on an ephemeral
port, so it exercises exactly what curl / container / Kubernetes probes hit.
"""
from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from hello_world.app import make_server

GREETING = "Hello, test!"


@pytest.fixture(scope="module")
def base_url():
    httpd = make_server("127.0.0.1", 0, GREETING)  # port 0 -> ephemeral
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()
        httpd.server_close()


def _request(url: str, method: str = "GET"):
    req = urllib.request.Request(url, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def test_root_returns_200_json_with_hostname(base_url):
    code, body = _request(base_url + "/")
    assert code == 200
    data = json.loads(body)
    assert data["message"] == GREETING
    assert data["hostname"] == socket.gethostname()


def test_health_returns_200(base_url):
    code, _ = _request(base_url + "/health")
    assert code == 200


def test_boom_returns_500(base_url):
    code, _ = _request(base_url + "/boom")
    assert code == 500


def test_unknown_path_returns_404(base_url):
    code, _ = _request(base_url + "/does-not-exist")
    assert code == 404


def test_post_root_returns_405(base_url):
    code, _ = _request(base_url + "/", method="POST")
    assert code == 405
