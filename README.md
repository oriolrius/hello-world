# hello-world

The DBAI course's small HTTP application. The same app runs by hand in S2,
inside a container from S4, and behind Kubernetes probes from S8 — so its
response contract is **fixed** and every later packaging change must preserve it.

## HTTP contract

Served on `0.0.0.0:8000` (from `config/settings.yaml`):

| Request | Response |
|---|---|
| `GET /` | `200` JSON `{"message": <greeting>, "hostname": <server hostname>}` |
| `GET /health` | `200` JSON `{"status": "ok"}` — the liveness/readiness probe target |
| `GET /boom` | `500` JSON — deliberate failure endpoint for the S8+ self-healing drills |
| `GET /<unknown>` | `404` JSON |
| `POST /` (or any write method) | `405` JSON — only `GET` is served |

The body of `GET /` includes the **server hostname**, so container and
Kubernetes checks can see *which* instance answered.

## Configuration

`config/settings.yaml` supplies the contract inputs:

```yaml
host: 0.0.0.0
port: 8000
greeting: "Hello, world!"
```

Override the file location with `HELLO_WORLD_SETTINGS=/path/to/settings.yaml`.
A malformed file fails loudly rather than starting with wrong values.

## Run it

```bash
uv sync                 # recreate the locked runtime in a clean environment
uv run hello-world      # binds 0.0.0.0:8000; Ctrl-C stops it (no supervisor)

# in another shell:
curl -i localhost:8000/          # 200 JSON with hostname
curl -i localhost:8000/health    # 200
curl -i localhost:8000/boom      # 500
curl -i localhost:8000/nope      # 404
curl -i -X POST localhost:8000/  # 405
```

## Test the contract

```bash
uv run pytest -q        # starts the real server on an ephemeral port and asserts every response
```

## How later sessions reuse this

The container image (S4) and the Kubernetes Deployment/Service/probes (S8+)
exercise the **same** endpoints: `/health` is the probe target and `/boom`
drives failure/self-healing drills. Because the contract is fixed here, those
later checks — and the monitoring in S10 — do not change the app.

`hello.py` is the retained S1 bootstrap; the S2 increment does not ship the
later student `greet(name)` solution or its solution test.
