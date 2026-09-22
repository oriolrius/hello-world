# S4 — containerize hello-world (APP-07)

You author your **own** `Dockerfile` and homework `compose.yml` on branch
**`s04-docker`**; the starter does not ship the completed solution. The
instructor answer key lives in `instructor/Dockerfile.reference` and
`instructor/compose.reference.yml`.

## The build contract

- **Base:** `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` (uv + Python pinned).
- **Locked, non-dev deps:** `uv sync --locked --no-dev`.
- **Source-independent cache layer:** copy `pyproject.toml` + `uv.lock` first and
  `uv sync --locked --no-dev --no-install-project`, *then* copy the source. A
  source-only change reuses the dependency layer.
- **Non-root:** the image runs as `appuser`.
- **No runtime sync / network install:** `CMD ["uv","run","--no-sync","hello-world"]`.
- **`.dockerignore`** keeps `.git`, `.venv`, `__pycache__`, caches, tests and
  evidence out of the build context.

## Run and check

```bash
docker build -f instructor/Dockerfile.reference -t hello-world:local .
docker run -d --name hello -p 127.0.0.1:8000:8000 hello-world:local
docker exec hello id -un            # -> appuser
curl -i localhost:8000/health       # 200 (and /, /boom, 404, 405 as the contract)
docker logs hello                   # startup line
docker exec hello sh                # shell/exec check
```

## Cache evidence (measure, don't hard-code seconds)

A source-only rebuild reuses the dependency layer (Docker prints `CACHED` for
the `uv sync … --no-install-project` step; observed ~2 s here). The **deliberate
ordering mistake** — `COPY . .` *before* installing deps — makes any source
change bust that layer and re-install everything; restoring the correct ordering
recovers the reuse. Record your own measured before/after times in `JOURNAL.md`.

## Homework Compose (two-container port exercise)

`instructor/compose.reference.yml` builds locally and binds **loopback**
(`127.0.0.1`) with two containers of the same image on `:8000` and `:8001`, so
you can see two instances answer on different ports. It is repeatable
(`up`/`down`), and S3 quality (`ruff` + `pytest` + the commit-message check)
stays green.

## Reviewed PR expectations

Open the `s04-docker` work as a PR into your `main`: the required S3 `quality`
check must pass, and a reviewer approves before merge (same protection as S3).
The distributed starter contains **no** completed `Dockerfile` or homework
`compose.yml` — those are your work.
