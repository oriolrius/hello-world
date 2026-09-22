# S8 — hello-world on Kubernetes (APP-13)

You import **only this `k8s/` folder** into your hello-world repo and reuse the
**image you already released** (S5). The manifests do not ship a solution — you
substitute your own GHCR release tag and pull secret. This runs on the **S8
`operations` profile** (pinned k3s, `PROFILE-04`); after the S8 transition your
`kubectl` works without sudo (see the operations RUNBOOK). Recovery of a
populated node follows the operations stop-only discipline.

## Apply order (namespace FIRST)

The order is mandatory — the namespace must exist before its pull Secret and
workloads:

```bash
# [workspace] on the k3s node (kubectl is non-sudo after the S8 transition)
kubectl apply -f k8s/00-namespace.yaml                 # 1. namespace 'hello'
kubectl -n hello create secret docker-registry ghcr-pull \
  --docker-server=ghcr.io --docker-username=<you> \
  --docker-password=<your read:packages PAT>           # 2. namespace-scoped pull secret
kubectl apply -f k8s/10-deployment.yaml -f k8s/20-service.yaml   # 3. workloads
kubectl -n hello rollout status deploy/hello-world
```

A fresh cluster proves the order: applying workloads before the namespace/secret
fails; applying in this order succeeds.

## The S8 drills (evidence)

1. **Two replicas answer** — record **two different pod hostnames**:
   ```bash
   curl -s http://<node>:30080/ ; # repeat — the hostname field alternates between pods
   kubectl -n hello get pods -o wide
   ```
   → **evidence screenshot 1**: two pods Running + two hostnames from `/`.
2. **Scale 2 → 4 → 2**:
   ```bash
   kubectl -n hello scale deploy/hello-world --replicas=4 && kubectl -n hello get pods
   kubectl -n hello scale deploy/hello-world --replicas=2
   ```
3. **Self-healing** — delete a pod, the Deployment replaces it:
   ```bash
   kubectl -n hello delete pod <one-pod> ; kubectl -n hello get pods -w
   ```
   → **evidence screenshot 2**: killed pod replaced, replica count restored.
4. **Rolling update** to your next tag (zero downtime):
   ```bash
   kubectl -n hello set image deploy/hello-world app=ghcr.io/oriolrius/hello-world:<next-tag>
   kubectl -n hello rollout status deploy/hello-world
   ```
5. **Rollback of a bad tag** — set an **unavailable** tag; the prior healthy
   replicas keep serving (readiness gates the rollout), then roll back:
   ```bash
   kubectl -n hello set image deploy/hello-world app=ghcr.io/oriolrius/hello-world:<does-not-exist>
   kubectl -n hello get pods            # new pod ImagePullBackOff; old pods still Ready + serving
   kubectl -n hello rollout undo deploy/hello-world
   ```
   → **evidence screenshot 3**: bad rollout blocked, service still up, rollback OK.

## Record the final valid image (Git ↔ cluster agree)

After an imperative rollback, write the **final valid running image** back into
`k8s/10-deployment.yaml` and commit it, so a later `kubectl apply -f k8s/` does
**not** re-introduce the bad tag:

```bash
# set image: ghcr.io/oriolrius/hello-world:<final-valid-tag> in 10-deployment.yaml
git commit -am "fix(k8s): pin hello-world to the final valid image after rollback"
```

## Qualification / stop-only

Qualification records the **actual image versions**, the **cluster state**
(nodes, pods, rollout history) and the three evidence screenshots. Only `k8s/`
is imported from the S8 tag — your application, earlier evidence and the S5
Compose-targeting release pipeline stay intact. After the lab, **stop** the node
(operations stop-only discipline); never reset a populated cluster.
