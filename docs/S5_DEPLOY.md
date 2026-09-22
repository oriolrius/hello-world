# S5 — deploy a registry release (APP-10)

S4 built the image locally; S5 deploys a **reviewed immutable release tag** from
GHCR. The committed [`compose.yml`](../compose.yml) encodes that contract and is
tracked in Git so an S6 reconstruction restores it from origin.

## The contract

```yaml
services:
  hello:
    image: ghcr.io/${GHCR_NAMESPACE:?…}/hello-world:${HELLO_IMAGE_TAG:?set the release tag}
    ports: ["8000:8000"]
    restart: unless-stopped
```

- `${HELLO_IMAGE_TAG:?…}` makes `docker compose` **reject** a missing or empty
  tag — there is no `latest` fallback and no local `build:`.
- The image is always an explicit `v*` registry tag.

## Run and roll back (explicit tag every time)

```bash
export GHCR_NAMESPACE=<you>
HELLO_IMAGE_TAG=v1.1.0 docker compose up -d        # deploy a release
HELLO_IMAGE_TAG=v1.0.0 docker compose up -d        # roll back to a prior release
```

Both choose exactly the named registry image (`tests/test_compose_registry.py`
verifies this). Never edit the file to a mutable default or a local build.

## Why it's committed (S4 local-build → S5 registry)

In S4 you built and ran the image on the box. In S5 the deployment references a
**published, reviewed** tag, so anyone (and any S6 recovery) redeploys the same
artifact. Because `compose.yml` is in Git, a clean clone from your origin
restores the deployment contract **before** any S6 redeployment command.
