# S5 — the version-tagged release pipeline (APP-09)

Pushing a `v*` tag runs `release.yml`: a **test** stage (locked deps, ruff,
pytest) that must pass before a **build-push** stage publishes the image to GHCR.
The S1 `hello.yml` and S3 `ci.yml` workflows stay separate. The instructor
reference is `instructor/release.reference.yml`; students author their own.

## Stages

1. **test** — `uv sync --locked`, `uv run ruff check .`, `uv run pytest -q`.
2. **build-push** (`needs: test`) — logs in to `ghcr.io`, builds
   `instructor/Dockerfile.reference`, and pushes
   `ghcr.io/<owner-lowercased>/hello-world:<the v* tag>` **and** `:latest`.
   `permissions: {contents: read, packages: write}`.

A broken test fails **test**, so **build-push is skipped** — no image is
published and every downstream deploy is blocked.

## Authentication (never record a credential)

- **Publishing (CI):** the workflow uses the automatic `GITHUB_TOKEN` with
  `packages: write`. No PAT is stored.
- **Pulling on the VM (deploy):** the VM authenticates to GHCR with a token that
  has only **`read:packages`** to pull the private image — it never needs write.
- The two are different scopes: publish is CI-side and write; deploy is VM-side
  and read-only. Keep both out of Git, logs and screenshots.

## Traceability

A successful tagged run publishes exactly the triggering `v*` tag (plus a
convenience `:latest`), and the image digest ties back to the source commit the
tag pointed at.
