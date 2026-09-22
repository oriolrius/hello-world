# S5 — the delivery & rollback learning path (APP-12)

The reference end-to-end journey a student runs in S5, assembled from the proven
pieces: the version-tagged pipeline (APP-09), the registry Compose (APP-10) and
the SSH deploy (APP-11). Push a `v*` tag and a green **test → build-push →
deploy** run puts the requested release on the VM with **no manual step**.

## 1. Ship a greeting release (AC#1/#2)

```bash
# edit the greeting in config/settings.yaml, then:
git commit -am "feat: new greeting"          # feat -> MINOR
uv run cz bump --yes                          # e.g. 1.0.0 -> 1.1.0
git push origin main --follow-tags            # tag push triggers release.yml
```

Measure **push → serving** wall-clock and the **manual-step count** (≈1: the tag
push) for the S2 comparison — the artisanal deploy's stopwatch is what this beats.
Prove the change:

```bash
curl -s http://localhost:8000/ | jq .message   # BEFORE: old greeting
# … after the deploy run is green …
curl -s http://localhost:8000/ | jq .message   # AFTER: new greeting
```

Reference evidence (this repo's qualification): the pipeline ran green
test → build-push → deploy and served the exact tagged image
(`RUNNING_IMAGE=ghcr.io/<owner>/hello-world:<tag>`), verified in APP-09/APP-11.

## 2. Three distinct failure drills (AC#3)

| Drill | Trigger | Observed outcome | Final state |
|---|---|---|---|
| fix-only patch | a `fix:` commit + `cz bump` | PATCH release (`1.1.0 → 1.1.1`), green deploy | new patch serves |
| broken test | a failing test on the tag | `test` red → **build-push skipped**, no image published | prior release still serves |
| failed image pull | deploy a non-existent tag | `docker compose pull` exits nonzero → **red deploy**, no old-image fallback | reconcile the tag, re-deploy |

Broken-test and failed-pull are **different** failures — one blocks publication,
the other blocks deployment — and both are observable (verified in APP-09/APP-11).

## 3. Rollback to a prior release (AC#4)

```bash
HELLO_IMAGE_TAG=v1.0.0 docker compose up -d     # serve the previous greeting/image
```

Rollback selects an explicit prior `v*` tag from the registry — **never `latest`**
and never a local build (the committed `compose.yml` forbids both, APP-10).

## 4. Workbench pin verification (AC#5)

Read the two running course images against the qualified manifest without
changing the workbench release model:

```bash
docker inspect --format '{{.Config.Image}}' $(docker compose -f ../ai-workbench/compose.yml ps -q pi-web-ui qdrant)
# must match ghcr.io/oriolrius/pi-web-ui:<pinned> and ghcr.io/oriolrius/qdrant:v1.15.0
```

## 5. Evidence (AC#6)

Record under `docs/evidence/s05/`: the green pipeline run URL, the before/after
`curl` greeting, the push→serving time + manual-step count, the three failure-drill
captures, and the rollback proof. Leave the exact reference **commit / image
digest / workflow-run** in `JOURNAL.md`. No credential values in any capture.
