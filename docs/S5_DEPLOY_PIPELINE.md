# S5 — deploy the exact release to the VM (APP-11)

The `deploy` job of `release.yml` (see `instructor/release.reference.yml`) SSHes
the freshly built release onto the workspace VM, so a green pipeline means the
**requested version is actually serving**.

## Responsibilities

| Where | Does |
|---|---|
| **Controller** (your laptop) | generates the dedicated **deploy keypair**, installs its PUBLIC key on the VM via the existing `dbai.pem` auth (the `initialize --deploy-public-key` bootstrap), and stores the PRIVATE key as the `VM_SSH_KEY` Actions secret and the Elastic IP as `VM_HOST`. |
| **GitHub Actions** | after `build-push`, the `deploy` job SSHes to `VM_HOST` with `VM_SSH_KEY`, passing `HELLO_IMAGE_TAG` (the triggering `v*`); it never runs on a self-hosted VM. |
| **VM** | logs in to GHCR with a **`read:packages`** token, `docker compose pull` (the committed registry compose), `up -d`, and a health check. |

## Failure propagation

- A missing/failed image pull returns **nonzero** and does **not** fall back to
  an old cached image or report the previous running version as the release.
- `set -euo pipefail` + the explicit health check make any remote command
  failure a **red** Actions job.

## Keys, registry auth, fingerprint, version

- The deploy **private** key, the GHCR token and any course key are **secrets** —
  never in Git history or logs (GitHub masks secret values).
- The deploy **public** key is installed through the same bootstrap the
  `ec2-console` rebuild uses, so a rebuilt VM re-accepts the same deploy key.
- After a VM replacement, verify the new host key from the trusted channel
  (`console.sh verify-host`) and, if the SSH Action pins a host fingerprint,
  update that pin — `VM_HOST`/`VM_SSH_KEY` themselves do not change.
- A successful run records the exact `v*` tag and the running image identity
  (`ghcr.io/<owner>/hello-world:<tag>`).
